# Literal translation of the Perl script https://github.com/andrewjanke/volgenmodel
# to Python and using Nipype interfaces where possible.
#
# In progress: use Nipype workflow.

# Author: Carlo Hamalainen <carlo@carlo-hamalainen.net>

# from nipype import config
# config.enable_debug_mode()

import os
import os.path
import subprocess
import nipype.pipeline.engine as pe
import nipype.interfaces.io as nio
import nipype.interfaces.utility as utils
from copy import deepcopy

from nipypeminc import  \
        Volcentre,      \
        Norm,           \
        Volpad,         \
        Voliso,         \
        Math,           \
        Pik,            \
        Blur,           \
        Gennlxfm,       \
        XfmConcat,      \
        BestLinReg,     \
        NlpFit,         \
        XfmAvg,         \
        XfmInvert,      \
        Resample,       \
        BigAverage,     \
        Reshape,        \
        VolSymm


import glob

import pickle
import gzip

def load_pklz(f):
    return pickle.load(gzip.open(f))

def _calc_threshold_blur_preprocess(input_file):
    import sys
    sys.path.append('/home/carlo/work/github/volgenmodel-nipype') # FIXME how to generalise this?
    from volgenmodel import get_step_sizes
    (step_x, step_y, step_z) = get_step_sizes(input_file)
    return abs(step_x + step_y + step_z)

calc_threshold_blur_preprocess = utils.Function(
                                        input_names=['input_file'],
                                        output_names=['threshold_blur'],
                                        function=_calc_threshold_blur_preprocess)


def _calc_initial_model_fwhm3d(input_file):
    import sys
    sys.path.append('/home/carlo/work/github/volgenmodel-nipype') # FIXME how to generalise this?
    from volgenmodel import get_step_sizes
    (xstep, ystep, zstep) = get_step_sizes(input_file)
    return (abs(xstep*4), abs(ystep*4), abs(zstep*4))

calc_initial_model_fwhm3d = utils.Function(
                                        input_names=['input_file'],
                                        output_names=['fwhm3d'],
                                        function=_calc_initial_model_fwhm3d)

def _write_stage_conf_file(snum, snum_txt, conf, end_stage):
    assert snum is not None
    assert snum_txt is not None
    assert conf is not None
    assert end_stage is not None

    import os.path
    import sys

    sys.path.append('/home/carlo/work/github/volgenmodel-nipype') # FIXME how to generalise this?
    from volgenmodel import to_perl_syntax

    conf_fname = os.path.join(os.getcwd(), "fit_stage_%02d.conf" % snum)
    # print "    + Creating", conf_fname

    with open(conf_fname, 'w') as CONF:
        CONF.write("# %s -- created by %s\n#\n" % (conf_fname, 'FIXME'))
        CONF.write("# End stage: " + str(end_stage) + "\n")
        CONF.write("# Stage Num: " + snum_txt + "\n\n")

        CONF.write('@conf = ')

        conf_dicts = []
        for s in range(end_stage + 1):
            conf_dicts.append({'step': + conf[s]['step'],
                               'blur_fwhm': conf[s]['blur_fwhm'],
                               'iterations': conf[s]['iterations']})

        CONF.write(to_perl_syntax(conf_dicts))

        CONF.write("\n")

    return conf_fname

write_stage_conf_file = utils.Function(
                                    input_names=['snum', 'snum_txt', 'conf', 'end_stage'],
                                    output_names=['conf_fname'],
                                    function=_write_stage_conf_file)

def to_perl_syntax(d):
    """
    Convert a list of dictionaries to Perl-style syntax. Uses
    string-replace so rather brittle.
    """

    return str(d).replace(':', ' => ').replace('[', '(').replace(']', ')')

def from_perl_syntax(d):
    """
    Essentially the inverse of to_perl_syntax() but we also nuke the
    '@' prefix on a list.
    """

    return str(d).replace(' => ', ':').replace('(', '[').replace(')', ']').replace('@', '')

def do_cmd(cmd):
    """
    Run a shell command and return all stdout, throwing an error
    if anything appears on stderr. Only used for commands that are
    expected to be short running, e.g. mincinfo.
    """

    print 'do_cmd:', cmd

    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    stdout, stderr = proc.communicate()

    if stderr == '':
        return stdout
    else:
        assert False, 'Stuff on stderr: ' + str(stderr)

