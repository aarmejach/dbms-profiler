import os,sys
import matplotlib.pyplot as plt
import numpy as np
from collections import namedtuple, defaultdict
from pprint import pprint

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

def plot_bar(counters, results, counter_name):
  for db in databases:
    for bench in benchmarks:
      for scale in scales:
        print "Processing " + counter_name + " " + db + " " + bench + " " + scale
        xs = []
        ys = []
        for qry in queries:
          qstr = 'q%02d'%qry
          key = ('perf', db, bench, scale, qstr)
          tmp = results.get(key)
          xs.append(qry)
          try:
            ys.append(tmp[counter_name].count)
          except TypeError:
            print "\t Skipping query " + str(qry)
            xs.pop()
        fig, ax = plt.subplots()
        ind = np.arange(len(xs))
        width = .75
        ax.bar(ind, ys, width)
        ax.set_ylabel(counters[counter_name])
        ax.set_title(counters[counter_name])
        ax.set_xticks(ind+width/2.)
        ax.set_xticklabels(xs)
        path="%s/%s/%s/%s"%(folder_figures, db, bench, scale)
        if not os.path.exists(path): os.makedirs(path)
        plt.savefig("%s/%s-%s-%s-%s.eps" % (path, counter_name, db, bench, scale))
        #plt.show()

def _main():
  global folder_figures, file_name, folder_results, databases, benchmarks, scales, queries

  # Go to profiler's base dir
  os.chdir(os.path.dirname(os.path.realpath(__file__))+ '/..')

  # Configuration parameters
  file_name = "common/perf-counters-axle-list"
  folder_results = "results-axle/"
  folder_figures = "figures/" + folder_results
  #databases = 'pgsql monetdb'.split()
  #benchmarks = 'tpch dbt3'.split()
  #scales = '1 100'.split()
  databases = 'pgsql'.split()
  benchmarks = 'tpch'.split()
  scales = '1'.split()
  queries = range(1,23)

  # Get counters of interest and read results
  counters = get_counters()

  results = get_results()

  # Add metrics of interest
  add_counter(counters, results, 'total_cycles', 'Total cycles', '$3c:k + $3c:u')
  add_counter(counters, results, 'total_insts', 'Total insts', '$c0:k + $c0:u')
  add_counter(counters, results, 'prcnt_kernel', '% Kernel cycles', '( $3c:k / $total_cycles ) * 100')
  add_counter(counters, results, 'ipc', 'IPC', '$total_insts / $total_cycles')
  add_counter(counters, results, 'l1i_mpki', 'L1I MPKI', '( 1000 * $280 ) / $total_insts')
  add_counter(counters, results, 'l1d_mpki', 'L1D MPKI', '( 1000 * $151 ) / $total_insts')
  #add_counter(counters, results, 'l2_mpki', 'L2 MPKI', '( 1000 * $4f2e ) / $total_insts')
  #add_counter(counters, results, 'l2i_mpki', 'L2I MPKI', '( 1000 * $2024 ) / $total_insts')
  #add_counter(counters, results, 'l2d_mpki', 'L2D MPKI', '$l2_mpki - $l2i_mpki')
  #add_counter(counters, results, 'l3_mpki', 'L3 MPKI', '( 1000 * $412e ) / $total_insts')
  #add_counter(counters, results, 'cpi', 'CPI', '1 / $ipc')
  #add_counter(counters, results, 'prcnt_misspred_branches', '% Misspredicted branches', '( $00c5 / $00c4 ) * 100')
  #add_counter(counters, results, 'prcnt_misspred_cond_branches', '% Misspredicted conditional branches', '( $01c5 / $01c4 ) * 100')
  #add_counter(counters, results, '', '', '')

  # Plot metric of interest -- bars
  plot_bar(counters, results, 'prcnt_kernel')
  plot_bar(counters, results, 'ipc')
  plot_bar(counters, results, 'l1i_mpki')
  plot_bar(counters, results, 'l1d_mpki')
  #plot_bar(counters, results, 'l2_mpki')
  #plot_bar(counters, results, 'l2i_mpki')
  #plot_bar(counters, results, 'l2d_mpki')
  #plot_bar(counters, results, 'l3_mpki')
  #plot(counters, results, 'cpi')
  #plot(counters, results, 'prcnt_misspred_branches')
  #plot(counters, results, 'prcnt_misspred_cond_branches')

if __name__ == '__main__':
  _main()
