#!/bin/bash

# Flaky script to WIPE ALL THE DOCKER CONTAINERS!!!!! AND IMAGES!!!!!

docker ps -a | awk '{print $1}' | grep -v CONTAINER | xargs -n 1 docker kill
docker ps -a | awk '{print $1}' | grep -v CONTAINER | xargs -n 1 docker rm
docker images | awk '{print $3}' | grep -v IMAGE | xargs -n 1 docker rmi
