#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""The harness for spike/mermaid/PRE-REGISTRATION.md (role H). Run isolated:

  python3 -I -S -B harness/mermaid_spike.py validation --sealed-sha256 HEX
  python3 -I -S -B harness/mermaid_spike.py arm0  CORPUS-OPTIONS
  python3 -I -S -B harness/mermaid_spike.py arms  CORPUS-OPTIONS     (M, P and S: §11.3 commit 5)
  python3 -I -S -B harness/mermaid_spike.py repro CORPUS-OPTIONS --arm ARM --corpus LABEL --case KEY
  python3 -I -S -B harness/mermaid_spike.py sealed --tar FILE --nonce-hex HEX   (§11.3 commit 6)
  python3 -I -S -B harness/mermaid_spike.py aggregate
  python3 -I -S -B harness/mermaid_spike.py fixtures --dir DIR --out FILE [--extractor X]
  python3 -I -S -B harness/mermaid_spike.py export --role F|X --out DIR
  python3 -I -S -B harness/mermaid_spike.py archive --corpus LABEL --out DIR CORPUS-OPTIONS

CORPUS-OPTIONS, bound: --bundle-dir D --work-dir W --private-map F --private-table F
(the private files are the owner's, outside the repository; never committed).
For testing, --fixture-manifest JSON --out-dir D --transcript-dir D runs unbound
on planted repositories, writes nowhere under results/, and carries no verdict.

Every invocation writes a transcript (results/transcripts/, or --transcript-dir
when unbound), opened before the arguments are parsed. Options cannot be
abbreviated or repeated. A bound run checks ms/binding.py first, and takes
every output path from its fixed place.
"""
import argparse
import glob
import hashlib
import json
import os
import sys
import traceback

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ms import aggregate as AG  # noqa: E402
from ms import arms as AR  # noqa: E402
from ms import binding as BD  # noqa: E402
from ms import blind as BL  # noqa: E402
from ms import corpus as K  # noqa: E402
from ms import rbridge as RB  # noqa: E402
from ms import transcript as TR  # noqa: E402

SPIKE = TR.SPIKE
RESULTS = TR.RESULTS
EXTRACTOR = os.path.join(SPIKE, "x", "extract2.py")
COMMANDS = ("validation", "arm0", "arms", "repro", "sealed", "aggregate", "fixtures", "export", "archive")
BOUND_CMDS = {"arm0", "arms", "repro", "sealed", "aggregate"}
ARM_OF = {"arm0": "arm0", "arms": "arms", "sealed": "sealed", "aggregate": "aggregate"}


def jdump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False, default=str) + "\n")


def inside(path, root):
    p, r = os.path.realpath(path), os.path.realpath(root)
    return p == r or p.startswith(r + os.sep)


def repeated(argv):
    seen, rep = set(), []
    for tok in argv:
        if tok == "--":
            break
        if tok.startswith("--"):
            n = tok.split("=", 1)[0]
            if n in seen and n not in rep:
                rep.append(n)
            seen.add(n)
    return rep


def prescan(argv, flag):
    for i, x in enumerate(argv):
        if x == flag and i + 1 < len(argv):
            return argv[i + 1]
        if x.startswith(flag + "="):
            return x.split("=", 1)[1]
    return None


def parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def sp(name):
        p = sub.add_parser(name, allow_abbrev=False)
        p.add_argument("--transcript-dir")
        return p

    def corpus(p):
        p.add_argument("--bundle-dir")
        p.add_argument("--work-dir")
        p.add_argument("--private-map")
        p.add_argument("--private-table")
        p.add_argument("--fixture-manifest")
        p.add_argument("--out-dir")
        p.add_argument("--extractor")
    p = sp("validation")
    p.add_argument("--sealed-sha256", required=True)
    p.add_argument("--bundles", required=True)
    corpus(sp("arm0"))
    corpus(sp("arms"))
    p = sp("repro")
    corpus(p)
    p.add_argument("--arm", required=True, choices=("M-merge", "M-PR", "P"))
    p.add_argument("--corpus", required=True)
    p.add_argument("--case", required=True)
    p.add_argument("--committed")
    p = sp("sealed")
    p.add_argument("--tar", required=True)
    p.add_argument("--nonce-hex", required=True)
    p.add_argument("--out-dir")
    p.add_argument("--extractor")
    p.add_argument("--sealed-sha256")
    p = sp("aggregate")
    p.add_argument("--summary")
    p.add_argument("--out")
    p = sp("fixtures")
    p.add_argument("--dir", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--extractor")
    p = sp("export")
    p.add_argument("--role", required=True, choices=("F", "X"))
    p.add_argument("--out", required=True)
    p.add_argument("--commit", default="HEAD")
    p = sp("archive")
    corpus(p)
    p.add_argument("--corpus", required=True)
    p.add_argument("--out", required=True)
    return ap


def unbound_requested(a):
    return bool(getattr(a, "fixture_manifest", None) or getattr(a, "summary", None)
                or (a.cmd == "sealed" and a.sealed_sha256))


# ------------------------------------------------------------------ corpora

def corpora(a, tr, arm):
    """Yields (label, stratum rows, Ctx) for each corpus, opening each in
    turn. Marks the arm executed when the first corpus is opened."""
    if a.fixture_manifest:
        man = json.load(open(a.fixture_manifest))
        for i, c in enumerate(man["corpora"]):
            if i == 0:
                tr.mark_executed()
            prs = json.load(open(c["prs"])) if c.get("prs") else None
            try:
                yield c["label"], c, open_ctx(c["label"], None, c["repo"], c["pin"], c.get("status", "in"),
                                              c.get("individual", False), c.get("salt", ""), None), prs
            except K.NoVerdict as e:
                yield c["label"], {"no_verdict": str(e)}, None, None
        return
    public = K.load_public()
    salt, ident = K.load_private(a.private_map, a.private_table, public)
    labels = sorted({r["corpus"] for r in public})
    rows = {lab: [r for r in public if r["corpus"] == lab] for lab in labels}
    first = True
    for lab in labels:
        r0 = rows[lab][0]
        meta = ident[(r0["stratum"], lab)]
        if first:
            if arm:
                BD.mark_executed(SPIKE, arm, tr.path)
            tr.mark_executed()
            first = False
        try:
            path = K.open_corpus(lab, a.bundle_dir, a.work_dir, meta["pin"])
        except K.NoVerdict as e:
            yield lab, {"no_verdict": str(e)}, None, None
            continue
        b = K.bundles().get(lab, {})
        prs = None
        if b.get("prs_file"):
            pf = os.path.join(a.bundle_dir, b["prs_file"])
            if K.sha256_file(pf) != b["prs_sha256"]:
                yield lab, {"no_verdict": "pull-request list sha256 differs"}, None, None
                continue
            prs = json.load(open(pf))
        try:
            ctx = open_ctx(lab, rows[lab], path, meta["pin"], r0["status"], meta["individual"], salt, a.work_dir)
        except K.NoVerdict as e:
            yield lab, {"no_verdict": str(e)}, None, None
            continue
        yield lab, rows[lab], ctx, prs


def open_ctx(label, rows, path, pin, status, individual, salt, tmp_root):
    """§7.6 and V3: a pin absent from the corpus, or a corpus with no
    selected path, is NO VERDICT for that corpus, and the arm exits non-zero."""
    from ms import history as HI
    if not HI.Repo(path).has_commit(pin):
        raise K.NoVerdict(f"the pin of {label} is absent")
    ctx = AR.Ctx(label, rows, path, pin, status, individual, salt, tmp_root=tmp_root)
    if not ctx.selected:
        raise K.NoVerdict(f"{label} is empty: no selected path")
    return ctx


def outdir(a, bound, default):
    if bound:
        return default
    if not a.out_dir or inside(a.out_dir, RESULTS):
        raise SystemExit("refusing: an unbound run must name --out-dir outside results/")
    return a.out_dir


def ctx_meta(ctx):
    return (ctx.status, ctx.individual, ctx.salt)


# ----------------------------------------------------------------- commands

def cmd_validation(a, tr, bound):
    """Writes results/VALIDATION for the validation commit: the sealed hash,
    which LOG.md must already record once (commit 2, §11.3), the lockfile's
    sha256, and the bundles' and pull-request lists' sha256s (§7.6)."""
    vp = os.path.join(SPIKE, BD.VALIDATION_REL)
    if os.path.exists(vp) or BD.derive(SPIKE)[0]:
        raise SystemExit("refusing: VALIDATION exists; the validation commit adds it once")
    rec = BD.sealed_in_log(open(os.path.join(SPIKE, "LOG.md"), encoding="utf-8").read())
    if rec != [a.sealed_sha256]:
        raise SystemExit(f"refusing: LOG.md records the sealed hash {rec or 'nowhere'}; it must record "
                         f"--sealed-sha256 exactly once, in commit 2")
    if inside(a.bundles, os.path.dirname(SPIKE)):
        raise SystemExit("refusing: --bundles is the owner's file, outside the repository")
    lock = K.sha256_file(os.path.join(SPIKE, "r", "package-lock.json"))
    v = {"sealed_sha256": a.sealed_sha256, "lockfile_sha256": lock, "bundles": json.load(open(a.bundles))}
    try:
        BD.validate_content(v)
    except ValueError as e:
        raise SystemExit(f"refusing: {e}")
    jdump(v, vp)
    print(f"wrote {BD.VALIDATION_REL}: sealed {a.sealed_sha256}, lockfile {lock}, {len(v['bundles'])} bundles")
    print("commit it in the validation commit, with nothing under a bound path")
    return 0


def cmd_arm0(a, tr, bound):
    R = RB.RCache()
    RB.check_install()
    out = {"corpora": {}, "r_config": None}
    d = outdir(a, bound, RESULTS)
    for lab, rows, ctx, prs in corpora(a, tr, "arm0"):
        if ctx is None:
            out["corpora"][lab] = rows
            print(f"{lab}: NO VERDICT ({rows['no_verdict']})")
            continue
        o = AR.redact_arm0(AR.arm0(ctx, R, prs), ctx_meta(ctx))
        out["corpora"][lab] = o
        for st in ("F", "D"):
            s = o[st]
            if s["distinct_blobs_at_pin"]:
                print(f"{lab} {st}: {s['in_subset']}/{s['distinct_blobs_at_pin']} blobs in the subset")
    out["r_config"] = R.config
    out["coverage"] = coverage(out)
    print("coverage by stratum:", json.dumps(out["coverage"], sort_keys=True))
    jdump(out, os.path.join(d, "arm0.json"))
    nv = [lab for lab, o in out["corpora"].items() if "no_verdict" in o]
    if nv:
        print(f"NO VERDICT for {len(nv)} corpora: exit 3")
        return 3
    return 0


def coverage(arm0_out):
    tot, ins = {}, {}
    for o in arm0_out["corpora"].values():
        for st in ("F", "D"):
            if st in o:
                tot[st] = tot.get(st, 0) + o[st]["distinct_blobs_at_pin"]
                ins[st] = ins.get(st, 0) + o[st]["in_subset"]
    return {st: (ins[st] / tot[st]) if tot[st] else 0.0 for st in tot}


def cmd_arms(a, tr, bound):
    d = outdir(a, bound, RESULTS)
    a0 = os.path.join(d, "arm0.json")
    if not os.path.isfile(a0):
        raise SystemExit(f"refusing: no Arm 0 output at {a0}; Arm 0 runs first")
    arm0_out = json.load(open(a0))
    mix, mix_why = AR.frozen_mix(list(v for v in arm0_out["corpora"].values() if "history" in v))
    print(f"S's edit mix: {mix_why}")
    R = RB.RCache()
    RB.check_install()
    ext = EXTRACTOR if bound else a.extractor
    allc, counts, ctxs = [], {}, []
    for lab, rows, ctx, prs in corpora(a, tr, "arms"):
        if ctx is None:
            counts[lab] = rows
            continue
        ctxs.append(ctx)
        m, mc = AR.arm_m(ctx, R, ext, prs)
        p, pc = AR.arm_p(ctx, R, ext)
        counts[lab] = {"M": mc, "P": pc}
        allc += [AR.redact(c, ctx_meta(ctx)) for c in m + p]
        print(f"{lab}: M {len(m)} cases, P {len(p)} cases")
    s, rates = AR.arm_s(AR.s_bases(ctxs, R), mix, R, ext)
    byl = {c.label: c for c in ctxs}
    allc += [AR.redact(c, ctx_meta(byl[c["corpus"]])) for c in s]
    print("S rates (properties of the edit generator):", json.dumps(rates, sort_keys=True))
    jdump({"cases": allc, "counts": counts, "s_rates": rates, "s_mix": mix, "s_mix_source": mix_why,
           "r_config": R.config}, os.path.join(d, "arms.json"))
    nv = [lab for lab, o in counts.items() if "no_verdict" in o]
    if nv:
        print(f"NO VERDICT for {len(nv)} corpora: exit 3")
        return 3
    return 0


def canon(case):
    c = {k: v for k, v in case.items() if not k.startswith("x_")}
    return json.dumps(c, sort_keys=True, ensure_ascii=False, default=str)


def cmd_repro(a, tr, bound):
    """F8: regenerate one case from the bundles and compare it byte for byte
    with the committed arms output."""
    d = outdir(a, bound, RESULTS)
    committed = a.committed if (a.committed and not bound) else os.path.join(d, "arms.json")
    want = [c for c in json.load(open(committed))["cases"] if c.get("key") == a.case and c["corpus"] == a.corpus
            and c["arm"] == a.arm]
    if len(want) != 1:
        raise SystemExit(f"refusing: {len(want)} committed cases match")
    R = RB.RCache()
    for lab, rows, ctx, prs in corpora(a, tr, None):
        if lab != a.corpus or ctx is None:
            continue
        cs = AR.arm_m(ctx, R, None, prs)[0] if a.arm.startswith("M") else AR.arm_p(ctx, R, None)[0]
        got = [AR.redact(c, ctx_meta(ctx)) for c in cs if c.get("key") == a.case and c["arm"] == a.arm]
        ok = len(got) == 1 and canon(got[0]) == canon(want[0])
        res = {"case": a.case, "corpus": a.corpus, "arm": a.arm, "reproduces": ok,
               "sha256_committed": hashlib.sha256(canon(want[0]).encode()).hexdigest(),
               "sha256_regenerated": hashlib.sha256(canon(got[0]).encode()).hexdigest() if got else None}
        print(json.dumps(res, sort_keys=True))
        jdump(res, os.path.join(d, "repro", f"{a.case}.json"))
        return 0 if ok else 1
    raise SystemExit(f"refusing: corpus {a.corpus} not opened")


def run_fixture_dir(fx, R, extractor):
    """H (and X) on one fixture directory (Appendix D's layout)."""
    from ms import case as C
    from ms import gitops as G
    from ms import xrun as XR
    exp = json.load(open(os.path.join(fx, "expect.json")))
    st = exp["stratum"]
    ext = "md" if st == "D" else "mmd"
    texts = [open(os.path.join(fx, f"{n}.{ext}"), encoding="utf-8").read() for n in ("base", "o", "t")]
    prep = C.prepare(st, *texts, R)
    out = {"fixture": os.path.basename(fx), "stratum": st, "expect": exp, "excluded": prep["excluded"],
           "exposed": bool(prep.get("exposed")), "records": []}
    if prep["excluded"] and "states" not in prep:
        return out
    m = G.merge_texts(f"c.{ext}", *(t.encode() for t in texts))
    res = C.outcome(prep, texts, m, R, path=f"c.{ext}") if "states" in prep and all(
        s.status == "in" for s in prep["states"]) else {"outcome": None, "records": []}
    out.update(outcome=res["outcome"], why=res.get("why"), records=res["records"],
               merged=C.decode(m.merged) if m.merged is not None else None)
    if extractor:
        xo, xf = XR.run_x(extractor, st, texts + [out["merged"] or ""])
        out["x_agree"], out["x_detail"] = XR.compare(out["records"], out["exposed"], xo, xf)
        out["x"] = xo
    return out


def cmd_fixtures(a, tr, bound):
    if inside(a.out, RESULTS):
        raise SystemExit("refusing: fixtures writes outside results/")
    R = RB.RCache()
    tr.mark_executed()
    res = [run_fixture_dir(fx, R, a.extractor) for fx in sorted(glob.glob(os.path.join(a.dir, "*")))
           if os.path.isfile(os.path.join(fx, "expect.json"))]
    if not res:
        raise SystemExit(f"refusing: no fixture under {a.dir}")
    jdump(res, a.out)
    for r in res:
        print(r["fixture"], r.get("outcome"), [(x["category"], x["tier"]) for x in r["records"]],
              "" if "x_agree" not in r else ("X agrees" if r["x_agree"] else f"X DISAGREES: {r['x_detail']}"))
    return 0


TIER_LETTERS = ("A", "B", "C", "D", "E")
X_TIERS = TIER_LETTERS + ("-", "\u2014")


class Malformed(Exception):
    pass


def expect_tiers(exp):
    """R-tiers: expect.json's "tiers" is a JSON list of §5.4's tier letters,
    "A" to "E", one per tier the fixture's records fall in; [] for a clean
    fixture. Anything else is malformed."""
    t = exp.get("tiers")
    if not isinstance(t, list) or not all(isinstance(x, str) and x in TIER_LETTERS for x in t):
        raise Malformed(f"tiers must be a list of {', '.join(TIER_LETTERS)}; got {t!r}")
    if not isinstance(exp.get("records"), list) or not all(
            isinstance(r, dict) and isinstance(r.get("category"), str) for r in exp["records"]):
        raise Malformed("records must be a list of {category, objects}")
    return t


def fixture_group(exp):
    return "identity" if any(r["category"] in AG.IDENTITY for r in exp["records"]) else "structure"


def lines_of(records, group):
    """Whether a run put the fixture on the qualifying side of the A and B
    lines (§10.4): a record of the group at tier A, at tier B. None for an
    answer whose tiers are not in the vocabulary."""
    cats = AG.IDENTITY if group == "identity" else AG.STRUCTURE | {"MC"}
    rs = [r for r in records if r.get("category") in cats]
    if any(r.get("tier") not in X_TIERS for r in rs):
        return None
    return {"A": any(r.get("tier") == "A" for r in rs), "B": any(r.get("tier") == "B" for r in rs)}


def sealed_lines(results):
    """[{name, group, line, f, h, x}] from run_fixture_dir results. x is
    None when X's answer is malformed or missing: §10.4's rules then read it
    as agreeing with neither, and aggregate.fixtures treats a fixture where
    H differs from F and X is None as disputed (R-sealed)."""
    out = []
    for r in results:
        exp = r["expect"]
        tiers, group = expect_tiers(exp), fixture_group(exp)
        hl = lines_of(r["records"], group)
        xl = lines_of((r.get("x") or {}).get("records", []), group) if r.get("x") else None
        for line in ("A", "B"):
            out.append({"name": r["fixture"], "group": group, "line": line, "f": line in tiers,
                        "h": hl[line], "x": None if xl is None else xl[line]})
    return out


def cmd_sealed(a, tr, bound):
    """§10.4, at commit 6: check sha256(nonce + tar) against VALIDATION, check
    every fixture's expect.json, and only then mark the run executed and run
    H and X on every sealed fixture."""
    import tarfile
    import tempfile
    want = tr_state(tr)["validation"]["sealed_sha256"] if bound else a.sealed_sha256
    data = open(a.tar, "rb").read()
    nonce = bytes.fromhex(a.nonce_hex)
    got = hashlib.sha256(nonce + data).hexdigest()
    if got != want:
        raise SystemExit(f"refusing: sha256(nonce + tar) is {got}, VALIDATION holds {want}")
    tmp = tempfile.mkdtemp(prefix="sealed.")
    with tarfile.open(a.tar) as tf:
        tf.extractall(tmp, filter="data")
    fxs = sorted(os.path.dirname(p) for p in glob.glob(os.path.join(tmp, "**", "expect.json"), recursive=True))
    if not fxs:
        raise SystemExit("refusing: the sealed tar holds no fixture")
    for fx in fxs:
        try:
            expect_tiers(json.load(open(os.path.join(fx, "expect.json"))))
        except (Malformed, ValueError) as e:
            raise SystemExit(f"refusing: sealed fixture {os.path.basename(fx)}: {e}")
    tr.mark_executed()
    if bound:
        BD.mark_executed(SPIKE, "sealed", tr.path)
    R = RB.RCache()
    ext = EXTRACTOR if bound else a.extractor
    out = sealed_lines([run_fixture_dir(fx, R, ext) for fx in fxs])
    d = outdir(a, bound, RESULTS)
    jdump({"sealed": out}, os.path.join(d, "sealed.json"))
    print(json.dumps(out, sort_keys=True, indent=1))
    return 0


def bound_summary(results):
    """The bound aggregate's input, from results/: (summary, missing), where
    missing lists the keys of real-arm cases holding a tier-A record with no
    reproduction result (F8). Row 4 is (a), the owner's choice (§0.1)."""
    arms = json.load(open(os.path.join(results, "arms.json")))
    a0 = json.load(open(os.path.join(results, "arm0.json")))
    sealed = json.load(open(os.path.join(results, "sealed.json")))["sealed"]
    repro = {}
    for p in glob.glob(os.path.join(results, "repro", "*.json")):
        o = json.load(open(p))
        repro[o["case"]] = o["reproduces"]
    missing = sorted({c["key"] for c in arms["cases"] if c["arm"] in AG.REAL and c.get("key") not in repro
                      and any(r.get("tier") == "A" and AG.group_of(r) for r in c.get("records", []))})
    for c in arms["cases"]:
        c["reproduces"] = repro.get(c.get("key"), False)
    summary = {"row4": "a", "cases": arms["cases"], "coverage": a0["coverage"], "sealed": sealed,
               "s_rates": arms["s_rates"]}
    return summary, missing


def cmd_aggregate(a, tr, bound):
    if bound:
        summary, missing = bound_summary(RESULTS)
        if missing:
            raise SystemExit("refusing: run `repro` first for every real-arm case with a tier-A record; "
                             "missing: " + ", ".join(missing))
        out = os.path.join(RESULTS, "verdict.json")
    else:
        if not a.out or inside(a.out, RESULTS):
            raise SystemExit("refusing: an unbound aggregate names --out outside results/")
        summary = json.load(open(a.summary))
        out = a.out
    tr.mark_executed()
    if bound:
        BD.mark_executed(SPIKE, "aggregate", tr.path)
    try:
        v = AG.verdict(summary)
    except ValueError as e:
        raise SystemExit(f"refusing: {e}")
    jdump(v, out)
    print("identity:", v["identity"]["verdict"], v["identity"].get("reason", ""))
    print("structure:", v["structure"]["verdict"], v["structure"].get("reason", ""))
    return 0


def cmd_export(a, tr, bound):
    man = BL.export(a.role, a.commit, a.out)
    print(f"export for {a.role} at {a.commit}: {a.out}")
    for name, sha in man:
        print(f"  {sha}  {name}")
    pp = a.out.rstrip("/") + ".prompt.txt"
    with open(pp, "w") as f:
        f.write(BL.prompt(a.role))
    print(f"prompt (Appendix E, verbatim): {pp}  sha256 {K.sha256_file(pp)}")
    return 0


def cmd_archive(a, tr, bound):
    """§7.6, run by the owner. Its transcript lives outside the repository
    (--transcript-dir), and a failure is reported without the corpus's
    name (H6)."""
    public = K.load_public()
    salt, ident = K.load_private(a.private_map, a.private_table, public)
    rows = [r for r in public if r["corpus"] == a.corpus]
    if not rows:
        raise SystemExit(f"refusing: {a.corpus} is not a listed corpus")
    name = ident[(rows[0]["stratum"], a.corpus)]["name"]
    if inside(a.out, os.path.dirname(SPIKE)):
        raise SystemExit("refusing: archives live outside the repository")
    try:
        res = K.archive(name, a.out)
    except K.ArchiveFailed as e:
        raise SystemExit(f"archive of {a.corpus} failed: {e}")
    print(json.dumps({a.corpus: res}, sort_keys=True))
    return 0


_STATE = {}


def tr_state(tr):
    return _STATE


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    cmd = argv[0] if argv and argv[0] in COMMANDS else "invalid"
    tdir = prescan(argv, "--transcript-dir")
    # An abbreviation of an unbound option still reads as unbound here, so its
    # transcript goes where it names; the parser then refuses it.
    unbound_pre = any(x.startswith(f) for x in argv for f in ("--fixture-m", "--summ", "--sealed-s"))
    if cmd in ("fixtures", "export", "archive"):
        unbound_pre = True
    if cmd == "validation":
        unbound_pre = True
    if tdir and (not unbound_pre or inside(tdir, RESULTS)):
        tdir = None
    if cmd == "archive" and (not tdir or inside(tdir, os.path.dirname(SPIKE))):
        # archive's transcript never lands in the repository (H6): without a
        # --transcript-dir outside it, the refusal is recorded in a fresh
        # directory outside it.
        import tempfile
        tdir = tempfile.mkdtemp(prefix="mermaid-archive-transcript.")
        print(f"archive transcript: {tdir}", file=sys.stderr)
        argv_tdir_ok = False
    else:
        argv_tdir_ok = True
    tr = TR.Transcript(cmd, ["mermaid_spike.py"] + argv, tdir if unbound_pre else None)
    rc, how = 1, "exited"
    try:
        if not (sys.flags.isolated and sys.flags.no_site):
            tr.binding({"bound": False, "reasons": ["not run with python3 -I -S"]})
            raise SystemExit("refusing: run as `python3 -I -S -B harness/mermaid_spike.py`")
        rep = repeated(argv)
        if rep:
            tr.binding({"bound": False, "reasons": [f"repeated {', '.join(rep)}"]})
            raise SystemExit(f"refusing: {', '.join(rep)} given more than once")
        try:
            a = parser().parse_args(argv)
        except SystemExit:
            tr.binding({"bound": False, "reasons": ["usage error"]})
            raise
        unbound = unbound_requested(a) or a.cmd in ("fixtures", "export", "validation", "archive")
        for opt in ("private_map", "private_table", "bundles"):
            v = getattr(a, opt, None)
            if v and inside(v, os.path.dirname(SPIKE)):
                raise SystemExit(f"refusing: --{opt.replace('_', '-')} is the owner's private file; "
                                 "it must be outside the repository")
        if a.cmd == "archive" and not argv_tdir_ok:
            raise SystemExit("refusing: archive writes its transcript outside the repository (--transcript-dir)")
        if unbound != unbound_pre:
            raise SystemExit("refusing: the options parse differently from how they read")
        if unbound:
            state = {"bound": False, "reasons": [f"{a.cmd}: unbound run"]}
            if a.cmd in ("arm0", "arms", "repro", "sealed", "aggregate") and not tdir:
                tr.binding(state)
                raise SystemExit("refusing: an unbound run names --transcript-dir outside results/")
        else:
            state = BD.check(SPIKE, ARM_OF.get(a.cmd), tr.path)
            if a.cmd == "repro":
                state = dict(state, reasons=[r for r in state["reasons"] if "already executed" not in r])
                state["bound"] = not state["reasons"]
        tr.binding(state)
        _STATE.update(state)
        if a.cmd in BOUND_CMDS and not unbound:
            if not state["bound"]:
                for r in state["reasons"]:
                    print("not bound:", r, file=sys.stderr)
                raise SystemExit("refusing: this run would not be bound")
            fixed = {"out_dir": None, "extractor": None, "out": None, "summary": None, "committed": None}
            given = [k for k, v in fixed.items() if getattr(a, k, None) not in (None, v)]
            if given:
                raise SystemExit("refusing: a bound run takes no " + ", ".join("--" + g.replace("_", "-")
                                                                              for g in given))
            if a.cmd in ("arm0", "arms", "repro"):
                for opt in ("bundle_dir", "work_dir", "private_map", "private_table"):
                    v = getattr(a, opt)
                    if not v or inside(v, os.path.dirname(SPIKE)):
                        raise SystemExit(f"refusing: --{opt.replace('_', '-')} is required, outside the repository")
        rc = {"validation": cmd_validation, "arm0": cmd_arm0, "arms": cmd_arms, "repro": cmd_repro,
              "sealed": cmd_sealed, "aggregate": cmd_aggregate, "fixtures": cmd_fixtures, "export": cmd_export,
              "archive": cmd_archive}[a.cmd](a, tr, not unbound)
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 2)
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
        how = "aborted" if rc else "exited"
    except RB.Broken as e:
        print(f"R is broken: {e}", file=sys.stderr)
        rc, how = 3, "aborted: toolchain broken"
    except BaseException:
        traceback.print_exc()
        rc, how = 1, "aborted by an exception"
    finally:
        tr.close(rc, how)
    return rc


if __name__ == "__main__":
    sys.exit(main())
