#!/usr/bin/env python

import os,sys,string
from os.path import join, getsize
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter
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

def mk_barchart(title, xticks, legend, data, data_err=None, ylim=None):
    assert(len(legend)==len(data))
    ind = np.arange(len(xticks))  # the x locations for the groups
    barwidth = 1.0/(len(legend)+1)       # the width of the bars

    print globals().keys()
    fig = plt.figure(figsize=figure_size)
    ax = fig.add_subplot(111)

    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlim(right=len(ind))

    rects = []
    left_empty = barwidth/2.0
    for i,d in enumerate(data):
        if data_err:
            errd = data_err[i]
        else:
            errd = None
        rects.append(ax.bar(left=left_empty+ind+i*barwidth, height=d, width=barwidth, alpha=1,
                            color=colors[i], ecolor='black', edgecolor='black', hatch=hatch_patterns[i]))

    # general formating
    ax.set_title(title, fontsize=title_fontsize)
    ax.set_xlabel(xtitle, fontsize=xtitle_fontsize)
    ax.set_ylabel(ytitle, fontsize=ytitle_fontsize)
    for item in ax.get_yticklabels():
        item.set_fontsize(ylabel_fontsize)

    # xticks possition and labels
    ax.set_xticks(ind + left_empty + (len(legend)/2.0)*barwidth)
    ax.set_xticklabels(xticks, fontsize=xlabel_fontsize)
    plt.gcf().subplots_adjust(bottom=0.2)

    leg = ax.legend([a[0] for a in rects],
          legend,
          loc=legend_loc,
          ncol=legend_ncol,
          frameon=True,
          borderaxespad=1.,
          bbox_to_anchor=bbox,
          fancybox=True,
          #prop={'size':10}, # smaller font size
          )

    for t in leg.get_texts():
        t.set_fontsize(legend_fontsize)    # the legend text fontsize
    ax.set_axisbelow(True)
    plt.gca().yaxis.grid(color='gray', linestyle='-', linewidth=0.5)
    plt.tight_layout()
    return plt

