#!/usr/bin/python

import sys, os, getopt
from subprocess import Popen, PIPE

ALL_APPS = "spec".split()
inputs = {
'spec' : "400.perlbench 403.gcc 416.gamess 433.milc 435.gromacs 437.leslie3d 445.gobmk 450.soplex 454.calculix 458.sjeng 462.libquantum 465.tonto 471.omnetpp 483.xalancbmk 401.bzip2 410.bwaves 429.mcf 434.zeusmp 436.cactusADM 444.namd 453.povray 456.hmmer 459.GemsFDTD 464.h264ref 470.lbm 473.astar 482.sphinx3".split() # 447.dealII and 481.wrf not working
}

# Specify only 1 scale
SCALE = 100

USAGE = """
Submit executions to cluster.
Optionally saves the results in a specified directory.

Usage:
%(scriptname)s {all | application} [-d, --directory  directory_name]

Arguments:
First argument is either "all", or a name of one application to run (see below for a list of available applications)
-d directory_name\tOptional. If given, copy a current version of the simulator
    to this directory and run all the simulations from there. The results will
    be local to this directory.

Examples:
'%(scriptname)s all' - all applications, all core configurations
'%(scriptname)s tpch' - runs tpch, all input queries
'%(scriptname)s tpch -d ideal' - runs tpch, all input queries, in directory "ideal"

Available applications: %(apps)s
""" % { "scriptname": os.path.basename(sys.argv[0]),
        "apps": " ".join(ALL_APPS)}

if len(sys.argv) < 2:
    print USAGE
    sys.exit(1)

try:
    opts, args = getopt.getopt(sys.argv[2:], "d:", ["directory"])
except getopt.GetoptError, err:
    # print help information and exit:
    print USAGE
    print "ERROR: ", str(err) # will print something like "option -a not recognized"
    sys.exit(1)
if not opts and len(args)>0:
  print USAGE
  sys.exit(1)

dir_prefix = "tests_zsim_baseline"
APPS = ALL_APPS
for o, a in opts:
  if o == "-p":
    if a not in ALL_CORES:
      print USAGE
      sys.exit(1)
    CORES = a.split()
  elif o == "-d":
    dir_prefix = "tests_zsim_" + a
  else:
    print o, a
    assert False, "unhandled option" # ...

if sys.argv[1] in ALL_APPS:
  APPS = [sys.argv[1]]
elif sys.argv[1] != "all":
  print USAGE
  sys.exit(1)

script_template = """#!/bin/sh
### Queue manager options
# Specify a job name
#$ -N zsim_baseline_%(APP)s_%(INPUT)s
# Shell
#$ -S /bin/bash
# What are the conditions for sending an email
# 'b'     Mail is sent at the beginning of the job.
# 'e'     Mail is sent at the end of the job.
# 'a'     Mail is sent when the job is aborted or rescheduled.
# 's'     Mail is sent when the job is suspended.
# 'n'     No mail is sent.
#$ -m as
# send mails to this email address:
#$ -M adria.armejach@bsc.es
# make this a working directory (stores the stderr/stdout files here)
#$ -wd /scratch/nas/1/adria/tmp

IFS='
'

export NAS_HOME=/scratch/nas/1/adria
export PINPATH=$NAS_HOME/zsim/pin_kit
export NVMAINPATH=$NAS_HOME/zsim/nvmain
export ZSIMPATH=$NAS_HOME/zsim
export PGPATH=$NAS_HOME/postgres
export BOOST=$NAS_HOME/boost
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$BOOST/stage/lib:$NAS_HOME/icu/source/lib
export PATH=$PGPATH/build/bin:$PATH
export SPECDIR=$NAS_HOME/SPECCPU2006

TESTHOME=$NAS_HOME/%(PREFIX)s
LOCALHOME=/users/scratch/adria
RES=$NAS_HOME/results-zsim/%(PREFIX)s
mkdir -p $RES

TESTCONFIG=%(APP)s_%(INPUT)s_%(SCALE)s
mkdir -p $TESTHOME/$TESTCONFIG
cd $TESTHOME/$TESTCONFIG

ulimit -c 0

### Config for zsim
if [ "%(APP)s" == "spec" ]; then
    cp $ZSIMPATH/tests/sandy-spec-dram.cfg in.cfg
    sed -i '/%(INPUT)s/s/^\ \ #/\ \ /' in.cfg

    ### Copy spec workload over using symlinks
    ln -s $SPECDIR/build/%(INPUT)s/* .

    ### Execute Zsim
    $ZSIMPATH/build/opt/zsim in.cfg &> simterm.txt

    ### Remove spec symlinks
    find . -type l | xargs rm -r
fi

### Sleep some more to allow sim to cleanup and move results
sleep 10
for file in *; do
    mv $file "$RES/${TESTCONFIG}_$file"
done

exit 0
"""

import tempfile, shutil

tmpdir_big = tempfile.mkdtemp()

root = "/scratch/nas/1/adria"
os.system("ssh adria@gaudi 'mkdir -p \"%(dir_prefix)s\"'" % {
	    "dir_prefix": root + "/" + dir_prefix})

for APP in APPS:
    for INPUT in inputs[APP]:
	print APP + " " + INPUT
        scriptname = os.path.join(tmpdir_big, "%s_%s_%s_%s.sh" % (dir_prefix, APP, INPUT, SCALE))
        scriptfile = file(scriptname, "w")
        script = script_template % { "PREFIX": dir_prefix, "APP" : APP, "INPUT" : INPUT, "pf" : "%02d", "SCALE" : SCALE }
        scriptfile.write(script)
        scriptfile.close()

os.system("rsync -aP %s adria@gaudi:" % tmpdir_big)

# qsub             # submit to "all.q" queue, max 3 hours
# qsub -l medium   # submit to "medium.q" queue, max 8 hours
# qsub -l big      # submit to "big.q" queue, max 48 hours
# qsub -l huge node2012=1 exclusive_job=1      # submit to "big.q" queue, max 48 hours
os.system("ssh adria@gaudi \"ls %s | xargs -I\\{} qsub -l big %s/\\{} \"" % (os.path.basename(tmpdir_big),os.path.basename(tmpdir_big)))

os.system("ssh adria@gaudi rm -r %s" % os.path.basename(tmpdir_big))

shutil.rmtree(tmpdir_big)
