#!/usr/bin/env python3
"""Smoke test: one scratch area, and its cleanup (owner's decisions 2026-10-09).

  1. scripts/_scratch.py: every Slide Lab scratch folder is under one root
     (C:\\Temp\\slidelab on Windows; SLIDE_LAB_SCRATCH_ROOT overrides it). A
     session's folder is named after the session folder, a second session
     with the same folder name gets its own folder, temporary folders are
     made under the root and deleted, and the scripts that used to write to
     the system temp folder now use the root. A headless browser render puts
     the browser's profile under <root>/_browser and deletes it afterwards
     (skipped, and said so, when no browser can start).
  2. "the deck is good": publish_cleanup.py --out also deletes the session's
     scratch folder; the dry run lists it with its size and deletes nothing;
     a folder a running process has locked is skipped and the output says so.
  3. "clean up my finished decks": --temp lists only scratch folders older
     than 7 days (never the font cache, never a folder in use, never anything
     outside the root), deletes nothing by itself; --temp --delete deletes
     only the folders named, and refuses a name not on the list; --temp
     --all-listed deletes the whole list; --scan points at --temp.
  4. tests delete their own temporary folders when they finish
     (tests/_test_temp.py, imported by every smoke test and the e2e harness);
     SLIDE_LAB_KEEP_TEST_TEMP=1 keeps them.

Run:  py -3 slide-builder/tests/run_scratch_area_smoke.py
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
QC_SCRIPTS = HERE.parents[1] / "slide-qc" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(QC_SCRIPTS))

import _scratch  # noqa: E402
import publish_cleanup as PC  # noqa: E402


def _cli(*args) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = PC.main([str(a) for a in args])
    return rc, buf.getvalue()


def _age(folder: Path, days: float) -> None:
    t = time.time() - days * 86400
    for p in [*folder.rglob("*"), folder]:
        os.utime(p, (t, t))


def _session(parent: Path, name: str) -> Path:
    s = parent / name
    s.mkdir(parents=True)
    (s / "_meta.json").write_text(json.dumps({"slides": []}), encoding="utf-8")
    (s / "Client Deck.pptx").write_bytes(b"deck")
    return s


def part1() -> None:
    print("[1] one scratch root, session folders named after the session")
    root = _scratch.root()
    assert root == Path(os.environ["SLIDE_LAB_SCRATCH_ROOT"]) == _test_temp.SCRATCH, root
    assert str(root).startswith(str(_test_temp.RUN_DIR)), "tests never use the real root"
    env = {k: v for k, v in os.environ.items() if k != _scratch.ROOT_ENV}
    real = subprocess.run([sys.executable, str(SCRIPTS / "_scratch.py"), "--root"],
                          capture_output=True, text=True, env=env).stdout.strip()
    if sys.platform == "win32":
        assert Path(real) == Path("C:/Temp/slidelab"), real
    else:
        assert Path(real) == Path(tempfile.gettempdir()) / "slidelab", real

    sessions = _test_temp.RUN_DIR / "sessions"
    a = _session(sessions / "Meridian", "2026-10-09 Board Deck")
    b = _session(sessions / "Other", "2026-10-09 Board Deck")      # same folder name
    sa = _scratch.session_scratch(a)
    assert sa == root / "2026-10-09 Board Deck" and sa.is_dir(), sa
    assert _scratch.session_scratch(a) == sa, "the same session gets the same folder"
    sb = _scratch.session_scratch(b)
    assert sb != sa and sb.parent == root and sb.name.startswith("2026-10-09 Board Deck_"), sb
    assert _scratch.find_session_scratch(a) == [sa] and _scratch.find_session_scratch(b) == [sb]
    r = subprocess.run([sys.executable, str(SCRIPTS / "_scratch.py"), "--session", str(a)],
                       capture_output=True, text=True)
    assert Path(r.stdout.strip()) == sa, r.stdout
    with _scratch.temp_dir("x_") as td:
        assert Path(td).parent == root and Path(td).is_dir()
    assert not Path(td).exists(), "a temporary folder is deleted after use"
    assert _scratch.cache_dir() == root / "_cache"

    # The scripts that wrote scratch elsewhere now use the root.
    import render_slides as RS
    with RS._scratch_tmp() as td:
        assert Path(td).parent == root, td
    for name in ("translate_html.py", "_chrome_schema.py"):
        src = (SCRIPTS / name).read_text(encoding="utf-8")
        assert "_scratch.cache_dir()" in src, name
    bare = []
    for f in [*SCRIPTS.glob("*.py"), *QC_SCRIPTS.glob("*.py")]:
        src = f.read_text(encoding="utf-8")
        for m in re.finditer(r"tempfile\.TemporaryDirectory\(\)|tempfile\.mkdtemp\(", src):
            line = src[:m.start()].count("\n") + 1
            ctx = src[max(0, m.start() - 300):m.start()]
            if "except Exception" in ctx or f.name in ("_contract.py", "_scratch.py",
                                                         "_browser.py"):
                continue                     # a fallback, or the contract's own self-test
            bare.append(f"{f.name}:{line}")
    assert not bare, f"scratch outside the root: {bare}"
    for name in ("render_html.py", "translate_html.py", "doctor.py"):
        src = (SCRIPTS / name).read_text(encoding="utf-8")
        assert "scratch_env(), sync_playwright()" in src, name
    print("    ok: one root (C:\\Temp\\slidelab by default), per-session folders, "
          "temporary folders under it and deleted, scripts use it")

    # Browser profile: under <root>/_browser while the render runs, gone after.
    html = _test_temp.RUN_DIR / "probe.html"
    html.write_text('<html><body style="margin:0"><div style="width:1280px;height:720px;'
                    'background:#1f4e79"></div></body></html>', encoding="utf-8")
    png = _test_temp.RUN_DIR / "probe.png"
    seen: set[str] = set()
    stop = threading.Event()
    bdir = root / "_browser"

    def watch():
        while not stop.is_set():
            try:
                for p in bdir.glob("*/*"):
                    seen.add(p.name)
            except OSError:
                pass
            time.sleep(0.05)
    th = threading.Thread(target=watch, daemon=True)
    th.start()
    r = subprocess.run([sys.executable, str(SCRIPTS / "render_html.py"), str(html), str(png)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=180)
    stop.set()
    th.join()
    if r.returncode == 3:
        print("    SKIPPED the browser-profile check: no browser could start here")
    else:
        assert r.returncode == 0 and png.exists(), r.stdout + r.stderr
        prof = [n for n in seen if n != _scratch.LOCK_FILE]
        assert prof, "the browser's profile was not made under <root>/_browser"
        left = [p for p in bdir.glob("*")] if bdir.exists() else []
        assert not left, f"browser scratch left behind: {left}"
        print(f"    ok: the browser profile was made under {bdir} ({sorted(prof)[:2]}) "
              "and deleted after the render")


def part2() -> None:
    print("[2] the deck is good: the session's scratch folder goes too")
    root = _scratch.root()
    s = _session(_test_temp.RUN_DIR / "sessions2", "Deck Two")
    sc = _scratch.session_scratch(s)
    (sc / "copy.pptx").write_bytes(b"x" * 250_000)
    (sc / "renders").mkdir()
    (sc / "renders" / "p1.png").write_bytes(b"x" * 750_000)
    rc, out = _cli("--out", s, "--dry-run")
    assert rc == 0 and str(sc) in out and "1.0 MB" in out and "would be deleted" in out, out
    assert sc.exists(), "a dry run deletes nothing"
    with _scratch.in_use(sc):
        rc, out = _cli("--out", s)
        assert rc == 0 and "is skipped" in out and "in use" in out, out
        assert sc.exists(), "a folder in use is never deleted"
    s2 = _session(_test_temp.RUN_DIR / "sessions3", "Deck Three")
    sc2 = _scratch.session_scratch(s2)
    (sc2 / "copy.pptx").write_bytes(b"x" * 500_000)
    other = root / "Unrelated task"
    other.mkdir()
    rc, out = _cli("--out", s2)
    assert rc == 0 and not sc2.exists() and "freed 0.5 MB" in out and str(sc2) in out, out
    assert other.exists() and sc.exists(), "only that session's scratch folder goes"
    print("    ok: dry run lists it with its size; the cleanup deletes it and prints "
          "the size freed; a folder in use is skipped and said so; nothing else is touched")


def part3() -> None:
    print("[3] clean up my finished decks: old scratch folders, by the user's choice")
    root = _scratch.root()
    for p in list(root.iterdir()):
        if p.is_dir():
            import shutil
            shutil.rmtree(p)
    old1, old2, new, busy, cache = (root / "old one", root / "old two", root / "new one",
                                    root / "old busy", root / "_cache")
    for f in (old1, old2, new, busy, cache):
        f.mkdir()
        (f / "data.bin").write_bytes(b"x" * 300_000)
    (busy / _scratch.LOCK_FILE).write_text(f"{os.getpid()} now", encoding="utf-8")
    for f in (old1, old2, busy, cache):
        _age(f, 10)
    touched = root / "old but touched"
    touched.mkdir()
    (touched / "a.bin").write_bytes(b"x")
    _age(touched, 10)
    (touched / "b.bin").write_bytes(b"x")                 # changed just now
    outside = _test_temp.RUN_DIR / "not in the root"
    outside.mkdir()
    (outside / "keep.bin").write_bytes(b"x")
    _age(outside, 30)

    rc, out = _cli("--temp")
    assert rc == 0, out
    assert "old one" in out and "old two" in out and "0.3 MB" in out, out
    assert "new one" not in out and "_cache" not in out and "old but touched" not in out, out
    assert re.search(r"skipped old busy: in use \(its lock file names process \d+", out), out
    assert "Nothing was deleted" in out and old1.exists() and old2.exists(), out
    assert "not in the root" not in out
    rows, skipped = PC.temp_list()
    assert {r[0].name for r in rows} == {"old one", "old two"}, rows
    assert PC._busy(new).startswith("in use (something in it changed"), PC._busy(new)

    rc, out = _cli("--temp", "--delete", "new one")
    assert rc == 2 and "REFUSED" in out and new.exists(), out
    rc, out = _cli("--temp", "--delete", "old busy")
    assert rc == 2 and busy.exists() and "in use" in out, out
    rc, out = _cli("--temp", "--delete", "..")
    assert rc == 2 and root.exists(), out
    rc, out = _cli("--temp", "--delete", "old one")
    assert rc == 0 and not old1.exists() and old2.exists() and "deleted old one (0.3 MB)" in out, out
    rc, out = _cli("--temp", "--all-listed")
    assert rc == 0 and not old2.exists() and "freed 0.3 MB" in out, out
    for f in (new, busy, cache, touched, outside):
        assert f.exists(), f"{f} must not be touched"
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            _cli("--delete", "x")
        raise AssertionError("--delete without --temp must be refused")
    except SystemExit as exc:
        assert exc.code == 2
    (busy / _scratch.LOCK_FILE).unlink()
    _age(busy, 10)
    sessions = _test_temp.RUN_DIR / "scan_root"
    sessions.mkdir()
    rc, out = _cli("--scan", sessions)
    assert rc == 0 and "Run --temp to list them" in out, out
    print("    ok: lists only folders older than 7 days, with sizes; skips folders in use "
          "and says why; deletes only what is named or listed; never the cache or "
          "anything outside the root")


CHILD = r'''
import sys, tempfile, os
sys.path.insert(0, r"{tests}")
import _test_temp
d = tempfile.mkdtemp(prefix="slidelab_e2e_")
open(os.path.join(d, "f.txt"), "w").write("x")
with tempfile.TemporaryDirectory() as t:
    pass
import _scratch
s = _scratch.scratch_dir("from a script")
print(_test_temp.RUN_DIR)
print(d)
print(s)
'''


def part4() -> None:
    print("[4] tests delete their own temporary folders")
    child = _test_temp.RUN_DIR / "child_test.py"
    child.write_text(CHILD.format(tests=str(HERE)), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in ("SLIDE_LAB_KEEP_TEST_TEMP",)}
    r = subprocess.run([sys.executable, str(child)], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    run_dir, made, scr = (Path(x) for x in r.stdout.split("\n")[:3])
    assert Path(made).parent == run_dir and Path(scr).is_relative_to(run_dir), r.stdout
    assert not run_dir.exists() and not made.exists() and not scr.exists(), \
        "the test's folders must be gone when it ends"
    r = subprocess.run([sys.executable, str(child)], capture_output=True, text=True,
                       env={**env, "SLIDE_LAB_KEEP_TEST_TEMP": "1"})
    run_dir = Path(r.stdout.split("\n")[0])
    assert run_dir.exists() and "test temp kept" in r.stderr, r.stderr
    import shutil
    shutil.rmtree(run_dir)
    missing = [f.name for f in [*HERE.glob("run_*.py"), HERE / "_e2e_harness.py"]
               if "import _test_temp" not in f.read_text(encoding="utf-8")]
    assert not missing, f"tests that do not delete their temp folders: {missing}"
    print("    ok: a test's folders (mkdtemp, scratch) are deleted at exit; "
          "SLIDE_LAB_KEEP_TEST_TEMP=1 keeps them; every smoke test imports the helper")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    part1()
    part2()
    part3()
    part4()
    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
