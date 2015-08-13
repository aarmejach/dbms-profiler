#!/usr/bin/python

from itertools import combinations, combinations_with_replacement
import random

APPSa = "403.gcc 433.milc 450.soplex 462.libquantum 462.libquantum 471.omnetpp 429.mcf 459.GemsFDTD 470.lbm 437.leslie3d".split()
#APPSa = "403.gcc 433.milc 450.soplex 462.libquantum 471.omnetpp 429.mcf 459.GemsFDTD 470.lbm 482.sphinx3".split()
#APPSb = "403.gcc 433.milc 437.leslie3d 450.soplex 462.libquantum 471.omnetpp 429.mcf 459.GemsFDTD 470.lbm 473.astar 482.sphinx3".split()
#APPSc = "403.gcc 433.milc 437.leslie3d 450.soplex 462.libquantum 471.omnetpp 429.mcf 459.GemsFDTD 470.lbm 473.astar 482.sphinx3".split()

#APPS = APPSa + APPSb + APPSc
APPS = APPSa + APPSa + APPSa

MIXES = list(combinations(APPS, 8))
#MIXES = list(combinations_with_replacement(APPS, 8))
print len(MIXES)

NUMMIXES = 32

print "mixes:"
OUTPUT = []

for i in xrange(0, NUMMIXES):
    n = random.randint(0, len(MIXES)-1)
    print n
    OUTPUT.append(MIXES[n])

print OUTPUT
