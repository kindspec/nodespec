#!/bin/sh
# usage: mpr-run.sh <stratum> <owner/name>   (run in evidence/)
s=$1; r=$2; d=$(echo $r | tr / _)
if [ $s = mmd ]; then b=../clones/$d.git; python3 -I flow_paths.py mmd $b > mpr/$d.paths
else b=../md-clones/$d.git; python3 -I flow_paths.py md ../md-clones/$d.wt > mpr/$d.paths; fi
python3 -I mpr_counts.py $b $r mpr/$d.paths | sed "s/^/$s\t/"
