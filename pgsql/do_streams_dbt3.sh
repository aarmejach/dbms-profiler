#!/bin/bash

do_stream_creation() {
    echo "Creating $1 stream files"
    i=1
    while [ $i -le $1 ]; do
        query_file="$RUNDIR/throughput_query$i"
        tmp_query_file="$RUNDIR/tmp_throughput_query$i.sql"
        param_file="$RUNDIR/throughput_param$i"

        # output PID to a tmp file
        echo "$$" > $RUNDIR/PID$i

        if [ ! -f $RUNDIR/$SEED_FILE ]; then
            echo "creating seed file $SEED_FILE, you can change the seed by "
            echo "modifying this file"
            date +%-m%d%H%M%S > $RUNDIR/$SEED_FILE
        fi
        seed=`cat $RUNDIR/$SEED_FILE`
        let "seed = $seed + $i"

        # generate the queries for thoughput test
        rm -f $query_file
        rm -f $tmp_query_file
        cd $DBGENDIR
        DSS_QUERY=queries/$DATABASE ./qgen -c -r $seed -p $i -s $SCALE -l $param_file > $query_file
        cd $RESULTS

        # Ugly hack to remove queries from query_file
        for q in $QUERIESALL; do
            if [[ $QUERIES =~ (^| )$q($| ) ]]; then
                echo "keep query $q"
            else
                echo "strip query $q"
                line=`grep "(Q$q)" $query_file -n | cut -f1 -d:`
                len=`wc -l $DBGENDIR/queries/$DATABASE/$q.sql | cut -f1 -d" "`
                let "lineend=$line+$len-1"
                sed -i "${line},${lineend}d" $query_file
            fi
        done

        let "i=$i+1"
    done
}
