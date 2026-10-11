# SPDX-License-Identifier: MIT
"""§10.5: runs X, the second extractor, and compares it with H.

X's contract (Appendix D's extractor paragraph): `python3 -I extract2.py
<stratum> <base> <o> <t> <merged>` prints one JSON object: the decided
values, the exposure, and every record with its category, objects and tier.
The contract names those things but not their JSON keys. x_view maps X's
names onto H's (LOG §8): the exposure from "exposure" -> "exposed", the
records from "records" of {"category", "objects", "tier"}.

H and X agree on a case if they report equal sets of (category, objects) and
the same exposure. A crash, a timeout, or an empty or unreadable output from
X is a disagreement, never an agreement. Compared categories are §5.3's
records: I1-I4, G0-G4, MC, C, D, S-LINKSTYLE, S-ORDER. Case outcomes (E,
OUT-OF-SUBSET, DUP-TITLE) are not records; H's "MC-ineligible" is reported
only and is not compared.
"""
import json
import os
import shutil
import subprocess
import tempfile

CATS = {"I1", "I2", "I3", "I4", "G0", "G1", "G2", "G3", "G4", "MC", "C", "D", "S-LINKSTYLE", "S-ORDER"}
TIMEOUT = 120


# §5.3's "A record's objects" defines objects for I1-I4, G0 and G1-G4 only;
# for MC, C, D, S-LINKSTYLE and S-ORDER the text gives none, so those are
# compared by category alone (R-x-compare).
OBJECTS_DEFINED = {"I1", "I2", "I3", "I4", "G0", "G1", "G2", "G3", "G4"}


def norm_records(recs):
    out = set()
    for r in recs:
        if not isinstance(r, dict) or r.get("category") not in CATS:
            continue
        if r["category"] not in OBJECTS_DEFINED:
            out.add((r["category"], ()))
            continue
        objs = r.get("objects")
        if isinstance(objs, str):
            objs = [objs]
        out.add((r["category"], tuple(sorted(str(o) for o in (objs or [])))))
    return out


def run_x(extractor, stratum, texts, timeout=TIMEOUT):
    """texts: base, o, t, merged (str). Returns (parsed output or None,
    failure reason or None)."""
    d = tempfile.mkdtemp(prefix="xrun.")
    try:
        ext = "md" if stratum == "D" else "mmd"
        paths = []
        for name, t in zip(("base", "o", "t", "merged"), texts):
            p = os.path.join(d, f"{name}.{ext}")
            with open(p, "wb") as f:
                f.write(t.encode("utf-8"))
            paths.append(p)
        try:
            r = subprocess.run(["python3", "-I", extractor, stratum] + paths, capture_output=True, text=True,
                               timeout=timeout, cwd=d, env={"PATH": os.environ.get("PATH", ""), "LC_ALL": "C.UTF-8"})
        except subprocess.TimeoutExpired:
            return None, "timeout"
        if r.returncode != 0:
            return None, f"exit {r.returncode}: {r.stderr.strip()[-200:]}"
        if not r.stdout.strip():
            return None, "empty output"
        try:
            o = json.loads(r.stdout)
        except ValueError:
            return None, "output is not one JSON object"
        v = x_view(o)
        if v is None:
            return None, "output lacks records or an exposure"
        return v, None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def x_view(o):
    """R-x-names (LOG §8): X's output read under H's names. X prints the
    exposure as {"exposure": {"exposed": <bool>, ...}} and its records as
    {"category", "objects", "tier", ...}, as its CHOICES.md entry 1 says. A
    top-level boolean "exposed" is read as well. Returns {"exposed",
    "records", "raw"} or None."""
    if not isinstance(o, dict) or not isinstance(o.get("records"), list):
        return None
    if isinstance(o.get("exposed"), bool):
        exp = o["exposed"]
    elif isinstance(o.get("exposure"), dict) and isinstance(o["exposure"].get("exposed"), bool):
        exp = o["exposure"]["exposed"]
    else:
        return None
    recs = []
    for r in o["records"]:
        if isinstance(r, dict) and r.get("category") == "G0":
            # §5.3: G0's object is the path. X names it by the merged file's
            # path on disk, H by "path"; both mean the case's one path.
            r = dict(r, objects=["path"])
        recs.append(r)
    return {"exposed": exp, "records": recs, "raw_keys": sorted(o)}


def compare(h_records, h_exposed, x_out, x_fail):
    """(agree, detail). A failed X run is a disagreement."""
    if x_fail is not None or x_out is None:
        return False, f"X failed: {x_fail}"
    hs, xs = norm_records(h_records), norm_records(x_out["records"])
    if x_out["exposed"] != h_exposed:
        return False, f"exposure: H {h_exposed}, X {x_out['exposed']}"
    if hs != xs:
        return False, f"H only {sorted(hs - xs)[:3]}; X only {sorted(xs - hs)[:3]}"
    return True, None


def tier_a_structure(recs):
    return {(r["category"], tuple(sorted(r["objects"]))) for r in recs
            if r.get("tier") == "A" and (r["category"] in ("G1", "G2", "G3", "G4") or
                                          (r["category"] == "MC" and r.get("group") in ("G2", "G3", "G4")))}


def x_tier_a_structure(x_out):
    if not x_out:
        return set()
    out = set()
    for r in x_out.get("records", []):
        if r.get("tier") == "A" and r.get("category") in ("G1", "G2", "G3", "G4", "MC"):
            out.add((r["category"], tuple(sorted(str(o) for o in r.get("objects") or []))))
    return out
