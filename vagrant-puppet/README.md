# Vagrant and Puppet

## Build the VM

    git clone https://github.com/carlohamalainen/volgenmodel-nipype
    cd volgenmodel-nipype/vagrant-puppet
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
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml01.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml02.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml03.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml04.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml05.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml06.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml07.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml08.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml09.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml10.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml11.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml12.mnc
    -rw-r--r-- 1 vagrant vagrant 439K Jun  5 08:12 sml13.mnc

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
