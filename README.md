# volgenmodel-nipype

Port of volgenmodel to Nipype along with interfaces for a number of Minc tools.

# Install

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

To run the doctests:

    python -m doctest -v nipypeminc.py

Should say something like:

    13 items passed all tests:
       4 tests in nipypeminc.Average
       3 tests in nipypeminc.Blob
       5 tests in nipypeminc.Blur
       5 tests in nipypeminc.Calc
       3 tests in nipypeminc.Convert
       4 tests in nipypeminc.Dump
       4 tests in nipypeminc.Extract
       4 tests in nipypeminc.Math
       3 tests in nipypeminc.Norm
       3 tests in nipypeminc.Resample
       4 tests in nipypeminc.ToEcat
       4 tests in nipypeminc.ToRaw
       5 tests in nipypeminc.aggregate_filename
    51 tests in 170 items.
    51 passed and 0 failed.
    Test passed.

# Vagrant/Puppet

Vagrant/Puppet scripts are here: [vagrant-puppet](vagrant-puppet).
