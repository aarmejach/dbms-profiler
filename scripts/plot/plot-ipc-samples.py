#!/usr/bin/env python

import os,sys,string,re
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from pprint import pprint

def add_results_perf(dir):
    a = re.compile("ipc-samples-[a-z]*\.csv")
    results = {}
    for root, sfs, fs in os.walk(dir):
        for f in fs:
            if a.match(f):
                tmp = root.split('/')
                results[tuple(tmp[3:])] = mp.mlab.csv2rec(os.path.join(root,f),delimiter=',')
    return results

def add_results_zsim(dir):
    results = {}
    for root, sfs, fs in os.walk(dir):
        for f in fs:
            if "zsim.h5.csv" in f:
                tmp = f.split('_')[0:3]
                tmp[1] = "q%02d" % int(tmp[1])
                tmp[1], tmp[2] = tmp[2], tmp[1]
                results[tuple(tmp[:])] = mp.mlab.csv2rec(os.path.join(root,f),delimiter=',')
    return results

def plot_lines_instr(results_perf, results_zsim):
    for key in results_perf:
        if not key in results_zsim:
            print "WARNING: key in perf but not in zsim" + str(key)
            continue

        fig = plt.figure(figsize=(15,4))
        ax = fig.add_subplot(111)

        #pprint(results_perf)
        #names_perf = results_perf[key].dtype.names
        #names_zsim = results_zsim[key].dtype.names

        # Line for perf
        #scaleFactor = len(results_perf[key]['absolute_time']) / 10000
        scaleFactor = 100
        x = results_perf[key]['absolute_instructions'][::scaleFactor]
        y = results_perf[key]['ipc'][::scaleFactor]
        line_perf = mp.lines.Line2D(x, y, linewidth=1, color='r', label='Real')

        # Line for zsim
        #scaleFactor = len(results_zsim[key]['absolute_time']) / 1000
        scaleFactor = 100
        x = results_zsim[key]['absolute_instructions'][::scaleFactor]
        y = results_zsim[key]['ipc'][::scaleFactor]
        line_zsim = mp.lines.Line2D(x, y, linewidth=1, color='b', label='Zsim')

        ax.add_line(line_perf)
        ax.add_line(line_zsim)
        ax.set_ylim(0,max(y)+0.2)
        ax.set_xlim(0,x[-1])
        ax.grid(b=None, which='major', axis='both')
        ax.set_xlabel('Instructions (Billions)', fontsize=16)
        ax.set_ylabel('IPC', fontsize=16)
        ax.legend()

        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

        if not os.path.exists(fig_dir): os.makedirs(fig_dir)
        plt.savefig("%s/%s-%s.eps" % (fig_dir, 'ipc-samples-instr', '-'.join(key)))
        #plt.show()

def plot_lines_time(results_perf, results_zsim):
    for key in results_perf:
        if not key in results_zsim:
            print "WARNING: key in perf but not in zsim" + str(key)
            continue

        fig = plt.figure(figsize=(15,4))
        ax = fig.add_subplot(111)

        #pprint(results_perf)
        #names_perf = results_perf[key].dtype.names
        #names_zsim = results_zsim[key].dtype.names

        # Line for perf
        scaleFactor = len(results_perf[key]['absolute_time']) / 10000
        x = results_perf[key]['absolute_time'][::scaleFactor]
        y = results_perf[key]['ipc'][::scaleFactor]
        line_perf = mp.lines.Line2D(x, y, linewidth=1, color='r', label='Real')

        # Line for zsim
        scaleFactor = len(results_zsim[key]['absolute_time']) / 10000
        x = results_zsim[key]['absolute_time'][::scaleFactor]
        y = results_zsim[key]['ipc'][::scaleFactor]
        line_zsim = mp.lines.Line2D(x, y, linewidth=1, color='b', label='Zsim')

        ax.add_line(line_perf)
        ax.add_line(line_zsim)
        ax.set_ylim(0,max(y)+0.2)
        ax.set_xlim(0,x[-1])
        ax.grid(b=None, which='major', axis='both')
        ax.set_xlabel('Time (s)', fontsize=16)
        ax.set_ylabel('IPC', fontsize=16)
        ax.legend()

        if not os.path.exists(fig_dir): os.makedirs(fig_dir)
        plt.savefig("%s/%s-%s.eps" % (fig_dir, 'ipc-samples-time', '-'.join(key)))
        #plt.show()

def _main():
    # Go to profiler's base dir
    os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/../..')

    # Configuration parameters
    perf_dir = "results-axle/perf/"
    zsim_dir = "results-zsim/tests_zsim_baseline/"
    global fig_dir
    fig_dir = "figures/validation/"

    # Gather results
    results_perf = add_results_perf(perf_dir)
    results_zsim = add_results_zsim(zsim_dir)

    #pprint(results_perf)
    #pprint(results_zsim)

    plot_lines_time(results_perf, results_zsim)
    plot_lines_instr(results_perf, results_zsim)

if __name__ == '__main__':
    _main()
