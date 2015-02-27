#!/usr/bin/python

import sys, os, getopt, time
from subprocess import Popen, PIPE

SIMTYPES="base alloy unison".split()

ALL_APPS = "spec spec-r spec-mix".split()
inputs = { # 447.dealII and 481.wrf not working
#'spec' : "400.perlbench 403.gcc 416.gamess 433.milc 435.gromacs 437.leslie3d 445.gobmk 450.soplex 454.calculix 458.sjeng 462.libquantum 465.tonto 471.omnetpp 483.xalancbmk 401.bzip2 410.bwaves 429.mcf 434.zeusmp 436.cactusADM 444.namd 453.povray 456.hmmer 459.GemsFDTD 464.h264ref 470.lbm 473.astar 482.sphinx3".split(),
#'spec-r' : "400.perlbench 403.gcc 416.gamess 433.milc 435.gromacs 437.leslie3d 445.gobmk 450.soplex 454.calculix 458.sjeng 462.libquantum 465.tonto 471.omnetpp 483.xalancbmk 401.bzip2 410.bwaves 429.mcf 434.zeusmp 436.cactusADM 444.namd 453.povray 456.hmmer 459.GemsFDTD 464.h264ref 470.lbm 473.astar 482.sphinx3".split()
'spec' : "403.gcc 433.milc 437.leslie3d 450.soplex 462.libquantum 471.omnetpp 410.bwaves 429.mcf 459.GemsFDTD 470.lbm 473.astar 482.sphinx3".split(),

'spec-r' : "403.gcc 433.milc 437.leslie3d 450.soplex 462.libquantum 471.omnetpp 410.bwaves 429.mcf 459.GemsFDTD 470.lbm 473.astar 482.sphinx3".split(),

'spec-mix' : [('403.gcc', '403.gcc', '403.gcc', '437.leslie3d', '450.soplex', '450.soplex', '459.GemsFDTD', '459.GemsFDTD'), ('433.milc', '437.leslie3d', '437.leslie3d', '429.mcf', '429.mcf', '459.GemsFDTD', '459.GemsFDTD', '459.GemsFDTD'), ('433.milc', '433.milc', '433.milc', '437.leslie3d', '462.libquantum', '462.libquantum', '471.omnetpp', '471.omnetpp'), ('403.gcc', '403.gcc', '403.gcc', '403.gcc', '433.milc', '437.leslie3d', '471.omnetpp', '459.GemsFDTD'), ('433.milc', '450.soplex', '450.soplex', '471.omnetpp', '459.GemsFDTD', '459.GemsFDTD', '459.GemsFDTD', '482.sphinx3'), ('462.libquantum', '462.libquantum', '462.libquantum', '429.mcf', '459.GemsFDTD', '470.lbm', '473.astar', '473.astar'), ('433.milc', '437.leslie3d', '437.leslie3d', '437.leslie3d', '437.leslie3d', '437.leslie3d', '462.libquantum', '459.GemsFDTD'), ('433.milc', '429.mcf', '470.lbm', '470.lbm', '482.sphinx3', '482.sphinx3', '482.sphinx3', '482.sphinx3'), ('403.gcc', '437.leslie3d', '450.soplex', '462.libquantum', '471.omnetpp', '429.mcf', '459.GemsFDTD', '473.astar'), ('437.leslie3d', '437.leslie3d', '437.leslie3d', '462.libquantum', '429.mcf', '429.mcf', '459.GemsFDTD', '473.astar'), ('437.leslie3d', '437.leslie3d', '437.leslie3d', '462.libquantum', '462.libquantum', '462.libquantum', '470.lbm', '473.astar'), ('433.milc', '437.leslie3d', '437.leslie3d', '450.soplex', '462.libquantum', '462.libquantum', '471.omnetpp', '473.astar'), ('433.milc', '450.soplex', '429.mcf', '429.mcf', '429.mcf', '429.mcf', '473.astar', '473.astar'), ('403.gcc', '403.gcc', '437.leslie3d', '462.libquantum', '471.omnetpp', '471.omnetpp', '459.GemsFDTD', '482.sphinx3'), ('403.gcc', '450.soplex', '450.soplex', '471.omnetpp', '470.lbm', '470.lbm', '473.astar', '473.astar'), ('403.gcc', '403.gcc', '450.soplex', '450.soplex', '462.libquantum', '470.lbm', '470.lbm', '470.lbm'), ('403.gcc', '433.milc', '450.soplex', '462.libquantum', '462.libquantum', '429.mcf', '429.mcf', '473.astar'), ('433.milc', '433.milc', '437.leslie3d', '462.libquantum', '462.libquantum', '459.GemsFDTD', '459.GemsFDTD', '470.lbm'), ('403.gcc', '437.leslie3d', '450.soplex', '429.mcf', '473.astar', '473.astar', '482.sphinx3', '482.sphinx3'), ('403.gcc', '437.leslie3d', '429.mcf', '473.astar', '482.sphinx3', '482.sphinx3', '482.sphinx3', '482.sphinx3'), ('403.gcc', '437.leslie3d', '450.soplex', '462.libquantum', '471.omnetpp', '429.mcf', '470.lbm', '470.lbm'), ('433.milc', '437.leslie3d', '473.astar', '473.astar', '473.astar', '473.astar', '473.astar', '473.astar'), ('403.gcc', '403.gcc', '450.soplex', '462.libquantum', '462.libquantum', '462.libquantum', '429.mcf', '470.lbm'), ('403.gcc', '471.omnetpp', '471.omnetpp', '459.GemsFDTD', '459.GemsFDTD', '459.GemsFDTD', '482.sphinx3', '482.sphinx3'), ('450.soplex', '462.libquantum', '429.mcf', '429.mcf', '459.GemsFDTD', '473.astar', '482.sphinx3', '482.sphinx3'), ('403.gcc', '403.gcc', '433.milc', '429.mcf', '470.lbm', '473.astar', '473.astar', '482.sphinx3'), ('403.gcc', '437.leslie3d', '437.leslie3d', '429.mcf', '429.mcf', '459.GemsFDTD', '473.astar', '473.astar'), ('433.milc', '437.leslie3d', '437.leslie3d', '437.leslie3d', '429.mcf', '482.sphinx3', '482.sphinx3', '482.sphinx3'), ('403.gcc', '403.gcc', '403.gcc', '403.gcc', '403.gcc', '429.mcf', '473.astar', '473.astar'), ('433.milc', '437.leslie3d', '437.leslie3d', '437.leslie3d', '471.omnetpp', '429.mcf', '429.mcf', '429.mcf'), ('450.soplex', '450.soplex', '429.mcf', '470.lbm', '470.lbm', '473.astar', '482.sphinx3', '482.sphinx3'), ('403.gcc', '437.leslie3d', '450.soplex', '450.soplex', '462.libquantum', '471.omnetpp', '459.GemsFDTD', '470.lbm'), ('403.gcc', '471.omnetpp', '471.omnetpp', '471.omnetpp', '471.omnetpp', '459.GemsFDTD', '473.astar', '482.sphinx3'), ('403.gcc', '403.gcc', '437.leslie3d', '450.soplex', '471.omnetpp', '471.omnetpp', '429.mcf', '459.GemsFDTD'), ('403.gcc', '433.milc', '450.soplex', '450.soplex', '459.GemsFDTD', '473.astar', '473.astar', '482.sphinx3'), ('403.gcc', '433.milc', '433.milc', '437.leslie3d', '437.leslie3d', '462.libquantum', '471.omnetpp', '429.mcf'), ('403.gcc', '437.leslie3d', '450.soplex', '450.soplex', '429.mcf', '429.mcf', '429.mcf', '473.astar'), ('433.milc', '433.milc', '437.leslie3d', '450.soplex', '450.soplex', '471.omnetpp', '429.mcf', '470.lbm'), ('403.gcc', '433.milc', '433.milc', '433.milc', '450.soplex', '450.soplex', '470.lbm', '473.astar'), ('433.milc', '433.milc', '450.soplex', '450.soplex', '450.soplex', '450.soplex', '471.omnetpp', '482.sphinx3'), ('403.gcc', '403.gcc', '471.omnetpp', '429.mcf', '429.mcf', '470.lbm', '473.astar', '482.sphinx3'), ('403.gcc', '403.gcc', '450.soplex', '450.soplex', '462.libquantum', '462.libquantum', '471.omnetpp', '470.lbm'), ('437.leslie3d', '437.leslie3d', '437.leslie3d', '437.leslie3d', '437.leslie3d', '437.leslie3d', '429.mcf', '473.astar'), ('403.gcc', '433.milc', '471.omnetpp', '429.mcf', '470.lbm', '473.astar', '473.astar', '482.sphinx3'), ('403.gcc', '433.milc', '433.milc', '433.milc', '462.libquantum', '471.omnetpp', '459.GemsFDTD', '470.lbm'), ('403.gcc', '403.gcc', '437.leslie3d', '437.leslie3d', '450.soplex', '459.GemsFDTD', '459.GemsFDTD', '473.astar'), ('403.gcc', '433.milc', '471.omnetpp', '429.mcf', '429.mcf', '459.GemsFDTD', '459.GemsFDTD', '482.sphinx3'), ('433.milc', '462.libquantum', '471.omnetpp', '459.GemsFDTD', '459.GemsFDTD', '482.sphinx3', '482.sphinx3', '482.sphinx3'), ('450.soplex', '450.soplex', '471.omnetpp', '429.mcf', '473.astar', '473.astar', '473.astar', '473.astar'), ('433.milc', '437.leslie3d', '462.libquantum', '462.libquantum', '471.omnetpp', '429.mcf', '470.lbm', '470.lbm'), ('403.gcc', '437.leslie3d', '437.leslie3d', '462.libquantum', '462.libquantum', '459.GemsFDTD', '459.GemsFDTD', '470.lbm'), ('403.gcc', '403.gcc', '450.soplex', '429.mcf', '429.mcf', '459.GemsFDTD', '470.lbm', '482.sphinx3'), ('403.gcc', '462.libquantum', '471.omnetpp', '471.omnetpp', '429.mcf', '429.mcf', '473.astar', '482.sphinx3'), ('437.leslie3d', '437.leslie3d', '450.soplex', '450.soplex', '450.soplex', '459.GemsFDTD', '473.astar', '473.astar'), ('433.milc', '437.leslie3d', '437.leslie3d', '437.leslie3d', '437.leslie3d', '470.lbm', '473.astar', '473.astar'), ('433.milc', '437.leslie3d', '437.leslie3d', '450.soplex', '470.lbm', '470.lbm', '470.lbm', '482.sphinx3'), ('462.libquantum', '462.libquantum', '462.libquantum', '429.mcf', '429.mcf', '429.mcf', '473.astar', '482.sphinx3'), ('433.milc', '459.GemsFDTD', '459.GemsFDTD', '459.GemsFDTD', '459.GemsFDTD', '459.GemsFDTD', '470.lbm', '473.astar'), ('433.milc', '471.omnetpp', '471.omnetpp', '471.omnetpp', '471.omnetpp', '429.mcf', '470.lbm', '473.astar'), ('433.milc', '433.milc', '450.soplex', '450.soplex', '471.omnetpp', '471.omnetpp', '471.omnetpp', '471.omnetpp'), ('433.milc', '433.milc', '433.milc', '462.libquantum', '462.libquantum', '462.libquantum', '429.mcf', '470.lbm'), ('403.gcc', '403.gcc', '450.soplex', '450.soplex', '462.libquantum', '462.libquantum', '429.mcf', '429.mcf'), ('433.milc', '433.milc', '437.leslie3d', '437.leslie3d', '429.mcf', '470.lbm', '470.lbm', '473.astar'), ('403.gcc', '437.leslie3d', '450.soplex', '462.libquantum', '471.omnetpp', '429.mcf', '429.mcf', '470.lbm')]
}

