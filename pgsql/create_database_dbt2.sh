#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

# Compile the benchmark
cd $BENCHDIR
cmake -G "Unix Makefiles" -DDBMS=pgsql -DCMAKE_BUILD_TYPE=Debug
make

cd storedproc/pgsql/c
make
make install #to shared folder, check
cd $BASEDIR

# Current time
t=$(timer)

TIME=`date`

# Create db and populate
sudo -u $PGUSER dbt2-pgsql-build-db -w $SCALE -l $PORT

# Configuration for query execution
query_configuration="
checkpoint_timeout = 600s
work_mem = 12GB                      #2 to 16GB
effective_cache_size = 192GB        #3/4 of total RAM (192GB)
default_statistics_target = 5000    #requires analyze to take effect
maintenance_work_mem = 32MB
"

echo "$query_configuration" | sudo -u $PGUSER tee -a $DATADIR/postgresql.conf
sudo -u $PGUSER pg_ctl reload -D $DATADIR

# Disable transparent huge pages
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

echo "Stop the postgres server"
sudo -u $PGUSER pg_ctl stop -D $DATADIR

sudo -u $PGUSER cp -a $DATADIR $DATADIR-template

cd $BASEDIR
printf 'Elapsed time: %s\n' $(timer $t)
