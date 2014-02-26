#!/bin/bash
BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)
DBMS="pgsql monetdb"

show_help() {
    echo "Execute TPC-H queries for specified database."
    echo "Specify DBMS to be used with -db. Possible options are $DBMS."
}


while test $# -gt 0
do
    case $1 in
        -h|--help) # print help
            show_help
            exit 1
            ;;
        -db|--database) # DBMS to be used
            DATABASE=$2
            shift
            ;;
    esac
    shift
done

if [ -d "$DATABASE" ]; then
    echo "Load configuration for $DATABASE"
    source "$BASEDIR/$DATABASE/config"
else
    show_help
    exit 0
fi

echo "Check if DB exists"
if [ -d "$DATADIR" ]; then
    echo "DB exists, skip creation"
else
    echo "DB does not exist, creating data dir in $DATADIR"
    source "$BASEDIR/$DATABASE/create_database.sh"
    echo "done creating data dir in $DATADIR"
fi

echo "Running queries for $DATABASE"
source "$BASEDIR/$DATABASE/run_queries.sh"
echo "done."
exit 1
