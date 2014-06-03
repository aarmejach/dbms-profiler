#!/usr/bin/env python

import os,sys,string
from os.path import join, getsize
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from collections import namedtuple, defaultdict
from pprint import pprint
from plotlib import *

#Event = namedtuple('Event', 'str count prc type')
Event = namedtuple('Event', 'str count')

# Populates 'counters' dictionary
# e.g.,
#{'00c5': 'Conditional branch instructions mispredicted',
# '0151': 'Number of lines brought into L1D cache. Replacements. L1_DCM / L2 accesses'}
def get_counters():
  counters = {}
  for line in open(file_name):
    if ((not line.startswith('#!')) and
        line.startswith('#r')):
      tmp = line.strip().replace('#', '').split(' ', 3)
      counter_str = tmp[0].lower().lstrip("r").lstrip("0") # counter number without initial 'r' and '0's
      counters[counter_str] = tmp[3] # key (counter number) : value (counter description)
  return counters

def _parse_csv_file(file_name):
  events = {}
  for line in open(file_name):
    line = line.strip()
    if line and (not line.startswith('#')):
      #event_count, event_str, event_prc = line.split(',')
      event_count, event_str = line.split(',')
      assert(event_str.startswith('raw'))
      event_str = event_str[6:].lower() # skips 'raw 0x' from the event str
      if event_str in events: # handle user and kernel counters
          event_str_new = event_str + ":u" #assumes exisintg is user
          events[event_str_new] = events.pop(event_str)
          # change str within Event
          events[event_str_new] = events[event_str_new]._replace(str = event_str_new)
          event_str = event_str + ":k"
      #event_type = None
      #if ':' in event_str:
        #event_str, event_type = event_str.split(':')
      #event = Event(event_str, int(event_count), event_prc, event_type)
      try:
          count = float(event_count)
      except ValueError:
          count = 1
          print "Warn: " + event_str + " not counted in " + file_name
      event = Event(event_str, count)
      events[event_str] = event
  return events

def get_results():
  results = {}
  for root, sfs, fs in os.walk(folder_results):
    for f in fs:
      if f == 'perf-stats.csv':
        tmp = root.split('/')
        results[tuple(tmp[1:])] = _parse_csv_file(os.path.join(root, f))
  return results

def _eval_term(d, term):
  t = term.split()
  r = {}
  for i in t:
    if i[0] == '$':
      r[i] = d[i[1:]].count
  for k in r:
    term = term.replace(k, str(r[k]))

  count = eval(term)
  return count

def add_counter(counters, results, counter_name, counter_label, counter_term):
  for k in results:
    v = results[k]
    try:
      count = _eval_term(v, counter_term)
    except KeyError:
      count = -1
    v[counter_name] = Event(counter_name, count)
  counters[counter_name] = counter_label

def data_to_csv(bench, xtick_labels, column_names, columns_data):
    assert(len(column_names)==len(columns_data))
    res = []

    # first row of the file is column names, need two leading empty spaces (workload, bench)
    column_names.insert(0, 'query')
    column_names.insert(0, 'workload')
    res.append(column_names)

    # Create rest of the rows, 1 elem of xticks and 1st of each data list.
    for x in xtick_labels:
        row = []
        row.append(bench)
        row.append(x)
        for elem in columns_data:
            assert(len(elem)==len(xtick_labels))
            row.append(elem[xtick_labels.index(x)])
        res.append(row)
    return res

