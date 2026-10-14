#!/usr/bin/env python3
"""render_slot.py - a limit on how many renders run at once on this computer.

Twenty design agents each rendering their own sketches, plus self-checks and
QC renders, all started browsers and PowerPoint/LibreOffice runs at the same
time, and single renders took a median of 110 s under that load (owner's
decision 2026-10-14, Q1). Every render now first takes one of N "render
slots", shared by every Slide Lab process on the computer:

    with render_slot("render_html.py (option_A.html)"), render_deadline(...), scratch_env():
        ...

The slot goes OUTSIDE render_deadline(): the time limit starts only once the
slot is held, so time spent waiting for a slot never counts toward it.

How it works: N lock files in C:\\Temp\\slidelab\\render_slots\\ (the Slide
Lab scratch root; SLIDE_LAB_SCRATCH_ROOT moves it, SLIDE_LAB_RENDER_SLOT_DIR
names the folder outright). A render holds one with the operating system's
file lock, so a render that crashes or is ended frees its slot by itself: no
leftover lock to clean up, and nothing else on the computer is touched.

  SLIDE_LAB_RENDER_SLOTS       how many renders at once (default 16; 0 or
                               "off" = no limit)
  SLIDE_LAB_RENDER_SLOT_WAIT   seconds to wait for a slot before giving up
                               (default 150). Past it the command exits 75
                               with a "busy, re-run" message (not the time-out
                               message: nothing was started).

No render waits on itself: a second render_slot() in the same process (one
render calling another) does not take a second slot, and a command started by
a process that holds a slot (it sees SLIDE_LAB_RENDER_SLOT_HELD) does not
either.

From a shell:
  py -3 render_slot.py --status     how many slots are in use now
"""
from __future__ import annotations

import contextlib
import os
import random
import sys
import tempfile
import threading
import time
from pathlib import Path

ENV_SLOTS = "SLIDE_LAB_RENDER_SLOTS"
ENV_DIR = "SLIDE_LAB_RENDER_SLOT_DIR"
ENV_WAIT = "SLIDE_LAB_RENDER_SLOT_WAIT"
ENV_HELD = "SLIDE_LAB_RENDER_SLOT_HELD"
DEFAULT_SLOTS = 16       # the 10/14 bench: 16 beat no limit, 4, 6, 8, 12 and 20
DEFAULT_WAIT = 150.0
ANNOUNCE_AFTER = 2.0
EXIT_BUSY = 75            # "temporary failure, try again"; no other Slide Lab exit uses it
SLOT_DIR_NAME = "render_slots"

_lock = threading.Lock()
_depth = 0                # render_slot() blocks open in this process


def slots() -> int:
    """How many renders may run at once (0 = no limit)."""
    raw = (os.environ.get(ENV_SLOTS) or "").strip().lower()
    if raw in ("off", "none", "no", "false"):
        return 0
    if not raw:
        return DEFAULT_SLOTS
    try:
        return max(0, int(raw))
    except ValueError:
        return DEFAULT_SLOTS


def max_wait() -> float:
    try:
        v = float(os.environ.get(ENV_WAIT) or DEFAULT_WAIT)
        return v if v > 0 else DEFAULT_WAIT
    except ValueError:
        return DEFAULT_WAIT


def slot_dir() -> Path:
    """The folder that holds the slot files (made if missing)."""
    env = (os.environ.get(ENV_DIR) or "").strip()
    if env:
        d = Path(env)
    else:
        try:
            sb = str(Path(__file__).resolve().parents[2] / "slide-builder" / "scripts")
            if sb not in sys.path:
                sys.path.append(sb)
            import _scratch
            d = _scratch.root() / SLOT_DIR_NAME
        except Exception:
            base = Path("C:/Temp/slidelab") if sys.platform == "win32" else \
                Path(tempfile.gettempdir()) / "slidelab"
            d = base / SLOT_DIR_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


# ------------------------------------------------------------ the OS lock
def _try_lock(path: Path):
    """An open, locked file descriptor for path, or None when another process
    holds it."""
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o666)
    except OSError:
        return None
    try:
        if sys.platform == "win32":
            import msvcrt
            os.lseek(fd, 0, 0)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except OSError:
        os.close(fd)
        return None


