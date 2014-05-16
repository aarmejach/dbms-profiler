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
$PGBINDIR/postgres -D "$DATADIR" -p $PORT &
PGPID=$!
while ! $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; do
    echo "Waiting for the Postgres server to start"
    sleep 2
done

# Additional sleep time seems necessary
sleep 3

# Warmup: run all queries in succession, always do this, even with zsim
echo "Warmup: run all queries in succession"
for i in $QUERIES;
do
    ii=$(printf "%02d" $i)
    /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
        --output=warmup_q$ii.exectime $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME\
        < $QUERIESDIR/q$ii.analyze.sql 2> warmup_q$ii.stderr > warmup_q$ii.stdout
done

if [ "$SIMULATOR" = true ]; then
    echo "Execute in Zsim: stop postgres server"
    $PGBINDIR/pg_ctl stop -D $DATADIR
    sleep 15
fi

# For each query, run...
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
    else
        if [ "$STAT" = false ]; then
            # Execute each query once
            /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
                --output=exectime.txt perf record -a -g -m 512 --\
                $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f $QUERIESDIR/q$ii.sql\
                2> stderr_callgraph.txt > stdout_callgraph.txt

            # Collect samples
            perf record -a -m 512 -e "r00C0" -s -F 1000 -o ipc-samples.data --\
                $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f $QUERIESDIR/q$ii.sql\
                2> stderr_samples.txt > stdout_samples.txt
        else
            source "$BASEDIR/common/perf-counters-axle.sh"
            for counter in "${array[@]}"; do
                echo "Running query $i for counters $counter."
                # Execute queries using perf stat, repeat 5
                LC_NUMERIC=C perf stat -r 3 -e $counter -p $PGPID -x "," --\
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
