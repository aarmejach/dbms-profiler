#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

mkdir -p $RESULTS
cd $RESULTS

# Start a new instance of Postgres
#$PGBINDIR/postgres -D "$DATADIR" -p $PORT &
#PGPID=$!
#while ! $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; do
  #echo "Waiting for the Postgres server to start"
  #sleep 2
#done

# Additional sleep time seems necessary
#sleep 3

# Warmup: run all queries in succession
echo "Warmup: run all queries in succession"
#/usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
    #--output=warmup.exectime sudo -u $PGUSER $PGBINDIR/psql -h /tmp\
    #-p $PORT -d $DB_NAME < $QUERIESDIR/qall.sql  2> warmup.stderr > warmup.stdout

/usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
    --output=warmup.exectime $PGBINDIR/postgres --single -j -D $DATADIR $DB_NAME\
    < $QUERIESDIR/qall.sql 2> warmup.stderr > warmup.stdout

for i in $QUERIES;
do
    echo "Running query: $i"
    ii=$(printf "%02d" $i)
    dir="q${ii}"
    mkdir -p $dir
    cd "$dir"
    #chmod 777 .

    if [ "$SIMULATOR" = true ]; then
        cp $SIMCONFIG in.cfg
        pattern="command = \"\";"
        cmd="command = \"bash -c \"$PGBINDIR/postgres --single -j -D $DATADIR $DB_NAME < $QUERIESDIR/q$ii.sql\"\""
        sed -i "s#${pattern}#${cmd}#g" in.cfg
        $ZSIMPATH/build/zsim in.cfg 2> term.stderr > term.stdout
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

    #sudo chown $USER:$USER *
    #chmod 775 .
    cd ..
done

#echo "Stop the postgres server"
#$PGBINDIR/pg_ctl stop -D $DATADIR

# Generate callgraphs
if [ "$SIMULATOR" = false ]; then
    if [ "$STAT" = false ]; then
        source "$BASEDIR/common/callgraph.sh"
    fi
fi
