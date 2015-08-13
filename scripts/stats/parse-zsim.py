#!/usr/bin/env python

import os,sys,string
from os.path import join, getsize
from collections import namedtuple, defaultdict
import numpy as np
from pprint import pprint
import csv
import h5py

def parse_h5file(file):
    res = {}

    f = h5py.File(file, 'r')
    #print "parsing ", file

    # Get the single dataset in the file
    try:
        dset = f["stats"]["root"]
        if dset.size == 0:
            raise ValueError
    except ValueError:
        print "ERROR reading file: " + file
        for key in zsimstatsdict:
            statlist = zsimstatsdict[key]
            for stat in statlist:
                res[key+"_"+stat] = -1
        for key in percorestatsdict:
            statlist = zsimstatsdict[key]
            for stat in statlist:
                for x in range(0,8):
                    res[key+str(x)+"_"+stat] = -1
        return res

    if 'zsim-ev.h5' in file:
        for key in zsimstatsdict:
            statlist = zsimstatsdict[key]
            for stat in statlist:
                res[key+"_"+stat] = float(np.sum(dset[-1][key][stat]))
        for key in percorestatsdict:
            statlist = zsimstatsdict[key]
            for stat in statlist:
                for x in range(0,dset[-1][key][stat].size):
                    res[key+str(x)+"_"+stat] = float(dset[-1][key][x][stat])
    else:
        # Periodic stats for dbt3
        for key in zsimstatsdict:
            statlist = zsimstatsdict[key]
            for stat in statlist:
                res[key+"_"+stat] = float(np.sum(dset[90][key][stat] - dset[57][key][stat]))
        for key in percorestatsdict:
            statlist = zsimstatsdict[key]
            for stat in statlist:
                for x in range(0,dset[-1][key][stat].size):
                    res[key+str(x)+"_"+stat] = float(dset[90][key][x][stat] - dset[57][key][x][stat])

    return res


def toFloat(a):
    for i in "W mA*t MB/s".split():
        if a.endswith(i):
            a=a[:-len(i)]
    return float(a)


def parse_nvmainFile(file):
    res = {}
    #print "parsing ", file

    array = open(file).read().strip().split('\n')
    idx = -1
    final_list = []
    tmp = []
    for elem in array:
        if '===' in elem:
            if idx > -1:
                final_list.append(tmp)
            idx = idx + 1
            tmp = []
        else:
            tmp.append(elem)

    if idx == 1:
        print "Parse NVMAIN " + file + " idx: " + str(idx)
        for key in nvmainstatsdict:
            statslist = nvmainstatsdict[key]
            for stat in statslist:
                res[key+"_"+stat] = sum(toFloat(i.split()[-1]) for i in final_list[0] if (key in i) and (stat in i))
    elif idx > 1:
        print "Parse NVMAIN " + file + " idx: " + str(idx)
        for key in nvmainstatsdict:
            statslist = nvmainstatsdict[key]
            for stat in statslist:
                res[key+"_"+stat] = sum(toFloat(i.split()[-1]) for i in final_list[90] if (key in i) and (stat in i)) - sum(toFloat(i.split()[-1]) for i in final_list[57] if (key in i) and (stat in i))

    return res


def get_results(d):
    results = {}
    for root, sfs, fs in os.walk(folder_results + d):
        for f in fs:
            #print f
            tmp = f.split('_')[0:3]
            # change query format
            if 'tpch' in tmp[0]:
                tmp[1] = "%02d" % int(tmp[1])

            if 'dbt3' in f:
                if 'zsim.h5' in f:
                    dict = parse_h5file(os.path.join(root, f))
                    if tuple(tmp[:]) in results:
                        results[tuple(tmp[:])].update(dict)
                    else:
                        results[tuple(tmp[:])] = dict
            else:
                if 'zsim-ev.h5' in f:
                    dict = parse_h5file(os.path.join(root, f))
                    if tuple(tmp[:]) in results:
                        results[tuple(tmp[:])].update(dict)
                    else:
                        results[tuple(tmp[:])] = dict

            if 'nvmain.out' in f:
                dict = parse_nvmainFile(os.path.join(root, f))
                if tuple(tmp[:]) in results:
                    results[tuple(tmp[:])].update(dict)
                else:
                    results[tuple(tmp[:])] = dict

    return results


