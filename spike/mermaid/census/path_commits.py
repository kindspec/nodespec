"""Count commits per (repo, path) through the GitHub API, capped at 3 (metadata only).

usage: python3 -I path_commits.py paths-all.tsv > path-commits.tsv
Output columns: repo, path, commits_on_default_branch (0..3, 3 means >=3), or ERR.
"""
import concurrent.futures as cf
import subprocess
import sys
import urllib.parse


def one(line):
    repo, path = line.rstrip("\n").split("\t", 1)
    q = urllib.parse.quote(path, safe="/")
    r = subprocess.run(["gh", "api", f"repos/{repo}/commits?path={q}&per_page=3", "--jq", "length"],
                       capture_output=True, text=True)
    n = r.stdout.strip() if r.returncode == 0 else "ERR"
    return f"{repo}\t{path}\t{n}"


lines = [l for l in open(sys.argv[1], encoding="utf-8") if "\t" in l]
with cf.ThreadPoolExecutor(8) as ex:
    for out in ex.map(one, lines):
        print(out, flush=True)
