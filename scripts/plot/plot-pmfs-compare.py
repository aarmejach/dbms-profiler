#!/usr/bin/env python

import os,sys,string,re
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from pprint import pprint
import h5py
from plotlib import *

def plot_bar(name, liststats, results_all):

    # reset the configuration to the default
    config='scripts/gen_results_default_config.py'
    # TODO For each directory set the local configuration

    # Ensure that results arrays have the same number of entries
    #rec = mp.mlab.rec_join(['bench', 'query', 'scale', 'db'], results_all.pop(0) ,results_all.pop(0))

    xtick_labels = results_all.itervalues().next()['query']
    column_names = []
    columns = []
    column_ids_errdata = []

    for stat in liststats:
        for k,v in results_all.iteritems():
            d = os.path.splitext(os.path.basename(k))[0]
            d = d.split("-")[-1]
            column_names.append(stat+' '+d)
            columns.append(v[stat])

    # TODO ylim logic
    plt = mk_barchart(
            config,
            name = name,
            xticks=xtick_labels,
            legend=column_names,
            data=columns,
            data_err = column_ids_errdata,
            ylim = None,
            )
    if not os.path.exists(fig_dir): os.makedirs(fig_dir)
    plt.savefig("%s/%s.eps" % (fig_dir, name))
    #plt.show()

def _main():
    global fig_dir

    # Go to profiler's base dir
    os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/../..')

    # Data folters
    folder_results = "results/"
    datafiles=[f for f in os.listdir(folder_results) if f.startswith("perf-data-pmfs-")]
    fig_dir = "figures/pmfs/comparison/"

    # Load CSV into a list of numpy recarray
    all_data = {}
    for f in datafiles:
        all_data[f] = mp.mlab.csv2rec(folder_results + f, delimiter=',')

    # Dict of bar charts to plot
    charts = {
        'exectime'  : ['total_cycles'],
        'instructions' : ['total_insts'],
        'prcnt_kernel_time' : ['prcnt_kernel_cycles']
        #'ipc'       : ['ipc'],
        #'l1d_mpki'  : ['l1d_mpki'],
        #'l1i_mpki'  : ['l1i_mpki'],
        #'l2_mpki'   : ['l2_mpki'],
        #'l3_mpki'   : ['l3_mpki'],
        #'cache_stats'   : ['l2_mpki', 'l3_mpki']
        }

    for key in charts:
        plot_bar(key, charts[key], all_data)

if __name__ == '__main__':
    _main()

