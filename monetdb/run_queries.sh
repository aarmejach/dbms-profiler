#!/bin/bash

# Install teardown() function to kill any lingering jobs
# Check if monetdb is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

mkdir -p $RESULTS
RESULTS=$RESULTS/${SCALE}GB-`date +"%Y%m%d-%H%M%S"`
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

    # Execute each query once
    /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
        --output=exectime.txt perf record --pid=$MDBPID -s -g -m 512 -- $MDBBINDIR/mclient\
        -d $DB_NAME < $QUERIESDIR/q$ii.sql  2> stderr.txt > stdout.txt

    cd ..
done

for i in $QUERIES;
do
    echo "Running tomograph on query: $i"
    ii=$(printf "%02d" $i)
    dir="q${ii}"
    cd "$dir"

    python $BASEDIR/$DATABASE/run_tomo.py $QUERIESDIR/q$ii.sql

    cd ..
done

echo "Stop the monetdb server"
kill $MDBPID

# Generate callgraph
for i in $QUERIES;
do
  ii=$(printf "%02d" $i)
  dir="q${ii}"
  mkdir -p $dir
  cd "$dir"

  cgf="q${ii}-callgraph.pdf"
  echo "Creating the call graph: $cgf"
  perf script | python "$BASEDIR/gprof2dot.py" -f perf | dot -Tpdf -o $cgf &

  cd - >/dev/null
done

# Wait for all pending jobs to finish.
for p in $(jobs -p);
do
  wait $p
done

exit 1
