#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Runs §11.2's V steps that need no blind role's output, each into its
# transcript under results/validation/: a header naming the commit and the
# toolchain, the step's full output, and its exit status. A step run on a
# work tree with uncommitted bound paths says so in its header.
#
#   harness/validate.sh [v0|v2|v3|v4 ...]     (default: v0 v2 v3 v4)
set -u
here=$(cd "$(dirname "$0")" && pwd)
spike=$(dirname "$here")
out="$spike/results/validation"
mkdir -p "$out"
steps=("$@")
[ ${#steps[@]} -eq 0 ] && steps=(v0 v2 v3 v4)
rc_all=0
for s in "${steps[@]}"; do
  t="$out/$s.txt"
  {
    echo "# $s, $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# nodespec HEAD: $(git -C "$spike" rev-parse HEAD)"
    dirty=$(git -C "$spike" status --porcelain -- harness r x v-fixtures PRE-REGISTRATION.md)
    echo "# bound paths clean: $([ -z "$dirty" ] && echo yes || echo "NO: $dirty")"
    echo "# $(python3 --version 2>&1); $(git --version); node $(node --version)"
    echo
  } > "$t"
  case $s in
    v0) python3 -I -S -B "$here/v0.py" >> "$t" 2>&1 ;;
    v2) python3 -I -S -B "$here/v2.py" >> "$t" 2>&1 ;;
    v3) python3 -I -S -B "$here/v3.py" >> "$t" 2>&1 ;;
    v4) python3 -I -S -B "$here/v4.py" --jobs 6 --timeout 900 >> "$t" 2>&1 ;;
    *) echo "unknown step $s" >> "$t"; false ;;
  esac
  rc=$?
  echo "# exit status $rc" >> "$t"
  echo "$s: exit $rc ($(tail -2 "$t" | head -1))"
  [ $rc -ne 0 ] && rc_all=1
done
exit $rc_all
