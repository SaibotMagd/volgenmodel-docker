# Vagrant and Puppet

## Build the VM

    git clone https://github.com/carlohamalainen/volgenmodel-nipype
    cd volgenmodel-nipype/vagrant
    vagrant box add debian80 http://carlo-hamalainen.net/vagrant/debian-jessie-minimal-2014-06-04.box
    vagrant up # This takes about 20 minutes to run.

## SSH to the machine

Use vagrant to ssh and then run the tests:

    vagrant ssh
    cd /opt/code/volgenmodel-nipype
    python -m doctest -v nipypeminc.py

# Run the test data set

Copy the files to a scratch directory on the VM. Hint: in the VM,
```/vagrant``` is an automatic mount of the directory where the the
vagrant was provisioned, in this case ```volgenmodel-nipype/vagrant```
on the host.

Files that you'll need:

    vagrant@vagrant:/scratch/fast-example$ ls -lh
    total 5.7M
    -rw-r--r-- 1 vagrant vagrant  440 Jun  5 08:12 fit.10-genmodel.conf
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml01_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml02_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml03_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml04_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml05_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml06_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml07_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml08_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml09_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml10_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml11_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml12_lowres.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml13_lowres.mnc

Note that ```/opt/code/volgenmodel-nipype/volgenmodel.py``` has the directory ```/scratch/fast-example``` hardcoded.

Pop into the right directory and load ipython:

    cd /scratch/fast-example
    ipython

In ipython, load the volgenmodel code (which creates the workflow) and then run the workflow:

    %run /opt/code/volgenmodel-nipype/volgenmodel.py
    workflow.run()

# Notes

This Vagrant/Puppet recipe is experimental, and not intended for
production systems that will run nipype or volgenmodel-nipype. In
particular the [Vagrantfile](Vagrantfile) calls the script
[build_minc_tools.sh](build_minc_tools.sh) which builds the latest
minc-toolkit from source, which takes some time.
