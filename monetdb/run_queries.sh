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
sudo -u $MDBUSER $MDBBINDIR/mserver5 --dbpath=$DATADIR/$DB_NAME --dbinit="clients.quit();" # allows us to read the wal log first
sudo -u $MDBUSER $MDBBINDIR/mserver5 --dbpath=$DATADIR/$DB_NAME --daemon=yes &
MDBPID=$!
sleep 5

# Warmup: run all queries in succession
echo "Warmup: run all queries in succession"
/usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
    --output=warmup.exectime sudo -u $MDBUSER $MDBBINDIR/mclient\
    -d $DB_NAME < $QUERIESDIR/qall.sql  2> warmup.stderr > warmup.stdout

for i in $QUERIES;
do
    echo "Running query: $i"
    ii=$(printf "%02d" $i)
    dir="q${ii}"
    mkdir -p $dir
    cd "$dir"

    # Execute each query once
    /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
        --output=exectime.txt sudo -u $MDBUSER $MDBBINDIR/mclient\
        -d $DB_NAME < $QUERIESDIR/q$ii.sql  2> stderr.txt > stdout.txt

    cd ..
done

echo "Stop the monetdb server"
kill $MDBPID

exit 1
