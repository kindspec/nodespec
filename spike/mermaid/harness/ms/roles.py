# SPDX-License-Identifier: MIT
"""§10: launching a blind role (X or F) behind §10.3's barrier.

The role runs as one fresh `claude -p` session inside a bubblewrap sandbox
(the pattern of blockspec's prereg-2 tierer). Visible inside, and nothing
else:

- /usr read-only, with /bin, /lib, /lib64 and /sbin as its usual links,
  so system libraries and python3 are there;
- /etc/ssl, /etc/resolv.conf, /etc/hosts and /etc/nsswitch.conf
  read-only, for TLS and name resolution;
- the claude binary, read-only, at /opt/claude/claude;
- a HOME holding only the CLI's credential file, read-only, and /tmp:
  fresh tmpfs, or with `scratch`, host directories that persist after the
  session (for F they go into custody with its work, unread);
- /work: the role's exported directory (blind.export), writable;
- fresh /tmp, /proc and /dev.

The environment is cleared (`--clearenv`) except HOME, PATH and LANG. Every
namespace is unshared except the network: §10.3 makes network access an
honour-system barrier, and Appendix E's prompt forbids fetching any kindspec
repository. The session gets no MCP server (`--strict-mcp-config` with an
empty configuration) and only built-in file and shell tools. The launcher
refuses to start if ANTHROPIC_API_KEY is set, and stops the session if its
init event reports another model, any tool outside that list, or any MCP
server.

Before the session, the same sandbox runs a barrier probe: a file planted
outside /work, the repository, ~/.claude and /home must be unreadable or
absent. The probe's result goes in the launch record.

Two records come out:
- the launch record (JSON): role, date, model asked for and reported, the
  tools and MCP servers the session reported, the export manifest with each
  file's sha256, the prompt as sent with its sha256, the sandbox argv, the
  barrier probe, and the exit status. It holds no session output, so it can
  be committed for either role (§10.3: LOG records what each agent was
  given);
- the session stream (stream-json), written where the caller says. For F it
  holds the sealed fixtures as written, so it stays in F's custody,
  unread, with F's work.

For F the launcher reads only the session's final result text, and records
the 64-hex tokens in it: their values if there is exactly one, else only
their count, since a second token could be the nonce.
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

MODEL = "claude-opus-5-5"
TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
SANDBOX_HOME = "/home/role"
SANDBOX_CLAUDE = "/opt/claude/claude"  # the CLI, bound away from its host path under /home
DEFAULT_CREDENTIALS = os.path.expanduser("~/.claude/.credentials.json")
HEX64 = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")


class Refused(Exception):
    pass


def claude_binary():
    p = shutil.which("claude")
    if not p:
        raise Refused("the claude CLI is not on PATH")
    return os.path.realpath(p)


def sandbox_argv(work, credentials, binary, extra=(), scratch=None):
    resolv = os.path.realpath("/etc/resolv.conf")
    a = ["bwrap", "--die-with-parent", "--new-session", "--unshare-all", "--share-net",
         "--clearenv", "--setenv", "HOME", SANDBOX_HOME, "--setenv", "PATH", "/usr/bin:/bin",
         "--setenv", "LANG", "C.UTF-8", "--ro-bind", "/usr", "/usr"]
    for link, target in (("/bin", "usr/bin"), ("/lib", "usr/lib"), ("/lib64", "usr/lib64"), ("/sbin", "usr/sbin")):
        a += ["--symlink", target, link]
    a += ["--ro-bind", "/etc/ssl", "/etc/ssl", "--ro-bind", resolv, "/etc/resolv.conf",
          "--ro-bind-try", "/etc/hosts", "/etc/hosts", "--ro-bind-try", "/etc/nsswitch.conf", "/etc/nsswitch.conf",
          "--proc", "/proc", "--dev", "/dev"]
    if scratch:
        # The role's /tmp and HOME persist in host directories, so whatever
        # the role writes outside /work (F's tar and nonce, say) survives
        # the session and goes into custody with its work, unread.
        os.makedirs(os.path.join(scratch, "tmp"), exist_ok=True)
        os.makedirs(os.path.join(scratch, "home", ".claude"), exist_ok=True)
        a += ["--bind", os.path.join(scratch, "tmp"), "/tmp", "--tmpfs", "/home",
              "--bind", os.path.join(scratch, "home"), SANDBOX_HOME]
    else:
        a += ["--tmpfs", "/tmp", "--tmpfs", "/home", "--dir", SANDBOX_HOME]
    a += ["--dir", SANDBOX_HOME + "/.claude",
          "--ro-bind", credentials, SANDBOX_HOME + "/.claude/.credentials.json",
          "--ro-bind", binary, SANDBOX_CLAUDE, *extra,
          "--bind", work, "/work", "--chdir", "/work", "--"]
    return a


def claude_argv(binary, prompt, mcp_config):
    return [binary, "-p", "--model", MODEL, "--no-session-persistence", "--output-format", "stream-json",
            "--verbose", "--strict-mcp-config", "--mcp-config", mcp_config,
            "--permission-mode", "acceptEdits", "--tools", *TOOLS, "--allowedTools", *TOOLS, "--", prompt]


PROBE = r"""
import json, os, sys
planted, repos = sys.argv[1], sys.argv[2:]
out = {}
def can_read(p):
    try:
        with open(p, "rb") as f:
            f.read(1)
        return True
    except OSError:
        return False
