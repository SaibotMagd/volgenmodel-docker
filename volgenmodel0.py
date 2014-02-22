# Literal translation of the Perl script https://github.com/andrewjanke/volgenmodel
# to Python and using Nipype interfaces where possible.
#
# Currently this code only runs on a single core as it does not take advantage
# of Nipype's workflow functionality. Future versions will support this.

# Author: Carlo Hamalainen <carlo@carlo-hamalainen.net>

from nipype import config
config.enable_debug_mode()

import os
import os.path
import subprocess
# import nipype.pipeline.engine as pe
# import nipype.interfaces.io as nio
# import nipype.interfaces.utility as utils

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

def to_perl_syntax(d):
    """
    Convert a list of dictionaries to Perl-style syntax. Uses
    string-replace so rather brittle.
    """

    return str(d).replace(':', ' => ').replace('[', '(').replace(']', ')')

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
        assert False, 'Stuff on stderr: ' + str(stderr) # FIXME Change to an appropriate exception?

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


default_conf = [ {'step': 16, 'blur_fwhm': 16, 'iterations': 4},
                 {'step':  8, 'blur_fwhm':  8, 'iterations': 8},
                 {'step':  4, 'blur_fwhm':  4, 'iterations': 8},
                 {'step':  2, 'blur_fwhm':  2, 'iterations': 4},
               ]

infiles = sorted(glob.glob('/scratch/fast-example/sml*mnc'))

