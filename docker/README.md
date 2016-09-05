# Docker test container

Install the Docker Engine: https://docs.docker.com/engine/installation/

## Run the test workflow

Clone repositories including the sample mouse brain data:

    git clone https://github.com/carlohamalainen/volgenmodel-nipype.git
    cd volgenmodel-nipype/docker
    git clone https://github.com/carlohamalainen/volgenmodel-fast-example.git # about 96Mb

Build and run:

    ./build.sh && docker run -i -t carlo/volgenmodel-nipype /bin/bash /opt/go.sh

End of output should look like:

    160110-04:08:59,19 workflow INFO:
             [Job finished] jobname: volsymm_final_model_02_ jobid: 75
    160110-04:08:59,22 workflow INFO:
             Pending[0] Submitting[1] jobs Slots[inf]
    160110-04:08:59,23 workflow INFO:
             Executing: datasink ID: 76
    160110-04:08:59,30 workflow INFO:
             Finished executing: datasink ID: 76
    160110-04:08:59,32 workflow INFO:
             Executing node datasink in dir: /scratch/volgenmodel-fast-example/workflow/datasink
    160110-04:09:59,38 workflow INFO:
             [Job finished] jobname: datasink jobid: 76
    1c1
    < hdf5 model-2016-01-09 {
    ---
    > hdf5 mouse00_volcentre_norm_resample_bigaverage_reshape_vol_symm {
    66c66
    <               :ident = "nobody:7e514b8f78db:2016.01.09.08.05.21:4581:1" ;
    ---
    >               :ident = "nobody:f957a4516fbc:2016.01.10.04.06.29:4220:1" ;
    68c68
    <               :history = "Sat Jan  9 08:05:21 2016>>> mincaverage -clobber /tmp/volsymm-ZhWtPJhp/FWD-rsmpl.mnc /tmp/volsymm-ZhWtPJhp/FWD-rsmpl.flip.mnc mouse00_volcentre_norm_resample_bigaverage_reshape_vol_symm.mnc\n",
    ---
    >               :history = "Sun Jan 10 04:06:29 2016>>> mincaverage -clobber /tmp/volsymm-RZdXLBn2/FWD-rsmpl.mnc /tmp/volsymm-RZdXLBn2/FWD-rsmpl.flip.mnc mouse00_volcentre_norm_resample_bigaverage_reshape_vol_symm.mnc\n",
    Binary image comparison:
    Images are identical.