out["planted_readable"] = can_read(planted)
out["planted_exists"] = os.path.lexists(planted)
out["repos_visible"] = {r: os.path.lexists(r) for r in repos}
out["home_entries"] = sorted(os.listdir("/home"))
out["sandbox_home_entries"] = sorted(os.listdir(os.environ["HOME"]))
out["claude_dir_entries"] = sorted(os.listdir(os.path.join(os.environ["HOME"], ".claude")))
out["work_entries"] = sorted(os.listdir("/work"))
out["env_keys"] = sorted(os.environ)
print(json.dumps(out, sort_keys=True))
"""


def barrier_probe(work, credentials, binary, repos, scratch=None):
    """Plant a file outside /work and show the sandbox cannot read it, nor
    see the repositories."""
    d = tempfile.mkdtemp(prefix="role-barrier.")
    planted = os.path.join(d, "planted-secret.txt")
    with open(planted, "w") as f:
        f.write("not for the role\n")
    try:
        r = subprocess.run(sandbox_argv(work, credentials, binary, scratch=scratch) +
                           ["/usr/bin/python3", "-I", "-S", "-c", PROBE, planted] + repos,
                           capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout) if r.returncode == 0 else {"error": r.stderr.strip()[-300:]}
    finally:
        shutil.rmtree(d, ignore_errors=True)
    ok = (res.get("planted_readable") is False and res.get("planted_exists") is False
          and not any(res.get("repos_visible", {"x": True}).values())
          and res.get("home_entries") == [os.path.basename(SANDBOX_HOME)]
          and res.get("claude_dir_entries") == [".credentials.json"]
          and set(res.get("env_keys", ["?"])) <= {"HOME", "PATH", "LANG", "PWD"})
    return ok, res


def init_problems(ev):
    """What is wrong with a session's init event: another model, any tool
    outside the built-in list, any MCP server, any plugin that is not built
    into the CLI, or any hook."""
    bad = []
    if ev.get("model") != MODEL:
        bad.append(f"model {ev.get('model')}")
    if sorted(ev.get("tools") or []) != sorted(TOOLS):
        bad.append(f"tools {ev.get('tools')}")
    if ev.get("mcp_servers"):
        bad.append(f"MCP servers {ev.get('mcp_servers')}")
    extra = [p for p in ev.get("plugins") or [] if not isinstance(p, dict) or p.get("path") != "builtin"]
    if extra:
        bad.append(f"plugins {extra}")
    if ev.get("hooks"):
        bad.append(f"hooks {ev.get('hooks')}")
    return bad


def manifest(work):
    out = []
    for root, _, files in os.walk(work):
        for n in sorted(files):
            p = os.path.join(root, n)
            out.append([os.path.relpath(p, work), hashlib.sha256(open(p, "rb").read()).hexdigest()])
    return sorted(out)


def launch(role, work, prompt, record_path, session_path, credentials=None, repos=(), log=print, scratch=None):
    """Run one role session. Returns the launch record (also written to
    record_path)."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        raise Refused("ANTHROPIC_API_KEY is set: a role runs on the CLI's subscription, not the API")
    if not shutil.which("bwrap"):
        raise Refused("bwrap is not installed; a role runs only inside its sandbox")
    credentials = credentials or DEFAULT_CREDENTIALS
    if not os.path.isfile(credentials):
        raise Refused(f"credential file not found: {credentials}")
    work = os.path.realpath(work)
    if not os.path.isdir(work) or os.path.exists(os.path.join(work, ".git")):
        raise Refused(f"{work} is not an exported directory (missing, or holds .git)")
    binary = claude_binary()
    version = subprocess.run([binary, "--version"], capture_output=True, text=True).stdout.strip()
    rec = {"role": role, "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "model_asked": MODEL, "claude_version": version, "tools_asked": TOOLS,
           "export_manifest": manifest(work), "prompt": prompt,
           "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
    if scratch is not None:
        if os.path.exists(scratch):
            raise Refused(f"{scratch} exists; a role's scratch starts empty")
        rec["scratch"] = scratch
    ok, probe = barrier_probe(work, credentials, binary, list(repos), scratch=scratch)
    rec["barrier_probe"] = probe
    rec["barrier_holds"] = ok
    if not ok:
        _write(record_path, rec)
        raise Refused(f"the barrier probe failed: {probe}")
    mcp_dir = tempfile.mkdtemp(prefix="role-mcp.")
    mcp = os.path.join(mcp_dir, "mcp-empty.json")
    with open(mcp, "w") as f:
        f.write('{"mcpServers": {}}\n')
    argv = sandbox_argv(work, credentials, binary, ["--ro-bind", mcp, "/etc/role-mcp-empty.json"], scratch) + \
        claude_argv(SANDBOX_CLAUDE, prompt, "/etc/role-mcp-empty.json")
    rec["sandbox_argv"] = argv[:-1] + ["<prompt>"]
    log(f"role {role}: barrier holds; starting {MODEL} in {work}")
    rc, init, result = None, None, None
    with open(session_path, "w", encoding="utf-8") as sess:
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            for line in p.stdout:
                sess.write(line)
                sess.flush()
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if init is None and ev.get("type") == "system" and ev.get("subtype") == "init":
                    init = ev
                    rec["model_reported"] = ev.get("model")
                    rec["tools_reported"] = ev.get("tools")
                    rec["mcp_servers_reported"] = ev.get("mcp_servers")
                    bad = init_problems(ev)
                    if bad:
                        p.kill()
                        rec["refused"] = "init event: " + "; ".join(bad)
                        log(f"role {role}: refused at init: {rec['refused']}")
                    else:
                        log(f"role {role}: init: model {ev.get('model')}, tools {ev.get('tools')}, no MCP server")
                if ev.get("type") == "result":
                    result = ev.get("result") or ""
            rc = p.wait()
        finally:
            if p.poll() is None:
                p.kill()
            shutil.rmtree(mcp_dir, ignore_errors=True)
    rec["exit_status"] = rc
    rec["init_seen"] = init is not None
    if init is None and not rec.get("refused"):
        # Without an init event, the model, tools and MCP servers the
        # session ran with were never checked: the run does not count.
        rec["refused"] = "no init event: the session's model, tools and MCP servers were not checked"
        log(f"role {role}: refused: {rec['refused']}")
    if role == "F":
        toks = HEX64.findall(result or "")
        rec["result_hex64_count"] = len(toks)
        if len(toks) == 1:
            rec["sealed_sha256"] = toks[0].lower()
    rec["session_sha256"] = hashlib.sha256(open(session_path, "rb").read()).hexdigest()
    _write(record_path, rec)
    log(f"role {role}: exit {rc}; launch record {record_path}")
    return rec


def _write(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False) + "\n")
