"""_test_temp.py — every test's temporary folders, deleted when the test ends.

Imported at the top of each smoke test. Tests made folders with
tempfile.mkdtemp() and many never removed them (slidelab_e2e_*, *_smoke_*
folders piled up in the system temp folder). Importing this:

  - points tempfile at one folder for this test run, under the Slide Lab
    scratch root (C:\\Temp\\slidelab\\_tests\\<test>_<id>\\), so every
    mkdtemp() and TemporaryDirectory() the test makes lands there;
  - points SLIDE_LAB_SCRATCH_ROOT at <that folder>\\scratch, so the scripts
    the test runs (in this process and in the commands it starts) put their
    scratch there too, never in the real scratch root;
  - deletes the whole folder when the test process ends.

SLIDE_LAB_KEEP_TEST_TEMP=1 keeps it for debugging (the path is printed).
"""
from __future__ import annotations

import atexit
import os
import secrets
import shutil
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.append(str(_SCRIPTS))

KEEP = os.environ.get("SLIDE_LAB_KEEP_TEST_TEMP", "").strip() == "1"


def _base() -> Path:
    """<scratch root>/_tests, from the REAL root (before this run overrides it)."""
    try:
        import _scratch
        saved = os.environ.pop(_scratch.ROOT_ENV, None)
        try:
            return _scratch.scratch_dir("_tests")
        finally:
            if saved is not None:
                os.environ[_scratch.ROOT_ENV] = saved
    except Exception:
        b = Path(tempfile.gettempdir()) / "slidelab_tests"
        b.mkdir(parents=True, exist_ok=True)
        return b


_name = Path(sys.argv[0]).stem if sys.argv and sys.argv[0] else "test"
RUN_DIR = _base() / f"{_name}_{os.getpid()}_{secrets.token_hex(3)}"
RUN_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH = RUN_DIR / "scratch"
SCRATCH.mkdir(exist_ok=True)

# A parent test run (a test that runs other tests) already chose the folders;
# a child keeps its own run folder but shares nothing else.
tempfile.tempdir = str(RUN_DIR)
os.environ["SLIDE_LAB_SCRATCH_ROOT"] = str(SCRATCH)
# This computer's own settings.local.json (say, three designs per slide) must
# not change what a test sees: tests run on the published settings.json. A
# test that wants a local file points this at its own.
os.environ.setdefault("SLIDE_LAB_SETTINGS_LOCAL", "none")
# The Storyline tab of the one Slide Lab page (2026-10-16) waits for the user
# before any prompt is written. The older suites test what comes after it, so
# it is off for them; run_one_page_smoke.py turns it on.
os.environ.setdefault("SLIDE_LAB_STORYLINE_TAB", "0")


def _writable_retry(func, path, *_exc) -> None:
    """rmtree error handler: a read-only file (git objects) is made writable
    and removed again."""
    import stat
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def _rmtree(p: Path) -> None:
    if sys.version_info >= (3, 12):
        shutil.rmtree(p, onexc=_writable_retry)
    else:
        shutil.rmtree(p, onerror=_writable_retry)


def _cleanup() -> None:
    if KEEP:
        print(f"[test temp kept: {RUN_DIR}]", file=sys.stderr)
        return
    tempfile.tempdir = None
    # A log file the test process still holds open (build.log) is closed
    # first; logging would otherwise close it only after this runs.
    # A pipeline script called in this process may still tee its output to
    # <out>/build.log (scripts/_log.py); close that log first.
    lg = sys.modules.get("_log")
    h = getattr(lg, "_attached", {}).get("handle") if lg else None
    if h is not None:
        try:
            sys.stdout = getattr(sys, "__stdout__", sys.stdout)
            sys.stderr = getattr(sys, "__stderr__", sys.stderr)
            h.close()
        except Exception:
            pass
    if "logging" in sys.modules:
        try:
            sys.modules["logging"].shutdown()
        except Exception:
            pass
    for _ in range(3):
        try:
            _rmtree(RUN_DIR)
        except OSError:
            pass
        if not RUN_DIR.exists():
            break
        # A file still held open (a render program closing late): try again.
        import time
        time.sleep(1.0)
    if RUN_DIR.exists():
        print(f"[test temp could not be fully deleted: {RUN_DIR}]", file=sys.stderr)


atexit.register(_cleanup)
