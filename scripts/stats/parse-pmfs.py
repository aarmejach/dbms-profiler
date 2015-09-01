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
      #counter_str = tmp[0].lower().lstrip("r").lstrip("0") # counter number without initial 'r' and '0's
      counter_str = tmp[0].lower().lstrip("r") # counter number without initial 'r', keep 0's
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
      assert(event_str.startswith('r'))
      event_str = event_str[1:].lower() # skips 'r' from the event str
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

def add_counter(counters, results, counter_name, counter_label, counter_term, no_negative=False):
  for k in results:
    v = results[k]
    try:
      count = _eval_term(v, counter_term)
      if no_negative and count < 0:
          count = 0
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
  os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/../..')

  # Configuration parameters
  file_name = "common/perf-counters-pmfs-list"
  counters = get_counters()

  folder_results = "results-pmfs/"
  directories=[d for d in os.listdir(folder_results) if os.path.isdir(folder_results + d)]

  for d in directories:
    folder_results = "results-pmfs/" + d
    csv_file = "results/perf-data-pmfs-" + d + ".csv"

    # Get counters of interest and read results
    results = get_results()

    # General metrics of interest
    add_counter(counters, results, 'total_cycles', 'Total cycles', '$0076:k + $0076:u')
    add_counter(counters, results, 'total_insts', 'Total insts', '$00c0:k + $00c0:u')
    add_counter(counters, results, 'prcnt_kernel_cycles',
                '% Kernel cycles', '( $0076:k / $total_cycles ) * 100')
    add_counter(counters, results, 'ipc', 'IPC', '$total_insts / $total_cycles')
    #add_counter(counters, results, 'cpi', 'CPI', '1 / $ipc')

    # Stalls General
    add_counter(counters, results, 'total_stall_compute',
                'Total cycles calculated by stall compute counters',
                '$total_cycles')
    add_counter(counters, results, 'prcnt_cycles_compute_user',
            '% Computational cycles user-level', '( ( $0076:u - $00d1:u ) / $total_stall_compute ) * 100')
    add_counter(counters, results, 'prcnt_cycles_compute_kernel',
            '% Computational cycles kernel-level', '( ( $0076:k - $00d1:k ) / $total_stall_compute ) * 100')
    add_counter(counters, results, 'prcnt_cycles_stalled_user',
                '% Stalled cycles user-level', '( $00d1:u / $total_stall_compute ) * 100')
    add_counter(counters, results, 'prcnt_cycles_stalled_kernel',
      '% Stalled cycles kernel-level', '( $00d1:k / $total_stall_compute ) * 100')

    # Stalls General
    #add_counter(counters, results, 'total_stall_compute',
                #'Total cycles calculated by stall compute counters',
                #'$15301c2:u + $15301c2:k + $1d301c2:u + ( $3c:k - $15301c2:k )')
    #add_counter(counters, results, 'prcnt_cycles_compute_user',
            #'% Computational cycles user-level', '( ( $0076:u - $00d1:u ) / $total_stall_compute ) * 100')
    #add_counter(counters, results, 'prcnt_cycles_compute_kernel',
                #'% Computational cycles kernel-level', '( $15301c2:k / $total_stall_compute ) * 100')
    #add_counter(counters, results, 'prcnt_cycles_stalled_user',
                #'% Stalled cycles user-level', '( $1d301c2:u / $total_stall_compute ) * 100')
    #add_counter(counters, results, 'prcnt_cycles_stalled_kernel',
      #'% Stalled cycles kernel-level', '( ( $3c:k - $15301c2:k ) / $total_stall_compute ) * 100') # XXX


    # Template
    #add_counter(counters, results, '', '', '')

    # Write CSV file with all the data
    data_to_csv(results)

if __name__ == '__main__':
  _main()
