#!/bin/sh

# runs the `CMD` defined in the Dockerfile
sudo docker run \
    --detach \
    --publish 9010:9010 \
    -e "NIMBUS_ELASTIC_ALLENNLP_SRL_WORKER_PORT=9010" \
    --name nimbus-elastic-allennlp-srl-worker-standalone \
    nimbus-elastic-allennlp-srl-worker \
    "$@"
