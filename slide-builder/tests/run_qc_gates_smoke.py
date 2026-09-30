#!/usr/bin/env python3
"""Smoke test for the Tier-2 QC gates.

Three things that were decorative or half-implemented before:

  1. `severity: "block"` did nothing. finalize counted blocking findings, printed
     the tally, and returned 0; nothing downstream read it, so a deck with
     blocking defects reported DONE. Now finalize records the count and compile
     refuses on it.
  2. Package integrity was unchecked. A structural edit outside the pipeline can
     leave an ORPHANED slide part (in the zip, referenced by no <p:sldId>).
     LibreOffice reports that as "source file could not be loaded", which is how
     the symptom got misfiled as a stale LibreOffice profile. The shipped
     13-slide deck still has exactly this defect.
  3. `chrome_zone_overlap` only checked the TOP zone despite its own comment
     promising the bottom one, and tested shape.top only (never top+height), so
     it could never see content reaching DOWN into the footer/page-number band.
     That is the class that recurred across slides 9/10/11.

Run:  py -3 slide-builder/tests/run_qc_gates_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import inspect
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pptx import Presentation  # noqa: E402
from pptx.util import Inches  # noqa: E402

import _state  # noqa: E402
from compile_picks import assert_package_integrity  # noqa: E402


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="qc_gates_smoke_"))
    try:
        print("[1] finalize's per-option record decides what may ship")
        out = tmp / "build"
        out.mkdir()
        _state.record_prep(out, "h1", out)
        K = _state.option_key
        clean = {"blocks": 0, "reasons": []}
        blocked = {"blocks": 1, "reasons": ["chrome_buried"]}

        def _allowed(keys):
            return _state.check_options_finalized(_state.read_state(out), keys)

        ok, why = _allowed([K(1, "A")])
        assert not ok and "has not run" in why, "no finalize at all must refuse"
        _state.begin_finalize(out)
        ok, why = _allowed([K(1, "A")])
        assert not ok and "did not finish" in why, "a crashed finalize must refuse"
        _state.record_option_qc(out, {K(1, "A"): clean, K(2, "A"): clean,
                                      K(3, "A"): blocked, K(3, "C"): blocked,
                                      K(5, "A"): blocked})
        _state.end_finalize(out, "ok")
        assert _allowed([K(1, "A"), K(2, "A")])[0], "clean picks must ship"
        ok, why = _allowed([K(1, "A"), K(3, "A")])
        assert not ok and "slide_03/A" in why, "a blocked pick must refuse, by name"
        assert not _allowed([K(4, "A")])[0], "an option never finalized must refuse"
        print("    ok: none / crashed / blocked / never-finalized all refuse, by option")

        # Fixing slide 3 with finalize --slide 3 must not wipe slide 5's block.
        _state.begin_finalize(out, slide=3)
        _state.record_option_qc(out, {K(3, "A"): clean, K(3, "C"): blocked})
        _state.end_finalize(out, "ok")
        assert _allowed([K(3, "A")])[0], "the fixed option ships"
        assert not _allowed([K(5, "A")])[0], (
            "a finalize --slide 3 wiped slide 5's block; that is how two blocked "
            "slides once reached compile")
        # A blocked option nobody picked must not stop the deck.
        assert _allowed([K(1, "A"), K(3, "A")])[0], "unpicked 3C must not block"
        print("    ok: --slide keeps other slides' blocks; unpicked blocks don't stop the deck")

        print("[2] an orphaned slide part is caught")
        good = tmp / "good.pptx"
        prs = Presentation()
        for _ in range(3):
            prs.slides.add_slide(prs.slide_layouts[6])
        prs.save(str(good))
        assert assert_package_integrity(good) == [], "a clean deck must pass"

        orphan = tmp / "orphan.pptx"
        shutil.copy2(good, orphan)
        prs2 = Presentation(str(orphan))
        lst = prs2.slides._sldIdLst
        lst.remove(list(lst)[1])      # unlist the slide but keep its part + rel
        prs2.save(str(orphan))
        problems = assert_package_integrity(orphan)
        assert problems, "an orphaned slide part must be detected"
        assert "orphaned" in problems[0], problems
        print(f"    ok: {problems[0]}")

        print("[3] chrome-zone check covers the BOTTOM zone and exempts placeholders")
        import finalize_deck
        src = inspect.getsource(finalize_deck.run_option_qc)
        assert "BOTTOM_ZONE_PX" in src, "bottom invariant zone still not implemented"
        assert "bottom_px > BOTTOM_ZONE_PX" in src, "bottom zone is not actually tested"
        assert "bottom_px = top_px + h_px" in src, "still testing shape.top only, not the bbox"
        assert "is_placeholder" in src, (
            "inherited template placeholders are not exempt; the check fired on "
            "every option of every slide and therefore carried no signal")
        print("    ok: bottom zone tested via the bounding box; template chrome exempt")

        print("[4] a decorative rule crossing text is caught; false positives are not")
        from pptx import Presentation as _P
        from pptx.util import Emu
        from pptx.enum.shapes import MSO_SHAPE
        import finalize_deck as F
        PX = 9525

        def _build(path, mode):
            prs = _P(); prs.slide_width = Emu(1280 * PX); prs.slide_height = Emu(720 * PX)
            s = prs.slides.add_slide(prs.slide_layouts[6])
            if mode == "rule_crosses":       # the shipped slide-9 defect
                r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(83*PX), Emu(192*PX), Emu(3*PX), Emu(450*PX))
                r.name = "accent-rule"; r.text_frame.text = ""
                for i, y in enumerate((200, 300, 400)):
                    tb = s.shapes.add_textbox(Emu(53*PX), Emu(y*PX), Emu(62*PX), Emu(40*PX))
                    tb.name = f"TextBox {i}"; tb.text_frame.text = f"0{i+1}"
            elif mode == "card_behind":      # legitimate: card behind text
                c = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(100*PX), Emu(100*PX), Emu(400*PX), Emu(200*PX))
                c.name = "card-bg"; c.text_frame.text = ""
                tb = s.shapes.add_textbox(Emu(120*PX), Emu(120*PX), Emu(300*PX), Emu(100*PX))
                tb.name = "TextBox 1"; tb.text_frame.text = "hello"
            else:                            # legitimate: underline inside the text bbox
                tb = s.shapes.add_textbox(Emu(100*PX), Emu(100*PX), Emu(300*PX), Emu(120*PX))
                tb.name = "TextBox 1"; tb.text_frame.text = "heading"
                r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(110*PX), Emu(150*PX), Emu(200*PX), Emu(3*PX))
                r.name = "rule-underline"; r.text_frame.text = ""
            prs.save(str(path))

        def _fires(mode) -> bool:
            p = tmp / f"{mode}.pptx"
            _build(p, mode)
            res = F.run_option_qc(p, tmp / "missing.png", set(), "")
            chk = [c for c in res["checks"] if c["check"] == "rule_crosses_text"][0]
            return not chk["pass"]

        assert _fires("rule_crosses"), "a rule drawn through text must be caught"
        assert not _fires("card_behind"), "a background card behind text must NOT fire"
        assert not _fires("underline"), "an underline inside the text bbox must NOT fire"
        print("    ok: fires on a rule through text; silent on cards and underlines")

        print("[4b] the grafted takeaway buried under a body panel is BLOCKED")

        def _buried(bury: bool) -> dict:
            prs = _P(); prs.slide_width = Emu(1280 * PX); prs.slide_height = Emu(720 * PX)
            s = prs.slides.add_slide(prs.slide_layouts[6])
            # finalize's free-floating takeaway on a layout with no subtitle
            # placeholder: drawn first, at title_bottom + 8.
            sub = s.shapes.add_textbox(Emu(53*PX), Emu(133*PX), Emu(700*PX), Emu(26*PX))
            sub.name = "subtitle"
            sub.text_frame.text = "Secondary supply is a scheduled outcome, not a surprise."
            # The design's own content, anchored to the top of the zone it was
            # told was empty. Drawn after, so it covers the takeaway.
            panel = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(53*PX),
                                       Emu((125 if bury else 220)*PX),
                                       Emu(700*PX), Emu(180*PX))
            panel.name = "Rectangle 1"; panel.text_frame.text = ""
            p = tmp / f"buried_{bury}.pptx"
            prs.save(str(p))
            res = F.run_option_qc(p, tmp / "missing.png", set(), "", body_zone=(175.0, 640.0))
            return [c for c in res["checks"] if c["check"] == "chrome_buried"][0]

        hit = _buried(True)
        assert not hit["pass"], "a panel covering the grafted takeaway must be caught"
        assert hit["severity"] == "block", (
            "this collision was a warning and warnings were read past; it shipped "
            "on eight slides of one deck")
        assert "subtitle" in hit["detail"], hit["detail"]
        clean = _buried(False)
        assert clean["pass"], (
            f"a panel starting below the body top must NOT fire: {clean['detail']}")
        print(f"    ok: {hit['detail'][:66]}...; clean layout silent")

        print("[5] check_done verifies one chain: compile -> deck -> content -> vision")
        import os
        import subprocess
        K = _state.option_key

        def _deck(path, n=3):
            p = _P()
            for _ in range(n):
                p.slides.add_slide(p.slide_layouts[6])
            p.save(str(path))
            return path

        def _build(name, n=3, kind="picks"):
            """A build that compiled cleanly into <name>/final_deck.pptx."""
            d = tmp / name
            d.mkdir()
            deck = _deck(d / "final_deck.pptx", n)
            _state.record_prep(d, "h", d)
            _state.begin_finalize(d)
            opts = [K(i, "A") for i in range(1, n + 1)]
            _state.record_option_qc(d, {k: {"blocks": 0, "reasons": []} for k in opts})
            _state.end_finalize(d, "ok")
            _state.record_compile(d, kind=kind, output=deck, slides=n, options=opts)
            return d, deck

        def _done(d, *extra) -> tuple[int, str]:
            r = subprocess.run(
                [sys.executable, str(SCRIPTS / "check_done.py"), "--out", str(d), *extra],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": str(SCRIPTS)})
            return r.returncode, r.stdout

        empty = tmp / "empty"
        empty.mkdir()
        assert _done(empty)[0] == 1, "an empty build must not be deliverable"

        d, deck = _build("done")
        rc, o = _done(d)
        assert rc == 1 and "no vision pass recorded" in o, o
        _state.record_vision_qc(d, deck, 2)                       # partial look
        rc, o = _done(d)
        assert rc == 1 and "2 slide(s) reviewed; the deck has 3" in o, o
        _state.record_vision_qc(d, deck, 3, criticals=0, majors=1, advisories=2)
        rc, o = _done(d)
        assert rc == 1 and "1 Major" in o, "an open Major must refuse (decision 6)"
        _state.record_vision_qc(d, deck, 3, criticals=0, majors=0, advisories=2)
        rc, o = _done(d)
        assert rc == 0, f"clean chain, only Advisory open, must be deliverable: {o}"
        print("    ok: none / partial / open Major refuse; Advisory-only passes")

        print("[6] a later finalize block on a shipped option re-opens 'done'")
        _state.record_option_qc(d, {K(2, "A"): {"blocks": 1, "reasons": ["chrome_buried"]}})
        rc, o = _done(d)
        assert rc == 1 and "slide_02/A" in o, o
        _state.record_option_qc(d, {K(2, "A"): {"blocks": 0, "reasons": []}})
        assert _done(d)[0] == 0
        print("    ok")

        print("[7] a deck edited after compile is not deliverable")
        prs4 = _P(str(deck))
        prs4.slides[0].shapes.add_textbox(Inches(1), Inches(1), Inches(2), Inches(1))
        prs4.save(str(deck))
        rc, o = _done(d)
        assert rc == 1 and "changed since it was compiled" in o, o
        print("    ok: the edit that broke something every time it was used re-opens 'done'")

        print("[8] re-prepping after compile makes the deck stale")
        d, deck = _build("reprep")
        _state.record_vision_qc(d, deck, 3)
        assert _done(d)[0] == 0
        _state.record_prep(d, "h2-edited-brief", d)
        rc, o = _done(d)
        assert rc == 1 and "changed after this deck was compiled" in o, o
        print("    ok")

        print("[9] a hand-made deck passed with --deck is refused")
        d, deck = _build("wrongdeck")
        _state.record_vision_qc(d, deck, 3)
        other = _deck(tmp / "handmade.pptx", 3)
        hm = _P(str(other))
        hm.slides[0].shapes.add_textbox(Inches(1), Inches(1), Inches(2), Inches(1))
        hm.save(str(other))
        rc, o = _done(d, "--deck", str(other))
        assert rc == 1 and "not the deck the last compile produced" in o, o
        # A byte-identical copy elsewhere (emailed, moved to OneDrive) is fine.
        import shutil as _sh
        copy = tmp / "sent_copy.pptx"
        _sh.copy(deck, copy)
        assert _done(d, "--deck", str(copy))[0] == 0, "an identical copy must pass"
        print("    ok: a different file refuses; an identical copy elsewhere passes")

        print("[10] a missing deck, and an unreadable one, are refusals")
        d, deck = _build("gone")
        deck.unlink()
        rc, o = _done(d)
        assert rc == 1 and "nothing to deliver" in o, o
        d = tmp / "notpptx"
        d.mkdir()
        junk = d / "final_deck.pptx"
        junk.write_text("not a pptx", encoding="utf-8")
        _state.record_prep(d, "h", d)
        _state.begin_finalize(d); _state.end_finalize(d, "ok")
        _state.record_compile(d, output=junk, slides=0)
        rc, o = _done(d)
        assert rc == 1 and "does not open" in o, (
            "the audit got DELIVERABLE for a file containing 'not a pptx': " + o)
        print("    ok")

        print("[11] record_vision_qc refuses a count larger than the deck")
        d, deck = _build("overcount")
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "record_vision_qc.py"), "--out", str(d),
             "--deck", str(deck), "--slides-reviewed", "999",
             "--criticals", "0", "--majors", "0"],
            capture_output=True, text=True)
        assert r.returncode == 2, r.stdout
        print("    ok")

        print("[12] the all-options and splice decks are checkable and labeled")
        d, deck = _build("allvar", kind="all_variations")
        _state.record_vision_qc(d, deck, 3)
        rc, o = _done(d)
        assert rc == 0 and "all-options comparison deck" in o, o
        d, _ = _build("splice", kind="splice")
        elsewhere = _deck(tmp / "client_deck_slidelab.pptx", 3)   # next to the original
        _state.record_compile(d, kind="splice", output=elsewhere, slides=3,
                              options=[K(1, "A")])
        _state.record_vision_qc(d, elsewhere, 3)
        rc, o = _done(d)
        assert rc == 0 and "spliced deck" in o, (
            "the spliced deck lives next to the original; check_done must find it "
            "from the compile record: " + o)
        print("    ok")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
