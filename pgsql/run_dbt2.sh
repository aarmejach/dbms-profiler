#!/bin/bash -e

# Install teardown() function to kill any lingering jobs
# Check if postgres is running
source "$BASEDIR/$DATABASE/common.sh"

# Check if pgsql port is free
#do_check_port

# Check if pgsql already running in datadir
#do_check_datadir

# Start Postgres server
#do_start_postgres

# Prepare benchmark
cd $BENCHDIR
cmake -G "Unix Makefiles" -DDBMS=pgsql -DCMAKE_BUILD_TYPE=Debug
make

cd ${BENCHDIR}/storedproc/pgsql/c
make
make install #to postgres shared folder

mkdir -p $RESULTS
cd $RESULTS

for CLIENTS in $CLIENTSLIST; do
    mkdir -p ${RESULTS}/$CLIENTS
    cd ${RESULTS}/$CLIENTS

    ORIGDATADIR=$DATADIR
    if [ "$STAT" = false ]; then
        # Execute with perf record
	echo "Running DBT-2 with perf record"
	# Get a fresh copy of the database
	cp -a $ORIGDATADIR $ORIGDATADIR-record
	DATADIR=$ORIGDATADIR-record
	do_start_postgres
	# Warmup
	cat $DATADIR/base/*/* > /dev/null
        $BENCHDIR/bin/dbt2-run-workload -a $DATABASE -d $DURATION\
             -w $SCALE -o $RESULTS/$CLIENTS/record -c $CLIENTS -l $PORT -n -N -i $PGPID -r
	do_stop_postgres
	rm -r $DATADIR
	if grep -Rq "driver is exiting normally" $RESULTS/$CLIENTS/record; then
	    rm -r $RESULTS/$CLIENTS/record
	fi
    else
        # Execute with perf stat
        source "$BASEDIR/common/perf-counters-axle.sh"
        for counter in "${array[@]}"; do
	    echo "Running dbt2 for counters $counter."

	    # Get a fresh copy of the database
	    cp -a $ORIGDATADIR $ORIGDATADIR-$counter
	    DATADIR=$ORIGDATADIR-$counter
	    do_start_postgres

	    # Warmup
	    cat $DATADIR/base/*/* > /dev/null

	    ${BENCHDIR}/bin/dbt2-run-workload -a $DATABASE -d $DURATION\
		 -w $SCALE -o $RESULTS/$CLIENTS/$counter -c $CLIENTS -l $PORT -n -N -i $PGPID\
	         -p $counter

	    do_stop_postgres
	    rm -r $DATADIR

	    if grep -Rq "driver is exiting normally" $RESULTS/$CLIENTS/$counter; then
		    rm -r $RESULTS/$CLIENTS/$counter
	    fi
        done
    fi
    DATADIR=$ORIGDATADIR
done

#echo "Stop the postgres server"
#sudo -u $PGUSER env PATH=$PATH dbt2-psql-stop-db

# Generate callgraphs
if [ "$STAT" = false ]; then
    cd $RESULTS
    for CLIENTS in $CLIENTSLIST; do
	cd $CLIENTS/

        cgf="callgraph.pdf"
	echo "Creating the call graph: $cgf"
	perf script | python "$BASEDIR/scripts/gprof2dot.py" -f perf | dot -Tpdf -o $cgf

	cd - >/dev/null
    done
fi
