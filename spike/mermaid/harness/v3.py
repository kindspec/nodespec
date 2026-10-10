#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION.md §11.2 V3: every component goes red on a planted case,
and on empty input. H's own plants only; the V-fixture half of V3 ("each
category fires on its V-fixtures") waits for F and runs in v-fixtures.py.

    python3 -I -S -B harness/v3.py [--only SECTION]

Each check prints PASS or FAIL with its name. A section that raises is a
FAIL named "section raised: ..."; V4 does not count such a crash as a kill.
Exit 1 if any check failed. Every plant is synthetic and built here, in a
temporary directory; nothing touches a corpus, the user's HOME, or the
repository's results/.
"""
import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import traceback

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SPIKE = os.path.dirname(HERE)

from ms import aggregate as AG  # noqa: E402
from ms import arms as AR  # noqa: E402
from ms import binding as BD  # noqa: E402
from ms import blind as BL  # noqa: E402
from ms import case as C  # noqa: E402
from ms import corpus as K  # noqa: E402
from ms import fence as FN  # noqa: E402
from ms import gitops as G  # noqa: E402
from ms import history as HI  # noqa: E402
from ms import oracle as OR  # noqa: E402
from ms import rbridge as RB  # noqa: E402
from ms import replay as RP  # noqa: E402
from ms import subset as SS  # noqa: E402
from ms import xrun as XR  # noqa: E402

RESULTS = {"pass": 0, "fail": 0}
R = RB.RCache()
TMP = None


def check(name, ok, detail=""):
    RESULTS["pass" if ok else "fail"] += 1
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not ok else ""))
    return ok


def tmpdir(tag):
    return tempfile.mkdtemp(prefix=tag + ".", dir=TMP)


# ----------------------------------------------------------------- helpers

def run_case(stratum, b, o, t, path=None):
    path = path or ("c.mmd" if stratum == "F" else "c.md")
    prep = C.prepare(stratum, b, o, t, R)
    if prep["excluded"] and "states" not in prep:
        return prep, None
    m = G.merge_texts(path, b.encode(), o.encode(), t.encode(), TMP)
    res = C.outcome(prep, [b, o, t], m, R, path=path)
    return prep, res


def cats(res, tier=None):
    return sorted({(r["category"], r["tier"]) for r in (res or {}).get("records", [])
                   if tier is None or r["tier"] == tier})


def has(res, cat, tier=None, obj=None):
    return any(r["category"] == cat and (tier is None or r["tier"] == tier) and (obj is None or obj in r["objects"])
               for r in (res or {}).get("records", []))


def md(diagram, prose="Prose before.\n"):
    return f"# Title\n\n{prose}\n```mermaid\n{diagram}```\n\nProse after.\n"


class Plant:
    """A planted git repository built with porcelain commands."""

    def __init__(self, tag):
        self.path = tmpdir(tag)
        self.home = tmpdir("home")
        self.e = G.env(self.home)
        self.g("init", "-q", "-b", "main")

    def g(self, *a, check=True, author=None):
        e = dict(self.e)
        if author:
            e.update(GIT_AUTHOR_NAME=author[0], GIT_AUTHOR_EMAIL=author[1])
        r = subprocess.run(["git", "-C", self.path, *a], capture_output=True, text=True, env=e)
        if check and r.returncode != 0:
            raise RuntimeError(f"git {a}: {r.stderr}")
        return r.stdout.strip()

    def commit(self, files, msg, author=("Ann", "ann@example.org")):
        for p, t in files.items():
            full = os.path.join(self.path, p)
            if t is None:
                if os.path.exists(full):
                    os.remove(full)
                continue
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(t)
        self.g("add", "-A")
        self.g("commit", "-q", "--allow-empty", "-m", msg, author=author)
        return self.g("rev-parse", "HEAD")


# ---------------------------------------------------------------- sections

def s_holes():
    """Both canonical holes, both styles, both strata (V3)."""
    b = "flowchart LR\n  api --> db\n  db --> cache\n  ui --> api\n"
    o = "flowchart LR\n  api --> pg\n  pg --> cache\n  ui --> api\n"
    t = b + "  worker --> db\n"
    bd = "flowchart LR\n  api[API] --> db[(Postgres)]\n  db --> cache[Cache]\n  ui[UI] --> api\n"
    od = "flowchart LR\n  api[API] --> pg[(Postgres)]\n  pg --> cache[Cache]\n  ui[UI] --> api\n"
    td = bd + "  worker[Worker] --> db\n"
    h3 = "flowchart LR\n  a[A] --> b[B]\n  x[X]\n  y[Y]\n"
    h3o = "flowchart LR\n  c[Cache] --> a\n  a[A] --> b[B]\n  x[X]\n  y[Y]\n"
    h3t = h3 + "  b --> c[Config]\n"
    h3tc = h3 + "  b --> c[Cache]\n  style c fill:#f00\n"
    for st in ("F", "D"):
        w = (lambda x: x) if st == "F" else md
        p, r = run_case(st, w(b), w(o), w(t))
        check(f"{st}: hole #2 bare style is clean I1 at tier A", r and r["outcome"] == "JUDGED" and
              has(r, "I1", "A", "db"), cats(r))
        check(f"{st}: hole #2 bare style is exposed", p.get("exposed") is True)
        check(f"{st}: hole #2's ghost is no G1: G1 is outside I1-I4", not has(r, "G1", obj="db"), cats(r))
        p, r = run_case(st, w(bd), w(od), w(td))
        check(f"{st}: hole #2 with a declared label is I1 at tier B through L1", has(r, "I1", "B", "db") and
              any(x.startswith("L1:db") for x in r.get("lint_new", [])), cats(r))
        p, r = run_case(st, w(h3), w(h3o), w(h3t))
        check(f"{st}: hole #3 with differing labels is I2 at tier B through L2", has(r, "I2", "B", "c") and
              any(x.startswith("L2:c") for x in r.get("lint_new", [])), cats(r))
        p, r = run_case(st, w(h3), w(h3o), w(h3tc))
        check(f"{st}: hole #3 differing only in style is I2 at tier A", has(r, "I2", "A", "c"), cats(r))
        check(f"{st}: hole #3 is exposed", p.get("exposed") is True)


def s_census_cases():
    """census/synth-results.out's synthetic cases, each a plant (V3)."""
    d = os.path.join(SPIKE, "census", "v4", "cases")
    want = {"deleteBox": "E", "dupAdd": "DUP-TITLE", "hole2": "E", "retitleBoth": "E"}
    clean = ["moveBetweenRetitled", "moveIntoRetitled", "moveIntoRetitledExplicit", "moveRenameBothExplicit",
             "moveRetitleBoth", "renameExplicit", "retitle", "retitleMemberMention", "unwrap", "wordToTitle"]
    for c in sorted(os.listdir(d)):
        b, o, t = (open(os.path.join(d, c, f + ".mmd")).read() for f in "bot")
        p, r = run_case("F", b, o, t)
        rec = [x for x in r["records"] if x["category"] not in ("S-ORDER", "MC-ineligible")] if r else []
        if c in want:
            check(f"census case {c}: {want[c]}", r and r["outcome"] == want[c], r and r["outcome"])
        elif c in clean:
            check(f"census case {c}: clean, no record, no MC", r and r["outcome"] == "JUDGED" and not rec,
                  [x["category"] for x in rec])
        elif c == "posRef":
            check("census case posRef: G2, one edge lost and one extra", r and sorted(
                x["detail"].split()[0] for x in rec if x["category"] == "G2") == ["extra", "lost"], rec)
        elif c == "renameExplicitRef":
            check("census case renameExplicitRef: clean, I1 on fe, tier B by a new L1",
                  has(r, "I1", "B", "fe") and "L1:fe" in r.get("lint_new", []), cats(r))


def s_conflicts():
    """Model conflicts, delete/modify, and holders that are not references."""
    b = "flowchart LR\n  a[A] --> b[B]\n  x[X]\n  y[Y]\n  z[Z]\n  b --> a\n"
    o = b.replace("a[A] --> b[B]", "a[From O] --> b[B]")
    t = b + "  a[From T]\n"
    p, r = run_case("F", b, o, t)
    check("a label both legs change is a model conflict; merged to a leg's value it is ineligible MC",
          r and has(r, "MC-ineligible") and not has(r, "MC") and not has(r, "G4"), cats(r))
    b = "flowchart LR\n  c[C] --> d[D]\n  e[E]\n  f[F]\n  g[G]\n  h[H]\n"
    o = "flowchart LR\n  d[D]\n  e[E]\n  f[F]\n  g[G]\n  h[H]\n"
    t = b + "  style c fill:#f00\n"
    p, r = run_case("F", b, o, t)
    check("delete/modify: one leg deletes c, the other restyles it: I3 on c", has(r, "I3", obj="c"), cats(r))
    d = os.path.join(SPIKE, "census", "v4", "cases", "retitle")
    q = C.prepare("F", *(open(os.path.join(d, f + ".mmd")).read() for f in "bot"), R)
    check("a holder is not a reference: retitling a box while the other leg adds a member is not exposed",
          q["exposed"] is False, q.get("exposure_reason"))
    t = "flowchart TD\n subgraph s1\n X\n end\n subgraph s2\n X\n end\n"
    m = SS.classify(t, R.get(t)).model
    check("membership: a node mentioned in two subgraphs is held by the first to close", m.get(("nhold", "X")) == "s1")


def s_positional():
    b = "flowchart TD\n  subgraph Front End\n    A\n  end\n  subgraph Back End\n    B\n  end\n"
    o = "flowchart TD\n  subgraph Back End\n    B\n  end\n"
    t = "flowchart TD\n  subgraph Front End\n    A\n  end\n  subgraph Back End\n    B\n    D\n  end\n"
    p, r = run_case("F", b, o, t)
    check("probe4: deleting one untitled subgraph and adding to another yields no I record",
          r and r["outcome"] == "JUDGED" and not any(x["category"].startswith("I") for x in r["records"]), cats(r))


def s_edge_to_subgraph():
    b = "flowchart TD\n  subgraph S [Box]\n    Q\n  end\n  A --> S\n  z[Z]\n"
    o = "flowchart TD\n  x[X]\n" + b.split("\n", 1)[1]
    t = b + "  y[Y]\n"
    p, r = run_case("F", b, o, t)
    B = p["states"][0].model
    check("an edge end naming a subgraph is a reference, not a node", B.get(("exist", "S")) == ("subgraph",),
          B.get(("exist", "S")))
    check("an edge to a subgraph is not I4", r and not has(r, "I4"), cats(r))


def s_i4():
    b = "flowchart LR\n  e1[Node]\n  A e1@--> B\n  z[Z]\n"
    p, r = run_case("F", b, "flowchart LR\n  x[X]\n" + b.split("\n", 1)[1], b + "  y[Y]\n")
    check("I4 is relative: a node-versus-edge-id clash present in the base is no record",
          r and r["outcome"] == "JUDGED" and not has(r, "I4"), cats(r))
    b = "flowchart LR\n  n1[One]\n  A --> B\n  z[Z]\n"
    o = "flowchart LR\n  n1[One]\n  e1[Node]\n  A --> B\n  z[Z]\n"
    t = b + "  A e1@--> C\n"
    p, r = run_case("F", b, o, t)
    check("I4: a clash the merge introduces is I4", has(r, "I4", obj="e1"), cats(r))


def s_exposure():
    b = "flowchart LR\n  api --> db\n  db --> cache\n  ui --> api\n"
    o = "flowchart LR\n  api --> pg\n  pg --> cache\n  ui --> api\n"
    t = b + "  worker --> db\n"
    p = C.prepare("F", b, o, t, R)
    m1 = G.merge_texts("c.mmd", b.encode(), o.encode(), t.encode(), TMP)
    m2 = G.Merge(b"flowchart LR\n  a --> b\n", False, 0, [])
    r1 = C.outcome(p, [b, o, t], m1, R, path="c.mmd")
    r2 = C.outcome(p, [b, o, t], m2, R, path="c.mmd")
    check("exposure is computed from inputs alone: changing the merged file does not change it",
          r1["exposed"] is True and r2["exposed"] is True and r1["records"] != r2["records"])
    import inspect
    check("exposure's signature takes B, O and T only", list(inspect.signature(OR.exposure).parameters) == ["B", "O", "T"])
    q = C.prepare("F", "flowchart LR\n  a --> b\n", "flowchart LR\n  a --> b\n  b --> c\n",
                  "flowchart LR\n  a --> b\n  x --> a\n", R)
    check("a case no refusal precondition touches is not exposed", q["exposed"] is False)


