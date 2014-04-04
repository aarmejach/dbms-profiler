import os
import matplotlib.pyplot as plt
import numpy as np
from collections import namedtuple, defaultdict
from pprint import pprint

#Event = namedtuple('Event', 'str count prc type')
Event = namedtuple('Event', 'str count')

def get_counters():
  counters = {}
  for line in open(file_name):
    if ((not line.startswith('#!')) and
        line.startswith('#')):
      tmp = line.strip().replace('#', '').split(' ', 3)
      counter_str = (tmp[0][-4:]).lower()
      counters[counter_str] = tmp[3]
  return counters

def _parse_csv_file(file_name):
  events = {}
  for line in open(file_name):
    line = line.strip()
    if line and (not line.startswith('#')):
      #event_count, event_str, event_prc = line.split(',')
      event_count, event_str = line.split(',')
      assert(event_str.startswith('r'))
      event_str = event_str[1:].lower()
      #event_type = None
      #if ':' in event_str:
        #event_str, event_type = event_str.split(':')
      #event = Event(event_str, int(event_count), event_prc, event_type)
      event = Event(event_str, float(event_count))
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

def plot(counters, results, counter_name):
  for db in databases:
    for bench in benchmarks:
      for scale in scales:
        xs = []
        ys = []
        for qry in queries:
          key = (db, bench, scale, 'q%02d'%qry)
          tmp = results.get(key)
          xs.append(qry)
          try:
            ys.append(tmp[counter_name].count)
          except TypeError:
            ys.append(-1)
        print xs
        print ys
        fig, ax = plt.subplots()
        ax.set_ylabel(counters[counter_name])
        ax.bar(xs, ys)
        path="%s/%s/%s/%s"%(folder_figures, db, bench, scale)
        if not os.path.exists(path): os.makedirs(path)
        plt.savefig("%s/%s-%s-%s-%s.eps" % (path, counter_name, db, bench, scale))
        #fig.show()

def _main():
  global folder_figures, file_name, folder_results, databases, benchmarks, scales, queries

  # Go to profiler's base dir
  os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/..')

  # Configuration parameters
  file_name = "common/perf-counters-axle-list"
  folder_results = "results-perf/"
  folder_figures = "figures/" + folder_results
  databases = 'pgsql monetdb'.split()
  benchmarks = 'tpch'.split()
  scales = '1 100'.split()
  queries = range(1,23)

  # Get counters of interest and read results
  counters = get_counters()
  #pprint(counters)
  results = get_results()
  #pprint(results)

  # Add metrics of interest
  add_counter(counters, results, 'total_cycles', 'Total cycles', '$003c:k + $003c:u')
  add_counter(counters, results, 'total_insts', 'Total insts', '$00c0:k + $00c0:u')
  add_counter(counters, results, 'prcnt_kernel', '% Kernel cycles', '( $003c:k / $total_cycles ) * 100')
  add_counter(counters, results, 'ipc', 'IPC', '$total_insts / $total_cycles')
  #add_counter(counters, results, 'cpi', 'CPI', '1 / $ipc')
  #add_counter(counters, results, 'prcnt_misspred_branches', '% Misspredicted branches', '( $00c5 / $00c4 ) * 100')
  #add_counter(counters, results, 'prcnt_misspred_cond_branches', '% Misspredicted conditional branches', '( $01c5 / $01c4 ) * 100')
  #add_counter(counters, results, '', '', '')

  # Plot metric of interest
  plot(counters, results, 'prcnt_kernel')
  plot(counters, results, 'ipc')
  #plot(counters, results, 'cpi')
  #plot(counters, results, 'prcnt_misspred_branches')
  #plot(counters, results, 'prcnt_misspred_cond_branches')

if __name__ == '__main__':
  _main()
