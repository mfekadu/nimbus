"""
Honestly, [this blog post][1] convinced me there's no hard in trying Sanic for this
service. It seems like we can benefit from not installing gunicorn too because Sanic is
already asynchronous.

[1]: https://medium.com/@ahmed.nafies/is-sanic-python-web-framework-the-new-flask-2fe06b409fa3
"""

import random
import asyncio
import tensorflow as tf
import tensorflow_hub as hub
from sanic import Sanic, response
from sanic_openapi import swagger_blueprint
from typing import List, Text, Union, Tuple
from enum import Enum
from elasticsearch import AsyncElasticsearch
from log_utils import log
from sanic_validation import validate_json


hub.logging.set_verbosity("DEBUG")

# https://sanic.readthedocs.io/en/latest/sanic/config.html
default_settings = {
    "ELASTIC_TF_EMBED_WORKER_PORT": 9010,
    "ELASTIC_TF_EMBED_WORKER_DEBUG": False,
    "ELASTIC_SEARCH_SCHEME": "http",
    "ELASTIC_SEARCH_HOST": "localhost",
    "ELASTIC_SEARCH_PORT": 9200,
    "ELASTIC_SEARCH_INDEX_NAME": "default_index",
    # These two encoders are 2 GB collectively.
    # Large one uses Transformer architecture.
    # Regular one used Deep Averaging Network (DAN)
    # Open links in browser to see a Google Colab
    "UNIVERSAL_SENTENCE_ENCODER_URL": "https://tfhub.dev/google/universal-sentence-encoder/4",
    "UNIVERSAL_SENTENCE_ENCODER_LARGE_URL": "https://tfhub.dev/google/universal-sentence-encoder-large/5",
    "MODULE_URL": "https://tfhub.dev/google/universal-sentence-encoder/4",
}


SUCCESS = 200
SUCCESS_DICT = {"completed": True}
FAILURE_DICT = {"completed": False}

app = Sanic(__name__)

model = None
es = None


class STD_KEYS(Enum):
    """
    An enum of standard keys to keep things consistent
    """

    IDX = "index_name"
    NAM = "name"
    CLS = "classification"
    TXT = "text"


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
        "items": [{"type": "dict", "schema": EMBED_REQUEST_SCHEMA}],
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
        "items": [{"type": "dict", "schema": INDEX_REQUEST_SCHEMA}],
        "required": True,
    }
}


def initialize_model(module_url):
    """Returns a Tensorflow model given the tfhub url."""
    # TODO: make this asynchronous? download can take a while.
    # Would be nice to have quick availability of API
    # that way API could reponse with something like {"ready": false} until DL is done
    global model
    log("\n\tdownloading model... (this will take a minute)\n")
    model = hub.load(module_url)
    log("done!")
    return model


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
    return model(texts)


def _embed_as_list(texts: Union[List[Text], Text]) -> List[float]:
    """Returns a List from the model applied to the given text """
    log()
    return _get_embeddings_tensor(texts).numpy().tolist()


def _extract_data(data: dict) -> Tuple:
    i = data.get(INDEX_OR_EMBED_SCHEMA_KEYS.IDX.value)
    n = data.get(INDEX_OR_EMBED_SCHEMA_KEYS.NAM.value)
    c = data.get(INDEX_OR_EMBED_SCHEMA_KEYS.CLS.value)
    t = data.get(INDEX_OR_EMBED_SCHEMA_KEYS.TXT.value)
    e = _embed_as_list(t)
    return e, i, n, c, t


def _extract_bulk_request_data(request) -> Tuple:
    """
    Given a Sanic request,
    Return a tuple (embeddings, indexes, names, classifications, texts)
    Helps both /index_bulk and /embed_bulk routes
    """
    dicts = request.json.get("texts", [])
    indexes, names, classifications, texts, embeddings = [], [], [], [], []
    for d in dicts:
        e, i, n, c, t = _extract_data(d)
        indexes.append(i)
        names.append(n)
        classifications.append(c)
        texts.append(t)
        embeddings.append(e)
    return (embeddings, indexes, names, classifications, texts)


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


@app.post("/index")
@validate_json(INDEX_REQUEST_SCHEMA)
async def index(request):
    """
    Given text and metadata,
    embed it with universal_sentence_encoder,
    then post to Elastic Search index
    """
    e, i, n, c, t = _extract_data(request.json)
    # now do the indexing
    return response.json(SUCCESS_DICT)


@app.post("/index_bulk")
@validate_json(INDEX_BULK_REQUEST_SCHEMA)
async def index_bulk(request):
    """
    Given text and metadata,
    embed it with universal_sentence_encoder,
    then post to Elastic Search index
    """
    e, i, n, c, t = _extract_bulk_request_data(request)
    # now do the indexing
    return response.json(SUCCESS_DICT)


async def setup_index(
    es: AsyncElasticsearch, index_name: str, mapping: dict = dict()
) -> bool:
    """
    Asynchronously setup the index_name with the given mapping dictionary

    Resources:
    * https://elasticsearch-py.readthedocs.io/en/master/async.html
    """
    log(info=True)
    if not isinstance(es, AsyncElasticsearch):
        raise ValueError("elasticsearch not initialized")
    if not await es.ping():
        raise ValueError("elasticsearch service is not healthy")

    # 400 means means resource_already_exists_exception
    res = await es.indices.create(index=index_name, body=mapping, ignore=[400])

    return {**SUCCESS_DICT, **res}


# https://sanic.readthedocs.io/en/latest/sanic/middleware.html?highlight=listener
@app.middleware("request")
async def print_on_request(request):
    print("I print when a request is received by the server")


@app.middleware("response")
async def print_on_response(request, response):
    print("I print when a response is returned by the server")


# https://sanic.readthedocs.io/en/latest/sanic/middleware.html?highlight=listener#listeners
@app.listener("before_server_start")
async def print_before_server_start(app, loop):
    print("print_before_server_start")
    print("loop", loop)

    # SETUP TENSORFLOW MODEL
    initialize_model(app.config.MODULE_URL)

    # SETUP CONNECTION TO ELASTICSEARCH
    es = AsyncElasticsearch(
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
    await setup_index(es=es, index_name=app.config.ELASTIC_SEARCH_INDEX_NAME)


@app.listener("after_server_start")
async def print_after_server_start(app, loop):
    print("print_after_server_start")


@app.listener("before_server_stop")
async def print_before_server_stop(app, loop):
    print("print_before_server_stop")
    await es.close()


@app.listener("after_server_stop")
async def print_after_server_stop(app, loop):
    print("print_after_server_stop")


if __name__ == "__main__":
    # SETUP DOCUMENTATION
    app.blueprint(swagger_blueprint)

    # SETUP ENVIRONMENT VARIABLES
    # https://sanic.readthedocs.io/en/latest/sanic/config.html#from-environment-variables
    # reads env vars start with NIMBUS_ and trims it off
    app.config.update(default_settings)
    app.config.load_environment_vars(prefix="NIMBUS_")
    for k, v in app.config.items():
        log(f"{k}: {v}", info=True)

    # RUN THE SERVER
    PORT = app.config.ELASTIC_TF_EMBED_WORKER_PORT
    DEBUG = app.config.ELASTIC_TF_EMBED_WORKER_DEBUG
    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)
