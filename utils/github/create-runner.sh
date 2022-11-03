#!/bin/bash

if [ $# -ne 1 ]; then
  echo "You must specify an SSH key to use in the connection"
  exit
fi
KEY=$1

# create the resource group
az group create --name SystemTestHostedRunner --location uksouth

# create the vm in the resources group
az vm create --resource-group SystemTestHostedRunner --name LocalTestnetRunner \
  --image Canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2:20.04.202206220  \
  --admin-username azureuser --ssh-key-values $KEY

# run installation steps
az vm run-command invoke \
  --resource-group SystemTestHostedRunner \
  --name LocalTestnetRunner \
  --command-id RunShellScript \
  --scripts "apt update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:ethereum/ethereum \
    && apt update \
    && apt install -y solc \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install console-stamp --global \
    && npm install web3 --global \
    && npm install ethers --global \
    && npm install commander --global  \
    && npm install -g ganache  \
    && npm install -g ganache-cli \
    && apt install -y vim \
    && apt install -y python3-pip \
    && python3 -m pip install web3 \
    && python3 -m pip install pysys==1.6.1 \
    && python3 -m pip install py-solc-x \
    && snap install go --classic \
    && curl -fsSL https://get.docker.com -o get-docker.sh \
    && sh ./get-docker.sh"
