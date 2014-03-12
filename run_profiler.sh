#!/bin/bash

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

source "$BASEDIR/common/config"

show_help() {
    echo "Execute benchmarks for certain databases."
    echo "You can specify DBMS to be used with -db. Possible options are $DATABASES."
}


while test $# -gt 0
do
    case $1 in
        -h|--help) # print help
            show_help
            exit 0
            ;;
        -db|--database) # DBMS to be used
            shift
            DATABASES=$1
            shift
            ;;
        -b|--benchmark) # bench to be used, if not specified all will be executed
            shift
            BENCHMARKS=$1
            shift
            ;;
        -p|--prepare) # just create the DB, don't run the benchmark
            PREPARE=true
            shift
            ;;
        -t|--tomograph) # this just works with monetdb
            TOMOGRAPH=true
            shift
            ;;
        -r|--results) # append a "name" to results dir
            shift
            RESULTSDIR_APPEND="-${1}"
            shift
            ;;
        -s|--stat) # use perf stat instead of record
            STAT=1
            shift
            ;;
        *)
            echo "Unrecognized option: $1"
            exit 1
    esac
    shift
done

echo "Profiler running benchmark/s: $BENCHMARKS, on $DATABASES."

for DATABASE in $DATABASES; do
    echo "Running on $DATABASE"
    cd $BASEDIR

    for bench in $BENCHMARKS; do
        echo "Running benchmark: $bench"

        # The DB folder must exist
        if [ -d "$DATABASE" ]; then
            echo "Load configuration for $DATABASE and $bench"
            source "$BASEDIR/$DATABASE/$bench"
        else
            show_help
            exit 0
        fi

        # Check if DB needs to be created and check if PREPARE flag is true
        if [ -d "$DATADIR" ]; then
            echo "DB folder exists, skip creation"
        else
            echo "DB does not exist, creating data dir in $DATADIR"
            source "$BASEDIR/$DATABASE/create_database_$bench.sh"
            echo "done creating data dir in $DATADIR"
        fi
        if [ "$PREPARE" = true ]; then
            echo "Exiting, prepare flag was set to true"
            exit 0
        fi

        # Will run the benchmark
        echo "Get ready to run benchmark $bench: drop caches."
        sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
        sleep 5

        echo "Running benchmark $bench for $DATABASE"
        source "$BASEDIR/$DATABASE/run_$bench.sh"
    done

done

echo "profiler done."
exit 0
