#!/usr/bin/python

import sys, os, getopt
from subprocess import Popen, PIPE

SIMTYPES="base footprint tidy".split()

#ALL_APPS = "tpch dbt2 dbt3".split()
ALL_APPS = "dbt3".split()
inputs = {
'tpch' : "2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22".split(),
#'dbt3' : "1 2 4 8".split(),
'dbt3' : "1 8".split(),
'dbt2' : "16".split()
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
  pg_ctl stop -m fast -D "$DATADIR" 2>/dev/null && sleep 2
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
export PGPATH=$NAS_HOME/postgres
export BOOST=$NAS_HOME/boost
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$BOOST/stage/lib:$NAS_HOME/icu/source/lib
export PATH=$PGPATH/build/bin:$PATH
export PGHOST=localhost
export DBT2BIN=/scratch/nas/1/adria/dbt2/bin

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
    DBDIR=pgdata40WH-dbt2
    DBNAME=dbt2

    rm -r $LOCALHOME/$DBDIR
    mkdir -p $LOCALHOME/$DBDIR
    rsync -aP --delete $NAS_HOME/$DBDIR/* $LOCALHOME/$DBDIR

    DATADIR=$LOCALHOME/$DBDIR
    chmod 700 $DATADIR
else
    DBDIR=pgdata%(SCALE)sGB-tpch
    DBNAME=tpch

    rm -r $LOCALHOME/$DBDIR
    mkdir -p $LOCALHOME/$DBDIR
    rsync -aP --max-size=25m --delete $NAS_HOME/$DBDIR/* $LOCALHOME/$DBDIR
    cp -asu $NAS_HOME/$DBDIR/* $LOCALHOME/$DBDIR 2> /dev/null

    DATADIR=$LOCALHOME/$DBDIR
    chmod 700 $DATADIR
fi

### Install teardown function
trap teardown EXIT INT TERM

### Config for zsim
PORT=5443
let "NEWPORT=$PORT+%(INPUT)s"
cp $ZSIMPATH/tests/sandy-postgres-%(SIMTYPE)s.cfg in.cfg
sed -i "s#PORT#$NEWPORT#g" in.cfg
sed -i "s#DATADIR#$DATADIR#g" in.cfg

### Execute Zsim
$ZSIMPATH/build/opt/zsim in.cfg &> simterm.txt &
ZSIMPID=$!

# Wait for the potgres server to start
sleep 2
while ! cat simterm.txt | grep -q "ready to accept connections" ; do
    if grep --quiet exiting simterm.txt; then
        exit 1
    fi
    if grep --quiet FATAL simterm.txt; then
        exit 1
    fi
    sleep 5
done
sleep 5

# Run queries
if [ "%(APP)s" == "tpch" ]; then

    ii=$(printf "%(pf)s" %(INPUT)s)
    psql -h localhost -p $NEWPORT -d $DBNAME -U aarmejac -f $QUERIESDIR/q$ii.sql 2> psqlterm.stderr > psqlterm.stdout &

elif [ "%(APP)s" == "dbt3" ]; then

    i=1
    while [ $i -le %(INPUT)s ]; do
        psql -h localhost -p $NEWPORT -d $DBNAME -U aarmejac -f $QUERIESDIR/throughput_query$i\
	    2> psqlterm_stream$i.stderr > psqlterm_stream$i.stdout &
        let "i=$i+1"
    done

else
    sleep 10
    VPORT=`grep "Virtualized bind" zsim.log.0| cut -f 8 -d " "`
    PGPID=`grep "Started process" zsim.log.0 | cut -d " " -f 6`
    $DBT2BIN/dbt2-run-workload -a pgsql -d 12000 -w 40 -c 16 -l $VPORT -o results -N -n -i $PGPID 2> dbt2_output.stderr > dbt2_output.stdout &
    DBT2PID=$!
fi

# Wait for all pending streams to finish.
for p in $(jobs -p); do
  if [ $p != $ZSIMPID ]; then
      wait $p
  fi
done

# Stop server
sleep 60
pg_ctl stop -m immediate -D ${DATADIR}
sleep 60

if [ "%(APP)s" == "dbt2" ]; then
    kill $DBT2PID
fi

# Sleep some more to allow sim to cleanup and move results
sleep 30
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
