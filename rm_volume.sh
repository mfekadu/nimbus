#!/bin/sh

if [ ! "$@" ]; then
    echo "USAGE:"
    echo
    echo "./rm_volume.sh VOLUME"

    echo
    echo "HERE IS A LIST OF VOLUME..."
    echo

    sudo docker volume list

    exit
fi

echo "removing $1 ..."
sudo docker volume rm "$1"

