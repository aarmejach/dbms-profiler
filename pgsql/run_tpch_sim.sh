#!/bin/bash -e

# Clean up when exiting
trap 'kill $(jobs -p)' SIGINT SIGTERM

# zsim execution
$ZSIMPATH/build/opt/zsim in.cfg &> simterm.txt &

# Sleep some
sleep 2

# Wait for the potgres server to start
while ! cat simterm.txt | grep -q "ready to accept connections" ; do
    sleep 5
done

# Additional waiting time
sleep 5

# Run query
PGBINDIR/psql -h /tmp -p PORT -d DBNAME -f QUERIESDIR/qQNUM.sql 2> psqlterm.stderr > psqlterm.stdout

# Additional waiting time
sleep 5

# Stop server
PGBINDIR/pg_ctl stop -w -D DATADIR

# Sleep some more to allow sim to cleanup
sleep 10

# Parse ipc samples
python BASEDIR/common/parse-ipc-samples-zsim.py > ipc-samples-zsim.csv

exit 0
