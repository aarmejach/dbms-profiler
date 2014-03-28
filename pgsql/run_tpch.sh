#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

mkdir -p $RESULTS
cd $RESULTS

# Warmup: run all queries in succession
echo "Warmup: run all queries in succession"
/usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
    --output=warmup.exectime $PGBINDIR/postgres --single -j -D $DATADIR $DB_NAME\
    < $QUERIESDIR/qall.sql 2> warmup.stderr > warmup.stdout

bq='\\"'
for i in $QUERIES;
do
    echo "Running query: $i"
    ii=$(printf "%02d" $i)
    dir="q${ii}"
    mkdir -p $dir
    cd "$dir"

    if [ "$SIMULATOR" = true ]; then
        cp $SIMCONFIG in.cfg
        pattern='command = "";'
        cmd="command = \"bash -c ${bq}$PGBINDIR/postgres --single -j -D $DATADIR $DB_NAME < $QUERIESDIR/q$ii.sql${bq}\";"
        sed -i "s#${pattern}#${cmd}#g" in.cfg
        $ZSIMPATH/build/opt/zsim in.cfg 2> term.stderr > term.stdout
    else
        if [ "$STAT" = false ]; then
            # Execute each query once
            /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
                --output=exectime.txt perf record -s -g -m 512 --\
                $PGBINDIR/postgres --single -j -D $DATADIR $DB_NAME < $QUERIESDIR/q$ii.sql\
                2> stderr.txt > stdout.txt
        else
            source "$BASEDIR/common/perf-counters-axle.sh"
            for counter in "${array[@]}"; do
                echo "Running query $i for counters $counter."
                # Execute queries using perf stat, repeat 3
                LC_NUMERIC=C perf stat --append -o perf-stats.csv -r 1 -e $counter -x "," --\
                    $PGBINDIR/postgres --single -j -D $DATADIR $DB_NAME < $QUERIESDIR/q$ii.sql\
                    2> stderr_$counter.txt > stdout_$counter.txt
            done
        fi
    fi

    cd ..
done

# Generate callgraphs
if [ "$SIMULATOR" = false ]; then
    if [ "$STAT" = false ]; then
        source "$BASEDIR/common/callgraph.sh"
    fi
fi
