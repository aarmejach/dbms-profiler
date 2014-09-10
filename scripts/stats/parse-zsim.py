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

    # Get the single dataset in the file
    try:
        dset = f["stats"]["root"]
    except ValueError:
        print "ERROR reading file: " + file
        for key in zsimstatsdict:
            statlist = zsimstatsdict[key]
            for stat in statlist:
                res[key+"_"+stat] = -1
        return res

    for key in zsimstatsdict:
        statlist = zsimstatsdict[key]
        for stat in statlist:
            res[key+"_"+stat] = float(np.sum(dset[-1][key][stat]))

    return res


def toFloat(a):
    for i in "W mA*t".split():
        if a.endswith(i):
            a=a[:-len(i)]
    return float(a)


def parse_nvmainFile(file):
    res = {}

    array = open(file).read().strip().split('\n')

    for key in nvmainstatsdict:
        statslist = nvmainstatsdict[key]
        for stat in statslist:
            res[key+"_"+stat] = sum(toFloat(i.split()[-1]) for i in array if (key in i) and (stat in i))

    return res


def get_results(d):
    results = {}
    for root, sfs, fs in os.walk(folder_results + d):
        for f in fs:
            tmp = f.split('_')[0:3]
            # change query format
            tmp[1] = "%02d" % int(tmp[1])

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

    # Add rows one by one
    for key in sorted(results):
        row = []
        row.append(key[0]) # bench
        row.append(key[1])# query
        row.append(key[2]) # scale

        # Get event dict and iterate over sorted keys
        dict = results.get(key)
        for k in sorted(dict):
            row.append(dict[k])
        data.append(row)

    with open(csv_file, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(data)


def _main():
    global zsimstatsdict, nvmainstatsdict, csv_file, folder_results

    # Go to profiler's base dir
    os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/../..')

    # Configuration parameters
    #file_name = "common/perf-counters-axle-list"
    folder_results = os.getcwd() + '/' + "results-zsim/"
    directories=[d for d in os.listdir(folder_results) if os.path.isdir(folder_results + d)]

    for d in directories:
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
        nvmainstatsdict = {
              'DRC'    : ['totalPower', 'rb_hits', 'rb_miss', 'drc_hits', 'drc_miss'],
              'FRFCFS' : ['totalPower', 'rb_hits', 'rb_miss'],
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

        #FRFCFS
        add_counter(results, 'frfcfs_rbhitrate', '$FRFCFS_rb_hits / ( $FRFCFS_rb_hits + $FRFCFS_rb_miss )')

        #pprint(results)

        # Write CSV file with all the data
        data_to_csv(results)

if __name__ == '__main__':
    _main()
