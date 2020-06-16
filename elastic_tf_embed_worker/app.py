"""
Honestly, [this blog post][1] convinced me there's no hard in trying Sanic for this
service. It seems like we can benefit from not installing gunicorn too because Sanic is
already asynchronous.

[1]: https://medium.com/@ahmed.nafies/is-sanic-python-web-framework-the-new-flask-2fe06b409fa3
"""

import random
import asyncio
import tensorflow as tf

from sanic import Sanic, response
from sanic_openapi import swagger_blueprint
from typing import List, Text, Union, Tuple, Optional
from enum import Enum
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_streaming_bulk
from log_utils import log
from sanic_validation import validate_json
from functools import wraps
from datetime import datetime
from model_utils import initialize_model

from app_config import default_settings


SUCCESS = 200
FAILURE = 500  # TODO: return useful statuses https://www.restapitutorial.com/httpstatuscodes.html
SUCCESS_DICT = {"completed": True}
FAILURE_DICT = {"completed": False}

app = Sanic(__name__)


def depends_on_es(
    app: Sanic,
    # es: AsyncElasticsearch
):
    """
    Decorator to make sure the Elasticsearch connection is healthy.

    Handles problems elegantly. 

    Resources:
    * https://sanic.readthedocs.io/en/latest/sanic/decorators.html
    """

    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            # es_health_check will make sure this is not None either
            es = app.es

            if await es_health_check(es):
                # the Elasticsearch connection is healthy.
                # run the handler method and return the response
                res = await f(request, *args, **kwargs)
                return res
            else:
                # the ES is not healthy or client problem
                return response.json(FAILURE_DICT, FAILURE)

        return decorated_function

    return decorator


class STD_KEYS(Enum):
    """
    An enum of standard keys to keep things consistent
    """

    IDX = "index_name"
    NAM = "name"
    CLS = "classification"
    TXT = "text"
    TIM = "timestamp"
    EMD = "embedding"


class DEFAULT_INDEX_MAPPING_KEYS(Enum):
    NAM = STD_KEYS.NAM.value
    CLS = STD_KEYS.CLS.value
    TXT = STD_KEYS.TXT.value
    TIM = STD_KEYS.TIM.value
    EMD = STD_KEYS.EMD.value


class EMBED_SCHEMA_KEYS(Enum):
    NAM = STD_KEYS.NAM.value
    CLS = STD_KEYS.CLS.value
    TXT = STD_KEYS.TXT.value


class INDEX_SCHEMA_KEYS(Enum):
    IDX = STD_KEYS.IDX.value
    NAM = STD_KEYS.NAM.value
    CLS = STD_KEYS.CLS.value
    TXT = STD_KEYS.TXT.value


INDEX_OR_EMBED_SCHEMA_KEYS = STD_KEYS


EMBED_REQUEST_SCHEMA = {
    EMBED_SCHEMA_KEYS.NAM.value: {"type": "string", "required": True},
    EMBED_SCHEMA_KEYS.CLS.value: {"type": "string", "required": True},
    EMBED_SCHEMA_KEYS.TXT.value: {"type": "string", "required": True},
}
"""
Example:

{
    "name": "Something",
    "classification": "question",
    "text": "What is Something?"
}
"""

EMBED_BULK_REQUEST_SCHEMA = {
    "texts": {
        "type": "list",
        "schema": {"type": "dict", "schema": EMBED_REQUEST_SCHEMA},
        "required": True,
    }
}
"""
Example:
{
    "texts": [
        {
            "name": "Something",
            "classification": "question",
            "text": "What is Something?",
        },
        {
            "name": "AnotherThing",
            "classification": "question",
            "text": "When did Something become AnotherThing?",
        },
    ]
}
"""


INDEX_REQUEST_SCHEMA = {
    INDEX_SCHEMA_KEYS.IDX.value: {"type": "string", "required": True},
    INDEX_SCHEMA_KEYS.NAM.value: {"type": "string", "required": True},
    INDEX_SCHEMA_KEYS.CLS.value: {"type": "string", "required": True},
    INDEX_SCHEMA_KEYS.TXT.value: {"type": "string", "required": True},
}

INDEX_BULK_REQUEST_SCHEMA = {
    "texts": {
        "type": "list",
        "schema": {"type": "dict", "schema": INDEX_REQUEST_SCHEMA},
        "required": True,
    }
}

