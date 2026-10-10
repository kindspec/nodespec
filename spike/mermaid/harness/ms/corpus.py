# SPDX-License-Identifier: MIT
"""§7: the corpora, their private identities, their archive, and redaction.

The public table is census/corpora-public.tsv, pinned by its sha256 (§7.1).
Individually owned corpora are named there only as u:<12 hex> with their pin
as h:<16 hex>. Their real names and pins come from two private files the
owner holds, passed by path and never committed:

  --private-map    "# salt<TAB><salt>" and rows "u:<label><TAB><owner/name>"
  --private-table  the private corpora table: the public table's columns,
                   with real names and pins

Every label and hashed pin is recomputed from them and must match the public
table, so a wrong or stale private file is refused, not used.
"""
import csv
import hashlib
import json
import os
import re
import subprocess

from . import gitops as G
from .transcript import SPIKE

PUBLIC = os.path.join(SPIKE, "census", "corpora-public.tsv")
PUBLIC_SHA256 = "2bc5e099c71f231cd5c4c9e3430038660af616e13182082f1e63cfdc9caaf22f"


class NoVerdict(Exception):
    """§7.6: a corpus that cannot be read as pinned is NO VERDICT."""


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u_label(salt, name):
    return "u:" + hashlib.sha256((salt + ":" + name).encode()).hexdigest()[:12]


def h_pin(salt, pin):
    return "h:" + hashlib.sha256((salt + ":pin:" + pin).encode()).hexdigest()[:16]


def h_commit(salt, sha):
    """R-redact-commit: a commit of an individually owned corpus is published
    as h: + 16 hex of sha256(salt + ":commit:" + sha), by analogy with §7.1's
    pin rule, which names no form for other commits."""
    return "h:" + hashlib.sha256((salt + ":commit:" + sha).encode()).hexdigest()[:16]


def h_value(v):
    """§7.3: a read-only corpus's id, label, title or path segment."""
    return "h:" + hashlib.sha256(v.encode()).hexdigest()[:16]


def load_public(path=PUBLIC, want_sha=PUBLIC_SHA256):
    if sha256_file(path) != want_sha:
        raise SystemExit(f"refusing: {path} does not have §7.1's sha256")
    rows = list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))
    return [r for r in rows if r["status"] in ("in", "read-only")]