def write_csv(path, data):
    import csv
    with open(path, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(data)

def plot_bar(counters, results, counter_name):
  for db in databases:
    for bench in benchmarks:
      for scale in scales:
        print "Processing " + counter_name + " " + db + " " + bench + " " + scale

        # reset the configuration to the default
        config='scripts/gen_results_default_config.py'
        # TODO For each directory set the local configuration

        xtick_labels = []
        d = []
        columns_data = []
        # TODO Change to: for dir in db/bench/scale
        for qry in queries:
          qstr = 'q%02d'%int(qry)
          key = ('perf', db, bench, scale, qstr)
          tmp = results.get(key)
          xtick_labels.append(qry)
          try:
            d.append(tmp[counter_name].count)
          except TypeError:
            print "\t Skipping query " + str(qry)
            xtick_labels.pop()
        column_names = [counter_name]
        column_ids_errdata = []
        columns_data.append(d)
        #fig, ax = plt.subplots()
        #ind = np.arange(len(xs))
        #width = .75
        #ax.bar(ind, ys, width)
        #ax.set_ylabel(counters[counter_name])
        #ax.set_title(counters[counter_name])
        #ax.set_xticks(ind+width/2.)
        #ax.set_xticklabels(xs)
        ylim = None
        # TODO ylim logic
        plt = mk_barchart(
                config,
                counter_name,
                xticks=xtick_labels,
                legend=column_names,
                data=columns_data,
                data_err = column_ids_errdata,
                ylim = ylim,
                )
        csv_data = data_to_csv(bench, xtick_labels, column_names, columns_data)
        path="%s/%s/%s/%s"%(folder_figures, db, bench, scale)
        if not os.path.exists(path): os.makedirs(path)
        write_csv("%s/%s-%s-%s-%s.csv" % (path, counter_name, db, bench, scale), csv_data)
        plt.savefig("%s/%s-%s-%s-%s.eps" % (path, counter_name, db, bench, scale))
        #plt.show()

def plot_stacked(counters, results, name, *counter_name):
  for db in databases:
    for bench in benchmarks:
      for scale in scales:
        print "Processing " + name + " " + db + " " + bench + " " + scale

        # reset the configuration to the default
        config ='scripts/gen_results_default_config.py'
        # TODO For each directory set the local configuration

        # benchmark names
        xtick_labels = [elem for elem in queries]

        # get data - list of lists
        columns_data = []
        for elem in counter_name:
            d = []
            for qry in queries:
                qstr = 'q%02d'%(int(qry))
                key = ('perf', db, bench, scale, qstr)
                tmp = results.get(key)
                try:
                    d.append(tmp[elem].count)
                except TypeError:
                    d.append(-1)
            columns_data.append(d)

        column_names = list(counter_name)
        column_ids_errdata = []
        xticks_per_bar_labels = None
        ylim = None
        # TODO ylim logic
        plt = mk_clusterstacked(
                              config,
                              name,
                              xticks=xtick_labels,
                              legend=column_names,
                              data=columns_data,
                              data_err = column_ids_errdata,
                              ylim = ylim,
                              xticks_per_bar=xticks_per_bar_labels,
                              )
        csv_data = data_to_csv(bench, xtick_labels, column_names, columns_data)
        path="%s/%s/%s/%s"%(folder_figures, db, bench, scale)
        if not os.path.exists(path): os.makedirs(path)
        write_csv("%s/%s-%s-%s-%s.csv" % (path, name, db, bench, scale), csv_data)
        plt.savefig("%s/%s-%s-%s-%s.eps" % (path, name, db, bench, scale))
        #plt.show()

def _main():
  global folder_figures, file_name, folder_results, databases, benchmarks, scales, queries

  # Go to profiler's base dir
  os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/..')

  # Configuration parameters
  file_name = "common/perf-counters-axle-list"
  folder_results = "results-axle/perf/"
  folder_figures = "figures/perf/"
  #databases = 'pgsql monetdb'.split()
  #benchmarks = 'tpch dbt3'.split()
  #scales = '1 100'.split()
  databases = 'pgsql'.split()
  benchmarks = 'tpch'.split()
  scales = '1'.split()
  #queries = range(1,23)
  queries = "2 3 4 5 6 7 9 10 12 13 14 15 16 17 18 19 21 22".split()
  #queries = "2 4 5 6 11 14 16 17 20 22".split()

  # Get counters of interest and read results
  counters = get_counters()

  results = get_results()

  # General metrics of interest
  add_counter(counters, results, 'total_cycles', 'Total cycles', '$3c:k + $3c:u')
  add_counter(counters, results, 'total_insts', 'Total insts', '$c0:k + $c0:u')
  add_counter(counters, results, 'prcnt_kernel_cycles',
                '% Kernel cycles', '( $3c:k / $total_cycles ) * 100')
  add_counter(counters, results, 'ipc', 'IPC', '$total_insts / $total_cycles')
  #add_counter(counters, results, 'cpi', 'CPI', '1 / $ipc')

  # Caches
  add_counter(counters, results, 'l1i_mpki', 'L1I MPKI', '( 1000 * $280 ) / $total_insts')
  add_counter(counters, results, 'l1d_mpki', 'L1D MPKI', '( 1000 * $151 ) / $total_insts')
  add_counter(counters, results, 'l2_mpki' , 'L2 MPKI' , '( 1000 * $4f2e ) / $total_insts')
  add_counter(counters, results, 'l2i_mpki', 'L2I MPKI', '( 1000 * $2024 ) / $total_insts')
  add_counter(counters, results, 'l2d_mpki', 'L2D MPKI', '$l2_mpki - $l2i_mpki')
  add_counter(counters, results, 'l3_mpki' , 'L3 MPKI' , '( 1000 * $412e ) / $total_insts')

  # Branch Predictor
  add_counter(counters, results, 'prcnt_misspred_branches',
                '% Misspredicted branches', '( $c5 / $c4 ) * 100')
  #add_counter(counters, results, 'prcnt_misspred_cond_branches',
                #'% Misspredicted conditional branches', '( $1c5 / $1c4 ) * 100')

  # Stalls General
  add_counter(counters, results, 'total_stall_compute',
                'Total cycles calculated by stall compute counters',
                '$15301c2:u + $15301c2:k + $1d301c2:u + ( $3c:k - $15301c2:k )')
  add_counter(counters, results, 'prcnt_cycles_compute_user',
                '% Computational cycles user-level', '( $15301c2:u / $total_stall_compute ) * 100')
  add_counter(counters, results, 'prcnt_cycles_compute_kernel',
                '% Computational cycles kernel-level', '( $15301c2:k / $total_stall_compute ) * 100')
  add_counter(counters, results, 'prcnt_cycles_stalled_user',
                '% Stalled cycles user-level', '( $1d301c2:u / $total_stall_compute ) * 100')
  add_counter(counters, results, 'prcnt_cycles_stalled_kernel',
      '% Stalled cycles kernel-level', '( ( $3c:k - $15301c2:k ) / $total_stall_compute ) * 100') # XXX

  # Stalls Memory
  add_counter(counters, results, 'prcnt_cycles_dtlb_walk',
                '% DTLB load miss walk cycles', '( $408 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_itlb_walk',
                '% ITLB walk cycles', '( $485 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_pending_l1d',
                '% cycles with a pending L1D load miss', '( $2a3 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_pending_l2',
                '% cycles with a pending L2 load miss', '( $1a3 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_pending_offcore_llcmem',
                '% cycles with an outstanding L2 miss request (i or d)', '( $1530860 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_pending_l2i',
                '% cycles instruction stalls on l2', '( ( ( 6 / 40 ) * ( $1024 / $2024 * $1530260 ) ) / $total_cycles ) * 100')

  # Stalls core
  add_counter(counters, results, 'prcnt_cycles_empty_freelist',
                '% cycles stalled free list empty', '( $c5b / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_full_pregisters',
                '% cycles stalled control structures full for physical registers',
                '( $f5b / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_full_branchorderbuffer',
                '% cycles allocator stalled full branch order buffer',
                '( $405b / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_full_oooresources',
                '% cycles stalled full OOO resources', '( $4f5b / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_iq',
                #'% cycles stalled full instructuion queue - no issue', '( $487 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_full_lb',
                '% cycles stalled full load buffers', '( $2a2 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_full_rs',
                '% cycles stalled full reservation stations', '( $4a2 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_full_sb',
                '% cycles stalled full store buffers', '( $8a2 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_full_rob',
                '% cycles stalled full reorder buffer', '( $10a2 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_writting_fpuword',
                '% cycles stalled writting FPU control word', '( $20a2 / $total_cycles ) * 100')

  # MLP
  add_counter(counters, results, 'mlp', 'Memory level parallelism', '$530160 / $1530160')

  # Template
  #add_counter(counters, results, '', '', '')


  # Plot metric of interest -- bars
  plot_bar(counters, results, 'prcnt_kernel_cycles')
  plot_bar(counters, results, 'ipc')
  plot_bar(counters, results, 'l1i_mpki')
  plot_bar(counters, results, 'l1d_mpki')
  plot_bar(counters, results, 'l2_mpki')
  plot_bar(counters, results, 'l2i_mpki')
  plot_bar(counters, results, 'l2d_mpki')
  plot_bar(counters, results, 'l3_mpki')
  plot_bar(counters, results, 'prcnt_misspred_branches')
  plot_bar(counters, results, 'mlp')

  # Plot metric of interest -- barstacks
  plot_stacked(counters, results, 'compute-stall-breakdown',
                'prcnt_cycles_compute_user', 'prcnt_cycles_compute_kernel',
                'prcnt_cycles_stalled_user', 'prcnt_cycles_stalled_kernel')

  plot_stacked(counters, results, 'memory-stalls-breakdown',
                'prcnt_cycles_dtlb_walk', 'prcnt_cycles_itlb_walk',
                'prcnt_cycles_pending_l1d', 'prcnt_cycles_pending_l2')

  plot_stacked(counters, results, 'core-stalls-breakdown',
                'prcnt_cycles_empty_freelist', 'prcnt_cycles_full_pregisters',
                'prcnt_cycles_full_branchorderbuffer', 'prcnt_cycles_full_oooresources',
                'prcnt_cycles_full_lb',
                'prcnt_cycles_full_rs', 'prcnt_cycles_full_sb',
                'prcnt_cycles_full_rob', 'prcnt_cycles_writting_fpuword')

if __name__ == '__main__':
  _main()
