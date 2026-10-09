#!/usr/bin/env python3
"""Smoke test: the review page keeps picks between rounds (2026-10-09).

Bug: the per-slide stamp hashed every option_* .py/.html, including the
option_X_native.py the conversion writes, so every converted pick looked
changed on the next review page and was dropped (its comments stayed).

  1. the stamp covers only the designer's files: writing option_A_native.py
     (and other pipeline files) leaves it unchanged
  2. round 1 in a real page (Playwright through scripts/_browser.py): pick 5
     slides, comment on 2, click Build my deck; a note typed afterwards on a
     third slide stays in the browser
  3. between rounds: the 2 commented slides are edited in place
     (record_picks --edits-done), two untouched picks are "converted", and
     slide 3 is redesigned with three new options
  4. round 2, same browser: 4 picks preselected (the 2 edited ones marked
     "edited from your comments", all 4 "kept from last round"), the
     redesigned slide empty, the applied comments gone, the untouched note kept
  5. round 2 in a fresh browser (no saved choices): the same 4 picks come from
     the page itself

Run:  py -3 slide-builder/tests/run_picks_kept_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402

SLIDES = [f"slide_{n:02d}" for n in range(1, 6)]


def _stamp_unit(out: Path) -> None:
    print("[1] the stamp ignores files written after the design")
    sd = out / "slide_05"
    before = _state.option_files_stamp(sd)
    time.sleep(1.1)
    for name in ("option_A_native.py", "option_A_native.plan.json", "option_A.sketch.png",
                 "option_A_translation_report.json"):
        (sd / name).write_text("# pipeline output\n", encoding="utf-8")
    assert _state.option_files_stamp(sd) == before, "a pipeline file changed the stamp"
    for name in ("option_A_native.py", "option_A_native.plan.json", "option_A.sketch.png",
                 "option_A_translation_report.json"):
        (sd / name).unlink()
    print("    ok")


def _hook(pg) -> None:
    pg.evaluate("() => { window.__copied = null;"
                " navigator.clipboard.writeText = t => {"
                " window.__copied = t; return Promise.resolve(); }; }")


def _state_of(pg) -> dict:
    return pg.evaluate("""() => {
        const r = {};
        window.__SLIDE_IDS__.forEach(sid => {
            const kept = document.getElementById('kept-' + sid);
            r[sid] = {
                badge: document.getElementById('badge-' + sid).textContent,
                kept: kept && kept.style.display !== 'none' ? kept.textContent : '',
                headline: document.getElementById('fb-' + sid + '-headline').value,
                other: document.getElementById('fb-' + sid + '-other').value,
                chips: Array.from(document.querySelectorAll(
                    '.chip.selected[data-slide="' + sid + '"]')).map(c => c.dataset.chip),
            };
        });
        return r;
    }""")


def _round2_checks(st: dict, local_note: bool) -> None:
    for sid in ("slide_01", "slide_02", "slide_04", "slide_05"):
        assert st[sid]["badge"] == "Picked A", (sid, st[sid])
        assert st[sid]["kept"].startswith("Kept from last round"), (sid, st[sid])
    for sid in ("slide_01", "slide_02"):
        assert "edited from your comments" in st[sid]["kept"], (sid, st[sid])
    for sid in ("slide_04", "slide_05"):
        assert "edited" not in st[sid]["kept"], (sid, st[sid])
    assert st["slide_03"]["badge"] == "Not decided yet", st["slide_03"]
    assert not st["slide_03"]["kept"], st["slide_03"]
    # applied comments are gone
    assert not st["slide_01"]["chips"] and not st["slide_02"]["headline"], st
    if local_note:
        assert st["slide_04"]["other"] == "Untouched note", st["slide_04"]


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed: skipped")
        print("SMOKE PASSED.")
        return 0
    import _browser
    tmp, out = H.new_build(5)
    try:
        for n in range(1, 6):
            H.write_option(out, n, "A")
        H.write_option(out, 3, "B")
        _stamp_unit(out)
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out).returncode == 0
        review = (out / "REVIEW.html").resolve().as_uri()
        errors: list[str] = []
        with sync_playwright() as pw:
            b = _browser.launch(pw)
            try:
                ctx = b.new_context()
                pg = ctx.new_page()
                pg.on("pageerror", lambda e: errors.append(str(e)))
                pg.on("dialog", lambda d: d.accept())

                print("[2] round 1: pick 5, comment on 2, Build my deck")
                pg.goto(review)
                pg.evaluate("() => localStorage.clear()")
                pg.reload()
                _hook(pg)
                for sid in SLIDES:
                    pg.click(f'#card-{sid} .decision-buttons button.pick[data-letter="A"]')
                pg.click('.chip[data-slide="slide_01"][data-chip="Too dense, simplify"]')
                pg.fill("#fb-slide_02-headline", "Shorter title")
                pg.click("#btn-build")
                pg.wait_for_function("() => window.__copied")
                msg = pg.evaluate("() => window.__copied")
                assert "Feedback:" in msg and "slide_02" in msg and "Shorter title" in msg, msg
                pg.fill("#fb-slide_04-other", "Untouched note")   # typed after Build
                print("    ok")

                print("[3] between rounds: edit 2 in place, convert 2, redesign slide 3")
                r = H.run("record_picks.py", "--out", out, "--approved", msg)
                assert r.returncode == 0, r.stdout[-1500:]
                assert sorted(c["slide"] for c in _state.pending_comments(
                    _state.read_state(out), "edit")) == ["slide_01", "slide_02"]
                time.sleep(1.1)
                for n in (1, 2):
                    p = out / f"slide_{n:02d}" / "option_A.py"
                    p.write_text(p.read_text(encoding="utf-8").replace(
                        "Point one", "Point one, edited"), encoding="utf-8")
                r = H.run("record_picks.py", "--out", out, "--edits-done")
                assert r.returncode == 0, r.stdout[-1500:]
                r = H.run("redesign_round.py", "start", "--out", out, "--slides", "3",
                          "--keep-previous")
                assert r.returncode == 0, r.stdout
                r = H.run("build_deck.py", "--slide", "3", "--out", out, "--template",
                          H.TEMPLATE, "--pattern", "direct", "--options", "3")
                assert r.returncode == 0, r.stdout[-1200:] + r.stderr[-600:]
                for L in "ABC":
                    H.write_option(out, 3, L)
                assert H.finalize(out).returncode == 0
                for n in (4, 5):   # what a conversion writes (after finalize: these
                    # direct-path test slides have nothing real to convert)
                    (out / f"slide_{n:02d}" / "option_A_native.py").write_text(
                        "# converted\n", encoding="utf-8")
                assert H.run("build_review.py", "--out", out).returncode == 0
                print("    ok")

                print("[4] round 2, same browser")
                pg.goto(review)
                pg.reload()
                st = _state_of(pg)
                _round2_checks(st, local_note=True)
                print("    ok: 4 picks preselected (2 marked edited), slide 3 empty, "
                      "applied comments gone, untouched note kept")

                print("[5] round 2, a fresh browser")
                ctx2 = b.new_context()
                pg2 = ctx2.new_page()
                pg2.on("pageerror", lambda e: errors.append(str(e)))
                pg2.goto(review)
                _round2_checks(_state_of(pg2), local_note=False)
                print("    ok: the page itself carries the recorded picks")
            finally:
                b.close()
        assert not errors, errors
    finally:
        H.cleanup(tmp)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
