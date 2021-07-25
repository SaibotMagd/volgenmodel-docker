#!/usr/bin/env bash
# TODO: write interfaces for niype and do in nipype
#cd ../7T_group_Hippocampus_28QSM/derived/avg_magnitude/

#for file in $(find -name m_composer_echo_1_merged_maths.nii); do
#   nii2mnc -unsigned -float -clobber $file ${file%.nii}_mnc.mnc;
#done
#
#for file in $(find -name m_composer_echo_1_merged_maths_mnc.mnc); do
#    echo $file
#    N4BiasFieldCorrection -i $file -o ${file%.mnc}_n4.mnc -d 3 -v;
#done
#cd -

#cd ../7T_group_Hippocampus_28QSM/derived/qsm_final_STI/
#
#for file in $(find -name p_composer_echo_1_roi_STI_maths_maths.nii); do
#   nii2mnc -float -clobber $file ${file%.nii}_mnc.mnc;
#done
#
#cd -

cd ../7T_group_Hippocampus_28QSM/derived/qsm_final_DeepQSM_2018-10-18-2208arci-UnetMadsResidual-batch40-fs4-cost_L2-drop_0.05_ep50-shapes_shape64_ex100_2018_10_18/

for file in $(find -name deepQSM_maths_maths.nii); do
   nii2mnc -float -clobber $file ${file%.nii}_mnc.mnc;
done

cd -