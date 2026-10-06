#!/usr/bin/env python3
"""Smoke test: the type scale (body 12pt default, 10.5pt floor, at most 3
body sizes, exceptions 9pt+).

  1. a slide that keeps to the scale passes: 12/14/16 body, a 40pt hero
     figure, 9pt chart labels named chart-..., a 9pt source line
  2. body text at 10pt is a finding; at 10.5pt it is only a note (below the
     12pt default but allowed)
  3. a fourth body size is flagged
  4. a chart label or source under 9pt is flagged
  5. slide-qc's hygiene check reports them as Major "text size" findings
  6. the FINAL-CHECK.html block lists the slide

Run:  py -3 slide-builder/tests/run_type_scale_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(ROOT / "slide-qc" / "scripts"))
import type_scale  # noqa: E402
import check_pptx_hygiene  # noqa: E402


def _box(slide, name, text, pt, top=1.0):
    tb = slide.shapes.add_textbox(Inches(1), Inches(top), Inches(6), Inches(0.5))
    tb.name = name
    run = tb.text_frame.paragraphs[0].add_run()
    run.text = text
    run.font.size = Pt(pt)
    return tb


def _deck(path, slides):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    for boxes in slides:
        s = prs.slides.add_slide(prs.slide_layouts[6])
        for b in boxes:
            _box(s, *b)
    prs.save(str(path))


GOOD = [("heading-1", "Vietnam clears both bars", 16), ("key-1", "$1.2B by 2030", 14),
        ("detail-1", "Partners 4, distribution 4, rules 4", 12), ("hero", "60%", 40),
        ("chart-ylab-200", "200", 9), ("chart-legend-vn", "Vietnam", 9),
        ("src", "Source: illustrative data, not real", 9, 6.9)]


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        deck = Path(td) / "t.pptx"
        _deck(deck, [
            GOOD,
            GOOD + [("cell-1", "Fails on size", 10)],
            GOOD + [("big-1", "Gate 2 at month 12", 18)],
            GOOD + [("chart-xlab-2024", "2024", 8), ("footnote-1", "1. Estimate", 8, 6.95)],
        ])
        res = dict(type_scale.check_pptx(deck))

        print("[1] a slide on the scale passes")
        assert res[1] == [], res[1]
        print("    ok")

        print("[2] body at 10pt is a finding; at 10.5pt only a note")
        assert any("under 10.5 pt" in p for p in res[2]), res[2]
        with tempfile.TemporaryDirectory() as td2:
            d2 = Path(td2) / "n.pptx"
            _deck(d2, [[g for g in GOOD if g[0] != "detail-1"]
                       + [("cell-1", "Fails on size", 10.5)]])
            (_, probs, nts), = type_scale.check_pptx(d2, with_notes=True)
            assert probs == [] and nts and "below the 12 pt default" in nts[0], (probs, nts)
            qc = check_pptx_hygiene.run_all_checks(d2)["violations"]
            sev = {v["severity"] for v in qc if v.get("category") == "text size"}
            assert sev == {"Advisory"}, qc
        print("    ok")

        print("[3] a fourth body size is flagged")
        assert any("4 body text sizes" in p for p in res[3]), res[3]
        print("    ok")

        print("[4] chart label or footnote under 9pt is flagged")
        assert any("under 9 pt" in p for p in res[4]), res[4]
        assert not any("under 10.5 pt" in p for p in res[4]), res[4]
        print("    ok")

        print("[5] slide-qc reports Major text-size findings")
        out = check_pptx_hygiene.run_all_checks(deck)
        ts = [v for v in out["violations"] if v.get("category") == "text size"
              and v["severity"] == "Major"]
        assert ts and all(v["severity"] == "Major" for v in ts), ts
        assert {v["slide"] for v in ts} == {2, 3, 4}, ts
        print("    ok")

        print("[6] the FINAL-CHECK block lists the slide")
        block = type_scale.html_block([("Slide 1", res[1]), ("Slide 2", res[2])])
        assert "Slide 2" in block and "Slide 1" not in block, block
        assert "ok" in type_scale.html_block([("Slide 1", [])])
        print("    ok")
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
