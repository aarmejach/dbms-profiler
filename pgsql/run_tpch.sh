#!/bin/bash -e

# Common function definitions
source "$BASEDIR/$DATABASE/common.sh"

# Include tpch warmup code
source "$BASEDIR/$DATABASE/do_warmup_tpch.sh"

# Include simulation execution code
source "$BASEDIR/$DATABASE/do_launch_simulation.sh"

# Install teardown function defined in common
# Reset cpu governor and kill lingering jobs
test -z "${DEBUG-}" && trap "teardown" EXIT

# Check if pgsql port is free
do_check_port

# Check if pgsql already running in datadir
do_check_datadir

# Current time
t=$(timer)

mkdir -p $RESULTS
cd $RESULTS

# Start Postgres server
#do_start_postgres

# Additional sleep time seems necessary
sleep 3

# Warmup: run all queries in succession, always do this, even with zsim
#do_warmup_tpch

if [ "$SIMULATOR" = true ]; then
    echo "Execute in Zsim: stop postgres server"
    do_stop_postgres
fi

# For each query, run...
for i in $QUERIES;
do
    echo "Running query: $i"
    ii=$(printf "%02d" $i)
    dir="q${ii}"
    mkdir -p $dir
    cd "$dir"

    do_start_postgres

    if [ "$SIMULATOR" = true ]; then
        do_launch_simulation $ii
    else
        # Callgraph run
        /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
            --output=q$ii.exectime perf record -a -g -m 512 -- $PGBINDIR/psql -h /tmp\
            -p $PORT -d $DB_NAME < $QUERIESDIR/q$ii.sql 2> q$ii.stderr > q$ii.stdout

        source "$BASEDIR/common/perf-counters-pmfs.sh"
        for counter in "${array[@]}"; do
            do_stop_postgres
            sudo dropcaches.sh
            do_start_postgres

            echo "Running query $i for counters $counter."
            # Execute queries using perf stat, repeat 3
            LC_NUMERIC=C perf stat -r 1 -e $counter -p $PGPID -x "," --\
                $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f $QUERIESDIR/q$ii.sql\
                2>> perf-stats.csv > stdout_$counter.txt
        done

        #if [ "$STAT" = false ]; then
            # Execute each query once for callgraph
            #perf record -a -g -m 512 --\
                #$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f $QUERIESDIR/q$ii.sql\
                #2> stderr_callgraph.txt > stdout_callgraph.txt

            # Collect samples for ipc
            #perf record -a -m 512 -e "r00C0" -s -F 1000 -o ipc-samples.data --\
                #$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f $QUERIESDIR/q$ii.sql\
                #2> stderr_samples.txt > stdout_samples.txt

            # Parse samples
            #perf script -D -i ipc-samples.data | python $BASEDIR/common/parse-ipc-samples-perf.py\
                #> ipc-samples-perf.csv
        #else
            #source "$BASEDIR/common/perf-counters-axle.sh"
            #for counter in "${array[@]}"; do
                #echo "Running query $i for counters $counter."
                # Execute queries using perf stat, repeat 3
                #LC_NUMERIC=C perf stat -r 1 -e $counter -p $PGPID -x "," --\
                    #$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f $QUERIESDIR/q$ii.sql\
                    #2>> perf-stats.csv > stdout_$counter.txt
            #done
        #fi
    fi

    do_stop_postgres
    sudo dropcaches.sh

    cd ..
done

# Generate callgraphs
if [ "$SIMULATOR" = false ]; then
    #do_stop_postgres
    if [ "$STAT" = false ]; then
        source "$BASEDIR/common/callgraph.sh"
    fi
else
    # Wait for zsim simulations to finish
    do_wait_zsim
    #rm -r ${DATADIR}-*
fi
