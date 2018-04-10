#!/usr/bin/env bash

function build_base()
{
    docker build -t fire/base:1.0 -f ../docker/fire_python_base/Dockerfile ..
}

function build_controller()
{
    docker build -t fire/controller -f ../docker/controller/Dockerfile ..
}

function build_analyst()
{
    docker build -t fire/analyst -f ../docker/analyst/Dockerfile ..
}

if [ "$1" == "base" ]; then
    build_base
elif [ "$1" == "analyst" ]; then
    build_analyst
elif [ "$1" == "controller" ]; then
    build_controller
else
    echo "Usage: build.sh COMMAND"
    echo "base for building base image"
    echo "analyst for building analyst image"
    echo "controller for building controller image"
fi