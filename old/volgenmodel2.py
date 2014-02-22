from nipype import config
config.enable_debug_mode()

import glob
import os
import os.path
import subprocess
import nipype.pipeline.engine as pe
import nipype.interfaces.io as nio
import nipype.interfaces.utility as utils

from nipypeminc import Volcentre, Norm, Volpad, Voliso, Math, Pik, Blur, Gennlxfm, XfmConcat, BestLinReg, NlpFit, XfmAvg, XfmInvert, Resample, BigAverage, Reshape, VolSymm

def run_command(cmd):
    """
    Run a shell command and return all stdout, throwing an error
    if anything appears on stderr. Only used for commands that are
    expected to be short running, e.g. mincinfo.
    """

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

    xstep = float(run_command(xcmd).split()[0])
    ystep = float(run_command(ycmd).split()[0])
    zstep = float(run_command(zcmd).split()[0])

    return (xstep, ystep, zstep)

# Hard coded things, should be parameters:
FAST_EXAMPLE_BASE_DIR = '/scratch/fast-example'
NORM_CUTOFF = 0.1
NORM_THRESHOLD_PERC = 0.1
NORM_THRESHOLD_BLUR = 7.5
NORMALISE = True
PAD_DISTANCE = 5
PAD_SMOOTH_DISTANCE = 1

ISOTROPIC_RESAMPLING = True
CHECK_FILE = True

FIT_STAGES = ['lin', 1, 3]

MODEL_MIN_STEP = 0.5
MODEL_NORM_THRESH = 0.1

LINMETHOD = 'bestlinreg'

SYMMETRIC = True
SYMMETRIC_DIR = 'x'

CHECKFILE = True

# fit.10-genmodel.conf:
#
# ICBM nlin conf
CONF = [ {'step': 32, 'blur_fwhm': 16, 'iterations': 20},
         {'step': 16, 'blur_fwhm': 8,  'iterations': 20},
         {'step': 12, 'blur_fwhm': 6,  'iterations': 20},
         {'step': 8,  'blur_fwhm': 4,  'iterations': 20},
         {'step': 6,  'blur_fwhm': 3,  'iterations': 20},
         {'step': 4,  'blur_fwhm': 2,  'iterations': 10},
         {'step': 2,  'blur_fwhm': 1,  'iterations': 10}, ]

# Top level workflow.
workflow = pe.Workflow(name="workflow")
workflow.base_dir = os.path.abspath(FAST_EXAMPLE_BASE_DIR)

infiles = glob.glob(os.path.join(FAST_EXAMPLE_BASE_DIR, 'sml*pre.mnc'))

datasource = []
for (i, f) in enumerate(infiles):
    d = pe.Node(interface=nio.DataGrabber(sort_filelist=True), name='datasource_%s' % i)
    d.inputs.base_directory = os.path.abspath(FAST_EXAMPLE_BASE_DIR)
    d.inputs.template = f

    datasource.append(d)

n_volcentre = []
n_normalise = []
n_pad       = []
n_iso       = []

for (f, fname) in enumerate(infiles): # for($f=0; $f<=$#files; $f++){
    # $resfiles[$f] = "$predir/$files[$f].res.mnc";
    # $fitfiles[$f] = "$predir/$files[$f].fit.mnc";
    # $nrmfile = "$predir/$files[$f].nrm.mnc";
    # $isofile = "$predir/$files[$f].iso.mnc";
    # $chkfile = "$predir/$files[$f].fit.jpg";

    # centre the volume so that a PAT xfm has a greater chance

    v = pe.Node(interface=Volcentre(input_file=fname, zero_dircos=True, verbose=True),
                name='CEN_%d' % f) # ==> $resfiles[$f]

    n_volcentre.append(v)

    if NORMALISE:
        (step_x, step_y, step_z) = get_step_sizes(fname)

        n = pe.Node(interface=Norm(cutoff=MODEL_NORM_THRESH,
                                   threshold=True,
                                   threshold_perc=MODEL_NORM_THRESH,
                                   threshold_blur=abs(step_x + step_y + step_z)),
                    name='NRM_%d_CEN_%d' % (f, f,)) # ==> $nrmfile
    else:
        n = pe.Node(interface=utils.IdentityInterface(fields=['input_file']),
                    name='NMV_%d' % f)

    n_normalise.append(n)

    workflow.connect(n_volcentre[f], 'output_file', n_normalise[f], 'input_file')

    if PAD_DISTANCE > 0:
        p = pe.Node(interface=Volpad(distance=PAD_DISTANCE,
                                     smooth=True,
                                     smooth_distance=PAD_DISTANCE/3),
                    name='PAD_%d' % f) # ==> fitfiles[$f]
    else:
        p = pe.Node(interface=utils.IdentityInterface(fields=['input_file']),
                    name='PAD_%d_NMV_%f' % (f, f,))

    n_pad.append(p)
    workflow.connect(n_normalise[f], 'output_file', n_pad[f], 'input_file')

    if ISOTROPIC_RESAMPLING:
        iso_tmp = pe.Node(interface=Voliso(avgstep=True),
                          name='ISO_%d' % f) # ==> isofile[$f]
    else:
        iso_tmp = pe.Node(interface=utils.IdentityInterface(fields=['input_file']),
                          name='IMV_%d_PAD_%d' % (f, f,))

    n_iso.append(iso_tmp)
    workflow.connect(n_pad[f], 'output_file', n_iso[f], 'input_file')

    if CHECKFILE:
        minc_pik_tmp = pe.Node(interface=Pik(triplanar=True, sagittal_offset=10),
                               name='cPAD_%d' % f)
        workflow.connect(n_pad[f], 'output_file', minc_pik_tmp, 'input_file')

