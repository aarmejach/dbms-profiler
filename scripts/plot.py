import os
import matplotlib.pyplot as plt
import numpy as np
from collections import namedtuple, defaultdict
from pprint import pprint

#Event = namedtuple('Event', 'str count prc type')
Event = namedtuple('Event', 'str count')

def get_counters(file_name):
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

def get_results(folder_name):
  results = {}
  for root, sfs, fs in os.walk(folder_name):
    for f in fs:
      if f == 'perf-stats.csv':
        tmp = root.split('/')
        assert(tmp[0] == '..')
        assert(tmp[1] == 'results-perf')
        results[tuple(tmp[2:])] = _parse_csv_file(os.path.join(root, f))
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

def add_counter(results, counters, counter_name, counter_label, counter_term):
  for k in results:
    v = results[k]
    try:
      count = _eval_term(v, counter_term)
    except KeyError:
      count = -1
    v[counter_name] = Event(counter_name, count)
  counters[counter_name] = counter_label

def plot(results, counters, counter_name):
  for db in 'pgsql monetdb'.split():
    for bench in 'tpch'.split():
      for scale in '1'.split():
        xs = []
        ys = []
        for qry in range(1,23):
          key = (db, bench, scale, 'q%02d'%qry)
          tmp = results.get(key)
          xs.append(qry)
          ys.append(tmp[counter_name].count)
        print xs
        print ys
        plt.ylabel(counters[counter_name])
        plt.bar(xs, ys)
        path="%s/%s/%s/%s"%(folder_output, db, bench, scale)
        if not os.path.exists(path): os.makedirs(path)
        plt.savefig("%s/%s.eps" % (path, counter_name))

def _main():
  file_name = "../common/perf-counters-axle-list"
  folder_name = "../results-perf"
  global folder_output
  folder_output = "../figures"

  counters = get_counters(file_name)
  #pprint(counters)
  results = get_results(folder_name)
  #pprint(results)

  # Add metrics of interest
  add_counter(results, counters, 'ipc', 'IPC', '( $00c0:k + $00c0:u ) / ( $003c:k + $003c:u )')
  #add_counter(results, counters, 'cpi', 'CPI', '1 / $ipc')

  # Plot metric of interest
  plot(results, counters, 'ipc')
  #plot(results, counters, 'cpi')

if __name__ == '__main__':
  _main()
