#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
teardown() {
  echo "Teardown: Cleaning up before exiting"
  sudo /usr/bin/cpupower frequency-set -g ondemand
  $PGBINDIR/pg_ctl stop -m fast -D "$DATADIR" 2>/dev/null && sleep 1
  JOBS=$(jobs -p)
  test -z "$JOBS" || { kill $JOBS && sleep 2; }
  JOBS=$(jobs -p)
  test -z "$JOBS" || kill -9 $JOBS
}

# Calculates elapsed time
timer() {
    if [[ $# -eq 0 ]]; then
        echo $(date '+%s')
    else
        local  stime=$1
        etime=$(date '+%s')

        if [[ -z "$stime" ]]; then stime=$etime; fi

        dt=$((etime - stime))
        ds=$((dt % 60))
        dm=$(((dt / 60) % 60))
        dh=$((dt / 3600))
        printf '%d:%02d:%02d' $dh $dm $ds
    fi
}

# To perform checks
die() {
  echo "$@"
  exit -1;
}

do_wait() {
    # Wait for all pending jobs to finish.
    for p in $(jobs -p);
    do
        if [ $p != $PGPID ]; then
            wait $p
        fi
    done
}

do_check_port() {
    # Check for processor running on Postgres given port
    PORT_PROCLIST="$(lsof -i tcp:$PORT | tail -n +2 | awk '{print $2}')"
    if [[ $(echo "$PORT_PROCLIST" | wc -w) -gt 0 ]]; then
        echo "The following processes have taken port $PORT"
        echo "Please terminate them before running this script"
        echo
        for p in $PORT_PROCLIST; do
            ps -o pid,cmd $p
        done
        exit -1
    fi
}

do_check_datadir() {
    # Check if a Postgres server is running in the same directory
    if $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; then
        echo "A Postgres server is already running in the selected directory. Exiting."
        $PGBINDIR/pg_ctl status -D $DATADIR
        exit -2
    fi
}

do_start_postgres(){
    echo "Starting Postgres server"
    $PGBINDIR/postgres -D "$DATADIR" -p $PORT &
    PGPID=$!
    while ! $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; do
        echo "Waiting for the Postgres server to start"
        sleep 2
    done
}

do_stop_postgres(){
    echo "Stoping Postgres server"
    $PGBINDIR/pg_ctl stop -w -D $DATADIR && sleep 15
}
