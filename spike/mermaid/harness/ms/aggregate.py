# SPDX-License-Identifier: MIT
"""§9: the verdicts, from a summary of every case. A pure function, so V3
can reach every verdict path with planted summaries.

A summary is {"row4": "a"|"c", "cases": [case], "coverage": {stratum:
fraction}, "sealed": [fixture], "s_rates": {stratum: {...}}}. A case is
{"key", "diff_key", "arm", "corpus", "stratum", "authors", "path_i",
"rank", "decided", "exposed", "inputs_in_subset", "outcome", "records",
"x_agree", "x_records", "x_tier_a", "reproduces"}; a record is {"category",
"objects", "tier", "group"?, "unreliable"?}. A sealed fixture is {"name",
"group": "identity"|"structure", "line": "A"|"B", "f", "h", "x"}: whether F,
H and X put it on the qualifying side of that line.
"""
FLOOR = 60
CAP = 30
AGREEMENT = 0.98
COVERAGE_BAR = 0.90
IDENTITY = {"I1", "I2", "I3", "I4"}
STRUCTURE = {"G0", "G1", "G2", "G3", "G4"}
REAL = ("M-merge", "M-PR", "P")


def group_of(r):
    c = r["category"]
    if c in IDENTITY:
        return "identity"
    if c in STRUCTURE or (c == "MC" and r.get("group") in ("G2", "G3", "G4")):
        return "structure"
    return None


def _robj(case, r):
    return {"arm": case["arm"], "corpus": case["corpus"], "stratum": case["stratum"], "case": case["key"],
            "category": r["category"], "objects": r["objects"], "tier": r["tier"]}


def fixtures(sealed):
    """§10.4: ({group: VOID?}, {group: [disputed fixture]})."""
    void, disputed = {"identity": False, "structure": False}, {"identity": [], "structure": []}
    for fx in sealed:
        if fx["h"] != fx["f"]:
            if fx["x"] == fx["f"]:
                void[fx["group"]] = True
            elif fx["x"] == fx["h"]:
                disputed[fx["group"]].append(fx)
    return void, disputed


def conditions(case, r, void):
    """F1-F9 for one tier-A record: the first that fails, or None."""
    g = group_of(r)
    if case["arm"] not in REAL or (g == "identity" and case["arm"] == "P"):
        return "F1"
    if case["outcome"] != "JUDGED" or not case.get("inputs_in_subset"):
        return "F3"
    if r["tier"] != "A":
        return "F4"
    if case["arm"] == "P" and r.get("unreliable"):
        return "F5"
    xr = {(x["category"], tuple(sorted(map(str, x.get("objects") or [])))) for x in case.get("x_records") or []}
    if (r["category"], tuple(sorted(r["objects"]))) not in xr:
        return "F7"
    if not case.get("reproduces"):
        return "F8"
    if void.get(g):
        return "F9"
    return None


def counted(cases, coverage):
    """§7.5, §8.3, §9.1: the structure group's decided cases under the caps:
    from M and P, from strata that pass the coverage bar, distinct by key and
    by pair of model diffs, one per P (path, i), at most 30 per corpus and per
    author. Deterministic: taken in key order."""
    seen_k, seen_d, seen_pi = set(), set(), set()
    per_c, per_a, out = {}, {}, []
    pool = [c for c in cases if c["arm"] in REAL and c.get("decided")
            and coverage.get(c["stratum"], 0) >= COVERAGE_BAR
            and not any(r.get("unreliable") for r in c.get("records", []))]
    pool.sort(key=lambda c: (c.get("rank", 0), c["key"]))
    for c in pool:
        if c["key"] in seen_k or c.get("diff_key") in seen_d:
            continue
        if c["arm"] == "P":
            if tuple(c["path_i"]) in seen_pi:
                continue
        if per_c.get(c["corpus"], 0) >= CAP or any(per_a.get(a, 0) >= CAP for a in c["authors"]):
            continue
        seen_k.add(c["key"])
        if c.get("diff_key"):
            seen_d.add(c["diff_key"])
        if c["arm"] == "P":
            seen_pi.add(tuple(c["path_i"]))
        per_c[c["corpus"]] = per_c.get(c["corpus"], 0) + 1
        for a in c["authors"]:
            per_a[a] = per_a.get(a, 0) + 1
        out.append(c)
    return out


