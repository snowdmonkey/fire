#!/usr/bin/env bash

docker run -d --name=kafka -p 2181:2181 -p 9092:9092 \
--env ADVERTISED_HOST=172.26.174.105 \
--env ADVERTISED_PORT=9092 \
spotify/kafka