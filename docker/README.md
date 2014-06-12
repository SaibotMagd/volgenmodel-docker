# Experimental Docker notes

Like the Vagrant notes, these are just for testing at the moment.

## Install Docker on Debian/Ubuntu

Quick install on Debian/Ubuntu, thanks to
https://coderwall.com/p/wlhavw

    echo deb http://get.docker.io/ubuntu docker main | sudo tee /etc/apt/sources.list.d/docker.list
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
    sudo apt-get update
    sudo apt-get install -y lxc-docker

## Load the prebuilt volgenmodel-nipype image

Load the image:

    # wget http://carlo-hamalainen.net/docker/volgenmodel-nipype-docker-2014-06-12.tar
    # docker load < volgenmodel-nipype-docker-2014-06-12.tar

or maybe:

    # wget -O- http://carlo-hamalainen.net/docker/volgenmodel-nipype-docker-2014-06-12.tar | docker load

Check that it's there:

    # docker images
    REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
    <none>              <none>              ea3a04316ee0        11 minutes ago      2.192 GB

Give it a nicer name:

    # docker tag ea3a04316ee0 volgenmodel-nipype
    # docker images
    REPOSITORY           TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
    volgenmodel-nipype   latest              ea3a04316ee0        12 minutes ago      2.192 GB

Run ```bash``` in the container and look around:

    docker run -t -i volgenmodel-nipype /bin/bash

e.g.

    root@14c248c7b481:/# ipython
    Python 2.7.3 (default, Mar 13 2014, 11:03:55)
    Type "copyright", "credits" or "license" for more information.

    IPython 0.13.1 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    In [1]: %run /opt/code/volgenmodel-nipype/nipypeminc.py

## Build the volgenmodel image

Build the image, tagging it with a description:

    mkdir tmp
    cd tmp
    wget https://raw.githubusercontent.com/carlohamalainen/volgenmodel-nipype/master/docker/Dockerfile
    docker build -t="ouruser/volgenmodel:v1" . # note the trailing dot

Look at the images. We get all the cumulative history of this image:

    $ docker images
    REPOSITORY            TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
    ouruser/volgenmodel   v1                  034b4d218e4b        20 seconds ago      1.25 GB
    debian                rc-buggy            350a74df81b1        6 days ago          159.9 MB
    debian                experimental        36d6c9c7df4c        6 days ago          159.9 MB
    debian                6.0.9               3b36e4176538        7 days ago          112.4 MB
    debian                squeeze             3b36e4176538        7 days ago          112.4 MB
    debian                7.5                 667250f9a437        7 days ago          115 MB
    debian                wheezy              667250f9a437        7 days ago          115 MB
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

Log out (hit ```Ctrl-d```).

## Commit the changes:

Look at the diff:

    # docker diff 56d0b4cb96de | head
    C /var/log/lastlog
    C /var/log/wtmp
    C /root
    A /root/.bash_history
    C /tmp
    A /tmp/build_minc_tools.sh
    C /etc/bash.bashrc
    C /opt/code/minc-toolkit
    A /opt/code/minc-toolkit/build
    A /opt/code/minc-toolkit/build/CPackSourceConfig.cmake

Do the commit:

    root@x1:~# docker commit 56d0b4cb96de ouruser/volgenmodel 'Installed all tools.'
    ea3a04316ee0839708c73b50a93b295706702723652efb28b4cd3390c324387a

Check that the new image is there:

    root@x1:~# docker images
    REPOSITORY            TAG                    IMAGE ID            CREATED             VIRTUAL SIZE
    ouruser/volgenmodel   Installed all tools.   ea3a04316ee0        47 seconds ago      2.192 GB
    ouruser/volgenmodel   v1                     034b4d218e4b        22 minutes ago      1.25 GB
    debian                rc-buggy               350a74df81b1        6 days ago          159.9 MB
    debian                experimental           36d6c9c7df4c        6 days ago          159.9 MB
    debian                6.0.9                  3b36e4176538        7 days ago          112.4 MB
    debian                squeeze                3b36e4176538        7 days ago          112.4 MB
    debian                7.5                    667250f9a437        7 days ago          115 MB
    debian                wheezy                 667250f9a437        7 days ago          115 MB
    debian                latest                 667250f9a437        7 days ago          115 MB
    debian                unstable               24a4621560e4        7 days ago          123.6 MB
    debian                testing                7f5d8ca9fdcf        7 days ago          121.8 MB
    debian                jessie                 b164861940b8        7 days ago          121.8 MB
    debian                stable                 caa04aa09d69        7 days ago          115 MB
    debian                oldstable              b96f0d33b520        7 days ago          112.4 MB
    debian                sid                    f3d4759f77a7        7 days ago          123.6 MB
    debian                7.4                    e565fbbc6033        6 weeks ago         115 MB
    debian                6.0.8                  d56191e18d6b        4 months ago        114.9 MB
    debian                7.3                    b5fe16f2ccba        4 months ago        117.8 MB

Finally, stop the container:

    docker stop volgenmodel1

## Save to a file:

    docker save ea3a04316ee0 > volgenmodel-nipype-docker-2014-06-12.tar

## Tidying up

To delete all containers:

    docker ps -a | awk '{print $1}' | grep -v CONTAINER | xargs -n 1 docker rm

To delete all images:

    docker rmi `docker images -q`
