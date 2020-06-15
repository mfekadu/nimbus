# https://sanic.readthedocs.io/en/latest/sanic/config.html
default_settings = {
    "ELASTIC_TF_EMBED_WORKER_PORT": 9010,
    "ELASTIC_TF_EMBED_WORKER_DEBUG": False,
    "ELASTIC_SEARCH_SCHEME": "http",
    "ELASTIC_SEARCH_HOST": "localhost",
    "ELASTIC_SEARCH_PORT": 9200,
    "ELASTIC_SEARCH_DEFAULT_INDEX": "default_index",
    # These two encoders are 2 GB collectively.
    # Large one uses Transformer architecture.
    # Regular one used Deep Averaging Network (DAN)
    # Open links in browser to see a Google Colab
    "UNIVERSAL_SENTENCE_ENCODER_URL": "https://tfhub.dev/google/universal-sentence-encoder/4",
    "UNIVERSAL_SENTENCE_ENCODER_LARGE_URL": "https://tfhub.dev/google/universal-sentence-encoder-large/5",
    "MODULE_URL": "https://tfhub.dev/google/universal-sentence-encoder/4",
}
