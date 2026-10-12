#!/usr/bin/env python3
"""_scratch.py — the one place Slide Lab puts scratch files outside a session folder.

Owner's decision (2026-10-09): every scratch file Slide Lab makes outside a
session folder (local copies, renders, checks, browser profiles, LibreOffice
profiles) goes under ONE root:

    C:\\Temp\\slidelab\\<session or task>\\      (Windows)
    <system temp folder>/slidelab/<session or task>/   (a Mac, or no C:\\Temp)

Before this, sessions and scripts invented their own folders in C:\\Temp
(deck1009, cf_check, ...) and the system temp folder filled with leftovers no
one could tie to a deck. One root means "the deck is good" can delete that
session's scratch, and "clean up my finished decks" can list the rest.

SLIDE_LAB_SCRATCH_ROOT overrides the root (tests point it at their own
folder so they never touch the real one).

Use:
  scratch_dir("task")            a named folder under the root (made if missing)
  session_scratch(session_dir)   the session's folder, named after the session
                                 folder (a second session with the same folder
                                 name gets "_<6 letters of a hash>" added)
  find_session_scratch(dir)      the session's existing folder(s), made by
                                 nothing (publish_cleanup uses this)
  temp_dir(prefix)               a tempfile.TemporaryDirectory under the root
                                 (deleted when the with-block ends)
  in_use(folder)                 with-block that marks a folder in use (a lock
                                 file), so a cleanup skips it
  cache_dir()                    the small caches (font lists), kept and reused

From a shell:
  py -3 scripts/_scratch.py --session "<session folder>"   prints the path (makes it)
  py -3 scripts/_scratch.py --root                          prints the root
"""
from __future__ import annotations

import contextlib
import hashlib
import os
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT_ENV = "SLIDE_LAB_SCRATCH_ROOT"
OWNER_FILE = "_slidelab_session.txt"     # which session folder this scratch belongs to
LOCK_FILE = "_slidelab_in_use.lock"      # present while a process uses the folder
CACHE = "_cache"                         # small caches, never listed for cleanup


def root() -> Path:
    """The scratch root, made if missing."""
    env = (os.environ.get(ROOT_ENV) or "").strip()
    if env:
        r = Path(env)
    elif sys.platform == "win32":
        r = Path("C:/Temp/slidelab")
        try:
            r.mkdir(parents=True, exist_ok=True)
        except OSError:
            r = Path(tempfile.gettempdir()) / "slidelab"
    else:
        r = Path(tempfile.gettempdir()) / "slidelab"
    r.mkdir(parents=True, exist_ok=True)
    return r


def safe_name(name: str) -> str:
    """A folder name made only of safe characters (spaces kept)."""
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(name or "")).strip(" .")
    return s[:80] or "scratch"


def scratch_dir(name: str) -> Path:
    """<root>/<name>/, made if missing."""
    p = root() / safe_name(name)
    p.mkdir(parents=True, exist_ok=True)
    return p


def cache_dir() -> Path:
    return scratch_dir(CACHE)


def _owner(folder: Path) -> str:
    try:
        return (folder / OWNER_FILE).read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _key(session_dir) -> str:
    return str(Path(session_dir).resolve()).casefold()


def _candidates(session_dir) -> list[Path]:
    sd = Path(session_dir).resolve()
    base = safe_name(sd.name)
    h = hashlib.sha1(_key(sd).encode("utf-8")).hexdigest()[:6]
    return [root() / base, root() / f"{base}_{h}"]


def find_session_scratch(session_dir) -> list[Path]:
    """The session's existing scratch folder(s); creates nothing."""
    want = _key(session_dir)
    return [c for c in _candidates(session_dir)
            if c.is_dir() and _owner(c).casefold() == want]


def session_scratch(session_dir) -> Path:
    """The session's scratch folder, named after the session folder; made if
    missing, with a note saying which session folder it belongs to."""
    found = find_session_scratch(session_dir)
    if found:
        return found[0]
    plain, hashed = _candidates(session_dir)
    target = plain if not plain.exists() else hashed
    target.mkdir(parents=True, exist_ok=True)
    (target / OWNER_FILE).write_text(str(Path(session_dir).resolve()), encoding="utf-8")
    return target


def temp_dir(prefix: str = "tmp_"):
    """tempfile.TemporaryDirectory under the scratch root (auto-deleted).
    Falls back to the system temp folder if the root cannot be made."""
    try:
        d = str(root())
    except OSError:
        d = None
    return tempfile.TemporaryDirectory(prefix=f"_{prefix}", dir=d)


# ---------------------------------------------------------------- in use
def _pid_alive(pid: int) -> bool:
    """True when the process exists. Never signals it (on Windows os.kill
    would end the process, so it is not used there)."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            k32 = ctypes.windll.kernel32
            h = k32.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
            if not h:
                return False
            try:
                code = ctypes.c_ulong()
                ok = k32.GetExitCodeProcess(h, ctypes.byref(code))
                return bool(ok) and code.value == 259    # STILL_ACTIVE
            finally:
                k32.CloseHandle(h)
        except Exception:
            return True                                 # cannot tell: assume in use
    try:
        os.kill(pid, 0)                                 # POSIX: signal 0 only checks
        return True
    except ProcessLookupError:
        return False
    except Exception:
        return True


def lock_holder(folder: Path) -> int | None:
    """The live process holding the folder's lock file, else None."""
    lf = Path(folder) / LOCK_FILE
    if not lf.exists():
        return None
    try:
        pid = int((lf.read_text(encoding="utf-8").split() or ["0"])[0])
    except Exception:
        return -1                                       # unreadable lock: treat as held
    return pid if _pid_alive(pid) else None


@contextlib.contextmanager
def in_use(folder):
    """Mark folder in use (a lock file with this process id) for the block."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    lf = folder / LOCK_FILE
    lf.write_text(f"{os.getpid()} {time.strftime('%Y-%m-%d %H:%M:%S')}", encoding="utf-8")
    try:
        yield folder
    finally:
        try:
            lf.unlink()
        except OSError:
            pass


def latest_change(folder: Path) -> float:
    """Newest modification time of the folder or anything in it."""
    folder = Path(folder)
    best = folder.stat().st_mtime
    for f in folder.rglob("*"):
        try:
            best = max(best, f.stat().st_mtime)
        except OSError:
            pass
    return best


def size(folder: Path) -> int:
    total = 0
    for f in Path(folder).rglob("*"):
        try:
            if f.is_file():
                total += f.stat().st_size
        except OSError:
            pass
    return total


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Where Slide Lab scratch files go.")
    ap.add_argument("--session", type=Path, help="A session folder: print (and make) its scratch folder.")
    ap.add_argument("--task", help="A task name: print (and make) <root>/<task>.")
    ap.add_argument("--root", action="store_true", help="Print the scratch root.")
    a = ap.parse_args(argv)
    if a.session:
        print(session_scratch(a.session))
    elif a.task:
        print(scratch_dir(a.task))
    else:
        print(root())
    return 0


if __name__ == "__main__":
    sys.exit(main())