def s_per_path_e():
    b = md("flowchart LR\n  api --> db\n  db --> cache\n  ui --> api\n", "Prose one.\n")
    o = md("flowchart LR\n  api --> pg\n  pg --> cache\n  ui --> api\n", "Prose from O.\n")
    t = md("flowchart LR\n  api --> db\n  db --> cache\n  ui --> api\n  worker --> db\n", "Prose from T.\n")
    p, r = run_case("D", b, o, t)
    check("per-path E: a D file whose prose conflicts and whose fence merges wrong is E",
          r and r["outcome"] == "E", r and r["outcome"])


def s_fences():
    d = "flowchart TD\n  A --> B\n"
    for opener in ("   ```mermaid", "```MERMAID", "~~~mermaid-example", "````Mermaid"):
        close = "~~~" if opener.lstrip().startswith("~") else ("````" if "````" in opener else "```")
        txt = f"x\n{opener}\n{d}{close}\ny\n"
        check(f"fence opener {opener.strip()!r} is recognised", len(FN.fences(txt)) == 1 and FN.fences(txt)[0][0] == d)
    check("a flowchart-elk header is a flowchart", FN.is_flowchart("flowchart-elk TD\n  A --> B\n"))
    check("a Flowchart header is not (Mermaid is case-sensitive)", not FN.is_flowchart("Flowchart TD\n"))
    check("a graph header after front matter and a comment is a flowchart",
          FN.is_flowchart("---\ntitle: t\n---\n%% c\n\n  graph LR\n"))
    two = md(d) + "\n```mermaid\nflowchart LR\n  X --> Y\n```\n"
    p = C.prepare("D", two, md(d), md(d + "  B --> C\n"), R)
    check("a D input with two fences excludes the case", (p["excluded"] or "").startswith("one-fence"))
    b = md("flowchart LR\n  a --> b\n")
    o = md("flowchart LR\n  a --> b\n  a --> c\n")
    t = md("flowchart LR\n  a --> b\n  b --> c\n")
    p = C.prepare("D", b, o, t, R)
    # A merged file with two fences, from inputs with one each: planted as
    # the merge result, since stock git rarely produces it.
    m = G.Merge((t + "\n```mermaid\nflowchart LR\n  q --> r\n```\n").encode(), False, 0, [])
    r = C.outcome(p, [b, o, t], m, R, path="c.md")
    check("a merged file with two fences is G0, tier B", r and r["outcome"] == "G0" and has(r, "G0", "B"),
          r and r["outcome"])
    check("G0 is not decided", r and r["outcome"] not in ("E", "JUDGED"))


def s_generated():
    pl = Plant("gen")
    fc = "flowchart TD\n  A --> B\n"
    pl.commit({"testdata/x.mmd": fc, "gen.mmd": "%% auto-generated by a tool\n" + fc,
               "deps/graph.mmd": fc, "deps/graph.dot": "digraph{}\n",
               "half/graph.mmd": fc, "half/graph.dot": "digraph{}\n",
               "svgonly/graph.mmd": fc, "svgonly/graph.svg": "<svg/>\n", "keep.mmd": fc}, "c1")
    for i in range(3):
        pl.commit({"deps/graph.mmd": fc + f"  B --> C{i}\n", "deps/graph.dot": f"digraph{{{i}}}\n",
                   "half/graph.mmd": fc + f"  B --> C{i}\n", "svgonly/graph.mmd": fc + f"  B --> C{i}\n",
                   "svgonly/graph.svg": f"<svg>{i}</svg>\n"}, f"c{i + 2}")
    pin = pl.g("rev-parse", "HEAD")
    sel = HI.select(HI.Repo(pl.path), pin)
    s, x = sel["selected"], sel["excluded"]
    check("a path under testdata/ is excluded", "testdata/x.mmd" in x and "testdata/x.mmd" not in s)
    check("a file declaring auto-generated is excluded", "gen.mmd" in x)
    check("graph.mmd beside a graph.dot changing in every commit is excluded", "deps/graph.mmd" in x, x.get("deps/graph.mmd"))
    check("graph.mmd beside a graph.dot changing in fewer than half its commits is selected", "half/graph.mmd" in s)
    check("graph.mmd beside only graph.svg is selected", "svgonly/graph.mmd" in s)
    check("an ordinary flowchart is selected", s.get("keep.mmd") == "F")


def _pr_plant():
    pl = Plant("mpr")
    pad = "".join(f"  p{i}[P{i}]\n" for i in range(8))
    base = "flowchart TD\n  a[A] --> b[B]\n" + pad + "  b --> c[C]\n" + pad.replace("p", "q") + \
        "  c --> d[D]\n" + pad.replace("p", "r") + "  d --> e[E]\n"
    c0 = pl.commit({"g.mmd": base}, "base")
    # rebase-merged pull request of three commits
    pl.g("checkout", "-q", "-b", "pr1")
    p1 = [pl.commit({"g.mmd": base.replace("a[A]", "a[A1]")}, "p1a"),
          pl.commit({"g.mmd": base.replace("a[A]", "a[A2]")}, "p1b"),
          pl.commit({"g.mmd": base.replace("a[A]", "a[A3]")}, "p1c")]
    pl.g("checkout", "-q", "main")
    pl.commit({"g.mmd": base.replace("e[E]", "e[E main]")}, "main moves")
    for s in p1:
        pl.g("cherry-pick", s)
    rebase_c = pl.g("rev-parse", "HEAD")
    rebase_target = pl.g("rev-parse", "HEAD~3")
    # squash-merged pull request of ten commits
    cur = pl.g("show", "HEAD:g.mmd") + "\n"
    pl.g("checkout", "-q", "-b", "pr2", "HEAD~1")
    p2 = []
    t = pl.g("show", "HEAD:g.mmd") + "\n"
    for i in range(10):
        t = t.replace("c[C]" if i == 0 else f"c[C{i - 1}]", f"c[C{i}]")
        p2.append(pl.commit({"g.mmd": t}, f"p2 {i}"))
    pl.g("checkout", "-q", "main")
    merged = cur.replace("c[C]", "c[C9]")
    squash_c = pl.commit({"g.mmd": merged}, "squash pr2")
    squash_target = pl.g("rev-parse", "HEAD^")
    # neither rule: the merge commit's diff is not the pull request's
    pl.g("checkout", "-q", "-b", "pr3")
    p3 = [pl.commit({"g.mmd": merged.replace("d[D]", "d[D3]")}, "p3a"),
          pl.commit({"g.mmd": merged.replace("d[D]", "d[D4]")}, "p3b")]
    pl.g("checkout", "-q", "main")
    neither_c = pl.commit({"g.mmd": merged.replace("d[D]", "d[D5]")}, "neither")
    pin = pl.g("rev-parse", "HEAD")
    prs = [{"number": 1, "head": p1[-1], "merge": rebase_c, "commit_count": 3, "commits": p1},
           {"number": 2, "head": p2[-1], "merge": squash_c, "commit_count": 10, "commits": p2},
           {"number": 3, "head": p3[-1], "merge": neither_c, "commit_count": 2, "commits": p3},
           {"number": 4, "head": p3[-1], "merge": neither_c, "commit_count": 251, "commits": ["0" * 40] * 251}]
    return pl, pin, prs, {"rebase_target": rebase_target, "squash_target": squash_target, "c0": c0}


def s_mpr():
    pl, pin, prs, w = _pr_plant()
    repo = HI.Repo(pl.path)
    sel = {"g.mmd": "F"}
    cases, counts = HI.pr_cases(repo, pin, sel, prs)
    by = {c["pr"]: c for c in cases}
    check("M-PR: a planted rebase merge of three commits takes c~3", 1 in by and by[1]["o"] == w["rebase_target"],
          counts)
    check("M-PR: a planted ten-commit squash merge takes c^", 2 in by and by[2]["o"] == w["squash_target"], counts)
    check("M-PR: a commit matching neither rule is excluded and counted", 3 not in by and counts["neither rule"] == 1,
          counts)
    check("M-PR: a pull request of 251 commits is excluded and counted", 4 not in by and counts["over 250 commits"] == 1,
          counts)
    pages = []

    def api(path):
        pages.append(path)
        page = int(path.rsplit("page=", 1)[1])
        if "/pulls?" in path:
            return [{"number": 9, "merged_at": "x", "head": {"sha": "h"}, "merge_commit_sha": "m",
                     "commits": 120}] if page == 1 else []
        n = {1: 100, 2: 20}.get(page, 0)
        return [{"sha": f"{page}{i:039d}"} for i in range(n)]
    lst = K.fetch_pr_list("o/r", api)
    check("M-PR: a pull request of 120 commits is read across two pages of the API",
          len(lst) == 1 and len(lst[0]["commits"]) == 120 and sum("commits?" in p for p in pages) == 2,
          [len(x["commits"]) for x in lst])


def _p_plant():
    pl = Plant("parm")
    v = ["flowchart TD\n  a[A] --> b[B]\n  c[C] --> d[D]\n  e[E] --> f[F]\n"]
    for i in range(1, 6):
        v.append(v[-1].replace("a[A" + ("" if i == 1 else str(i - 1)) + "]", f"a[A{i}]"))
    c = [pl.commit({"p.mmd": v[0]}, "v0")]
    pl.g("checkout", "-q", "-b", "side")
    side = pl.commit({"p.mmd": v[0].replace("e[E]", "e[Side]")}, "side")
    pl.g("checkout", "-q", "main")
    c.append(pl.commit({"p.mmd": v[1]}, "v1"))
    pl.g("merge", "-q", "--no-edit", "side")
    c.append(pl.commit({"p.mmd": v[2]}, "v2"))
    for i in (3, 4, 5):
        c.append(pl.commit({"p.mmd": v[i]}, f"v{i}"))
    return pl, pl.g("rev-parse", "HEAD"), side, c


def s_p_ancestry():
    """A step whose first-parent blob matches but whose predecessor is not an
    ancestor: only the ancestry half of the predecessor rule drops it."""
    pl = Plant("panc")
    v0 = "flowchart TD\n  a[A] --> b[B]\n"
    M = "flowchart TD\n  a[A] --> b[M]\n"
    S = "flowchart TD\n  a[A] --> b[S]\n"
    c1 = pl.commit({"p.mmd": v0}, "v0")
    m = pl.commit({"p.mmd": M}, "M on main")
    pl.g("checkout", "-q", "-b", "side", c1)
    pl.commit({"p.mmd": M}, "the same M on side")
    s = pl.commit({"p.mmd": S}, "S on side")
    pl.g("checkout", "-q", "main")
    pl.g("merge", "-q", "--no-edit", "-s", "ours", "side")
    pin = pl.g("rev-parse", "HEAD")
    repo = HI.Repo(pl.path)
    seg = HI.segments(HI.walk(repo, pin)[1]["p.mmd"])[0]
    cs = [c for c, _ in seg]
    adjacent = s in cs and m in cs and cs.index(s) == cs.index(m) + 1
    check("plant: m on main and S on side are consecutive versions", adjacent, cs)
    trip, counts = HI.p_triples(repo, {"p.mmd": "F"}, HI.walk(repo, pin)[1])
    check("P: a pair whose first-parent blob matches but whose predecessor is not an ancestor is dropped",
          adjacent and counts["pairs"] >= 1 and counts["predecessor ok"] == counts["pairs"] - 1, counts)


def s_p():
    pl, pin, side, cs = _p_plant()
    repo = HI.Repo(pl.path)
    walked = HI.walk(repo, pin)
    trip, counts = HI.p_triples(repo, {"p.mmd": "F"}, walked[1])
    segs = HI.segments(walked[1]["p.mmd"])
    commits = [c for c, _ in segs[0]]
    i_side = commits.index(side)
    check("P: a non-ancestral pair drops its cases", not any(t["i"] <= i_side < t["i"] + t["a"] + t["b"] and
                                                             commits[i_side + 1] for t in trip
                                                             if t["i"] <= i_side and t["i"] + t["a"] + t["b"] > i_side),
          counts)
    v2 = commits.index(cs[2])
    check("P: a step whose first-parent blob differs from its predecessor drops the case",
          not any(t["i"] < v2 <= t["i"] + t["a"] + t["b"] for t in trip), [(t["i"], t["a"], t["b"]) for t in trip])
    check("P: the predecessor rule still keeps the linear tail", any(t["i"] >= v2 for t in trip))
    a = "x\nanchor\nold\ny\n"
    try:
        RP.replay("x\nanchor\nother\ny\n", a, "x\nanchor\nnew\ny\n")
        nc = False
    except RP.NonCommuting:
        nc = True
    check("P: a replay that cannot place an edit is non-commuting", nc)
    try:
        RP.replay("q\nanchor\nold\nanchor\n", a, "x\nanchor\nnew\ny\n")
        nc2 = False
    except RP.NonCommuting:
        nc2 = True
    check("P: a replay whose anchor is not unique is non-commuting", nc2)
    check("P: replay reproduces V[i+a+b] when applied to V[i+a]", RP.replay(a, a, "x\nanchor\nnew\ny\nz\n") ==
          "x\nanchor\nnew\ny\nz\n")
    # a record equal to the truth is not a P record; a unit neither leg touched is UNRELIABLE
    b = "flowchart TD\n  a[A] --> b[B]\n  c[C]\n"
    o = "flowchart TD\n  a[A] --> b[B]\n  c[C]\n  d[D]\n"
    t = "flowchart TD\n  a[Z] --> b[B]\n  c[C]\n"
    prep = C.prepare("F", b, o, t, R)
    M = SS.classify(o, R.get(o)).model
    dec = OR.decide(*(s.model for s in prep["states"]))[0]
    rec = [{"category": "G4", "objects": ["a"], "tier": "A", "units": [repr(("ntext", "a"))]},
           {"category": "G4", "objects": ["c"], "tier": "A", "units": [repr(("ntext", "c"))]}]
    out = C.p_filter([dict(r) for r in rec], prep, M, "flowchart TD\n  a[A] --> b[B]\n  c[Q]\n  d[D]\n", R, dec)
    check("P: a record equal to the truth is not a P record", [r["objects"] for r in out] == [["c"]], out)
    check("P: a record on a unit neither leg touched, where the truth differs, is UNRELIABLE",
          out and out[0].get("unreliable"))
    out2 = C.p_filter([dict(rec[0])], prep, M, "flowchart TD\n  a[Q] --> b[B]\n  c[C]\n  d[D]\n", R, dec)
    check("P: a record on a unit only leg T touched is a P record, not UNRELIABLE",
          len(out2) == 1 and not out2[0].get("unreliable"), out2)


