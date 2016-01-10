# volgenmodel-nipype

Port of [volgenmodel](https://github.com/andrewjanke/volgenmodel) to Nipype. Interfaces to MINC tools that were previously in this repo are now in the master branch of [Nipype](https://github.com/nipy/nipype).

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

The final output is in ```$FAST_EXAMPLE_BASE_DIR/volgenmodel_final_output```.

# Vagrant/Puppet

(Old, probably doesn't work now.)

Vagrant/Puppet scripts are here: [vagrant-puppet](vagrant-puppet).

# Docker

See [volgenmodel-nipype/docker](docker) for a script to run a sample mouse
brain workflow. This uses a sample mouse brain model which is
available in a separate repository (around 96Mb in size): https://github.com/carlohamalainen/volgenmodel-fast-example.git
