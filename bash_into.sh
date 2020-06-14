#!/bin/sh

if [ ! "$@" ]; then
    echo "USAGE:"
    echo
    echo "./bash_into.sh CONTAINER"

    echo
    echo "HERE IS A LIST OF CONTAINERS..."
    echo

    docker container list --format "table {{.ID}}\t{{.Names}}\t{{.Command}}\t{{.Ports}}"

    exit
fi

docker exec -it "$1" /bin/bash; exit
