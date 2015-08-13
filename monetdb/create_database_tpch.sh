#!/bin/bash

# Install teardown() function to kill any lingering jobs
# Check if monetdb is running
source "$BASEDIR/$DATABASE/common.sh"

# Current time
t=$(timer)

# Initialize monetdb daemon and create database
# should I set up locales?
mkdir -p "$DATADIR" || die "Failed to create directory $DATADIR"
$MDBBINDIR/mserver5 --dbpath=$DATADIR/$DB_NAME --set gdk_nr_threads=4 --daemon=yes &
#$MDBBINDIR/mserver5 --dbpath=$DATADIR/$DB_NAME --set gdk_nr_threads 8 --daemon=yes &
#$MDBBINDIR/monetdbd create $DATADIR
#$MDBBINDIR/monetdbd start $DATADIR
#$MDBBINDIR/monetdb create $DB_NAME
#$MDBBINDIR/monetdb release $DB_NAME

MDBPID=$!
echo "monetdb server runing on pid $MDBPID"
sleep 10

# disable resolving of *.tbl to '*.tbl' in case there are no matching files
shopt -s nullglob

# compile dbgen
cd "$BENCHDIR"
if ! [ -x dbgen ] || ! [ -x qgen ];
then
  make -j $CORES
fi

# generate tpc-h data
mkdir -p "$TPCHTMP" || die "Failed to create temporary directory: '$TPCHTMP'"
cd "$TPCHTMP"
cp "$BENCHDIR/dists.dss" .
# Run dbgen with "force", to overwrite existing files
# Create table files separately to have better IO throughput
"$BENCHDIR/dbgen" -s $SCALE -f -v -T c &
"$BENCHDIR/dbgen" -s $SCALE -f -v -T s &
"$BENCHDIR/dbgen" -s $SCALE -f -v -T n &
"$BENCHDIR/dbgen" -s $SCALE -f -v -T r &
"$BENCHDIR/dbgen" -s $SCALE -f -v -T O &
"$BENCHDIR/dbgen" -s $SCALE -f -v -T L &
"$BENCHDIR/dbgen" -s $SCALE -f -v -T P &
"$BENCHDIR/dbgen" -s $SCALE -f -v -T S &

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
$MDBBINDIR/mclient -d $DB_NAME < "$BENCHDIR/dss.ddl"

cd "$TPCHTMP"
for f in *.tbl; do
  bf="$(basename $f .tbl)"
  # http://www.pilhokim.com/index.php?title=Project/EFIM/TPC-H#Setup_MonetDB
  echo "COPY INTO $bf FROM '$(pwd)/$f' USING DELIMITERS '|','\n';" | $MDBBINDIR/mclient -d $DB_NAME &
done

# TODO: It would be nice if there was a way to limit the number of
# concurrently executing jobs to $CORES. It is surprisingly easy to make COPY
# CPU-bound.
for p in $(jobs -p); do
  if [ $p == $MDBPID ]; then continue; fi
  wait $p;
done

# Create primary and foreign keys
#$MDBBINDIR/mclient -d $DB_NAME < "$BENCHDIR/dss.ri"

# Remove tmp folder
cd "$BASEDIR"
rm -rf "$TPCHTMP"

# Since wal_level is hopefully set to 'minimal', it ought to be possible to skip
# WAL logging these create index operations, too.
echo "Creating 'All' indexes..."
# Primary key definitions already create indexes ????
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_r_regionkey ON region (r_regionkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_n_nationkey ON nation (n_nationkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_p_partkey ON part (p_partkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_s_suppkey ON supplier (s_suppkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_c_custkey ON customer (c_custkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_o_orderkey ON orders (o_orderkey);"

# Pg does not create indexed on foreign keys, create them manually
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_n_regionkey ON nation (n_regionkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_s_nationkey ON supplier (s_nationkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_c_nationkey ON customer (c_nationkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_ps_suppkey ON partsupp (ps_suppkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_ps_partkey ON partsupp (ps_partkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_o_custkey ON orders (o_custkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_orderkey ON lineitem (l_orderkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_suppkey_partkey ON lineitem (l_partkey, l_suppkey);"

# other indexes
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_shipdate ON lineitem (l_shipdate);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_partkey ON lineitem (l_partkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_suppkey ON lineitem (l_suppkey);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_receiptdate ON lineitem (l_receiptdate);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_orderkey_quantity ON lineitem (l_orderkey, l_quantity);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_o_orderdate ON orders (o_orderdate);"
$MDBBINDIR/mclient -d $DB_NAME -s "CREATE INDEX i_l_commitdate ON lineitem (l_commitdate);"

for p in $(jobs -p); do
    if [ $p == $MDBPID ]; then continue; fi
    wait $p;
done

# Disable transparent huge pages
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

echo "Stop the monetdb server"
kill $MDBPID
#$MDBBINDIR/monetdbd stop $DATADIR
sleep 10

if [ -d "$QUERIESDIR" ]; then
    echo "Queries folder exists, skip query creation."
else
    echo "Queries folder does not exists, query creation."
    mkdir -p $QUERIESDIR
    cd "$BENCHDIR"
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
