#!/usr/bin/env bash
# shellcheck disable=SC2015  # ok() always succeeds, so A && ok || bad is if-then-else
# SPDX-License-Identifier: MIT
# The review step of each §11.3 pull request after validation, run in a FRESH
# CLONE of the merged result: it re-derives the validation commit from
# history alone and checks what the harness cannot check about itself.
# Each check prints PASS or FAIL; the exit status is 1 if any failed.
#
#   harness/reverify.sh [spike/mermaid dir]    (default: this script's ../)
set -u
spike=${1:-$(cd "$(dirname "$0")/.." && pwd)}
for v in $(env | sed -n 's/^\(GIT_[A-Za-z0-9_]*\)=.*/\1/p'); do unset "$v"; done
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
g() { git -C "$spike" "$@"; }
bound=(harness r x v-fixtures PRE-REGISTRATION.md)
fails=0
ok() { echo "PASS  $*"; }
bad() { echo "FAIL  $*"; fails=$((fails + 1)); }

[ "$(g rev-parse --is-shallow-repository 2>/dev/null)" = false ] && ok "not shallow" || bad "shallow or not a repository"
mapfile -t vcs < <(g log --full-history --format=%H --diff-filter=A -- results/VALIDATION)
if [ "${#vcs[@]}" -ne 1 ]; then
  bad "${#vcs[@]} commits add results/VALIDATION; exactly one must"
  echo "reverify: $fails failed"; exit 1
fi
V=${vcs[0]}
ok "validation commit $V"
if g rev-parse --verify -q "$V^" >/dev/null && g diff --quiet "$V^" "$V" -- "${bound[@]}"; then
  ok "the validation commit changes no bound path"
else
  bad "the validation commit has no parent, or changes a bound path"
fi
later=$(g log --full-history --format=%H "$V..HEAD" -- "${bound[@]}")
[ -z "$later" ] && ok "no later commit touches a bound path" || bad "later commits touch a bound path: $later"
[ "$(g log --full-history --format=%H -- results/VALIDATION | wc -l)" -eq 1 ] \
  && ok "VALIDATION never changed" || bad "VALIDATION changed after it was added"
others=$(grep -rhoE '"validation_commit": *"[0-9a-f]{40}"' "$spike/results" 2>/dev/null \
  | grep -oE '[0-9a-f]{40}' | sort -u | grep -vx "$V")
[ -z "$others" ] && ok "every output that names a validation commit names $V" \
  || bad "outputs name another validation commit: $others"
badtr=$(grep -rl '^# bound: True' "$spike/results/transcripts" 2>/dev/null | while read -r t; do
  grep -q "validation commit $V" "$t" || echo "$t"
done)
[ -z "$badtr" ] && ok "every bound transcript names $V" || bad "bound transcripts name another commit: $badtr"
for arm in arm0 arms sealed aggregate; do
  n=$(g log --all --full-history --format=%H --diff-filter=A -- "results/executed/$arm.json" | wc -l)
  [ "$n" -le 1 ] && ok "$arm executed at most once ($n)" || bad "$arm's marker was added $n times"
done
[ "$fails" -eq 0 ] && { echo "reverify: PASS"; exit 0; }
echo "reverify: $fails failed"; exit 1
