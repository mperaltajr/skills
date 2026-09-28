#!/usr/bin/env python3
"""Smoke test for the shared full-fidelity text walk (_extract.py).

Both adopt_deck (6b) and refresh_deck (6c) used to walk only `slide.shapes` and
keep shapes where `has_text_frame` was true. That silently dropped every table
cell, every shape nested in a group, and all chart labels. Measured on a probe
slide carrying 8 figures, the old walk recovered 2.

This matters twice over:
  * option 6c ("refresh my recurring/PMO deck") could not see, and therefore
    could not update, the numbers in your tables;
  * anything built on top of extraction (a replicated page's figure ledger)
    would inherit the same blindness and report a clean result over unread text.

Run:  py -3 slide-builder/tests/run_extract_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pptx import Presentation  # noqa: E402
from pptx.chart.data import CategoryChartData  # noqa: E402
from pptx.enum.chart import XL_CHART_TYPE  # noqa: E402
from pptx.util import Inches  # noqa: E402

import _extract  # noqa: E402


def _probe_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    tb = s.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(6), Inches(0.6))
    tb.text_frame.text = "Market reaches $300B by 2027"
    tb2 = s.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(6), Inches(0.5))
    tb2.text_frame.text = "Up 3x versus 2024"
    t = s.shapes.add_table(2, 2, Inches(0.5), Inches(1.7), Inches(4), Inches(1)).table
    t.cell(0, 0).text = "Lead time"; t.cell(0, 1).text = "6-12 months"
    t.cell(1, 0).text = "Capacity";  t.cell(1, 1).text = "sold out"
    g1 = s.shapes.add_textbox(Inches(5), Inches(3), Inches(2), Inches(0.4))
    g1.text_frame.text = "TAM $450B"
    g2 = s.shapes.add_textbox(Inches(5), Inches(3.5), Inches(2), Inches(0.4))
    g2.text_frame.text = "~4x upside"
    s.shapes.add_group_shape([g1, g2])
    cd = CategoryChartData(); cd.categories = ["2024", "2027"]
    cd.add_series("Market", (300.0, 450.0))
    s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                       Inches(0.5), Inches(3.2), Inches(4), Inches(2), cd)
    return s


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="extract_smoke_"))
    try:
        print("[1] every figure is recovered, including tables, groups and charts")
        prs = Presentation()
        slide = _probe_slide(prs)
        surfaces, unreachable = _extract.walk_slide(slide, 1)
        blob = " | ".join(s["text"] for s in surfaces)
        for fig in ("$300B", "3x", "6-12 months", "sold out", "$450B", "~4x", "450"):
            assert fig in blob, f"{fig!r} was not recovered (old walk missed it)"
        kinds = {s["kind"] for s in surfaces}
        assert {"text", "table_cell", "chart_category", "chart_value"} <= kinds, kinds
        assert any(s["addr"].count("/g") for s in surfaces), "grouped shapes not recursed"
        print(f"    ok: {len(surfaces)} surfaces, all 7 figures, kinds={sorted(kinds)}")

        print("[2] chart data is read-only; text surfaces are writable")
        assert all(not s["writable"] for s in surfaces if s["kind"].startswith("chart"))
        assert all(s["writable"] for s in surfaces if s["kind"] in ("text", "table_cell"))
        print("    ok: chart values reported but never offered for rewrite")

        print("[3] addresses round-trip back to a writable text frame")
        cell = next(s for s in surfaces if s["text"] == "6-12 months")
        tf = _extract.resolve_text_frame(slide, cell["addr"])
        assert tf is not None and tf.text == "6-12 months", cell["addr"]
        grouped = next(s for s in surfaces if s["text"] == "~4x upside")
        assert _extract.resolve_text_frame(slide, grouped["addr"]) is not None
        chartish = next(s for s in surfaces if s["kind"] == "chart_value")
        assert _extract.resolve_text_frame(slide, chartish["addr"]) is None, \
            "chart data must not resolve to a writable frame"
        print("    ok: table cell + grouped shape resolve; chart data does not")

        print("[4] refresh_deck (option 6c) now sees and writes table cells")
        deck = tmp / "pmo.pptx"
        prs.save(str(deck))
        env = {**os.environ, "PYTHONPATH": str(SCRIPTS)}
        spec = tmp / "spec.json"
        r = subprocess.run([sys.executable, str(SCRIPTS / "refresh_deck.py"), "spec",
                            str(deck), "--out", str(spec)],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr[-400:]
        d = json.loads(spec.read_text(encoding="utf-8"))
        assert any(f["kind"] == "table_cell" for f in d["fields"]), "no table cells in spec"
        for f in d["fields"]:
            if f["current_text"] == "6-12 months":
                f["new_text"] = "sold out"
        spec.write_text(json.dumps(d), encoding="utf-8")
        out = tmp / "refreshed.pptx"
        r = subprocess.run([sys.executable, str(SCRIPTS / "refresh_deck.py"), "apply",
                            str(deck), str(spec), "--out", str(out)],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr[-400:]
        cells = [c.text for row in Presentation(str(out)).slides[0].shapes[2].table.rows
                 for c in row.cells]
        assert "sold out" in cells, f"table cell write failed: {cells}"
        print("    ok: table cell updated through the spec/apply round trip")

        print("[5] unreadable surfaces are reported, never silently skipped")
        prs2 = Presentation()
        s2 = prs2.slides.add_slide(prs2.slide_layouts[6])
        png = tmp / "x.png"
        png.write_bytes(bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
            "890000000a49444154789c6360000002000100ffff03000006000557bfabd400"
            "00000049454e44ae426082"))
        s2.shapes.add_picture(str(png), Inches(1), Inches(1), Inches(1), Inches(1))
        _surf, unreach = _extract.walk_slide(s2, 1)
        assert unreach and "picture" in unreach[0]["why"], unreach
        print(f"    ok: {unreach[0]['why']}")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
