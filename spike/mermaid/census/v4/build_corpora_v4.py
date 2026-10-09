"""Apply the draft's §7.1 inclusion rule and write the private and public corpus tables.

usage: python3 -I v4/build_corpora_v4.py <private-dir>    (run in evidence/)

Private inputs (never committed; they name individually owned repositories):
  repo-meta-all.tsv, md-repo-meta.tsv          licence SPDX ids from gh api
  v2/forks-owner.tsv                           owner type from gh api
  v4/mmd-counts-v4.tsv, md-counts-raw.tsv      per-corpus counts
  <private-dir>/noassertion-classified.PRIVATE.tsv   NOASSERTION licences, classified
  <private-dir>/individuals-map.PRIVATE.tsv    the salt
Outputs:
  v4/corpora-v4.PRIVATE.tsv   names every corpus
  v4/corpora-public.tsv       individually owned corpora as u:<12 hex of sha256(salt:owner/name)>
"""
import csv
import hashlib
import sys

priv = sys.argv[1]
PERMISSIVE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense", "0BSD",
              "CC0-1.0", "CC-BY-4.0", "W3C"}
READ_ONLY = {"GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0", "MPL-2.0", "CC-BY-SA-4.0", "CeCILL-2.0"}

meta = {}
for f in ("repo-meta-all.tsv", "md-repo-meta.tsv"):
    for r in csv.reader(open(f), delimiter="\t"):
        meta[r[0]] = r
owner = {r[0]: r[2] for r in csv.reader(open("v2/forks-owner.tsv"), delimiter="\t")}
noassert = {r[0]: r[1] for r in csv.reader(open(f"{priv}/noassertion-classified.PRIVATE.tsv"), delimiter="\t")
            if r and not r[0].startswith("#")}
salt = [l.split("\t")[1].strip() for l in open(f"{priv}/individuals-map.PRIVATE.tsv") if l.startswith("# salt")][0]


def label(name):
    if owner.get(name) == "Organization":
        return name
    return "u:" + hashlib.sha256((salt + ":" + name).encode()).hexdigest()[:12]


def lic(name):
    l = meta[name][1]
    if l == "NOASSERTION":
        l = noassert.get(name, "OUT:unclassified")
    if l in PERMISSIVE:
        return l, "in"
    if l in READ_ONLY:
        return l, "read-only"
    return l.removeprefix("OUT:"), "out"


head = ["stratum", "corpus", "licence", "status", "pin", "flow_paths", "commits", "authors",
        "top_author_share", "bot_share", "version_pairs", "not_ancestor_pairs", "triples",
        "triples_on_ancestry", "merges_2p", "both_sides_evaluable", "owner_type"]
rows = []
for r in csv.reader(open("v4/mmd-counts-v4.tsv"), delimiter="\t"):
    if len(r) < 21 or (int(r[11]) == 0 and int(r[20]) == 0):
        continue
    l, st = lic(r[0])
    rows.append(["mmd", r[0], l, st, r[1], r[4], r[6], r[7], r[12], r[13], r[8], r[9], r[10], r[11], r[14], r[20]])
for r in csv.reader(open("md-counts-raw.tsv"), delimiter="\t"):
    if len(r) < 18:
        continue
    l, st = lic(r[0])
    rows.append(["md", r[0], l, st, r[1], r[2], "-", r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[17]])
rows.sort(key=lambda r: (r[0], label(r[1])))  # deterministic order, independent of run order
with open("v4/corpora-v4.PRIVATE.tsv", "w") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(head)
    for r in rows:
        w.writerow(r + [owner.get(r[1], "?")])
with open("v4/corpora-public.tsv", "w") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(head)
    for r in rows:
        pin = r[4]
        if label(r[1]) != r[1]:
            # v4: a pin identifies its repository (one commit search finds it), so an
            # individually owned corpus's pin is published only as a salted hash
            pin = "h:" + hashlib.sha256((salt + ":pin:" + pin).encode()).hexdigest()[:16]
        w.writerow([r[0], label(r[1])] + r[2:4] + [pin] + r[5:] + [owner.get(r[1], "?")])
