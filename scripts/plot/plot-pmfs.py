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

def plot_clusterstacked(data, name, *counter_name):

    # reset the configuration to the default
    config='scripts/gen_results_default_config.py'
    # TODO For each directory set the local configuration

    xtick_labels = list(set(data['bench']))
    xtick_inner_labels = data['query']
    column_names = list(counter_name)
    columns = []
    column_ids_errdata = []

    # Populate data to plot
    for counter in counter_name:
        columns.append(data[counter])

    #name = '-'.join(column_names)

    plt = mk_clusterstacked(
                      config,
                      name,
                      xticks=xtick_labels,
                      xticks_inner=xtick_inner_labels,
                      legend=column_names,
                      data=columns,
                      data_err = column_ids_errdata,
                      ylim = None,
                      xticks_per_bar=None,
                      )
    if not os.path.exists(folder_figures): os.makedirs(folder_figures)
    plt.savefig("%s/%s.eps" % (folder_figures, name))


def _main():
    global folder_figures

    # Go to profiler's base dir
    os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/../..')

    # Configuration parameters
    folder_results = "results/"
    datafiles=[f for f in os.listdir(folder_results) if f.startswith("perf-data-axle-pmfs-")]
    #data_file = "results/perf-data.csv"
    for f in datafiles:
        d = os.path.splitext(os.path.basename(f))[0]
        d = d.split("-")[-1]

        folder_figures = "figures/axle-pmfs/" + d
        results_file = "results/" + f

        # Load CSV into a numpy recarray
        data = mp.mlab.csv2rec(results_file, delimiter=',')

        # Plot metric of interest -- bars
        plot_bar(data, 'prcnt_kernel_cycles')
        plot_bar(data, 'ipc')

        # Plot metric of interest -- barstacks
        plot_stacked(data, 'compute-stall-breakdown',
                'prcnt_cycles_compute_user', 'prcnt_cycles_compute_kernel',
                'prcnt_cycles_stalled_user', 'prcnt_cycles_stalled_kernel')


if __name__ == '__main__':
  _main()
