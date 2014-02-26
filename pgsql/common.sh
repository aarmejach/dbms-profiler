#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
teardown() {
  echo "Cleaning up before exiting"
  sudo -u $PGUSER $PGBINDIR/pg_ctl stop -m fast -D "$DATADIR" 2>/dev/null && sleep 1
  JOBS=$(jobs -p)
  test -z "$JOBS" || { kill $JOBS && sleep 2; }
  JOBS=$(jobs -p)
  test -z "$JOBS" || kill -9 $JOBS
}
test -z "${DEBUG-}" && trap "teardown" EXIT

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

# Check for the running Postgres; exit if there is any on the given port
PORT_PROCLIST="$(lsof -i tcp:$PORT | tail -n +2 | awk '{print $2}')"
if [[ $(echo "$PORT_PROCLIST" | wc -w) -gt 0 ]];
then
  echo "The following processes have taken port $PORT"
  echo "Please terminate them before running this script"
  echo
  for p in $PORT_PROCLIST;
  do
    ps -o pid,cmd $p
  done
  exit -1
fi

# Check if a Postgres server is running in the same directory
if sudo -u $PGUSER $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; then
  echo "A Postgres server is already running in the selected directory. Exiting."
  sudo -u $PGUSER $PGBINDIR/pg_ctl status -D $DATADIR
  exit -2
fi
