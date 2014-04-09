#!/bin/bash -e

# Clean up when exiting
trap 'kill $(jobs -p)' EXIT SIGINT SIGTERM

# zsim execution
$ZSIMPATH/build/opt/zsim in.cfg &> simterm.txt &
ZSIMPID=$!

# Sleep some
sleep 2

# Wait for the potgres server to start
while ! cat simterm.txt | grep -q "ready to accept connections" ; do
    sleep 5
done

# Additional waiting time
sleep 5

# Run query streams
i=1
while [ $i -le %NUMSTREAMS% ]; do
    $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -f $RUNDIR/throughput_query$i\
        2> psqlterm_stream$i.stderr > psqlterm_stream$i.stdout &
    let "i=$i+1"
done

# Wait for all pending streams to finish.
echo "Wait for all pending streams to finish"
for p in $(jobs -p); do
  if [ $p != $ZSIMPID ]; then
      wait $p
  fi
done
echo "All streams finished. Stop postgres and exit."

# Additional waiting time
sleep 5

# Stop server
$PGBINDIR/pg_ctl stop -w -D $DATADIR

# Sleep some more to allow sim to cleanup
sleep 10

#exit 0
