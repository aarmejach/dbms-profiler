#!/bin/bash -e

# Run tomograph
for i in $QUERIES;
do
    echo "Running tomograph on query: $i"
    ii=$(printf "%02d" $i)
    dir="q${ii}"
    cd "$dir"

    python $BASEDIR/$DATABASE/run_tomo.py $QUERIESDIR/q$ii.sql

    cd ..
done
