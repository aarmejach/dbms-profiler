#!/usr/bin/python
# parse periodic stats to generate ipc throu time chart

import h5py # presents HDF5 files as numpy arrays
import numpy as np
import sys

# return time in seconds
def get_time(cycles):
    freq = 2.6 * 10**9
    return float(cycles / freq)

def _main():

    if len(sys.argv) == 2:
        ftmp = str(sys.argv[1])
    else:
        ftmp = 'zsim.h5'

    # Open periodic stats file
    f = h5py.File(ftmp, 'r')

    # Get the single dataset in the file
    dset = f["stats"]["root"]

    # Each dataset is first indexed by record. A record is a snapshot of all the
    # stats taken at a specific time.  All stats files have at least two records,
    # at beginning (dest[0]) and end of simulation (dset[-1]).  Inside each record,
    # the format follows the structure of the simulated objects. A few examples:

    instructions = dset['sandy']['instrs']
    cycles = dset['sandy']['cycles']
    assert(len(instructions)==len(cycles))

    # initial values
    #prev_instr = instructions[0][0]
    #prev_cycles = cycles[0][0]
    #prev_time = 0

    print 'absolute_time,absolute_instructions,instructions,cycles,ipc'

    for i in xrange(1,len(instructions)):
        current_cycles = float(cycles[i][0])

        instr_sample = instructions[i][0] - instructions[i-1][0]
        cycles_sample = current_cycles - cycles[i-1][0]

        current_time =  get_time(current_cycles)
        # Print time in seconds, instructions for the period, cycles for period, ipc
        print '%f,%d,%d,%d,%f' % (current_time, instructions[i][0], instr_sample, cycles_sample, instr_sample/cycles_sample)


if __name__ == '__main__':
    _main()
