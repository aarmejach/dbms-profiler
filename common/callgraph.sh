#!/bin/bash

# Generate callgraphs
for i in $QUERIES;
do
  ii=$(printf "%02d" $i)
  dir="q${ii}"
  mkdir -p $dir
  cd "$dir"

  cgf="q${ii}-callgraph.pdf"
  echo "Creating the call graph: $cgf"
  perf script | python "$BASEDIR/gprof2dot.py" -f perf | dot -Tpdf -o $cgf &

  cd - >/dev/null
done

# Wait for all pending jobs to finish.
for p in $(jobs -p);
do
  wait $p
done

