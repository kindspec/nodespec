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
    check("blind: X's spec holds §4, §5, Appendices A, C and D, and not §6, Appendix B or E",
          all(h in spec for h in BL.SECTIONS) and "## 6. FOUND" not in spec and "## Appendix B" not in spec
          and "## Appendix E" not in spec)
    from ms import hparse  # noqa: F401
    doc = os.path.join(SPIKE, "blind", "mermaid-12.1.0-flowchart.md")
    blob = subprocess.run(["git", "hash-object", doc], capture_output=True, text=True).stdout.strip()
    check("blind: the Mermaid document is mermaid@12.1.0's docs/syntax/flowchart.md", blob == BL.MERMAID_DOC_BLOB)
    check("blind: Appendix E's prompts are cut verbatim", BL.prompt("X").startswith("You are writing a program") and
          BL.prompt("F").startswith("You are writing test cases"))


def s_binding():
    """The binding (ms/binding.py) on a planted copy of the spike."""
    root = tmpdir("bind")
    sp = os.path.join(root, "spike", "mermaid")
    os.makedirs(sp)
    for d in ("harness", "r"):
        shutil.copytree(os.path.join(SPIKE, d), os.path.join(sp, d),
                        ignore=shutil.ignore_patterns("node_modules", "__pycache__"))
    shutil.copy(os.path.join(SPIKE, "PRE-REGISTRATION.md"), sp)
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
        json.dump({"sealed_sha256": "a" * 64, "lockfile_sha256": "b" * 64}, f)
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
        json.dump({"sealed_sha256": "a" * 64, "lockfile_sha256": "b" * 64}, f)
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
        json.dump({"sealed_sha256": "a" * 64, "lockfile_sha256": "b" * 64}, f)
    g3("add", "-A")
    g3("commit", "-q", "-m", "validation")
    rv = subprocess.run(["bash", os.path.join(HERE, "reverify.sh"), sp3], capture_output=True, text=True)
    check("reverify: passes on a clean validation history", rv.returncode == 0 and "reverify: PASS" in rv.stdout,
          rv.stdout[-300:])
    with open(os.path.join(sp3, "results", "VALIDATION"), "w") as f:
        json.dump({"sealed_sha256": "c" * 64, "lockfile_sha256": "b" * 64}, f)
    g3("commit", "-q", "-am", "VALIDATION changed")
    check("binding: VALIDATION changed after it was added is refused", not BD.check(sp3, "arm0")["bound"])
    rv = subprocess.run(["bash", os.path.join(HERE, "reverify.sh"), sp3], capture_output=True, text=True)
    check("reverify: fails when VALIDATION changed", rv.returncode != 0)


SECTIONS = [s_holes, s_census_cases, s_conflicts, s_positional, s_edge_to_subgraph, s_i4, s_exposure, s_per_path_e, s_fences,
            s_generated, s_mpr, s_p_ancestry, s_p, s_authors, s_hermetic, s_redaction, s_xfail, s_verdicts, s_subset_refusals,
            s_fuzz, s_blind, s_binding, s_cli_arms]


def main():
    global TMP
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--only")
    a = ap.parse_args()
    TMP = tempfile.mkdtemp(prefix="v3.")
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
    n = RESULTS["pass"] + RESULTS["fail"]
    print(f"\n{n} checks, {RESULTS['fail']} failed")
    print("V3:", "PASS" if RESULTS["fail"] == 0 and n else "FAIL")
    return 0 if RESULTS["fail"] == 0 and n else 1


if __name__ == "__main__":
    sys.exit(main())
