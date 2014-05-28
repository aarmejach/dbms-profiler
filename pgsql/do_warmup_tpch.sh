#!/bin/bash

# Warmup:
# 1- Do a sequential scan of all tables, puts data in OS/GPFS page cache
# 2- Run all queries

declare -a arr=("select AVG(l_quantity) from lineitem;"\
                "select AVG(ps_availqty) from partsupp;"\
                "select AVG(p_size) from part;"\
                "select AVG(s_acctbal) from supplier;"\
                "select AVG(c_custkey) from customer;"\
                "select AVG(o_orderkey) from orders;"\
                "select AVG(n_nationkey) from nation;"\
                "select AVG(r_regionkey) from region;")

do_warmup_tpch() {
    echo "Warmup for $BENCHMARK with scale ${SCALE}GB"

    for query in "${arr[@]}"; do
        $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME -c "$query" > /dev/null &
    done

    do_wait

    for i in $QUERIES; do
        ii=$(printf "%02d" $i)
        /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
            --output=warmup_q$ii.exectime $PGBINDIR/psql -h /tmp -p $PORT -d $DB_NAME\
            < $QUERIESDIR/q$ii.analyze.sql 2> warmup_q$ii.stderr > warmup_q$ii.stdout
    done
}
