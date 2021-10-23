#!/bin/bash

set -e 

pushd ./src/
docker build -t distributed-pi-server -f ./server/Dockerfile .
docker build -t distributed-pi-client -f ./client/Dockerfile .
docker build -t distributed-pi-renderer -f ./renderer/Dockerfile .
docker build -t distributed-pi-verifier -f ./verifier/Dockerfile .
popd