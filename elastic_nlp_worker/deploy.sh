#!/bin/sh

# runs the `CMD` defined in the Dockerfile
docker run \
    --detach \
    --publish 9010:9010 \
    -e "NIMBUS_ELASTIC_NLP_WORKER_PORT=9010" \
    --name nimbus-elastic-nlp-worker-standalone \
    nimbus-elastic-nlp-worker
