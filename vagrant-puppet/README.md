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

Main output files:

    $ find /scratch/fast-example/volgenmodel_final_output/
    /scratch/fast-example/volgenmodel_final_output/
    /scratch/fast-example/volgenmodel_final_output/model
    /scratch/fast-example/volgenmodel_final_output/model/sml_mincbigaverage_output_reshape_output_volsymm_output.mnc
    /scratch/fast-example/volgenmodel_final_output/stdev
    /scratch/fast-example/volgenmodel_final_output/stdev/sml_mincbigaverage_sd_file_output_volsymm_output.mnc

Workflow directory:

    $ ls -l /scratch/fast-example/workflow/
    total 512
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 bigaverage_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:34 bigaverage_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:40 bigaverage_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 blur_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 blur_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:37 blur_02_
    -rw-r--r-- 1 vagrant vagrant 145927 Jun  5 10:37 d3.v3.min.js
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:41 datasink
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:37 datasource_sml
    -rw-r--r-- 1 vagrant vagrant  29970 Jun  5 10:37 graph1.json
    -rw-r--r-- 1 vagrant vagrant  13388 Jun  5 10:37 graph.json
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 identity_transformation
    -rw-r--r-- 1 vagrant vagrant   6691 Jun  5 10:37 index.html
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 initial_model
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 initial_model_fwhm3d
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:27 merge_lastlin_initxfm_01_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:27 merge_lastlin_initxfm_02_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:32 merge_xfm_00_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:33 merge_xfm_01_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:39 merge_xfm_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 merge_xfmavg_and_step100_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:33 merge_xfmavg_and_step101_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:39 merge_xfmavg_and_step102_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:27 merge_xfm_mapnode_result_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:33 merge_xfm_mapnode_result_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:39 merge_xfm_mapnode_result_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 mincmath_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 mincmath_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:37 mincmath_02_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:33 nlpfit_01_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:39 nlpfit_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 norm_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 norm_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:37 norm_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:34 pik_check_iavg_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:34 pik_check_iavg_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:40 pik_check_iavg_02_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:32 pik_check_resample_00_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:34 pik_check_resample_01_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:41 pik_check_resample_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 pik_check_voliso00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 pik_check_voliso01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:41 pik_check_voliso02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 pik_on_stage_model_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:37 pik_on_stage_model_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:41 pik_on_stage_model_02_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:25 preprocess_normalise
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:25 preprocess_pik
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:25 preprocess_threshold_blur
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:25 preprocess_volcentre
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:25 preprocess_voliso
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:25 preprocess_volpad
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:27 register_00_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:32 resample_00_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:34 resample_01_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:40 resample_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 resample_to_short_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:34 resample_to_short_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:40 resample_to_short_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 select_first_datasource
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 select_first_volpad
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 voliso_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 voliso_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:37 voliso_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:41 volsymm_final_model_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 volsymm_on_short_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:37 volsymm_on_short_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:41 volsymm_on_short_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 write_conf_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:25 write_conf_02_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:32 xfmavg_00_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:33 xfmavg_01_
    drwxr-xr-x 3 vagrant vagrant   4096 Jun  5 10:39 xfmavg_02_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:32 xfmconcat_00_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:33 xfmconcat_01_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:39 xfmconcat_02_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:27 xfmconcat_for_nlpfit_01_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:27 xfmconcat_for_nlpfit_02_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:27 xfminvert_00_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:33 xfminvert_01_
    drwxr-xr-x 4 vagrant vagrant   4096 Jun  5 10:39 xfminvert_02_

# Notes

This Vagrant/Puppet recipe is experimental, and not intended for
production systems that will run nipype or volgenmodel-nipype. In
particular the [Vagrantfile](Vagrantfile) calls the script
[build_minc_tools.sh](build_minc_tools.sh) which builds the latest
minc-toolkit from source, which takes some time.
