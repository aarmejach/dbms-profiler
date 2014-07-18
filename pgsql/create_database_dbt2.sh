#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"
test -z "${DEBUG-}" && trap "teardown" EXIT

# Current time
t=$(timer)

# Prepare benchmark
cd $BENCHDIR
cmake -G "Unix Makefiles" -DDBMS=pgsql -DCMAKE_BUILD_TYPE=Debug
make

cd ${BENCHDIR}/storedproc/pgsql/c
make
make install #to postgres shared folder

cd $BASEDIR

# Check if pgsql port is free
do_check_port

# Check if pgsql already running in datadir
do_check_datadir

#initdb
${PGBINDIR}/initdb -D "${DATADIR}" --locale=C

# Start Postgres server
do_start_postgres

#createdb
${PGBINDIR}/createdb -h /tmp -p ${PORT} $DB_NAME --locale=C

# Change postgres configuration for data loading
loading_configuration="
checkpoint_segments = 300
checkpoint_timeout = 3600s
checkpoint_completion_target = 0.9
checkpoint_timeout = $CHECKPOINT_TIMEOUT
work_mem = $WORK_MEM
effective_cache_size = $EFFECTIVE_CACHE
shared_buffers = $SHARED_BUFFERS
default_statistics_target = $STATISTICS_TARGET
maintenance_work_mem = $MAINTAINANCE_MEM
"
echo "$loading_configuration" | tee -a $DATADIR/postgresql.conf
$PGBINDIR/pg_ctl reload -D $DATADIR

# Create tables
env PGBINDIR=$PGBINDIR DBT2DBNAME=$DB_NAME $BENCHDIR/bin/pgsql/dbt2-pgsql-create-tables -l ${PORT}

# Data generation
env PGPORT=${PORT} PGDATABASE=$DB_NAME $BENCHDIR/bin/dbt2-datagen --direct -w ${SCALE} --pgsql

# Create Indexes
env PGBINDIR=$PGBINDIR DBT2DBNAME=$DB_NAME $BENCHDIR/bin/pgsql/dbt2-pgsql-create-indexes -l ${PORT}

# Load stored functions
PSQL="${PGBINDIR}/psql -p ${PORT} -e -d ${DB_NAME}"
SHAREDIR=`${PGBINDIR}/pg_config --sharedir`
echo "loading C stored functions..."
${PSQL} -f ${SHAREDIR}/contrib/delivery.sql
${PSQL} -f ${SHAREDIR}/contrib/new_order.sql
${PSQL} -f ${SHAREDIR}/contrib/order_status.sql
${PSQL} -f ${SHAREDIR}/contrib/payment.sql
${PSQL} -f ${SHAREDIR}/contrib/stock_level.sql

# Set seed
${PGBINDIR}/psql -p ${PORT} -e -d ${DB_NAME} -c "SELECT setseed(0);"

# VACUUM FULL ANALYZE: Build optimizer statistics for newly-created
# tables. The VACUUM FULL is probably unnecessary; we want to scan the
# heap and update the commit-hint bits on each new tuple, but a regular
# VACUUM ought to suffice for that.
${PGBINDIR}/vacuumdb -p ${PORT} -z -f -d ${DB_NAME}

# Stop pg server
do_stop_postgres

# Load configuration
benchmark_configuration="
track_activities = off
track_counts = off
track_io_timing = off
update_process_title = off
autovacuum = off
"
echo "$benchmark_configuration" | tee -a $DATADIR/postgresql.conf

# Go to basedir and print elapsed time
cd $BASEDIR
printf 'Elapsed time: %s\n' $(timer $t)
