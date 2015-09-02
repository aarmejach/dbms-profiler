#!/bin/bash

# read file with perf counters list
file=$BASEDIR/common/perf-counters-pmfs-list
#file=perf-counters-axle-list
list=`cat $file | grep -o 'r[0-9]\+[0-9A-F]*:[uk]\|r[0-9]\+[0-9A-F]*'`

merge_level=4
it=1
array_item=
array_index=0

# create the array dynamically using the list
for elem in $list; do

    if [ $it -eq $merge_level ]; then
        array_item=${array_item}${elem}
        array[$array_index]=$array_item
        array_index=$((array_index+1))
        it=1
        array_item=
        continue
    fi

    array_item=${array_item}${elem},

    ((it++))
done
# don't forget counters if not divisable by merge_level!
if [ "x$array_item" != "x" ]; then
    array_item=`echo ${array_item} | sed 's/,$//g'`
    array[$array_index]=$array_item
fi

#for counter in "${array[@]}"; do
    #echo $counter
#done
