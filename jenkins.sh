#!/usr/bin/env bash

cd docker
docker-compose build
docker-compose push
docker stack deploy --compose-file=docker-compose.yml  --with-registry-auth fire