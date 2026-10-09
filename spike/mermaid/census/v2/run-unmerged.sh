#!/bin/sh
# usage: v2/run-unmerged.sh <prs|forks> <stratum> <owner/name>   (run in evidence/)
m=$1; s=$2; r=$3; d=$(echo $r | tr / _)
if [ $s = mmd ]; then b=../clones/$d.git; else b=../md-clones/$d.git; fi
if [ ! -s mpr/$d.paths ]; then
  if [ $s = mmd ]; then python3 -I flow_paths.py mmd $b > mpr/$d.paths; else python3 -I flow_paths.py md ../md-clones/$d.wt > mpr/$d.paths; fi
fi
timeout 5400 python3 -I v2/unmerged_counts.py $m $b $r mpr/$d.paths | sed "s/^/$s\t/" || echo "$s	$r	TIMEOUT-OR-FAIL"
