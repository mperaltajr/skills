#!/usr/bin/env python3
"""Smoke test: the computer's render slots, one browser run per worker, and
build_deck.py --pending (owner's decisions 2026-10-14, Q1 and Q2 item 4).

  [1] 10 processes each holding a slot for 1 s with 3 slots: never more than
      3 at once
  [2] a holder that is ended frees its slot by itself
  [3] queue time does not count: with a 2 s time limit and the only slot
      held for 3 s, a quick job behind it still succeeds; render_html.py and
      translate_html.py take the slot before the time limit
  [4] no self-deadlock: a render inside a render (same process) and a
      command started by a holder do not wait for a second slot
  [5] a wait past SLIDE_LAB_RENDER_SLOT_WAIT exits 75 with its own "busy,
      re-run" message, not the time-out message
  [6] render_html.py draws 3 pages in one run; a stuck page fails alone and
      the others are drawn (needs a browser)
  [7] build_deck.py --pending on a 25-slide build with 5 empty slide folders
      lists exactly those 5; the dispatch plan says rolling pool past 20 and
      one message of foreground calls up to 20

Run:  py -3 slide-builder/tests/run_render_slots_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
QC = SKILL.parent / "slide-qc" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(QC))

PY = sys.executable


def _env(slot_dir: Path, n: int, **extra) -> dict:
    e = dict(os.environ)
    e.pop("SLIDE_LAB_RENDER_SLOT_HELD", None)
    e["SLIDE_LAB_RENDER_SLOT_DIR"] = str(slot_dir)
    e["SLIDE_LAB_RENDER_SLOTS"] = str(n)
    e.update({k: str(v) for k, v in extra.items()})
    return e


HOLD = r"""
import sys, time
sys.path.insert(0, sys.argv[1])
import render_slot
log, secs = sys.argv[2], float(sys.argv[3])
with render_slot.render_slot("test"):
    open(log, "a").write(f"start {time.time()}\n")
    time.sleep(secs)
    open(log, "a").write(f"end {time.time()}\n")
"""

QUICK_BEHIND = r"""
import sys, time
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[2])
from _browser import render_slot, render_deadline
with render_slot("quick"), render_deadline("quick job", seconds=2):
    time.sleep(0.5)
print("QUICK DONE")
"""

NESTED = r"""
import os, subprocess, sys
sys.path.insert(0, sys.argv[1])
import render_slot
with render_slot.render_slot("outer"):
    with render_slot.render_slot("inner"):
        pass
    child = "import sys; sys.path.insert(0, sys.argv[1]); import render_slot\n" \
            "with render_slot.render_slot('child'): print('CHILD DONE')"
    r = subprocess.run([sys.executable, "-c", child, sys.argv[1]],
                       capture_output=True, text=True, timeout=20)
    print(r.stdout.strip())
