#!/bin/bash
set -Eeuo pipefail

#######################################
#
# installing pip and python and docker 
#
#######################################

source /etc/os-release

echo "Installing pip & python & docker"

sudo apt-get update -y
sudo apt-get install -y python3
sudo apt-get install -y python3-distutils || :  # if the package is not available and the command fails, do nothing,
                                                # the distutils are already installed


curl -O https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py

sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common


curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io