# Specify only 1 scale
SCALE = 100

USAGE = """
Submit executions to cluster.
Optionally saves the results in a specified directory.

Usage:
%(scriptname)s {base | alloy | unison} {all | application} [-d, --directory  directory_name]

Arguments:
First argument is either "all", or a name of one application to run (see below for a list of available applications)
-d directory_name\tOptional. If given, copy a current version of the simulator
    to this directory and run all the simulations from there. The results will
    be local to this directory.

Examples:
'%(scriptname)s base all' - all applications, all core configurations
'%(scriptname)s base tpch' - runs tpch, all input queries
'%(scriptname)s base tpch -d ideal' - runs tpch, all input queries, in directory "ideal"

Available applications: %(apps)s
""" % { "scriptname": os.path.basename(sys.argv[0]),
        "apps": " ".join(ALL_APPS)}

# Regular param check
if len(sys.argv) < 3:
    print USAGE
    sys.exit(1)

try:
    opts, args = getopt.getopt(sys.argv[3:], "d:", ["directory"])
except getopt.GetoptError, err:
    # print help information and exit:
    print USAGE
    print "ERROR: ", str(err) # will print something like "option -a not recognized"
    sys.exit(1)
if not opts and len(args)>0:
  print USAGE
  sys.exit(1)

#Sim type
if sys.argv[1] in SIMTYPES:
    SIMTYPE = sys.argv[1]
