# Experimental Docker notes

Like the Vagrant notes, these are just for testing at the moment.

## Install Docker on Debian/Ubuntu

Quick install on Debian/Ubuntu, thanks to
https://coderwall.com/p/wlhavw

    echo deb http://get.docker.io/ubuntu docker main | sudo tee /etc/apt/sources.list.d/docker.list
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
    sudo apt-get update
    sudo apt-get install -y lxc-docker

## Build the volgenmodel image

Build the image, tagging it with a description:

    mkdir tmp
    cd tmp
    wget https://raw.githubusercontent.com/carlohamalainen/volgenmodel-nipype/master/docker/Dockerfile
    docker build -t="ouruser/volgenmodel:v1" . # note the trailing dot

Look at the images. The top one is the one with all of our changes.

    $ docker images
    REPOSITORY            TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
    ouruser/volgenmodel   v1                  d2c3c059eb23        39 seconds ago      1.217 GB
    debian                rc-buggy            350a74df81b1        6 days ago          159.9 MB
    debian                experimental        36d6c9c7df4c        6 days ago          159.9 MB
    debian                squeeze             3b36e4176538        7 days ago          112.4 MB
    debian                6.0.9               3b36e4176538        7 days ago          112.4 MB
    debian                wheezy              667250f9a437        7 days ago          115 MB
    debian                7.5                 667250f9a437        7 days ago          115 MB
    debian                latest              667250f9a437        7 days ago          115 MB
    debian                unstable            24a4621560e4        7 days ago          123.6 MB
    debian                testing             7f5d8ca9fdcf        7 days ago          121.8 MB
    debian                jessie              b164861940b8        7 days ago          121.8 MB
    debian                stable              caa04aa09d69        7 days ago          115 MB
    debian                oldstable           b96f0d33b520        7 days ago          112.4 MB
    debian                sid                 f3d4759f77a7        7 days ago          123.6 MB
    debian                7.4                 e565fbbc6033        6 weeks ago         115 MB
    debian                6.0.8               d56191e18d6b        4 months ago        114.9 MB
    debian                7.3                 b5fe16f2ccba        4 months ago        117.8 MB

## Start a container

Run it in the background so we can ssh in:

    docker run -d -P --name volgenmodel1 ouruser/volgenmodel:v1

See it running:

    # docker ps
    CONTAINER ID        IMAGE                    COMMAND             CREATED             STATUS              PORTS                   NAMES
    3e99e883f050        ouruser/volgenmodel:v1   /usr/sbin/sshd -D   11 seconds ago      Up 10 seconds       0.0.0.0:49153->22/tcp   volgenmodel1

Ssh in using the port mentioned:

    ssh -p 49153 root@localhost   # password is set in the Dockerfile

## Manually compile tools

FIXME This would be done automatically...

### MINC tools

    cd /tmp
    wget https://raw.githubusercontent.com/carlohamalainen/volgenmodel-nipype/master/vagrant-puppet/build_minc_tools.sh
    bash build_minc_tools.sh

### pyminc

    cd /opt/code/pyminc
    python setup.py install

### nipype

    cd /opt/code/nipype
    python setup.py install

### environment variables

Append to ```/etc/bash.bashrc```:

    export PATH=$PATH:/opt/code/minc-widgets/gennlxfm:/opt/code/minc-widgets/mincbigaverage:/opt/code/minc-widgets/mincnorm:/opt/code/minc-widgets/nlpfit:/opt/code/minc-widgets/volalign:/opt/code/minc-widgets/volcentre:/opt/code/minc-widgets/volextents:/opt/code/minc-widgets/volflip:/opt/code/minc-widgets/voliso:/opt/code/minc-widgets/volpad:/opt/code/minc-widgets/volsymm:/opt/code/minc-widgets/xfmavg:/opt/code/minc-widgets/xfmflip
    export PYTHONPATH=/opt/code/volgenmodel-nipype
    export PATH=$PATH:/opt/code/volgenmodel-nipype/extra-scripts
    export PERL5LIB=/usr/local/perl


## Tidying up

To delete all containers:

    docker ps -a | awk '{print $1}' | grep -v CONTAINER | xargs -n 1 docker rm

To delete all images:

    docker rmi `docker images -q`


## Temp stuff

Run ```bash``` in the container:

    docker run -t -i ouruser/volgenmodel:v1 /bin/bash
    root@4880af4cb8f1:/# ls /opt/code
    minc-toolkit  minc-widgets  nipype  pyminc  volgenmodel-nipype


