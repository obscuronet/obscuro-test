#!/usr/bin/env bash
# Script to run the latest image of the VM for running obscuro test
#

docker run -it -e DOCKER_TEST_ENV=true --network=node_network obscuronet/obscuro_test:latest