INDEX_MAPPINGS = {
    "properties": {
        "doc": {
            "properties": {
                "classification": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "embedding": {"type": "dense_vector", "dims": 512},
                "name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "text": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "timestamp": {"type": "date"},
            }
        }
    }
}


@app.get("/")
async def hello(request):
    log()
    friendly_address = [
        "Friend 🤗",
        "Pal 👋",
        "Beautiful 😊",
        "Neighbor 🤗",
        "Human 🤖🧬",
        "🌍",
    ]
    return response.json({"message": f"Hello, {random.choice(friendly_address)}!"})


@app.route("/streaming")
async def stream_foo_bar(request):
    """
    https://sanic.readthedocs.io/en/latest/sanic/response.html#streaming
    """

    async def streaming_fn(response):
        await response.write("foo")
        await response.write(".")
        await asyncio.sleep(0.5)
        await response.write(".")
        await asyncio.sleep(0.5)
        await response.write(".")
        await asyncio.sleep(1)
        await response.write(".")
        await asyncio.sleep(0.5)
        await response.write("bar")

    return response.stream(streaming_fn, content_type="text/plain")


def _get_embeddings_tensor(texts: Union[List[Text], Text]):
    """Returns a tf.Tensor from the model applied to the given text """
    log()
    if not isinstance(texts, list) and not isinstance(texts, str):
        raise ValueError(f"expected list or str but got {type(texts)}")
    texts = [texts] if type(texts) == str else texts
    # we pass in to the model only a single sentence
    tensor = app.model(texts)
    assert len(tensor) == 1, "weird tensorflow must have changed the output shape??"
    # so this function can expect to only ever return a single embedding
    tensor = tensor[0]
    # TODO: consider runtime differce of bulk passing sentences into tensorflow vs one-by-one  # noqa
    # TODO: I suspect tensorflow can take advantage of GPU to parallelize. It's ok for now.    # noqa
    return tensor


def _embed_as_list(texts: Union[List[Text], Text]) -> List[float]:
    """Returns a List from the model applied to the given text """
    log()
    return _get_embeddings_tensor(texts).numpy().tolist()


def _extract_data(data: dict) -> Tuple:
    x_index_name = data.get(INDEX_OR_EMBED_SCHEMA_KEYS.IDX.value)
    x_name = data.get(INDEX_OR_EMBED_SCHEMA_KEYS.NAM.value)
    x_class = data.get(INDEX_OR_EMBED_SCHEMA_KEYS.CLS.value)
    x_text = data.get(INDEX_OR_EMBED_SCHEMA_KEYS.TXT.value)
    x_embedding = _embed_as_list(x_text)
    return x_embedding, x_index_name, x_name, x_class, x_text


def _extract_bulk_request_data(request) -> Tuple:
    """
    Given a Sanic request,
    Return a tuple (embeddings, indexes, names, classifications, texts)
    Helps both /index_bulk and /embed_bulk routes
    """
    x_embeddings, x_indexes, x_names, x_classifications, x_texts = [], [], [], [], []
    for (x_embedding, x_index_name, x_name, x_class, x_text,) in _gen_bulk_request_data(
        request
    ):
        x_embeddings.append(x_embedding)
        x_indexes.append(x_index_name)
        x_names.append(x_name)
        x_classifications.append(x_class)
        x_texts.append(x_text)
    return (x_embeddings, x_indexes, x_names, x_classifications, x_texts)


def _gen_bulk_request_data(request) -> Tuple:
    """
    Given a Sanic request,
    Yield a tuple (embeddings, indexes, names, classifications, texts)
    """
    dicts = request.json.get("texts", [])
    for d in dicts:
        # unpacking the tuple first
        # ensures that this function returns what it promises
        x_embedding, x_index_name, x_name, x_class, x_text = _extract_data(d)
        yield x_embedding, x_index_name, x_name, x_class, x_text


@app.post("/embed")
@validate_json(EMBED_REQUEST_SCHEMA)
async def embed(request):
    """Returns the universal_sentence_encoder embeddings of the given text"""
    log(f"request.json: {request.json}")
    e, _, _, _, _ = _extract_data(request.json)
    return response.json(e)


@app.post("/embed_bulk")
@validate_json(EMBED_BULK_REQUEST_SCHEMA)
async def embed_bulk(request):
    """Returns the universal_sentence_encoder embeddings of the given list of text"""
    log(f"text: {request.json}")
    e, _, _, _, _ = _extract_bulk_request_data(request)
    return response.json(e)


