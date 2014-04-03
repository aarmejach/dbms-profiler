#!/bin/bash

# read file with perf counters list
file=$BASEDIR/common/perf-counters-axle-list
#file=perf-counters-axle-list
list=`cat $file | grep -o 'r[0-9A-F][0-9A-F][0-9A-F][0-9A-F]:[a-z]\|r[0-9A-F][0-9A-F][0-9A-F][0-9A-F]'`

merge_level=3
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


##### General
#C0H 00H Number of instructions at retirement.
#3CH 00H Number of thread cycles while the thread is not in a halt state.
#D0H 81H ALL Load uops retired to architectural path.
#D0H 82H ALL Store uops retired to architectural path.
#03H 10H Number of cases where any load is blocked but has no DCU miss
#5BH 0CH Cycles stalled due to free list empty.
#5BH 0FH Cycles stalled due to control structures full for physical registers.
#5BH 40H Cycles Allocator is stalled due Branch Order Buffer.
#5BH 4FH Cycles stalled due to out of order resources full.
#87H 01H Stalls caused by changing prefix length of the instruction.
#87H 04H Stall cycles due to IQ is full.
#A2H 01H Cycles Allocation is stalled due to Resource Related reason.
#A2H 02H Counts the cycles of stall due to lack of load buffers.
#A2H 04H Cycles stalled due to no eligible RS entry available.
#A2H 08H Cycles stalled due to no store buffers available.
#A2H 10H Cycles stalled due to re-order buffer full.
#A2H 20H Cycles stalled due to writing the FPU control word.
#A3H 04H Cycles of dispatch stalls. Set AnyThread to count per core.

##### ITLB
#C1H 02H Instructions that experienced an ITLB miss.
#85H 01H Misses in all ITLB levels that cause page walks.
#85H 02H Misses in all ITLB levels that cause completed page walks.
#85H 04H Cycle PMH is busy with a walk. ITLB.
#85H 10H Number of cache load STLB hits. No page walk. ITLB

##### DTLB
#08H 01H Misses in all TLB levels that cause a page walk of any page size. Loads
#08H 02H Misses in all TLB levels that caused page walk completed of any size. Loads
#08H 04H Cycle PMH is busy with a walk. DTLB loads
#49H 01H Miss in all TLB levels causes an page walk of any page size. stores
#49H 02H Miss in all TLB levels causes a page walk that completes of any page size. stores
#49H 04H Cycles PMH is busy with this walk. stores

##### STLB
#08H 10H Number of cache load STLB hits. No page walk.
#49H 10H Stores that miss first TLB but hit the second. No page walks.

##### Branch Predictor
#88H C1H Speculative and retired conditional branches.
#88H FFH Speculative and retired branches.
#89H FFH Speculative and retired mispredicted branches.
#C4H 00H Branch instructions at retirement.
#C4H 01H Counts the number of conditional branch instructions retired.
#C5H 00H Mispredicted branch instructions at retirement.
#C5H 01H Mispredicted conditional branch instructions retired.

##### L1I
#80H 02H Number of ICache, Streaming Buffer and Victim Cache Misses.

##### L1D
#48H 01H Increments the number of outstanding L1D misses every cycle.
#4EH 02H HW Prefetch requests that miss the L1D cache. Streamer and IP-based.
#51H 01H Number of lines brought into L1D cache. Replacements.
#51H 02H Counts the number of allocations of modified L1D cache lines.
#51H 04H Number of modified lines evicted from L1D cache due to replacement.
#51H 08H CL's in M evicted of L1D due to Snoop HitM or dirty line replacement.
#A3H 02H Cycles with pending L1 miss loads. Set AnyThread to count per core.

##### L2
#F0H 04H L2 cache accesses when fetching instructions.
#F0H 01H Demand Data Read requests that access L2 cache.
#24H 01H Demand Data Read requests that hit L2 cache.
#24H 03H Counts any demand and L1 HW prefetch data load requests to L2.
#24H 04H Counts the number of store RFO requests that hit the L2 cache.
#24H 08H Counts the number of store RFO requests that miss the L2 cache.
#24H 0CH Counts all L2 store RFO requests.
#24H 10H Number of instruction fetches that hit the L2 cache.
#24H 20H Number of instruction fetches that missed the L2 cache.
#24H 30H Counts all L2 code requests.
#24H 40H Requests from L2 Hardware prefetcher that hit L2.
#24H 80H Requests from L2 Hardware prefetcher that missed L2.
#24H C0H Any requests from L2 Hardware prefetchers to L2.
#F0H 02H RFO requests that access L2 cache.
#27H 01H RFOs that miss cache lines in L2.
#27H 0FH RFOs that access cache lines in any state in L2.
#28H 0FH Not rejected writebacks from L1D to L2 cache.
#A3H 01H Cycles with pending L2 miss loads. Set AnyThread to count per core.
#F0H 80H Transactions accessing L2 pipe.
#F1H 07H L2 cache lines filling L2.

##### LLC - uncore - offcore
#2EH 4FH Requests from the core that reference a cache line in the LLC.
#60H 01H Outstanding Data Read txs in SQ to uncore. Cmask=1 counts cycles.
#60H 04H Outstanding RFO store txs in SQ to uncore. Cmask=1 counts cycles.
#60H 08H Outstanding cacheable data read txs in SQ to uncore. Cmask=1 counts cycles.
#B0H 08H Data read requests sent to uncore (demand and prefetch).

##### Retired UOP loads
#D1H 01H Retired load uops with L1 cache hits as data sources.
#D1H 02H Retired load uops with L2 cache hits as data sources.
#D1H 04H Retired load uops which data sources were data hits in LLC without snoops required.
#D1H 20H Retired load uops which data sources were data missed LLC.
#D1H 40H Retired load uops which data sources missed L1 but hit Fill Buffer. 
#D2H 01H Retired load uops whose data source was an on-package core cache LLC hit and cross-core snoop missed.
#D2H 02H Retired load uops whose data source was an on-package LLC hit and cross-core snoop hits. 
#D2H 04H Retired load uops whose data source was an on-package core cache with HitM responses. 
#D2H 08H Retired load uops whose data source was LLC hit with no snoop required.
