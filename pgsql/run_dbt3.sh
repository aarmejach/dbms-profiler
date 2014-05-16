#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

mkdir -p $RESULTS
cd $RESULTS

# Start and Warmup
echo "Start pg server"
$PGBINDIR/postgres -D "$DATADIR" -p $PORT &
PGPID=$!
while ! $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; do
    echo "Waiting for the Postgres server to start"
    sleep 2
done

# Additional sleep time seems necessary
sleep 3

RUNDIR=$RESULTS/run
mkdir -p $RUNDIR

# Create stream files and warmup
i=1
while [ $i -le $NUMSTREAMS ]
do
    query_file="$RUNDIR/throughput_query$i"
    tmp_query_file="$RUNDIR/tmp_throughput_query$i.sql"
    param_file="$RUNDIR/throughput_param$i"

    # output PID to a tmp file
    echo "$$" > $RUNDIR/PID$i

    if [ ! -f $RUNDIR/$SEED_FILE ]; then
        echo "creating seed file $SEED_FILE, you can change the seed by "
        echo "modifying this file"
        date +%-m%d%H%M%S > $RUNDIR/$SEED_FILE
    fi
    seed=`cat $RUNDIR/$SEED_FILE`
    let "seed = $seed + $i"

    # generate the queries for thoughput test
    rm -f $query_file
    rm -f $tmp_query_file
    cd $DBGENDIR
    DSS_QUERY=queries/$DATABASE ./qgen -c -r $seed -p $i -s $SCALE -l $param_file > $query_file
    cd $RESULTS

    # Ugly hack to remove queries from query_file
    for q in $QUERIESALL; do
        if [[ $QUERIES =~ (^| )$q($| ) ]]; then
            echo "keep query $q"
        else
            echo "strip query $q"
            line=`grep "(Q$q)" $query_file -n | cut -f1 -d:`
            len=`wc -l $DBGENDIR/queries/$DATABASE/$q.sql | cut -f1 -d" "`
            let "lineend=$line+$len-1"
            sed -i "${line},${lineend}d" $query_file
        fi
    done
    #line=`grep "(Q1)" $query_file -n | cut -f1 -d:`
    #let "lineend=$line+26"
    #sed -i "${line},${lineend}d" $query_file

    # modify $query_file so that the commands are in one line
    #${PARSE_QUERY} $query_file $tmp_query_file T $perf_run_num $stream_num

    # get the execution plan for each query
    #PLANDIR=$OUTPUT_DIR/db/plans
    #mkdir -p $PLANDIR
    #i=1
    #while [ $i -le 22 ]
    #do
            #if [ $i -ne 15 ]; then
                    #${DBSCRIPTDIR}/get_query_plan.sh ${scale_factor} ${i} \
                                    #${PLANDIR}/throughput_stream${stream_num}_query${i}.txt \
                                    #${RUNDIR} ${SEED_FILE} ${DBPORT}
            #fi
            #let "i=$i+1"
    #done

    # Warmup run each stream once
    echo "Warmup using stream $i"
    /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
        --output=warmup$i.exectime $PGBINDIR/psql -h /tmp\
        -p $PORT -d $DB_NAME -f $query_file  2> warmup$i.stderr > warmup$i.stdout &

    let "i=$i+1"
done

# Wait for all pending streams to finish.
echo "Wait for all pending streams to finish"
for p in $(jobs -p); do
  if [ $p != $PGPID ]; then
      wait $p
  fi
done
echo "Warmup done and stream creation done."

if [ "$SIMULATOR" = true ]; then
    echo "Execute in Zsim: stop postgres server"
    $PGBINDIR/pg_ctl stop -D $DATADIR
    sleep 15
fi

sleep 3

if [ "$SIMULATOR" = true ]; then
        cp $PGSIMCONFIG in.cfg
        sed -i "s#PGBINDIR#$PGBINDIR#g" in.cfg
        sed -i "s#PORT#$PORT#g" in.cfg
        sed -i "s#DATADIR#$DATADIR#g" in.cfg
        cp $PGSIMSCRIPT run.sh
        sed -i "s/%NUMSTREAMS%/$NUMSTREAMS/g" run.sh
        source ./run.sh
else
    # Run the streams for each counter

    if [ "$STAT" = false ]; then
        # Unsing perf record, no callgraph, just sampling.
        i=1
        while [ $i -le $NUMSTREAMS ]; do
            # run the queries
            echo "`date`: start throughput queries for stream $i for counter $counter"

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
        for p in $(jobs -p); do
          if [ $p != $PGPID ]; then
              wait $p
          fi
        done
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
                # You can't use -a and have the query redirected to a file with -o, so use -a and redirect.
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
            for p in $(jobs -p); do
              if [ $p != $PGPID ]; then
                  wait $p
              fi
            done

            e_time=`$GTIME`
            echo "`date`: end queries for counter $counter"
            printf 'Elapsed time: %s\n' $(timer $t)

            sleep 2

        done
    fi
fi

if [ "$SIMULATOR" = false ]; then
    $PGBINDIR/pg_ctl stop -D $DATADIR
fi
