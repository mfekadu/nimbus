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
from log_utils import log, warn
from sanic_validation import validate_json
from functools import wraps
from datetime import datetime
from model_utils import initialize_model
from itertools import chain, groupby
from app_config import default_settings


SUCCESS = 200
FAILURE = 500  # TODO: return useful statuses https://www.restapitutorial.com/httpstatuscodes.html
SUCCESS_DICT = {"completed": True}
FAILURE_DICT = {"completed": False}

app = Sanic(__name__)
# SETUP ENVIRONMENT VARIABLES
# https://sanic.readthedocs.io/en/latest/sanic/config.html#from-environment-variables
# reads env vars start with NIMBUS_ and trims it off
app.config.update(default_settings)
app.config.load_environment_vars(prefix="NIMBUS_")
for k, v in app.config.items():
    log(f"set env var  {k}: {v}", info=True)


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

    DOC = "doc"  # refers to a document object that encapsulates the NAM/EMD/TXT/etc...
    IDX = "index_name"  # the ElasticSearch index on which we perform index/query
    NAM = "name"  # the name (title) of the document # TODO: refactor/rename this to be Title
    CLS = "classification"  # any kind of classification (e.g. Question/Sentence/etc)
    TXT = "text"  # the actual text to be embedded/indexed
    TIM = "timestamp"  # the current timestamp
    EMD = "embedding"  # the actual embedding of the TXT
    BULK_TEXTS = "texts"  # a list of EMBED_REQUEST_SCHEMA


class DEFAULT_INDEX_MAPPING_KEYS(Enum):
    DOC = STD_KEYS.DOC.value
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


class QUERY_SCHEMA_KEYS(Enum):
    TXT = STD_KEYS.TXT.value


def enum_left_join(e1: Enum, e2: Enum, new_enum_name: str = None) -> Enum:
    """
    Given two Enums, return an enum that is the left_join of both enums.

    Resource:
    * https://stackoverflow.com/questions/33679930/how-to-extend-python-enum
    """
    new_enum_name = new_enum_name or f"{e1.__name__}_OR_{e2.__name__}"
    # the following will be [e1_1, e2_1, e1_2, e2_2, e1_3, e2_3, ..., e1_n, e2_n]
    left_first_chain_generator = ((x.name, x.value) for x in chain(e1, e2))
    sorted_left_first = sorted(left_first_chain_generator, key=lambda tup: tup[0])
    left_first_enum_keys = [
        list(v)[0] for _, v in groupby(sorted_left_first, lambda z: z[0])
    ]
    return Enum(new_enum_name, left_first_enum_keys)


class TEST_1(Enum):
    A = 1
    B = 2
    C = 3


class TEST_2(Enum):
    B = 4
    C = 5
    D = 6


output = enum_left_join(TEST_1, TEST_2)
assert output.__name__ == f"{TEST_1.__name__}_OR_{TEST_2.__name__}"
assert output.A.value == 1
assert output.B.value == 2
assert output.C.value == 3
assert output.D.value == 6

INDEX_OR_EMBED_SCHEMA_KEYS = enum_left_join(
    INDEX_SCHEMA_KEYS, EMBED_SCHEMA_KEYS, "INDEX_OR_EMBED_SCHEMA_KEYS"
)


QUERY_REQUEST_SCHEMA = {
    # https://cerberus-sanhe.readthedocs.io/usage.html#empty
    QUERY_SCHEMA_KEYS.TXT.value: {"type": "string", "required": True, "empty": False},
}


