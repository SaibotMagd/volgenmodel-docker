#!/usr/bin/env python

from pyminc.volumes.factory import volumeFromFile

if __name__ == "__main__":
    infile_mine = volumeFromFile('/home/carlo/work/github/volgenmodel-nipype/model.mnc')
    infile_perl = volumeFromFile('/scratch/run_lowres/model.mnc')

    d = infile_mine.data - infile_perl.data

    print 'min', d.min().tolist()
    print 'max', d.max().tolist()
    print 'mean', d.mean().tolist()
