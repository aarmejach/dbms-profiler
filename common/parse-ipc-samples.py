import sys, re

prev_time = 0
reference_time = 0
pid = 0
freq=2.6

for line in sys.stdin:
    if 'PERF_RECORD_FORK' in line:
        assert(pid==0)
        tmp = re.split('\)|:', line)
        pid = tmp[-5]
        #print pid
    else:
        if pid != 0:
            if 'PERF_RECORD_SAMPLE' in line:
                if str(pid + '/' + pid) in line:
                    tmp = line.split()
                    if prev_time == 0:
                        reference_time = prev_time = int(tmp[1])
                    else:
                        current_time = int(tmp[1])
                        instructions = int(tmp[-3])
                        absolute_time = float(current_time - reference_time) / 10**9
                        period_time = current_time - prev_time
                        cycles = freq * period_time
                        # Print time in seconds, instructions for the period, cycles for period, ipc
                        print '%f,%d,%d,%f' % (absolute_time, instructions, cycles, instructions / cycles)
                        prev_time = current_time