def _unlock(fd) -> None:
    try:
        if sys.platform == "win32":
            import msvcrt
            os.lseek(fd, 0, 0)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_UN)
    except OSError:
        pass
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def _pid_alive(pid: int) -> bool:
    try:
        import _scratch
        return _scratch._pid_alive(pid)
    except Exception:
        return True


def _held_by_parent() -> bool:
    """True when a process that started this one holds a slot now."""
    raw = (os.environ.get(ENV_HELD) or "").strip()
    if not raw:
        return False
    try:
        pid = int(raw)
    except ValueError:
        return False
    return pid != os.getpid() and _pid_alive(pid)


def in_use() -> int:
    """How many slots are held now (by any process)."""
    n = slots()
    if n <= 0:
        return 0
    d = slot_dir()
    busy = 0
    for i in range(1, n + 1):
        fd = _try_lock(d / f"slot_{i}.lock")
        if fd is None:
            busy += 1
        else:
            _unlock(fd)
    return busy


def _busy_exit(what: str, n: int, waited: float) -> None:
    here = Path(__file__).resolve().parent
    sys.stderr.write(
        f"ERROR: {what} did not start: all {n} render slots on this computer stayed "
        f"busy for {int(waited)} s (other Slide Lab renders are running). Nothing was "
        f"rendered and nothing was ended.\n"
        f"Next: run the same command again (busy, re-run). If it keeps happening, let "
        f"the other renders finish first, or allow more at once with "
        f"SLIDE_LAB_RENDER_SLOTS (now {n}) or a longer wait with SLIDE_LAB_RENDER_SLOT_WAIT "
        f"(now {int(max_wait())} s).\n"
        f"To see the slots in use: py -3 \"{here / 'render_slot.py'}\" --status\n")
    sys.stderr.flush()
    sys.exit(EXIT_BUSY)


@contextlib.contextmanager
def render_slot(what: str = "the render"):
    """Hold one render slot for the with-block (see the top of this file)."""
    global _depth
    n = slots()
    with _lock:
        nested = _depth > 0
        if nested or n <= 0 or _held_by_parent():
            _depth += 1
            skip = True
        else:
            skip = False
    if skip:
        try:
            yield None
        finally:
            with _lock:
                _depth -= 1
        return

    d = slot_dir()
    names = [d / f"slot_{i}.lock" for i in range(1, n + 1)]
    start = time.monotonic()
    announced = False
    fd = None
    cap = max_wait()
    while True:
        order = names[:]
        random.shuffle(order)
        for p in order:
            fd = _try_lock(p)
            if fd is not None:
                break
        if fd is not None:
            break
        waited = time.monotonic() - start
        if waited >= cap:
            _busy_exit(what, n, waited)
        if not announced and waited >= ANNOUNCE_AFTER:
            sys.stderr.write(f"waiting for a render slot, {n} in use ({what}; "
                             f"up to {int(cap)} s; the render's own time limit starts "
                             f"once it has one)\n")
            sys.stderr.flush()
            announced = True
        time.sleep(0.15 + random.random() * 0.2)
    if announced:
        sys.stderr.write(f"got a render slot after {time.monotonic() - start:.0f} s\n")
    saved = os.environ.get(ENV_HELD)
    os.environ[ENV_HELD] = str(os.getpid())
    with _lock:
        _depth += 1
    try:
        yield fd
    finally:
        with _lock:
            _depth -= 1
        if saved is None:
            os.environ.pop(ENV_HELD, None)
        else:
            os.environ[ENV_HELD] = saved
        _unlock(fd)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Slide Lab's machine-wide render slots.")
    ap.add_argument("--status", action="store_true", help="print how many slots are in use")
    args = ap.parse_args(argv)
    n = slots()
    if n <= 0:
        print(f"No render limit ({ENV_SLOTS} is off).")
        return 0
    print(f"{in_use()} of {n} render slots in use ({slot_dir()}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
