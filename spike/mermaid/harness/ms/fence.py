# SPDX-License-Identifier: MIT
"""§3: Mermaid fences, the flowchart test, and §7.4's generated-file rules.

READINGS (README "Readings", R-fence-*):
- A closing line holds only the run: no indentation and no trailing
  whitespace, a "\\r" before the newline aside.
- An opener with no closing line is a fence whose body runs to the end of
  the file.
- The body is the text between the opener's line and the closing line,
  exactly.
"""
import re

OPENER = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*mermaid(-example)?\b", re.IGNORECASE)
_KEYWORD = re.compile(r"(flowchart-elk|flowchart|graph)(?:[ \t]|$)")


def _lines(text):
    """(start, line without its terminator, end) for each "\\n"-ended line."""
    out, pos = [], 0
    for ln in text.split("\n"):
        ln = ln + "\n" if pos + len(ln) < len(text) else ln
        if not ln:
            break
        body = ln[:-1] if ln.endswith("\n") else ln
        if body.endswith("\r"):
            body = body[:-1]
        out.append((pos, body, pos + len(ln)))
        pos += len(ln)
    return out


def fences(text):
    """Every Mermaid fence: list of (body, opener line number)."""
    ls = _lines(text)
    out, i = [], 0
    while i < len(ls):
        m = OPENER.match(ls[i][1])
        if not m:
            i += 1
            continue
        run = m.group(1)
        ch, n = run[0], len(run)
        start = ls[i][2]
        j = i + 1
        while j < len(ls) and not (len(ls[j][1]) >= n and set(ls[j][1]) == {ch}):
            j += 1
        end = ls[j][0] if j < len(ls) else len(text)
        out.append((text[start:end], i + 1))
        i = j + 1
    return out


def is_flowchart(diagram):
    """§3: the first line that is not blank, not a %% comment, and not inside
    a leading --- front-matter block starts with flowchart, flowchart-elk or
    graph, in lower case, followed by whitespace or the end of the line.
    READING: leading whitespace on that line is allowed (Mermaid's detector
    allows it), and a front-matter block leads only if its '---' is the first
    non-blank line."""
    ls = [b for _, b, _ in _lines(diagram)]
    i = 0
    while i < len(ls) and not ls[i].strip():
        i += 1
    if i < len(ls) and ls[i].strip() == "---":
        j = i + 1
        while j < len(ls) and ls[j].strip() != "---":
            j += 1
        i = j + 1
    while i < len(ls):
        s = ls[i].strip()
        if s and not s.startswith("%%"):
            return bool(_KEYWORD.match(s))
        i += 1
    return False


def diagram_of(stratum, text):
    """The diagram of a stratum-F file (the file) or a stratum-D file (the
    body of its one Mermaid fence). Returns (diagram, None) or (None, why)."""
    if stratum == "F":
        return (text, None) if is_flowchart(text) else (None, "not a flowchart")
    fs = fences(text)
    if len(fs) != 1:
        return None, f"{len(fs)} Mermaid fences"
    if not is_flowchart(fs[0][0]):
        return None, "its fence is not a flowchart"
    return fs[0][0], None


# ------------------------------------------------------- §7.4 generated files

GENERATED_SEGMENTS = {"testdata", "test", "tests", "__tests__", "__snapshots__", "snapshots", "baseline",
                      "baselines", "fixture", "fixtures", "generated", "gen", "dist", "build", "out",
                      "node_modules", "vendor"}
_DECLARES = re.compile(r"auto-?generated|do not edit", re.IGNORECASE)


def generated_by_path(path):
    """Any directory segment, case-folded, in §7.4's list."""
    return any(seg.casefold() in GENERATED_SEGMENTS for seg in path.split("/")[:-1])


def generated_by_declaration(text):
    """One of the first ten lines matches auto-?generated|do not edit."""
    return any(_DECLARES.search(ln) for ln in text.splitlines()[:10])


def stratum_of(path):
    p = path.lower()
    if p.endswith((".mmd", ".mermaid")):
        return "F"
    if p.endswith(".md"):
        return "D"
    return None
