#!/bin/sh

if [ ! "$@" ]; then
    echo "USAGE:"
    echo
    echo "./rm_image.sh IMAGE"

    echo
    echo "HERE IS A LIST OF IMAGE..."
    echo

    sudo docker image list

    exit
fi

sudo docker image rm "$1"

