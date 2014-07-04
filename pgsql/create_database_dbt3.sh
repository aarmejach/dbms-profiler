#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

# Prepare benchmark
echo "Prepare the benchmark: configure and make"
cd "$BENCHDIR"
sh autogen.sh
./configure --with-postgresql=$PGPATH/build
make

# Initialize DATADIR
mkdir -p "$DATADIR" || die "Failed to create directory $DATADIR"
$PGBINDIR/initdb -D "$DATADIR" --encoding=UTF-8 --locale=C

# Start a new instance of Postgres
$PGBINDIR/postgres -D "$DATADIR" -p $PORT &
PGPID=$!
while ! $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; do
  echo "Waiting for the Postgres server to start"
  sleep 2
done

# Create database
$PGBINDIR/createdb -h /tmp -p $PORT $DB_NAME --encoding=UTF-8 --locale=C

# disable resolving of *.tbl to '*.tbl' in case there are no matching files
shopt -s nullglob

cd "$DBGENDIR"
if ! [ -x dbgen ] || ! [ -x qgen ];
then
  make -j $CORES
fi

if [ -d "$TPCHTMP" ]; then
    cd "$TPCHTMP"
else
    mkdir -p "$TPCHTMP" || die "Failed to create temporary directory: '$TPCHTMP'"
    cd "$TPCHTMP"
    cp "$DBGENDIR/dists.dss" .
    # Run dbgen with "force", to overwrite existing files
    # Create table files separately to have better IO throughput
    "$DBGENDIR/dbgen" -s $SCALE -f -v -T c &
    "$DBGENDIR/dbgen" -s $SCALE -f -v -T s &
    "$DBGENDIR/dbgen" -s $SCALE -f -v -T n &
    "$DBGENDIR/dbgen" -s $SCALE -f -v -T r &
    "$DBGENDIR/dbgen" -s $SCALE -f -v -T O &
    "$DBGENDIR/dbgen" -s $SCALE -f -v -T L &
    "$DBGENDIR/dbgen" -s $SCALE -f -v -T P &
    "$DBGENDIR/dbgen" -s $SCALE -f -v -T S &
fi

# Wait for all pending jobs to finish.
for p in $(jobs -p);
do
  if [ $p != $PGPID ];
  then
      wait $p
  fi
done

#echo "DROP DATABASE IF EXISTS $DB_NAME" | $PGBINDIR/psql -h /tmp -p $PORT
# Make sure we're all on the same page wrt encoding, collations, etc.
#$PGBINDIR/createdb -h /tmp -p $PORT $DB_NAME --encoding=UTF-8 --locale=C
#if [ $? != 0 ]; then
  # Did you forget to disconnect from the database before dropping?
  #echo "Error: Can't proceed without database"
  #exit -1
#fi

# Configuration for query execution
query_configuration="
checkpoint_segments = 300
checkpoint_timeout = 3600s
checkpoint_completion_target = 0.9
checkpoint_timeout = $CHECKPOINT_TIMEOUT
work_mem = $WORK_MEM                            #2 to 16GB
effective_cache_size = $EFFECTIVE_CACHE         #3/4 of total RAM (192GB)
shared_buffers = $SHARED_BUFFERS                #1/4 of total RAM (64GB)
default_statistics_target = $STATISTICS_TARGET  #requires analyze to take effect
maintenance_work_mem = $MAINTAINANCE_MEM
"
echo "$query_configuration" | tee -a $DATADIR/postgresql.conf
$PGBINDIR/pg_ctl reload -D $DATADIR


TIME=`date`
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "comment on database $DB_NAME is 'DBT3 data, created at $TIME'"
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME < "$DBGENDIR/dss.ddl"

cd "$TPCHTMP"
for f in *.tbl; do
  bf="$(basename $f .tbl)"
  # We truncate the empty table in the sames transaction to enable Postgres to
  # safely skip WAL-logging. See
  # http://www.postgresql.org/docs/current/static/populate.html#POPULATE-PITR
  echo "truncate $bf; COPY $bf FROM '$(pwd)/$f' WITH DELIMITER AS '|'" | $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME &
done

# TODO: It would be nice if there was a way to limit the number of
# concurrently executing jobs to $CORES. It is surprisingly easy to make COPY
# CPU-bound.
for p in $(jobs -p); do
  if [ $p == $PGPID ]; then continue; fi
  wait $p;
done

# Create primary and foreign keys
#$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME < "$DBGENDIR/dss.ri" &

# Remove tmp folder
cd "$BASEDIR"
#rm -rf "$TPCHTMP"

# Since wal_level is hopefully set to 'minimal', it ought to be possible to skip
# WAL logging these create index operations, too.
echo "Creating 'All' indexes..."
# Primary key definitions already create indexes
#$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_r_regionkey ON region (r_regionkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_n_nationkey ON nation (n_nationkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_p_partkey ON part (p_partkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_s_suppkey ON supplier (s_suppkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_c_custkey ON customer (c_custkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_o_orderkey ON orders (o_orderkey);" &
#$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_ps_partkey_suppkey ON partsupp (ps_partkey, ps_suppkey);" &
#$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_orderkey_linenumber ON lineitem (l_orderkey, l_linenumber);" &

# Pg does not create indexed on foreign keys, create them manually
#$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_n_regionkey ON nation (n_regionkey);" & # not used
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_s_nationkey ON supplier (s_nationkey);" &
#$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_c_nationkey ON customer (c_nationkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_ps_suppkey ON partsupp (ps_suppkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_ps_partkey ON partsupp (ps_partkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_o_custkey ON orders (o_custkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_orderkey ON lineitem (l_orderkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_suppkey_partkey ON lineitem (l_partkey, l_suppkey);" &

# other indexes
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_shipdate ON lineitem (l_shipdate);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_partkey ON lineitem (l_partkey);" &
#$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_suppkey ON lineitem (l_suppkey);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_receiptdate ON lineitem (l_receiptdate);" &
#$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_orderkey_quantity ON lineitem (l_orderkey, l_quantity);" &
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_o_orderdate ON orders (o_orderdate);" &
#$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_commitdate ON lineitem (l_commitdate);" & # not used

for p in $(jobs -p); do
    if [ $p == $PGPID ]; then continue; fi
    wait $p;
done

# Disable transparent huge pages
#echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# Always analyze after bulk-loading; when hacking Postgres, typically Postgres
# is run with autovacuum turned off.
echo "Running vacuum freeze analyze..."
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "vacuum freeze"
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "analyze"
# Checkpoint, so we have a "clean slate". Just in-case.
echo "Checkpointing..."
$PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "checkpoint"

echo "Stop the postgres server"
$PGBINDIR/pg_ctl stop -D $DATADIR

execution_configuration="
track_activities = off
track_counts = off
track_io_timing = off
update_process_title = off
autovacuum = off
"
echo "$execution_configuration" | tee -a $DATADIR/postgresql.conf

cd $BASEDIR
printf 'Elapsed time: %s\n' $(timer $t)
