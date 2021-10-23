# distributed-pi

## Overview

There are 4 logical units used in this pipeline:

- The **distributed-pi-server** sends jobs out to and receives completed work from clients
- The **distributed-pi-client** requests jobs from the server and performs the computation of base-16 digits for a given range.
- The **distributed-pi-renderer** takes the base-16 results submitted by the clients and concatenates the results into a base 16 render, which is the largest contiguous region of submitted results. It then takes the base-16 render and converts it to a base-10 decimal number.
- The **distributed-pi-verifier** checks the base-16 results for any gaps and creates prioritized jobs for the server to distribute.

## Prerequisites

Install Docker.

## Setup

```shell
./build.sh
```

## Running

Start the MongoDB instance:

```shell
sudo docker run --name=mongo -p 27017:27017 --rm -d -v /path/to/mongo/data:/data/db mongo
```

Start the server instances (they will synchronize using the MongoDB instance):

```shell
sudo docker run --rm -d -p 8081:8080 -e DB_URI=mongodb://<mongodb-ip>:27017/distributed-pi distributed-pi-server
```

Start the clients:

```shell
sudo docker run --rm -d --name=distributed-pi-client -e BASE_SERVER_URI=http://<distributed-pi-server-ip>:8080 -e NUM_WORKERS=16 distributed-pi-client
```

Start verifiers:

```shell
sudo docker run --rm -d --name=distributed-pi-verifier -e BASE16_VERIFIER_INTERVAL=300 -e DB_URI=mongodb://<mongodb-ip>:27017/distributed-pi distributed-pi-verifier
```

Start renderers:

```shell
sudo docker run --rm -d --name=distributed-pi-renderer -p 8081:8080 -e DB_URI=mongodb://<mongodb-ip>:27017/distributed-pi distributed-pi-renderer
```
