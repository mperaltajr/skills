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

Since 2026-10-09 (validated fix from a session report):
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

Since 2026-10-13 (owner-approved, session report item 4):
  - prep, --slide, --insert and record_picks --edits-done each add an entry
    (time, step, md5 and git blob id of each installed agent file) to the
    build's agent history; the first entry is the pin.
  - when the files differ across that history, compile and check_done look
    every version up in git (classify_blob): if all of them are on main the
    build carries on, with one line in COMPILED.md and at delivery ("built
    with slide-builder-worker from main 9e81cf4 and 1ea67d5"); a version only
    on a branch, never committed, missing, or one git cannot place is
    refused, and so is an old build that recorded md5s only.
  - a build session never copies or restores agent files, not even when the
    user says it is fine. Developer installs go through doctor.py fix only.

Since 2026-10-14 (owner-approved, speed verdict Q2 item 7):
  - compile judges only the translator file, the one agent that can still
    run after compile (FALLBACK MODE for a QC fix). The workers have all
    finished by then; check_done judges the versions they ran with.
  - check_done judges the versions the build's steps ran with. A file
    installed after the last agent step is a warning there, not a refusal:
    no page was made with it.

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
                if _on(c, "HEAD") and _main_tip_blob(path, main) == blob:
                    return {"kind": "main_current", "commit": c, "branch": main,
                            "text": f"it is the current {main} version (commit "
                                    f"{_short(c)}); this checkout's copy is the one "
                                    "that differs (a branch or a local edit)",
                            "do": "leave the installed file as it is and build from a "
                                  f"checkout of {main}; only the main session installs, "
                                  "after a merge"}
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


def _main_tip_blob(path: Path, main: str) -> str:
    """The blob id of the agent file with this name on the tip of main
    ('' when unknown). A probe file with another name is looked up as the
    worker."""
    name = Path(path).name
    if name[:-3] not in AGENT_NAMES:
        name = "slide-builder-worker.md"
    rc, out = _git("rev-parse", "--verify", "--quiet",
                   f"{main}:{SKILL_ROOT.name}/agents/{name}")
    return out.strip() if rc == 0 else ""


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
    """The one command that fixes it, for the refusal message. Installs go
    through doctor.py fix only (it backs the installed files up into
    _backup_<date> first, then copies). There is no copy-by-hand route any
    more: on 2026-10-13 a hand copy right after a merge skipped the backup and
    the checks, and a build session then restored the old files by hand."""
    doctor = SKILL_ROOT / "scripts" / "doctor.py"
    return (f'  py -3 "{doctor}" fix      (backs up the installed files into _backup_<date> '
            "first, then copies)\n"
            "  Run it in the main Slide Lab session, from a checkout of main, never from a "
            "build session.")


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


def installed_versions() -> dict:
    """{agent name: {"md5": ..., "blob": git blob id}} of the installed files;
    both "" when a file is missing. The blob id is computed here, so it works
    without git; looking it up (classify_blob) needs git."""
    dest = installed_agents_dir()
    out = {}
    for name in AGENT_NAMES:
        p = dest / f"{name}.md"
        try:
            out[name] = ({"md5": _digest(p), "blob": git_blob_hash(p)} if p.exists()
                         else {"md5": "", "blob": ""})
        except OSError:
            out[name] = {"md5": "", "blob": ""}
    return out


def classify_blob(blob: str) -> dict | None:
    """Where this version of an agent file lives in git.

    {"kind": "main" | "branch" | "uncommitted" | "missing", "commit", "branch",
     "label": short plain words, e.g. "main 9e81cf4"}. None when git is
    missing or cannot answer (callers refuse: a version nobody can place is
    not accepted)."""
    if not blob:
        return {"kind": "missing", "commit": "", "branch": "", "label": "not installed"}
    try:
        main = _main_ref()
        commits = _commits_with_blob(blob)
        if not commits:
            return {"kind": "uncommitted", "commit": "", "branch": "",
                    "label": "a version never committed (local edits)"}
        if main:
            on_main = [c for c in commits if _on(c, main)]
            if on_main:
                c = on_main[-1]          # git lists newest first: the first to write it
                return {"kind": "main", "commit": c, "branch": main,
                        "label": f"{main} {_short(c).split(' ')[0]}"}
        c = commits[0]
        branches = [b for b in _branches_with(c) if b not in ("main", "origin/main")]
        name = branches[0] if branches else "(a branch that no longer exists)"
        return {"kind": "branch", "commit": c, "branch": name,
                "label": f"branch {name} {_short(c).split(' ')[0]} (not on {main or 'main'})"}
    except Exception:
        return None


def agent_history(state: dict) -> list:
    """The build's agent history, oldest first; the first entry is the pin.
    An older build recorded only md5s at prep: that reads as one entry with
    no blob ids (blob None)."""
    ag = state.get("agents") or {}
    hist = ag.get("history")
    if hist:
        return list(hist)
    if ag.get("installed"):
        return [{"at": ag.get("at", ""), "step": "prep", "md5": dict(ag["installed"]),
                 "blob": None}]
    return []


def differing_agents(state: dict, now: dict | None = None, names=AGENT_NAMES,
                     include_now: bool = True) -> list:
    """Agent names (of `names`) whose installed file is not the same across
    the build's history and (with include_now) what is installed now."""
    hist = agent_history(state)
    if not hist:
        return []
    now = now or installed_versions()
    out = []
    for name in names:
        seen = {(e.get("md5") or {}).get(name, "") for e in hist}
        if include_now:
            seen.add(now[name]["md5"])
        if len(seen) > 1:
            out.append(name)
    return out


def versions_compatible(state: dict, names=AGENT_NAMES,
                        include_now: bool = True) -> tuple[bool, str, str]:
    """(ok, refusal, note) for the agent files this build was made with.

    ok, no note: every step used the files installed now (or the build has no
    record). ok with a note: the files differ, but every version is on main
    (two reviewed main versions), so the build carries on; the note goes into
    COMPILED.md and the delivery report. Not ok: a version only on a branch,
    never committed, missing, one git cannot place, or an old build that
    recorded md5s only (owner's decisions A to D, 2026-10-13).

    `names` limits the check to some agents (compile: the translator only,
    the one agent that can still run after compile). include_now=False
    judges only the versions the build's steps ran with, not what is
    installed now (check_done: every agent has finished by then, so a later
    install touched no page; installed_changed_after_last_step() gives the
    warning). Owner's decision 2026-10-14 (speed verdict Q2 item 7)."""
    hist = agent_history(state)
    now = installed_versions()
    differing = differing_agents(state, now, names, include_now)
    if not differing:
        return True, "", ""
    where = f"at {installed_agents_dir()}"
    if any(e.get("blob") is None for e in hist):
        return False, (
            "the agent files Claude Code runs changed after this build was prepared ("
            + ", ".join(differing) + f", {where}). This build recorded only file "
            "fingerprints at prep, so their versions cannot be looked up, and slides "
            "built before and after the change cannot be checked as one. Do not copy "
            "or restore agent files from this session, even if the user says it is "
            "fine. Start a new Claude session and prepare the build again with "
            "build_deck.py. " + NEW_SESSION), ""
    bad, notes, current_bad = [], [], False
    for name in differing:
        blobs = []
        for e in hist + ([{"blob": {name: now[name]["blob"]}}] if include_now else []):
            b = (e.get("blob") or {}).get(name, "")
            if b not in blobs:
                blobs.append(b)
        infos = [classify_blob(b) for b in blobs]
        if any(i is None for i in infos):
            bad.append(f"{name}: git could not look its versions up")
            current_bad = True
            continue
        not_main = [i for i in infos if i["kind"] != "main"]
        if not_main:
            bad.append(f"{name}: " + "; ".join(i["label"] for i in not_main))
            if infos[-1]["kind"] != "main":
                current_bad = True
            continue
        shorts = []
        for i in infos:
            sh = i["label"].split(" ", 1)[-1]
            if sh not in shorts:
                shorts.append(sh)
        notes.append(f"{name} from main {' and '.join(shorts)}")
    if bad:
        todo = ("The files installed now are not a version from main: the main Slide "
                "Lab session installs main with doctor.py fix (after merging). "
                if current_bad and include_now else "")
        return False, (
            "the agent files Claude Code runs changed after this build was prepared, and not every "
            "version is on main (" + "; ".join(bad) + f"; {where}). A slide built by "
            "an agent file that is only on a branch, or was never committed, cannot "
            "ship. " + todo + "Do not copy or restore agent files from this session, "
            "even if the user says it is fine. Start a new Claude session and prepare "
            "the build again with build_deck.py. " + NEW_SESSION), ""
    return True, "", ("built with " + "; ".join(notes)
                      + " (every version used is on main, so the build carries on)")


def installed_changed_after_last_step(state: dict) -> str:
    """'' when the agent files installed now are the ones the build's last
    recorded step ran with; otherwise one plain warning naming them.
    check_done shows it as a warning, not a refusal: no agent of this build
    ran with the new files (owner's decision 2026-10-14)."""
    hist = agent_history(state)
    if not hist:
        return ""
    last = hist[-1].get("md5") or {}
    now = installed_versions()
    changed = [n for n in AGENT_NAMES if last.get(n, "") != now[n]["md5"]]
    if not changed:
        return ""
    labels = []
    for n in changed:
        info = classify_blob(now[n]["blob"])
        labels.append(f"{n} ({info['label'] if info else 'version unknown'})")
    return ("the agent files installed now changed after this build's last agent step ("
            + ", ".join(labels) + "). No page of this deck was made with them, so the "
            "deck is not affected. Do not copy or restore agent files from this session; "
            "start a new Claude session before the next build or round of fixes")


def changed_since_prep(state: dict) -> str:
    """'' when the build may carry on (the same agent files throughout, the
    build predates the record, or every version used is on main); otherwise
    the plain refusal. versions_compatible() also gives the note to record."""
    return versions_compatible(state)[1]
