#!/bin/sh

if [ ! "$@" ]; then
    echo "USAGE:"
    echo
    echo "./show_logs_of.sh CONTAINER"

    echo
    echo "HERE IS A LIST OF CONTAINERS..."
    echo

    sudo docker container list --format "table {{.ID}}\t{{.Names}}\t{{.Command}}\t{{.Ports}}"

    exit
fi

sudo docker logs --follow "$1"