async def index_and_log(es: AsyncElasticsearch, index_name: str, doc: str):
    log()
    res = await es.index(index=index_name, body=doc)
    log(f"called es.index ( {index_name} , body=`doc` ) and got res = {res}", info=True)
    return res


async def refresh_if_possible(index_name):
    # A refresh makes all operations performed on an index
    # since the last refresh available for search.
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-refresh.html
    # https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch.client.IndicesClient.refresh
    return await app.es.indices.refresh(
        index=index_name,
        # ignore any errors if index_name is no good
        ignore_unavailable=True,
        allow_no_indices=True,
    )


@app.post("/index")
@validate_json(INDEX_REQUEST_SCHEMA)
@depends_on_es(app)
async def index(request):
    """
    Given text and metadata,
    embed it with universal_sentence_encoder,
    then post to Elastic Search index
    """
    x_embedding, x_index_name, x_name, x_class, x_text = _extract_data(request.json)

    default_index_name = app.config.ELASTIC_SEARCH_DEFAULT_INDEX

    res = dict()

    # now do the indexing
    # https://elasticsearch-py.readthedocs.io/en/master/#example-usage
    res["res1"] = await create_index_if_not_exist(app.es, x_index_name)
    res["res2"] = await create_index_if_not_exist(app.es, default_index_name)

    doc = {
        DEFAULT_INDEX_MAPPING_KEYS.CLS.value: x_class,
        DEFAULT_INDEX_MAPPING_KEYS.NAM.value: x_name,
        DEFAULT_INDEX_MAPPING_KEYS.TXT.value: x_text,
        DEFAULT_INDEX_MAPPING_KEYS.TIM.value: datetime.now(),
        DEFAULT_INDEX_MAPPING_KEYS.EMD.value: x_embedding,
    }

    res["res3"] = await index_and_log(es=app.es, index_name=x_index_name, doc=doc)
    res["res4"] = await index_and_log(es=app.es, index_name=default_index_name, doc=doc)

    res["res5"] = await refresh_if_possible(index_name=x_index_name)
    res["res6"] = await refresh_if_possible(index_name=default_index_name)
    return response.json({**SUCCESS_DICT, **res}, SUCCESS)


@app.post("/index_bulk")
@validate_json(INDEX_BULK_REQUEST_SCHEMA)
@depends_on_es(app)
async def index_bulk(request):
    """
    Given text and metadata,
    embed it with universal_sentence_encoder,
    then post to Elastic Search index
    """
    # x_es, x_is, x_ns, x_cs, x_ts = _extract_bulk_request_data(request)
    log()

    default_index_name = app.config.ELASTIC_SEARCH_DEFAULT_INDEX
    index_names = [default_index_name]

    # https://elasticsearch-py.readthedocs.io/en/master/async.html#elasticsearch.helpers.async_bulk
    # https://elasticsearch-py.readthedocs.io/en/master/helpers.html#bulk-helpers
    async def _gen():
        for (
            x_embedding,
            x_index_name,
            x_name,
            x_class,
            x_text,
        ) in _gen_bulk_request_data(request):
            await create_index_if_not_exist(app.es, x_index_name)
            await create_index_if_not_exist(app.es, default_index_name)
            index_names.append(x_index_name)
            yield {
                "_index": x_index_name,
                # tell async_bulk that this should be an index operation
                # though, default is index
                "_op_type": "index",
                "doc": {
                    DEFAULT_INDEX_MAPPING_KEYS.CLS.value: x_class,
                    DEFAULT_INDEX_MAPPING_KEYS.NAM.value: x_name,
                    DEFAULT_INDEX_MAPPING_KEYS.TXT.value: x_text,
                    DEFAULT_INDEX_MAPPING_KEYS.TIM.value: datetime.now(),
                    DEFAULT_INDEX_MAPPING_KEYS.EMD.value: x_embedding,
                },
            }
        return

    num_docs = 0
    # await async_bulk(app.es, _gen())
    async for ok, result in async_streaming_bulk(app.es, _gen()):
        num_docs += 1
        action, result = result.popitem()
        if not ok:
            log(f"failed to {action} docuemnt {result}", info=True)

    # A refresh makes all operations performed on an index
    # since the last refresh available for search.
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-refresh.html
    for n in index_names:
        await refresh_if_possible(index_name=n)

    log(f"finished indexing {num_docs} docs", info=True)

    # now do the indexing
    return response.json(SUCCESS_DICT)