def load_private(map_path, table_path, public):
    """{public label: {"name", "pin"}} for every u: row, checked against the
    public table. Org rows map to themselves."""
    salt, labels = None, {}
    for line in open(map_path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if f[0] == "# salt":
            salt = f[1]
        elif f[0].startswith("u:") and len(f) == 2:
            labels[f[0]] = f[1]
    if not salt:
        raise SystemExit("refusing: the private map holds no salt")
    priv = {(r["stratum"], r["corpus"]): r for r in csv.DictReader(open(table_path, encoding="utf-8"),
                                                                    delimiter="\t")}
    out = {}
    for r in public:
        lab = r["corpus"]
        if not lab.startswith("u:"):
            out[(r["stratum"], lab)] = {"name": lab, "pin": r["pin"], "individual": False}
            continue
        name = labels.get(lab)
        if name is None or u_label(salt, name) != lab:
            raise SystemExit(f"refusing: the private map does not resolve {lab}")
        pr = priv.get((r["stratum"], name))
        if pr is None or h_pin(salt, pr["pin"]) != r["pin"]:
            raise SystemExit(f"refusing: the private table's pin for {lab} does not hash to the public one")
        out[(r["stratum"], lab)] = {"name": name, "pin": pr["pin"], "individual": True}
    return salt, out


# ------------------------------------------------------------------ archive

def bundles(spike=SPIKE):
    """§7.6: each bundle's and pull-request list's sha256, as the validation
    commit's results/VALIDATION records them (R-bundles). Empty before
    validation, and whenever the derivation reports a reason, so a bound arm
    then makes every corpus NO VERDICT."""
    from . import binding as BD
    _, v, rs = BD.derive(spike)
    return v["bundles"] if v and not rs else {}


def open_corpus(label, bundle_dir, work_dir, pin, want=None):
    """Clone the corpus's bundle into work_dir/<hash of label>, after checking
    its sha256 against VALIDATION's record. A pin absent from the bundle is NO
    VERDICT (§7.6)."""
    want = want or bundles().get(label)
    if not want:
        raise NoVerdict(f"no archived bundle recorded for {label}")
    b = os.path.join(bundle_dir, want["file"])
    if not os.path.isfile(b) or sha256_file(b) != want["sha256"]:
        raise NoVerdict(f"the bundle for {label} is missing or its sha256 differs")
    dest = os.path.join(work_dir, hashlib.sha256(label.encode()).hexdigest()[:16] + ".git")
    if os.path.exists(dest):
        raise SystemExit(f"refusing: {dest} exists; every run starts from a fresh clone of the bundle")
    e = G.env(os.devnull)
    r = subprocess.run(["git", "clone", "-q", "--mirror", b, dest], capture_output=True, env=e)
    if r.returncode != 0:
        raise NoVerdict(f"the bundle for {label} does not clone")
    if subprocess.run(["git", "-C", dest, "cat-file", "-e", pin + "^{commit}"], env=e,
                      capture_output=True).returncode != 0:
        raise NoVerdict(f"the pin of {label} is absent from its bundle")
    return dest


def fetch_pr_list(repo_name, api):
    """§7.6 and §8.2: every merged pull request (number, head sha, merge
    commit sha, commit count, and the commit list read across every page).
    api(path) -> parsed JSON page; injectable so V3 can plant one."""
    out, page = [], 1
    while True:
        prs = api(f"repos/{repo_name}/pulls?state=closed&per_page=100&page={page}")
        if not prs:
            break
        for p in prs:
            if not p.get("merged_at"):
                continue
            commits, cp = [], 1
            while True:
                cs = api(f"repos/{repo_name}/pulls/{p['number']}/commits?per_page=100&page={cp}")
                if not cs:
                    break
                commits += [c["sha"] for c in cs]
                if len(cs) < 100:
                    break
                cp += 1
            out.append({"number": p["number"], "head": p["head"]["sha"], "merge": p["merge_commit_sha"],
                        "commit_count": p.get("commits", len(commits)), "commits": commits})
        if len(prs) < 100:
            break
        page += 1
    return out


def gh_api(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh api {path}: {r.stderr.strip()[:200]}")
    return json.loads(r.stdout)


class ArchiveFailed(Exception):
    """An archive step failed. Its message never names the corpus: a
    corpus may belong to a private individual (H6)."""


def archive(name, label, out_dir, api=gh_api, url=None):
    """Fetch a corpus (name: owner/name) with its refs/pull/*/head refs,
    bundle it, and save its merged pull-request list under file names derived
    from its public label. Returns {"file", "sha256", "prs_file",
    "prs_sha256"}. Run by the owner before validation; never by a bound arm.
    Every subprocess's output is captured, and a failure is re-raised with
    the corpus's name and URL removed."""
    os.makedirs(out_dir, exist_ok=True)
    # The files are named from the corpus's public label, never its name:
    # their names are committed in VALIDATION (R-bundles), and a hash of the
    # name alone would let anyone link a u: label to its repository.
    tag = hashlib.sha256(label.encode()).hexdigest()[:16]
    mirror = os.path.join(out_dir, tag + ".mirror.git")
    e = G.env(os.devnull)
    url = url or f"https://github.com/{name}.git"

    def scrub(x):
        return str(x).replace(url, "<url>").replace(name, "<corpus>").replace(name.split("/")[0], "<owner>")

    def run(argv, check=True):
        r = subprocess.run(argv, capture_output=True, env=e)
        if check and r.returncode != 0:
            raise ArchiveFailed(f"{scrub(' '.join(argv[:3]))}: exit {r.returncode}: "
                                f"{scrub(r.stderr.decode('utf-8', 'replace').strip()[-300:])}")
        return r
    try:
        run(["git", "clone", "-q", "--mirror", url, mirror])
        run(["git", "-C", mirror, "fetch", "-q", "origin", "+refs/pull/*/head:refs/pull/*/head"], check=False)
        bundle = os.path.join(out_dir, tag + ".bundle")
        run(["git", "-C", mirror, "bundle", "create", "-q", bundle, "--all"])
        prs = fetch_pr_list(name, api)
    except ArchiveFailed:
        raise
    except Exception as x:  # noqa: BLE001 -- any failure is reported scrubbed
        raise ArchiveFailed(f"{x.__class__.__name__}: {scrub(x)}") from None
    pf = os.path.join(out_dir, tag + ".prs.json")
    with open(pf, "w") as f:
        f.write(json.dumps(prs, sort_keys=True, indent=1) + "\n")
    return {"file": os.path.basename(bundle), "sha256": sha256_file(bundle), "prs_file": os.path.basename(pf),
            "prs_sha256": sha256_file(pf)}


# ---------------------------------------------------------------- redaction

HEXTOK = re.compile(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])")


def redaction_hits(text, forbidden_names, forbidden_shas):
    """Every planted name (full name or owner part), and every hex token of 7
    to 40 characters that is a prefix of a forbidden commit, in text."""
    hits = []
    low = text.lower()
    for n in forbidden_names:
        for part in {n, n.split("/")[0]}:
            if part and part.lower() in low:
                hits.append(part)
    shas = list(forbidden_shas)
    for m in HEXTOK.finditer(low):
        if any(s.startswith(m.group(0)) for s in shas):
            hits.append(m.group(0))
    return hits
