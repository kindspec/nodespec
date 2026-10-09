#!/bin/sh
# usage: v3/run-v3.sh <mpr|unmerged> <stratum> <owner/name>   (run in evidence/)
m=$1; s=$2; r=$3; d=$(echo $r | tr / _)
if [ $s = mmd ]; then b=../clones/$d.git; else b=../md-clones/$d.git; fi
extra=""
case $r in apache/airflow|backstage/backstage|grafana/grafana) [ $m = unmerged ] && extra=fast;; esac
red=""
[ $r = grafana/grafana ] && red=--redact
python3 -I v3/d_cases_v3.py $m $b $r mpr/$d.paths $s $extra $red
