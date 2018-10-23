#!/usr/bin/env python3
from os.path import join as opj
import os
from nipype.interfaces.fsl import ExtractROI, BET, MultiImageMaths, ImageMaths
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.pipeline.engine import Workflow, Node, MapNode

# <editor-fold desc="Parameters">
os.environ["FSLOUTPUTTYPE"] = "NIFTI"

# work on scratch space only
experiment_dir = '/mnt/r/DEEPQSM-Q0537/deepqsm/data/processed/7T_group_Hippocampus_28QSM/derived/'
# dir with raw data, converted data and pipelines
output_dir = '/mnt/r/DEEPQSM-Q0537/deepqsm/data/processed/7T_group_Hippocampus_28QSM/derived'
# make this dir in the exp_dir
working_dir = '/mnt/i/uqsbollm/atemp'
# make this dir in the exp_dir for working copies of data.

# subject_list = ['20150619_0914_S30_SC']
subject_list = ['20150430_1217_S08_SB', '20150514_1233_S10_DS', '20150515_1206_S04_NO', '20150519_1156_S02_RP',
                '20150521_1019_S06_JV', '20150605_1000_S19_AM', '20150605_1305_S27_JR', '20150612_1000_S26_NF',
                '20150612_1316_S28_JL', '20150514_1055_S09_JH', '20150515_1034_S11_BS', '20150518_1409_S13_NF',
                '20150520_1400_S07_EM', '20150601_1134_S18_NM', '20150605_1057_S24_CA', '20150605_1400_S22_ZS',
                '20150612_1055_S15_LS', '20150612_1403_S21_NZ', '20150514_1143_S12_JU', '20150515_1121_S05_JL',
                '20150519_1110_S01_SF', '20150520_1451_S17_JC', '20150603_1657_S23_PM', '20150605_1147_S20_BL',
                '20150605_1453_S14_NF', '20150612_1147_S25_MP', '20150619_0914_S30_SC']

print(subject_list)

# </editor-fold>

# <editor-fold desc="Create Workflow and link to subject list">
wf = Workflow(name='qsm')
wf.base_dir = opj(experiment_dir, working_dir)

# create infosource to iterate over subject list
infosource = Node(IdentityInterface(fields=['subject_id']), name="infosource")
infosource.iterables = [('subject_id', subject_list)]
# </editor-fold>

# <editor-fold desc="Select files">
templates = {'QSM': 'cut_phase/{subject_id}/_cutPhs_node*/deepQSM.nii',
             'mask_file': 'cut_phase/{subject_id}/_cutPhs_node*/eroded_mask.nii'}
selectfiles = Node(SelectFiles(templates, base_directory=experiment_dir), name='selectfiles')

wf.connect([(infosource, selectfiles, [('subject_id', 'subject_id')])])
# </editor-fold>

# <editor-fold desc="Define the function that calls MultiImageMaths">
def generate_multiimagemaths_lists(in_files):
    in_file = in_files[0]
    operand_files = in_files[1:]
    op_string = '-add %s '
    op_string = len(operand_files) * op_string
    return in_file, operand_files, op_string
# </editor-fold>

# <editor-fold desc="Mask processing">
generate_add_masks_lists_n = Node(Function(
    input_names=['in_files'],
    output_names=['list_in_file', 'list_operand_files', 'list_op_string'],
    function=generate_multiimagemaths_lists),
    name='generate_add_masks_lists_node')

add_masks_n = Node(MultiImageMaths(),
                   name="add_masks_node")

wf.connect([(selectfiles, generate_add_masks_lists_n, [('mask_file', 'in_files')])])
wf.connect([(generate_add_masks_lists_n, add_masks_n, [('list_in_file', 'in_file')])])
wf.connect([(generate_add_masks_lists_n, add_masks_n, [('list_operand_files', 'operand_files')])])
wf.connect([(generate_add_masks_lists_n, add_masks_n, [('list_op_string', 'op_string')])])

# </editor-fold>

# <editor-fold desc="QSM Post processing">
generate_add_qsms_lists_n = Node(Function(
    input_names=['in_files'],
    output_names=['list_in_file', 'list_operand_files', 'list_op_string'],
    function=generate_multiimagemaths_lists),
    name='generate_add_qsms_lists_node')

add_qsms_n = Node(MultiImageMaths(),
                  name="add_qsms_node")

wf.connect([(selectfiles, generate_add_qsms_lists_n, [('QSM', 'in_files')])])
wf.connect([(generate_add_qsms_lists_n, add_qsms_n, [('list_in_file', 'in_file')])])
wf.connect([(generate_add_qsms_lists_n, add_qsms_n, [('list_operand_files', 'operand_files')])])
wf.connect([(generate_add_qsms_lists_n, add_qsms_n, [('list_op_string', 'op_string')])])

# divide QSM by mask
final_qsm_n = Node(ImageMaths(op_string='-div'),
                   name="divide_added_qsm_by_added_masks")

wf.connect([(add_qsms_n, final_qsm_n, [('out_file', 'in_file')])])
wf.connect([(add_masks_n, final_qsm_n, [('out_file', 'in_file2')])])

# </editor-fold>

# <editor-fold desc="Datasink">
datasink = Node(DataSink(base_directory=experiment_dir, container=output_dir),
                name='datasink')

wf.connect([(add_masks_n, datasink, [('out_file', 'mask_sum_DeepQSM')])])
wf.connect([(add_qsms_n, datasink, [('out_file', 'qsm_sum_DeepQSM')])])
wf.connect([(final_qsm_n, datasink, [('out_file', 'qsm_final_DeepQSM')])])

# </editor-fold>

# <editor-fold desc="Run">
wf.run('MultiProc', plugin_args={'n_procs': 8})

# </editor-fold>
