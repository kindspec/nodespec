#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""The mutation gate: each mutant below breaks the checker by one token, and
some test under tests/ must fail on it.

For each mutant the gate checks that its text occurs exactly once in the file,
applies it, and hashes the file before and after: an unchanged hash is BROKEN,
never a pass, because a mutant that did not apply is otherwise
indistinguishable from one the tests survived. It clears __pycache__, runs the
tests with PYTHONDONTWRITEBYTECODE=1, and restores the file, checking its hash
against the original.

A mutant listed in EQUIVALENT is one no input can tell from the original; it
is still applied and run, and the tests killing it is a failure too, since the
claim is then false.

Exit 0 when every mutant is killed (and every equivalent one survives), 1 when
any survives or is BROKEN, 2 when the unmutated tests do not pass, which is no
verdict.
"""

import hashlib
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER = "reference/nodespec/checker.py"
GRAMMAR = "reference/nodespec/grammar.py"
RUNNER = "conformance/run_cases.py"

# (name, file, old, new). Each changes one token.
MUTANTS = [
    # --- §3 ----------------------------------------------------------------
    ("lone-cr-means-crlf", CHECKER, r'rb"\r(?!\n)"', r'rb"\r(?=\n)"'),
    ("bad-encoding-does-not-stop", CHECKER, "return None, out, True", "return None, out, False"),
    ("bom-kept-in-the-first-line", CHECKER, "text = text[1:]", "text = text[0:]"),
    ("crlf-strips-two", CHECKER, 'ln[:-1] if ln.endswith("\\r")', 'ln[:-2] if ln.endswith("\\r")'),
    ("drops-the-first-line-when-empty", CHECKER, 'if lines[-1] == "":', 'if lines[0] == "":'),
    ("keeps-the-final-empty-line", CHECKER, "        lines.pop()\n", "        pass\n"),
    # --- §4.2 --------------------------------------------------------------
    (
        "front-matter-fence-wsp-is-space",
        CHECKER,
        'if lines and lines[0].strip(g.WSP_CHARS) == "---":',
        'if lines and lines[0].strip(" ") == "---":',
    ),
    ("front-matter-excludes-its-close", CHECKER, "front = j + 1", "front = j"),
    ("unclosed-front-matter-is-one-line", CHECKER, "front = len(lines)", "front = 1"),
    ("conflict-marker-of-six", CHECKER, "if line[:7] in", "if line[:6] in"),
    ("conflict-marker-no-pipes", CHECKER, '"|" * 7', '"|" * 8'),
    ("directive-needs-brace", CHECKER, 'if "%%{" in line:', 'if "%%{{" in line:'),
    ("comment-may-hold-eq-quote", GRAMMAR, "'=\"' not in line", "'==\"' not in line"),
    ("comment-may-hold-eq", GRAMMAR, "'=\"' not in line", "'=' not in line"),
    ("comment-may-start-with-brace", GRAMMAR, r"\x20-\x7a\x7c-\x7e", r"\x20-\x7a\x7b-\x7e"),
    ("comment-may-hold-del", GRAMMAR, r'_CCHAR = r"[\t\x20-\x7e"', r'_CCHAR = r"[\t\x20-\x7f"'),
    # --- §4.3 --------------------------------------------------------------
    (
        "every-line-is-the-header-place",
        CHECKER,
        "            header_seen = True\n",
        "            header_seen = False\n",
    ),
    ("header-without-td", GRAMMAR, '_DIR = r"(?:TB|TD|BT|LR|RL)"', '_DIR = r"(?:TB|BT|LR|RL)"'),
    (
        "first-word-splits-on-space-only",
        CHECKER,
        "        if c in g.WSP_CHARS:",
        '        if c in " ":',
    ),
    (
        "nested-subgraph-at-top-level",
        CHECKER,
        '        if block is not None:\n            return None, ("nested-block"',
        '        if block is None:\n            return None, ("nested-block"',
    ),
    (
        "end-does-not-close",
        CHECKER,
        '        elif st.kind == "end":\n            block = None',
        '        elif st.kind == "end":\n            block = block',
    ),
    (
        "eof-block-is-balanced",
        CHECKER,
        '    if block is not None:\n        refuse("unbalanced',
        '    if block is None:\n        refuse("unbalanced',
    ),
    ("accdescr-brace-admitted", CHECKER, r"accDescr[ \t]*[:{])", r"accDescr[ \t]*[:])"),
    ("click-admitted", CHECKER, 'if fw == "click" or', 'if fw == "clicks" or'),
    ("markdown-string-malformed", CHECKER, "or '\"`' in line:", "or '\"``' in line:"),
    ("triple-colon-malformed", CHECKER, 'if ":::" in line or', 'if "::::" in line or'),
    # --- §4.4 --------------------------------------------------------------
    (
        "hasownproperty-not-reserved",
        CHECKER,
        '"hasOwnProperty", "direction"}',
        '"hasOwnproperty", "direction"}',
    ),
    (
        "direction-not-reserved",
        CHECKER,
        '"hasOwnProperty", "direction"}',
        '"hasOwnProperty", "Direction"}',
    ),
    ("L-form-without-digits", CHECKER, r'_[A-Za-z0-9_]+_[0-9]+")', r'_[A-Za-z0-9_]+_[0-9]*")'),
    ("keyword-_top-not-reserved", GRAMMAR, "_blank _parent _top", "_blank _parent _topx"),
    ("classdef-node-allowed", CHECKER, 'st.decls[0][0] == "node"', 'st.decls[0][0] == "nodes"'),
    (
        "class-target-node-reserved",
        CHECKER,
        'st.names[-1][0] == "node"',
        'st.names[0][0] == "node"',
    ),
    (
        "reserved-line-contributes",
        CHECKER,
        '                refuse("reserved-id", f"`{x}` is reserved and cannot be an id here", x)\n'
        "            continue\n",
        '                refuse("reserved-id", f"`{x}` is reserved and cannot be an id here", x)\n'
        "            pass\n",
    ),
    (
        "stray-line-contributes",
        CHECKER,
        "        if stray:\n            continue\n",
        "        if False:\n            continue\n",
    ),
    # --- §4.5 --------------------------------------------------------------
    ("label-without-backslash", GRAMMAR, r"\x41-\x5a\x5c\x5e-\x7a\x7e", r"\x41-\x5a\x5e-\x7a\x7e"),
    ("label-may-lead-with-hyphen", GRAMMAR, r"\x2a-\x2c\x2e\x30", r"\x2a-\x2e\x30"),
    (
        "quoted-without-hash",
        GRAMMAR,
        r'_QCHAR = r"[\t\x20\x21\x23-\x7e"',
        r'_QCHAR = r"[\t\x20\x21\x24-\x7e"',
    ),
    (
        "quoted-may-be-blank",
        GRAMMAR,
        "any(c not in WSP_CHARS for c in text)",
        "any(c in WSP_CHARS for c in text)",
    ),
    ("quoted-backtick-at-end", GRAMMAR, 'not text.startswith("`")', 'not text.endswith("`")'),
    ("quoted-eq-at-start", GRAMMAR, 'not text.endswith("=")', 'not text.startswith("=")'),
    ("unquoted-double-tilde", GRAMMAR, 'return "~~~" not in label', 'return "~~" not in label'),
    ("odd-shape-closes-with-paren", GRAMMAR, '(">", "]", "odd")', '(">", ")", "odd")'),
    (
        "node-stmt-ignores-the-rest",
        GRAMMAR,
        "if not sh or not _TRAIL.fullmatch(line, sh[0]):",
        "if not sh or not _TRAIL.match(line, sh[0]):",
    ),
    # --- §4.6 --------------------------------------------------------------
    ("link-of-two-dashes", GRAMMAR, r"|-{3,}|", r"|-{2,}|"),
    ("link-short-both-heads", GRAMMAR, r"|<-{2,}>|", r"|<-{1,}>|"),
    ("link-of-two-tildes", GRAMMAR, r"|~{3,})", r"|~{2,})"),
    ("link-of-two-equals", GRAMMAR, r"|={3,}|", r"|={2,}|"),
    ("link-needs-pipe-after", GRAMMAR, r'r")(?=[| \t])")', r'r")(?=[|])")'),
    (
        "amp-without-space-before",
        GRAMMAR,
        r'_AMP = re.compile(r"[ \t]+&',
        r'_AMP = re.compile(r"[ \t]*&',
    ),
    ("edge-label-unchecked", GRAMMAR, "if not label_ok(lm.group(1)):", "if label_ok(lm.group(1)):"),
    ("edge-id-group-before-allowed", CHECKER, "(len(grps[k]) > 1 or", "(len(grps[k]) > 2 or"),
    ("edge-id-group-after-allowed", CHECKER, "len(grps[k + 1]) > 1)", "len(grps[k + 1]) > 2)"),
    (
        "edge-id-on-group-contributes",
        CHECKER,
        "                        eid,\n                    )\n                continue\n",
        "                        eid,\n                    )\n                pass\n",
    ),
    (
        "duplicate-edge-counts-named",
        CHECKER,
        "        if eid is None:",
        "        if eid is not None:",
    ),
    ("duplicate-edge-of-three", CHECKER, "        if n > 1:", "        if n > 2:"),
    ("duplicate-edge-ignores-link", CHECKER, "key = (a, b, link, label)", "key = (a, b, a, label)"),
    (
        "duplicate-edge-ignores-end",
        CHECKER,
        "key = (a, b, link, label)",
        "key = (a, a, link, label)",
    ),
    ("duplicate-edge-ignores-label", CHECKER, "key = (a, b, link, label)", "key = (a, b, link, a)"),
    (
        "duplicate-edge-label-strips-spaces",
        CHECKER,
        "ln.label.strip(g.WSP_CHARS)",
        'ln.label.strip(" ")',
    ),
    ("too-many-at-500", CHECKER, "if len(edges) > MAX_EDGES:", "if len(edges) >= MAX_EDGES:"),
    ("limit-501", CHECKER, "MAX_EDGES = 500", "MAX_EDGES = 501"),
    # --- §4.7 --------------------------------------------------------------
    ("subgraph-alone-is-malformed", GRAMMAR, 'if text == "" or', 'if text == " " or'),
    ("subgraph-quote-is-apostrophe", GRAMMAR, "text.startswith('\"')", 'text.startswith("\'")'),
    (
        "subgraph-wsp-anywhere",
        GRAMMAR,
        "before = text if bracket < 0 else",
        "before = text if bracket > 0 else",
    ),
    # --- §4.8 --------------------------------------------------------------
    ("style-prop-accdescr", GRAMMAR, '("accTitle", "accDescr")', '("accTitle", "accTitle")'),
    ("style-name-keyword-whole-only", GRAMMAR, "or head in KEYWORDS:", "or name in KEYWORDS:"),
    ("style-name-v-hyphen", GRAMMAR, 'or head == "v" or', 'or head == "w" or'),
    (
        "style-swimlane-beta-prefix",
        GRAMMAR,
        'name.startswith("swimlane-beta-")',
        'name.startswith("swimlane-beta--")',
    ),
    ("style-unit-v", GRAMMAR, 'return m.group(1) != "v"', 'return m.group(1) != "w"'),
    ("style-number-unsigned", GRAMMAR, r'r"(?:-?[0-9]+', r'r"(?:[0-9]+'),
    (
        "style-words-split-on-tabs",
        GRAMMAR,
        '_SPACES = re.compile(" +")',
        '_SPACES = re.compile("[ \\t]+")',
    ),
    ("style-value-strips-both-ends", GRAMMAR, 'value.lstrip(" ")', 'value.strip(" ")'),
    # --- §4.9 --------------------------------------------------------------
    ("stray-without-td", CHECKER, '"]+(?:TB|BT|RL|LR|TD)"', '"]+(?:TB|BT|RL|LR)"'),
    ("stray-starts-not-ends", CHECKER, '.endswith("direction")', '.startswith("direction")'),
    ("stray-trailing-wsp-only", CHECKER, "line.rstrip(_MWS)", "line.rstrip(g.WSP_CHARS)"),
    (
        "stray-comments-not-exempt",
        CHECKER,
        "and not g.is_comment(line)\n",
        "and not g.is_blank(line)\n",
    ),
    (
        "stray-direction-stmt-not-exempt",
        CHECKER,
        "and not g.is_direction_stmt(line)\n",
        "and not g.is_end_line(line)\n",
    ),
    ("direction-flag-not-set", CHECKER, "block.direction = True", "block.direction = False"),
    # --- §5 ----------------------------------------------------------------
    (
        "duplicate-declaration-of-three",
        CHECKER,
        "if kinds.count(kind) > 1:",
        "if kinds.count(kind) > 2:",
    ),
    ("kind-clash-of-three", CHECKER, "if len(set(kinds)) > 1:", "if len(set(kinds)) > 2:"),
    (
        "undeclared-inverted",
        CHECKER,
        "            if i not in decls:",
        "            if i in decls:",
    ),
    (
        "wrong-kind-union",
        CHECKER,
        "elif not set(decls[i]) & allowed:",
        "elif not set(decls[i]) | allowed:",
    ),
    (
        "class-target-may-be-class",
        CHECKER,
        "_CLASS_TARGET = frozenset({NODE, SUBGRAPH, EDGE})",
        "_CLASS_TARGET = frozenset({NODE, SUBGRAPH, CLASS})",
    ),
    (
        "style-may-name-an-edge",
        CHECKER,
        '(sid, _NODE_OR_SUBGRAPH, "a style line")',
        '(sid, _CLASS_TARGET, "a style line")',
    ),
    # --- §6 ----------------------------------------------------------------
    ("member-twice-of-three", CHECKER, "if members[i] > 1:", "if members[i] > 2:"),
    ("cycle-test-inverted", CHECKER, "if x == start:", "if x != start:"),
    ("cycle-of-one-only", CHECKER, "stack.extend(holds.get(x, ()))", "stack.extend(())"),
    # --- §7 ----------------------------------------------------------------
    (
        "class-not-last-inverted",
        CHECKER,
        'if st.kind == "class" and i < last_other:',
        'if st.kind == "class" and i > last_other:',
    ),
    (
        "class-not-last-skips-style",
        CHECKER,
        'if st.kind != "class"), default=-1)',
        'if st.kind != "style"), default=-1)',
    ),
    ("styled-twice-of-three", CHECKER, "if count[t] > 1:", "if count[t] > 2:"),
    (
        "styled-twice-counts-mentions",
        CHECKER,
        "for t in set(st.targets):",
        "for t in list(st.targets):",
    ),
    (
        "styled-twice-style-only",
        CHECKER,
        'for kind in ("style", "class"):',
        'for kind in ("style", "style"):',
    ),
    # --- readings settled after draft 0's first text (e7e643e) ---------------
    (
        "front-matter-not-exempt-from-stray",
        CHECKER,
        "            i >= front\n",
        "            i >= 0\n",
    ),
    (
        "stray-word-any-case",
        CHECKER,
        '_STRAY = re.compile("direction["',
        '_STRAY = re.compile("[dD]irection["',
    ),
    ("stray-direction-lower-case", CHECKER, '"]+(?:TB|BT|RL|LR|TD)"', '"]+(?:TB|BT|RL|LR|TD|lr)"'),
    ("L-form-without-underscores", CHECKER, r'_[A-Za-z0-9_]+_[0-9]+")', r'_[A-Za-z0-9]+_[0-9]+")'),
    ("subgraph-skips-one-wsp", GRAMMAR, '"*subgraph" + _WSP + "*")', '"*subgraph" + _WSP + "?")'),
    # --- the case runner ---------------------------------------------------
    (
        "runner-ignores-the-identifier",
        RUNNER,
        "if f.identifier not in allowed:",
        "if f.identifier in allowed:",
    ),
    (
        "runner-ignores-the-id",
        RUNNER,
        "and f.id not in ids[f.identifier]:",
        "and f.id in ids[f.identifier]:",
    ),
    (
        "runner-passes-an-accepted-refusal",
        RUNNER,
        'return ["expected a refusal, got accept"]',
        "return []",
    ),
    (
        "runner-no-tree-is-a-pass",
        RUNNER,
        "        return 2\n    if failed:",
        "        return 0\n    if failed:",
    ),
]

EQUIVALENT = {
    "keeps-the-final-empty-line": (
        "the empty text after a final line end is then read as one more line, which is "
        "blank; a blank line is allowed anywhere and contributes nothing, and front matter "
        "that is never closed runs to the end of the file either way"
    ),
}


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def clear_pycache():
    for top in ("reference", "tests", "conformance"):
        for dirpath, dirnames, _ in os.walk(os.path.join(ROOT, top)):
            if "__pycache__" in dirnames:
                shutil.rmtree(os.path.join(dirpath, "__pycache__"))
                dirnames.remove("__pycache__")


def run_tests():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    cmd = [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", "tests"]
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True).returncode


def main():
    names = [m[0] for m in MUTANTS]
    if len(names) != len(set(names)):
        print("BROKEN: two mutants share a name")
        return 1
    orphans = sorted(set(EQUIVALENT) - set(names))
    if orphans:
        print(f"BROKEN: EQUIVALENT names mutants that do not exist: {', '.join(orphans)}")
        return 1
    clear_pycache()
    if run_tests() != 0:
        print("the tests fail on the unmutated checker: no verdict")
        return 2
    problems = 0
    for name, rel, old, new in MUTANTS:
        path = os.path.join(ROOT, rel)
        with open(path, "rb") as fh:
            original = fh.read()
        before = sha(path)
        text = original.decode("utf-8")
        n = text.count(old)
        if n != 1:
            print(f"BROKEN {name}: its text occurs {n} times in {rel}, not once")
            problems += 1
            continue
        mutated = text.replace(old, new)
        try:
            compile(mutated, path, "exec")
        except SyntaxError as e:
            print(f"BROKEN {name}: the mutated {rel} does not compile: {e.msg}")
            problems += 1
            continue
        try:
            with open(path, "wb") as fh:
                fh.write(mutated.encode("utf-8"))
            if sha(path) == before:
                print(f"BROKEN {name}: {rel} is unchanged after applying it")
                problems += 1
                continue
            clear_pycache()
            rc = run_tests()
        finally:
            with open(path, "wb") as fh:
                fh.write(original)
            clear_pycache()
        if sha(path) != before:
            print(f"BROKEN: {rel} was not restored after {name}")
            return 1
        if rc not in (0, 1):
            print(f"BROKEN {name}: the tests ended with exit {rc}, which is no verdict")
            problems += 1
        elif name in EQUIVALENT:
            if rc == 1:
                print(f"FALSE EQUIVALENCE {name}: a test kills it")
                problems += 1
            else:
                print(f"equivalent {name}")
        elif rc == 0:
            print(f"SURVIVED {name}")
            problems += 1
        else:
            print(f"killed {name}")
    total = len(MUTANTS)
    print(f"{total} mutant(s), {len(EQUIVALENT)} equivalent, {problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
