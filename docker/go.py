from volgenmodel import *

workflow = make_workflow()
workflow.run(plugin='MultiProc', plugin_args={'n_procs' : 4})
