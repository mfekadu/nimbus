#!/bin/sh

rasa train \
    -vv \
    --data data/ \
    --config config.yml \
    --domain domain.yml \
    --out models/

rasa test \
    -vv \
    --endpoints endpoints_local_model.yml \
    --model models/ \
    --stories tests/ \
    --nlu data/ \
    --out results/
