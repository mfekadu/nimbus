"""
Honestly, [this blog post][1] convinced me there's no hard in trying Sanic for this
service. It seems like we can benefit from not installing gunicorn too because Sanic is
already asynchronous.

[1]: https://medium.com/@ahmed.nafies/is-sanic-python-web-framework-the-new-flask-2fe06b409fa3
"""


import asyncio
import tensorflow as tf
import tensorflow_hub as hub
from sanic import Sanic, response
from sanic_openapi import swagger_blueprint
from typing import List, Text, Union
from enum import Enum
from elasticsearch import Elasticsearch
from log_utils import log
from sanic_validation import validate_json


hub.logging.set_verbosity("DEBUG")

# https://sanic.readthedocs.io/en/latest/sanic/config.html
default_settings = {
    "ELASTIC_TF_EMBED_WORKER_PORT": 9010,
    "ELASTIC_TF_EMBED_WORKER_DEBUG": False,
    "ELASTIC_SEARCH_BASE_URL": None,
    "ELASTIC_SEARCH_INDEX_NAME": None,
    # These two encoders are 2 GB collectively.
    # Large one uses Transformer architecture.
    # Regular one used Deep Averaging Network (DAN)
    # Open links in browser to see a Google Colab
    "UNIVERSAL_SENTENCE_ENCODER_URL": "https://tfhub.dev/google/universal-sentence-encoder/4",
    "UNIVERSAL_SENTENCE_ENCODER_LARGE_URL": "https://tfhub.dev/google/universal-sentence-encoder-large/5",
    "MODULE_URL": "https://tfhub.dev/google/universal-sentence-encoder/4",
}


SUCCESS = 200

app = Sanic(__name__)
app.blueprint(swagger_blueprint)
# https://sanic.readthedocs.io/en/latest/sanic/config.html#from-environment-variables
# reads env vars start with NIMBUS_ and trims it off
app.config.update(default_settings)
app.config.load_environment_vars(prefix="NIMBUS_")
for k, v in app.config.items():
    log(f"{k}: {v}")


model = None


class EMBEDDING_SCHEMA_KEYS(Enum):
    NAM = "name"
    CLS = "classification"
    TXT = "text"


EMBEDDING_REQUEST_SCHEMA = {
    EMBEDDING_SCHEMA_KEYS.NAM.value: {"type": "string", "required": True},
    EMBEDDING_SCHEMA_KEYS.CLS.value: {"type": "string", "required": True},
    EMBEDDING_SCHEMA_KEYS.TXT.value: {"type": "string", "required": True},
}
"""
Example:

{
    "name": "Something",
    "classification": "question",
    "text": "What is Something?"
}
"""

EMBEDDING_BULK_REQUEST_SCHEMA = {
    "texts": {
        "type": "list",
        "items": [
            {
                "type": "dict",
                "schema": {
                    EMBEDDING_SCHEMA_KEYS.NAM.value: {
                        "type": "string",
                        "required": True,
                    },
                    EMBEDDING_SCHEMA_KEYS.CLS.value: {
                        "type": "string",
                        "required": True,
                    },
                    EMBEDDING_SCHEMA_KEYS.TXT.value: {
                        "type": "string",
                        "required": True,
                    },
                },
            }
        ],
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


def get_embeddings_tensor(texts: Union[List[Text], Text]):
    """Returns a tf.Tensor from the model applied to the given text """
    log()
    if not isinstance(texts, list) and not isinstance(texts, str):
        raise ValueError(f"expected list or str but got {type(texts)}")
    texts = [texts] if type(texts) == str else texts
    return model(texts)


@app.get("/")
async def hello(request):
    log()
    return response.json({"message": "Hello, Friend!"})


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


@app.post("/embed")
@validate_json(EMBEDDING_REQUEST_SCHEMA)
async def embed(request):
    """Returns the universal_sentence_encoder embeddings of the given text"""
    log(f"request.json: {request.json}")
    text = request.json.get("text", None)
    e = get_embeddings_tensor(text)
    return response.json(e.numpy().tolist())


@app.post("/embed_bulk")
@validate_json(EMBEDDING_BULK_REQUEST_SCHEMA)
async def embed_bulk(request):
    """Returns the universal_sentence_encoder embeddings of the given list of text"""
    log(f"text: {request.json}")
    dicts = request.json.get("texts", [])
    # names = [d.get(EMBEDDING_SCHEMA_KEYS.NAM.value) for d in dicts]
    # classes = [d.get(EMBEDDING_SCHEMA_KEYS.CLS.value) for d in dicts]
    texts = [d.get(EMBEDDING_SCHEMA_KEYS.TXT.value) for d in dicts]
    e = get_embeddings_tensor(texts)
    return response.json(e.numpy().tolist())


if __name__ == "__main__":

    PORT = app.config.ELASTIC_TF_EMBED_WORKER_PORT
    DEBUG = app.config.ELASTIC_TF_EMBED_WORKER_DEBUG

    initialize_model(app.config.MODULE_URL)

    client = Elasticsearch()

    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)