# create the initial model from the "first" file
(step_x, step_y, step_z) = get_step_sizes(infiles[0])

blur_init_model = pe.Node(interface=Blur(fwhm3d=(abs(step_x * 4), abs(step_y * 4), abs(step_z * 4))),
                          name='BLR-init-model')
workflow.connect(n_pad[0], 'output_file', blur_init_model, 'input_file') # ==> "$opt{'workdir'}/00-init-model");

# create an apropriate identity transformation
identity_trans = pe.Node(interface=Gennlxfm(step=CONF[0]['step']),
                         name='IDT_BLR-init-model') # ==> $initxfm
workflow.connect(blur_init_model, 'output_file', identity_trans, 'like')





# Determine the last linear stage.
lastlin = FIT_STAGES[::-1].index('lin') - len(FIT_STAGES) + 1

# Generate the config files for each stage.
for snum in range(0, len(FIT_STAGES)):
    end_stage = FIT_STAGES[snum]

    print 'Generating config file for stage %02d' % snum

    if end_stage == 'lin':
       print "---Linear fit---"
    else:
        print "---Non Linear fit---"

        # FIXME should make this a Function interface so that it's explicit in the workflow graph?
        conf_fname = os.path.join(FAST_EXAMPLE_BASE_DIR, 'fit-stage-%02d.conf' % snum)  #   "$cworkdir/fit.conf";
        print 'Creating', conf_fname

        with open(conf_fname, 'w') as f:
            f.write( ("# {conf_fname} -- created by {me}\n#\n"
                      "# End stage: {end_stage}\n"
                      "# Stage Num: {snum_txt}\n\n").format(conf_fname=conf_fname,
                                                            me='FIXME',
                                                            end_stage=end_stage,
                                                            snum_txt='%02d' % snum))

            f.write("@conf = (\n")
            for s in range(0, end_stage + 1):
               f.write("   {'step' => " + str(CONF[s]['step']))
               f.write(", 'blur_fwhm' => " + str(CONF[s]['blur_fwhm']))
               f.write(", 'iterations' => " + str(CONF[s]['iterations']))
               f.write("},\n")
            f.write("   );\n")


    # FIXME save the file name?


