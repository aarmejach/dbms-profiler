#!/bin/bash

# Launch a Zsim simulation into the background if cpu's available
# Expects 1 parameter: $1 -> query number in 02d format, or number of streams
# pwd is the query execution results folder

do_launch_simulation() {
    # Limit number of simulations to number of cores, wait if necessary
    do_wait_available_core

    echo "Launching Zsim simulation for $1, $BENCHMARK, with scale ${SCALE}GB"

    cp $PGSIMCONFIG in.cfg
    sed -i "s#PGBINDIR#$PGBINDIR#g" in.cfg
    sed -i "s#PORT#$PORT#g" in.cfg
    sed -i "s#DATADIR#$DATADIR#g" in.cfg
    cp $PGSIMSCRIPT run-$1.sh
    sed -i "s#QNUM#$1#g" run-$1.sh
    sed -i "s#PGBINDIR#$PGBINDIR#g" run-$1.sh
    sed -i "s#PORT#$PORT#g" run-$1.sh
    sed -i "s#DBNAME#$DB_NAME#g" run-$1.sh
    sed -i "s#QUERIESDIR#$QUERIESDIR#g" run-$1.sh
    sed -i "s#DATADIR#$DATADIR#g" run-$1.sh
    sed -i "s#BASEDIR#$BASEDIR#g" run-$1.sh
    sed -i "s#RUNDIR#$RUNDIR#g" run-$1.sh
    sed -i "s#NUMSTREAMS#$NUMSTREAMS#g" run-$1.sh
    ./run-$1.sh &
}