else:
    print USAGE
    sys.exit(1)

dir_prefix = "tests_zsim_" + SIMTYPE

APPS = ALL_APPS
for o, a in opts:
  if o == "-d":
    dir_prefix = "tests_zsim_" + a
  else:
    print o, a
    assert False, "unhandled option" # ...

if sys.argv[2] in ALL_APPS:
  APPS = [sys.argv[2]]
elif sys.argv[2] != "all":
  print USAGE
  sys.exit(1)

script_template = """#!/bin/sh
### Queue manager options
# Specify a job name
#$ -N zsim_%(SIMTYPE)s_%(APP)s_%(NUMBER)s
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

TESTCONFIG="%(APP)s_%(WLNAME)s_%(SCALE)s"
mkdir -p $TESTHOME/$TESTCONFIG
cd $TESTHOME/$TESTCONFIG

ulimit -c 0

### Config for zsim
if [ "%(APP)s" == "spec" ]; then
    cp $ZSIMPATH/tests/sandy-spec-%(SIMTYPE)s.cfg in.cfg

    ### Uncomment command lines
    sed -i '/%(INPUT)s/s/^\ \ #/\ \ /' in.cfg

    ### Copy spec workload over using symlinks
    ln -s $SPECDIR/build/%(INPUT)s/* .

elif [ "%(APP)s" == "spec-r" ]; then
    cp $ZSIMPATH/tests/sandy-spec-multi-%(SIMTYPE)s.cfg in.cfg

    ### Uncomment command lines
    sed -i '/%(INPUT)s/s/^\ \ #/\ \ /' in.cfg

    ### Copy spec workload over using symlinks
    ln -s $SPECDIR/build/%(INPUT)s/* .

elif [ "%(APP)s" == "spec-mix" ]; then
    cp $ZSIMPATH/tests/sandy-spec-multi-%(SIMTYPE)s.cfg in.cfg

    i=0
    for WL in %(INPUT)s; do
        ### Uncomment command lines
        sed -i "/$WL$i/s/^\ \ #/\ \ /" in.cfg

        ### Copy spec workload over using symlinks
        ln -sf $SPECDIR/build/$WL/* .

        i=$((i+1))
    done
fi

### Execute Zsim
$ZSIMPATH/build/opt/zsim in.cfg &> simterm.txt

if grep --quiet "gm_create failed" simterm.txt; then
    touch "../%(APP)s_script%(NUMBER)s"
fi

### Remove spec symlinks
find . -type l | xargs rm -r

### Sleep some more to allow sim to cleanup and move results
sleep 10
for file in *; do
    mv $file "$RES/${TESTCONFIG}_$file"
done

exit 0
"""

