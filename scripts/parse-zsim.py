#!/usr/bin/env python

import os,sys,string
from os.path import join, getsize
from collections import namedtuple, defaultdict
import numpy as np
from pprint import pprint
import csv
import h5py

def parse_h5file(file):
    error = False
    res = {}

    f = h5py.File(file, 'r')

    # Get the single dataset in the file
    dset = f["stats"]["root"]

    for key in statsdict:
        statlist = statsdict[key]
        for stat in statlist:
            res[key+"_"+stat] = float(np.sum(dset[-1][key][stat]))

    return res,error


def get_results():
    results = {}
    for root, sfs, fs in os.walk(folder_results):
        for f in fs:
            if f == 'zsim-ev.h5':
                tmp = root.split('/')
                dict,error = parse_h5file(os.path.join(root, f))
                if not error:
                    results[tuple(tmp[1:])] = dict
                else:
                    print "SKIPPING configuration " + " ".join(tmp)
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
        dict[counter_name] = count


def data_to_csv(results):
    data = []

    # First row, column names. Get first dict elem and sort event dictionary keys.
    column_names = ['bench', 'query', 'db', 'scale']
    for elem in sorted(results[results.keys()[0]]):
        column_names.append(elem)
    data.append(column_names)

    # Add rows one by one
    for key in sorted(results):
        row = []
        row.append(key[2]) # bench
        row.append(key[4]) # query
        row.append(key[1]) # db
        row.append(key[3]) # scale

        # Get event dict and iterate over sorted keys
        dict = results.get(key)
        for k in sorted(dict):
            row.append(dict[k])
        data.append(row)

    with open(csv_file, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(data)


def _main():
    global statsdict, csv_file, folder_results

    # Go to profiler's base dir
    os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/..')

    # Configuration parameters
    #file_name = "common/perf-counters-axle-list"
    folder_results = "results-axle/zsim/"
    csv_file = "figures/zsim-data.csv"

    # Define stats of interest and gather results
    statsdict = {
          'sandy' : ['instrs', 'cycles', 'mispredBranches'],
          'l1d'   : ['mGETS', 'mGETXIM', 'hGETS', 'hGETX'],
          'l1i'   : ['mGETS', 'mGETXIM', 'hGETS', 'hGETX'],
          'l2'    : ['mGETS', 'mGETXIM', 'hGETS', 'hGETX'],
          'l3'    : ['mGETS', 'mGETXIM', 'hGETS', 'hGETX'],
          'mem'   : ['rd', 'wr']
          }
    results = get_results()

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

    #pprint(results)
    
    # Write CSV file with all the data
    data_to_csv(results)

if __name__ == '__main__':
    _main()