def mk_clusterstacked(title, xticks, legend, data, data_err=None, ylim=None, xticks_per_bar=None):
    assert(len(legend)==len(data))
    ind = np.arange(len(xticks))        # the x locations for the groups
    barwidth = 1.0/float(num_clustered+1)      # the width of the bars

    # create a new figure, set the figure size specified in config
    fig = plt.figure(figsize=figure_size)
    # add subplot returns an axe instance
    ax = fig.add_subplot(111)

    # set the specified ylim and xlim for the returned subplot
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlim(right=len(ind))

    # calculate bottoms for stacking
    y = np.row_stack(data)
    # this call to 'cumsum' (cumulative sum), passing in your y data,
    # is necessary to avoid having to manually order the datasets
    y_stack = np.cumsum(y, axis=0)

    # add bars to be printed
    rects = []
    left_empty = barwidth/2.0
    for idx,d in enumerate(data):
        for i in xrange(num_clustered):
            #this gives every n'th element given a starting position 'i'
            # will give the values for a certain configuration for one breakdown component
            dd = d[i::num_clustered]

            # calculate bottoms
            if idx == 0:
                bb = [0] * len(dd)
            else:
                b = y_stack[idx-1]
                bb = b[i::num_clustered]

            assert(len(ind)==len(dd)==len(bb))
            rects.append(ax.bar(left=ind+left_empty+(i*barwidth), height=dd, width=barwidth, bottom=bb,
                            alpha=1, color=colors[idx], ecolor='black', edgecolor='black', hatch=hatch_patterns[idx]))

    # put labels for data bars that overflow ylim
    last = 0
    multi = 0
    if ylim and label_enable:
        for i,elem in enumerate(y_stack[idx]):
            if elem > ylim[1]:
                if last == i-1:
                    padding = left_empty/2
                    multi = multi+1
                else:
                    padding = 0
                    multi = 0
                ax.text((padding*multi)+left_empty+(i*barwidth)+((i/num_clustered)*barwidth)+(barwidth/2.),
                        ylim[1]+label_y_space, '%s'%round(elem,2), ha='center', va='bottom',
                        rotation=lable_angle_rotation, fontsize=numbers_fontsize)
                last = i

    # general formating
    ax.set_title(title)
    ax.set_xlabel(xtitle, fontsize=xtitle_fontsize)
    ax.set_ylabel(ytitle, fontsize=ytitle_fontsize)
    for item in ax.get_yticklabels():
        item.set_fontsize(ylabel_fontsize)

    # xticks possition and labels
    ax.set_xticks(ind + left_empty + (num_clustered/2.0)*barwidth)
    ax.set_xticklabels(xticks,y=-.05, fontsize=xlabel_fontsize)
    plt.gcf().subplots_adjust(bottom=0.2)

    # TODO: labels for configuration L B S BS D DK W WK ...
    if xticks_per_bar:
        for i in xrange(num_clustered):
            for idx in xrange(len(ind)):
                ax.text(rects[i][idx].get_x()+rects[i][idx].get_width()/2., labels_y, '%s'%xticks_per_bar[i],
                    ha='center', va='baseline', fontsize=text_fontsize, rotation=labels_rotation)

    plt.tight_layout()
    # Graph shrinking if desired, no shrinking by default
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * shrink_width_factor, box.height * shrink_height_factor])

    leg = ax.legend([a[0] for a in rects[0::num_clustered]], # get the right colors
          legend, # labels
          loc=legend_loc,
          ncol=legend_ncol,
          frameon=True,
          borderaxespad=0.5,
          bbox_to_anchor=bbox,
          fancybox=True,
          #prop={'size':10}, # smaller font size
          )

    for t in leg.get_texts():
        t.set_fontsize(legend_fontsize)    # the legend text fontsize
    ax.set_axisbelow(True)
    plt.gca().yaxis.grid(color='gray', linestyle='-', linewidth=0.5)
    return plt

def plot_bar(counters, results, counter_name):
  for db in databases:
    for bench in benchmarks:
      for scale in scales:
        print "Processing " + counter_name + " " + db + " " + bench + " " + scale

        # reset the configuration to the default
        execfile('scripts/gen_results_default_config.py', globals(), globals())
        # TODO For each directory set the local configuration

        xtick_labels = []
        d = []
        columns_data = []
        # TODO Change to: for dir in db/bench/scale
        for qry in queries:
          qstr = 'q%02d'%qry
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
                title=string.capwords(counter_name) if title == "from-filename" else title,
                xticks=xtick_labels,
                legend=column_names,
                data=columns_data,
                data_err = column_ids_errdata,
                ylim = ylim,
                )
        path="%s/%s/%s/%s"%(folder_figures, db, bench, scale)
        if not os.path.exists(path): os.makedirs(path)
        plt.savefig("%s/%s-%s-%s-%s.eps" % (path, counter_name, db, bench, scale))
        #plt.show()

