#!/bin/bash

export PATH=$PATH:/usr/local/bin:/usr/bin:/bin

cd /opt/code/minc-toolkit/
rm -fr build
mkdir build
cd build
cmake -DMT_BUILD_SHARED_LIBS=ON -DMT_BUILD_VISUAL_TOOLS=ON ..
make install
echo 'export LD_LIBRARY_PATH=/usr/local/lib/' >> /etc/bash.bashrc
