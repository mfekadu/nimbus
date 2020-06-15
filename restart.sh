#!/bin/sh

if [ ! "$@" ]; then
    echo "USAGE:"
    echo
    echo "./restart.sh CONTAINER"

    echo
    echo "HERE IS A LIST OF CONTAINERS..."
    echo

    sudo docker container list --format "table {{.ID}}\t{{.Names}}\t{{.Command}}\t{{.Ports}}"

    exit
fi

sudo docker container restart "$1"
