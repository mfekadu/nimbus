#!/bin/sh

export NIMBUS_ELASTIC_ALLENNLP_SRL_WORKER_PORT=9010
export NIMBUS_ELASTIC_ALLENNLP_SRL_WORKER_DEBUG=True

export MODULE_URL="https://tfhub.dev/google/universal-sentence-encoder-large/5" # "https://tfhub.dev/google/universal-sentence-encoder/4"

# https://github.com/tensorflow/hub/issues/25
export TFHUB_DOWNLOAD_PROGRESS=1

# run the app locally
python3 app.py
