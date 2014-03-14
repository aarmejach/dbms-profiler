#!/bin/bash

# Install teardown() function to kill any lingering jobs
# Check if monetdb is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

mkdir -p $RESULTS
cd $RESULTS

# Initialize monetdb daemon
$MDBBINDIR/mserver5 --dbpath=$DATADIR/$DB_NAME --dbinit="clients.quit();" # allows us to read the wal log first
$MDBBINDIR/mserver5 --dbpath=$DATADIR/$DB_NAME --daemon=yes &
MDBPID=$!
sleep 5

# Warmup: run all queries in succession
echo "Warmup: run all queries in succession, monetdbpid: $MDBPID"
/usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
    --output=warmup.exectime $MDBBINDIR/mclient\
    -d $DB_NAME < $QUERIESDIR/qall.sql  2> warmup.stderr > warmup.stdout

sleep 5

for i in $QUERIES;
do
    echo "Running query: $i"
    ii=$(printf "%02d" $i)
    dir="q${ii}"
    mkdir -p $dir
    cd "$dir"

    if [ "$STAT" = false ]; then
        # Execute each query once
        /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k' \
            --output=exectime.txt perf record --pid=$MDBPID -s -g -m 512 -- \
            $MDBBINDIR/mclient -d $DB_NAME < $QUERIESDIR/q$ii.sql \
            2> stderr.txt > stdout.txt
    else
        source "$BASEDIR/common/perf-counters-axle.sh"
        for counter in "${array[@]}"; do
            echo "Running query $i for counters $counter."
            # Execute queries using perf stat, repeat 3
            LC_NUMERIC=C perf stat --append -o perf-stats.csv \
                -r 1 -e $counter --pid=$MDBPID -x "," -- \
                $MDBBINDIR/mclient -d $DB_NAME < $QUERIESDIR/q$ii.sql \
                2> stderr_$counter.txt > stdout_$counter.txt
        done
    fi

    cd ..
done

# Run monetdb tomograph, need to be enabled at command line
if [ "$TOMOGRAPH" = true ]; then
    source "$BASEDIR/monetdb/run_tomo.sh"
fi

echo "Stop the monetdb server"
kill $MDBPID

# Generate callgraphs
if [ "$STAT" = false ]; then
    source "$BASEDIR/common/callgraph.sh"
fi
