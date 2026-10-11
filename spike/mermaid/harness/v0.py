#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION.md §11.2 V0: the renderer.

    python3 -I -S -B harness/v0.py [--no-install]

R installs from the committed lockfile with `npm ci --ignore-scripts` (the
only step that uses the network), then every R call runs with the network
off, under Node v24.20.0, with §4.4's configuration and the jsdom globals set
before Mermaid is imported. On planted texts it shows each behaviour Appendix
A relies on, as census/v0-probes.out recorded it. Exit 1 if any check fails;
exit 3 if R cannot run this way, which §11.2 says stops the work.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ms import flowlex as FL  # noqa: E402
from ms import model as MD  # noqa: E402
from ms import rbridge as RB  # noqa: E402
from ms import subset as SS  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def one(text, **env):
    if env:
        env = dict(env, SPIKE_R_TEST="1")
    return RB.run_one(text, env)


def V(o, vid):
    return next((v for v in o.get("vertices", []) if v["id"] == vid), None)


def main():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--no-install", action="store_true")
    a = ap.parse_args()
    print("== install")
    if not a.no_install:
        r = subprocess.run(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=RB.R_DIR,
                           capture_output=True, text=True)
        check("npm ci --ignore-scripts installs from the committed lockfile", r.returncode == 0, r.stderr[-300:])
    lock = os.path.join(RB.R_DIR, "package-lock.json")
    print(f"  lockfile sha256 {hashlib.sha256(open(lock, 'rb').read()).hexdigest()}")
    lk = json.load(open(lock))
    check("the lockfile pins mermaid 12.1.0 and jsdom 26.1.0 with integrity hashes",
          lk["packages"]["node_modules/mermaid"]["version"] == "12.1.0" and
          lk["packages"]["node_modules/jsdom"]["version"] == "26.1.0" and
          all(p.get("integrity") for k, p in lk["packages"].items() if k))
    try:
        n = RB.check_install()
        check(f"every one of the lockfile's {n} packages is installed at its version", True)
        node = RB.node_bin()
    except RB.Broken as e:
        print(f"R cannot run: {e}")
        return 3
    print(f"  node {subprocess.run([node, '--version'], capture_output=True, text=True).stdout.strip()}")
    chunk = os.path.join(RB.R_DIR, "node_modules", "mermaid", "dist", "chunks", "mermaid.core", "chunk-EU5HNXII.mjs")
    got = hashlib.sha256(open(chunk, "rb").read()).hexdigest() if os.path.exists(chunk) else None
    check("H's lexer table (ms/flowlex.py) was transcribed from the installed flowchart lexer", got == FL.LEXER_SHA256)
    net = subprocess.run(RB.offline(["cat", "/proc/net/dev"]), capture_output=True, text=True)
    ifaces = [ln.split(":")[0].strip() for ln in net.stdout.splitlines()[2:]]
    check("R's calls run with the network off: only the loopback interface exists", ifaces == ["lo"], ifaces)
    rc, o = one("flowchart TD\n  A[Alpha] --> B\n")
    check("a labelled chart parses with the jsdom globals set", o.get("parse") is True, o)
    print("== configuration (§4.4)")
    rc, o = one("flowchart TD\n  A[Alpha] --> B\n")
    cfg = o.get("config", {})
    check("mermaid.initialize gets §4.4's configuration", cfg.get("securityLevel") == "strict" and
          cfg.get("maxEdges") == 100000 and cfg.get("flowchart") == {"htmlLabels": False} and
          cfg.get("startOnLoad") is False and cfg.get("jsdom") is True, cfg)
    check("versions: mermaid 12.1.0 under node v24.20.0", cfg.get("versions") == {"node": "v24.20.0",
                                                                                  "mermaid": "12.1.0"}, cfg)
    src = open(RB.WRAPPER).read()
    i_doc, i_imp = src.find("globalThis.document = dom.window.document"), src.find("await import('mermaid')")
    check("the wrapper sets globalThis.window and document before it imports mermaid", 0 <= i_doc < i_imp)
    check("the wrapper never passes suppressErrors", "suppressErrors" not in src.replace(
        "// - mermaid.parse(text) is called without suppressErrors", ""))

    print("== behaviours Appendix A relies on")
    rc, o = one("flowchart TD\n  A[Alpha] --> Ghost\n")
    g = V(o, "Ghost")
    check("an edge to an undeclared id creates that node, its id as label, no shape (probe implicit)",
          g and g["text"] == "Ghost" and g["type"] is None)
    rc, o = one("flowchart TD\n  A[First] --> B\n  A(Second)\n")
    check("a node declared twice keeps the last label and the last shape (twice, twiceShape)",
          V(o, "A")["text"] == "Second" and V(o, "A")["type"] == "round")
    for name, t, want in (("twoSub", "flowchart TD\n subgraph s1\n X\n end\n subgraph s2\n X\n end\n", "s1"),
                          ("twoSubRev", "flowchart TD\n subgraph s2\n X\n end\n subgraph s1\n X\n end\n", "s2"),
                          ("twoSubNested", "flowchart TD\n subgraph s1\n subgraph s2\n X\n end\n X\n end\n", "s2")):
        rc, o = one(t)
        holder = next(s["id"] for s in o["subgraphs"] if "X" in s["nodes"])
        check(f"a node in two subgraphs belongs to the first to close ({name})", holder == want, o["subgraphs"])
    rc, o = one("flowchart LR\n  A e1@--> B\n  e1[Node]\n")
    check("an edge id e1 used before a node statement e1[...] swallows the node (edgeIdThenNode)",
          V(o, "e1") is None and o["edges"][0]["id"] == "e1")
    rc, o = one("flowchart LR\n  e1[Node e1]\n  A e1@--> B\n")
    check("a node e1 declared first coexists with an edge id e1 (nodeEqEdgeId)",
          V(o, "e1") and V(o, "e1")["text"] == "Node e1" and o["edges"][0]["isUserDefinedId"])
    rc, o = one("flowchart LR\n  A e1@--> B\n  C e1@--> D\n")
    check("a duplicate user-defined edge id falls back to an automatic id (dupEdgeId)",
          [e["isUserDefinedId"] for e in o["edges"]] == [True, False] and o["edges"][1]["id"] != "e1")
    rc, o = one("flowchart TD\n  subgraph S\n    Q\n  end\n  A --> S\n")
    check("an edge to a subgraph's id creates a vertex with that id and no shape (edgeToSub)",
          V(o, "S") and V(o, "S")["type"] is None)
    rc, o3 = one("flowchart TD\n  subgraph Front End\n    A\n  end\n  subgraph Back End\n    B\n  end\n")
    rc, o4 = one("flowchart TD\n  subgraph New Group\n    C\n  end\n  subgraph Front End\n    A\n  end\n"
                 "  subgraph Back End\n    B\n  end\n")
    check("untitled subgraphs get subGraphN by position, and renumber when one is inserted earlier (probe3)",
          [(s["id"], s["title"]) for s in o3["subgraphs"]] == [("subGraph0", "Front End"), ("subGraph1", "Back End")]
          and [(s["id"], s["title"]) for s in o4["subgraphs"]][1] == ("subGraph1", "Front End"))
    check("keyed by title, the renumbering changes no key", {k for k in MD.from_r(o3) if k[0] == "stitle"} <=
          {k for k in MD.from_r(o4) if k[0] == "stitle"})
    rc, o = one("flowchart TD\n  A -->|hi &amp; there| B\n")
    check("edge text is not entity-decoded (labelEdge)", o["edges"][0]["text"] == "hi &amp; there", o["edges"][0])
    rc, o = one('flowchart TD\n  A[Alpha]\n  click A "https://example.com" _blank\n')
    check("a click URL is normalized and adds the class clickable (probe2 click)",
          V(o, "A")["link"] == "https://example.com/" and "clickable" in V(o, "A")["classes"])
    big = "flowchart TD\n" + "".join(f"  n{i} --> n{i + 1}\n" for i in range(600))
    rc, o = one(big)
    check("a chart of 600 edges parses under §4.4's maxEdges", o.get("parse") and len(o["edges"]) == 600)
    rc, o = one(big, DEFAULT_EDGES="1")
    check("... and fails under the default, without hash, the canary parsing (Edge limit exceeded)",
          o.get("parse") is False and o.get("hash") is False and o.get("canary") == "ok" and
          "Edge limit exceeded. 500 edges found, but the limit is 500." in o.get("msg", ""), o)
    rc, o = one("flowchart TD\n  A -->\n")
    check("a syntax error throws an error with hash: the text does not parse", o.get("parse") is False and
          o.get("hash") is True)
    for name, t, cls, msg in (
            ("linkStyle out of range", "flowchart TD\n  A --> B\n  linkStyle 5 stroke:#f00\n", "TypeError",
             "Cannot set properties of undefined (setting 'style')"),
            ("an unknown shape", 'flowchart TD\n  A@{ shape: notashape, label: "x" }\n', "Error",
             "No such shape: notashape."),
            ("a Flowchart TD header", "Flowchart TD\n  A --> B\n", "UnknownDiagramError", "No diagram type detected"),
            ("a GRAPH TD header", "GRAPH TD\n  A --> B\n", "UnknownDiagramError", "No diagram type detected")):
        rc, o = one(t)
        check(f"without hash, canary parses, text does not parse: {name}", o.get("parse") is False and
              o.get("hash") is False and o.get("canary") == "ok" and o.get("cls") == cls and msg in o.get("msg", ""),
              o)
    rc, o = one("flowchart TD\n  A[Alpha] --> B\n", NO_JSDOM="1")
    check("a labelled chart without the jsdom globals: TypeError without hash, the canary fails, R exits non-zero",
          rc == 3 and o.get("abort") is True and o.get("cls") == "TypeError", (rc, o))
    rc, o = one("flowchart TD\n  A[Alpha] --> B\n", NO_JSDOM="1")
    rc2, o2 = RB.run_one("flowchart TD\n  A[Alpha] --> B\n", {"NO_JSDOM": "1"})
    check("the test seams are refused without SPIKE_R_TEST=1", rc2 == 3 and o2.get("cls") == "Usage", o2)
    t = "flowchart TD\n  A e1@--> B\n  e1 --> C\n"
    rc, o = one(t)
    check("an edge end naming an earlier edge id yields start e1 with no vertex e1 (edgeFromEdgeIdNode)",
          V(o, "e1") is None and any(e["start"] == "e1" for e in o["edges"]))
    check("... and H refuses it", SS.classify(t, RB.run_one(t)[1]).status != "in")
    t = "flowchart TD\n  subgraph T\n    A\n  end\n  subgraph Other Box\n    B\n  end\n  subgraph subGraph1 [X]\n    C\n  end\n"
    rc, o = one(t)
    check("an explicit subgraph subGraphN after an untitled one merges into R's numbered subgraph",
          len(o["subgraphs"]) == 2 and "C" in next(s["nodes"] for s in o["subgraphs"] if s["id"] == "subGraph1"), o["subgraphs"])
    check("... and H refuses it", SS.classify(t, RB.run_one(t)[1]).status != "in")

    print("== batch mode")
    texts = ["%%{init: {\"flowchart\": {\"htmlLabels\": true}}}%%\nflowchart TD\n  A[a <b>x</b>] --> B\n",
             "flowchart TD\n  A[a <b>x</b>] --> B\n", "flowchart TD\n  A -->\n", "graph LR\n  x --> y\n"]
    cfg, res = RB.run_batch(texts)
    singles = [RB.run_one(t)[1] for t in texts]
    for s in singles:
        s.pop("config", None)
    for r in res:
        r.pop("id", None)
    check("batch mode gives single-shot mode's result for every text, a directive's config not carried over",
          res == singles, [(a == b) for a, b in zip(res, singles)])
    print(f"\n{'V0: PASS' if not FAILS else f'V0: FAIL ({len(FAILS)} failed)'}")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
