FROM ubuntu
MAINTAINER Carlo Hamalainen <carlo@carlo-hamalainen.net>

RUN         apt-get -qq update
RUN         apt-get -qqy install python git ipython screen htop vim octave cmake cmake-curses-gui build-essential g++ cmake cmake-curses-gui bison flex freeglut3 freeglut3-dev libxi6 libxi-dev libxmu6 libxmu-dev libxmu-headers python-pip python-dev python-scipy python-numpy python-lxml imagemagick zlib1g-dev

#set locale
RUN locale-gen en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV PERL_UNICODE "AS"

RUN         mkdir -p /opt
WORKDIR     /opt

RUN git clone --recursive git://github.com/BIC-MNI/minc-toolkit.git minc-toolkit
WORKDIR /opt/minc-toolkit
RUN rm -fr build
WORKDIR /opt/minc-toolkit/build
RUN cmake -DMT_BUILD_SHARED_LIBS=ON -DMT_BUILD_VISUAL_TOOLS=ON ..
RUN make
RUN make install

WORKDIR     /opt

RUN git clone https://github.com/nipy/nipype
WORKDIR /opt/nipype

RUN pip install -U pip
RUN pip install networkx
RUN pip install nibabel
RUN pip install traits
RUN pip install nose
RUN pip install future
RUN pip install simplejson
RUN pip install prov
RUN python setup.py install


WORKDIR     /opt
RUN git clone https://github.com/isAarya/volgenmodel-nipype
WORKDIR /opt/volgenmodel-nipype

ENV PYTHONPATH /opt/volgenmodel-nipype
ENV PATH /opt/volgenmodel-nipype/extra-scripts:$PATH

ENV PERL5LIB /usr/local/perl

RUN mkdir /scratch

ADD volgenmodel-fast-example /scratch/volgenmodel-fast-example

ADD go.py /opt/
ADD go.sh /opt/

WORKDIR /opt

CMD /bin/bash
