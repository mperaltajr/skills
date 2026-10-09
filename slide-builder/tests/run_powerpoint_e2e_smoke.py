#!/usr/bin/env python3
"""End-to-end smoke on PowerPoint only: a fictional build, every stage as its
own process, with LibreOffice turned off (SLIDE_LAB_NO_LIBREOFFICE=1), while
the user's PowerPoint stays as it was (owner's decision, 2026-10-09).

  prep stub (build_deck.py) -> option scripts -> review page + picks
  (record_picks.py) -> finalize (one-deck render) -> final check page
  (build_review.py --final) -> compile (PowerPoint opens-cleanly check, final
  render) -> slide-qc render (render_slides.py)

Checks that every stage worked, that finalize rendered all options as one deck
through PowerPoint, that compile ran PowerPoint's opens-cleanly check, that the
PowerPoint notice was printed once per command, and that the user's open
presentations are the same before and after.

  --time N   also time an N-slide build end to end on PowerPoint and on
             LibreOffice (when installed) and print both; not part of the suite

Run:  py -3 slide-builder/tests/run_powerpoint_e2e_smoke.py [--time 20]
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE.parent.parent / "slide-qc" / "scripts"))

import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402
import render_slides as RS  # noqa: E402
from _ppt_snapshot import snapshot  # noqa: E402

QC = HERE.parent.parent / "slide-qc" / "scripts"


def _ok(r, what):
    assert r.returncode == 0, f"{what} failed:\n{r.stdout[-2500:]}\n{r.stderr[-2500:]}"
    return r


def build(n: int, env: dict, check: bool = True) -> dict:
    """One fictional n-slide build, every stage. Returns seconds per stage."""
    t = {}
    t0 = time.monotonic()
    tmp, out = H.new_build(n)
    t["prep"] = time.monotonic() - t0
    try:
        for i in range(1, n + 1):
            H.write_option(out, i)
        picks = {f"slide_{i:02d}": "A" for i in range(1, n + 1)}
        t0 = time.monotonic()
        r = _ok(H.run("build_review.py", "--out", out, **env), "review page")
        token = _state.read_state(out)["review"]["token"]
        body = _state.canonical_picks(picks)
        _ok(H.run("record_picks.py", "--out", out, "--approved",
                  f"PICKS {body} CHECK {_state.approval_check(token, body)}", **env), "picks")
        t["review+picks"] = time.monotonic() - t0
        t0 = time.monotonic()
        r = _ok(H.run("finalize_deck.py", "--out", out, "--template", H.TEMPLATE, **env),
                "finalize")
        t["finalize"] = time.monotonic() - t0
        import re as _re
        m = _re.search(r"rendered in ([0-9.]+)s", r.stdout)
        if m:
            t["(of which render)"] = float(m.group(1))
        if check:
            assert f"{n} as one deck" in r.stdout, r.stdout[-1500:]
            assert "PowerPoint)" in r.stdout and "LibreOffice)" not in r.stdout, r.stdout[-1500:]
            assert (r.stdout + r.stderr).count(RS.NOTICE) == 1, "notice not printed once"
            assert all((out / f"slide_{i:02d}" / "option_A.png").exists() for i in range(1, n + 1))
            # each picture is its own slide: equal to that option rendered alone
            import numpy as np
            from PIL import Image
            def _img(p):
                return np.asarray(Image.open(p).convert("L"), dtype=float)
            alone = []
            for i in range(1, n + 1):
                sd = out / f"slide_{i:02d}"
                RS.render(sd / "option_A.pptx", sd / "_alone", 120, quiet=True)
                alone.append(_img(sd / "_alone" / "slide_01.png"))
            for i in range(1, n + 1):
                a = _img(out / f"slide_{i:02d}" / "option_A.png")
                d = [np.abs(a - b).mean() if a.shape == b.shape else 999 for b in alone]
                assert int(np.argmin(d)) == i - 1 and d[i - 1] < 0.5, (i, d)
        t0 = time.monotonic()
        r = _ok(H.run("build_review.py", "--out", out, "--final", **env), "final check")
        tok = (_state.read_state(out).get("final_check") or {}).get("token")
        assert tok and (out / "FINAL-CHECK.html").exists()
        t["final check"] = time.monotonic() - t0
        t0 = time.monotonic()
        r = _ok(H.run("compile_picks.py", "--out", out, "--final-token", tok, **env), "compile")
        t["compile"] = time.monotonic() - t0
        deck = out / "final_deck.pptx"
        if check:
            assert "PowerPoint opens it cleanly" in r.stdout, r.stdout[-1500:]
            assert (r.stdout + r.stderr).count(RS.NOTICE) == 1
            assert len(list((out / "final_pngs").glob("slide_*.png"))) == n
            comp = _state.read_state(out)["stages"]["compile"]
            assert comp["slides"] == n, comp
            md = (out / "COMPILED.md").read_text(encoding="utf-8")
            assert "Opens in PowerPoint (read-only, no repair, slide count matches): **yes**" in md
        t0 = time.monotonic()
        r = _ok(H.run_path(QC / "render_slides.py", deck, out / "_qc", **env), "slide-qc render")
        t["slide-qc render"] = time.monotonic() - t0
        if check:
            assert "(PowerPoint" in r.stdout and len(list((out / "_qc").glob("slide_*.png"))) == n
    finally:
        H.cleanup(tmp)
    return t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--time", type=int, default=0)
    args = ap.parse_args()
    if not RS.powerpoint_available():
        print("  skipped: PowerPoint can't be driven on this computer")
        print("SMOKE PASSED.")
        return 0
    before = snapshot()
    print("[1] a 3-slide fictional build on PowerPoint only (no LibreOffice)")
    t = build(3, {"SLIDE_LAB_NO_LIBREOFFICE": "1"})
    print("    ok: prep, review + picks, finalize (one deck), final check, compile "
          "(PowerPoint opens it cleanly), slide-qc render")
    print("    " + ", ".join(f"{k} {v:.1f}s" for k, v in t.items()))
    if args.time:
        print(f"[2] timing a {args.time}-slide build")
        tp = build(args.time, {"SLIDE_LAB_RENDERER": "powerpoint"}, check=False)
        rows = [("PowerPoint", tp)]
        if RS.libreoffice_available():
            tl = build(args.time, {"SLIDE_LAB_RENDERER": "libreoffice"}, check=False)
            rows.append(("LibreOffice", tl))
        for name, tt in rows:
            total = sum(v for k, v in tt.items() if not k.startswith("("))
            print(f"    {name:<12} total {total:6.1f}s  "
                  + "  ".join(f"{k} {v:.1f}s" for k, v in tt.items()))
    after = snapshot()
    assert before[1] == after[1], "the user's open presentations changed"
    if before[0]:
        assert after[0], "PowerPoint was running before and is not now"
    print(f"  ok: the user's PowerPoint: {len(before[1])} presentation(s) open before, "
          f"the same {len(after[1])} after")
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
