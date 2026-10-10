#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION.md §11.2 V4: a mutation sweep over every gate, in the style
of blockspec's armed_check.sh.

    python3 -I -S -B harness/v4.py [--jobs N] [--timeout SECONDS] [--only SUBSTRING]

Each mutation breaks one gate in a scratch copy of spike/mermaid (harness/,
r/ with node_modules linked, census/, blind/, PRE-REGISTRATION.md), then runs
the copy's own checks: V3 for the harness, V0 (--no-install) for R's wrapper.
The mutated file is hashed before and after; a mutation whose pattern does
not occur exactly once leaves the file unchanged and is reported BROKEN,
never killed or survived. A mutant is killed only by a named check going red:
a run that only crashes a section ("section raised"), or that times out,
counts as surviving. V4 passes only with every mutant killed and none BROKEN.
"""
import argparse
import concurrent.futures
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)

# (name, file relative to spike/mermaid, old, new, checker: "v3" or "v0")
M = [
    # ---- the oracle (§5)
    ("decide: a model conflict is decided as leg O's value", "harness/ms/oracle.py",
     "        else:\n            mc.add(u)\n    absent", "        else:\n            dec[u] = o\n    absent", "v3"),
    ("decide: a membership with a holder decided absent stays decided", "harness/ms/oracle.py",
     "        if any(v and v in absent for v in vals):", "        if False:", "v3"),
    ("refusal: dangling never fires", "harness/ms/oracle.py",
     "            if k in absent:\n                dang", "            if False:\n                dang", "v3"),
    ("refusal: collision never fires", "harness/ms/oracle.py",
     "        if diff:\n            out.append((\"collision\"", "        if False:\n            out.append((\"collision\"", "v3"),
    ("refusal: delete/modify never fires", "harness/ms/oracle.py",
     "            if ch:\n                out.append((\"delete/modify\"", "            if False:\n                out.append((\"delete/modify\"", "v3"),
    ("I4 never fires", "harness/ms/oracle.py",
     "        if (mk and len(mk) > 1) or", "        if False and (mk and len(mk) > 1) or", "v3"),
    ("I4: a clash already in an input is a record", "harness/ms/oracle.py",
     "        if any(len(X.get(u) or ()) > 1 for X in (B, O, T)):\n            continue",
     "        if False:\n            continue", "v3"),
    ("tier B: a new lint failure does not demote", "harness/ms/oracle.py",
     '            r["tier"] = "B"', '            r["tier"] = "A"', "v3"),
    ("tier B: an old lint failure demotes too", "harness/ms/case.py",
     "    lint_new = lint_m - lint_in", "    lint_new = lint_m", "v3"),
    ("G1 is not outside I1-I4", "harness/ms/oracle.py",
     "            g1_outside = not (related(u, d) or related(u, m))", "            g1_outside = True", "v3"),
    ("exposure never fires", "harness/ms/oracle.py",
     "    keysB = present_keys(B)\n    for X, Y, leg", "    return False, None\n    keysB = present_keys(B)\n    for X, Y, leg", "v3"),
    ("MC: a merged value equal to a leg's is eligible", "harness/ms/oracle.py",
     "        if m in legs:\n            recs.append(_rec(\"MC-ineligible\"", "        if False:\n            recs.append(_rec(\"MC-ineligible\"", "v3"),
    ("L1 never fails", "harness/ms/oracle.py", '            out.add(("L1", k))', "            pass", "v3"),
    ("L2 never fails", "harness/ms/oracle.py", '            out.add(("L2", k))', "            pass", "v3"),
    ("G2: a lost edge is not reported", "harness/ms/oracle.py",
     '                recs.append(_rec("G2", _edge_objs(u, d), "A", [u],', '                recs.append(_rec("G9", _edge_objs(u, d), "A", [u],', "v3"),
    ("a holder is a reference (the census's v3 rule)", "harness/ms/oracle.py",
     "    return set()\n\n\ndef refers", "    return {v} if p in (\"nhold\", \"shold\") and v else set()\n\n\ndef refers", "v3"),
    # ---- the model (Appendix A)
    ("model: an edge to a subgraph makes a node", "harness/ms/model.py",
     "        if vid in skey and vid not in node_statement_ids:\n            continue",
     "        if False:\n            continue", "v3"),
    ("model: untitled subgraphs keyed by Mermaid's positional id", "harness/ms/model.py",
     '            skey[s["id"]] = "title:" + s["title"]', '            skey[s["id"]] = s["id"]', "v3"),
    # Not a mutant: "membership goes to the last subgraph to close" (setdefault
    # -> assignment in model.py) is equivalent, because Mermaid's makeUniq
    # already keeps every node in one subgraph's list (V4 run of 2026-10-10).
    ("model: a repeated untitled title is not DUP-TITLE", "harness/ms/model.py",
     "        if all(k.startswith(\"title:\") for k in dup):", "        if False:", "v3"),
    ("subset: H's model need not equal R's", "harness/ms/subset.py", "    if mh != mr:", "    if False:", "v3"),
    # ---- H
    ("H: labels with '<' are not sanitized", "harness/ms/hparse.py",
     '    if not t or "<" not in t:\n        return t', "    if True:\n        return t", "v3"),
    ("H: a node after an edge id of its name is kept", "harness/ms/hparse.py",
     "            self.swallowed.add(vid)\n            return", "            self.swallowed.add(vid)", "v3"),
    ("H: a shape-data label ignored", "harness/ms/hparse.py",
     '            if doc.get("label"):\n                v["text"] = doc["label"]', "            pass", "v3"),
    # ---- fences, selection (§3, §7.4)
    ("fence: any line closes a fence", "harness/ms/fence.py",
     "not (len(ls[j][1]) >= n and set(ls[j][1]) == {ch})", "False", "v3"),
    ("fence: the keyword test ignores case", "harness/ms/fence.py",
     '_KEYWORD = re.compile(r"(flowchart-elk|flowchart|graph)(?:[ \\t]|$)")',
     '_KEYWORD = re.compile(r"(flowchart-elk|flowchart|graph)(?:[ \\t]|$)", re.I)', "v3"),
    ("fence: two fences do not exclude", "harness/ms/fence.py", "    if len(fs) != 1:", "    if not fs:", "v3"),
    ("selection: generated path segments are kept", "harness/ms/fence.py",
     "    return any(seg.casefold() in GENERATED_SEGMENTS", "    return False and any(seg.casefold() in GENERATED_SEGMENTS", "v3"),
    ("selection: a declared generated file is kept", "harness/ms/fence.py",
     "    return any(_DECLARES.search(ln)", "    return False and any(_DECLARES.search(ln)", "v3"),
    ("selection: one co-changing commit makes a sibling derived", "harness/ms/history.py",
     "    return 2 * len(co) >= len(mine)", "    return len(co) >= 1", "v3"),
    # ---- the merge (F2) and E
    ("F2: the caller's XDG_CONFIG_HOME reaches git", "harness/ms/gitops.py",
     '"XDG_CONFIG_HOME": home,', '"XDG_CONFIG_HOME": os.environ.get("XDG_CONFIG_HOME", home),', "v3"),
    ("F2: an in-tree .gitattributes is honoured", "harness/ms/gitops.py",
     "            f.write(NEUTRAL_ATTRIBUTES)\n        git(repo, \"checkout\"", "            pass\n        git(repo, \"checkout\"", "v3"),
    ("E: a conflict is not E", "harness/ms/case.py",
     "    if merge.unmerged or G.has_new_marker(mtxt, inputs):", "    if False:", "v3"),
    ("G0: a merged file with two fences is judged", "harness/ms/case.py",
     '        res.update(outcome="G0", why=why)', '        res.update(outcome="JUDGED", why=why)', "v3"),
    ("P: every record is a P record", "harness/ms/case.py",
     "        if not any(M.get(u) != TR.get(u) for u in units):\n            continue", "        pass", "v3"),
    ("P: UNRELIABLE never marked", "harness/ms/case.py",
     '            r["unreliable"] = "a unit neither leg touched differs from the truth"', "            pass", "v3"),
    # ---- history (§7.5, §8.2, §8.3)
    ("P: the ancestry half of the predecessor rule dropped", "harness/ms/history.py",
     "                good = repo.is_ancestor(c0, c1) and", "                good =", "v3"),
    ("P: the first-parent half of the predecessor rule dropped", "harness/ms/history.py",
     "and bool(fp) and repo.blob_at(fp[0], path) == b0", "", "v3"),
    ("M-PR: rebase takes c~(k-1)", "harness/ms/history.py",
     "            if mine == theirs and None not in theirs:\n                target = cur",
     "            if mine == theirs and None not in theirs:\n                target = chain[-1]", "v3"),
    ("M-PR: the squash rule never matches", "harness/ms/history.py",
     "repo.patch_id(p, c) == repo.patch_id(mb[0], head)", "False", "v3"),
    ("M-PR: no 250-commit cap", "harness/ms/history.py",
     'if pr.get("commit_count", k) > 250 or k > 250:', "if False:", "v3"),
    ("authors: noreply not read as login", "harness/ms/history.py", "    if m:\n        e = m.group(1)", "    pass", "v3"),
    ("authors: names do not join", "harness/ms/history.py",
     '    return {"e:" + e, "n:" + (name or "").casefold()}', '    return {"e:" + e}', "v3"),
    ("replay: a non-unique anchor is used", "harness/ms/replay.py", "            if len(hits) != 1:", "            if not hits:", "v3"),
    # ---- the aggregator (§9)
    ("floor 59", "harness/ms/aggregate.py", "FLOOR = 60", "FLOOR = 59", "v3"),
    ("cap 31", "harness/ms/aggregate.py", "CAP = 30", "CAP = 31", "v3"),
    ("agreement 96%", "harness/ms/aggregate.py", "AGREEMENT = 0.98", "AGREEMENT = 0.96", "v3"),
    ("coverage bar 89%", "harness/ms/aggregate.py", "COVERAGE_BAR = 0.90", "COVERAGE_BAR = 0.89", "v3"),
    ("P counts toward identity k", "harness/ms/aggregate.py",
     'if c["arm"] in ("M-merge", "M-PR") and c.get("exposed") and c.get("inputs_in_subset"):',
     'if c["arm"] in ("M-merge", "M-PR", "P") and c.get("exposed") and c.get("inputs_in_subset"):', "v3"),
    ("k counts only judged cases", "harness/ms/aggregate.py",
     'if c["arm"] in ("M-merge", "M-PR") and c.get("exposed") and c.get("inputs_in_subset"):',
     'if c["arm"] in ("M-merge", "M-PR") and c.get("exposed") and c.get("inputs_in_subset") and c["outcome"] == "JUDGED":', "v3"),
    ("P's bound not stated as replayed", "harness/ms/aggregate.py", 'if by_arm["P"] * 2 > n', 'if by_arm["P"] > n', "v3"),
    ("F7 not required", "harness/ms/aggregate.py", "    if (r[\"category\"], tuple(sorted(r[\"objects\"]))) not in xr:\n        return \"F7\"",
     "    pass", "v3"),
    ("F8 not required", "harness/ms/aggregate.py", '    if not case.get("reproduces"):\n        return "F8"', "    pass", "v3"),
    ("VOID ignored", "harness/ms/aggregate.py", "                void[fx[\"group\"]] = True", "                pass", "v3"),
    ("a disputed structure fixture ignored", "harness/ms/aggregate.py",
     '        if disputed["structure"]:\n            reasons.append', '        if False:\n            reasons.append', "v3"),
    ("tier-A disagreement ignored", "harness/ms/aggregate.py",
     "        if any(_x_tier_a(c) != _h_tier_a(c) for c in decided_real(cases)):", "        if False:", "v3"),
    ("a blocked structure record ignored", "harness/ms/aggregate.py",
     '        if any(b["case"] in cnt_keys for b in blocked["structure"]):', "        if False:", "v3"),
    ("row 4 (c): a zero rate is shown", "harness/ms/aggregate.py",
     'v.get("x_confirmed_identity_a", 0) > 0', 'v.get("x_confirmed_identity_a", 0) >= 0', "v3"),
    ("row 4 (c) computed under (a)", "harness/ms/aggregate.py",
     '    elif summary.get("row4", "a") == "c":', '    elif True:', "v3"),
    ("units: identical diffs counted twice", "harness/ms/aggregate.py",
     '        if c["key"] in seen_k or c.get("diff_key") in seen_d:', '        if c["key"] in seen_k:', "v3"),
    ("units: an UNRELIABLE case counted", "harness/ms/aggregate.py",
     '            and not any(r.get("unreliable") for r in c.get("records", []))]', "]", "v3"),
    ("a P identity record can be FOUND", "harness/ms/aggregate.py",
     '            if g == "identity" and c["arm"] == "P":\n                anomalies', '            if False:\n                anomalies', "v3"),
    ("empty input accepted", "harness/ms/aggregate.py", '        raise ValueError("the aggregator has no input")', "        pass", "v3"),
    # ---- X (§10.5)
    ("X: a failed run agrees", "harness/ms/xrun.py", '        return False, f"X failed: {x_fail}"', '        return True, None', "v3"),
    ("X: exposure not compared", "harness/ms/xrun.py", '    if x_out["exposed"] != h_exposed:', "    if False:", "v3"),
    ("X: no timeout", "harness/ms/xrun.py", '            return None, "timeout"', '            return {"exposed": False, "records": []}, None', "v3"),
    # ---- redaction (§7.3, private individuals)
    ("redaction: an individual's commits published", "harness/ms/arms.py",
     '                sp[k] = K.h_commit(salt, sp[k])', '                pass', "v3"),
    ("redaction: read-only objects published", "harness/ms/arms.py",
     '                r["objects"] = [K.h_value(str(o)) for o in r.get("objects") or []]', '                pass', "v3"),
    ("redaction: authors published", "harness/ms/arms.py",
     '    c["authors"] = ["a:" + hashlib.sha256(a.encode()).hexdigest()[:16] for a in c.get("authors") or []]', '    pass', "v3"),
    # ---- binding, CLI, reverify
    ("binding: a later harness commit accepted", "harness/ms/binding.py",
     "        if later.strip():\n            reasons.append", "        if False:\n            reasons.append", "v3"),
    ("binding: a marker found only in the work tree", "harness/ms/binding.py",
     '    _, out, _ = _git(spike, "log", "--all", "--full-history", "--format=%H", "--diff-filter=A", "--", rel)\n    return bool(out.strip())',
     "    return False", "v3"),
    ("binding: a validation commit that edits the harness accepted", "harness/ms/binding.py",
     '_git(spike, "diff", "--quiet", f"{vc}^", vc, "--", *BOUND)[0] != 0', "False", "v3"),
    ("binding: uncommitted results accepted", "harness/ms/binding.py",
     '        reasons.append(f"uncommitted under results/: {line}")', "        pass", "v3"),
    ("binding: VALIDATION may change", "harness/ms/binding.py",
     '    if touched.split() != [vc]:', "    if False:", "v3"),
    ("CLI: repeated options accepted", "harness/mermaid_spike.py", "    rep = repeated(argv)\n", "    rep = []\n", "v3"),
    ("CLI: abbreviations accepted", "harness/mermaid_spike.py",
     "        p = sub.add_parser(name, allow_abbrev=False)", "        p = sub.add_parser(name)", "v3"),
    ("CLI: runs without -I -S", "harness/mermaid_spike.py", "        if not (sys.flags.isolated and sys.flags.no_site):",
     "        if False:", "v3"),
    ("CLI: an unbound aggregate may write under results/", "harness/mermaid_spike.py",
     '        if not a.out or inside(a.out, RESULTS):', "        if not a.out:", "v3"),
    ("CLI: a NO VERDICT corpus exits 0", "harness/mermaid_spike.py",
     '        print(f"NO VERDICT for {len(nv)} corpora: exit 3")\n        return 3\n    return 0\n\n\ndef coverage',
     '        return 0\n    return 0\n\n\ndef coverage', "v3"),
    ("reverify: drops the later-commit check", "harness/reverify.sh", '[ -z "$later" ]', "true", "v3"),
    ("reverify: drops the validation diff", "harness/reverify.sh",
     'g diff --quiet "$V^" "$V" -- "${bound[@]}"', "true", "v3"),
    ("reverify: VALIDATION may change", "harness/reverify.sh",
     '[ "$(g log --full-history --format=%H -- results/VALIDATION | wc -l)" -eq 1 ]', "true", "v3"),
    ("blind: X's spec drops Appendix D", "harness/ms/blind.py",
     'SECTIONS = ["## 4. The model", "## 5. The oracle", "## Appendix A", "## Appendix C", "## Appendix D"]',
     'SECTIONS = ["## 4. The model", "## 5. The oracle", "## Appendix A", "## Appendix C"]', "v3"),
    # ---- the review of nodespec#3: its 33 mutants (R1-R33), as the code now reads
    ("R1 identity: a disputed identity fixture ignored", "harness/ms/aggregate.py",
     '    elif disputed["identity"]:\n        ident.update(', '    elif False:\n        ident.update(', "v3"),
    ("R2 fixtures: VOID when X agrees with H", "harness/ms/aggregate.py",
     '            elif fx["x"] == fx["f"]:\n                void', '            elif fx["x"] == fx["h"]:\n                void', "v3"),
    ("R3 cap: author cap ignored", "harness/ms/aggregate.py",
     ' or any(per_a.get(a, 0) >= CAP for a in c["authors"]):', ':', "v3"),
    ("R4 cap: corpus cap ignored", "harness/ms/aggregate.py",
     '        if per_c.get(c["corpus"], 0) >= CAP or', '        if False or', "v3"),
    ("R5 F3 dropped", "harness/ms/aggregate.py",
     '    if case["outcome"] != "JUDGED" or not case.get("inputs_in_subset"):', '    if False:', "v3"),
    ("R6 tier filter dropped: B records become blocked", "harness/ms/aggregate.py",
     '            if g is None or r["tier"] != "A":', '            if g is None:', "v3"),
    ("R7 S counts as a real arm", "harness/ms/aggregate.py",
     'REAL = ("M-merge", "M-PR", "P")', 'REAL = ("M-merge", "M-PR", "P", "S")', "v3"),
    ("R8 k counts exposed cases with inputs out of the subset", "harness/ms/aggregate.py",
     'if c["arm"] in ("M-merge", "M-PR") and c.get("exposed") and c.get("inputs_in_subset"):',
     'if c["arm"] in ("M-merge", "M-PR") and c.get("exposed"):', "v3"),
    ("R9 coverage bar not applied to the floor", "harness/ms/aggregate.py",
     '    pool = [c for c in decided_real(cases) if coverage.get(c["stratum"], 0) >= COVERAGE_BAR]',
     '    pool = decided_real(cases)', "v3"),
    ("R10 blocked check reads the identity list", "harness/ms/aggregate.py",
     'for b in blocked["structure"]):', 'for b in blocked["identity"]):', "v3"),
    ("R11 agreement: exactly 98% fails", "harness/ms/aggregate.py",
     '    if not n or agree / n < AGREEMENT:', '    if not n or agree / n <= AGREEMENT:', "v3"),
    ("R12 exposure: both-legs-add clause dropped", "harness/ms/oracle.py",
     '    for k in sorted((present_keys(O) & present_keys(T)) - keysB):\n        if any(',
     '    for k in []:\n        if any(', "v3"),
    ("R13 exposure: only leg O's removals examined", "harness/ms/oracle.py",
     '    for X, Y, leg in ((O, T, "O"), (T, O, "T")):', '    for X, Y, leg in ((O, T, "O"),):', "v3"),
    ("R14 delete/modify: only one direction", "harness/ms/oracle.py",
     '        for X, Y in ((O, T), (T, O)):', '        for X, Y in ((O, T),):', "v3"),
    ("R15 collision ignores a kind difference", "harness/ms/oracle.py",
     '        diff = [u for u in set(O) | set(T) if keyed_by(u) == k and O.get(u) != T.get(u)]',
     '        diff = [u for u in set(O) | set(T) if keyed_by(u) == k and u[0] != "exist" and O.get(u) != T.get(u)]', "v3"),
    ("R16 undecided membership reads only the decided holder", "harness/ms/oracle.py",
     '        vals = {B.get(u), O.get(u), T.get(u)}', '        vals = set()', "v3"),
    ("R17 G3 never reported", "harness/ms/oracle.py",
     '            recs.append(_rec("G3", {u[1], d, m}', '            recs.append(_rec("G9", {u[1], d, m}', "v3"),
    ("R18 G4 ignores titles, links and user-id edge labels", "harness/ms/oracle.py",
     '        elif p in ("ntext", "stitle", "link", "etext"):', '        elif p in ("ntext",):', "v3"),
    ("R19 eligible MC of text is tier C", "harness/ms/oracle.py",
     '{"G2": "A", "G3": "A", "G4": "A", "C": "C", "D": "D"}', '{"G2": "A", "G3": "A", "G4": "C", "C": "C", "D": "D"}', "v3"),
    ("R20 tier B looks only at a record's first object", "harness/ms/oracle.py",
     '        if r["tier"] == "A" and failing & set(r["objects"]):', '        if r["tier"] == "A" and failing & set(r["objects"][:1]):', "v3"),
    ("R21 new lint: only the base's failures subtracted", "harness/ms/case.py",
     '    for s, txt in zip(prep["states"], inputs):', '    for s, txt in zip(prep["states"][:1], inputs[:1]):', "v3"),
    ("R22 UNRELIABLE: untouched read as base == O only", "harness/ms/case.py",
     '        if any(B.get(u) == O.get(u) == T.get(u) and', '        if any(B.get(u) == O.get(u) and', "v3"),
    ("R23 G0 is tier A", "harness/ms/case.py", '"objects": ["path:" + path], "tier": "B"', '"objects": ["path:" + path], "tier": "A"', "v3"),
    ("R24 M-PR rebase: patch-ids compared unordered", "harness/ms/history.py",
     '            if mine == theirs and None not in theirs:',
     '            if sorted(mine, key=str) == sorted(theirs, key=str) and None not in theirs:', "v3"),
    ("R25 M-PR squash: head diffed against c^", "harness/ms/history.py",
     'repo.patch_id(p, c) == repo.patch_id(mb[0], head)', 'repo.patch_id(p, c) == repo.patch_id(p, head)', "v3"),
    ("R26 P: the last predecessor step unchecked", "harness/ms/history.py",
     '                    if not all(ok[i:i + a + b]):', '                    if not all(ok[i:i + a + b - 1]):', "v3"),
    ("R27 M: convergent cases kept as evaluable", "harness/ms/history.py",
     '    if x_b == y_b:\n        return "convergent"', '    if False:\n        return "convergent"', "v3"),
    ("R28 decided ignores UNRELIABLE", "harness/ms/arms.py",
     '            and not any(r.get("unreliable") for r in records))', '            )', "v3"),
    ("R29 a case's authors are the leg tips", "harness/ms/arms.py",
     '            a, bot = ctx.author(ctx.last_changer(sp["base"], sp[leg], path))', '            a, bot = ctx.author(sp[leg])', "v3"),
    ("R30 P rank reversed", "harness/ms/arms.py",
     '{(1, 1): 0, (1, 3): 1, (3, 1): 2}', '{(1, 1): 2, (1, 3): 1, (3, 1): 0}', "v3"),
    ("R31 bound aggregate computes row 4 (c)", "harness/mermaid_spike.py",
     '    summary = {"row4": "a", "cases"', '    summary = {"row4": "c", "cases"', "v3"),
    ("R32 sealed: F's line always qualifying", "harness/mermaid_spike.py",
     '"line": line, "f": line in tiers,', '"line": line, "f": True,', "v3"),
    ("R33 bound aggregate: every case reproduces", "harness/mermaid_spike.py",
     '        c["reproduces"] = repro.get(c.get("key"), False)', '        c["reproduces"] = True', "v3"),
    # ---- the fixes for that review
    ("L5: a duplicated edge's ends do not fail", "harness/ms/oracle.py",
     '            out.add(("L5", u[1][0]))\n            out.add(("L5", u[1][1]))', '            pass', "v3"),
    ("X compared with H's records after P's truth filter", "harness/ms/arms.py",
     'XR.compare(res.get("records_unfiltered", res["records"]), case["exposed"], xo, xf)',
     'XR.compare(res["records"], case["exposed"], xo, xf)', "v3"),
    ("tier-A disagreement only over the counted cases", "harness/ms/aggregate.py",
     '        if any(_x_tier_a(c) != _h_tier_a(c) for c in decided_real(cases)):',
     '        if any(_x_tier_a(c) != _h_tier_a(c) for c in cnt):', "v3"),
    ("bound aggregate: missing repro results not refused", "harness/mermaid_spike.py",
     '        if missing:\n            raise SystemExit', '        if False:\n            raise SystemExit', "v3"),
    ("sealed: malformed tiers accepted", "harness/mermaid_spike.py",
     '    if not isinstance(t, list) or not all(isinstance(x, str) and x in TIER_LETTERS for x in t):',
     '    if False:', "v3"),
    ("sealed: an X tier outside the vocabulary accepted", "harness/mermaid_spike.py",
     '    if any(r.get("tier") not in X_TIERS for r in rs):\n        return None', '    pass', "v3"),
    ("sealed: a malformed X answer reads as agreeing with F", "harness/ms/aggregate.py",
     '            if fx["x"] is None:\n                # R-sealed', '            if False:\n                # R-sealed', "v3"),
    ("archive: failures not scrubbed", "harness/ms/corpus.py",
     '        return str(x).replace(url, "<url>").replace(name, "<corpus>").replace(name.split("/")[0], "<owner>")',
     '        return str(x)', "v3"),
    ("archive: private files inside the repository accepted", "harness/mermaid_spike.py",
     '            if v and inside(v, os.path.dirname(SPIKE)):\n                raise SystemExit(f"refusing: --{opt',
     '            if False:\n                raise SystemExit(f"refusing: --{opt', "v3"),
    ("archive: transcript allowed inside the repository", "harness/mermaid_spike.py",
     '        if a.cmd == "archive" and (not tdir or inside(tdir, os.path.dirname(SPIKE))):', '        if False:', "v3"),
    ("binding: LOG.md's sealed hash not compared", "harness/ms/binding.py",
     '    if rec != [v["sealed_sha256"]]:', '    if False:', "v3"),
    ("binding: a malformed bundle entry accepted", "harness/ms/binding.py",
     '            raise ValueError(f"bundle entry for {lab} is malformed")', '            pass', "v3"),
    ("k: duplicate diff pairs counted twice", "harness/ms/aggregate.py",
     '            if c["key"] in exposed or (c.get("diff_key") and c["diff_key"] in seen_d):',
     '            if c["key"] in exposed:', "v3"),
    ("P: a dropped (1,1) case falls back to (1,3)", "harness/ms/aggregate.py",
     '    pool = [c for c in pool if c["arm"] != "P" or chosen.get(tuple(c["path_i"])) is c]', '    pass', "v3"),
    ("S tier-A records not listed as blocked", "harness/ms/aggregate.py",
     '            if g is None or r["tier"] != "A":\n                continue', '            if g is None or r["tier"] != "A" or c["arm"] == "S":\n                continue', "v3"),
    ("G2 on a user-id edge suppressed by an identity record", "harness/ms/oracle.py",
     '            if "edge" in kinds and "edge" in set(d or ()) ^ set(m or ()):',
     '            if g1_outside and "edge" in kinds and "edge" in set(d or ()) ^ set(m or ()):', "v3"),
    ("replay: edits applied in forward order", "harness/ms/replay.py",
     "    for s, e, new in reversed(edits):", "    for s, e, new in edits:", "v2"),
    # ---- R (§4.4), checked by V0
    ("R: a broken canary does not abort", "r/rmodel.mjs",
     "      return { abort: true, cls, msg, canaryCls: e2?.constructor?.name ?? typeof e2 };",
     "      return { parse: false, hash: false, cls, msg };", "v0"),
    ("R: maxEdges left at the default", "r/rmodel.mjs", "if (!defaultEdges) CONFIG.maxEdges = 100000;", "", "v0"),
    ("R: an error with hash treated as a toolchain error", "r/rmodel.mjs",
     "    if (hasHash) return { parse: false, hash: true, cls, msg };", "", "v0"),
    ("R: securityLevel loose", "r/rmodel.mjs", "securityLevel: 'strict'", "securityLevel: 'loose'", "v0"),
    ("R: jsdom globals after the import", "r/rmodel.mjs",
     "  globalThis.document = dom.window.document;\n}\nconst mermaid = (await import('mermaid')).default;",
     "}\nconst mermaid = (await import('mermaid')).default;\nif (!noDom) globalThis.document = globalThis.window.document;",
     "v0"),
    ("R: not run offline", "harness/ms/rbridge.py", '    return ["unshare", "--net", "--map-root-user", "--"] + argv',
     "    return argv", "v0"),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def copy_spike(dst):
    for d in ("harness", "census", "blind", "v-fixtures"):
        if not os.path.isdir(os.path.join(SPIKE, d)):
            continue
        shutil.copytree(os.path.join(SPIKE, d), os.path.join(dst, d), ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(dst, "r"))
    for f in os.listdir(os.path.join(SPIKE, "r")):
        src = os.path.join(SPIKE, "r", f)
        if f == "node_modules":
            os.symlink(src, os.path.join(dst, "r", f))
        elif os.path.isfile(src):
            shutil.copy(src, os.path.join(dst, "r", f))
    shutil.copy(os.path.join(SPIKE, "PRE-REGISTRATION.md"), dst)
    shutil.copy(os.path.join(SPIKE, "LOG.md"), dst)


def run_checker(root, which, timeout):
    """v3 (and, once F's V-fixtures are committed, vfix.py v3 on them), v0
    (--no-install) or v2."""
    runs = {"v3": [["v3.py"]], "v0": [["v0.py", "--no-install"]], "v2": [["v2.py"]]}[which]
    if which == "v3" and any(os.path.isfile(os.path.join(root, "v-fixtures", d, "expect.json"))
                             for d in (os.listdir(os.path.join(root, "v-fixtures"))
                                       if os.path.isdir(os.path.join(root, "v-fixtures")) else [])):
        runs.append(["vfix.py", "v3", "--dir", os.path.join(root, "v-fixtures")])
    rc_all, out_all = 0, ""
    for script, *args in runs:
        argv = [sys.executable, "-I", "-S", "-B", os.path.join(root, "harness", script)] + args
        try:
            r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, cwd=root)
        except subprocess.TimeoutExpired as e:
            out = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
            return None, out_all + out, True
        rc_all = rc_all or r.returncode
        out_all += r.stdout
    return rc_all, out_all, False


def mutant(n, mu, tmp, timeout):
    name, rel, old, new, which = mu
    root = tempfile.mkdtemp(prefix=f"m{n:03d}.", dir=tmp)
    try:
        copy_spike(root)
        p = os.path.join(root, rel)
        before = sha(p)
        src = open(p, encoding="utf-8").read()
        count = src.count(old)
        if count == 1:
            with open(p, "w", encoding="utf-8") as f:
                f.write(src.replace(old, new))
        after = sha(p)
        if before == after:
            return f"MUTATION {n:3} {name}: BROKEN -- pattern found {count} times, file unchanged ({before})", "broken"
        rc, out, to = run_checker(root, which, timeout)
        if to:
            return f"MUTATION {n:3} {name}: *** SURVIVED (timeout after {timeout}s) [{before} -> {after}] ***", "survived"
        fails = [ln.strip()[6:] for ln in out.splitlines() if ln.strip().startswith("FAIL")]
        named = [f for f in fails if not f.startswith("section raised")]
        if rc != 0 and named:
            return (f"MUTATION {n:3} {name}: KILLED by {which} [{before} -> {after}] "
                    f"({len(named)} red; first: {named[0][:100]})"), "killed"
        if rc != 0:
            return (f"MUTATION {n:3} {name}: *** KILLED ONLY BY A CRASH [{before} -> {after}] "
                    f"({(fails or ['(no FAIL line)'])[0][:100]}) ***"), "survived"
        return f"MUTATION {n:3} {name}: *** SURVIVED [{before} -> {after}] -- {which} stayed green ***", "survived"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--only")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="v4.")
    try:
        print("=== 0. baseline: the unmutated copy, V3 and V0")
        base = tempfile.mkdtemp(prefix="base.", dir=tmp)
        copy_spike(base)
        for which in ("v3", "v0", "v2"):
            rc, out, to = run_checker(base, which, a.timeout)
            print(f"   {which}: " + (out.strip().splitlines() or ["(no output)"])[-1])
            if rc != 0:
                print("baseline is not green; stop")
                return 1
        muts = [(i, m) for i, m in enumerate(M, 1) if not a.only or a.only in m[0]]
        print(f"\n=== {len(muts)} mutations, timeout {a.timeout}s each: each must turn its checker red")
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
            res = list(ex.map(lambda im: mutant(im[0], im[1], tmp, a.timeout), muts))
        tally = {"killed": 0, "survived": 0, "broken": 0}
        for line, kind in res:
            print(line)
            tally[kind] += 1
        print(f"\n{len(muts)} mutants: {tally['killed']} killed, {tally['survived']} survived, {tally['broken']} BROKEN")
        ok = tally["killed"] == len(muts) and len(muts) > 0
        print("V4:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
