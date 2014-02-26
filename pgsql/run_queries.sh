#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

mkdir -p $RESULTS
RESULTS=$RESULTS/${SCALE}GB-`date +"%Y%m%d%H%M%S"`
mkdir -p $RESULTS
cd $RESULTS

# Start a new instance of Postgres
sudo -u $PGUSER taskset -c 2 $PGBINDIR/postgres -D "$DATADIR" -p $PORT &
PGPID=$!
while ! sudo -u $PGUSER $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; do
  echo "Waiting for the Postgres server to start"
  sleep 1
done

# Warmup: run all queries in succession
echo "Warmup: run all queries in succession"
/usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
    --output=warmup.exectime sudo -u $PGUSER $PGBINDIR/psql -h /tmp\
    -p $PORT -d $DB_NAME < $QUERIESDIR/qall.sql  2> warmup.stderr > warmup.stdout

for i in $QUERIES;
do
    echo "Running query: $i"
    ii=$(printf "%02d" $i)
    dir="q${ii}"
    mkdir -p $dir
    cd "$dir"

    # Execute each query once
    /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
        --output=exectime.txt sudo -u $PGUSER $PGBINDIR/psql -h /tmp\
        -p $PORT -d $DB_NAME < $QUERIESDIR/q$ii.sql  2> stderr.txt > stdout.txt

    cd ..
done

echo "Stop the postgres server"
sudo -u $PGUSER $PGBINDIR/pg_ctl stop -D $DATADIR

exit 1
