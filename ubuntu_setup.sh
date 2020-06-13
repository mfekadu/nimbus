#!/bin/bash
set -Eeuo pipefail

#######################################
#
# installing pip and python and docker and poetry 
#
#######################################

source /etc/os-release

echo "Installing pip & python & docker"

sudo apt-get update -y
sudo apt-get install -y python3
sudo apt-get install -y python3-distutils || :  # if the package is not available and the command fails, do nothing,
                                                # the distutils are already installed
sudo apt-get install gcc libpq-dev -y
sudo apt-get install python-dev python-pip -y
sudo apt-get install python3-dev python3-pip python3-venv python3-wheel -y


##curl -O https://bootstrap.pypa.io/get-pip.py
#sudo python3 get-pip.py
#rm get-pip.py

sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common


# echo >> ~/.bashrc && echo "alias python=python3" >> ~/.bashrc && echo >> ~/.bashrc 
# echo "REMEMBER TO RUN `source ~/.bashrc` and `$HOME/.poetry/env`" 
# sudo ln /usr/bin/python3  /usr/bin/python || :

#
# poetry
#

curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3

#
# docker
#

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

echo "now get docker-compose"

sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose || :

sudo curl -L https://raw.githubusercontent.com/docker/compose/1.26.0/contrib/completion/bash/docker-compose -o /etc/bash_completion.d/docker-compose