def verdict(summary):
    cases = summary["cases"]
    if not cases:
        raise ValueError("the aggregator has no input")
    coverage = summary.get("coverage", {})
    void, disputed = fixtures(summary.get("sealed", []))
    found = {"identity": [], "structure": []}
    voided = {"identity": [], "structure": []}
    blocked = {"identity": [], "structure": []}
    anomalies, refusals, near = [], [], []
    for c in cases:
        for r in c.get("records", []):
            g = group_of(r)
            if r["tier"] == "B":
                refusals.append(_robj(c, r))
            if r["tier"] == "C":
                near.append(_robj(c, r))
            if g is None or r["tier"] != "A" or c["arm"] == "S":
                continue
            if g == "identity" and c["arm"] == "P":
                anomalies.append(_robj(c, r))  # §6: listed, never FOUND, no verdict
                continue
            why = conditions(c, r, void)
            if why is None:
                found[g].append(_robj(c, r))
            elif why == "F9":
                voided[g].append(_robj(c, r))
            else:
                blocked[g].append(dict(_robj(c, r), failed=why))

    out = {"lists": {"blocked": blocked, "p_anomalies": anomalies, "with_refusals": refusals,
                     "with_near_misses": near, "found_in_voided_group": voided,
                     "disputed_fixtures": {g: [f["name"] for f in v] for g, v in disputed.items()},
                     "strata_below_coverage": sorted(s for s, v in coverage.items() if v < COVERAGE_BAR),
                     "s_generator_rates": summary.get("s_rates", {})}}

    # ---- identity
    exposed = {c["key"]: c for c in cases if c["arm"] in ("M-merge", "M-PR") and c.get("exposed")
               and c.get("inputs_in_subset")}
    k = len(exposed)
    ident = {"k": k, "exposed_cases": sorted(({"corpus": c["corpus"], "arm": c["arm"], "outcome": c["outcome"]}
                                              for c in exposed.values()), key=lambda x: repr(x))}
    if found["identity"]:
        ident.update(verdict="FOUND", arms=sorted({r["arm"] for r in found["identity"]}), found=found["identity"])
    elif void["identity"]:
        ident.update(verdict="NO VERDICT", reason="VOID")
    elif disputed["identity"]:
        ident.update(verdict="NO VERDICT", reason="disputed sealed fixture: "
                     + ", ".join(f["name"] for f in disputed["identity"]))
    elif summary.get("row4", "a") == "c":
        rates = summary.get("s_rates", {})
        shown = any(v.get("x_confirmed_identity_a", 0) > 0 for v in rates.values())
        ident.update(verdict="MECHANISM SHOWN, frequency unmeasured" if shown else "MECHANISM NOT SHOWN",
                     census_reason="not exposed" if k == 0 else f"{k} exposed, none silent")
    elif k == 0:
        ident.update(verdict="NO VERDICT", reason="not exposed")
    else:
        ident.update(verdict="NO VERDICT", reason=f"{k} exposed, none silent")
    out["identity"] = ident

    # ---- structure
    cnt = counted(cases, coverage)
    n = len(cnt)
    by_arm = {a: sum(1 for c in cnt if c["arm"] == a) for a in REAL}
    agree = sum(1 for c in cnt if c.get("x_agree"))
    st = {"n": n, "n_by_arm": by_arm, "agreement": (agree / n) if n else None}
    if found["structure"]:
        st.update(verdict="FOUND", arms=sorted({r["arm"] for r in found["structure"]}), found=found["structure"])
    else:
        reasons = []
        if void["structure"]:
            reasons.append("VOID")
        if n < FLOOR:
            reasons.append(f"floor: {n} decided cases under the caps, below {FLOOR}")
        if not n or agree / n < AGREEMENT:
            reasons.append(f"agreement {agree}/{n} below {AGREEMENT:.0%}" if n else "agreement over zero cases")
        if any(_x_tier_a(c) != _h_tier_a(c) for c in cnt):
            reasons.append("a tier-A structure disagreement between H and X")
        cnt_keys = {c["key"] for c in cnt}
        if any(b["case"] in cnt_keys for b in blocked["structure"]):
            reasons.append("a blocked structure record among the decided cases")
        if disputed["structure"]:
            reasons.append("disputed sealed fixture: " + ", ".join(f["name"] for f in disputed["structure"]))
        if reasons:
            st.update(verdict="NO VERDICT", reason="; ".join(reasons))
        else:
            st.update(verdict="NOT FOUND", bound=3 / n,
                      bounds="real consecutive edits replayed as concurrent, not real merges"
                      if by_arm["P"] * 2 > n else "real concurrent editing")
    out["structure"] = st
    return out


def _h_tier_a(c):
    return {(r["category"], tuple(sorted(r["objects"]))) for r in c.get("records", [])
            if r["tier"] == "A" and group_of(r) == "structure"}


def _x_tier_a(c):
    return {(e[0], tuple(sorted(map(str, e[1])))) for e in c.get("x_tier_a") or []}
