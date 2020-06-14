#!/bin/sh

echo "sudo docker login"
echo
echo "you may need your sudo password first... then hub.docker.com username/password"
echo
sudo docker login

echo
echo "okay now manually run the following..."
echo
echo "sudo docker push <account_username>/<repository_name>:<custom_image_tag>"