print("NESTED DONE")
"""


def _wait_for(path: Path, secs: float = 20) -> None:
    t = time.time()
    while time.time() - t < secs:
        if path.exists() and path.read_text().strip():
            return
        time.sleep(0.05)
    raise AssertionError(f"{path} never written")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="render_slots_"))

    print("[1] 10 holders, 3 slots: never more than 3 at once")
    sd = tmp / "slots1"
    logs = [tmp / f"log1_{i}.txt" for i in range(10)]     # one each: appends interleave
    ps = [subprocess.Popen([PY, "-c", HOLD, str(QC), str(lg), "1"], env=_env(sd, 3))
          for lg in logs]
    for p in ps:
        assert p.wait(timeout=60) == 0
    ev = []
    for line in "".join(lg.read_text() for lg in logs).splitlines():
        kind, t = line.split()
        ev.append((float(t), 1 if kind == "start" else -1))
    ev.sort(key=lambda x: (x[0], x[1]))
    cur = peak = 0
    for _t, d in ev:
        cur += d
        peak = max(peak, cur)
    assert sum(1 for e in ev if e[1] == 1) == 10, ev
    assert peak <= 3, f"{peak} held a slot at once with 3 slots"
    print(f"    ok: peak {peak}")

    print("[2] an ended holder frees its slot")
    sd = tmp / "slots2"
    log = tmp / "log2.txt"
    holder = subprocess.Popen([PY, "-c", HOLD, str(QC), str(log), "60"], env=_env(sd, 1))
    _wait_for(log)
    holder.kill()                      # our own child process only
    holder.wait(timeout=20)
    log3 = tmp / "log2b.txt"
    t0 = time.time()
    r = subprocess.run([PY, "-c", HOLD, str(QC), str(log3), "0"], env=_env(sd, 1),
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "start" in log3.read_text(), r.stderr
    assert time.time() - t0 < 15, "the slot was not freed when its holder ended"
    print(f"    ok: next holder got it in {time.time() - t0:.1f} s")

    print("[3] waiting for a slot does not count toward the time limit")
    sd = tmp / "slots3"
    log = tmp / "log3.txt"
    holder = subprocess.Popen([PY, "-c", HOLD, str(QC), str(log), "3"], env=_env(sd, 1))
    _wait_for(log)
    r = subprocess.run([PY, "-c", QUICK_BEHIND, str(SCRIPTS), str(QC)],
                       env=_env(sd, 1, SLIDE_LAB_RENDER_TIMEOUT=2),
                       capture_output=True, text=True, timeout=60)
    holder.wait(timeout=30)
    assert r.returncode == 0 and "QUICK DONE" in r.stdout, (r.returncode, r.stderr[-600:])
    assert "waiting for a render slot" in r.stderr, r.stderr
    for name in ("render_html.py", "translate_html.py"):
        src = (SCRIPTS / name).read_text(encoding="utf-8")
        a, b = src.find("with render_slot("), src.find("render_deadline(", src.find("with render_slot("))
        assert a > 0 and b > a and "\\" in src[a:b], f"{name}: the slot must come before the time limit"
    print("    ok: the quick job waited, then finished inside its 2 s limit")

    print("[4] no self-deadlock")
    sd = tmp / "slots4"
    r = subprocess.run([PY, "-c", NESTED, str(QC)], env=_env(sd, 1),
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and "CHILD DONE" in r.stdout and "NESTED DONE" in r.stdout, \
        (r.stdout, r.stderr[-600:])
    print("    ok: nested and child renders ran with 1 slot")

    print("[5] a long wait ends with its own busy message")
    sd = tmp / "slots5"
    log = tmp / "log5.txt"
    holder = subprocess.Popen([PY, "-c", HOLD, str(QC), str(log), "15"], env=_env(sd, 1))
    _wait_for(log)
    r = subprocess.run([PY, "-c", HOLD, str(QC), str(tmp / "log5b.txt"), "0"],
                       env=_env(sd, 1, SLIDE_LAB_RENDER_SLOT_WAIT=3),
                       capture_output=True, text=True, timeout=60)
    holder.kill()
    holder.wait(timeout=20)
    assert r.returncode == 75, (r.returncode, r.stderr)
    assert "busy, re-run" in r.stderr and "timed out" not in r.stderr, r.stderr
    print("    ok: exit 75, busy, re-run")

    print("[6] one browser run for several pages; a stuck page fails alone")
    try:
        import playwright  # noqa: F401
        have_browser = True
    except ImportError:
        have_browser = False
    if not have_browser:
        print("    SKIPPED: Playwright is not installed")
    else:
        pages = tmp / "pages"
        pages.mkdir()
        for L, color in (("A", "#1f4e79"), ("B", "#c00000"), ("C", "#2e7d32")):
            (pages / f"option_{L}.html").write_text(
                f'<html><body style="margin:0"><div style="width:1280px;height:720px;'
                f'background:{color}"></div></body></html>', encoding="utf-8")
        e = _env(tmp / "slots6", 6)
        r = subprocess.run([PY, str(SCRIPTS / "render_html.py")]
                           + [str(pages / f"option_{L}.html") for L in "ABC"],
                           env=e, capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr[-800:]
        for L in "ABC":
            assert (pages / f"option_{L}.sketch.png").exists(), L
        print("    ok: 3 pages, one command")
        for L in "ABC":
            (pages / f"option_{L}.sketch.png").unlink()
        (pages / "option_B.html").write_text(
            "<html><body><script>while (true) {}</script></body></html>", encoding="utf-8")
        r = subprocess.run([PY, str(SCRIPTS / "render_html.py")]
                           + [str(pages / f"option_{L}.html") for L in "ABC"],
                           env=dict(e, SLIDE_LAB_RENDER_PAGE_TIMEOUT="8"),
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 4, (r.returncode, r.stderr[-800:])
        assert (pages / "option_A.sketch.png").exists() and (pages / "option_C.sketch.png").exists(), \
            r.stderr[-800:]
        assert not (pages / "option_B.sketch.png").exists()
        assert "1 of 3 page(s) did not render: option_B.html" in r.stderr, r.stderr[-800:]
        assert "re-run just those" in r.stderr
        print("    ok: the stuck page failed alone, A and C were drawn")

    print("[7] build_deck.py --pending and the dispatch plan")
    out = tmp / "build"
    out.mkdir()
    empty = {4, 9, 17, 23, 25}
    slides = []
    for n in range(1, 26):
        d = out / f"slide_{n:02d}"
        d.mkdir()
        (d / "_prompt.md").write_text("prompt", encoding="utf-8")
        if n not in empty:
            (d / ("option_A.html" if n % 2 else "option_A.py")).write_text("x", encoding="utf-8")
        slides.append({"n": n, "options": ["A"]})
    (out / "_meta.json").write_text(json.dumps({"slides": slides}), encoding="utf-8")
    r = subprocess.run([PY, str(SCRIPTS / "build_deck.py"), "--pending", "--out", str(out)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr[-800:])
    assert "5 slide(s) have no worker output: 4, 9, 17, 23, 25." in r.stdout, r.stdout
    for n in range(1, 26):
        shown = f"slide_{n:02d}" in r.stdout
        assert shown == (n in empty), (n, r.stdout)
    for n in empty:
        (out / f"slide_{n:02d}" / "option_A.html").write_text("x", encoding="utf-8")
    r = subprocess.run([PY, str(SCRIPTS / "build_deck.py"), "--pending", "--out", str(out)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0 and "No slides pending" in r.stdout, r.stdout
    import build_deck as B
    big = "\n".join(B.dispatch_how_lines(out, list(range(1, 30))))
    small = "\n".join(B.dispatch_how_lines(out, list(range(1, 11))))
    assert "Rolling pool" in big and "start the next on the list" in big, big
    assert "wave, wait" not in big.lower() and "--pending" in big
    assert "run_in_background false" in small and "ONE message" in small, small
    assert "--pending" in small
    print("    ok: exactly the 5 empty slides; rolling pool past 20; one message up to 20")

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
