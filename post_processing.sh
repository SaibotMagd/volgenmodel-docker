#!/usr/bin/env bash
# TODO: write interfaces for niype and do in nipype

cd ../7T_group_Hippocampus_28QSM/derived/new_data_to_atlas_space/

#for file in $(find -name *_resample.mnc); do
#   mnc2nii $file ${file%.mnc}_nii.nii;
#done

for file in $(find -name *_bigaverage.mnc); do
   mnc2nii $file ${file%.mnc}_nii.nii;
done


cd -