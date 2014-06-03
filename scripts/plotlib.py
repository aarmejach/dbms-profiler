import os,sys,string,re
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter
from pprint import pprint

def mk_barchart(config, name, xticks, legend, data, data_err=None, ylim=None):
    assert(len(legend)==len(data))

    # Load config file
    execfile(config, globals(), globals())
    #import gen_results_default_config

    ind = np.arange(len(xticks))  # the x locations for the groups
    barwidth = 1.0/(len(legend)+1)       # the width of the bars

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

    mytitle = title
    if mytitle == "from-filename":
        mytitle = string.capwords(name)

    # general formating
    ax.set_title(mytitle, fontsize=title_fontsize)
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

def mk_stacked(config, name, xticks, legend, data, data_err=None, ylim=None, xticks_per_bar=None):
    assert(len(legend)==len(data))

    # Load config file
    execfile(config, globals(), globals())

    ind = np.arange(len(xticks))        # the x locations for the groups
    barwidth = 1.0/2                    # the width of the bars, no clustering

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
        #for i in xrange(num_clustered):
            #this gives every n'th element given a starting position 'i'
            # will give the values for a certain configuration for one breakdown component
            #dd = d[i::num_clustered]

            # calculate bottoms
            if idx == 0:
                b = [0] * len(d)
            else:
                b = y_stack[idx-1]
                #bb = b[i::num_clustered]

            assert(len(ind)==len(d)==len(b))
            rects.append(ax.bar(left=ind+left_empty, height=d, width=barwidth, bottom=b,
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
                ax.text((padding*multi)+left_empty+(i*barwidth)+(i*barwidth)+(barwidth/2.),
                        ylim[1]+label_y_space, '%s'%round(elem,2), ha='center', va='bottom',
                        rotation=lable_angle_rotation, fontsize=numbers_fontsize)
                last = i

    mytitle = title
    if mytitle == "from-filename":
        mytitle = string.capwords(name)

    # general formating
    ax.set_title(mytitle)
    ax.set_xlabel(xtitle, fontsize=xtitle_fontsize)
    ax.set_ylabel(ytitle, fontsize=ytitle_fontsize)
    for item in ax.get_yticklabels():
        item.set_fontsize(ylabel_fontsize)

    # xticks possition and labels
    ax.set_xticks(ind + left_empty + (barwidth/2.0))
    ax.set_xticklabels(xticks,y=-0.01, fontsize=xlabel_fontsize)
    plt.gcf().subplots_adjust(bottom=0.2)

    # TODO: labels for configuration L B S BS D DK W WK ...
    #if xticks_per_bar:
        #for i in xrange(num_clustered):
            #for idx in xrange(len(ind)):
                #ax.text(rects[i][idx].get_x()+rects[i][idx].get_width()/2., labels_y, '%s'%xticks_per_bar[i],
                    #ha='center', va='baseline', fontsize=text_fontsize, rotation=labels_rotation)

    plt.tight_layout()
    # Graph shrinking if desired, no shrinking by default
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * shrink_width_factor, box.height * shrink_height_factor])

    leg = ax.legend([a[0] for a in rects], # get the right colors
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

def mk_clusterstacked(config, name, xticks, legend, data, data_err=None, ylim=None, xticks_per_bar=None):
    assert(len(legend)==len(data))

    # Load config file
    execfile(config, globals(), globals())

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

    mytitle = title
    if mytitle == "from-filename":
        mytitle = string.capwords(name)

    # general formating
    ax.set_title(mytitle)
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

