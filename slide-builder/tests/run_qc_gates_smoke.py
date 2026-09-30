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

        print("[5] check_done refuses until a FULL vision pass is recorded")
        import os
        import subprocess
        d = tmp / "done"
        d.mkdir()
        deck = d / "final_deck.pptx"
        prs3 = Presentation()
        for _ in range(3):
            prs3.slides.add_slide(prs3.slide_layouts[6])
        prs3.save(str(deck))

        def _done() -> tuple[int, str]:
            r = subprocess.run(
                [sys.executable, str(SCRIPTS / "check_done.py"), "--out", str(d)],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": str(SCRIPTS)})
            return r.returncode, r.stdout

        assert _done()[0] == 1, "an empty build must not be deliverable"
        _state.record_prep(d, "h", d); _state.record_review(d)
        _state.record_compile(d); _state.record_qc(d, 0, "clean")
        rc, o = _done()
        assert rc == 1 and "no vision pass recorded" in o, o
        _state.record_vision_qc(d, deck, 2, 0)          # partial look
        rc, o = _done()
        assert rc == 1 and "covered 2 of 3" in o, o
        _state.record_vision_qc(d, deck, 3, 1)          # every slide
        assert _done()[0] == 0, "a compiled, clean, fully-reviewed deck IS deliverable"
        _state.record_qc(d, 2, "2 blocking")            # a block re-opens it
        assert _done()[0] == 1, "a blocking QC finding must re-open 'done'"
        print("    ok: no vision pass / partial pass / QC block all refuse; full pass passes")

        print("[6] a deck edited after the vision pass is not deliverable")
        _state.record_qc(d, 0, "clean")
        _state.record_vision_qc(d, deck, 3, 0)
        assert _done()[0] == 0, "precondition: the reviewed deck is deliverable"
        # The ad hoc post-compile edit that broke something every time it was used.
        prs4 = Presentation(str(deck))
        prs4.slides[0].shapes.add_textbox(Inches(1), Inches(1), Inches(2), Inches(1))
        prs4.save(str(deck))
        rc, o = _done()
        assert rc == 1 and "changed since the vision pass" in o, o
        print("    ok: hand-editing the compiled deck re-opens 'done'")

        print("[7] a missing deck is a refusal, not a silent pass")
        d2 = tmp / "done_nodeck"
        d2.mkdir()
        _state.record_prep(d2, "h", d2); _state.record_review(d2)
        _state.record_compile(d2); _state.record_qc(d2, 0, "clean")
        _state.record_vision_qc(d2, d2 / "final_deck.pptx", 3, 0)
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_done.py"), "--out", str(d2)],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS)})
        assert r.returncode == 1 and "nothing to deliver" in r.stdout, r.stdout
        print("    ok: no deck, no delivery")

        print("[8] --all-variations output is recognized as a deliverable")
        d3 = tmp / "done_allvar"
        d3.mkdir()
        allvar = d3 / "final_deck_all_variations.pptx"
        prs5 = Presentation()
        for _ in range(3):
            prs5.slides.add_slide(prs5.slide_layouts[6])
        prs5.save(str(allvar))
        _state.record_prep(d3, "h", d3); _state.record_review(d3)
        _state.record_compile(d3); _state.record_qc(d3, 0, "clean")
        _state.record_vision_qc(d3, allvar, 3, 0)
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_done.py"), "--out", str(d3)],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS)})
        assert r.returncode == 0, (
            "the all-options deck is what 'put every option in one deck' "
            f"produces; it must be checkable: {r.stdout}")
        print("    ok: final_deck_all_variations.pptx resolves without --deck")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