def s_authors():
    A = HI.Authors()
    a1 = A.of("Ann Smith", "ann@x.org")
    a2 = A.of("A. Smith", "ANN@x.org")
    b1 = A.of("Bob", "bob@one.org")
    b2 = A.of("bob", "bob@two.org")
    n1 = A.of("Carol", "12345+carol@users.noreply.github.com")
    check("authors: two identities sharing an email are one author", a1 == a2 == A.of("Ann Smith", "ann@x.org"))
    check("authors: two identities sharing a case-folded name are one author", A.of("Bob", "bob@one.org") ==
          A.of("bob", "bob@two.org"))
    check("authors: distinct people stay distinct", A.of("Ann Smith", "ann@x.org") != A.of("Bob", "bob@one.org"))
    check("authors: a noreply address maps to its login", "e:carol" in HI.identity_keys(
        "Carol", "12345+carol@users.noreply.github.com"))
    check("bots: an author whose name or email contains bot is a bot", HI.is_bot("renovate[bot]", "x@y") and
          HI.is_bot("Ann", "ROBOT@x") and not HI.is_bot("Ann", "ann@x"))


def s_hermetic():
    b = "flowchart TD\n  a[A]\n"
    o = "flowchart TD\n  a[From O]\n"
    t = "flowchart TD\n  a[From T]\n"
    plain = G.merge_texts("c.mmd", b.encode(), o.encode(), t.encode(), TMP)
    home = tmpdir("planted-home")
    os.makedirs(os.path.join(home, ".config", "git"))
    with open(os.path.join(home, ".gitconfig"), "w") as f:
        f.write("[core]\n\tattributesFile = ~/.config/git/attributes\n[merge]\n\tconflictStyle = diff3\n")
    with open(os.path.join(home, ".config", "git", "attributes"), "w") as f:
        f.write("* merge=union\n")
    old = {k: os.environ.get(k) for k in ("HOME", "XDG_CONFIG_HOME")}
    os.environ["HOME"], os.environ["XDG_CONFIG_HOME"] = home, os.path.join(home, ".config")
    try:
        planted = G.merge_texts("c.mmd", b.encode(), o.encode(), t.encode(), TMP)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    check("hermetic merge: a ~/.gitconfig and ~/.config/git/attributes setting merge=union change no result",
          plain.unmerged and planted.unmerged and plain.merged == planted.merged)
    pl = Plant("attrs")
    pl.commit({"c.mmd": b, ".gitattributes": "*.mmd merge=union\n"}, "base")
    pl.g("checkout", "-q", "-b", "t")
    tt = pl.commit({"c.mmd": t}, "t")
    pl.g("checkout", "-q", "main")
    oo = pl.commit({"c.mmd": o}, "o")
    res = G.merge_commits(pl.path, oo, tt, ["c.mmd"], TMP)["c.mmd"]
    check("hermetic merge: a .gitattributes in the corpus's tree setting merge=union changes no result",
          res.unmerged)


def s_redaction():
    salt = "planted-salt"
    pl = Plant("ro")
    b = "flowchart LR\n  api[Zebracorn] --> zebranode\n  zebranode --> cache\n  ui --> api\n"
    pl.commit({"docs/flow.mmd": b}, "b")
    pl.g("checkout", "-q", "-b", "side")
    pl.commit({"docs/flow.mmd": b + "  worker --> zebranode\n"}, "t")
    pl.g("checkout", "-q", "main")
    pl.commit({"docs/flow.mmd": b.replace("zebranode", "pg")}, "o")
    pl.g("merge", "-q", "--no-edit", "side", check=False)
    pl.g("add", "-A")
    pl.g("commit", "-q", "-m", "m", "--allow-empty", check=False)
    ro_pin = pl.g("rev-parse", "HEAD")
    pi = Plant("ind")
    me = ("Alice Privatesson", "alice@private.example")
    pi.commit({"private/secretname.mmd": b}, "b", author=me)
    pi.g("checkout", "-q", "-b", "side")
    pi.commit({"private/secretname.mmd": b + "  worker --> zebranode\n"}, "t", author=me)
    pi.g("checkout", "-q", "main")
    pi.commit({"private/secretname.mmd": b.replace("zebranode", "pg")}, "o", author=me)
    pi.g("merge", "-q", "--no-edit", "side", check=False)
    pi.g("add", "-A")
    pi.g("commit", "-q", "-m", "m", "--allow-empty", check=False)
    in_pin = pi.g("rev-parse", "HEAD")
    shas = pi.g("rev-list", "--all").split()
    raw, red = [], []
    for repo, pin, status, ind in ((pl.path, ro_pin, "read-only", False), (pi.path, in_pin, "in", True)):
        ctx = AR.Ctx("u:000000000000" if ind else "ro/corpus", None, repo, pin, status, ind, salt, TMP)
        cs, _ = AR.arm_m(ctx, R, None)
        check(f"redaction plant: the {status}{' individual' if ind else ''} corpus yields an M case",
              any(c.get("key") for c in cs))
        raw += cs
        red += [AR.redact(c, (status, ind, salt)) for c in cs]
        red.append(AR.redact_arm0(AR.arm0(ctx, R), (status, ind, salt)))
    forbidden_names = ["Zebracorn", "zebranode", "Alice Privatesson", "alice@private.example", "secretname"]
    txt_red = json.dumps(red, default=str)
    txt_raw = json.dumps(raw, default=str)
    hits = K.redaction_hits(txt_red, forbidden_names, shas)
    if hits:
        i = txt_red.find(hits[0])
        print("    redaction hit context:", txt_red[max(0, i - 120):i + 50])
    check("redaction: no planted read-only label, individual owner or individual commit sha in output",
          raw and not hits, hits[:5])
    check("redaction: the same check on the unredacted table finds them",
          bool(K.redaction_hits(txt_raw, forbidden_names, shas)))
    check("redaction: a 7-character prefix of an individual commit is caught by the scan",
          bool(K.redaction_hits("see " + shas[0][:7], [], shas)))


def s_xfail():
    d = tmpdir("xstub")
    stubs = {"crash": "raise SystemExit(5)\n", "empty": "pass\n", "garbage": "print('not json')\n",
             "good": "import json; print(json.dumps({'exposed': True, 'records': [{'category': 'I1', "
                     "'objects': ['db','worker']}]}))\n"}
    out = {}
    for k, src in stubs.items():
        p = os.path.join(d, k + ".py")
        with open(p, "w") as f:
            f.write(src)
        xo, xf = XR.run_x(p, "F", ["a", "b", "c", "d"])
        out[k] = XR.compare([{"category": "I1", "objects": ["db", "worker"], "tier": "A"}], True, xo, xf)[0]
    check("X failure: an X that crashes makes its case a disagreement", out["crash"] is False)
    check("X failure: an X that prints nothing makes its case a disagreement", out["empty"] is False)
    check("X failure: an X that prints no JSON makes its case a disagreement", out["garbage"] is False)
    check("X agreement: equal records and exposure agree", out["good"] is True)
    xo = {"exposed": False, "records": [{"category": "I1", "objects": ["db", "worker"]}]}
    check("X disagreement: equal records, differing exposure", XR.compare(
        [{"category": "I1", "objects": ["db", "worker"], "tier": "A"}], True, xo, None)[0] is False)
    p = os.path.join(d, "slow.py")
    with open(p, "w") as f:
        f.write("import time; time.sleep(5)\n")
    xo, xf = XR.run_x(p, "F", ["a", "b", "c", "d"], timeout=1)
    check("X failure: a timeout is a disagreement", xf == "timeout" and not XR.compare([], False, xo, xf)[0])