EMBED_REQUEST_SCHEMA = {
    # https://cerberus-sanhe.readthedocs.io/usage.html#empty
    EMBED_SCHEMA_KEYS.NAM.value: {"type": "string", "required": True, "empty": False},
    EMBED_SCHEMA_KEYS.CLS.value: {"type": "string", "required": True, "empty": False},
    EMBED_SCHEMA_KEYS.TXT.value: {"type": "string", "required": True, "empty": False},
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
    STD_KEYS.BULK_TEXTS.value: {
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
    # https://cerberus-sanhe.readthedocs.io/usage.html#empty
    INDEX_SCHEMA_KEYS.IDX.value: {"type": "string", "required": True, "empty": False},
    INDEX_SCHEMA_KEYS.NAM.value: {"type": "string", "required": True, "empty": False},
    INDEX_SCHEMA_KEYS.CLS.value: {"type": "string", "required": True, "empty": False},
    INDEX_SCHEMA_KEYS.TXT.value: {"type": "string", "required": True, "empty": False},
}

INDEX_BULK_REQUEST_SCHEMA = {
    STD_KEYS.BULK_TEXTS.value: {
        "type": "list",
        "schema": {"type": "dict", "schema": INDEX_REQUEST_SCHEMA},
        "required": True,
    }
}

INDEX_MAPPINGS = {
    # https://www.elastic.co/guide/en/elasticsearch/reference/7.7/indices-put-mapping.html#indices-put-mapping
    "properties": {
        DEFAULT_INDEX_MAPPING_KEYS.DOC.value: {
            "properties": {
                DEFAULT_INDEX_MAPPING_KEYS.CLS.value: {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                DEFAULT_INDEX_MAPPING_KEYS.EMD.value: {
                    "type": "dense_vector",
                    "dims": 512,
                },
                "name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                DEFAULT_INDEX_MAPPING_KEYS.TXT.value: {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                DEFAULT_INDEX_MAPPING_KEYS.TIM.value: {"type": "date"},
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
    list_of_tensors = app.model(texts)
    assert (
        len(list_of_tensors) == 1
    ), "weird tensorflow must have changed the output shape??"
    # so this function can expect to only ever return a single embedding
    tensor = list_of_tensors[0]
    if len(tensor) != 512:  # TODO: make a config variable TENSOR_LENGTH = 512
        warn(
            f"WARNING (MAY CAUSE ERRORS!!) expected len(tensor) == 512 but got {len(tensor)}"  # noqa
            "\n"
            "if there is no error then you should consider modifying this code in app.py"  # noqa
            "\n"
            "consider parameterizing the TENSOR_LENGTH because you may have downloaded a new/different model"  # noqa
            "\n"
            "honestly, I think this warning will never show, but if it does... nice :)"
        )
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
    dicts = request.json.get(STD_KEYS.BULK_TEXTS.value, [])
    for d in dicts:
        # unpacking the tuple first
        # ensures that this function returns what it promises
        x_embedding, x_index_name, x_name, x_class, x_text = _extract_data(d)
        yield x_embedding, x_index_name, x_name, x_class, x_text


def make_elastic_query_request_for_cosine_similarity(
    size: int,
    script_string: str,
    query_vector: List[float],
    keys_to_include_in_result: List[str],
) -> dict:
    """
    Returns a dictionary that adheres to ElasticSearch's
    query-dsl-script-score-query for  _dense_vector_functions
    using the built in cosineSimilarity function.

    Resources:
    * https://www.elastic.co/guide/en/elasticsearch/reference/7.7/query-dsl-script-score-query.html#_dense_vector_functions
    """
    return {
        "size": size,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": script_string,
                    "params": {"query_vector": query_vector},
                },
            }
        },
        "_source": {"includes": keys_to_include_in_result},
    }


async def search(
    es: AsyncElasticsearch,
    query_string: str,
    index_name: str = app.config.ELASTIC_SEARCH_DEFAULT_INDEX,
    size: int = app.config.ELASTIC_SEARCH_DEFAULT_QUERY_SIZE,
    doc_key: str = DEFAULT_INDEX_MAPPING_KEYS.DOC.value,
    emd_key: str = DEFAULT_INDEX_MAPPING_KEYS.EMD.value,
    includes: List[str] = [
        DEFAULT_INDEX_MAPPING_KEYS.CLS.value,
        DEFAULT_INDEX_MAPPING_KEYS.TXT.value,
        DEFAULT_INDEX_MAPPING_KEYS.NAM.value,
    ],
):
    """Returns the top 25 (by default) Elasticsearch results of a simple query_string

    Resources:
    * https://elasticsearch-py.readthedocs.io/en/master/async.html#elasticsearch.AsyncElasticsearch.search
    * https://www.elastic.co/guide/en/elasticsearch/reference/7.7/query-dsl-script-score-query.html#_dense_vector_functions
    """
    log()
    query_vector = _embed_as_list(query_string)

    my_dense_vector_accessor = f"{doc_key}.{emd_key}"  # defaults to "doc.embedding"
    #                                     ^ (notice the `.` dot in between)
    # the `.` dot is NOT referenced in the documentation.
    # rather the documentation suggests to script something like doc['embedding']
    # that failed when I tried it.
    # Very weird. Maybe their script is a broken subset of JavaScript?
    # Either way, we use the dot. Thank you, dot!

    keys_to_include_in_result = [f"{doc_key}.{subkey}" for subkey in includes]

    script_string = (
        f"cosineSimilarity(params.query_vector, '{my_dense_vector_accessor}') + 1.0"
    )

    request_body = make_elastic_query_request_for_cosine_similarity(
        size, script_string, query_vector, keys_to_include_in_result,
    )

    warn(f"searching on the index_name: {index_name}")

    warn(f"the elasticsearch query body looks like:\n {request_body}")

    res = await es.search(
        index=index_name,
        body=request_body,
        # ignore any errors if index_name is no good
        ignore_unavailable=True,
        allow_no_indices=True,
        allow_partial_search_results=True,
        ignore_throttled=True,
    )

    log(
        f"called es.search ( {index_name} , body={request_body} ) and got res = {res}",
        info=True,
    )

    return res


@app.post("/query")
@validate_json(QUERY_REQUEST_SCHEMA)
async def query(request):
    """
    Returns the top SIZE (default 25) Elasticsearch results of a simple query_string

    TODO: this endpoint is for simple queries (just text input) so...
    TODO: consider making an `advanced_query` endpoint...
    TODO: that further parameterizs the `search` function.

    Resources:
    * https://www.elastic.co/guide/en/elasticsearch/reference/7.7/search.html
    * https://elasticsearch-py.readthedocs.io/en/master/async.html#elasticsearch.AsyncElasticsearch.search
    """
    log(f"request.json: {request.json}")
    data = request.json.get(STD_KEYS.TXT.value, "")
    if not data:
        return response.json(FAILURE_DICT, FAILURE)
    result = await search(es=app.es, query_string=data)
    return response.json(result)


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
                DEFAULT_INDEX_MAPPING_KEYS.DOC.value: {
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
    # SETUP DOCUMENTATION
    app.blueprint(swagger_blueprint)

    # RUN THE SERVER
    PORT = app.config.ELASTIC_TF_EMBED_WORKER_PORT
    DEBUG = app.config.ELASTIC_TF_EMBED_WORKER_DEBUG
    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)
