# volgenmodel-nipype
volgenmodel-nipype is the port of [volgenmodel](https://github.com/andrewjanke/volgenmodel) to [Nipype](https://github.com/nipy/nipype). It creates nonlinear models from a series of input MINC files.

# Run
Install minc: https://bic-mni.github.io
```bash
    wget http://packages.bic.mni.mcgill.ca/minc-toolkit/Debian/minc-toolkit-1.9.16-20180117-Ubuntu_16.04-x86_64.deb
    sudo apt-get install libc6 libstdc++6 imagemagick perl
    sudo dpkg -i minc-toolkit-1.9.16-20180117-Ubuntu_16.04-x86_64.deb
    sudo apt-get install libgl1-mesa-glx libglu1-mesa
```

Clone code and test-data:    
```bash
git clone https://github.com/CAIsr/volgenmodel-nipype.git
git clone https://github.com/CAIsr/volgenmodel-fast-example.git
```

install miniconda:
```bash
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

start new terminal and install packages required:
```bash
pip install nipype
```

run volgenmodel with the test data:
```bash
python3 volgenmodel.py
```

# Citation
This method is an implementation of the technique described in this paper:

   http://www.ncbi.nlm.nih.gov/pubmed/25620005

If you use it in a publication please cite:

   Janke AL, Ullmann JF, Robust methods to create ex vivo minimum
deformation atlases for brain mapping.
   Methods. 2015 Feb;73:18-26. doi: [10.1016/j.ymeth.2015.01.005](http://dx.doi.org/10.1016/j.ymeth.2015.01.005)


# Install on Linux

## Prerequisites

### minc-toolkit / minc-widgets

On Debian/Ubuntu systems:

    sudo apt-get install octave cmake cmake-curses-gui \
                         build-essential g++ \
                         cmake cmake-curses-gui \
                         bison flex \
                         freeglut3 freeglut3-dev \
                         libxi6 libxi-dev libxmu6 libxmu-dev libxmu-headers

Build minc-toolkit from Github:

    git clone --recursive git://github.com/BIC-MNI/minc-toolkit.git minc-toolkit
    cd minc-toolkit
    rm -fr build
    mkdir build
    cd build
    cmake -DMT_BUILD_SHARED_LIBS=ON -DMT_BUILD_VISUAL_TOOLS=ON ..
    make &> make.log   # check the log!
    sudo make install  # installs to /usr/local

You should also end up with the tools from https://github.com/BIC-MNI/minc-widgets

### nipype

Install the latest from Github:

    sudo apt-get install python-nibabel python-traits python-future python-simplejson
    sudo pip install prov

    git clone https://github.com/nipy/nipype
    cd nipype
    sudo python setup.py install

### bestlinreg and minccomplete

The scripts bestlinreg and minccomplete are included in this repository in [extra-scripts](extra-scripts).

# Running

Then:

    git clone https://github.com/carlohamalainen/volgenmodel-nipype
    cd volgenmodel-nipype
    export PYTHONPATH=`pwd`
    export PATH=$PATH:`pwd`/extra-scripts
    export PERL5LIB=/usr/local/perl  # assuming minc-toolkit is installed in /usr/local

Load the ```volgenmodel.py``` script using IPython or similar, being sure to
tweak ```FAST_EXAMPLE_BASE_DIR``` to something appropriate. Then

    workflow.run()

runs the workflow on a single core, or

    workflow.run(plugin='MultiProc', plugin_args={'n_procs' : 4})

runs it on 4 cores.

The workflow for a small 3-stage model is:

![workflow fast-example](https://github.com/carlohamalainen/volgenmodel-nipype/raw/master/volgenmodel_graph.png)

The final output is in ```$FAST_EXAMPLE_BASE_DIR/volgenmodel_final_output```.

# Run in docker (currently not working)
Install the Docker Engine: 
* for [windows:](https://docs.docker.com/engine/installation/windows/#/docker-for-windows)
* for [mac:](https://docs.docker.com/engine/installation/mac/#/docker-for-mac)
* for [linux:](https://docs.docker.com/engine/installation/linux/ubuntulinux/)

Clone repositories including the sample mouse brain data:

    git clone https://github.com/carlohamalainen/volgenmodel-nipype.git
    cd volgenmodel-nipype/docker
    git clone https://github.com/carlohamalainen/volgenmodel-fast-example.git # about 96Mb

open a shell in the docker folder and run:

    docker build --no-cache -t='carlo/volgenmodel-nipype' .
    docker run -i -t carlo/volgenmodel-nipype /bin/bash /opt/go.sh

it should run now :)

The final model should look like this:

![mouse model triplanar](https://raw.githubusercontent.com/carlohamalainen/volgenmodel-fast-example/master/model-2016-01-09.png)


