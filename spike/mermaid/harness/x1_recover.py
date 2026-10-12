"""Recover X's first-invocation output from the record.

X's work directory was revised in place by invocations 2 and 3, so X1's
files survive only in the record:

- extract2.py: invocation 2 copied it to /tmp/extract2.orig.py (its
  scratch is kept by --scratch) after one Edit, which is undone here;
- CHOICES.md: invocation 1 wrote and changed it only with Write and Edit,
  so replaying those calls rebuilds it; invocation 2's first Read of it,
  made before any edit, must show the same lines.

The copy of extract2.py is checked against every partial Read invocation 2
made of the file before editing it. Both files are written to OUT.

usage: x1_recover.py X1_SESSION X2_SESSION X2_ORIG_PY OUT_DIR
"""
import hashlib
import json
import os
import re
import sys

x1_session, session, orig_py, out = sys.argv[1:5]

events = [json.loads(l) for l in open(session, encoding="utf-8") if l.strip()]
uses = {}
order = []
results = {}
for ev in events:
    for c in (ev.get("message") or {}).get("content") or []:
        if not isinstance(c, dict):
            continue
        if c.get("type") == "tool_use":
            uses[c["id"]] = c
            order.append(c["id"])
        elif c.get("type") == "tool_result":
            body = c.get("content")
            if isinstance(body, list):
                body = "".join(b.get("text", "") for b in body if isinstance(b, dict))
            results[c["tool_use_id"]] = body


def edits(c):
    if c["name"] in ("Write", "Edit"):
        return True
    return c["name"] == "Bash" and "extract2.py" in c["input"].get("command", "") \
        and re.search(r"open\([^)]*['\"]w['\"]|>\s*/?\S*extract2\.py|sed -i|cp ", c["input"]["command"])


LINE = re.compile(r"^\s*(\d+)\t(.*)$")


def numbered(text):
    rows = {}
    for line in text.split("\n"):
        m = LINE.match(line)
        if m:
            rows[int(m.group(1))] = m.group(2)
    return rows


py = open(orig_py, encoding="utf-8").read()
cp_at = next(i for i, uid in enumerate(order) if uses[uid]["name"] == "Bash"
             and "cp extract2.py /tmp/extract2.orig.py" in uses[uid]["input"]["command"])
for uid in reversed(order[:cp_at]):
    c = uses[uid]
    if c["name"] == "Edit" and c["input"]["file_path"].endswith("/extract2.py"):
        a, b = c["input"]["old_string"], c["input"]["new_string"]
        if py.count(b) != 1:
            sys.exit("cannot undo an Edit made before the copy")
        py = py.replace(b, a)
        print("undone: one Edit made before the copy")
    elif edits(c):
        sys.exit("an unexpected write before the copy")
py = py.split("\n")
choices = None
checked = 0
for uid in order:
    c = uses[uid]
    if edits(c):
        break
    if c["name"] != "Read":
        continue
    path = c["input"]["file_path"]
    rows = numbered(results.get(uid) or "")
    if path.endswith("/CHOICES.md") and choices is None and "offset" not in c["input"]:
        choices = rows
    elif path.endswith("/extract2.py"):
        for n, text in rows.items():
            if py[n - 1] != text:
                sys.exit(f"extract2.py copy differs from invocation 2's Read at line {n}")
            checked += 1

if choices is None:
    sys.exit("no whole Read of CHOICES.md before the first edit")
n = max(choices)
if sorted(choices) != list(range(1, n + 1)):
    sys.exit("CHOICES.md Read has gaps")

written = {}
for line in open(x1_session, encoding="utf-8"):
    ev = json.loads(line) if line.strip() else {}
    for c in (ev.get("message") or {}).get("content") or []:
        if not isinstance(c, dict) or c.get("type") != "tool_use":
            continue
        i = c["input"]
        if c["name"] == "Write":
            written[i["file_path"]] = i["content"]
        elif c["name"] == "Edit" and i["file_path"] in written:
            s = written[i["file_path"]]
            if not i.get("replace_all") and s.count(i["old_string"]) != 1:
                sys.exit("an invocation-1 Edit does not apply exactly once")
            written[i["file_path"]] = s.replace(i["old_string"], i["new_string"],
                                                -1 if i.get("replace_all") else 1)
        elif c["name"] == "Bash" and "CHOICES" in i.get("command", ""):
            sys.exit("invocation 1 touched CHOICES.md from Bash")
text = written["/work/CHOICES.md"]
seen = text.split("\n")
if seen[-1] == "":
    seen.pop()
read = [choices[i] for i in range(1, n + 1)]
if read[-1] == "" and len(read) == len(seen) + 1:
    read.pop()
if read != seen:
    sys.exit("CHOICES.md replay differs from invocation 2's Read")
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "CHOICES.md"), "w", encoding="utf-8").write(text)
open(os.path.join(out, "extract2.py"), "w", encoding="utf-8").write("\n".join(py))
for name in ("extract2.py", "CHOICES.md"):
    h = hashlib.sha256(open(os.path.join(out, name), "rb").read()).hexdigest()
    print(f"{h}  {name}")
print(f"extract2.py lines checked against invocation 2's Reads: {checked}")
print(f"CHOICES.md lines: {n}")
