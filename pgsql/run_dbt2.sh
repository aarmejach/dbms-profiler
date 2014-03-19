#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

# Start the database
sudo -u $PGUSER dbt2-pgsql-start-db

if [ "$STAT" = false ]; then
    # Execute with perf record
    sudo -u $PGUSER dbt2-run-workload -a $DATABASE -d $DURATION\
            -w $SCALE -o $RESULTS -c $CLIENTS -l $PORT -n\
            -u $DB_NAME -perfrecord

else
    # Execute with perf stat
    # Get the performance counters array
    source "$BASEDIR/common/perf-counters-axle.sh"
    for counter in "${array[@]}"; do
        echo "Running dbt2 for counters $counter."
        
        # Get a fresh copy of the database
        sudo -u $PGUSER rm -r $DATADIR
        sudo -u $PGUSER cp -a $DATADIR-template $DATADIR
        
        sudo -u $PGUSER dbt2-run-workload -a $DATABASE -d $DURATION\
            -w $SCALE -o $RESULTS/$counter -c $CLIENTS -l $PORT -n\
            -u $DB_NAME -perfstat $counter
    done
fi

echo "Stop the postgres server"
sudo -u $PGUSER dbt2-psql-stop-db

# Generate callgraphs
if [ "$STAT" = false ]; then
    cd $RESULTS

    cgf="callgraph.pdf"
    echo "Creating the call graph: $cgf"
    perf script | python "$BASEDIR/gprof2dot.py" -f perf | dot -Tpdf -o $cgf 

    cd - >/dev/null
fi
