#!/bin/bash -e

# Common function definitions
source "$BASEDIR/$DATABASE/common.sh"

# Include tpch warmup code
source "$BASEDIR/$DATABASE/do_warmup_tpch.sh"

# Include stream creation code
source "$BASEDIR/$DATABASE/do_streams_dbt3.sh"

# Include simulation execution code
source "$BASEDIR/$DATABASE/do_launch_simulation.sh"

# Install teardown function defined in common
# Reset cpu governor and kill lingering jobs
test -z "${DEBUG-}" && trap "teardown" EXIT

# Check if pgsql port is free
do_check_port

# Check if pgsql already running in datadir
do_check_datadir

mkdir -p $RESULTS
cd $RESULTS

# Start Postgres server
do_start_postgres

# Additional sleep time seems necessary
sleep 3

# Warmup: run all queries in succession, always do this, even with zsim
do_warmup_tpch

if [ "$SIMULATOR" = true ]; then
    echo "Execute in Zsim: stop postgres server"
    do_stop_postgres
fi

for NUMSTREAMS in ${STREAMS}; do

    RESULTS=${RESULTS}/${NUMSTREAMS}streams
    mkdir -p $RESULTS
    cd $RESULTS
    RUNDIR=$RESULTS/run
    mkdir -p $RUNDIR

    # Create stream files
    do_stream_creation $NUMSTREAMS

    if [ "$SIMULATOR" = true ]; then
        do_launch_simulation $NUMSTREAMS
    else
        # Run the streams for each counter

        if [ "$STAT" = false ]; then
            # Unsing perf record, no callgraph, just sampling.
            i=1
            while [ $i -le $NUMSTREAMS ]; do

                query_file="$RUNDIR/throughput_query$i"
                #if [ $i -eq $NUMSTREAMS ]; then
                if [ $i -eq 1 ]; then
                    echo "Launch stream $i, attaching perf to postgres server"
                    # First stream, attach perf to postgres pid to collect samples
                    perf record -a -m 512 -e "r00C0" -s -F 1000 -o ipc-samples.data --\
                        $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f ${query_file}\
                        2> stderr_record_stream${i}.txt > stdout_record_stream${i}.txt &
                else
                    echo "Launch stream $i, no perf"
                    $PGBINDIR/psql -h /tmp -p ${PORT} -d ${DB_NAME} -f ${query_file}\
                        2> stderr_record_stream${i}.txt > stdout_record_stream${i}.txt &
                fi

                let "i=$i+1"
            done

            # Wait for all streams to finish.
            do_wait

            sleep 5

            # Parse samples: Not working for multi-process runs
            #perf script -D -i ipc-samples.data | python $BASEDIR/common/parse-ipc-samples.py\
                #> ipc-samples-perf.csv
        else
            # Using perf stat
            source "$BASEDIR/common/perf-counters-axle.sh"
            for counter in "${array[@]}"; do

                i=1
                while [ $i -le $NUMSTREAMS ]; do
                    # run the queries
                    echo "`date`: start throughput queries for stream $i for counter $counter"
                    t=$(timer)

                    query_file="$RUNDIR/throughput_query$i"
                    #if [ $i -eq $NUMSTREAMS ]; then
                    if [ $i -eq 1 ]; then
                        echo "Launch stream $i, attaching perf to postgres server"
                        # Last stream, attach perf to postgres pid
                        LC_NUMERIC=C perf stat -e $counter -p $PGPID -x "," --\
                            $PGBINDIR/psql -h /tmp -p ${PORT} -d ${DB_NAME} -f ${query_file}\
                            2>> perf-stats.csv > stdout_stat_stream${i}_$counter.txt &
                    else
                        echo "Launch stream $i, no perf"
                        $PGBINDIR/psql -h /tmp -p ${PORT} -d ${DB_NAME} -f ${query_file}\
                            2> stderr_stat_stream${i}_$counter.txt > stdout_stat_stream${i}_$counter.txt &
                    fi

                    let "i=$i+1"
                done

                # Wait for all streams to finish.
                do_wait

                e_time=`$GTIME`
                echo "`date`: end queries for counter $counter"
                printf 'Elapsed time: %s\n' $(timer $t)

                sleep 2

            done
        fi
    fi
done

if [ "$SIMULATOR" = false ]; then
    do_stop_postgres
else
    # Wait for zsim simulations
    do_wait_zsim
    rm -r ${DATADIR}-*
fi
