#!/bin/sh

if [ ! "$@" ]; then
    echo "USAGE:"
    echo
    echo "./rm_container.sh CONTAINER"

    echo
    echo "HERE IS A LIST OF CONTAINER..."
    echo

    sudo docker container list

    exit
fi

echo "stopping $1 ..."
sudo docker container stop "$1"
echo "removing $1 ..."
sudo docker container rm "$1"

