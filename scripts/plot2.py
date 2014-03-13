from plot import get_counters, get_results, add_counter, plot

file_name = "./common/perf-counters-axle.sh"
counters = get_counters(file_name)
# pprint(counters)

folder_name = './results-perf'
results = get_results(folder_name)
# pprint(results)

add_counter(results, counters, 'c/i', 'Division', '$ff88 / $ff89 * $82d0')
add_counter(results, counters, 'i/c', '1/Division', '1 / $c/i')

plot(results, counters, 'ff88')