def plot_stacked(counters, results, name, *counter_name):
  for db in databases:
    for bench in benchmarks:
      for scale in scales:
        print "Processing " + name + " " + db + " " + bench + " " + scale

        # reset the configuration to the default
        execfile('scripts/gen_results_default_config.py', globals(), globals())
        # TODO For each directory set the local configuration

        # benchmark names
        xtick_labels = [elem for elem in queries]

        # get data - list of lists
        columns_data = []
        for elem in counter_name:
            d = []
            for qry in queries:
                qstr = 'q%02d'%qry
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
        plt = mk_clusterstacked(title=string.capwords(name) if title == "from-filename" else title,
                              xticks=xtick_labels,
                              legend=column_names,
                              data=columns_data,
                              data_err = column_ids_errdata,
                              ylim = ylim,
                              xticks_per_bar=xticks_per_bar_labels,
                              )
        path="%s/%s/%s/%s"%(folder_figures, db, bench, scale)
        if not os.path.exists(path): os.makedirs(path)
        plt.savefig("%s/%s-%s-%s-%s.eps" % (path, name, db, bench, scale))
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
  #add_counter(counters, results, 'l2_mpki', 'L2 MPKI', '( 1000 * $4f2e ) / $total_insts')
  #add_counter(counters, results, 'l2i_mpki', 'L2I MPKI', '( 1000 * $2024 ) / $total_insts')
  #add_counter(counters, results, 'l2d_mpki', 'L2D MPKI', '$l2_mpki - $l2i_mpki')
  #add_counter(counters, results, 'l3_mpki', 'L3 MPKI', '( 1000 * $412e ) / $total_insts')

  # Branch Predictor
  #add_counter(counters, results, 'prcnt_misspred_branches',
                #'% Misspredicted branches', '( $c5 / $c4 ) * 100')
  #add_counter(counters, results, 'prcnt_misspred_cond_branches',
                #'% Misspredicted conditional branches', '( $1c5 / $1c4 ) * 100')

  # Stalls General
  add_counter(counters, results, 'prcnt_cycles_compute_user',
                '% Computational cycles user-level', '( $15301C2:u / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_compute_kernel',
                '% Computational cycles kernel-level', '( $15301C2:k / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_stalled_user',
                '% Stalled cycles user-level', '( $1d301C2:u / $total_cycles ) * 100')
  add_counter(counters, results, 'prcnt_cycles_stalled_kernel',
                '% Stalled cycles kernel-level', '( $1d301C2:k / $total_cycles ) * 100')

  # Stalls Memory
  #add_counter(counters, results, 'prcnt_cycles_dtlb_walk',
                #'% DTLB load miss walk cycles', '( $408 / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_itlb_walk',
                #'% ITLB walk cycles', '( $485 / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_pending_l1d',
                #'% cycles with a pending L1D load miss', '( $2A3 / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_pending_l2',
                #'% cycles with a pending L2 load miss', '( $1A3 / $total_cycles ) * 100')

  # Stalls core
  #add_counter(counters, results, 'prcnt_cycles_empty_freelist',
                #'% cycles stalled free list empty', '( $C5B / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_pregisters',
                #'% cycles stalled control structures full for physical registers',
                #'( $F5B / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_branchorderbuffer',
                #'% cycles allocator stalled full branch order buffer',
                #'( $405B / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_oooresources',
                #'% cycles stalled full OOO resources', '( $4F5B / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_iq',
                #'% cycles stalled full instructuion queue - no issue', '( $487 / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_lb',
                #'% cycles stalled full load buffers', '( $2A2 / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_rs',
                #'% cycles stalled full reservation stations', '( $4A2 / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_sb',
                #'% cycles stalled full store buffers', '( $8A2 / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_full_rob',
                #'% cycles stalled full reorder buffer', '( $10A2 / $total_cycles ) * 100')
  #add_counter(counters, results, 'prcnt_cycles_writting_fpuword',
                #'% cycles stalled writting FPU control word', '( $20A2 / $total_cycles ) * 100')

  # Template
  #add_counter(counters, results, '', '', '')


  # Plot metric of interest -- bars
  plot_bar(counters, results, 'prcnt_kernel_cycles')
  plot_bar(counters, results, 'ipc')
  plot_bar(counters, results, 'l1i_mpki')
  plot_bar(counters, results, 'l1d_mpki')
  #plot_bar(counters, results, 'l2_mpki')
  #plot_bar(counters, results, 'l2i_mpki')
  #plot_bar(counters, results, 'l2d_mpki')
  #plot_bar(counters, results, 'l3_mpki')

  # Plot metric of interest -- barstacks
  #plot_stacked(counters, results, 'compute-stall',
                #'prcnt_cycles_compute_user', 'prcnt_cycles_compute_kernel',
                #'prcnt_cycles_stalled_user', 'prcnt_cycles_stalled_kernel')

if __name__ == '__main__':
  _main()