# Foreach end stage in the fitting profile
for snum in range(len(FIT_STAGES)): 
   my($snum_txt, $end_stage, $f, $cworkdir,
      $conf_fname, @modxfm, @rsmpl);
   my($step_x, $step_y, $step_z);


   $end_stage = $fit_stages[$snum];
   $snum_txt = sprintf("%02d", $snum);
   print STDOUT "  + [Stage: $snum_txt] End stage: $end_stage\n";

   # make subdir in working dir for files
   $cworkdir = "$opt{'workdir'}/$snum_txt";
   &do_cmd('mkdir', $cworkdir) if !-e $cworkdir;

   # set up model and xfm names
   my($avgxfm, $symxfm, $iavgfile, $istdfile, $stage_model,
      $iavgfilechk, $istdfilechk, $stage_modelchk);
   $avgxfm = "$cworkdir/avgxfm.xfm";
   $iavgfile = "$cworkdir/model.iavg.mnc";
   $istdfile = "$cworkdir/model.istd.mnc";
   $stage_model = "$cworkdir/model.avg.mnc";
   $iavgfilechk = "$cworkdir/model.iavg.jpg";
   $istdfilechk = "$cworkdir/model.istd.jpg";
   $stage_modelchk = "$cworkdir/model.avg.jpg";

   # if this stages model exists, skip to the next stage
   if(&mcomplete($stage_model)){
      printf STDOUT "   | $stage_model - exists, skipping\n";
      $cmodel = $stage_model;
      next;
      }

   # create the ISO model
   my($isomodel_base, $modelmaxstep);
   $isomodel_base = "$cworkdir/fit-model-iso";

   printf STDOUT "   | $isomodel_base - creating\n";
   $modelmaxstep = $conf[(($end_stage eq 'lin') ? 0 : $end_stage)]{'step'}/4;

   # check that the resulting model won't be too large
   # this seems confusing but it actually makes sense...
   if($modelmaxstep < $opt{'model_min_step'}){
      $modelmaxstep = $opt{'model_min_step'};
      }

   print "   -- Model Max step: $modelmaxstep\n";
   &do_cmd_batch("NRM$$-$snum_txt-model", "BLR$$-init-model",
                 'mincnorm', '-clobber',
                 '-cutoff', $opt{'model_norm_thresh'},
                 '-threshold',
                 '-threshold_perc', $opt{'model_norm_thresh'},
                 '-threshold_blur', 3,
                 '-threshold_mask', "$isomodel_base.msk.mnc",
                 $cmodel, "$isomodel_base.nrm.mnc");
   &do_cmd_batch("ISO$$-$snum_txt-model", "NRM$$-$snum_txt-model",
                 'voliso', '-clobber',
                 '-maxstep', $modelmaxstep,
                 "$isomodel_base.nrm.mnc","$isomodel_base.mnc");
   &do_cmd_batch("cISO$$-$snum_txt-model", "ISO$$-$snum_txt-model",
                 'mincpik', '-clobber',
                 '-triplanar', '-horizontal',
                 '-scale', 4, '-tilesize', 400,
                 '-sagittal_offset', 10,
                 "$isomodel_base.mnc", "$isomodel_base.jpg") if $opt{'check'};

   # create the isomodel fit mask
   #chomp($step_x = `mincinfo -attvalue xspace:step $isomodel_base.msk.mnc`);
   $step_x = 1;
   &do_cmd_batch("ISB$$-$snum_txt-model", "NRM$$-$snum_txt-model",
                 'mincblur', '-clobber',
                 '-fwhm', ($step_x * 15),
                 "$isomodel_base.msk.mnc", "$isomodel_base.msk");
   &do_cmd_batch("ISM$$-$snum_txt-model", "ISB$$-$snum_txt-model",
                 'mincmath', '-clobber',
                 '-gt', '-const', 0.1,
                 "$isomodel_base.msk_blur.mnc", "$isomodel_base.fit-msk.mnc");


   # linear or nonlinear fit
   if($end_stage eq 'lin'){
      print STDOUT "---Linear fit---\n";
      }
   else{
      print STDOUT "---Non Linear fit---\n";

      # create nlin fit config
      if($end_stage ne 'lin'){
         $conf_fname = "$cworkdir/fit.conf";
         print STDOUT "    + Creating $conf_fname +\n";

         open(CONF, ">$conf_fname");
         print CONF "# $conf_fname -- created by $me\n#\n" .
                    "# End stage: $end_stage\n" .
                    "# Stage Num: $snum_txt\n\n";

         print CONF "\@conf = (\n";
         foreach $s (0..$end_stage){
            print CONF "   {'step' => " . $conf[$s]{'step'} .
               ", 'blur_fwhm' => " . $conf[$s]{'blur_fwhm'} .
               ", 'iterations' => " . $conf[$s]{'iterations'} . "},\n";
            }
         print CONF "   );\n";
         close(CONF);
         }
      }

   # register each file in the input series
   for($f=0; $f<=$#files; $f++){
      $modxfm[$f] = "$cworkdir/$files[$f].xfm";

      if(&mcomplete($modxfm[$f])){
         printf STDOUT "---$modxfm[$f] exists, skipping---\n";
         &do_cmd_batch("FIT$$-$snum_txt-$f", "ISO$$-$snum_txt-model",
                       'true');
         }
      else{
         if($end_stage eq 'lin'){
            &do_cmd_batch("FIT$$-$snum_txt-$f", "ISO$$-$snum_txt-model",
                          split(/\ /, $opt{'linmethod'}),
                          '-clobber',
                          "$isomodel_base.mnc", $fitfiles[$f], $modxfm[$f]);
            }
         else{
            # use the last linear xfm as a starting point
            my $initcnctxfm = "$cworkdir/init-$files[$f].xfm";
            &do_cmd_batch("IXF$$-$snum_txt-$f", "ISO$$-$snum_txt-model,IDT$$",
                          'xfmconcat', '-clobber',
                          "$opt{'workdir'}/$lastlin/$files[$f].xfm", $initxfm,
                          $initcnctxfm);

            &do_cmd_batch("FIT$$-$snum_txt-$f", "IXF$$-$snum_txt-$f,ISM$$-$snum_txt-model",
                          'nlpfit', '-clobber',
                          '-init_xfm', $initcnctxfm,
                          '-config', $conf_fname,
                          '-source_mask', "$isomodel_base.fit-msk.mnc",
                          "$isomodel_base.mnc", $fitfiles[$f], $modxfm[$f]);
            }
         }
      }

   # average xfms
   &do_cmd_batch("AXF$$-$snum_txt", "FIT$$-$snum_txt-*",
                 'xfmavg', '-clobber',
                 (($end_stage eq 'lin') ? '-ignore_nonlinear' : '-ignore_linear'),
                 @modxfm, $avgxfm);

   # resample each file in the input series
   for($f=0; $f<=$#files; $f++){
      my($chkfile, $invxfm, $resxfm);

      $invxfm = "$cworkdir/inv-$files[$f].xfm";
      $resxfm = "$cworkdir/rsmpl-$files[$f].xfm";
      $rsmpl[$f] = "$cworkdir/rsmpl-$files[$f].mnc";
      $chkfile = "$cworkdir/rsmpl-$files[$f].jpg";

      if(&mcomplete($rsmpl[$f])){
         printf STDOUT "   | $rsmpl[$f] - exists, skipping\n";
         }
      else{
         printf STDOUT "   | $rsmpl[$f] - resampling\n";

         # invert model xfm
         &do_cmd_batch("XIN$$-$snum_txt-$f", "FIT$$-$snum_txt-$f",
                       'xfminvert', '-clobber', $modxfm[$f], $invxfm);

         # concat
         &do_cmd_batch("XCN$$-$snum_txt-$f", "AXF$$-$snum_txt,XIN$$-$snum_txt-$f",
                       'xfmconcat', '-clobber', $invxfm, $avgxfm, $resxfm);

         # resample
         &do_cmd_batch("RES$$-$snum_txt-$f", "XCN$$-$snum_txt-$f",
                       'mincresample', '-clobber',
                       '-sinc',
                       '-transformation', $resxfm,
                       '-like', "$isomodel_base.mnc",
                       $resfiles[$f], $rsmpl[$f]);
         &do_cmd_batch("cRES$$-$snum_txt-$f", "RES$$-$snum_txt-$f",
                       'mincpik', '-clobber',
                       '-triplanar',
                       '-sagittal_offset', 10,
                       $rsmpl[$f], $chkfile) if $opt{'check'};
         }
      }

   # create model
   &do_cmd_batch("IAV$$-$snum_txt", "RES$$-$snum_txt-*",
                 'mincbigaverage', '-clobber',
                 '-float',
                 '-robust',
                 '-tmpdir', "$opt{'workdir'}/tmp",
                 '-sdfile', $istdfile,
                 @rsmpl, $iavgfile);
   &do_cmd_batch("cIAV$$-$snum_txt", "IAV$$-$snum_txt",
                 'mincpik', '-clobber',
                 '-triplanar', '-horizontal',
                 '-scale', 4, '-tilesize', 400,
                 '-sagittal_offset', 10,
                 $iavgfile, $iavgfilechk) if $opt{'check'};
   &do_cmd_batch("cIAV$$-$snum_txt", "IAV$$-$snum_txt",
                 'mincpik', '-clobber',
                 '-triplanar', '-horizontal',
                 '-scale', 4, '-tilesize', 400,
                 '-lookup', '-hotmetal',
                 '-sagittal_offset', 10,
                 $istdfile, $istdfilechk) if $opt{'check'};

   # do symmetric averaging if required
   if($opt{'symmetric'}){
      my (@fit_args, $symfile);

      $symxfm = "$cworkdir/model.sym.xfm";
      $symfile = "$cworkdir/model.iavg-short.mnc";

      # convert double model to short
      &do_cmd_batch("MTS$$-$snum_txt", "IAV$$-$snum_txt",
                    'mincreshape', '-clobber',
                    '-short',
                    $iavgfile, $symfile);

      # set up fit args
      if($end_stage eq 'lin'){
         @fit_args = ('-linear');
         }
      else{
         @fit_args = ('-nonlinear', '-config_file', $conf_fname);
         }

      &do_cmd_batch("SYM$$-$snum_txt", "MTS$$-$snum_txt",
                    'volsymm', '-clobber',
                    "-$opt{'symmetric_dir'}",
                    @fit_args,
                    $symfile, $symxfm, $stage_model);
      }
   else{
      &do_cmd_batch("SYM$$-$snum_txt", "IAV$$-$snum_txt",
                    'ln', '-s', '-f', &basename($iavgfile), $stage_model);
      }
   &do_cmd_batch("cSYM$$-$snum_txt", "SYM$$-$snum_txt",
                 'mincpik', '-clobber',
                 '-triplanar', '-horizontal',
                 '-scale', 4, '-tilesize', 400,
                 '-sagittal_offset', 10,
                 $stage_model, $stage_modelchk) if $opt{'check'};

   # create clean script for resampled and temp xfm files
   open(CLEAN, ">$cworkdir/clean.sh");
   print CLEAN "#! /bin/sh\n" .
               "#\n" .
               "# clean up for stage $snum_txt\n" .
               "\n" .
               "if [ -e $stage_model ]\n" .
               "then\n" .
               "   echo \"Removing files\"\n   \n" .
               "   rm -f $cworkdir/rsmpl-*.mnc\n" .
               "   rm -f $cworkdir/rsmpl-*.xfm\n" .
               "   rm -f $cworkdir/inv-*.xfm\n" .
               "   rm -f $cworkdir/inv-*.mnc\n" .
               "   rm -f $cworkdir/init-*.xfm\n" .
               "   rm -f $cworkdir/init-*.mnc\n" .
               "   rm -rf $opt{'workdir'}/tmp\n" .
               "fi\n";
   close(CLEAN);
   &do_cmd('chmod', '+x', "$cworkdir/clean.sh");

   # run clean script if required
   if($opt{'clean'}){
      &do_cmd_batch("CLN$$-$snum_txt", "SYM$$-$snum_txt",
                    "$cworkdir/clean.sh");
      }

   # if on last step, copy model to $opt{'output_model'}
   if($snum == $#fit_stages){
      &do_cmd_batch("FNL$$-$snum_txt", "SYM$$-$snum_txt",
                    'cp', '-i', $stage_model, $opt{'output_model'});

      # add the history string to the output file
      &do_cmd_batch("HIS$$-$snum_txt", "FNL$$-$snum_txt",
                    'minc_modify_header',
                    '-sappend', ":history='$history'",
                    $opt{'output_model'});

      # create and output standard deviation file if requested
      if(defined($opt{'output_stdev'})){
         if($opt{'symmetric'}){
            &do_cmd_batch("FNL$$-$snum_txt", "SYM$$-$snum_txt",
               'volsymm', '-clobber',
               "-$opt{'symmetric_dir'}",
               '-nofit',
               $istdfile, $symxfm, $opt{'output_stdev'});
            }
         else{
            &do_cmd_batch("FNL$$-$snum_txt", "SYM$$-$snum_txt",
               'cp', '-f', $istdfile, $opt{'output_stdev'});
            }

         # add the history string to the output file
         &do_cmd_batch("HIS$$-$snum_txt", "FNL$$-$snum_txt",
                    'minc_modify_header',
                    '-sappend', ":history='$history'",
                    $opt{'output_stdev'});
         }
      }
   else{
      # spaghetti code ALERT!
      # resubmit ourselves for the next iteration and then exit
      if($opt{'batch'}){
         &do_cmd_batch("STG$$-$snum_txt", "SYM$$-$snum_txt", @orig_cmd);
         exit(0);
         }
      }

   $cmodel = $stage_model;
} # end stage loop







