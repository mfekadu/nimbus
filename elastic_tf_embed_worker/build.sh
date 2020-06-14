#!/bin/sh
# -t just gives a name to this image
# expects Dockerfile in the "." directory
sudo docker build -t nimbus-elastic-tf-embed-worker .
