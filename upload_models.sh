#!/bin/sh

# only upload models that are changed/new
gsutil rsync -r models gs://nimbus-rasa-models-bucket-mf/models
