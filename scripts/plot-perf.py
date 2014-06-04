#!/usr/bin/env python

import os,sys,string
from os.path import join, getsize
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from pprint import pprint
from plotlib import *

def plot_bar(data, *counter_name):

    # reset the configuration to the default
    config='scripts/gen_results_default_config.py'
    # TODO For each directory set the local configuration

    xtick_labels = data['query']
    column_names = list(counter_name)
    columns = []
    column_ids_errdata = []

    # Populate data to plot
    for counter in counter_name:
        columns.append(data[counter])

    name = '-'.join(column_names)

    plt = mk_barchart(
            config,
            name,
            xticks=xtick_labels,
            legend=column_names,
            data=columns,
            data_err = column_ids_errdata,
            ylim = None,
            )
    if not os.path.exists(folder_figures): os.makedirs(folder_figures)
    plt.savefig("%s/%s.eps" % (folder_figures, name))


def plot_stacked(data, name, *counter_name):

    # reset the configuration to the default
    config='scripts/gen_results_default_config.py'
    # TODO For each directory set the local configuration

    xtick_labels = data['query']
    column_names = list(counter_name)
    columns = []
    column_ids_errdata = []

    # Populate data to plot
    for counter in counter_name:
        columns.append(data[counter])

    #name = '-'.join(column_names)

    plt = mk_stacked(
                      config,
                      name,
                      xticks=xtick_labels,
                      legend=column_names,
                      data=columns,
                      data_err = column_ids_errdata,
                      ylim = None,
                      xticks_per_bar=None,
                      )
    if not os.path.exists(folder_figures): os.makedirs(folder_figures)
    plt.savefig("%s/%s.eps" % (folder_figures, name))


def _main():
    global data_file, folder_figures

    # Go to profiler's base dir
    os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/..')

    # Configuration parameters
    data_file = "figures/perf-data.csv"
    folder_figures = "figures/perf/"

    # Load CSV into a numpy recarray
    data = mp.mlab.csv2rec(data_file, delimiter=',')

    # Plot metric of interest -- bars
    plot_bar(data, 'prcnt_kernel_cycles')
    plot_bar(data, 'ipc')
    plot_bar(data, 'l1i_mpki')
    plot_bar(data, 'l1d_mpki')
    plot_bar(data, 'l2_mpki')
    plot_bar(data, 'l2i_mpki')
    plot_bar(data, 'l2d_mpki')
    plot_bar(data, 'l3_mpki')
    plot_bar(data, 'prcnt_misspred_branches')
    plot_bar(data, 'mlp')

    # Plot metric of interest -- barstacks
    plot_stacked(data, 'compute-stall-breakdown',
                'prcnt_cycles_compute_user', 'prcnt_cycles_compute_kernel',
                'prcnt_cycles_stalled_user', 'prcnt_cycles_stalled_kernel')

    plot_stacked(data, 'memory-stalls-breakdown',
                'prcnt_cycles_dtlb_walk', 'prcnt_cycles_itlb_walk',
                'prcnt_cycles_pending_l1d', 'prcnt_cycles_pending_l2')

    plot_stacked(data, 'core-stalls-breakdown',
                'prcnt_cycles_empty_freelist', 'prcnt_cycles_full_pregisters',
                'prcnt_cycles_full_branchorderbuffer', 'prcnt_cycles_full_oooresources',
                'prcnt_cycles_full_lb',
                'prcnt_cycles_full_rs', 'prcnt_cycles_full_sb',
                'prcnt_cycles_full_rob', 'prcnt_cycles_writting_fpuword')


if __name__ == '__main__':
  _main()
