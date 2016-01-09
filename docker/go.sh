#!/bin/bash

. /usr/local/minc-toolkit-config.sh

cd /opt

python go.py

mincdiff /scratch/volgenmodel-fast-example/model-2016-01-09.mnc \
         /scratch/volgenmodel-fast-example/volgenmodel_final_output/model/mouse00_volcentre_norm_resample_bigaverage_reshape_vol_symm.mnc