import tempfile, shutil

tmpdir_huge = tempfile.mkdtemp()

root = "/scratch/nas/1/adria"
#os.system("ssh adria@arvei.ac.upc.edu 'rm -rf \"%(dir_prefix)s\"'" % { "dir_prefix" : root + "/" + dir_prefix })
os.system("ssh adria@arvei.ac.upc.edu 'mkdir -p \"%(dir_prefix)s\"'" % { "dir_prefix" : root + "/" + dir_prefix })

i=0
for APP in APPS:
    for INPUT in inputs[APP]:
        if type(INPUT) is str:
            INPUT = (INPUT,)
	print APP + " " + str(INPUT)
        scriptname = os.path.join(tmpdir_huge, "%s_%s_%s_%s.sh" % (dir_prefix, APP, "script"+str(i), SCALE))
        scriptfile = file(scriptname, "w")
        script = script_template % { "PREFIX": dir_prefix, "APP" : APP, "INPUT" : " ".join(INPUT), "pf" : "%02d", "SCALE" : SCALE, "NUMBER" : i, "WLNAME" : "-".join(INPUT), "SIMTYPE" : SIMTYPE }
        scriptfile.write(script)
        scriptfile.close()
        i=i+1

os.system("rsync -aP %s adria@arvei.ac.upc.edu:" % tmpdir_huge)

# qsub             # submit to "all.q" queue, max 3 hours
# qsub -l medium   # submit to "medium.q" queue, max 8 hours
# qsub -l big      # submit to "big.q" queue, max 48 hours
# qsub -l huge node2012=1 exclusive_job=1      # submit to "big.q" queue, max 48 hours
os.system("ssh adria@arvei.ac.upc.edu \"ls %s | xargs -I\\{} qsub -l huge %s/\\{} \"" % (os.path.basename(tmpdir_huge),os.path.basename(tmpdir_huge)))

# Wait and re-launch dead simulations
home = "/homeA/a/adria"
os.system("ssh adria@arvei.ac.upc.edu 'sleep 60'")
os.system("ssh adria@arvei.ac.upc.edu 'cd %(dir_prefix)s && while ls *script*; do for f in `ls *script*`; do echo $f && qsub -l huge %(TMPDIR)s/*$f* && rm $f; done; sleep 30; done'" % { "dir_prefix" : root + "/" + dir_prefix, "TMPDIR" : home + "/" + os.path.basename(tmpdir_huge) })

os.system("ssh adria@arvei.ac.upc.edu rm -r %s" % os.path.basename(tmpdir_huge))

shutil.rmtree(tmpdir_huge)
