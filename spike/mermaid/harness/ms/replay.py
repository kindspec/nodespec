# SPDX-License-Identifier: MIT
"""Appendix B.1: line replay for arm P.

Compute difflib.SequenceMatcher(None, A, C, autojunk=False) over the lines of
A = V[i+a] and C = V[i+a+b]. For each opcode other than `equal`, its anchor
is the nearest unchanged line before it in A, or the start of the text. Place
the edit in V[i] after the unique line equal to the anchor, provided the lines
it replaces follow there exactly. If the anchor is not unique, is absent, or
the replaced lines differ, the case is non-commuting.

Lines keep their terminators, so a replay is exact bytes. R-replay-overlap:
two edits placed on overlapping lines of V[i] are non-commuting too.
"""
import difflib


class NonCommuting(Exception):
    pass


def replay(base, a_text, c_text):
    """V[i] with the edits A -> C replayed on it, or NonCommuting."""
    V = base.splitlines(keepends=True)
    A = a_text.splitlines(keepends=True)
    C = c_text.splitlines(keepends=True)
    ops = difflib.SequenceMatcher(None, A, C, autojunk=False).get_opcodes()
    unchanged = set()
    for tag, i1, i2, _, _ in ops:
        if tag == "equal":
            unchanged.update(range(i1, i2))
    edits = []
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            continue
        prev = [k for k in unchanged if k < i1]
        if prev:
            anchor = A[max(prev)]
            hits = [k for k, ln in enumerate(V) if ln == anchor]
            if len(hits) != 1:
                raise NonCommuting(f"anchor {'absent' if not hits else 'not unique'}: {anchor!r}")
            at = hits[0] + 1
        else:
            at = 0
        if V[at:at + (i2 - i1)] != A[i1:i2]:
            raise NonCommuting(f"replaced lines differ at line {at + 1}")
        edits.append((at, at + (i2 - i1), C[j1:j2]))
    edits.sort()
    for (s1, e1, _), (s2, e2, _) in zip(edits, edits[1:]):
        if s2 < e1 or (s2 == s1 and e1 == s1 and e2 == s2):
            raise NonCommuting("two edits land on the same lines")
    out = list(V)
    for s, e, new in reversed(edits):
        out[s:e] = new
    return "".join(out)
