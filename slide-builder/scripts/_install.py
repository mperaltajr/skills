"""_install.py — is the agent Claude Code will dispatch the one in this repo?

Claude Code dispatches `slide-builder-worker` and `slide-builder-translator`
from ~/.claude/agents/, not from slide-builder/agents/. The start-of-session
git pull refreshes this repo only. So every fix written into the repo copy is
invisible at runtime until someone copies the file over, and nothing said so:
on 2026-09-30 the installed copies turned out to be from 18 June, and every
translator fix since (the rule that keeps decks openable in PowerPoint, the
takeaway rule, the chart ban, the label-wrap rule) had never reached a running
agent.

build_deck.py calls check_installed_agents() before any agent is dispatched and
refuses to prep on a mismatch; doctor.py shows the same check.

Since 2026-10-09 (validated fix, Kinfield v3.1 session report):
  - the refusal says WHICH version is installed, by looking the installed
    file up in the repo's git history: an older version from main (copy the
    repo version over), an unmerged branch (merge that branch first), or no
    committed version at all (local edits: back them up first). Without git,
    or when anything goes wrong, it falls back to the plain message. It never
    crashes the check.
  - installing backs the installed files up first, into
    ~/.claude/agents/_backup_<date>/ as <name>.md.bak (a subfolder and not a
    .md file, so Claude Code never loads a backup as an agent); the last
    KEEP_BACKUPS folders are kept.
  - prep records the installed files' fingerprints in the build state;
    compile and check_done compare them and stop when they changed. Slides
    built before and after a mid-build install came from different agent
    files, and a swap-and-restore around prep made the prep check certify
    something that was not true.

Agent files load when a Claude session starts: after installing, start a new
Claude session.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parent
AGENT_NAMES = ("slide-builder-worker", "slide-builder-translator")
KEEP_BACKUPS = 5
NEW_SESSION = ("Agent files load when a Claude session starts: after installing, "
               "start a new Claude session.")


def installed_agents_dir() -> Path:
    """Where Claude Code loads user agents from. Overridable for tests."""
    override = os.environ.get("SLIDE_LAB_AGENTS_DIR")
    return Path(override) if override else Path.home() / ".claude" / "agents"


def _digest(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def git_blob_hash(path: Path) -> str:
    """The id git gives this file's content (what `git hash-object` prints),
    computed here so it works without git."""
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


# ---------------------------------------------------------------- git lookup
def _git(*args, timeout: int = 20) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True,
                       text=True, timeout=timeout, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "")


def _main_ref() -> str | None:
    for ref in ("main", "origin/main", "master", "origin/master"):
        rc, _ = _git("rev-parse", "--verify", "--quiet", ref + "^{commit}")
        if rc == 0:
            return ref
    return None


def _commits_with_blob(blob: str) -> list[str]:
    """Commits (any branch) that wrote a file with exactly this content.
    -m: a version first written by a merge (a resolved conflict) is found too;
    without it git shows no changes for merge commits."""
    rc, out = _git("log", "--all", "-m", f"--find-object={blob}", "--no-abbrev",
                   "--format=%x01%H", "--raw", timeout=60)
    if rc != 0:
        raise RuntimeError("git log failed")
    found, cur = [], None
    for line in out.splitlines():
        if line.startswith("\x01"):
            cur = line[1:].strip()
        elif line.startswith(":") and cur:
            parts = line.split()
            if len(parts) >= 4 and parts[3] == blob and cur not in found:
                found.append(cur)
    return found


def _on(commit: str, ref: str) -> bool:
    rc, _ = _git("merge-base", "--is-ancestor", commit, ref)
    return rc == 0


def _branches_with(commit: str) -> list[str]:
    rc, out = _git("branch", "--all", "--contains", commit,
                   "--format=%(refname:short)")
    return [b.strip() for b in out.splitlines() if b.strip()] if rc == 0 else []


def _short(commit: str) -> str:
    rc, out = _git("show", "-s", "--format=%h of %cs", commit)
    return out.strip() if rc == 0 and out.strip() else commit[:7]


def which_version(path: Path) -> dict | None:
    """Which committed version of an agent file this is, from git history.

    {"kind": "main_older" | "main_newer" | "branch" | "uncommitted",
     "commit": "...", "branch": "...", "text": plain sentence, "do": what to do}
    None when git is missing or the lookup fails (callers fall back to the
    plain message)."""
    try:
        blob = git_blob_hash(path)
        main = _main_ref()
        commits = _commits_with_blob(blob)
        if not commits:
            return {"kind": "uncommitted", "commit": "", "branch": "",
                    "text": "it matches no version ever committed to this repo, so "
                            "it holds local edits",
                    "do": "back it up first (the copy below does), then copy the "
                          "repo version over"}
        if main:
            on_main = [c for c in commits if _on(c, main)]
            if on_main:
                c = on_main[0]
                if not _on(c, "HEAD"):
                    return {"kind": "main_newer", "commit": c, "branch": main,
                            "text": f"it is a newer version from {main} (commit "
                                    f"{_short(c)}) than this checkout has",
                            "do": "update this checkout (git pull) and run again; "
                                  "do not copy this older checkout over it"}
                return {"kind": "main_older", "commit": c, "branch": main,
                        "text": f"it is an older version from {main} (commit {_short(c)})",
                        "do": "copy the repo version over"}
        c = commits[0]
        branches = [b for b in _branches_with(c) if b not in ("main", "origin/main")]
        name = branches[0] if branches else "(a branch that no longer exists)"
        return {"kind": "branch", "commit": c, "branch": name,
                "text": f"it is an unmerged version from branch {name} (commit "
                        f"{_short(c)}), not on {main or 'main'}",
                "do": f"merge branch {name} into {main or 'main'} first, then install "
                      f"from {main or 'main'} (only the main session installs, after "
                      "the merge)"}
    except Exception:
        return None


def repo_copy_unmerged(src: Path) -> bool:
    """True when git says this checkout's copy of the file is on no commit of
    main (a worktree builder's unmerged edit). False when unsure."""
    try:
        main = _main_ref()
        if not main:
            return False
        commits = _commits_with_blob(git_blob_hash(src))
        return not any(_on(c, main) for c in commits)
    except Exception:
        return False


# ---------------------------------------------------------------- the check
def check_installed_agents(explain: bool = True) -> list[str]:
    """Return one line per agent whose installed copy is missing or differs.
    With explain, a differing copy's line says which version it is (git)."""
    problems: list[str] = []
    dest = installed_agents_dir()
    for name in AGENT_NAMES:
        src = SKILL_ROOT / "agents" / f"{name}.md"
        inst = dest / f"{name}.md"
        if not src.exists():
            continue  # a repo without the agent has nothing to compare
        if not inst.exists():
            problems.append(f"{name}: not installed at {inst}")
        elif _digest(src) != _digest(inst):
            line = f"{name}: installed copy differs from the repo"
            info = which_version(inst) if explain else None
            if info:
                line += f"; {info['text']}. To fix: {info['do']}."
                if info["kind"] != "main_newer" and repo_copy_unmerged(src):
                    line += (" Note: this checkout's own copy is not on main yet "
                             "either; install only from main, after the merge.")
            problems.append(line)
    return problems


def _today_backup_dir(dest: Path) -> Path:
    stamp = datetime.now().strftime("%Y-%m-%d")
    d = dest / f"_backup_{stamp}"
    if d.exists():
        d = dest / f"_backup_{stamp}_{datetime.now().strftime('%H%M%S')}"
    return d


def backup_installed(dest: Path | None = None) -> Path | None:
    """Copy the installed agent files to dest/_backup_<date>/<name>.md.bak
    before anything overwrites them. Keeps the last KEEP_BACKUPS backup
    folders. Returns the folder, or None when there was nothing to back up."""
    dest = Path(dest) if dest else installed_agents_dir()
    present = [dest / f"{n}.md" for n in AGENT_NAMES if (dest / f"{n}.md").exists()]
    if not present:
        return None
    bdir = _today_backup_dir(dest)
    bdir.mkdir(parents=True, exist_ok=True)
    for f in present:
        shutil.copy2(f, bdir / (f.name + ".bak"))
    old = sorted(p for p in dest.glob("_backup_*") if p.is_dir())
    for p in old[:-KEEP_BACKUPS]:
        shutil.rmtree(p, ignore_errors=True)
    return bdir


def copy_command() -> str:
    """The commands that fix it, for the refusal message: back up, then copy."""
    dest = installed_agents_dir()
    src = SKILL_ROOT / "agents"
    bdir = dest / f"_backup_{datetime.now().strftime('%Y-%m-%d')}"
    doctor = SKILL_ROOT / "scripts" / "doctor.py"
    lines = [f'  py -3 "{doctor}" fix      (backs up the installed files first, then copies)',
             "  or by hand, backing up first:",
             f'  mkdir "{bdir}"']
    for n in AGENT_NAMES:
        if (dest / f"{n}.md").exists():
            lines.append(f'  copy "{dest / (n + ".md")}" "{bdir / (n + ".md.bak")}"')
    for n in AGENT_NAMES:
        lines.append(f'  copy "{src / (n + ".md")}" "{dest / (n + ".md")}"')
    return "\n".join(lines)


# ---------------------------------------------------------------- per build
def installed_fingerprints() -> dict:
    """{agent name: md5 of the installed file, or "" when it is missing}."""
    dest = installed_agents_dir()
    out = {}
    for name in AGENT_NAMES:
        p = dest / f"{name}.md"
        try:
            out[name] = _digest(p) if p.exists() else ""
        except OSError:
            out[name] = ""
    return out


def changed_since_prep(state: dict) -> str:
    """'' when the installed agent files are the ones recorded at prep (or
    the build predates the record); otherwise the plain refusal."""
    rec = (state.get("agents") or {}).get("installed")
    if not rec:
        return ""
    now = installed_fingerprints()
    changed = [n for n in AGENT_NAMES if rec.get(n, "") != now.get(n, "")]
    if not changed:
        return ""
    return (
        "the agent files Claude Code runs changed after this build was prepared ("
        + ", ".join(changed) + f", at {installed_agents_dir()}). Slides built before "
        "and after the change came from different agent files, so this build "
        "cannot be checked as one. Either put back the files that were installed "
        "at prep (doctor.py keeps backups in _backup_<date> there), or start a new "
        "Claude session and prepare the build again with build_deck.py. "
        + NEW_SESSION)
