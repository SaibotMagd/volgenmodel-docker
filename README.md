# volgenmodel-nipype

Port of volgenmodel to Nipype along with interfaces for a number of Minc tools.

# Status

Things still left to do:

* Many FIXMEs in ```volgenmodel.py```.
* Symmetric averaging (end of stage).

# Install

Prerequisites:

* https://github.com/nipy/nipype
* https://github.com/BIC-MNI/minc-widgets
* bestlinreg
* minccomplete

Then:

    git clone https://github.com/carlohamalainen/volgenmodel-nipype
    cd volgenmodel-nipype

Load the ```volgenmodel.py``` script using IPython or similar, being sure to
tweak ```FAST_EXAMPLE_BASE_DIR``` to something appropriate. Then

    workflow.run()

runs the workflow on a single core, or

    workflow.run(plugin='MultiProc', plugin_args={'n_procs' : 4})

runs it on 4 cores.
