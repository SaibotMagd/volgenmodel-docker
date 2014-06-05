# Vagrant and Puppet

To build a VM using Vagrant and Puppet:

    git clone https://github.com/carlohamalainen/volgenmodel-nipype
    cd volgenmodel-nipype/vagrant-puppet
    vagrant box add debian80 http://carlo-hamalainen.net/vagrant/debian-jessie-minimal-2014-06-04.box
    vagrant up # This takes about 20 minutes to run.
    vagrant ssh

Now you'll be in the VM with minc-toolkit, nipype, volgenmodel-nipype all built. Try the tests:

    cd /opt/code/volgenmodel-nipype
    python -m doctest -v nipypeminc.py

# Notes

This Vagrant/Puppet recipe is experimental, and not intended for
production systems that will run nipype or volgenmodel-nipype. In
particular the [Vagrantfile](Vagrantfile) calls the script
[build_minc_tools.sh](build_minc_tools.sh) which builds the latest
minc-toolkit from source, which takes some time.
