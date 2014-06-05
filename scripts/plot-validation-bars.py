#!/usr/bin/env python

import os,sys,string,re
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from pprint import pprint
import h5py
from plotlib import *

def plot_bar(name, liststats, results_perf, results_zsim):
    
    # reset the configuration to the default
    config='scripts/gen_results_default_config.py'
    # TODO For each directory set the local configuration

    # Ensure that results arrays have the same number of entries
    rec = mp.mlab.rec_join(['bench', 'query', 'scale', 'db'], results_perf, results_zsim)

    xtick_labels = rec['query']
    column_names = []
    columns = []
    column_ids_errdata = []

    for stat in liststats:
        column_names.append(stat+' real')
        column_names.append(stat+' simulated')
        columns.append(rec[stat+'1'])
        columns.append(rec[stat+'2'])

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
    os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/..')

    # Data folters
    perf_file = "figures/perf-data.csv"
    zsim_file = "figures/zsim-data.csv"
    fig_dir = "figures/validation/"

    # Load CSV into a numpy recarray
    perf_data = mp.mlab.csv2rec(perf_file, delimiter=',')
    zsim_data = mp.mlab.csv2rec(zsim_file, delimiter=',')

    # Dict of bar charts to plot
    charts = {
        'ipc'       : ['ipc'],
        'l1d_mpki'  : ['l1d_mpki'],
        'l1i_mpki'  : ['l1i_mpki'],
        'l2_mpki'   : ['l2_mpki'],
        'l3_mpki'   : ['l3_mpki'],
        'cache_stats'   : ['l2_mpki', 'l3_mpki']
        }

    for key in charts:
        plot_bar(key, charts[key], perf_data, zsim_data)

if __name__ == '__main__':
    _main()

