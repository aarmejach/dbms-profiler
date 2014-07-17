#!/usr/bin/env python

import os,sys,string
from os.path import join, getsize
from collections import namedtuple, defaultdict
from pprint import pprint
import csv

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
  error = False
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
          count = 0
          error = True
          print "Warn: " + event_str + " not counted in " + file_name
      event = Event(event_str, count)
      events[event_str] = event
  return events,error

def get_results():
  results = {}
  for root, sfs, fs in os.walk(folder_results):
    for f in fs:
      if f == 'perf-stats.csv':
        tmp = root.split('/')
        dict,error = _parse_csv_file(os.path.join(root, f))
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
      print "Warn: Keyerror " + k + "for term " + counter_term
      count = -1
    v[counter_name] = Event(counter_name, count)
  counters[counter_name] = counter_label

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
        eventdict = results.get(key)
        for k in sorted(eventdict):
            row.append(eventdict[k].count)
        data.append(row)

    with open(csv_file, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(data)

def _main():
  global csv_file, file_name, folder_results

  # Go to profiler's base dir
  os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/..')

  # Configuration parameters
  file_name = "common/perf-counters-axle-list"
  folder_results = "results-axle/perf/"
  csv_file = "figures/perf-data.csv"

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
  add_counter(counters, results, 'prcnt_cycles_pending_l1d_miss',
                '% cycles with a pending L1D load miss', '( $2a3 / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_pending_l2_miss',
                #'% cycles with a pending L2 load miss', '( $1a3 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_pending_l2d_miss',
                '% cycles with an outstanding L2 data miss request', '( $1530860 / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_pending_l2i_miss',
                '% cycles instruction stalls on l2', '( $1530260 / $total_cycles ) * 100')
                #'% cycles instruction stalls on l2', '( ( ( 6 / 40 ) * ( $1024 / $2024 * $1530260 ) ) / $total_cycles ) * 100')

  # Stalls core
  #add_counter(counters, results, 'prcnt_cycles_empty_freelist',
                #'% cycles stalled free list empty', '( $c5b / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_pregisters',
                #'% cycles stalled control structures full for physical registers',
                #'( $f5b / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_branchorderbuffer',
                #'% cycles allocator stalled full branch order buffer',
                #'( $405b / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_oooresources',
                #'% cycles stalled full OOO resources', '( $4f5b / $total_cycles ) * 100')
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

  # Write CSV file with all the data
  data_to_csv(results)

if __name__ == '__main__':
  _main()
