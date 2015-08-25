#!/bin/bash -e

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
            ;;
        -b|--benchmark) # bench to be used, if not specified all will be executed
            shift
            BENCHMARKS=$1
            ;;
        -p|--prepare) # just create the DB, don't run the benchmark
            PREPARE=true
            ;;
        -t|--tomograph) # this just works with monetdb
            TOMOGRAPH=true
            ;;
        -a|--append) # append a "name" to results dir
            shift
            RESULTSDIR=$RESULTSDIR-$1
            ;;
        -r|--record) # use perf record instead of stat
            STAT=false
            ;;
        -sim|--simulator) # execute in the simulator
            SIMULATOR=true
            ;;
        -s|--scale) # scale in GB
            shift
            SCALE=$1
            ;;
        *)
            echo "Unrecognized option: $1"
            exit 1
    esac
    shift
done

if [ "$SIMULATOR" = true ]; then
    RESULTSDIR=$RESULTSDIR/zsim
else
    RESULTSDIR=$RESULTSDIR/perf
fi

# Argument testing
#if [ "$RESULTSDIR_APPEND" = "" ]; then
    #if [ "$STAT" = "true" ]; then
        #RESULTSDIR_APPEND="-perf"
    #else
        #RESULTSDIR_APPEND="-time"
    #fi
#fi

echo "Profiler running benchmark/s: $BENCHMARKS, on $DATABASES."

for DATABASE in $DATABASES; do
    echo "Running on $DATABASE"
    cd $BASEDIR

    for BENCHMARK in $BENCHMARKS; do
        echo "Running benchmark: $BENCHMARK"

        # The DB folder must exist
        if [ -d "$DATABASE" ]; then
            echo "Load configuration for $DATABASE and $BENCHMARK"
            source "$BASEDIR/$DATABASE/$BENCHMARK"
        else
            show_help
            exit 0
        fi

        # Check if DB needs to be created and check if PREPARE flag is true
        if [ -d "$DATADIR" ]; then
            echo "DB folder exists, skip creation"
        else
            echo "DB does not exist, creating data dir in $DATADIR"
            source "$BASEDIR/$DATABASE/create_database_$BENCHMARK.sh"
            echo "done creating data dir in $DATADIR"
        fi
        if [ "$PREPARE" = true ]; then
            echo "Exiting, prepare flag was set to true"
            exit 0
        fi

        # Will run the benchmark
        echo "Get ready to run benchmark $BENCHMARK: drop caches."
        sudo dropcaches.sh
        #sudo /usr/bin/cpupower frequency-set -g performance
        #sudo /usr/bin/cpupower frequency-set -u 2600000
        sleep 5

        echo "Running benchmark $BENCHMARK for $DATABASE"
        source "$BASEDIR/$DATABASE/run_$BENCHMARK.sh"

        # Change governor back to ondemand
        #sudo /usr/bin/cpupower frequency-set -g ondemand
    done

done

echo "profiler done."
exit 0
