from __future__ import division
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import namedtuple, defaultdict
from pprint import pprint

Event = namedtuple('Event', 'str count prc type')

def get_counters(file_name):
  counters = {}
  for line in open(file_name):
    if ((not line.startswith('#!')) and
        (not line.startswith('##')) and
        line.startswith('#')):
      tmp = line.strip().replace('#', '').replace('--', '').split(' ', 2)
      counter_str = (tmp[1][:2] + tmp[0][:2]).lower()
      counters[counter_str] = tmp[2]
  return counters

def _parse_csv_file(file_name):
  events = defaultdict(list)
  for line in open(file_name):
    line = line.strip()
    if line and (not line.startswith('#')):
      event_count, event_str, event_prc = line.split(',')
      assert(event_str.startswith('r'))
      event_str = event_str[1:].lower()
      event_type = None
      if ':' in event_str:
        event_str, event_type = event_str.split(':')
      event = Event(event_str, int(event_count), event_prc, event_type)
      events[event_str].append(event)
  return dict(events)

def get_results(folder_name):
  results = {}
  for root, sfs, fs in os.walk(folder_name):
    for f in fs:
      if f == 'perf-stats.csv':
        tmp = root.split('/')
        assert(tmp[0] == '.')
        assert(tmp[1] == 'results-perf')
        results[tuple(tmp[2:])] = _parse_csv_file(os.path.join(root, f))
  return results

def _eval_term(d, term):
  t = term.split()
  r = {}
  for i in t:
    if i[0] == '$':
      r[i] = d[i[1:]][0].count
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
    v[counter_name] = [Event(counter_name, count, '100%', None)]
  counters[counter_name] = counter_label

def plot(results, counters, counter_name):
  xs = []
  ys = []
  for b in 'tpch tpcc'.split():
    for i in range(1,23):
      key = ('pgsql', 'tpch', '1', 'q%02d'%i)
      tmp = results.get(key)
      xs.append(i)
      ys.append(tmp[counter_name][0].count)
  plt.ylabel(counters[counter_name])
  plt.bar(xs, ys)
  plt.show()


def _main():
  file_name = "./common/perf-counters-axle.sh"
  counters = get_counters(file_name)
  # pprint(counters)

  folder_name = './results-perf'
  results = get_results(folder_name)
  # pprint(results)

  add_counter(results, counters, 'c/i', 'Division', '$ff88 / $ff89 * $82d0')
  add_counter(results, counters, 'i/c', '1/Division', '1 / $c/i')

  plot(results, counters, 'ff88')

if __name__ == '__main__':
  _main()
