#!/bin/sh

# only download models that are changed/new
gsutil rsync -r gs://nimbus-rasa-models-bucket-mf/models models
