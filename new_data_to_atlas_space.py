#!/usr/bin/env python3
from os.path import join as opj
import os
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.interfaces.io import SelectFiles, DataSink, DataGrabber
from nipype.pipeline.engine import Workflow, Node, MapNode
from nipype.interfaces.minc import  \
        Resample,       \
        BigAverage,     \
        VolSymm

# <editor-fold desc="Parameters">

base_dir = '/gpfs1/scratch/30days/uqsbollm/7T_group_Hippocampus_28QSM'
source_volgenmodel_dir = base_dir + '/derived/avg_magnitude/workflow/'
stage_id = '06'

# source_files_to_warp_dir = base_dir + '/derived/avg_magnitude/'
# file_pattern_input = '*/m_composer_echo_1_merged_maths_mnc_n4.mnc'
# source_file_name = 'magnitude'

# source_files_to_warp_dir = base_dir + '/derived/qsm_final_STI/'
# file_pattern_input = '*/p_composer_echo_1_roi_STI_maths_maths_mnc.mnc'
# source_file_name = 'STI'

source_files_to_warp_dir = base_dir + '/derived/qsm_final_DeepQSM_2018-10-18-2208arci-UnetMadsResidual-batch40-fs4-cost_L2-drop_0.05_ep50-shapes_shape64_ex100_2018_10_18/'
file_pattern_input = '*/deepQSM_maths_maths_mnc.mnc'
source_file_name = 'DeepQSM'

output_dir = base_dir + '/derived/new_data_to_atlas_space/'


# shouldn't change
stage_dir = source_volgenmodel_dir + 'xfmconcat_' + stage_id + '_/mapflow/'
targetDir = source_volgenmodel_dir + 'voliso_' + stage_id + '_/'
working_dir = '/gpfs1/scratch/30days/uqsbollm/temp'
file_pattern_transform = '*/*_volcentre_norm__nlpfit_xfm_output.mnc_xfminvert_output.mnc_xfmconcat.xfm'

# </editor-fold>

# <editor-fold desc="Select files">
wf = Workflow(name='new_data_to_atlas_space')
wf.base_dir = opj(working_dir)

datasource_input = Node(interface=DataGrabber(sort_filelist=True), name='datasource_input')
datasource_input.inputs.base_directory = os.path.abspath(source_files_to_warp_dir)
datasource_input.inputs.template = file_pattern_input

datasource_transform = Node(interface=DataGrabber(sort_filelist=True), name='datasource_transform')
datasource_transform.inputs.base_directory = os.path.abspath(stage_dir)
datasource_transform.inputs.template = file_pattern_transform

datasource_target = Node(interface=DataGrabber(sort_filelist=True), name='datasource_target')
datasource_target.inputs.base_directory = os.path.abspath(targetDir)
datasource_target.inputs.template = '*volcentre_norm_resample_bigaverage_reshape_vol_symm_norm_voliso.mnc'
# </editor-fold>

# <editor-fold desc="Resample">
resample = MapNode(interface=Resample(sinc_interpolation=True),
                   name='resample_',
                   iterfield=['input_file', 'transformation'])

wf.connect(datasource_input, 'outfiles', resample, 'input_file')
wf.connect(datasource_transform, 'outfiles', resample, 'transformation')
wf.connect(datasource_target, 'outfiles', resample, 'like')
# </editor-fold>

# <editor-fold desc="Bigaverage">
bigaverage = Node(interface=BigAverage(output_float=True, robust=False),
                  name='bigaverage',
                  iterfield=['input_file'])

wf.connect(resample, 'output_file', bigaverage, 'input_files')
# </editor-fold>

# <editor-fold desc="Datasink">
datasink = Node(DataSink(base_directory=output_dir, container=output_dir),
                name='datasink')

wf.connect([(bigaverage, datasink, [('output_file', source_file_name + '_average_' + stage_id)])])
wf.connect([(resample, datasink, [('output_file', source_file_name + '_atlas_space_' + stage_id)])])
wf.connect([(datasource_transform, datasink, [('outfiles', '_transforms_' + stage_id)])])

# </editor-fold>

# <editor-fold desc="Run">
wf.run('MultiProc', plugin_args={'n_procs': 9})

# </editor-fold>
