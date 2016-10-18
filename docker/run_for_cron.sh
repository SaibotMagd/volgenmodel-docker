#!/bin/bash

set -e
set -x

cd /home/carlo/production/volgenmodel-nipype-docker

./build.sh

docker run -i -t iatest-c/carlo/volgenmodel-nipype /bin/bash /opt/go.sh
