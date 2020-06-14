#!/bin/sh

# runs the `CMD` defined in the Dockerfile
sudo docker run \
    --detach \
    --publish 9010:9010 \
    -e "NIMBUS_ELASTIC_TF_EMBED_WORKER_PORT=9010" \
    --name nimbus-elastic-tf-embed-worker-standalone \
    nimbus-elastic-tf-embed-worker
