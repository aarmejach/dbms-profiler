#!/usr/bin/python

import sys, os, getopt
from subprocess import Popen, PIPE

SIMTYPES="base alloy unison tpc footprint tidy".split()

#ALL_APPS = "tpch dbt2 dbt3".split()
ALL_APPS = "dbt3".split()
inputs = {
'tpch' : "2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22".split(),
#'dbt3' : "1 2 4 8".split(),
'dbt3' : "4".split(),
'dbt2' : "16 32 64".split()
}

# Specify only 1 scale
SCALE = 10

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
#$ -N zsim_%(SIMTYPE)s_%(APP)s_%(INPUT)s
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

teardown() {
  #pg_ctl stop -m fast -D "$DATADIR" 2>/dev/null && sleep 2
  kill -9 $ZSIMPID
  JOBS=$(jobs -p)
  test -z "$JOBS" || { kill $JOBS && sleep 3; }
  JOBS=$(jobs -p)
  test -z "$JOBS" || kill -9 $JOBS
  rm -r $DATADIR
}

export NAS_HOME=/scratch/nas/1/adria
export PINPATH=$NAS_HOME/zsim/pin_kit
export NVMAINPATH=$NAS_HOME/zsim/nvmain
export ZSIMPATH=$NAS_HOME/zsim
export MDBPATH=$NAS_HOME/monetdb
export BOOST=$NAS_HOME/boost
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$BOOST/stage/lib:$NAS_HOME/icu/source/lib:$MDBPATH/lib
export PATH=$MDBPATH/bin:$PATH
export DOTMONETDB=$NAS_HOME/.monetdb

TESTHOME=$NAS_HOME/%(PREFIX)s
LOCALHOME=/users/scratch/adria
RES=$NAS_HOME/results-zsim/%(PREFIX)s
mkdir -p $RES

TESTCONFIG=%(APP)s_%(INPUT)s_%(SCALE)s
mkdir -p $TESTHOME/$TESTCONFIG
cd $TESTHOME/$TESTCONFIG

ulimit -c 0

### Queries dir
QUERIESDIR=$NAS_HOME/queries/pgsql/

### Get data dir
if [ "%(APP)s" == "dbt2" ]; then
    DBDIR=pgdata100WH-dbt2
    DBNAME=dbt2
else
    DBDIR=mdbdata%(SCALE)sGB-tpch
    DBNAME=tpch

    rm -r $LOCALHOME/$DBDIR
    mkdir -p $LOCALHOME/$DBDIR
    rsync -aP --delete $NAS_HOME/$DBDIR/* $LOCALHOME/$DBDIR
    #rsync -aP --max-size=25m --delete $NAS_HOME/$DBDIR/* $LOCALHOME/$DBDIR
    #cp -asu $NAS_HOME/$DBDIR/* $LOCALHOME/$DBDIR 2> /dev/null

    DATADIR=$LOCALHOME/$DBDIR
    chmod 700 $DATADIR
fi

### Install teardown function
trap teardown EXIT INT TERM

### Config for zsim
PORT=5443
let "NEWPORT=$PORT+%(INPUT)s"
cp $ZSIMPATH/tests/sandy-monetdb-%(SIMTYPE)s.cfg in.cfg
sed -i "s#PORT#$NEWPORT#g" in.cfg
sed -i "s#DATADIR#$DATADIR/$DBNAME#g" in.cfg
cp $DOTMONETDB $HOME

### Execute Zsim
$ZSIMPATH/build/opt/zsim in.cfg &> simterm.txt &
ZSIMPID=$!

# Wait for the monetdb server to start
sleep 500

# Get virt port
VPORT=`grep "Virtualized bind" zsim.log.0| cut -f 8 -d " "`
echo $VPORT

# Run queries
if [ "%(APP)s" == "tpch" ]; then

    ii=$(printf "%(pf)s" %(INPUT)s)
    psql -h localhost -p $NEWPORT -d $DBNAME -U aarmejach -f $QUERIESDIR/q$ii.sql 2> psqlterm.stderr > psqlterm.stdout &

elif [ "%(APP)s" == "dbt3" ]; then

    i=1
    while [ $i -le %(INPUT)s ]; do
        mclient -d mapi:monetdb://127.0.0.1:$VPORT/tpch $QUERIESDIR/throughput_query$i\
	    2> mdbterm_stream$i.stderr > mdbterm_stream$i.stdout &
        let "i=$i+1"
        sleep 100
    done

else
    #TODO dbt2
    : #nop
fi

# Wait for all pending streams to finish.
for p in $(jobs -p); do
  echo $p
  if [ $p != $ZSIMPID ]; then
      wait $p
  fi
done

# Stop server
sleep 20
kill -9 $ZSIMPID

# Sleep some more to allow sim to cleanup and move results
sleep 10
for file in *; do
    mv $file "$RES/${TESTCONFIG}_$file"
done

exit 0
"""

import tempfile, shutil

tmpdir_huge = tempfile.mkdtemp()

root = "/scratch/nas/1/adria"
os.system("ssh adria@arvei.ac.upc.edu 'mkdir -p \"%(dir_prefix)s\"'" % {
	    "dir_prefix": root + "/" + dir_prefix})

for APP in APPS:
    for INPUT in inputs[APP]:
	print APP + " " + INPUT
        scriptname = os.path.join(tmpdir_huge, "%s_%s_%s_%s.sh" % (dir_prefix, APP, INPUT, SCALE))
        scriptfile = file(scriptname, "w")
        script = script_template % { "PREFIX": dir_prefix, "APP" : APP, "INPUT" : INPUT, "pf" : "%02d", "SCALE" : SCALE, "SIMTYPE" : SIMTYPE }
        scriptfile.write(script)
        scriptfile.close()

os.system("rsync -aP %s adria@arvei.ac.upc.edu:" % tmpdir_huge)

# qsub             # submit to "all.q" queue, max 3 hours
# qsub -l medium   # submit to "medium.q" queue, max 8 hours
# qsub -l big      # submit to "big.q" queue, max 48 hours
# qsub -l huge node2012=1 exclusive_job=1      # submit to "big.q" queue, max 48 hours
os.system("ssh adria@arvei.ac.upc.edu \"ls %s | xargs -I\\{} qsub -l huge,node2014=1,no_concurrent_adria=1 %s/\\{} \"" % (os.path.basename(tmpdir_huge),os.path.basename(tmpdir_huge)))

os.system("ssh adria@arvei.ac.upc.edu rm -r %s" % os.path.basename(tmpdir_huge))

shutil.rmtree(tmpdir_huge)