def _eval_term(d, term):
    t = term.split()
    r = {}
    for i in t:
        if i[0] == '$':
            r[i] = d[i[1:]]
    for k in r:
        term = term.replace(k, str(r[k]))

    count = eval(term)
    return count


def add_counter(results, counter_name, counter_term):
    for k in results:
        dict = results[k]
        try:
            count = _eval_term(dict, counter_term)
        except KeyError:
            print "Warn: Keyerror " + str(k) + "for term " + counter_term
            count = -1
        except ZeroDivisionError:
            count = 0
        dict[counter_name] = count


def data_to_csv(results):
    data = []

    # First row, column names. Get first dict elem and sort event dictionary keys.
    column_names = ['bench', 'query', 'scale']
    for elem in sorted(results[results.keys()[0]]):
        column_names.append(elem)
    data.append(column_names)

    # Add rows one by one, check all possible workloads and add empty lines for the
    # ones that do not have results. Issue a warning if that is the case.
    for benchtype in reversed(sorted(benchmarks.iterkeys())):
        benchlist = benchmarks[benchtype]
        for bench in benchlist:
            # change query format
            if 'tpch' in benchtype:
                bench = "%02d" % int(bench)
            if 'dbt3' in benchtype:
                scale = '10'
            else:
                scale = '100'
            key = (benchtype, bench, scale)
            row = []
            row.append(key[0]) # bench
            row.append(key[1])# query
            row.append(key[2]) # scale
            if key in results:
                # Get event dict and iterate over sorted keys
                dict = results.get(key)
                for k in sorted(dict):
                    row.append(dict[k])
                data.append(row)
            else:
                row.append([0] * len(results[results.keys()[0]]))
                data.append(row)
                print "WARN: Missing benchmark " + benchtype + " " + bench + " in file " + csv_file.split("/")[-1]


    #for key in sorted(results):
        #row = []
        #row.append(key[0]) # bench
        #row.append(key[1])# query
        #row.append(key[2]) # scale

        # Get event dict and iterate over sorted keys
        #dict = results.get(key)
        #for k in sorted(dict):
            #row.append(dict[k])
        #data.append(row)

    with open(csv_file, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(data)


def parse_periodic_stats(d):
    for root, sfs, fs in os.walk(folder_results + d):
        print root
        for f in fs:
            if 'zsim.h5' in f:
                print f
                os.system("python common/parse-ipc-samples-zsim.py %(IN)s > %(OUT)s"%{'IN':os.path.join(root, f), 'OUT':os.path.join(root,f)+'.csv'})


def _main():
    global percorestatsdict, zsimstatsdict, nvmainstatsdict, csv_file, folder_results, benchmarks

    # Go to profiler's base dir
    os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/../..')

    # Configuration parameters
    #file_name = "common/perf-counters-axle-list"
    folder_results = os.getcwd() + '/' + "results-zsim/"
    #directories=[d for d in os.listdir(folder_results) if os.path.isdir(folder_results + d)]
    directories=['tests_zsim_base', 'tests_zsim_footprint', 'tests_zsim_tidy-new']

    benchmarks = { # 447.dealII and 481.wrf not working
    #'spec' : "400.perlbench 403.gcc 416.gamess 433.milc 435.gromacs 437.leslie3d 445.gobmk 450.soplex 454.calculix 458.sjeng 462.libquantum 465.tonto 471.omnetpp 483.xalancbmk 401.bzip2 410.bwaves 429.mcf 434.zeusmp 436.cactusADM 444.namd 453.povray 456.hmmer 459.GemsFDTD 464.h264ref 470.lbm 473.astar 482.sphinx3".split(),
    #'spec-r' : "400.perlbench 403.gcc 416.gamess 433.milc 435.gromacs 437.leslie3d 445.gobmk 450.soplex 454.calculix 458.sjeng 462.libquantum 465.tonto 471.omnetpp 483.xalancbmk 401.bzip2 410.bwaves 429.mcf 434.zeusmp 436.cactusADM 444.namd 453.povray 456.hmmer 459.GemsFDTD 464.h264ref 470.lbm 473.astar 482.sphinx3".split(),
    #'spec' : "403.gcc 433.milc 437.leslie3d 450.soplex 462.libquantum 471.omnetpp 410.bwaves 429.mcf 459.GemsFDTD 470.lbm 473.astar 482.sphinx3".split(),
    #'spec-r' : "403.gcc 433.milc 437.leslie3d 450.soplex 462.libquantum 471.omnetpp 410.bwaves 429.mcf 459.GemsFDTD 470.lbm 473.astar 482.sphinx3".split(),

'spec-mix3' : [
        ('450.soplex', '459.GemsFDTD', '403.gcc', '433.milc', '471.omnetpp', '437.leslie3d', '470.lbm', '437.leslie3d'), ('433.milc', '450.soplex', '462.libquantum', '470.lbm', '433.milc', '450.soplex', '462.libquantum', '459.GemsFDTD'), ('403.gcc', '459.GemsFDTD', '437.leslie3d', '433.milc', '462.libquantum', '437.leslie3d', '403.gcc', '462.libquantum'), ('403.gcc', '471.omnetpp', '429.mcf', '403.gcc', '462.libquantum', '471.omnetpp', '470.lbm', '470.lbm'), ('433.milc', '429.mcf', '437.leslie3d', '403.gcc', '471.omnetpp', '437.leslie3d', '462.libquantum', '471.omnetpp'), ('403.gcc', '433.milc', '437.leslie3d', '462.libquantum', '429.mcf', '470.lbm', '429.mcf', '459.GemsFDTD'), ('450.soplex', '471.omnetpp', '437.leslie3d', '403.gcc', '459.GemsFDTD', '450.soplex', '462.libquantum', '429.mcf'), ('433.milc', '459.GemsFDTD', '470.lbm', '403.gcc', '459.GemsFDTD', '462.libquantum', '462.libquantum', '429.mcf'), ('450.soplex', '462.libquantum', '437.leslie3d', '462.libquantum', '471.omnetpp', '429.mcf', '403.gcc', '462.libquantum'), ('429.mcf', '459.GemsFDTD', '471.omnetpp', '429.mcf', '437.leslie3d', '462.libquantum', '459.GemsFDTD', '470.lbm'), ('462.libquantum', '429.mcf', '403.gcc', '462.libquantum', '459.GemsFDTD', '470.lbm', '437.leslie3d', '433.milc'), ('462.libquantum', '462.libquantum', '437.leslie3d', '403.gcc', '459.GemsFDTD', '433.milc', '429.mcf', '437.leslie3d'), ('462.libquantum', '470.lbm', '471.omnetpp', '459.GemsFDTD', '433.milc', '462.libquantum', '471.omnetpp', '437.leslie3d'), ('462.libquantum', '471.omnetpp', '459.GemsFDTD', '471.omnetpp', '429.mcf', '470.lbm', '437.leslie3d', '471.omnetpp'), ('433.milc', '437.leslie3d', '470.lbm', '403.gcc', '433.milc', '450.soplex', '462.libquantum', '429.mcf'), ('459.GemsFDTD', '470.lbm', '433.milc', '462.libquantum', '470.lbm', '450.soplex', '462.libquantum', '462.libquantum'), ('471.omnetpp', '459.GemsFDTD', '403.gcc', '437.leslie3d', '462.libquantum', '471.omnetpp', '429.mcf', '437.leslie3d'), ('462.libquantum', '429.mcf', '459.GemsFDTD', '470.lbm', '462.libquantum', '429.mcf', '429.mcf', '437.leslie3d'), ('433.milc', '429.mcf', '433.milc', '462.libquantum', '429.mcf', '459.GemsFDTD', '437.leslie3d', '470.lbm'), ('433.milc', '462.libquantum', '459.GemsFDTD', '437.leslie3d', '462.libquantum', '462.libquantum', '462.libquantum', '471.omnetpp'), ('403.gcc', '450.soplex', '471.omnetpp', '433.milc', '462.libquantum', '471.omnetpp', '450.soplex', '470.lbm'), ('433.milc', '459.GemsFDTD', '450.soplex', '471.omnetpp', '462.libquantum', '462.libquantum', '429.mcf', '459.GemsFDTD'), ('450.soplex', '429.mcf', '462.libquantum', '471.omnetpp', '459.GemsFDTD', '437.leslie3d', '471.omnetpp', '459.GemsFDTD'), ('403.gcc', '450.soplex', '462.libquantum', '459.GemsFDTD', '470.lbm', '437.leslie3d', '462.libquantum', '437.leslie3d'), ('450.soplex', '462.libquantum', '450.soplex', '470.lbm', '462.libquantum', '462.libquantum', '429.mcf', '459.GemsFDTD'), ('450.soplex', '462.libquantum', '429.mcf', '403.gcc', '471.omnetpp', '429.mcf', '450.soplex', '429.mcf'), ('429.mcf', '437.leslie3d', '433.milc', '450.soplex', '471.omnetpp', '462.libquantum', '459.GemsFDTD', '437.leslie3d'), ('462.libquantum', '471.omnetpp', '470.lbm', '437.leslie3d', '462.libquantum', '429.mcf', '470.lbm', '433.milc'), ('450.soplex', '437.leslie3d', '403.gcc', '433.milc', '450.soplex', '459.GemsFDTD', '433.milc', '470.lbm'), ('462.libquantum', '471.omnetpp', '450.soplex', '462.libquantum', '433.milc', '450.soplex', '462.libquantum', '437.leslie3d'), ('403.gcc', '433.milc', '450.soplex', '471.omnetpp', '459.GemsFDTD', '403.gcc', '462.libquantum', '462.libquantum'), ('450.soplex', '429.mcf', '433.milc', '450.soplex', '470.lbm', '471.omnetpp', '459.GemsFDTD', '470.lbm')],

    #'tpch' : "2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22".split(),
    #'dbt3' : "1 2 4 6 8".split()
    'dbt3' : "4".split()
    #'dbt2' : "16 32 64".split()
    #'bigmem' : "stream graph500 nascg nasmg".split(),

    #'bigmem-mix' : [
            #('stream', 'graph500'),
            #('stream', 'nasmg'),
            #('stream', 'nascg'),
            #('graph500', 'nascg'),
            #('graph500', 'nasmg'),
            #('nascg', 'nasmg')
            #]
    }

    benchmarks['spec-mix3'] = ["-".join(elem) for elem in benchmarks['spec-mix3']]
    #benchmarks['bigmem-mix'] = ["-".join(elem) for elem in benchmarks['bigmem-mix']]

    for d in directories:

        # Parse periodic stats for ipc sampling
        #parse_periodic_stats(d)

        csv_file = os.getcwd() + '/' + "results/zsim-data-" + d + ".csv"

        # Define stats of interest and gather results
        zsimstatsdict = {
              'sandy' : ['instrs', 'cycles', 'mispredBranches'],
              'l1d'   : ['mGETS', 'mGETXIM', 'hGETS', 'hGETX'],
              'l1i'   : ['mGETS', 'mGETXIM', 'hGETS', 'hGETX'],
              'l2'    : ['mGETS', 'mGETXIM', 'hGETS', 'hGETX'],
              'l3'    : ['mGETS', 'mGETXIM', 'hGETS', 'hGETX'],
              'mem'   : ['rd', 'wr', 'PUTS', 'PUTX', 'rdlat', 'wrlat', 'footprint', 'addresses']
              }
        percorestatsdict = {
              'sandy' : ['instrs', 'cycles', 'mispredBranches']
              }
        nvmainstatsdict = {
              'DRC'    : ['totalPower', 'rb_hits', 'rb_miss', 'drc_hits', 'drc_miss'],
              'PredictorDRC' : ['truePredictions', 'falsePredictions'],
              'FRFCFS' : ['totalPower', 'rb_hits', 'rb_miss'],
              'ootprintCache' : ['subarray0.activeEnergy', 'subarray0.burstEnergy'],
              'y.channel0.FRFCFS' : ['bandwidth', 'mem_reads'],
              'y.channel1.FRFCFS' : ['bandwidth', 'mem_reads']
              }
        results = get_results(d)
        #pprint(results)

        # General statistics of interest
        add_counter(results, 'ipc', '$sandy_instrs / $sandy_cycles')

        # Caches
        add_counter(results, 'l1d_hits', '$l1d_hGETS + $l1d_hGETX')
        add_counter(results, 'l1d_misses', '$l1d_mGETS + $l1d_mGETXIM')
        add_counter(results, 'l1i_hits', '$l1i_hGETS + $l1i_hGETX')
        add_counter(results, 'l1i_misses', '$l1i_mGETS + $l1i_mGETXIM')
        add_counter(results, 'l2_hits', '$l2_hGETS + $l2_hGETX')
        add_counter(results, 'l2_misses', '$l2_mGETS + $l2_mGETXIM')
        add_counter(results, 'l3_hits', '$l3_hGETS + $l3_hGETX')
        add_counter(results, 'l3_misses', '$l3_mGETS + $l3_mGETXIM')

        add_counter(results, 'l1d_mpki', '( $l1d_misses * 1000 ) / $sandy_instrs')
        add_counter(results, 'l1i_mpki', '( $l1i_misses * 1000 ) / $sandy_instrs')
        add_counter(results, 'l2_mpki', '( $l2_misses * 1000 ) / $sandy_instrs')
        add_counter(results, 'l3_mpki', '( $l3_misses * 1000 ) / $sandy_instrs')

        # Mem
        add_counter(results, 'mem_acceses', '$mem_rd + $mem_wr')

        # DRC
        add_counter(results, 'drc_hitrate', '$DRC_drc_hits / ( $DRC_drc_hits + $DRC_drc_miss )')
        add_counter(results, 'drc_rbhitrate', '$DRC_rb_hits / ( $DRC_rb_hits + $DRC_rb_miss )')

        #PredictorDRC
        add_counter(results, 'predictor_rate', '$PredictorDRC_truePredictions / ( $PredictorDRC_truePredictions + $PredictorDRC_falsePredictions )')

        #FRFCFS
        add_counter(results, 'frfcfs_rbhitrate', '$FRFCFS_rb_hits / ( $FRFCFS_rb_hits + $FRFCFS_rb_miss )')

        add_counter(results, 'ipc0', '$sandy0_instrs / $sandy0_cycles')
        add_counter(results, 'ipc1', '$sandy1_instrs / $sandy1_cycles')
        add_counter(results, 'ipc2', '$sandy2_instrs / $sandy2_cycles')
        add_counter(results, 'ipc3', '$sandy3_instrs / $sandy3_cycles')
        add_counter(results, 'ipc4', '$sandy4_instrs / $sandy4_cycles')
        add_counter(results, 'ipc5', '$sandy5_instrs / $sandy5_cycles')
        add_counter(results, 'ipc6', '$sandy6_instrs / $sandy6_cycles')
        add_counter(results, 'ipc7', '$sandy7_instrs / $sandy7_cycles')
        #pprint(results)

        # Write CSV file with all the data
        data_to_csv(results)

if __name__ == '__main__':
    _main()
