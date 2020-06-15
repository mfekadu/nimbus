"""
This module is a utility for downloading large models

Examples:
* spacy's `en_core_web_lg`
* anything from https://www.tensorflow.org/hub
* nltk stuff
* allennlp models
* etc

Usage
* just call the function you want

```
python -c "from model_utils import get_tfhub_sent_encoder; get_tfhub_sent_encoder()"
```

```
python -c "from model_utils import initialize_model; initialize_model(\"..url.\")"
```
"""
import tensorflow_hub as hub
from log_utils import log
from app_config import default_settings


hub.logging.set_verbosity("DEBUG")


def initialize_model(module_url):
    """Returns a Tensorflow model given the tfhub url."""
    log("\n\tdownloading model... (this will take a minute)\n", info=True)
    model = hub.load(module_url)
    log("done!")
    return model


def get_tfhub_sent_encoder_dan():
    log(info=True)
    url = default_settings.get("UNIVERSAL_SENTENCE_ENCODER_URL")
    assert url, f"unexpected url:{url}. check app_config.py"
    return initialize_model(url)


def get_tfhub_sent_encoder_transformer():
    log(info=True)
    url = default_settings.get("UNIVERSAL_SENTENCE_ENCODER_LARGE_URL")
    assert url, f"unexpected url:{url}. check app_config.py"
    return initialize_model(url)


def get_tfhub_sent_encoder():
    """
    chooses transformer by default
    """
    log(info=True)
    return get_tfhub_sent_encoder_transformer()


def get_spacy_large():
    log(info=True)
    raise NotImplementedError()


def get_spacy_small():
    log(info=True)
    raise NotImplementedError()


def get_spacy_medium():
    log(info=True)
    raise NotImplementedError()


def get_allennlp_srl():
    log(info=True)
    raise NotImplementedError()


def get_allennlp_openie():
    log(info=True)
    raise NotImplementedError()


def get_huggingface_qa():
    log(info=True)
    raise NotImplementedError()
