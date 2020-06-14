#!/bin/sh

export NIMBUS_ELASTIC_TF_EMBED_WORKER_PORT=9010
export NIMBUS_ELASTIC_TF_EMBED_WORKER_DEBUG=True

export MODULE_URL="https://tfhub.dev/google/universal-sentence-encoder/4" # "https://tfhub.dev/google/universal-sentence-encoder-large/5"

# run the app locally
python3 app.py
