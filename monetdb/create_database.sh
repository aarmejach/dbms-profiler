#!/bin/bash

# Install teardown() function to kill any lingering jobs
# Check if monetdb is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

# Initialize monetdb daemon and create database
# should I set up locales?
sudo -u $MDBUSER mkdir -p "$DATADIR" || die "Failed to create directory $DATADIR"
sudo -u $MDBUSER $MDBBINDIR/mserver5 --dbpath=$DATADIR/$DB_NAME --daemon=yes &
MDBPID=$!
echo "monetdb server runing on pid $MDBPID"
sleep 10

# disable resolving of *.tbl to '*.tbl' in case there are no matching files
shopt -s nullglob

# compile dbgen
cd "$BASEDIR/dbgen"
if ! [ -x dbgen ] || ! [ -x qgen ];
then
  make -j $CORES
fi

# generate tpc-h data
sudo -u $MDBUSER mkdir -p "$TPCHTMP" || die "Failed to create temporary directory: '$TPCHTMP'"
cd "$TPCHTMP"
sudo -u $MDBUSER cp "$BASEDIR/dbgen/dists.dss" .
# Run dbgen with "force", to overwrite existing files
# Create table files separately to have better IO throughput
sudo -u $MDBUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T c &
sudo -u $MDBUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T s &
sudo -u $MDBUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T n &
sudo -u $MDBUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T r &
sudo -u $MDBUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T O &
sudo -u $MDBUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T L &
sudo -u $MDBUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T P &
sudo -u $MDBUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T S &

# Wait for all pending jobs to finish.
for p in $(jobs -p);
do
  if [ $p != $MDBPID ];
  then
      wait $p
  fi
done

# Take the time and create tables
TIME=`date`
sudo -u $MDBUSER $MDBBINDIR/mclient -d $DB_NAME < "$BASEDIR/dbgen/dss.ddl"

cd "$TPCHTMP"
for f in *.tbl; do
  bf="$(basename $f .tbl)"
  # http://www.pilhokim.com/index.php?title=Project/EFIM/TPC-H#Setup_MonetDB
  echo "COPY INTO $bf FROM '$(pwd)/$f' USING DELIMITERS '|','\n';" | sudo -u $MDBUSER $MDBBINDIR/mclient -d $DB_NAME &
done

# TODO: It would be nice if there was a way to limit the number of
# concurrently executing jobs to $CORES. It is surprisingly easy to make COPY
# CPU-bound.
for p in $(jobs -p); do
  if [ $p == $MDBPID ]; then continue; fi
  wait $p;
done

# Create primary and foreign keys
sudo -u $MDBUSER $MDBBINDIR/mclient -d $DB_NAME < "$BASEDIR/dbgen/dss.ri"

# Remove tmp folder
cd "$BASEDIR"
sudo -u $MDBUSER rm -rf "$TPCHTMP"

# Since wal_level is hopefully set to 'minimal', it ought to be possible to skip
# WAL logging these create index operations, too.
echo "Creating 'All' indexes..."
# Primary key definitions already create indexes ????
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_r_regionkey ON region (r_regionkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_n_nationkey ON nation (n_nationkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_p_partkey ON part (p_partkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_s_suppkey ON supplier (s_suppkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_c_custkey ON customer (c_custkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_o_orderkey ON orders (o_orderkey);" &

# Pg does not create indexed on foreign keys, create them manually
sudo -u $MDBUSER  $MDBBINDIR/mclient -h /tmp -p $PORT -d $DB_NAME -s "CREATE INDEX i_n_regionkey ON nation (n_regionkey);" & # not used
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_s_nationkey ON supplier (s_nationkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_c_nationkey ON customer (c_nationkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_ps_suppkey ON partsupp (ps_suppkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_ps_partkey ON partsupp (ps_partkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_o_custkey ON orders (o_custkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_orderkey ON lineitem (l_orderkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_suppkey_partkey ON lineitem (l_partkey, l_suppkey);" &

# other indexes
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_shipdate ON lineitem (l_shipdate);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_partkey ON lineitem (l_partkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_suppkey ON lineitem (l_suppkey);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_receiptdate ON lineitem (l_receiptdate);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_orderkey_quantity ON lineitem (l_orderkey, l_quantity);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_o_orderdate ON orders (o_orderdate);" &
sudo -u $MDBUSER  $MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_commitdate ON lineitem (l_commitdate);" & # not used

for p in $(jobs -p); do
    if [ $p == $MDBPID ]; then continue; fi
    wait $p;
done

# Disable transparent huge pages
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

echo "Stop the monetdb server"
kill $MDBPID
sleep 5

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