async def es_health_check(es: AsyncElasticsearch) -> bool:
    """Make sure the Elasticsearch connection is healthy.

    Resources:
    * https://sanic.readthedocs.io/en/latest/sanic/decorators.html
    """
    if not isinstance(es, AsyncElasticsearch):
        log(f"not isinstance(es, AsyncElasticsearch) {es}", info=True)
        log(f"app.es ?? {app.es}", info=True)
        return False

    if not await es.ping():
        return False

    return True


async def set_default_mappings(es: AsyncElasticsearch, index_name: str):
    log(info=True)
    return await es.indices.put_mapping(index=index_name, body=INDEX_MAPPINGS)


async def create_index_if_not_exist(
    es: AsyncElasticsearch, index_name: str, mapping: Optional[dict] = None
) -> bool:
    """
    Asynchronously setup the index_name with the given mapping dictionary

    Resources:
    * https://elasticsearch-py.readthedocs.io/en/master/async.html
    """
    log(info=True)
    if not await es_health_check(es):
        raise ValueError("problem with Elasticsearch or the client")

    # 400 means means resource_already_exists_exception
    res = await es.indices.create(index=index_name, body=mapping, ignore=[400])

    res["set_default_mappings"] = await set_default_mappings(
        es=es, index_name=index_name
    )

    return {**SUCCESS_DICT, **res}


# https://sanic.readthedocs.io/en/latest/sanic/middleware.html?highlight=listener
@app.middleware("request")
async def print_on_request(request):
    print("I print when a request is received by the server")


@app.middleware("response")
async def print_on_response(request, response):
    print("I print when a response is returned by the server")


def setup_es(app, loop):
    log()
    # SETUP CONNECTION TO ELASTICSEARCH
    app.es = AsyncElasticsearch(
        # could be multiple nodes
        hosts=[
            {
                "host": app.config.ELASTIC_SEARCH_HOST,
                "port": int(app.config.ELASTIC_SEARCH_PORT),
            }
        ],
        scheme=app.config.ELASTIC_SEARCH_SCHEME,
    )

    # SETUP ELASTICSEARCH INDICES

    # loop = asyncio.get_event_loop()
    log("let's make sure elastic is connected before anything else", info=True)

    def _do(f):
        async def _f(*args, **kwargs):
            res = await f(*args, **kwargs)
            print(f"\t{f.__name__}(): {res}")

        return _f

    _do(es_health_check)(app.es)
    _do(app.es.ping)()
    _do(create_index_if_not_exist)(
        es=app.es, index_name=app.config.ELASTIC_SEARCH_DEFAULT_INDEX
    )


def setup_model(app, loop):
    # SETUP TENSORFLOW MODEL
    app.model = initialize_model(app.config.MODULE_URL)


# https://sanic.readthedocs.io/en/latest/sanic/middleware.html?highlight=listener#listeners
@app.listener("before_server_start")
async def print_before_server_start(app, loop):
    log()
    print("loop", loop)
    # SETUP CONNECTION TO ELASTICSEARCH && SETUP ELASTICSEARCH INDICES
    setup_es(app, loop)
    # SETUP TENSORFLOW MODEL
    setup_model(app, loop)


@app.listener("after_server_start")
async def print_after_server_start(app, loop):
    print("print_after_server_start")


@app.listener("before_server_stop")
async def print_before_server_stop(app, loop):
    print("print_before_server_stop")
    await app.es.close()


@app.listener("after_server_stop")
async def print_after_server_stop(app, loop):
    print("print_after_server_stop")


if __name__ == "__main__":
    # SETUP ENVIRONMENT VARIABLES
    # https://sanic.readthedocs.io/en/latest/sanic/config.html#from-environment-variables
    # reads env vars start with NIMBUS_ and trims it off
    app.config.update(default_settings)
    app.config.load_environment_vars(prefix="NIMBUS_")
    for k, v in app.config.items():
        log(f"set env var  {k}: {v}", info=True)

    # SETUP DOCUMENTATION
    app.blueprint(swagger_blueprint)

    # RUN THE SERVER
    PORT = app.config.ELASTIC_TF_EMBED_WORKER_PORT
    DEBUG = app.config.ELASTIC_TF_EMBED_WORKER_DEBUG
    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)
