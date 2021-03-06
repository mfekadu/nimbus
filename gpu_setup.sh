#!/bin/sh


# https://cloud.google.com/compute/docs/gpus/install-drivers-gpu#ubuntu-driver-steps

curl -O http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub



sudo apt update -y


sudo apt install -y cuda


# Verifying the GPU driver install
nvidia-smi

