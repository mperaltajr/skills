#!/usr/bin/env python3
"""update.py — is a newer Slide Lab available?

  py -3 slide-builder/scripts/update.py check        at most once a day
  py -3 slide-builder/scripts/update.py check --now  always (user said "update Slide Lab")
  py -3 slide-builder/scripts/update.py after-pull   after the user approved and Claude ran git pull

Why this exists: the install used to rely on a Claude Code start-up hook that
ran `git pull`. Company-managed Claude Code (allowManagedHooksOnly) ignores
hooks users add, so those installs never updated and nobody was told.

`check` only looks (git fetch, which downloads nothing into your files) and
prints one of:
  UP TO DATE
  UPDATE AVAILABLE: <n> change(s). <summary lines>
  SKIPPED: <reason>          (already checked today, offline, not a git copy)
It never changes files. The pull itself is a separate, visible command that
Claude runs only after the user says yes:
  git -C "<skills folder>" pull --ff-only
`after-pull` then copies the agent files Claude Code runs, checks that every
Python package the new version needs is installed, and says whether Claude
must be restarted.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

ONE_DAY = 20 * 3600   # a little under a day, so a daily morning start always checks


def _git(*args, timeout=60) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=timeout)


def _stamp() -> Path:
    return REPO / ".git" / "slide-lab-last-update-check"


def check(now: bool) -> int:
    if not (REPO / ".git").exists():
        print("SKIPPED: this Slide Lab copy was not installed with git, so it "
              "cannot update itself. Reinstall with git clone (see README).")
        return 0
    st = _stamp()
    if not now and st.exists() and time.time() - st.stat().st_mtime < ONE_DAY:
        print("SKIPPED: already checked today.")
        return 0
    try:
        r = _git("fetch", "--quiet", "origin", timeout=90)
    except Exception as exc:
        print(f"SKIPPED: could not reach the Slide Lab server ({type(exc).__name__}).")
        return 0
    if r.returncode != 0:
        print("SKIPPED: could not reach the Slide Lab server "
              f"({(r.stderr or '').strip().splitlines()[-1:] or ['offline']}).")
        return 0
    try:
        st.write_text(time.strftime("%Y-%m-%d %H:%M"), encoding="utf-8")
    except OSError:
        pass
    up = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    upstream = up.stdout.strip() if up.returncode == 0 else "origin/main"
    n = _git("rev-list", "--count", f"HEAD..{upstream}")
    behind = int(n.stdout.strip() or 0) if n.returncode == 0 else 0
    if behind == 0:
        print("UP TO DATE")
        return 0
    dirty = _git("status", "--porcelain", "--untracked-files=no").stdout.strip()
    if _git("merge-base", "HEAD", upstream).returncode != 0:
        # The server's history was rewritten (it was cleaned of client names
        # on 2026-10-05), so a pull can never fast-forward this copy.
        print("UPDATE AVAILABLE: Slide Lab's history was replaced on the server, "
              "so this copy needs a one-time reset instead of a pull.")
        print(f'To install (after the user says yes):  git -C "{REPO}" reset --keep {upstream}')
        print("It keeps the user's own edits where it can and refuses if one would "
              "be overwritten; if it refuses, tell the user which files and stop.")
        return 0
    log = _git("log", "--format=  - %s", f"HEAD..{upstream}", "-n", "8")
    print(f"UPDATE AVAILABLE: {behind} change(s).")
    print(log.stdout.rstrip())
    if behind > 8:
        print(f"  ... and {behind - 8} more")
    print(f'To install (after the user says yes):  git -C "{REPO}" pull --ff-only')
    if dirty:
        print("NOTE: this copy has local edits to Slide Lab's own files; the "
              "pull may refuse. If it does, tell the user and do not discard "
              "their edits without asking.")
    return 0


def after_pull() -> int:
    import doctor
    restart = False
    msg = doctor.fix_agents()
    if msg:
        print(f"  [fixed] {msg}")
        restart = True
    rows = doctor.run_checks()
    bad = [r for r in rows if r["required"] and not r["ok"]]
    if bad:
        doctor.print_table(rows)
        print("  The update needs the steps above before the next build.")
    if restart:
        print("RESTART NEEDED: the agent files changed. Close and reopen Claude "
              "before building, or the next build stops with an agents-out-of-date "
              "message.")
    else:
        print("UPDATED: no restart needed.")
    return 1 if bad else 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["check"]:
        return check(now="--now" in argv)
    if argv[:1] == ["after-pull"]:
        return after_pull()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