def get_step_sizes(mincfile):
    """
    Get the x, y, and z step sizes from a Minc file.
    """

    xcmd = 'mincinfo -attvalue xspace:step ' + mincfile
    ycmd = 'mincinfo -attvalue yspace:step ' + mincfile
    zcmd = 'mincinfo -attvalue zspace:step ' + mincfile

    xstep = float(do_cmd(xcmd).split()[0])
    ystep = float(do_cmd(ycmd).split()[0])
    zstep = float(do_cmd(zcmd).split()[0])

    return (xstep, ystep, zstep)


if __name__ == '__main__':
    default_conf = [ {'step': 16, 'blur_fwhm': 16, 'iterations': 4},
                     {'step':  8, 'blur_fwhm':  8, 'iterations': 8},
                     {'step':  4, 'blur_fwhm':  4, 'iterations': 8},
                     {'step':  2, 'blur_fwhm':  2, 'iterations': 4},
                   ]

    FAST_EXAMPLE_BASE_DIR = '/scratch/fast-example'

    # Top level workflow.
    workflow = pe.Workflow(name="workflow")

    # FIXME
    # Just for testing, tell Nipype to keep all outputs.
    # workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

    workflow.base_dir = os.path.abspath(FAST_EXAMPLE_BASE_DIR)

    infiles = glob.glob(os.path.join(FAST_EXAMPLE_BASE_DIR, 'sml*.mnc'))

    datasource = pe.Node(interface=nio.DataGrabber(sort_filelist=True), name='datasource_sml')
    datasource.inputs.base_directory = os.path.abspath(FAST_EXAMPLE_BASE_DIR)
    datasource.inputs.template = 'sml*.mnc'

    datasink = pe.Node(interface=nio.DataSink(), name="datasink")
    datasink.inputs.base_directory = os.path.abspath(os.path.join(FAST_EXAMPLE_BASE_DIR, 'volgenmodel_final_output'))

    infiles = sorted(glob.glob(os.path.join(FAST_EXAMPLE_BASE_DIR, 'sml*mnc')))

    opt = { 'verbose': 0,
            'clobber': 0,
            'fake': 0,
            'check': 1,
            'clean': 0,
            'keep_tmp': 0,
            # 'workdir': os.path.join(os.getcwd(), 'work'), # "./$me-work",
            'batch': 0,
            'symmetric': 0,
            'symmetric_dir': 'x',
            'normalise': 1,
            'model_norm_thresh': 0.1,
            'model_min_step': 0.5,
            'pad': 10,
            'iso': 1,
            'config_file': None,
            'linmethod': 'bestlinreg',
            'init_model': None,
            'output_model': None,
            'output_stdev': None,
            'fit_stages': 'lin,lin,lin,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3',
          }

    # from create-model.sh
    opt['symmetric'] = 1
    opt['symmetric_dir'] = 'x'
    opt['check'] = 1
    opt['normalise'] = 1
    opt['model_norm_thresh'] = 0.1
    opt['model_min_step'] = 1.0
    opt['pad'] = 5
    opt['config_file'] = os.path.join(FAST_EXAMPLE_BASE_DIR, 'fit.10-genmodel.conf')
    opt['fit_stages'] = 'lin,1,3'
    opt['output_model'] = 'model.mnc'
    opt['output_stdev'] = 'stdev.mnc'
    # opt['workdir'] = '/scratch/fast-example/work'
    opt['verbose'] = 1
    opt['clobber'] = 1

    def eval_to_int(x):
        try:
            return int(x)
        except:
            return x

    # setup the fit stages
    fit_stages = opt['fit_stages'].split(',')
    fit_stages = map(eval_to_int, fit_stages)

    # check for infiles and create files array
    if opt['verbose']: print "+++ INFILES\n"

    dirs = [None] * len(infiles)
    files = [None] * len(infiles)
    fileh = {}

    c = 0

    for z in infiles:
        dir = None
        f = None

        c_txt = '%04d' % c

        # check
        assert os.path.exists(z)

        # set up arrays
        dirs[c] = os.path.split(z)[0] # &dirname($_);
        files[c] = c_txt + '-' + os.path.basename(z) # "$c_txt-" . &basename($_);
        files[c] = files[c].replace('.mnc', '') # =~ s/\.mnc$//;
        fileh[files[c]] = c

        if opt['verbose']:
            print "  | [{c_txt}] {d} / {f}".format(c_txt=c_txt, d=dirs[c], f=files[c])
        c += 1

    # set up the @conf array
    if opt['config_file'] is not None:
        conf = None
        exec(from_perl_syntax(open(opt['config_file'], 'r').read()))
        assert conf is not None
    else:
        conf = default_conf

    # sanity check for fit config
    if fit_stages[-1] > (len(conf) - 1):
       assert False, ( "Something is amiss with fit config, requested a "
                       "fit step ($fit_stages[-1]) beyond what is defined in the "
                       "fitting protocol (size: $#conf)\n\n")

    # do pre-processing
    preprocess_volcentre = pe.MapNode(
                    interface=Volcentre(zero_dircos=True),
                    name='preprocess_volcentre',
                    iterfield=['input_file'])

    workflow.connect(datasource, 'outfiles', preprocess_volcentre, 'input_file')


    # normalise
    if opt['normalise']:
        preprocess_threshold_blur = pe.MapNode(
                                        interface=deepcopy(calc_threshold_blur_preprocess), # Beware! Need deepcopy since calc_threshold_blur_preprocess is not a constructor!
                                        name='preprocess_threshold_blur',
                                        iterfield=['input_file'])

        workflow.connect(preprocess_volcentre, 'output_file', preprocess_threshold_blur, 'input_file')

        preprocess_normalise = pe.MapNode(
                                    interface=Norm(
                                                cutoff=opt['model_norm_thresh'],
                                                threshold=True,
                                                threshold_perc=opt['model_norm_thresh']),
                                                # output_file=nrmfile),
                                    name='preprocess_normalise',
                                    iterfield=['input_file', 'threshold_blur'])

        workflow.connect(preprocess_threshold_blur, 'threshold_blur', preprocess_normalise, 'threshold_blur')

        # do_cmd('mv -f %s %s' % (nrmfile, resfiles[f],))
    else:
        preprocess_normalise = pe.MapNode(
                                    interface=utils.IdentityInterface(fields=['input_file']),
                                    name='preprocess_normalise',
                                    iterfield=['input_file'])

    workflow.connect(preprocess_volcentre, 'output_file', preprocess_normalise, 'input_file')

    # extend/pad
    if opt['pad'] > 0:
        preprocess_volpad = pe.MapNode(
                                interface=Volpad(
                                            distance=opt['pad'],
                                            smooth=True,
                                            smooth_distance=int(opt['pad'])/3), # FIXME int or float division?
                                            # output_file=fitfiles[f]),
                                name='preprocess_volpad',
                                iterfield=['input_file'])
    else:
        preprocess_volpad = pe.MapNode(
                                    interface=utils.IdentityInterface(fields=['input_file']),
                                    name='preprocess_volpad',
                                    iterfield=['input_file'])

    workflow.connect(preprocess_normalise, 'output_file', preprocess_volpad, 'input_file')

    # isotropic resampling
    if opt['iso']:
        preprocess_voliso = pe.MapNode(
                                    interface=Voliso(avgstep=True), # output_file=isofile),
                                    name='preprocess_voliso',
                                    iterfield=['input_file'])
    else:
        preprocess_voliso = pe.MapNode(
                                    interface=utils.IdentityInterface(fields=['input_file']),
                                    name='preprocess_iso',
                                    iterfield=['input_file'])

    workflow.connect(preprocess_volpad, 'output_file', preprocess_voliso, 'input_file')

    # checkfile
    if opt['check']:
        preprocess_pik = pe.MapNode(
                                interface=Pik(
                                            triplanar=True,
                                            sagittal_offset=10), # output_file=chkfile),
                                name='preprocess_pik',
                                iterfield=['input_file'])
    else:
        preprocess_pik = pe.MapNode(
                                interface=utils.IdentityInterface(fields=['input_file']),
                                name='preprocess_pik',
                                iterfield=['input_file'])

    workflow.connect(preprocess_volpad, 'output_file', preprocess_pik, 'input_file')


    # setup the initial model
    if opt['init_model'] is not None:
        # cmodel = opt['init_model']
        raise NotImplemented
        # To do this, make a data grabber that sends the MNC file to
        # the identity_transformation node below.
    else:
        # Select the 'first' output file from volpad (fitfiles[] in the original volgenmodel).
        select_first_volpad = pe.Node(interface=utils.Select(index=[0]), name='select_first_volpad')
        workflow.connect(preprocess_volpad, 'output_file', select_first_volpad, 'inlist')

        # Select the 'first' input file to calculate the fhwm3d parameter (infiles[] in the original volgenmodel).
        select_first_datasource = pe.Node(interface=utils.Select(index=[0]), name='select_first_datasource')
        workflow.connect(datasource, 'outfiles', select_first_datasource, 'inlist')

        # Calculate the fhwm3d parameter using the first datasource.
        initial_model_fwhm3d = pe.Node(interface=deepcopy(calc_initial_model_fwhm3d), name='initial_model_fwhm3d') # Beware! Need deepcopy since calc_initial_model_fwhm3d is not a constructor!
        workflow.connect(select_first_datasource, 'out', initial_model_fwhm3d, 'input_file')


        initial_model = pe.Node(
                            interface=Blur(), # output_file_base=os.path.join(opt['workdir'], '00-init-model')),
                            name='initial_model')

        workflow.connect(select_first_volpad,  'out',    initial_model, 'input_file')
        workflow.connect(initial_model_fwhm3d, 'fwhm3d', initial_model, 'fwhm3d')

    # Current model starts off as the initial model.
    cmodel = initial_model

    identity_transformation = pe.Node(
                                    interface=Gennlxfm(step=conf[0]['step']), # output_file=initxfm, also output_grid!
                                    name='identity_transformation')

    workflow.connect(initial_model, 'output_file', identity_transformation, 'like')

    # get last linear stage from fit config

    s = None
    end_stage = None

    snum = 0
    lastlin = 0
    for snum in range(len(fit_stages)): # for($snum = 0; $snum <= $#fit_stages; $snum++){
        if fit_stages[snum] == 'lin':
            lastlin = snum # "%02d" % snum

    print "+++ Last Linear stage:", lastlin

    # Foreach end stage in the fitting profile
    print "+++ Fitting";

    last_linear_stage_xfm_node = None

    for snum in range(len(fit_stages)):
        snum_txt = None
        end_stage = None
        # f = None
        # cworkdir = None
        # conf_fname = None
        # modxfm = [None] * len(files)
        # rsmpl = [None] * len(files)

        end_stage = fit_stages[snum]
        snum_txt = "%02d_" % snum
        print "  + [Stage: {snum_txt}] End stage: {end_stage}".format(snum_txt=snum_txt, end_stage=end_stage)

        # make subdir in working dir for files
        # cworkdir = os.path.join(opt['workdir'], snum_txt)
        # if not os.path.exists(cworkdir):
        #     do_cmd('mkdir ' + cworkdir)

        # set up model and xfm names
        # avgxfm = os.path.join(cworkdir, "avgxfm.xfm")
        # iavgfile = os.path.join(cworkdir, "model.iavg.mnc")
        # istdfile = os.path.join(cworkdir, "model.istd.mnc")
        # stage_model = os.path.join(cworkdir, "model.avg.mnc")
        # iavgfilechk = os.path.join(cworkdir, "model.iavg.jpg")
        # istdfilechk = os.path.join(cworkdir, "model.istd.jpg")
        # stage_modelchk = os.path.join(cworkdir, "model.avg.jpg")

        # create the ISO model
        # isomodel_base = os.path.join(cworkdir, "fit-model-iso")
        if end_stage == 'lin':
            _idx = 0
        else:
            _idx = end_stage
        modelmaxstep = conf[_idx]['step']/4

        # check that the resulting model won't be too large
        # this seems confusing but it actually makes sense...
        if float(modelmaxstep) < float(opt['model_min_step']):
            modelmaxstep = opt['model_min_step']

        print "   -- Model Max step:", modelmaxstep

        norm = pe.Node(
                    interface=Norm(
                                cutoff=opt['model_norm_thresh'],
                                threshold=True,
                                threshold_perc=opt['model_norm_thresh'],
                                threshold_blur=3),
                                # output_threshold_mask=isomodel_base + ".msk.mnc"),
                                # input_file=cmodel,
                                # output_file=isomodel_base + ".nrm.mnc"),
                    name='norm_' + snum_txt)

        workflow.connect(cmodel, 'output_file', norm, 'input_file')

        voliso = pe.Node(
                        interface=Voliso(maxstep=modelmaxstep),
                                    # input_file=isomodel_base + ".nrm.mnc",
                                    # output_file=isomodel_base + ".mnc"),
                        name='voliso_' + snum_txt)
        workflow.connect(norm, 'output_file', voliso, 'input_file')

        if opt['check']:
            pik = pe.Node(
                        interface=Pik(
                                    triplanar=True,
                                    horizontal_triplanar_view=True,
                                    scale=4,
                                    tile_size=400,
                                    sagittal_offset=10),
                                    # input_file=isomodel_base + ".mnc",
                                    # output_file=isomodel_base + ".jpg"),
                        name='pik_check_voliso' + snum_txt)

            workflow.connect(voliso, 'output_file', pik, 'input_file')


        # create the isomodel fit mask
        #chomp($step_x = `mincinfo -attvalue xspace:step $isomodel_base.msk.mnc`);
        step_x = 1
        blur = pe.Node(
                    interface=Blur(fwhm=step_x*15), # input_file=isomodel_base + ".msk.mnc",
                                                    # output_file_base=isomodel_base + ".msk"),
                    name='blur_' + snum_txt)

        workflow.connect(norm, 'output_threshold_mask', blur, 'input_file')

        mincmath = pe.Node(
                        interface=Math(test_gt=0.1),
                                    # input_files=[isomodel_base + ".msk_blur.mnc"],
                                    # output_file=isomodel_base + ".fit-msk.mnc"),
                        name='mincmath_' + snum_txt)

        workflow.connect(blur, 'output_file', mincmath, 'input_files')

        # linear or nonlinear fit
        if end_stage == 'lin':
            print "---Linear fit---"
        else:
            print "---Non Linear fit---"

            # create nlin fit config
            if end_stage != 'lin':
                write_conf = pe.Node(
                                    interface=deepcopy(write_stage_conf_file), # Beware! Need deepcopy since write_stage_conf_file is not a constructor!
                                    name='write_conf_' + snum_txt)

                write_conf.inputs.snum       = snum
                write_conf.inputs.snum_txt   = snum_txt
                write_conf.inputs.conf       = conf
                write_conf.inputs.end_stage  = end_stage

        # register each file in the input series
        if end_stage == 'lin':
            assert opt['linmethod'] == 'bestlinreg'
            bestlinreg = pe.MapNode(
                                interface=BestLinReg(),
                                                # source=isomodel_base + ".mnc",
                                                # target=fitfiles[f],
                                                # output_xfm=modxfm[f]),
                                name='register_' + snum_txt,
                                iterfield=['target'])

            workflow.connect(voliso,            'output_file', bestlinreg, 'source')
            workflow.connect(preprocess_voliso, 'output_file', bestlinreg, 'target')

            if snum == lastlin:
                last_linear_stage_xfm_node = bestlinreg

            modxfm = bestlinreg
        else:
            xfmconcat = pe.MapNode(
                                interface=XfmConcat(),
                                            # input_files=[os.path.join(opt['workdir'], lastlin, files[f] + ".xfm"), initxfm],
                                            # output_file=initcnctxfm),
                                name='xfmconcat_for_nlpfit_' + snum_txt,
                                iterfield=['input_files'])

            merge_lastlin_initxfm = pe.MapNode(
                            interface=utils.Merge(2),
                            name='merge_lastlin_initxfm_' + snum_txt,
                            iterfield=['in1'])

            workflow.connect(last_linear_stage_xfm_node, 'output_xfm',  merge_lastlin_initxfm, 'in1')
            workflow.connect(identity_transformation,    'output_file', merge_lastlin_initxfm, 'in2')

            workflow.connect(merge_lastlin_initxfm, 'out', xfmconcat, 'input_files')

            workflow.connect(identity_transformation, 'output_grid', xfmconcat, 'input_grid_files')

            nlpfit = pe.MapNode(
                            interface=NlpFit(),
                                        # init_xfm=initcnctxfm,
                                        # config_file=conf_fname),
                                        # source_mask=isomodel_base + ".fit-msk.mnc",
                                        # source=isomodel_base + ".mnc",
                                        # target=fitfiles[f],
                                        # output_xfm=modxfm[f]),
                            name='nlpfit_' + snum_txt,
                            iterfield=['target', 'init_xfm'])

            workflow.connect(write_conf, 'conf_fname', nlpfit, 'config_file')

            workflow.connect(xfmconcat,         'output_file', nlpfit, 'init_xfm')
            workflow.connect(mincmath,          'output_file', nlpfit, 'source_mask')
            workflow.connect(voliso,            'output_file', nlpfit, 'source')
            workflow.connect(preprocess_voliso, 'output_file', nlpfit, 'target') # FIXME Make sure that fitfiles[f] is preprocess_voliso at this point in the program.

            workflow.connect(xfmconcat, 'output_grids', nlpfit, 'input_grid_files')

            modxfm = nlpfit

        # average xfms
        xfmavg = pe.Node(
                        interface=XfmAvg(),
                                    # input_files=modxfm,
                                    # output_file=avgxfm),
                        name='xfmavg_' + snum_txt)


        if end_stage != 'lin':
            workflow.connect(nlpfit, 'output_grid', xfmavg, 'input_grid_files')

        workflow.connect(modxfm, 'output_xfm', xfmavg, 'input_files') # FIXME check that this works - multiple outputs of MapNode going into single list of xfmavg.

        if end_stage == 'lin':
            xfmavg.interface.inputs.ignore_nonlinear = True
        else:
            xfmavg.interface.inputs.ignore_linear = True


        # invert model xfm
        xfminvert = pe.MapNode(
                            interface=XfmInvert(),
                                        # input_file=modxfm[f],
                                        # output_file=invxfm),
                            name='xfminvert_' + snum_txt,
                            iterfield=['input_file'])

        workflow.connect(modxfm, 'output_xfm', xfminvert, 'input_file')

        # concat: invxfm, avgxfm
        merge_xfm = pe.MapNode(
                        interface=utils.Merge(2),
                        name='merge_xfm_' + snum_txt,
                        iterfield=['in1'])

        workflow.connect(xfminvert, 'output_file', merge_xfm, 'in1')
        workflow.connect(xfmavg,    'output_file', merge_xfm, 'in2')

        # Collect grid files of xfminvert and xvmavg. This is in two steps.
        #
        # 1. Merge MapNode results.
        merge_xfm_mapnode_result = pe.Node(
                            interface=utils.Merge(1),
                            name='merge_xfm_mapnode_result_' + snum_txt)
        workflow.connect(xfminvert, 'output_grid', merge_xfm_mapnode_result, 'in1')

        # 2. Merge xfmavg's single output with the result from step 1.
        merge_xfmavg_and_step1 = pe.Node(
                        interface=utils.Merge(2),
                        name='merge_xfmavg_and_step1' + snum_txt)
        workflow.connect(merge_xfm_mapnode_result,  'out',         merge_xfmavg_and_step1, 'in1')
        workflow.connect(xfmavg,                    'output_grid', merge_xfmavg_and_step1, 'in2')

        xfmconcat = pe.MapNode(
                            interface=XfmConcat(),
                                            # input_files=[invxfm, avgxfm],
                                            # output_file=resxfm),
                            name='xfmconcat_' + snum_txt,
                            iterfield=['input_files'])

        workflow.connect(merge_xfm, 'out', xfmconcat, 'input_files')

        workflow.connect(merge_xfmavg_and_step1, 'out', xfmconcat, 'input_grid_files')

        # resample
        resample = pe.MapNode(
                            interface=Resample(sinc_interpolation=True),
                                        # transformation=resxfm,
                                        # like=isomodel_base + ".mnc",
                                        # input_file=resfiles[f],
                                        # output_file=rsmpl[f]),
                            name='resample_' + snum_txt,
                            iterfield=['input_file', 'transformation'])

        workflow.connect(preprocess_normalise, 'output_file', resample, 'input_file')

        workflow.connect(xfmconcat, 'output_file',  resample, 'transformation')

        workflow.connect(voliso,               'output_file', resample, 'like')

        if opt['check']:
            pik_check_resample = pe.MapNode(
                                        interface=Pik(
                                                    triplanar=True,
                                                    sagittal_offset=10),
                                                    # input_file=rsmpl[f],
                                                    # output_file=chkfile),
                                        name='pik_check_resample_' + snum_txt,
                                        iterfield=['input_file'])

            workflow.connect(resample, 'output_file', pik_check_resample, 'input_file')

        # create model
        bigaverage = pe.Node(
                            interface=BigAverage(
                                            output_float=True,
                                            robust=True),
                                            # tmpdir=os.path.join(opt['workdir'], 'tmp'),
                                            # sd_file=istdfile,
                                            # input_files=rsmpl,
                                            # output_file=iavgfile),
                            name='bigaverage_' + snum_txt,
                            iterfield=['input_file'])

        workflow.connect(resample, 'output_file', bigaverage, 'input_files')

        if opt['check']:
            pik_check_iavg = pe.Node(
                                    interface=Pik(
                                                triplanar=True,
                                                horizontal_triplanar_view=True,
                                                scale=4,
                                                tile_size=400,
                                                sagittal_offset=10),
                                                # input_file=iavgfile,
                                                # output_file=iavgfilechk),
                                    name='pik_check_iavg_' + snum_txt)

            workflow.connect(bigaverage, 'output_file', pik_check_iavg, 'input_file')

        # do symmetric averaging if required
        if opt['symmetric']:
            # symxfm = os.path.join(cworkdir, 'model.sym.xfm')
            # symfile = os.path.join(cworkdir, 'model.iavg-short.mnc')

            # convert double model to short
            resample_to_short = pe.Node(
                                        interface=Reshape(write_short=True),
                                                    # input_file=iavgfile,
                                                    # output_file=symfile),
                                        name='resample_to_short_' + snum_txt)

            workflow.connect(bigaverage, 'output_file', resample_to_short, 'input_file')


            assert opt['symmetric_dir'] == 'x' # FIXME handle other cases
            volsymm_on_short = pe.Node(
                                    interface=VolSymm(x=True),
                                                    # input_file=symfile,
                                                    # trans_file=symxfm, # FIXME This is an output!
                                                    # output_file=stage_model),
                                    name='volsymm_on_short_' + snum_txt)

            workflow.connect(resample_to_short, 'output_file', volsymm_on_short, 'input_file')

            # set up fit args
            if end_stage == 'lin':
                volsymm_on_short.interface.inputs.fit_linear = True
            else:
                volsymm_on_short.interface.inputs.fit_nonlinear = True
                workflow.connect(write_conf, 'conf_fname', volsymm_on_short, 'config_file')

        else:
            # do_cmd('ln -s -f %s %s' % (os.path.basename(iavgfile), stage_model,))
            volsymm_on_short = pe.Node(
                                    interface=utils.IdentityInterface(fields=['input_file']),
                                    name='volsymm_on_short_' + snum_txt)

            workflow.connect(bigaverage, 'output_file', volsymm_on_short, 'input_file')

        # We finally have the stage model.
        stage_model = volsymm_on_short

        if opt['check']:
            pik_on_stage_model = pe.Node(
                                        interface=Pik(
                                                    triplanar=True,
                                                    horizontal_triplanar_view=True,
                                                    scale=4,
                                                    tile_size=400,
                                                    sagittal_offset=10),
                                                    # input_file=stage_model,
                                                    # output_file=stage_modelchk),
                                        name='pik_on_stage_model_' + snum_txt)

            workflow.connect(stage_model, 'output_file', pik_on_stage_model, 'input_file')


        # if on last step, copy model to $opt{'output_model'}
        if snum == len(fit_stages) - 1:
            workflow.connect(stage_model, 'output_file', datasink, 'model')

            # create and output standard deviation file if requested
            if opt['output_stdev'] is not None:
                if opt['symmetric']:
                    assert opt['symmetric_dir'] == 'x' # FIXME handle other cases
                    volsymm_final_model = pe.Node(
                                                interface=VolSymm(
                                                                x=True,
                                                                nofit=True),
                                                                # input_file=istdfile,
                                                                # trans_file=symxfm, # FIXME This is an output!
                                                                # output_file=opt['output_stdev']),
                                                name='volsymm_final_model_' + snum_txt)

                    workflow.connect(bigaverage,        'sd_file',      volsymm_final_model, 'input_file')
                    workflow.connect(volsymm_on_short,  'trans_file',   volsymm_final_model, 'trans_file')
                    workflow.connect(volsymm_on_short,  'output_grid',  volsymm_final_model, 'input_grid_files')
                    workflow.connect(volsymm_final_model, 'output_file', datasink, 'stdev') # FIXME we ignore opt['output_stdev']
                else:
                    # do_cmd('cp -f %s %s' % (istdfile, opt['output_stdev'],))
                    workflow.connect(bigaverage, 'sd_file', datasink, 'stdev') # FIXME we ignore opt['output_stdev']

        cmodel = stage_model

    # workflow.run(plugin='MultiProc', plugin_args={'n_procs' : 8})
