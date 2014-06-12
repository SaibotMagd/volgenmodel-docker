FROM debian
MAINTAINER Carlo Hamalainen <carlo@carlo-hamalainen.net>

RUN apt-get -qq update
RUN apt-get -qqy install python-pip python-numpy python-dev python-networkx python-nose libgetopt-tabular-perl imagemagick octave ipython htop screen git cmake cmake-curses-gui build-essential g++ bison flex freeglut3 freeglut3-dev libxi6 libxi-dev libxmu6 libxmu-dev libxmu-headers wget

RUN /usr/bin/pip install nibabel
RUN /usr/bin/pip install traits traitsui

RUN mkdir -p /opt/code

RUN git clone --recursive https://github.com/BIC-MNI/minc-toolkit.git   /opt/code/minc-toolkit
RUN git clone https://github.com/mcvaneede/pyminc.git                   /opt/code/pyminc
RUN git clone https://github.com/nipy/nipype.git                        /opt/code/nipype
RUN git clone https://github.com/BIC-MNI/minc-widgets.git               /opt/code/minc-widgets
RUN git clone https://github.com/carlohamalainen/volgenmodel-nipype.git /opt/code/volgenmodel-nipype

# http://docs.docker.com/examples/running_ssh_service/
RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:screencast' |chpasswd
EXPOSE 22
CMD    ["/usr/sbin/sshd", "-D"]
