#!/usr/bin/env python

import os,sys,string,re
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from pprint import pprint

def add_results(dir):
    a = re.compile("ipc-samples-[a-z]*\.csv")
    results = {}
    for root, sfs, fs in os.walk(dir):
        #print root
        for f in fs:
            #print f
            if a.match(f):
                tmp = root.split('/')
                results[tuple(tmp[2:])] = mp.mlab.csv2rec(os.path.join(root,f),delimiter=',')
    return results

def plot_lines(results_perf, results_zsim):
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
        x = results_perf[key]['absolute_time']
        y = results_perf[key]['ipc']
        line_perf = mp.lines.Line2D(x, y, linewidth=1, color='r', label='Real')

        # Line for zsim
        x = results_zsim[key]['absolute_time']
        y = results_zsim[key]['ipc']
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
        plt.savefig("%s/%s-%s.eps" % (fig_dir, 'ipc-samples', '-'.join(key)))
        #plt.show()

def _main():
    # Go to profiler's base dir
    os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/..')

    # Configuration parameters
    perf_dir = "results-axle/perf/"
    zsim_dir = "results-axle/zsim/"
    global fig_dir
    fig_dir = "figures/validation/"

    # Gather results
    results_perf = add_results(perf_dir)
    results_zsim = add_results(zsim_dir)

    #pprint(results_perf)
    #pprint(results_zsim)

    plot_lines(results_perf, results_zsim)

if __name__ == '__main__':
    _main()
