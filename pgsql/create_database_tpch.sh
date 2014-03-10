#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

# Initialize DATADIR
sudo -u $PGUSER mkdir -p "$DATADIR" || die "Failed to create directory $DATADIR"
sudo -u $PGUSER $PGBINDIR/initdb -D "$DATADIR" --encoding=UTF-8 --locale=C

# Start a new instance of Postgres
sudo -u $PGUSER $PGBINDIR/postgres -D "$DATADIR" -p $PORT &
PGPID=$!
while ! sudo -u $PGUSER $PGBINDIR/pg_ctl status -D $DATADIR | grep "server is running" -q; do
  echo "Waiting for the Postgres server to start"
  sleep 2
done

# Create database
sudo -u $PGUSER $PGBINDIR/createdb -h /tmp -p $PORT $PGUSER --encoding=UTF-8 --locale=C

DEBUG_ASSERTIONS=`sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PORT -c 'show debug_assertions' -t | grep on | wc -l`

# disable resolving of *.tbl to '*.tbl' in case there are no matching files
shopt -s nullglob

if [ $DEBUG_ASSERTIONS = 1 ] ;
then
    echo "Error: debug_assertions are enabled">&2
    exit -1
fi

cd "$BASEDIR/dbgen"
if ! [ -x dbgen ] || ! [ -x qgen ];
then
  make -j $CORES
fi

sudo -u $PGUSER mkdir -p "$TPCHTMP" || die "Failed to create temporary directory: '$TPCHTMP'"
cd "$TPCHTMP"
sudo -u $PGUSER cp "$BASEDIR/dbgen/dists.dss" .
# Run dbgen with "force", to overwrite existing files
# Create table files separately to have better IO throughput
sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T c &
sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T s &
sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T n &
sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T r &
sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T O &
sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T L &
sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T P &
sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T S &

# Wait for all pending jobs to finish.
for p in $(jobs -p);
do
  if [ $p != $PGPID ];
  then
      wait $p
  fi
done

data_loading_configuration="
checkpoint_segments = 300
checkpoint_timeout = 3600s
checkpoint_completion_target = 0.9
shared_buffers = 32GB
maintenance_work_mem = 1GB
"

echo "DROP DATABASE IF EXISTS $DB_NAME" | sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PORT
# Make sure we're all on the same page wrt encoding, collations, etc.
sudo -u $PGUSER $PGBINDIR/createdb -h /tmp -p $PORT $DB_NAME --encoding=UTF-8 --locale=C
if [ $? != 0 ]; then
  # Did you forget to disconnect from the database before dropping?
  echo "Error: Can't proceed without database"
  exit -1
fi

TIME=`date`
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "comment on database $DB_NAME is 'TPC-H data, created at $TIME'"
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME < "$BASEDIR/dbgen/dss.ddl"

# Configuration parameters for efficient data loading
echo "$data_loading_configuration" | sudo -u $PGUSER tee -a $DATADIR/postgresql.conf

sudo -u $PGUSER $PGBINDIR/pg_ctl reload -D $DATADIR

cd "$TPCHTMP"
for f in *.tbl; do
  bf="$(basename $f .tbl)"
  # We truncate the empty table in the sames transaction to enable Postgres to
  # safely skip WAL-logging. See
  # http://www.postgresql.org/docs/current/static/populate.html#POPULATE-PITR
  echo "truncate $bf; COPY $bf FROM '$(pwd)/$f' WITH DELIMITER AS '|'" | sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME &
done

# TODO: It would be nice if there was a way to limit the number of
# concurrently executing jobs to $CORES. It is surprisingly easy to make COPY
# CPU-bound.
for p in $(jobs -p); do
  if [ $p == $PGPID ]; then continue; fi
  wait $p;
done

# Create primary and foreign keys
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME < "$BASEDIR/dbgen/dss.ri"

# Remove tmp folder
cd "$BASEDIR"
sudo -u $PGUSER rm -rf "$TPCHTMP"

# Since wal_level is hopefully set to 'minimal', it ought to be possible to skip
# WAL logging these create index operations, too.
echo "Creating 'All' indexes..."
# Primary key definitions already create indexes
#sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_r_regionkey ON region (r_regionkey);" &
#sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_n_nationkey ON nation (n_nationkey);" &
#sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_p_partkey ON part (p_partkey);" &
#sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_s_suppkey ON supplier (s_suppkey);" &
#sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_c_custkey ON customer (c_custkey);" &
#sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_o_orderkey ON orders (o_orderkey);" &

# Pg does not create indexed on foreign keys, create them manually
#sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_n_regionkey ON nation (n_regionkey);" & # not used
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_s_nationkey ON supplier (s_nationkey);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_c_nationkey ON customer (c_nationkey);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_ps_suppkey ON partsupp (ps_suppkey);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_ps_partkey ON partsupp (ps_partkey);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_o_custkey ON orders (o_custkey);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_orderkey ON lineitem (l_orderkey);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_suppkey_partkey ON lineitem (l_partkey, l_suppkey);" &

# other indexes
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_shipdate ON lineitem (l_shipdate);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_partkey ON lineitem (l_partkey);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_suppkey ON lineitem (l_suppkey);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_receiptdate ON lineitem (l_receiptdate);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_orderkey_quantity ON lineitem (l_orderkey, l_quantity);" &
sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_o_orderdate ON orders (o_orderdate);" &
#sudo -u $PGUSER  $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "CREATE INDEX i_l_commitdate ON lineitem (l_commitdate);" & # not used

for p in $(jobs -p); do
    if [ $p == $PGPID ]; then continue; fi
    wait $p;
done

# Configuration for query execution
query_configuration="
checkpoint_timeout = 600s
work_mem = 12GB                      #2 to 16GB
effective_cache_size = 192GB        #3/4 of total RAM (192GB)
default_statistics_target = 5000    #requires analyze to take effect
maintenance_work_mem = 32MB
"
echo "$query_configuration" | sudo -u $PGUSER tee -a $DATADIR/postgresql.conf
sudo -u $PGUSER $PGBINDIR/pg_ctl reload -D $DATADIR

# Disable transparent huge pages
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# Always analyze after bulk-loading; when hacking Postgres, typically Postgres
# is run with autovacuum turned off.
echo "Running vacuum freeze analyze..."
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "vacuum freeze"
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "analyze"
# Checkpoint, so we have a "clean slate". Just in-case.
echo "Checkpointing..."
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "checkpoint"

echo "Stop the postgres server"
sudo -u $PGUSER $PGBINDIR/pg_ctl stop -D $DATADIR

if [ -d "$QUERIESDIR" ]; then
    echo "Queries folder exists, skip query creation."
else
    echo "Queries folder does not exists, query creation."
    mkdir -p $QUERIESDIR
    cd "$BASEDIR/dbgen"
    for i in $(seq 1 22);
    do
        ii=$(printf "%02d" $i)
        DSS_QUERY=queries/$DATABASE ./qgen -d -s $SCALE $i > $QUERIESDIR/q$ii.sql
        cat $QUERIESDIR/q$ii.sql >> $QUERIESDIR/qall.sql
        sed 's/^select/explain select/' $QUERIESDIR/q$ii.sql > $QUERIESDIR/q$ii.explain.sql
        sed 's/^select/explain analyze select/' $QUERIESDIR/q$ii.sql > $QUERIESDIR/q$ii.analyze.sql
    done
fi

cd $BASEDIR
printf 'Elapsed time: %s\n' $(timer $t)