opt = { 'verbose': 0,
        'clobber': 0,
        'fake': 0,
        'check': 1,
        'clean': 0,
        'keep_tmp': 0,
        'workdir': os.path.join(os.getcwd(), 'work'), # "./$me-work",
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
opt['config_file'] = '/scratch/fast-example/py.fit.10-genmodel.conf'
opt['fit_stages'] = 'lin,1,3'
opt['output_model'] = 'model.mnc'
opt['output_stdev'] = 'stdev.mnc'
opt['workdir'] = '/scratch/fast-example/work'
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

# # check for output model
# $opt{'output_model'} = "$dirs[0]/VolModel-ALL.mnc" if !defined($opt{'output_model'});
# if(-e $opt{'output_model'} && !$opt{'clobber'}){
#    die "$me: $opt{'output_model'} exists, use -clobber to overwrite\n\n";
#    }

# make working dir
do_cmd('mkdir ' + opt['workdir']) # if !-e $opt{'workdir'};

# save the original command
# open(FH, '>', "$opt{'workdir'}/orig-command.sh");
# print FH "#! /bin/sh\n" .
#          "#\n".
#          "# volgenmodel script\n\n" .
#          join(' ', @orig_cmd) ."\n";
# close(FH);
# &do_cmd('chmod', '+x', "$opt{'workdir'}/orig-command.sh");

# write script to kill processing
# if($opt{'batch'}){
#   open(FH, '>', "$opt{'workdir'}/kill-proc.sh");
#   print FH "#! /bin/sh\n" .
#            "#\n" .
#            "# simple script to kill processing\n\n" .
#            "qdel \'*$$*\'\n";
#   close(FH);
#   &do_cmd('chmod', '+x', "$opt{'workdir'}/kill-proc.sh");
#   }

# set up the @conf array
if opt['config_file'] is not None:
    conf = eval(open(opt['config_file'], 'r').read())
else:
    conf = default_conf

# sanity check for fit config
if fit_stages[-1] > (len(conf) - 1):
   assert False, ( "Something is amiss with fit config, requested a "
                   "fit step ($fit_stages[-1]) beyond what is defined in the "
                   "fitting protocol (size: $#conf)\n\n")

# do pre-processing

cleanfiles = []

nrmfile = [None] * len(files)
isofile = [None] * len(files)
chkfile = [None] * len(files)
resfiles = [None] * len(files)
fitfiles = [None] * len(files)

print "+++ pre-processing input data"

predir = opt['workdir'] + '/00-pre'
do_cmd('mkdir -p ' + predir)

for f in range(len(files)): # for($f=0; $f<=$#files; $f++){
    resfiles[f] = os.path.join(predir, files[f] + '.res.mnc')
    fitfiles[f] = os.path.join(predir, files[f] + '.fit.mnc')
    nrmfile = os.path.join(predir, files[f] + '.nrm.mnc')
    isofile = os.path.join(predir, files[f] + '.iso.mnc')
    chkfile = os.path.join(predir, files[f] + '.fit.jpg')

    print "ZZZ pre-processing loop; f: ", f
    print "ZZZ pre-processing loop; resfiles[f]: ", resfiles[f]
    print "ZZZ pre-processing loop; fitfiles[f]: ", fitfiles[f]
    print "ZZZ pre-processing loop; nrmfile[f]: ", nrmfile
    print "ZZZ pre-processing loop; isofile[f]: ", isofile
    print "ZZZ pre-processing loop; chkfile[f]: ", chkfile

    cleanfiles.append(nrmfile)

    if os.path.exists(resfiles[f]) and os.path.exists(fitfiles[f]):
        print "   | %s - exists, skipping" % resfiles[f]
    else:
        # centre the volume so that a PAT xfm has a greater chance
        print "   | %s - centreing" % resfiles[f]

        # &do_cmd_batch("CEN$$-$f", 'none',
        #               'volcentre', '-clobber',
        #               '-zero_dircos',
        #               $infiles[$f], $resfiles[$f]);
        volcentre = Volcentre(
                        input_file=infiles[f],
                        output_file=resfiles[f],
                        zero_dircos=True)
        volcentre.run()

        # normalise
        if opt['normalise']:
            # get step sizes
            # chomp($step_x = `mincinfo -attvalue xspace:step $infiles[$f]`);
            # chomp($step_y = `mincinfo -attvalue yspace:step $infiles[$f]`);
            # chomp($step_z = `mincinfo -attvalue zspace:step $infiles[$f]`);
            (step_x, step_y, step_z) = get_step_sizes(infiles[f])

            print "   | %s - normalising" % nrmfile

            # &do_cmd_batch("NRM$$-$f", "CEN$$-$f",
            #               'mincnorm', '-clobber',
            #               '-cutoff', $opt{'model_norm_thresh'},
            #               '-threshold',
            #               '-threshold_perc', $opt{'model_norm_thresh'},
            #               '-threshold_blur', abs($step_x + $step_y + $step_z),
            #               $resfiles[$f], $nrmfile);
            normalise = Norm(
                            cutoff=opt['model_norm_thresh'],
                            threshold=True,
                            threshold_perc=opt['model_norm_thresh'],
                            threshold_blur=abs(step_x + step_y + step_z),
                            input_file=resfiles[f],
                            output_file=nrmfile)
            normalise.run()

            # &do_cmd_batch("NMV$$-$f", "NRM$$-$f",
            #               'mv', '-f', $nrmfile, $resfiles[$f]);
            do_cmd('mv -f %s %s' % (nrmfile, resfiles[f],))
        else:
            # &do_cmd_batch("NMV$$-$f", "CEN$$-$f", "true");
            pass

        # extend/pad
        if opt['pad'] > 0:
           print "   | %s - padding" % fitfiles[f]

           # &do_cmd_batch("PAD$$-$f", "NMV$$-$f",
           #               'volpad', '-clobber',
           #               '-distance', $opt{'pad'},
           #               '-smooth',
           #               '-smooth_distance', sprintf('%d', $opt{'pad'}/3),
           #               $resfiles[$f], $fitfiles[$f]);
           volpad = Volpad(
                        distance=opt['pad'],
                        smooth=True,
                        smooth_distance=int(opt['pad'])/3, # FIXME int or float division?
                        input_file=resfiles[f],
                        output_file=fitfiles[f])
           volpad.run()
        else:
           # &do_cmd_batch("PAD$$-$f", "NMV$$-$f",
           #               'cp', '-f', $resfiles[$f], $fitfiles[$f]);
           do_cmd('cp -f %s %s' % (resfiles[f], fitfiles[f],))

        # isotropic resampling
        if opt['iso']:
            print "   | %s - resampling isotropically" % isofile

            # do_cmd_batch("ISO$$-$f", "PAD$$-$f",
            #              'voliso', '--clobber',
            #              '--avgstep',
            #              $fitfiles[$f], $isofile);
            voliso = Voliso(
                        avgstep=True,
                        input_file=fitfiles[f],
                        output_file=isofile)
            voliso.run()
            # &do_cmd_batch("IMV$$-$f", "ISO$$-$f",
            #               'mv', '-f', $isofile, $fitfiles[$f]);
            do_cmd('mv -f %s %s' % (isofile, fitfiles[f],))
        else:
           # &do_cmd_batch("IMV$$-$f", "PAD$$-$f", "true");
           pass

        # checkfile
        if opt['check']:
            # &do_cmd_batch("cPAD$$-$f", "IMV$$-$f",
            #               'mincpik', '-clobber',
            #               '-triplanar',
            #               '-sagittal_offset', 10,
            #               $fitfiles[$f], $chkfile)
            pik = Pik(
                    triplanar=True,
                    sagittal_offset=10,
                    input_file=fitfiles[f],
                    output_file=chkfile)
            pik.run()

# clean up
# &do_cmd_batch("CLN$$-nrm", "PAD$$-*",
#               'rm', '-f', @cleanfiles) if $opt{'clean'};

# setup the initial model
print "+++ Setting up the initial model"

if opt['init_model'] is not None:
    cmodel = opt['init_model']
else:
   # create the initial model from the "first" file
   cmodel = os.path.join(opt['workdir'], '00-init-model_blur.mnc')

   if os.path.exists(cmodel):
      print "   | %s - exists, skipping" % cmodel
      # &do_cmd_batch("BLR$$-init-model", "IMV$$-0", 'true');
   else:
      # my($step_x, $step_y, $step_z);
      # get step sizes
      # chomp($step_x = `mincinfo -attvalue xspace:step $infiles[0]`);
      # chomp($step_y = `mincinfo -attvalue yspace:step $infiles[0]`);
      # chomp($step_z = `mincinfo -attvalue zspace:step $infiles[0]`);
      (step_x, step_y, step_z) = get_step_sizes(infiles[0])

      print "   | %s - creating" % cmodel

      # &do_cmd_batch("BLR$$-init-model", "IMV$$-0",
      #               'mincblur', '-clobber',
      #               '-3dfwhm', abs($step_x * 4), abs($step_y * 4), abs($step_z * 4),
      #               $fitfiles[0], "$opt{'workdir'}/00-init-model");
      blur = Blur(
                fwhm3d=(abs(step_x * 4), abs(step_y * 4), abs(step_z * 4)),
                input_file=fitfiles[0],
                output_file_base=os.path.join(opt['workdir'], '00-init-model'))
      blur.run()

# create an apropriate identity transformation
initxfm = os.path.join(opt['workdir'], 'ident-' + str(conf[0]['step']) + '.xfm')
# &do_cmd_batch("IDT$$", "BLR$$-init-model",
#               'gennlxfm', '-clobber',
#               '-like', $cmodel,
#               '-step', $conf[0]{'step'},
#               $initxfm);
gennlxfm = Gennlxfm(
                like=cmodel,
                step=conf[0]['step'],
                output_file=initxfm)
gennlxfm.run()

# get last linear stage from fit config

s = None
end_stage = None

snum = 0
lastlin = '00'
for snum in range(len(fit_stages)): # for($snum = 0; $snum <= $#fit_stages; $snum++){
    if fit_stages[snum] == 'lin':
        lastlin = "%02d" % snum

print "+++ Last Linear stage:", lastlin

# Foreach end stage in the fitting profile
print "+++ Fitting";
for snum in range(len(fit_stages)): # for($snum = 0; $snum <= $#fit_stages; $snum++){
    # my($snum_txt, $end_stage, $f, $cworkdir, $conf_fname, @modxfm, @rsmpl);
    # my($step_x, $step_y, $step_z);
    snum_txt = None
    end_stage = None
    f = None
    cworkdir = None
    conf_fname = None
    modxfm = [None] * len(files)
    rsmpl = [None] * len(files)

    # my($step_x, $step_y, $step_z);

    end_stage = fit_stages[snum]
    snum_txt = "%02d" % snum
    print "  + [Stage: {snum_txt}] End stage: {end_stage}".format(snum_txt=snum_txt, end_stage=end_stage)

    # make subdir in working dir for files
    cworkdir = os.path.join(opt['workdir'], snum_txt)
    if not os.path.exists(cworkdir):
        do_cmd('mkdir ' + cworkdir)

    # set up model and xfm names
    # my($avgxfm, $symxfm, $iavgfile, $istdfile, $stage_model, $iavgfilechk, $istdfilechk, $stage_modelchk);
    avgxfm = os.path.join(cworkdir, "avgxfm.xfm")
    iavgfile = os.path.join(cworkdir, "model.iavg.mnc")
    istdfile = os.path.join(cworkdir, "model.istd.mnc")
    stage_model = os.path.join(cworkdir, "model.avg.mnc")
    iavgfilechk = os.path.join(cworkdir, "model.iavg.jpg")
    istdfilechk = os.path.join(cworkdir, "model.istd.jpg")
    stage_modelchk = os.path.join(cworkdir, "model.avg.jpg")

    # if this stages model exists, skip to the next stage
    if os.path.exists(stage_model):
       print "   | %s - exists, skipping" % stage_model;
       cmodel = stage_model
       continue

    # create the ISO model
    isomodel_base = os.path.join(cworkdir, "fit-model-iso")

    print "   | %s - creating" % isomodel_base

    # $modelmaxstep = $conf[(($end_stage eq 'lin') ? 0 : $end_stage)]{'step'}/4;
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

    # &do_cmd_batch("NRM$$-$snum_txt-model", "BLR$$-init-model",
    #               'mincnorm', '-clobber',
    #               '-cutoff', $opt{'model_norm_thresh'},
    #               '-threshold',
    #               '-threshold_perc', $opt{'model_norm_thresh'},
    #               '-threshold_blur', 3,
    #               '-threshold_mask', "$isomodel_base.msk.mnc",
    #               $cmodel, "$isomodel_base.nrm.mnc");
    norm = Norm(
            cutoff=opt['model_norm_thresh'],
            threshold=True,
            threshold_perc=opt['model_norm_thresh'],
            threshold_blur=3,
            threshold_mask=isomodel_base + ".msk.mnc",
            input_file=cmodel,
            output_file=isomodel_base + ".nrm.mnc")
    norm.run()

    # &do_cmd_batch("ISO$$-$snum_txt-model", "NRM$$-$snum_txt-model",
    #               'voliso', '-clobber',
    #               '-maxstep', $modelmaxstep,
    #               "$isomodel_base.nrm.mnc","$isomodel_base.mnc");
    voliso = Voliso(
                maxstep=modelmaxstep,
                input_file=isomodel_base + ".nrm.mnc",
                output_file=isomodel_base + ".mnc")
    voliso.run()

    if opt['check']:
        # &do_cmd_batch("cISO$$-$snum_txt-model", "ISO$$-$snum_txt-model",
        #               'mincpik', '-clobber',
        #               '-triplanar', '-horizontal',
        #               '-scale', 4, '-tilesize', 400,
        #               '-sagittal_offset', 10,
        #               "$isomodel_base.mnc", "$isomodel_base.jpg")

        pik = Pik(
                triplanar=True,
                horizontal_triplanar_view=True,
                scale=4,
                tile_size=400,
                sagittal_offset=10,
                input_file=isomodel_base + ".mnc",
                output_file=isomodel_base + ".jpg")
        pik.run()

    # create the isomodel fit mask
    #chomp($step_x = `mincinfo -attvalue xspace:step $isomodel_base.msk.mnc`);
    step_x = 1
    # &do_cmd_batch("ISB$$-$snum_txt-model", "NRM$$-$snum_txt-model",
    #               'mincblur', '-clobber',
    #               '-fwhm', ($step_x * 15),
    #               "$isomodel_base.msk.mnc", "$isomodel_base.msk");
    blur = Blur(
            fwhm=step_x*15,
            input_file=isomodel_base + ".msk.mnc",
            output_file_base=isomodel_base + ".msk")
    blur.run()

    # &do_cmd_batch("ISM$$-$snum_txt-model", "ISB$$-$snum_txt-model",
    #               'mincmath', '-clobber',
    #               '-gt', '-const', 0.1,
    #               "$isomodel_base.msk_blur.mnc", "$isomodel_base.fit-msk.mnc");
    mincmath = Math(
                test_gt=0.1,
                input_files=[isomodel_base + ".msk_blur.mnc"],
                output_file=isomodel_base + ".fit-msk.mnc")
    mincmath.run()

    # linear or nonlinear fit
    if end_stage == 'lin':
        print "---Linear fit---"
    else:
        print "---Non Linear fit---"

        # create nlin fit config
        if end_stage != 'lin':
            conf_fname = os.path.join(cworkdir, "fit.conf")
            print "    + Creating", conf_fname

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

    # register each file in the input series
    for f in range(len(files)): # for($f=0; $f<=$#files; $f++)
        modxfm[f] = os.path.join(cworkdir, files[f] + ".xfm")

        if os.path.exists(modxfm[f]):
            print "---%s exists, skipping---" % modxfm[f]
            # &do_cmd_batch("FIT$$-$snum_txt-$f", "ISO$$-$snum_txt-model", 'true');
        else:
            if end_stage == 'lin':
                # &do_cmd_batch("FIT$$-$snum_txt-$f", "ISO$$-$snum_txt-model",
                #               split(/\ /, $opt{'linmethod'}),
                #               '-clobber',
                #               "$isomodel_base.mnc", $fitfiles[$f], $modxfm[$f]);
                assert opt['linmethod'] == 'bestlinreg'
                bestlinreg = BestLinReg(
                                 source=isomodel_base + ".mnc",
                                 target=fitfiles[f],
                                 output_xfm=modxfm[f])
                bestlinreg.run() # FIXME check these outputs explicitly.
            else:
                # use the last linear xfm as a starting point
                initcnctxfm = os.path.join(cworkdir, 'init-' + files[f] + ".xfm")
                # &do_cmd_batch("IXF$$-$snum_txt-$f", "ISO$$-$snum_txt-model,IDT$$",
                #               'xfmconcat', '-clobber',
                #               "$opt{'workdir'}/$lastlin/$files[$f].xfm", $initxfm,
                #               $initcnctxfm);
                xfmconcat = XfmConcat(
                                input_files=[os.path.join(opt['workdir'], lastlin, files[f] + ".xfm"),
                                             initxfm],
                                output_file=initcnctxfm)
                xfmconcat.run()

                # &do_cmd_batch("FIT$$-$snum_txt-$f", "IXF$$-$snum_txt-$f,ISM$$-$snum_txt-model",
                #               'nlpfit', '-clobber',
                #               '-init_xfm', $initcnctxfm,
                #               '-config', $conf_fname,
                #               '-source_mask', "$isomodel_base.fit-msk.mnc",
                #               "$isomodel_base.mnc", $fitfiles[$f], $modxfm[$f]);
                nlpfit = NlpFit(
                            init_xfm=initcnctxfm,
                            config_file=conf_fname,
                            source_mask=isomodel_base + ".fit-msk.mnc",
                            source=isomodel_base + ".mnc",
                            target=fitfiles[f],
                            output_xfm=modxfm[f])
                nlpfit.run()

    # average xfms
    # &do_cmd_batch("AXF$$-$snum_txt", "FIT$$-$snum_txt-*",
    #               'xfmavg', '-clobber',
    #               (($end_stage eq 'lin') ? '-ignore_nonlinear' : '-ignore_linear'),
    #               @modxfm, $avgxfm);
    xfmavg = XfmAvg(
                input_files=[m for m in modxfm if m is not None], # FIXME averaging model xfms so far?
                output_file=avgxfm)

    if end_stage == 'lin':
        xfmavg.inputs.ignore_nonlinear = True
    else:
        xfmavg.inputs.ignore_linear = True

    xfmavg.run()

    # resample each file in the input series
    for f in range(len(files)): # for($f=0; $f<=$#files; $f++)
        invxfm = os.path.join(cworkdir, 'inv-' + files[f] + '.xfm')
        resxfm = os.path.join(cworkdir, 'rsmpl-' + files[f] + '.xfm')
        rsmpl[f] = os.path.join(cworkdir, 'rsmpl-' + files[f] + '.mnc')
        chkfile = os.path.join(cworkdir, 'rsmpl-' + files[f] + '.jpg')

        if os.path.exists(rsmpl[f]):
            print "   | %s - exists, skipping" % rsmpl[f]
        else:
            print "   | %s - resampling" % rsmpl[f]

            # invert model xfm
            # &do_cmd_batch("XIN$$-$snum_txt-$f", "FIT$$-$snum_txt-$f",
            #               'xfminvert', '-clobber', $modxfm[$f], $invxfm);
            xfminvert = XfmInvert(
                            input_file=modxfm[f],
                            output_file=invxfm)
            xfminvert.run()

            # concat
            # &do_cmd_batch("XCN$$-$snum_txt-$f", "AXF$$-$snum_txt,XIN$$-$snum_txt-$f",
            #               'xfmconcat', '-clobber', $invxfm, $avgxfm, $resxfm);
            xfmconcat = XfmConcat(
                            input_files=[invxfm, avgxfm],
                            output_file=resxfm)
            xfmconcat.run()

            # resample
            # &do_cmd_batch("RES$$-$snum_txt-$f", "XCN$$-$snum_txt-$f",
            #               'mincresample', '-clobber',
            #               '-sinc',
            #               '-transformation', $resxfm,
            #               '-like', "$isomodel_base.mnc",
            #               $resfiles[$f], $rsmpl[$f]);
            resample = Resample(
                            sinc_interpolation=True,
                            transformation=resxfm,
                            like=isomodel_base + ".mnc",
                            input_file=resfiles[f],
                            output_file=rsmpl[f])
            resample.run()

            # &do_cmd_batch("cRES$$-$snum_txt-$f", "RES$$-$snum_txt-$f",
            #               'mincpik', '-clobber',
            #               '-triplanar',
            #               '-sagittal_offset', 10,
            #               $rsmpl[$f], $chkfile) if $opt{'check'};
            if opt['check']:
                pik = Pik(
                        triplanar=True,
                        sagittal_offset=10,
                        input_file=rsmpl[f],
                        output_file=chkfile)
                pik.run()

    # create model
    # &do_cmd_batch("IAV$$-$snum_txt", "RES$$-$snum_txt-*",
    #               'mincbigaverage', '-clobber',
    #               '-float',
    #               '-robust',
    #               '-tmpdir', "$opt{'workdir'}/tmp",
    #               '-sdfile', $istdfile,
    #               @rsmpl, $iavgfile);
    bigaverage = BigAverage(
                    output_float=True,
                    robust=True,
                    tmpdir=os.path.join(opt['workdir'], 'tmp'),
                    sd_file=istdfile,
                    input_files=[r for r in rsmpl if r is not None], # FIXME need this filter?
                    output_file=iavgfile)
    bigaverage.run()

    # &do_cmd_batch("cIAV$$-$snum_txt", "IAV$$-$snum_txt",
    #               'mincpik', '-clobber',
    #               '-triplanar', '-horizontal',
    #               '-scale', 4, '-tilesize', 400,
    #               '-sagittal_offset', 10,
    #               $iavgfile, $iavgfilechk) if $opt{'check'};
    if opt['check']:
        pik = Pik(
                triplanar=True,
                horizontal_triplanar_view=True,
                scale=4,
                tile_size=400,
                sagittal_offset=10,
                input_file=iavgfile,
                output_file=iavgfilechk)
        pik.run()

    # do symmetric averaging if required
    if opt['symmetric']:
        # my (@fit_args, $symfile);

        symxfm = os.path.join(cworkdir, 'model.sym.xfm')
        symfile = os.path.join(cworkdir, 'model.iavg-short.mnc')

        # convert double model to short
        # &do_cmd_batch("MTS$$-$snum_txt", "IAV$$-$snum_txt",
        #               'mincreshape', '-clobber',
        #               '-short',
        #               $iavgfile, $symfile);
        resample = Reshape(
                        write_short=True,
                        input_file=iavgfile,
                        output_file=symfile)
        resample.run()

        # &do_cmd_batch("SYM$$-$snum_txt", "MTS$$-$snum_txt",
        #               'volsymm', '-clobber',
        #               "-$opt{'symmetric_dir'}",
        #               @fit_args,
        #               $symfile, $symxfm, $stage_model);
        assert opt['symmetric_dir'] == 'x' # FIXME handle other cases
        volsymm = VolSymm(
                    x=True,
                    input_file=symfile,
                    trans_file=symxfm, # FIXME This is an output!
                    output_file=stage_model)

        # set up fit args
        if end_stage == 'lin':
            volsymm.inputs.fit_linear = True
        else:
            volsymm.inputs.fit_nonlinear = True
            volsymm.inputs.config_file = conf_fname

        volsymm.run()

    else:
       # &do_cmd_batch("SYM$$-$snum_txt", "IAV$$-$snum_txt",
       #               'ln', '-s', '-f', &basename($iavgfile), $stage_model);
       do_cmd('ln -s -f %s %s' % (os.path.basename(iavgfile), stage_model,))

    # &do_cmd_batch("cSYM$$-$snum_txt", "SYM$$-$snum_txt",
    #               'mincpik', '-clobber',
    #               '-triplanar', '-horizontal',
    #               '-scale', 4, '-tilesize', 400,
    #               '-sagittal_offset', 10,
    #               $stage_model, $stage_modelchk) if $opt{'check'};
    if opt['check']:
        pik = Pik(
                triplanar=True,
                horizontal_triplanar_view=True,
                scale=4,
                tile_size=400,
                sagittal_offset=10,
                input_file=stage_model,
                output_file=stage_modelchk)
        pik.run()

    # # create clean script for resampled and temp xfm files
    # open(CLEAN, ">$cworkdir/clean.sh");
    # print CLEAN "#! /bin/sh\n" .
    #             "#\n" .
    #             "# clean up for stage $snum_txt\n" .
    #             "\n" .
    #             "if [ -e $stage_model ]\n" .
    #             "then\n" .
    #             "   echo \"Removing files\"\n   \n" .
    #             "   rm -f $cworkdir/rsmpl-*.mnc\n" .
    #             "   rm -f $cworkdir/rsmpl-*.xfm\n" .
    #             "   rm -f $cworkdir/inv-*.xfm\n" .
    #             "   rm -f $cworkdir/inv-*.mnc\n" .
    #             "   rm -f $cworkdir/init-*.xfm\n" .
    #             "   rm -f $cworkdir/init-*.mnc\n" .
    #             "   rm -rf $opt{'workdir'}/tmp\n" .
    #             "fi\n";
    # close(CLEAN);
    # &do_cmd('chmod', '+x', "$cworkdir/clean.sh");

    # # run clean script if required
    # if($opt{'clean'}){
    #    &do_cmd_batch("CLN$$-$snum_txt", "SYM$$-$snum_txt",
    #                  "$cworkdir/clean.sh");
    #    }

    # if on last step, copy model to $opt{'output_model'}
    if snum == len(fit_stages) - 1:
        # &do_cmd_batch("FNL$$-$snum_txt", "SYM$$-$snum_txt",
        #              'cp', '-i', $stage_model, $opt{'output_model'});
        do_cmd('cp -f %s %s' % (stage_model, opt['output_model'],)) # FIXME added 'f', not interactive.

        # add the history string to the output file
        # &do_cmd_batch("HIS$$-$snum_txt", "FNL$$-$snum_txt",
        #               'minc_modify_header',
        #               '-sappend', ":history='$history'",
        #               $opt{'output_model'});

        # create and output standard deviation file if requested
        if opt['output_stdev'] is not None:
            if opt['symmetric']:
                # &do_cmd_batch("FNL$$-$snum_txt", "SYM$$-$snum_txt",
                #               'volsymm', '-clobber',
                #               "-$opt{'symmetric_dir'}",
                #               '-nofit',
                #               $istdfile, $symxfm, $opt{'output_stdev'});
                assert opt['symmetric_dir'] == 'x' # FIXME handle other cases
                volsymm = VolSymm(
                                x=True,
                                nofit=True,
                                input_file=istdfile,
                                trans_file=symxfm, # FIXME This is an output!
                                output_file=opt['output_stdev'])
                volsymm.run()
            else:
                # &do_cmd_batch("FNL$$-$snum_txt", "SYM$$-$snum_txt",
                #               'cp', '-f', $istdfile, $opt{'output_stdev'});
                do_cmd('cp -f %s %s' % (istdfile, opt['output_stdev'],))

                # # add the history string to the output file
                # &do_cmd_batch("HIS$$-$snum_txt", "FNL$$-$snum_txt",
                #               'minc_modify_header',
                #               '-sappend', ":history='$history'",
                #               $opt{'output_stdev'});
    else:
        pass
        # # spaghetti code ALERT!
        # # resubmit ourselves for the next iteration and then exit
        # if($opt{'batch'}){
        #    &do_cmd_batch("STG$$-$snum_txt", "SYM$$-$snum_txt", @orig_cmd);
        #    exit(0);
        #    }


    cmodel = stage_model
