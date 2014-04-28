#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

mkdir -p $RESULTS
cd $RESULTS

# Start and Warmup
echo "Start and Warmup: run all queries in succession"
if [ "$SIMULATOR" = false ]; then
    $PGBINDIR/postgres -D "$DATADIR" -p $PORT &
    PGPID=$!
    while ! $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; do
        echo "Waiting for the Postgres server to start"
        sleep 2
    done

    # Additional sleep time seems necessary
    sleep 3

    # Warmup: run all queries in succession
    echo "Warmup: run all queries in succession"
    /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
        --output=warmup.exectime $PGBINDIR/psql -h /tmp\
        -p $PORT -d $DB_NAME < $QUERIESDIR/qall.analyze.sql  2> warmup.stderr > warmup.stdout
fi

#bq='\\"'
#damp='\&\&'
#sq="'"
#simpgstart="$PGBINDIR/pg_ctl -o ${sq}-p ${PORT}${sq} -w start -D $DATADIR"
#simpgquery="$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f"
#simpgstop="$PGBINDIR/pg_ctl -o ${sq}-p ${PORT}${sq} -w stop -D $DATADIR"
#echo $simpgstart
#echo $simpgquery
#echo $simpgstop
for i in $QUERIES;
do
    echo "Running query: $i"
    ii=$(printf "%02d" $i)
    dir="q${ii}"
    mkdir -p $dir
    cd "$dir"

    if [ "$SIMULATOR" = true ]; then
        cp $PGSIMCONFIG in.cfg
        sed -i "s#PGBINDIR#$PGBINDIR#g" in.cfg
        sed -i "s#PORT#$PORT#g" in.cfg
        sed -i "s#DATADIR#$DATADIR#g" in.cfg
        cp $PGSIMSCRIPT run-$ii.sh
        sed -i "s/%QNUM%/$ii/g" run-$ii.sh
        source ./run-$ii.sh
        #pattern='command = "";'
        #cmd="command = \"bash -c ${bq}$PGBINDIR/postgres --single -j -D $DATADIR $DB_NAME < $QUERIESDIR/q$ii.sql${bq}\";"
        #cmd="command = \"bash -c ${bq}$simpgstart $damp $simpgquery $QUERIESDIR/q$ii.sql $damp $simpgstop${bq}\";"
        #echo $cmd
        #sed -i "s#${pattern}#${cmd}#g" in.cfg
        #$ZSIMPATH/build/opt/zsim in.cfg 2> term.stderr > term.stdout
    else
        if [ "$STAT" = false ]; then
            # Execute each query once
            /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
                --output=exectime.txt perf record -p $PGPID -s -g -m 512 --\
                $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f $QUERIESDIR/q$ii.sql\
                2> stderr.txt > stdout.txt
        else
            source "$BASEDIR/common/perf-counters-axle.sh"
            for counter in "${array[@]}"; do
                echo "Running query $i for counters $counter."
                # Execute queries using perf stat, repeat 5
                LC_NUMERIC=C perf stat -r 5 -e $counter -p $PGPID -x "," --\
                    $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f $QUERIESDIR/q$ii.sql\
                    2>> perf-stats.csv > stdout_$counter.txt
            done
        fi
    fi

    cd ..
done

# Generate callgraphs
if [ "$SIMULATOR" = false ]; then
    $PGBINDIR/pg_ctl stop -D $DATADIR
    if [ "$STAT" = false ]; then
        source "$BASEDIR/common/callgraph.sh"
    fi
fi