def cli(argv, timeout=900):
    r = subprocess.run([sys.executable, "-I", "-S", "-B", os.path.join(HERE, "mermaid_spike.py")] + argv,
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def s_cli_arms():
    """Arm 0, M, P, S on fixture corpora through the CLI, unbound."""
    td, out = tmpdir("tr"), tmpdir("out")
    empty = Plant("empty")
    empty.commit({"README.txt": "x\n"}, "c")
    pl, pin, prs, _ = _pr_plant()
    pf = os.path.join(tmpdir("prs"), "prs.json")
    with open(pf, "w") as f:
        json.dump(prs, f)
    man = {"corpora": [{"label": "plant/one", "repo": pl.path, "pin": pin, "prs": pf}]}
    mf = os.path.join(tmpdir("man"), "m.json")
    with open(mf, "w") as f:
        json.dump(man, f)
    rc, o = cli(["arm0", "--fixture-manifest", mf, "--out-dir", out, "--transcript-dir", td])
    check("Arm 0 runs on a fixture corpus", rc == 0 and os.path.exists(os.path.join(out, "arm0.json")), o[-300:])
    rc, o = cli(["arms", "--fixture-manifest", mf, "--out-dir", out, "--transcript-dir", td])
    check("arms M, P and S run on a fixture corpus", rc == 0 and os.path.exists(os.path.join(out, "arms.json")), o[-300:])
    if rc == 0:
        cs = json.load(open(os.path.join(out, "arms.json")))["cases"]
        mc = [c for c in cs if c["arm"] in ("M-PR", "P") and c.get("key")]
        if mc:
            c0 = mc[0]
            rc2, o2 = cli(["repro", "--fixture-manifest", mf, "--out-dir", tmpdir("rep"), "--transcript-dir", td,
                           "--arm", c0["arm"], "--corpus", "plant/one", "--case", c0["key"],
                           "--committed", os.path.join(out, "arms.json")])
            check("the reproduction script regenerates a case byte for byte", rc2 == 0 and '"reproduces": true' in o2,
                  o2[-300:])
        else:
            check("the reproduction script regenerates a case byte for byte", False, "no case to reproduce")
    for name, man2 in (("an empty corpus", {"corpora": [{"label": "e", "repo": empty.path,
                                                           "pin": empty.g("rev-parse", "HEAD")}]}),
                       ("a pin absent from the corpus", {"corpora": [{"label": "p", "repo": pl.path,
                                                                        "pin": "f" * 40}]})):
        mf2 = os.path.join(tmpdir("man"), "m.json")
        with open(mf2, "w") as f:
            json.dump(man2, f)
        for cmd in ("arm0", "arms"):
            od = tmpdir("o")
            if cmd == "arms":
                with open(os.path.join(od, "arm0.json"), "w") as f:
                    json.dump({"corpora": {}}, f)
            rc, o = cli([cmd, "--fixture-manifest", mf2, "--out-dir", od, "--transcript-dir", td])
            check(f"{cmd} exits non-zero on {name}", rc != 0, o[-200:])
    rc, o = cli(["arm0", "--fixture-manifes", mf, "--out-dir", out, "--transcript-dir", td])
    check("an abbreviated option is refused", rc != 0)
    rc, o = cli(["arm0", "--fixture-manifest", mf, "--out-dir", out, "--out-dir", out, "--transcript-dir", td])
    check("a repeated option is refused", rc != 0 and "more than once" in o)
    r = subprocess.run([sys.executable, os.path.join(HERE, "mermaid_spike.py"), "aggregate", "--summary", mf,
                        "--out", os.path.join(out, "v.json"), "--transcript-dir", td], capture_output=True, text=True)
    check("the harness refuses to run without python3 -I -S", r.returncode != 0 and "-I -S" in r.stderr)
    sf = os.path.join(tmpdir("sum"), "s.json")
    with open(sf, "w") as f:
        json.dump({"cases": []}, f)
    rc, o = cli(["aggregate", "--summary", sf, "--out", os.path.join(out, "v.json"), "--transcript-dir", td])
    check("the aggregator exits non-zero on empty input", rc != 0 and "no input" in o)
    sf2 = os.path.join(tmpdir("sum"), "s.json")
    with open(sf2, "w") as f:
        json.dump(_sum(_base(3)), f)
    rc, o = cli(["aggregate", "--summary", sf2, "--out", os.path.join(SPIKE, "results", "v.json"), "--transcript-dir", td])
    check("an unbound run may not write under results/", rc != 0 and not os.path.exists(os.path.join(SPIKE, "results", "v.json")))
    trs = os.listdir(td)
    check("every invocation wrote a transcript, refused ones included", len(trs) >= 12, len(trs))


# ------------------------------------------------------------ aggregator

def _case(i, arm="M-merge", corpus="c0", stratum="F", authors=None, decided=True, exposed=False, outcome="JUDGED",
          records=None, agree=True, x_records=None, x_tier_a=None, reproduces=True, path_i=None, diff=None):
    recs = records or []
    return {"key": f"k{i:05d}", "diff_key": diff or f"d{i:05d}", "arm": arm, "corpus": corpus, "stratum": stratum,
            "authors": authors or [f"a{i}"], "path_i": path_i or [f"p{i}", 0, 0], "rank": 0, "decided": decided,
            "exposed": exposed, "inputs_in_subset": True, "outcome": outcome, "records": recs, "x_agree": agree,
            "x_records": x_records if x_records is not None else [{"category": r["category"], "objects": r["objects"]}
                                                                  for r in recs],
            "x_tier_a": x_tier_a if x_tier_a is not None else [[r["category"], r["objects"]] for r in recs
                                                                if r["tier"] == "A" and AG.group_of(r) == "structure"],
            "reproduces": reproduces}


def _base(n=60, **kw):
    return [_case(i, corpus=f"c{i % 5}", **kw) for i in range(n)]


def _sum(cases, row4="a", coverage=None, sealed=None, s_rates=None):
    return {"row4": row4, "cases": cases, "coverage": coverage or {"F": 0.95, "D": 0.95}, "sealed": sealed or [],
            "s_rates": s_rates or {}}


I1 = {"category": "I1", "objects": ["db", "worker"], "tier": "A"}
G2 = {"category": "G2", "objects": ["a", "b"], "tier": "A"}


def s_verdicts():
    V = AG.verdict
    cs = _base()
    cs[0] = _case(0, records=[I1], exposed=True)
    v = V(_sum(cs))
    check("verdict: identity FOUND (M-merge)", v["identity"]["verdict"] == "FOUND" and v["identity"]["arms"] == ["M-merge"])
    cs = _base()
    cs[0] = _case(0, arm="M-PR", records=[I1], exposed=True)
    check("verdict: identity FOUND (M-PR)", V(_sum(cs))["identity"]["arms"] == ["M-PR"])
    cs = _base()
    cs.append(_case(999, arm="P", records=[G2]))
    v = V(_sum(cs))
    check("verdict: structure FOUND (P)", v["structure"]["verdict"] == "FOUND" and v["structure"]["arms"] == ["P"])
    v = V(_sum(_base()))
    check("verdict: identity with 0 exposed cases is NO VERDICT (not exposed)",
          v["identity"]["verdict"] == "NO VERDICT" and v["identity"]["reason"] == "not exposed")
    cs = _base()
    cs[0] = _case(0, exposed=True, outcome="OUT-OF-SUBSET", decided=False)
    v = V(_sum(cs))
    check("verdict: one exposed case merged OUT-OF-SUBSET is NO VERDICT (1 exposed, none silent)",
          v["identity"]["reason"] == "1 exposed, none silent")
    cs = _base()
    cs[0] = _case(0, exposed=True, outcome="DUP-TITLE", decided=False)
    check("verdict: one exposed case merged DUP-TITLE is NO VERDICT (1 exposed, none silent)",
          V(_sum(cs))["identity"]["reason"] == "1 exposed, none silent")
    cs = [_case(i, corpus=f"c{i % 5}", exposed=True, outcome="E" if i % 2 else "JUDGED",
                records=[] if i % 2 else [dict(I1, tier="B")]) for i in range(60)]
    v = V(_sum(cs))
    check("verdict: 60 exposed cases, some E and some B, is NO VERDICT (60 exposed, none silent), never NOT FOUND",
          v["identity"]["verdict"] == "NO VERDICT" and v["identity"]["reason"] == "60 exposed, none silent")
    sealed_d = [{"name": "s1", "group": "identity", "line": "A", "f": True, "h": False, "x": False}]
    v = V(_sum(_base(), sealed=sealed_d))
    check("verdict: identity with a disputed sealed fixture is NO VERDICT naming it",
          v["identity"]["verdict"] == "NO VERDICT" and "s1" in v["identity"]["reason"])
    void_i = [{"name": "s2", "group": "identity", "line": "A", "f": True, "h": False, "x": True}]
    cs = _base()
    cs[0] = _case(0, records=[I1], exposed=True)
    v = V(_sum(cs, sealed=void_i))
    check("verdict: identity VOID turns a FOUND into found in a voided group",
          v["identity"]["verdict"] == "NO VERDICT" and v["identity"]["reason"] == "VOID" and
          v["lists"]["found_in_voided_group"]["identity"])
    v = V(_sum(_base(), sealed=void_i))
    check("verdict: identity VOID with no FOUND is NO VERDICT (VOID)", v["identity"]["reason"] == "VOID")
    cs = _base(60)
    cs[0] = _case(0, outcome="E")
    v = V(_sum(cs))
    check("verdict: structure NOT FOUND at 60 decided cases of which some are E", v["structure"]["verdict"] == "NOT FOUND"
          and v["structure"]["n"] == 60)
    v = V(_sum(_base(59)))
    check("verdict: 59 decided cases is NO VERDICT", v["structure"]["verdict"] == "NO VERDICT" and "floor" in v["structure"]["reason"])
    cs = [_case(i, corpus="big" if i < 31 else f"c{i % 5}") for i in range(60)]
    check("verdict: 60 cases with 31 from one corpus is NO VERDICT (cap 30)",
          V(_sum(cs))["structure"]["verdict"] == "NO VERDICT" and V(_sum(cs))["structure"]["n"] == 59)
    cs = [_case(i, corpus=f"c{i % 5}", authors=["same"] if i < 31 else [f"a{i}"]) for i in range(60)]
    check("verdict: 60 cases with 31 from one author is NO VERDICT (cap 30)", V(_sum(cs))["structure"]["n"] == 59)
    cs = [_case(i, corpus=f"c{i % 5}", arm="P" if i < 31 else "M-merge") for i in range(60)]
    v = V(_sum(cs))
    check("verdict: P supplying 31 of 60 is NOT FOUND stated as a bound on replayed edits",
          v["structure"]["verdict"] == "NOT FOUND" and "replayed" in v["structure"]["bounds"])
    cs = [_case(i, corpus=f"c{i % 5}") for i in range(97)] + [_case(100 + i, corpus=f"c{i % 5}", agree=False) for i in range(3)]
    cs = [dict(c, corpus=f"c{i % 4}", authors=[f"a{i}"]) for i, c in enumerate(cs)]
    v = V(_sum(cs, coverage={"F": 1.0}))
    check("verdict: 97.9% agreement or less is NO VERDICT", v["structure"]["n"] < 60 or
          ("agreement" in v["structure"].get("reason", "")), v["structure"])
    cs = [_case(i, corpus=f"c{i % 3}") for i in range(90)]
    cs[5] = dict(cs[5], x_agree=False)
    cs[6] = dict(cs[6], x_agree=False)
    v = V(_sum(cs))
    check("verdict: 58 of 60 agreeing (96.7%) is NO VERDICT on agreement", v["structure"]["verdict"] == "NO VERDICT" and
          "agreement" in v["structure"]["reason"], v["structure"])
    cs = [_case(i, corpus=f"c{i % 3}", agree=(i != 7)) for i in range(60)]
    v = V(_sum(cs))
    check("verdict: 59 of 60 agreeing (98.3%) passes the agreement bar", v["structure"]["verdict"] == "NOT FOUND", v["structure"])
    v = V(_sum([_case(0, decided=False)]))
    check("verdict: agreement over zero cases is NO VERDICT", "zero cases" in v["structure"]["reason"])
    cs = _base()
    cs[0] = _case(0, records=[G2], x_records=[], x_tier_a=[])
    v = V(_sum(cs))
    check("verdict: a structure tier-A record from H only is NO VERDICT, never NOT FOUND",
          v["structure"]["verdict"] == "NO VERDICT" and "tier-A" in v["structure"]["reason"], v["structure"])
    check("verdict: an H-only structure record is a blocked record (F7)", any(
        b["failed"] == "F7" for b in v["lists"]["blocked"]["structure"]))
    cs = _base()
    cs[0] = _case(0, x_tier_a=[["G2", ["a", "b"]]])
    v = V(_sum(cs))
    check("verdict: a structure tier-A record from X only is NO VERDICT", v["structure"]["verdict"] == "NO VERDICT" and
          "tier-A" in v["structure"]["reason"])
    cs = _base()
    cs[0] = _case(0, records=[G2], reproduces=False)
    v = V(_sum(cs))
    check("verdict: one blocked structure record among the decided cases is NO VERDICT",
          v["structure"]["verdict"] == "NO VERDICT" and "blocked" in v["structure"]["reason"])
    cs = _base()
    cs[0] = _case(0, records=[I1], reproduces=False, exposed=True)
    v = V(_sum(cs))
    check("verdict: one blocked identity record does not touch the structure verdict",
          v["structure"]["verdict"] == "NOT FOUND" and v["lists"]["blocked"]["identity"])
    for line in ("A", "B"):
        dsp = [{"name": f"d{line}", "group": "structure", "line": line, "f": True, "h": False, "x": False}]
        v = V(_sum(_base(), sealed=dsp))
        cs = _base()
        cs[0] = _case(0, records=[G2])
        v2 = V(_sum(cs, sealed=dsp))
        check(f"verdict: a disputed structure fixture on the {line} line is NO VERDICT for NOT FOUND and leaves FOUND",
              v["structure"]["verdict"] == "NO VERDICT" and v2["structure"]["verdict"] == "FOUND")
    vs = [{"name": "v", "group": "structure", "line": "A", "f": True, "h": False, "x": True}]
    cs = _base()
    cs[0] = _case(0, records=[G2])
    v = V(_sum(cs, sealed=vs))
    check("verdict: a structure VOID group turns a FOUND into found in a voided group",
          v["structure"]["verdict"] == "NO VERDICT" and v["lists"]["found_in_voided_group"]["structure"])
    cs = [_case(i, corpus=f"c{i % 5}", stratum="D" if i < 10 else "F") for i in range(60)]
    cs.append(_case(500, stratum="D", records=[G2]))
    v = V(_sum(cs, coverage={"F": 0.95, "D": 0.899}))
    check("verdict: a stratum at 89.9% coverage adds nothing to the floor, and its FOUND still counts",
          v["structure"]["verdict"] == "FOUND" and AG.counted(cs, {"F": 0.95, "D": 0.899}) and
          all(c["stratum"] == "F" for c in AG.counted(cs, {"F": 0.95, "D": 0.899})))
    cs = _base()
    cs.append(_case(700, arm="P", records=[I1], exposed=True))
    v = V(_sum(cs))
    check("verdict: P cases never count toward identity; a P identity record is a P anomaly, never FOUND",
          v["identity"]["verdict"] == "NO VERDICT" and v["identity"]["reason"] == "not exposed" and v["lists"]["p_anomalies"])
    check("verdict: the P anomaly's case, otherwise decided, counts toward the structure floor",
          any(c["key"] == "k00700" for c in AG.counted(cs, {"F": 0.95})))
    v = V(_sum(_base(), row4="a", s_rates={"F": {"x_confirmed_identity_a": 3}}))
    check("verdict: row 4 (a): with no real FOUND the identity verdict is a NO VERDICT label, never MECHANISM SHOWN",
          v["identity"]["verdict"] == "NO VERDICT")
    v = V(_sum(_base(), row4="c", s_rates={"F": {"x_confirmed_identity_a": 3}}))
    check("verdict: row 4 (c): a non-zero X-confirmed S rate gives MECHANISM SHOWN, frequency unmeasured",
          v["identity"]["verdict"] == "MECHANISM SHOWN, frequency unmeasured")
    v = V(_sum(_base(), row4="c", s_rates={"F": {"identity_a": 4, "x_confirmed_identity_a": 0}}))
    check("verdict: row 4 (c): S identity records X does not confirm give MECHANISM NOT SHOWN",
          v["identity"]["verdict"] == "MECHANISM NOT SHOWN")
    v = V(_sum(_base(), row4="c", s_rates={"F": {"x_confirmed_identity_a": 0}}))
    check("verdict: row 4 (c): a zero S rate gives MECHANISM NOT SHOWN", v["identity"]["verdict"] == "MECHANISM NOT SHOWN")
    v = V(_sum(_base(), row4="c", s_rates={"F": {"x_confirmed_identity_a": 3}}, sealed=void_i))
    check("verdict: row 4 (c): a VOID identity group gives NO VERDICT (VOID) in place of MECHANISM SHOWN",
          v["identity"]["reason"] == "VOID")
    v = V(_sum(_base(), row4="c", s_rates={"F": {"x_confirmed_identity_a": 3}}, sealed=sealed_d))
    check("verdict: row 4 (c): a disputed identity fixture gives NO VERDICT (disputed)",
          "disputed" in v["identity"]["reason"])
    cs = _base()
    cs[0] = _case(0, records=[I1], exposed=True)
    v = V(_sum(cs, row4="c", s_rates={"F": {"x_confirmed_identity_a": 3}}))
    check("verdict: row 4 (c): a real FOUND gives FOUND (arm), not MECHANISM SHOWN", v["identity"]["verdict"] == "FOUND")
    cs = _base(60)
    cs.append(dict(_case(1), key="k00001"))
    check("units: a duplicated triple counts once", len(AG.counted(cs, {"F": 1})) == 60)
    cs = _base(60)
    cs.append(_case(800, diff="d00003"))
    check("units: a copied file with the same diffs counts once", len(AG.counted(cs, {"F": 1})) == 60)
    cs = [_case(i, arm="P", corpus=f"c{i % 5}", path_i=["p", 0, 0]) for i in range(3)]
    check("units: P contributes at most one case per (path, i)", len(AG.counted(cs, {"F": 1})) == 1)
    cs = _base()
    cs[3] = dict(cs[3], records=[dict(G2, tier="C", unreliable="x")])
    check("units: an UNRELIABLE record's case does not count toward the floor", len(AG.counted(cs, {"F": 1})) == 59)
    try:
        V(_sum([]))
        empty = False
    except ValueError:
        empty = True
    check("the aggregator refuses empty input", empty)


def s_subset_refusals():
    """V1's refusal half: H refuses each out-of-subset construct Appendix A
    lists (needs no V-fixture)."""
    texts = {
        "markdown-string label": 'flowchart TD\n  A["`**bold**`"]\n',
        "icon node": 'flowchart TD\n  A@{ icon: "fa:user", label: "x" }\n',
        "image node": 'flowchart TD\n  A@{ img: "https://example.com/x.png" }\n',
        "@{ } key other than shape and label": 'flowchart TD\n  A@{ shape: rect, pos: "b" }\n',
        "two untitled subgraphs sharing a title": "flowchart TD\n  subgraph Front End\n    A\n  end\n"
                                                  "  subgraph Front End\n    B\n  end\n",
        "explicit subgraph id subGraphN": "flowchart TD\n  subgraph Other Box\n    B\n  end\n"
                                          "  subgraph subGraph0 [T]\n    A\n  end\n",
        "edge end naming a user-defined edge id": "flowchart TD\n  A e1@--> B\n  e1 --> C\n",
        "statement H does not parse (ellipse shape)": "flowchart TD\n  A(-x-)\n",
    }
    for name, t in texts.items():
        s = SS.classify(t, R.get(t))
        check(f"V1 refusal: H refuses {name}", s.status != "in", s.status)
    s = SS.classify(texts["two untitled subgraphs sharing a title"], R.get(texts["two untitled subgraphs sharing a title"]))
    check("V1 refusal: two untitled subgraphs of one title are DUP-TITLE", s.status == "duptitle")
    t = "flowchart TD\n  A[Alpha] --> B\n  subgraph S [Box]\n    B\n  end\n"
    check("V1: a plain chart is in the subset", SS.classify(t, R.get(t)).status == "in")
    r = json.loads(json.dumps(R.get(t)))
    r["vertices"][0]["text"] = "Something else"
    check("subset: a text whose H model differs from R's is out of the subset", SS.classify(t, r).status == "out")
    check("V1: H on empty input is refused", SS.classify("", R.get("")).status != "in")


def s_fuzz():
    """H's development check, kept as a V3 check: H's model equals R's on
    random synthetic flowcharts wherever both accept, and H accepts most."""
    rng = random.Random(20261009)
    ids = ["A", "B", "db", "api", "node1", "x1", "o", "v", "vpc", "default", "é", "1", "S", "e1", "endpoint"]
    labels = ["Alpha", "Two words", "a<br>b", "a<br/>b", "x & y", "it's", '"quoted"', "n-1", "Ünï", "50%"]
    shapes = [("[", "]"), ("(", ")"), ("([", "])"), ("[[", "]]"), ("[(", ")]"), ("((", "))"), (">", "]"),
              ("{", "}"), ("{{", "}}"), ("[/", "\\]"), ("[\\", "/]"), ("(((", ")))")]
    links = ["-->", "---", "-.->", "==>", "~~~", "--o", "--x", "<-->", "o--o"]

    def vert():
        i = rng.choice(ids)
        if rng.random() < 0.5:
            return i
        if rng.random() < 0.1:
            return f'{i}@{{ shape: {rng.choice(["rounded", "cyl", "diam"])}, label: "{rng.choice(["Hi", "Two words"])}" }}'
        a, b = rng.choice(shapes)
        return f"{i}{a}{rng.choice(labels)}{b}"

    def stmt(depth=0):
        r = rng.random()
        if r < 0.65:
            s = vert()
            for _ in range(rng.randint(0, 2)):
                lk = rng.choice(links)
                r2 = rng.random()
                s += (f" {lk}|{rng.choice(labels)}| " if r2 < 0.2 else
                      f" e{rng.randint(1, 2)}@{lk} " if r2 < 0.3 else f" {lk} ") + vert()
            return [s]
        if r < 0.75 and depth < 2:
            return [rng.choice(["subgraph " + rng.choice(ids), "subgraph Front End", "subgraph sg [Title]"])] + \
                ["  " + x for _ in range(rng.randint(0, 2)) for x in stmt(depth + 1)] + ["end"]
        if r < 0.85:
            return [f"style {rng.choice(ids)} fill:#f96"]
        if r < 0.92:
            return [f"classDef c{rng.randint(1, 2)} fill:#f9f", f"class {rng.choice(ids)} c1"]
        return [f'click {rng.choice(ids)} "https://example.com/p"']
    texts = []
    for _ in range(200):
        lines = [rng.choice(["flowchart TD", "graph LR", "flowchart-elk TB"])]
        for _ in range(rng.randint(1, 6)):
            lines += ["  " + x for x in stmt()]
        texts.append("\n".join(lines) + "\n")
    rs = R.get_many(texts)
    st = [SS.classify(t, r) for t, r in zip(texts, rs)]
    diffs = [s.reason for s in st if s.status == "out" and "differs" in (s.reason or "")]
    parsed = [s for s in st if s.status != "noparse"]
    ins = sum(1 for s in parsed if s.status == "in")
    check("fuzz: H's model equals R's wherever both accept (200 random charts)", not diffs, diffs[:2])
    check("fuzz: H accepts most charts R parses", parsed and ins / len(parsed) > 0.8, f"{ins}/{len(parsed)}")


def s_blind():
    check("blind: the committed X spec is a fresh cut of the document",
          open(os.path.join(SPIKE, "blind", "x", "SPEC.md"), encoding="utf-8").read() == BL.x_spec())
    spec = BL.x_spec()
    check("blind: X's spec holds §4, §5, Appendices A and C and Appendix D's extractor contract, and not §6, "
          "Appendix B or E", all(h in spec for h in BL.SECTIONS) and "## 6. FOUND" not in spec and
          "## Appendix B" not in spec and "## Appendix E" not in spec and "**Extractor.**" in spec)
    check("blind: X's spec leaves out Appendix D's fixture contract (§10.3)", "**Fixtures.**" not in spec
          and "expect.json" not in spec)
    from ms import hparse  # noqa: F401
    doc = os.path.join(SPIKE, "blind", "mermaid-12.1.0-flowchart.md")
    blob = subprocess.run(["git", "hash-object", doc], capture_output=True, text=True).stdout.strip()
    check("blind: the Mermaid document is mermaid@12.1.0's docs/syntax/flowchart.md", blob == BL.MERMAID_DOC_BLOB)
    check("blind: Appendix E's prompts are cut verbatim", BL.prompt("X").startswith("You are writing a program") and
          BL.prompt("F").startswith("You are writing test cases"))


VAL_A = {"sealed_sha256": "a" * 64, "lockfile_sha256": "b" * 64,
         "bundles": {"org/corpus": {"file": "x.bundle", "sha256": "d" * 64, "prs_file": "x.prs.json",
                                    "prs_sha256": "e" * 64}}}


def s_binding():
    """The binding (ms/binding.py) on a planted copy of the spike."""
    root = tmpdir("bind")
    sp = os.path.join(root, "spike", "mermaid")
    os.makedirs(sp)
    for d in ("harness", "r"):
        shutil.copytree(os.path.join(SPIKE, d), os.path.join(sp, d),
                        ignore=shutil.ignore_patterns("node_modules", "__pycache__"))
    shutil.copy(os.path.join(SPIKE, "PRE-REGISTRATION.md"), sp)
    with open(os.path.join(sp, "LOG.md"), "w") as f:
        f.write("# log\n\n- sealed fixtures sha256: " + "a" * 64 + "\n")
    e = G.env(tmpdir("h"))

    def g(*a):
        return subprocess.run(["git", "-C", root, *a], capture_output=True, text=True, env=e)
    g("init", "-q", "-b", "main")
    g("add", "-A")
    g("commit", "-q", "-m", "harness")
    st = BD.check(sp, "arm0")
    check("binding: no VALIDATION is not bound", not st["bound"])
    os.makedirs(os.path.join(sp, "results"))
    with open(os.path.join(sp, "results", "VALIDATION"), "w") as f:
        json.dump(VAL_A, f)
    g("add", "-A")
    g("commit", "-q", "-m", "validation")
    st = BD.check(sp, "arm0")
    check("binding: a validation commit adding VALIDATION only is bound", st["bound"], st["reasons"])
    with open(os.path.join(sp, "results", "stray.txt"), "w") as f:
        f.write("x")
    check("binding: an uncommitted file under results/ is refused", not BD.check(sp, "arm0")["bound"])
    os.remove(os.path.join(sp, "results", "stray.txt"))
    BD.mark_executed(sp, "arm0", "t.txt")
    check("binding: an arm's marker in the work tree refuses that arm", not BD.check(sp, "arm0")["bound"])
    g("add", "-A")
    g("commit", "-q", "-m", "arm0 ran")
    os.remove(os.path.join(sp, "results", "executed", "arm0.json"))
    g("add", "-A")
    g("commit", "-q", "-m", "marker removed")
    check("binding: a marker deleted later still refuses the arm (history)", not BD.check(sp, "arm0")["bound"])
    check("binding: another arm is still bound", BD.check(sp, "arms")["bound"], BD.check(sp, "arms")["reasons"])
    with open(os.path.join(sp, "harness", "ms", "oracle.py"), "a") as f:
        f.write("# edit\n")
    check("binding: an uncommitted harness edit is refused", not BD.check(sp, "arms")["bound"])
    g("add", "-A")
    g("commit", "-q", "-m", "late harness edit")
    check("binding: a commit after validation touching the harness is refused", not BD.check(sp, "arms")["bound"])
    g("revert", "--no-edit", "HEAD")
    st = BD.check(sp, "arms")
    check("binding: a later edit and its revert, the tree back to the validation commit's, is still refused",
          not st["bound"] and any("after the validation commit" in x for x in st["reasons"]), st["reasons"])
    rv = subprocess.run(["bash", os.path.join(HERE, "reverify.sh"), sp], capture_output=True, text=True)
    check("reverify: fails when a later commit touches the harness", rv.returncode != 0 and "FAIL" in rv.stdout,
          rv.stdout[-300:])
    root2 = tmpdir("bind2")
    sp2 = os.path.join(root2, "spike", "mermaid")
    shutil.copytree(sp, sp2)
    shutil.rmtree(os.path.join(sp2, "results"))

    def g2(*a):
        return subprocess.run(["git", "-C", root2, *a], capture_output=True, text=True, env=e)
    g2("init", "-q", "-b", "main")
    g2("add", "-A")
    g2("commit", "-q", "-m", "harness")
    os.makedirs(os.path.join(sp2, "results"))
    with open(os.path.join(sp2, "results", "VALIDATION"), "w") as f:
        json.dump(VAL_A, f)
    with open(os.path.join(sp2, "harness", "ms", "aggregate.py"), "a") as f:
        f.write("FLOOR = 1\n")
    g2("add", "-A")
    g2("commit", "-q", "-m", "validation that also edits the harness")
    check("binding: a validation commit that also edits the harness is refused", not BD.check(sp2, "arm0")["bound"])
    rv = subprocess.run(["bash", os.path.join(HERE, "reverify.sh"), sp2], capture_output=True, text=True)
    check("reverify: fails when the validation commit edits the harness", rv.returncode != 0, rv.stdout[-300:])
    root3 = tmpdir("bind3")
    sp3 = os.path.join(root3, "spike", "mermaid")
    shutil.copytree(sp2, sp3)
    shutil.rmtree(os.path.join(sp3, "results"))

    def g3(*a):
        return subprocess.run(["git", "-C", root3, *a], capture_output=True, text=True, env=e)
    g3("init", "-q", "-b", "main")
    g3("add", "-A")
    g3("commit", "-q", "-m", "harness")
    os.makedirs(os.path.join(sp3, "results"))
    with open(os.path.join(sp3, "results", "VALIDATION"), "w") as f:
        json.dump(VAL_A, f)
    g3("add", "-A")
    g3("commit", "-q", "-m", "validation")
    rv = subprocess.run(["bash", os.path.join(HERE, "reverify.sh"), sp3], capture_output=True, text=True)
    check("reverify: passes on a clean validation history", rv.returncode == 0 and "reverify: PASS" in rv.stdout,
          rv.stdout[-300:])
    with open(os.path.join(sp3, "results", "VALIDATION"), "w") as f:
        json.dump(dict(VAL_A, sealed_sha256="c" * 64), f)
    g3("commit", "-q", "-am", "VALIDATION changed")
    check("binding: VALIDATION changed after it was added is refused", not BD.check(sp3, "arm0")["bound"])
    root4 = tmpdir("bind4")
    sp4 = os.path.join(root4, "spike", "mermaid")
    shutil.copytree(sp2, sp4)
    shutil.rmtree(os.path.join(sp4, "results"))
    with open(os.path.join(sp4, "harness", "ms", "aggregate.py"), "w") as f:
        f.write(open(os.path.join(SPIKE, "harness", "ms", "aggregate.py")).read())
    with open(os.path.join(sp4, "LOG.md"), "w") as f:
        f.write("# log\n\n- sealed fixtures sha256: " + "f" * 64 + "\n")

    def g4(*a):
        return subprocess.run(["git", "-C", root4, *a], capture_output=True, text=True, env=e)
    g4("init", "-q", "-b", "main")
    g4("add", "-A")
    g4("commit", "-q", "-m", "harness and commit 2's sealed hash")
    os.makedirs(os.path.join(sp4, "results"))
    with open(os.path.join(sp4, "results", "VALIDATION"), "w") as f:
        json.dump(VAL_A, f)
    g4("add", "-A")
    g4("commit", "-q", "-m", "validation")
    st = BD.check(sp4, "arm0")
    check("binding: VALIDATION's sealed hash must equal the one LOG.md records (commit 2)",
          not st["bound"] and any("LOG.md" in r for r in st["reasons"]), st["reasons"])
    check("binding: no bundle is read while the derivation reports a reason", K.bundles(sp4) == {})
    root5 = tmpdir("bind5")
    sp5 = os.path.join(root5, "spike", "mermaid")
    os.makedirs(sp5)
    shutil.copy(os.path.join(SPIKE, "PRE-REGISTRATION.md"), sp5)
    with open(os.path.join(sp5, "LOG.md"), "w") as f:
        f.write("# log\n\n- sealed fixtures sha256: " + "a" * 64 + "\n- sealed fixtures sha256: " + "a" * 64 + "\n")

    def g5(*a):
        return subprocess.run(["git", "-C", root5, *a], capture_output=True, text=True, env=e)
    g5("init", "-q", "-b", "main")
    g5("add", "-A")
    g5("commit", "-q", "-m", "commit 2 records the hash twice")
    os.makedirs(os.path.join(sp5, "results"))
    with open(os.path.join(sp5, "results", "VALIDATION"), "w") as f:
        json.dump(VAL_A, f)
    g5("add", "-A")
    g5("commit", "-q", "-m", "validation")
    vc_, v_, rs_ = BD.derive(sp5)
    check("binding: LOG.md recording the sealed hash twice is refused", rs_ and any("LOG.md" in r for r in rs_), rs_)
    try:
        BD.validate_content(dict(VAL_A, bundles={"x": {"file": "a/b", "sha256": "d" * 64, "prs_file": "p",
                                                        "prs_sha256": "e" * 64}}))
        bad = False
    except ValueError:
        bad = True
    check("binding: a malformed bundle entry in VALIDATION is refused", bad)
    rv = subprocess.run(["bash", os.path.join(HERE, "reverify.sh"), sp3], capture_output=True, text=True)
    check("reverify: fails when VALIDATION changed", rv.returncode != 0)



# ------------------------------------------------- oracle units, directly

def upd(M, changes):
    out = dict(M)
    out.update(changes)
    return out


def s_oracle_units():
    """Categories, tiers and refusal cases on hand-built models."""
    base = {("exist", "a"): ("node",), ("exist", "b"): ("node",), ("ntext", "a"): "A", ("ntext", "b"): "B",
            ("shape", "a"): "square", ("shape", "b"): "square", ("nhold", "a"): "", ("nhold", "b"): "",
            ("exist", "s"): ("subgraph",), ("stitle", "s"): "Box", ("shold", "s"): "",
            ("link", "a"): ("https://x.org/", None)}
    B = dict(base)

    def recs(O, T, M):
        return OR.judge(B, O, T, M, set())[0]
    O = upd(B, {("stitle", "s"): "New box"})
    M = upd(B, {("stitle", "s"): "Other"})
    r = recs(O, B, M)
    check("G4: a subgraph title merged wrong is G4", any(x["category"] == "G4" and x["objects"] == ["s"] for x in r), r)
    O = upd(B, {("link", "a"): ("https://y.org/", None)})
    M = upd(B, {("link", "a"): ("https://z.org/", None)})
    check("G4: a click target merged wrong is G4", any(x["category"] == "G4" for x in recs(O, B, M)))
    O = upd(B, {("nhold", "a"): "s"})
    M = dict(B)
    r = recs(O, B, M)
    check("G3: a membership merged wrong is G3, tier A", any(x["category"] == "G3" and x["tier"] == "A" for x in r), r)
    O = upd(B, {("ntext", "a"): "From O"})
    T = upd(B, {("ntext", "a"): "From T"})
    M = upd(B, {("ntext", "a"): "Neither"})
    r = recs(O, T, M)
    check("MC: an eligible text conflict is MC in group G4, tier A",
          any(x["category"] == "MC" and x.get("group") == "G4" and x["tier"] == "A" for x in r), r)
    O = upd(B, {("exist", "k"): ("node",)})
    T = upd(B, {("exist", "k"): ("edge",)})
    check("collision: both legs add k with differing kinds and nothing else", any(
        kind == "collision" and k == "k" for kind, k, _ in OR.refusals(B, O, T, *OR.decide(B, O, T)[:2])))
    e = {("exist", "e"): ("edge",), ("eref", "e"): ("a", "b", "solid:none>arrow")}
    O = upd(upd(B, e), {("etext", "e"): "x"})
    T = upd(upd(B, e), {("etext", "e"): "y"})
    r = recs(O, T, dict(B))
    check("R-ident: a user-id edge both legs add differently, lost in the merge, is I2 and G2 (only G1 is excluded)",
          any(x["category"] == "I2" for x in r) and any(x["category"] == "G2" and "e" in x["objects"] for x in r), r)
    O = upd(upd(B, {("etext", "e"): "x"}), e)
    M = upd(upd(B, e), {("etext", "e"): "q"})
    check("G4: a user-id edge's label merged wrong is G4", any(x["category"] == "G4" and x["objects"] == ["e"]
                                                              for x in recs(upd(B, e), O, M)))


def s_l5():
    """R-L5: a duplicated edge's two ends newly fail L5 (§5.3 G2 objects,
    §5.4)."""
    base = "flowchart TD\n  A[Alpha] --> B[Beta]\n  C[Gamma]\n  x1[x1]\n  x2[x2]\n  x3[x3]\n  D[Delta]\n"
    o = base.replace("  C[Gamma]\n", "  A --> C\n  C[Gamma]\n")
    t = base.replace("  D[Delta]\n", "  D[Delta]\n  A --> C\n")
    p, r = run_case("F", base, o, t)
    check("L5: the same edge added on both legs is G2 at tier B, through L5 on its ends",
          has(r, "G2", "B") and not has(r, "G2", "A") and "L5:A" in r.get("lint_new", []), cats(r))


class _Ctx:
    label = "plant/p"


def s_p_x():
    """§10.5 with §8.3: X never sees the truth, so it is compared with H's
    records before P's truth filter."""
    v0 = "flowchart TD\n  A[Alpha]\n  B[Beta]\n"
    v1 = v0 + "  C[Gamma]\n"
    v2 = "flowchart TD\n  A[Alpha]\n  D[Delta]\n  B[Beta]\n  C[Gamma]\n"
    t = RP.replay(v0, v1, v2)
    d = tmpdir("xp")
    x = os.path.join(d, "x.py")
    with open(x, "w") as f:
        f.write("import json\nprint(json.dumps({'exposed': False, 'records': [{'category': 'S-ORDER', "
                "'objects': []}]}))\n")
    c = AR.evaluate(_Ctx(), {"arm": "P", "path": "c.mmd"}, "F", [v0, v1, t],
                    lambda: G.merge_texts("c.mmd", v0.encode(), v1.encode(), t.encode(), TMP), R, x, truth=v2)
    check("P: H's unfiltered records hold the S-ORDER X reports", any(
        r["category"] == "S-ORDER" for r in c.get("x_records", [])) and c["outcome"] == "JUDGED")
    check("P: X agrees with H's records before the truth filter", c.get("x_agree") is True, c.get("x_detail"))
    check("P: the truth filter still removes the record from H's P records",
          not any(r["category"] == "S-ORDER" for r in c["records"]), c["records"])


def s_aggregate_scope():
    """§9.1 and §10.5 over every decided real-arm case; F8 needs a
    reproduction; S never qualifies; k and P's fallback follow §7.5 and §8.3."""
    V = AG.verdict
    cs = [_case(i, corpus="c%d" % (i % 3)) for i in range(30)] + [_case(100 + i, corpus="cx") for i in range(30)]
    v = V(_sum(cs + [_case(999, corpus="cx", x_tier_a=[["G2", ["a", "b"]]], agree=False)]))
    check("scope: an X-only tier-A record in a decided case over the corpus cap is NO VERDICT",
          v["structure"]["verdict"] == "NO VERDICT" and "tier-A" in v["structure"]["reason"], v["structure"])
    v = V(_sum(cs + [_case(998, corpus="c0", x_tier_a=[["G2", ["a", "b"]]], agree=False, diff="d00000")]))
    check("scope: an X-only tier-A record in a decided duplicate-diff case is NO VERDICT",
          v["structure"]["verdict"] == "NO VERDICT" and "tier-A" in v["structure"]["reason"], v["structure"])
    cs = _base()
    cs[0] = _case(0, outcome="E", records=[G2])
    check("F3: a tier-A record in a case that is not JUDGED is not FOUND", V(_sum(cs))["structure"]["verdict"] != "FOUND")
    cs = _base()
    cs[0] = _case(0, records=[dict(G2, tier="B")])
    v = V(_sum(cs))
    check("a tier-B record is never blocked", not v["lists"]["blocked"]["structure"] and v["lists"]["with_refusals"])
    cs = _base()
    cs.append(_case(600, arm="S", records=[G2]))
    v = V(_sum(cs))
    check("S: a tier-A record from S is never FOUND, is listed blocked (F1), and S never counts toward the floor",
          v["structure"]["verdict"] == "NOT FOUND" and any(b["failed"] == "F1" and b["arm"] == "S"
                                                            for b in v["lists"]["blocked"]["structure"])
          and all(c["arm"] != "S" for c in AG.counted(cs, {"F": 1})))
    cs = _base()
    cs[0] = dict(_case(0, exposed=True), inputs_in_subset=False)
    check("k: an exposed case whose inputs are not all in the subset does not count",
          V(_sum(cs))["identity"]["reason"] == "not exposed")
    cs = _base()
    cs[0] = _case(0, exposed=True)
    cs[1] = _case(1, exposed=True, diff="d00000")
    check("k: two exposed cases with one pair of model diffs count once (§7.5)",
          V(_sum(cs))["identity"]["reason"] == "1 exposed, none silent")
    cs = [dict(_case(i, corpus=f"c{i % 4}", agree=i >= 2)) for i in range(100)]
    v = V(_sum(cs))
    check("agreement: exactly 98% passes", v["structure"]["n"] == 100 and v["structure"]["verdict"] == "NOT FOUND",
          v["structure"])
    p11 = dict(_case(1, arm="P", path_i=["p", 0, 0], diff="d00000"), rank=0)
    p13 = dict(_case(2, arm="P", path_i=["p", 0, 0]), rank=1)
    cnt = AG.counted([_case(0), p11, p13], {"F": 1})
    check("P: a decided (1,1) case dropped as a duplicate is not replaced by its (1,3) case",
          sorted(c["key"] for c in cnt) == ["k00000"], [c["key"] for c in cnt])
    cnt = AG.counted([p13, dict(p11, diff_key="dzzz")], {"F": 1})
    check("P: rank (1,1) is preferred over (1,3) for a (path, i)", [c["key"] for c in cnt] == ["k00001"])


def _results_dir(cases, sealed=None, repro=None):
    d = tmpdir("results")
    with open(os.path.join(d, "arms.json"), "w") as f:
        json.dump({"cases": cases, "s_rates": {}}, f)
    with open(os.path.join(d, "arm0.json"), "w") as f:
        json.dump({"coverage": {"F": 1.0}}, f)
    with open(os.path.join(d, "sealed.json"), "w") as f:
        json.dump({"sealed": sealed or []}, f)
    os.makedirs(os.path.join(d, "repro"))
    for k, ok in (repro or {}).items():
        with open(os.path.join(d, "repro", k + ".json"), "w") as f:
            json.dump({"case": k, "reproduces": ok}, f)
    return d


class _Tr:
    def __init__(self):
        self.marked = False
        self.path = "t.txt"

    def mark_executed(self):
        self.marked = True


def s_bound_aggregate():
    """H4, R31, R33: the bound aggregate's input."""
    import mermaid_spike as CLI
    cs = _base(3)
    cs[0] = _case(0, records=[G2])
    d = _results_dir(cs)
    summary, missing = CLI.bound_summary(d)
    check("bound aggregate: row 4 is (a)", summary["row4"] == "a")
    check("bound aggregate: a real-arm tier-A record with no reproduction is listed as missing", missing == ["k00000"])
    check("bound aggregate: a case with no reproduction result does not reproduce",
          summary["cases"][0]["reproduces"] is False)
    old = CLI.RESULTS
    CLI.RESULTS = d
    tr = _Tr()
    try:
        CLI.cmd_aggregate(argparse.Namespace(), tr, True)
        refused = False
    except SystemExit as e:
        refused = "k00000" in str(e.code)
    finally:
        CLI.RESULTS = old
    check("bound aggregate: refuses, naming the missing repro keys, before it marks itself executed",
          refused and not tr.marked)
    d = _results_dir(cs, repro={"k00000": True})
    summary, missing = CLI.bound_summary(d)
    check("bound aggregate: a reproduced record is not missing", not missing and summary["cases"][0]["reproduces"])


def _sealed_tar(d, tiers, records, more=()):
    """A sealed tar of the bare hole #2 fixture "fx" (and any `more`
    (name, tiers, records) fixtures on the same texts), sorted names and
    zeroed times; returns (path, sha256(nonce + tar)) with nonce 01 * 32."""
    import hashlib
    import io
    import tarfile
    b = "flowchart LR\n  api --> db\n  db --> cache\n  ui --> api\n"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for name, ti_, rec in [("fx", tiers, records)] + list(more):
            fx = os.path.join(d, name)
            os.makedirs(fx)
            for n, t in (("base", b), ("o", b.replace("db", "pg")), ("t", b + "  worker --> db\n")):
                with open(os.path.join(fx, n + ".mmd"), "w") as f:
                    f.write(t)
            with open(os.path.join(fx, "expect.json"), "w") as f:
                json.dump({"stratum": "F", "exposed": True, "records": rec, "tiers": ti_, "why": "plant"}, f)
            for n in sorted(os.listdir(fx)):
                ti = tf.gettarinfo(os.path.join(fx, n), f"sealed/{name}/" + n)
                ti.mtime = ti.uid = ti.gid = 0
                ti.mode = 0o644
                with open(os.path.join(fx, n), "rb") as fh:
                    tf.addfile(ti, fh)
    tp = os.path.join(d, "s.tar")
    with open(tp, "wb") as f:
        f.write(buf.getvalue())
    return tp, hashlib.sha256(b"\x01" * 32 + buf.getvalue()).hexdigest()


def s_sealed():
    """H5: R-tiers; a malformed sealed fixture is logged, the rest still run."""
    d = tmpdir("sealed")
    x = os.path.join(d, "x.py")
    with open(x, "w") as f:
        f.write("import json\nprint(json.dumps({'exposed': True, 'records': [{'category': 'I1', "
                "'objects': ['db', 'worker'], 'tier': 'A'}]}))\n")
    td = tmpdir("tr")
    tp, h = _sealed_tar(tmpdir("good"), ["A"], [{"category": "I1", "objects": ["db", "worker"]}])
    out = tmpdir("out")
    rc, o = cli(["sealed", "--tar", tp, "--nonce-hex", "01" * 32, "--sealed-sha256", h, "--out-dir", out,
                 "--extractor", x, "--transcript-dir", td])
    lines = json.load(open(os.path.join(out, "sealed.json")))["sealed"] if rc == 0 else []
    check("sealed: a well-formed tar runs, and F's lines come from its tiers",
          rc == 0 and {(ln["line"], ln["f"]) for ln in lines} == {("A", True), ("B", False)}, o[-300:])
    check("sealed: H's and X's lines are computed (bare-style hole #2: A, not B)",
          all(ln["h"] == (ln["line"] == "A") and ln["x"] == (ln["line"] == "A") for ln in lines), lines)
    tp2, h2 = _sealed_tar(tmpdir("bad"), ["A"], [{"category": "I1", "objects": ["db", "worker"]}],
                          more=[("fy", "A", [{"category": "I1", "objects": ["db"]}])])
    td2, out2 = tmpdir("tr2"), tmpdir("o")
    rc, o = cli(["sealed", "--tar", tp2, "--nonce-hex", "01" * 32, "--sealed-sha256", h2, "--out-dir", out2,
                 "--extractor", x, "--transcript-dir", td2])
    t = "".join(open(os.path.join(td2, n)).read() for n in os.listdir(td2))
    sj = json.load(open(os.path.join(out2, "sealed.json"))) if rc == 0 else {}
    check("sealed: a fixture whose tiers the parser cannot read is logged as malformed, not refused (LOG §3, §4)",
          rc == 0 and "# executed:" in t and [m["name"] for m in sj.get("malformed", [])] == ["fy"], o[-300:])
    check("sealed: the other fixtures are still lined",
          {ln["name"] for ln in sj.get("sealed", [])} == {"fx"}, sj.get("sealed"))
    from ms import aggregate as AGG
    v = AGG.verdict(dict(_sum(_base()), sealed=sj.get("sealed", []), sealed_malformed=sj.get("malformed", [])))
    check("sealed: a malformed sealed fixture is listed in the verdict", v["lists"]["malformed_sealed_fixtures"])
    import mermaid_spike as CLI
    res = [{"fixture": "f", "expect": {"records": [{"category": "G2", "objects": []}], "tiers": ["A"]},
            "records": [], "x": {"records": [{"category": "G2", "objects": [], "tier": "tier-A"}]}}]
    ln = CLI.sealed_lines(res)
    check("sealed: an X tier outside the vocabulary gives x = None", all(x_["x"] is None for x_ in ln))
    check("sealed: H differing from F with X malformed is disputed, not VOID",
          AG.fixtures(ln)[1]["structure"] and not AG.fixtures(ln)[0]["structure"])


def s_archive_leak():
    """H6: a failed archive names no corpus."""
    d = tmpdir("arch")
    from ms import transcript as TRN
    tr = TRN.Transcript("archive", ["mermaid_spike.py", "archive", "--corpus", "u:000000000000"],
                        os.path.join(d, "tr"))
    try:
        K.archive("planted-private-owner/planted-repo", "u:000000000000", os.path.join(d, "out"),
                  url=os.path.join(d, "planted-private-owner", "planted-repo.git"))
        failed = None
    except K.ArchiveFailed as e:
        failed = str(e)
        print(f"archive failed: {e}")
    finally:
        tr.close(1, "aborted")
    t = open(tr.path).read()
    check("archive: a failure is reported", failed is not None)
    check("archive: a failed archive's transcript names neither the owner nor the repository",
          "planted-private-owner" not in t and "planted-repo" not in t, t[-300:])
    rc, o = cli(["archive", "--corpus", "x", "--out", tmpdir("o"), "--private-map",
                 os.path.join(SPIKE, "LOG.md"), "--private-table", os.path.join(SPIKE, "LOG.md"),
                 "--transcript-dir", tmpdir("t")])
    check("archive: a private file inside the repository is refused", rc != 0 and "outside the repository" in o, o[-200:])
    rc, o = cli(["archive", "--corpus", "x", "--out", tmpdir("o"), "--private-map", tmpdir("p") + "/m",
                 "--private-table", tmpdir("p") + "/t"])
    check("archive: a run without --transcript-dir outside the repository is refused", rc != 0 and
          "transcript outside" in o, o[-200:])


def s_history_more():
    """R14, R24, R26, R27, R29, R30 plants."""
    b = "flowchart LR\n  c[C] --> d[D]\n  e[E]\n  f[F]\n  g[G]\n  h[H]\n"
    o = "flowchart LR\n  d[D]\n  e[E]\n  f[F]\n  g[G]\n  h[H]\n"
    t = b + "  style c fill:#f00\n"
    p, r = run_case("F", b, t, o)
    check("delete/modify with the legs swapped: I3 on c", has(r, "I3", obj="c"), cats(r))
    b = "flowchart LR\n  api --> db\n  db --> cache\n  ui --> api\n"
    p, r = run_case("F", b, b + "  worker --> db\n", b.replace("db", "pg"))
    check("hole #2 with the legs swapped is exposed and I1", p.get("exposed") is True and has(r, "I1", obj="db"),
          cats(r))
    # rebase with the pull request's commits replayed in reverse order
    pl = Plant("rev")
    lines = [f"  n{i}[N{i}]\n" for i in range(30)]
    base = "flowchart TD\n" + "".join(lines)
    pl.commit({"g.mmd": base}, "base")
    pl.g("checkout", "-q", "-b", "pr")
    cur, prc = base, []
    for i in (2, 14, 26):
        cur = cur.replace(f"n{i}[N{i}]", f"n{i}[M{i}]")
        prc.append(pl.commit({"g.mmd": cur}, f"pr {i}"))
    pl.g("checkout", "-q", "main")
    pl.commit({"g.mmd": base.replace("n8[N8]", "n8[Main]")}, "main moves")
    for c in reversed(prc):
        pl.g("cherry-pick", c)
    head_c = pl.g("rev-parse", "HEAD")
    pin = head_c
    cases, counts = HI.pr_cases(HI.Repo(pl.path), pin, {"g.mmd": "F"},
                                [{"number": 7, "head": prc[-1], "merge": head_c, "commit_count": 3, "commits": prc}])
    check("M-PR: a pull request's commits landed in another order are not a rebase merge",
          counts["rebase"] == 0, counts)
    # the last predecessor step of a triple fails
    pl = Plant("plast")
    V = ["flowchart TD\n  a[A] --> b[B]\n", "flowchart TD\n  a[A1] --> b[B]\n", "flowchart TD\n  a[A1] --> b[S]\n",
         "flowchart TD\n  a[A1] --> b[S]\n  c[C]\n"]
    pl.commit({"p.mmd": V[0]}, "v0")
    c1 = pl.commit({"p.mmd": V[1]}, "v1")
    pl.g("checkout", "-q", "-b", "side")
    pl.commit({"p.mmd": V[2]}, "s")
    pl.g("checkout", "-q", "main")
    pl.g("merge", "-q", "--no-ff", "--no-commit", "side")
    with open(os.path.join(pl.path, "p.mmd"), "w") as f:
        f.write("flowchart TD\n  a[A1] --> b[W]\n")
    pl.g("add", "-A")
    pl.g("commit", "-q", "-m", "merge, resolved to W")
    pl.commit({"p.mmd": V[3]}, "v3")
    pin = pl.g("rev-parse", "HEAD")
    repo = HI.Repo(pl.path)
    trip, counts = HI.p_triples(repo, {"p.mmd": "F"}, HI.walk(repo, pin)[1])
    seq = [b_ for _, b_ in HI.segments(HI.walk(repo, pin)[1]["p.mmd"])[0]]
    check("plant: versions V0, V1, S, V3 in order", len(seq) == 4, len(seq))
    check("P: a triple whose last step fails the predecessor rule is dropped",
          not any(t_["i"] == 1 and (t_["a"], t_["b"]) == (1, 1) for t_ in trip) and
          any(t_["i"] == 0 and (t_["a"], t_["b"]) == (1, 1) for t_ in trip), [(t_["i"], t_["a"], t_["b"]) for t_ in trip])
    # convergent
    pl = Plant("conv")
    b = "flowchart TD\n  a[A] --> b[B]\n"
    pl.commit({"c.mmd": b}, "b")
    pl.g("checkout", "-q", "-b", "side")
    pl.commit({"c.mmd": b + "  c[C]\n", "other.txt": "1\n"}, "side")
    pl.g("checkout", "-q", "main")
    pl.commit({"c.mmd": b + "  c[C]\n", "other2.txt": "2\n"}, "main")
    pl.g("merge", "-q", "--no-edit", "side")
    cases, counts = HI.merge_cases(HI.Repo(pl.path), pl.g("rev-parse", "HEAD"), {"c.mmd": "F"})
    check("M: a path both sides changed to the same blob is convergent, not a case",
          counts["convergent"] == 1 and not cases, counts)
    # authors are the last changers of the path, not the leg tips
    pl = Plant("auth")
    b = "flowchart LR\n  api --> db\n  db --> cache\n  ui --> api\n"
    pl.commit({"c.mmd": b}, "b")
    pl.g("checkout", "-q", "-b", "side")
    pl.commit({"c.mmd": b + "  worker --> db\n"}, "t", author=("Tess", "tess@t.org"))
    pl.commit({"other.txt": "x\n"}, "tip", author=("Tipper", "tip@t.org"))
    pl.g("checkout", "-q", "main")
    pl.commit({"c.mmd": b.replace("db", "pg")}, "o", author=("Olga", "olga@o.org"))
    pl.g("merge", "-q", "--no-edit", "side")
    ctx = AR.Ctx("plant/a", None, pl.path, pl.g("rev-parse", "HEAD"), "in", False, "", TMP)
    cs, _ = AR.arm_m(ctx, R, None)
    au = cs[0]["authors"] if cs else []
    check("authors: a case's authors are the last changers of the path on each leg",
          sorted(au) == sorted([ctx.authors.of("Olga", "olga@o.org"), ctx.authors.of("Tess", "tess@t.org")]), au)
    pl = Plant("prank")
    v = "flowchart TD\n" + "".join(f"  n{i}[N{i}]\n" for i in range(12))
    pl.commit({"p.mmd": v}, "v0")
    for i in (1, 3, 5, 7, 9):
        v = v.replace(f"n{i}[N{i}]", f"n{i}[M{i}]")
        pl.commit({"p.mmd": v}, f"v{i}")
    pin = pl.g("rev-parse", "HEAD")
    ctx = AR.Ctx("plant/p", None, pl.path, pin, "in", False, "", TMP)
    ps, _ = AR.arm_p(ctx, R, None)
    ranks = {(c["spec"]["a"], c["spec"]["b"]): c.get("rank") for c in ps if c.get("rank") is not None}
    want = {(1, 1): 0, (1, 3): 1, (3, 1): 2}
    check("P: ranks are (1,1) 0, (1,3) 1, (3,1) 2", ranks and all(want[k] == v for k, v in ranks.items()) and
          (1, 1) in ranks, ranks)
    check("decided: a case with an UNRELIABLE record is not decided",
          AR.decided_of(None, "JUDGED", [{"unreliable": "x"}]) is False and AR.decided_of(None, "JUDGED", []) is True)


def s_rereview():
    """The unfiltered tier-A set under P, salted bundle names, archive's
    scrubbing and repository boundary, L5 on a user edge id, the coverage
    scope, missing X answers, authors and R-select."""
    # P: H's unfiltered tier-A set is what X is held to (ptier).
    v0 = "flowchart TD\n  A[Alpha]\n  B[Beta]\n  A --> B\n  C[Gamma]\n"
    v1 = v0 + "  A --> B\n"
    v2 = "flowchart TD\n  A[Alpha]\n  B[Beta]\n  C[Gamma]\n  A --> B\n"
    t = RP.replay(v0, v1, v2)
    prep = C.prepare("F", v0, v1, t, R)
    res = C.outcome(prep, [v0, v1, t], G.merge_texts("c.mmd", v0.encode(), v1.encode(), t.encode(), TMP), R,
                    path="c.mmd", truth=v2)
    x = os.path.join(tmpdir("px"), "x.py")
    with open(x, "w") as f:
        f.write("import json\nprint(%r)\n" % json.dumps({"exposed": bool(prep.get("exposed")), "records": [
            {"category": r["category"], "objects": r["objects"], "tier": r["tier"]} for r in res["records_unfiltered"]]}))
    c = AR.evaluate(_Ctx(), {"arm": "P", "path": "c.mmd"}, "F", [v0, v1, t],
                    lambda: G.merge_texts("c.mmd", v0.encode(), v1.encode(), t.encode(), TMP), R, x, truth=v2)
    check("plant: the P case has an unfiltered tier-A structure record that the truth filter removes",
          any(r["tier"] == "A" for r in res["records_unfiltered"]) and not any(r["tier"] == "A" for r in res["records"]))
    c.update(path_i=["c.mmd", 0, 0], rank=0, authors=["pa"], corpus="c9")
    v = AG.verdict(_sum(_base() + [c]))
    check("a perfect X on a P case whose tier-A record the truth filter removes leaves NOT FOUND standing",
          v["structure"]["verdict"] == "NOT FOUND", v["structure"])
    # bundle file names come from the salted label, not the name
    import hashlib
    src = Plant("bsrc")
    src.commit({"a.mmd": "flowchart TD\n  A --> B\n"}, "x")
    name = "planted-private-owner/planted-repo"
    res_b = K.archive(name, K.u_label("a-secret-salt", name), tmpdir("bout"), api=lambda path: [], url=src.path)
    guess = hashlib.sha256(name.encode()).hexdigest()[:16]
    check("archive: bundle file names cannot be computed from the corpus name without the salt",
          guess not in res_b["file"] and guess not in res_b["prs_file"], res_b)

    def boom(path):
        raise RuntimeError(f"API failed for {name}")
    try:
        K.archive(name, "u:000000000000", tmpdir("bout2"), api=boom, url=src.path)
        msg, typ = "", None
    except Exception as e:  # noqa: BLE001 -- the check is on what escapes
        msg, typ = str(e), type(e)
    check("archive: a failure outside a subprocess is raised as ArchiveFailed, scrubbed",
          typ is K.ArchiveFailed and "planted-private-owner" not in msg, f"{typ}: {msg}")
    import mermaid_spike as CLI
    rc, o = cli(["archive", "--corpus", "x", "--out", tmpdir("o"), "--private-map",
                 os.path.join(CLI.REPO, "private-map.tsv"), "--private-table", tmpdir("p") + "/t",
                 "--transcript-dir", tmpdir("t")])
    check("archive: a private file anywhere in the repository, outside spike/mermaid too, is refused",
          rc != 0 and "outside the repository" in o, o[-200:])
    # L5 on a duplicated user edge id
    b = "flowchart LR\n  A[A]\n  C[C]\n  x1[x1]\n  x2[x2]\n  x3[x3]\n  D[D]\n"
    o_ = b.replace("  C[C]\n", "  C[C]\n  A e1@--> C\n")
    t_ = b + "  A e1@--> C\n"
    p, r = run_case("F", b, o_, t_)
    check("L5: a user edge id both legs add gives a G2 at tier B through L5 on the edge's ends",
          has(r, "G2", "B") and not has(r, "G2", "A") and "L5:A" in r.get("lint_new", []), cats(r))
    # the disagreement check reaches a stratum below the coverage bar
    cs = _base() + [_case(900, stratum="D", x_tier_a=[["G2", ["a", "b"]]], agree=False)]
    v = AG.verdict(_sum(cs, coverage={"F": 0.95, "D": 0.5}))
    check("scope: an X-only tier-A record in a stratum below the coverage bar is NO VERDICT",
          v["structure"]["verdict"] == "NO VERDICT" and "tier-A" in v["structure"]["reason"], v["structure"])
    # a missing X answer is None, never "not qualifying"
    ln = CLI.sealed_lines([{"fixture": "f", "expect": {"records": [{"category": "G2", "objects": []}],
                                                      "tiers": ["A"]}, "records": []}])
    check("sealed: a missing X answer gives x = None on both lines", [x_["x"] for x_ in ln] == [None, None], ln)
    # authors: never a merge commit; identities from every ref
    pl = Plant("lc")
    pl.commit({"keep.txt": "k\n"}, "root", author=("Bea", "bea@b.org"))
    base = pl.commit({"p.mmd": "flowchart TD\n  a --> b\n"}, "b", author=("Bea", "bea@b.org"))
    pl.g("checkout", "-q", "-b", "side")
    pl.commit({"p.mmd": "flowchart TD\n  a --> c\n"}, "s", author=("Sam", "sam@s.org"))
    pl.g("checkout", "-q", "main")
    pl.commit({"other.txt": "x\n"}, "m", author=("Max", "max@m.org"))
    pl.e.update(GIT_AUTHOR_NAME="Merger", GIT_AUTHOR_EMAIL="merger@m.org")
    pl.g("merge", "-q", "--no-ff", "--no-edit", "side")
    pl.g("checkout", "-q", "-b", "elsewhere")
    pl.commit({"x.txt": "1\n"}, "joins the names", author=("Ann", "ann@two.org"))
    pl.g("checkout", "-q", "main")
    pl.commit({"y.txt": "1\n"}, "a", author=("Ann", "ann@one.org"))
    pl.commit({"z.txt": "1\n"}, "b2", author=("Annie", "ann@two.org"))
    ctx = AR.Ctx("plant/lc", None, pl.path, pl.g("rev-parse", "main"), "in", False, "", TMP)
    lc = ctx.last_changer(base, pl.g("rev-parse", "main"), "p.mmd")
    check("authors: a leg's last changer is never a merge commit",
          ctx.author(lc)[0] == ctx.authors.of("Sam", "sam@s.org"), ctx.author(lc))
    check("authors: identities from every ref join before any lookup",
          ctx.authors.of("Ann", "ann@one.org") == ctx.authors.of("Annie", "ann@two.org"))
    # R-select: a D path whose last version holds two fences, one a flowchart
    pl = Plant("dsel")
    two = ("# T\n\n```mermaid\nflowchart TD\n  A --> B\n```\n\n```mermaid\nsequenceDiagram\n  A->>B: hi\n```\n")
    pl.commit({"doc.md": two, "one.md": "```mermaid\nflowchart TD\n  A --> B\n```\n"}, "c")
    sel = HI.select(HI.Repo(pl.path), pl.g("rev-parse", "HEAD"))
    check("R-select: a D path with two fences is not selected, even when one is a flowchart (§3)",
          "doc.md" not in sel["selected"] and sel["selected"].get("one.md") == "D", sel)

SECTIONS = [s_holes, s_census_cases, s_conflicts, s_positional, s_edge_to_subgraph, s_i4, s_exposure, s_per_path_e, s_fences,
            s_generated, s_mpr, s_p_ancestry, s_p, s_authors, s_hermetic, s_redaction, s_xfail, s_verdicts, s_subset_refusals,
            s_fuzz, s_blind, s_binding, s_cli_arms, s_oracle_units, s_l5, s_p_x, s_aggregate_scope,
            s_bound_aggregate, s_sealed, s_archive_leak, s_history_more, s_rereview]


def main():
    global TMP
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--only")
    a = ap.parse_args()
    TMP = tempfile.mkdtemp(prefix="v3.")

    def results_files():
        out = set()
        for root, _, files in os.walk(os.path.join(SPIKE, "results")):
            out |= {os.path.join(root, f) for f in files}
        return out
    before = results_files()
    try:
        RB.check_install()
        for s in SECTIONS:
            if a.only and s.__name__ != a.only:
                continue
            print(f"== {s.__name__}: {(s.__doc__ or '').strip().splitlines()[0] if s.__doc__ else ''}")
            try:
                s()
            except Exception as e:
                check(f"section raised: {s.__name__}: {e.__class__.__name__}: {e}", False)
                traceback.print_exc(file=sys.stdout)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    if not a.only:
        added = sorted(results_files() - before)
        check("V3 wrote nothing under results/", not added, added[:3])
    n = RESULTS["pass"] + RESULTS["fail"]
    print(f"\n{n} checks, {RESULTS['fail']} failed")
    print("V3:", "PASS" if RESULTS["fail"] == 0 and n else "FAIL")
    return 0 if RESULTS["fail"] == 0 and n else 1


if __name__ == "__main__":
    sys.exit(main())
