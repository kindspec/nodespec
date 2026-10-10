# SPDX-License-Identifier: MIT
"""§4.3: "A blob is in the subset only if H parses it and H's model equals R's
model." One diagram text in, one State out."""
from . import hparse as H
from . import model as MD


class State:
    """status: "in" | "noparse" | "out" | "duptitle".
    model: H's model when "in". db: H's parse (for the lints) when H parsed.
    reason: why it is not "in"."""
    __slots__ = ("status", "model", "db", "reason", "r")

    def __init__(self, status, model=None, db=None, reason=None, r=None):
        self.status, self.model, self.db, self.reason, self.r = status, model, db, reason, r

    def __repr__(self):
        return f"State({self.status}, {self.reason!r})"


def classify(text, r):
    """r: R's result for this text (rbridge)."""
    if not r.get("parse"):
        return State("noparse", reason=f"{r.get('cls')}: {r.get('msg')}", r=r)
    try:
        db = H.parse(text)
    except H.Refuse as e:
        return State("out", reason=f"H refuses: {e.args[0]}", r=r)
    except RecursionError:
        return State("out", reason="H refuses: nesting too deep", r=r)
    try:
        mh = MD.from_h(db)
    except MD.DupTitle as e:
        return State("duptitle", db=db, reason=e.args[0], r=r)
    except MD.OutOfSubset as e:
        return State("out", db=db, reason=f"H refuses: {e.args[0]}", r=r)
    try:
        mr = MD.from_r(r)
    except MD.DupTitle as e:
        return State("duptitle", db=db, reason=e.args[0], r=r)
    except MD.OutOfSubset as e:
        return State("out", db=db, reason=f"R's model: {e.args[0]}", r=r)
    if mh != mr:
        return State("out", db=db, reason="H's model differs from R's: " + "; ".join(MD.describe_diff(mh, mr)),
                     r=r)
    return State("in", model=mh, db=db, r=r)
