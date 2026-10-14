#!/usr/bin/env python3
"""Smoke test: a top-anchored text box holds its capitals, and the text does
not move.

One-line boxes get exact spacing 0.8 x the size (translate_html.TIGHT_SINGLE),
which puts the first baseline 0.6 x the size below the box top, so capitals
(about 0.72 x) reached above the box: selected in PowerPoint, its frame cut
through the letters (2026-10-13). The box is now drawn pad_top_px higher and
taller with that much top inset; the spacing and the text's place stay.
Made-up content.

  1. the plan carries pad_top_px on one-line text, a list and svg text; op y
     (where the text is placed) is unchanged
  2. the built box starts pad higher, is pad taller, its top inset is pad,
     in whole 360 EMU steps; tables untouched
  3. caps_above_frame: fires on the same slide drawn without the pad, not
     with it; the translation report carries no TEXT_ABOVE_FRAME
  4. rendered (LibreOffice; PowerPoint too unless SLIDE_LAB_SKIP_POWERPOINT=1),
     every letter's baseline is where it was without the pad (0.5 px)

The selection frame itself can only be judged by eye in PowerPoint.
Needs Playwright's Chromium and LibreOffice.
Run:  py -3 slide-builder/tests/run_text_top_pad_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import copy
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(SKILL.parent / "slide-qc" / "scripts"))

import translate_html as T  # noqa: E402
from twins.html_emit import build  # noqa: E402

DESIGN = """<!doctype html><html><head><meta charset="utf-8"><style>
body { margin: 0; }
.slide-canvas { position: relative; width: 1280px; height: 720px; background: #fff;
  font-family: Arial, sans-serif; color: #1a1a1a; overflow: hidden; }
.a { position: absolute; margin: 0; }
</style></head><body><div class="slide-canvas">
<p class="a" data-shape-id="hero" style="left:60px;top:80px;font-size:64px;font-weight:700">$4.8B</p>
<p class="a" data-shape-id="label" style="left:60px;top:200px;font-size:16px">Total by year five</p>
<p class="a" data-shape-id="body" style="left:400px;top:80px;width:300px;font-size:16px;line-height:22px">
Two lines of body text that wrap inside their box as designed</p>
<ul class="a" data-shape-id="pts" style="left:400px;top:220px;width:300px;font-size:16px;line-height:22px">
<li>First point</li><li>Second point</li></ul>
<table class="a" data-shape-id="tbl" style="left:60px;top:400px;border-collapse:collapse;font-size:14px">
<tr><td style="padding:6px;border-bottom:1px solid #999">Region</td><td style="padding:6px">Units</td></tr>
<tr><td style="padding:6px">North</td><td style="padding:6px">1,240</td></tr></table>
<svg class="a" style="left:800px;top:80px" width="300" height="80"><text x="10" y="40" font-size="28"
 fill="#1f3a5f">Svg label</text></svg>
</div></body></html>"""


def _strip(plan: dict) -> dict:
    p = copy.deepcopy(plan)
    for o in p["ops"]:
        o.pop("pad_top_px", None)
    return p


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        html = td / "option_A.html"
        html.write_text(DESIGN, encoding="utf-8")
        rep = T.translate_many([(html, td, "A", True)], check=False)[0]
        plan = json.loads((td / "option_A_native.plan.json").read_text(encoding="utf-8"))
        by = {o.get("name"): o for o in plan["ops"] if o["op"] == "text"}

        print("[1] the plan carries the pad")
        for name in ("hero", "label", "pts"):
            assert by[name].get("pad_top_px", 0) > 0, (name, by[name].get("pad_top_px"))
        svg_text = [o for o in plan["ops"] if o["op"] == "text" and o.get("name") is None
                    and "Svg" in o["paragraphs"][0][0]["t"]]
        assert svg_text and svg_text[0].get("pad_top_px", 0) > 0, svg_text
        hero = by["hero"]
        r = hero["paragraphs"][0][0]
        S = T._snapped_px(r["size_px"])
        asc, desc, _n = T.vertical_metrics(r["font"], r["bold"])
        need = T.cap_height(r["font"], r["bold"]) * S - T.ppt_first_baseline(
            hero["line_height_px"], S, asc, desc)
        assert need <= hero["pad_top_px"] < need + 360 / 9525 + 1e-6, (need, hero["pad_top_px"])
        print(f"    ok: hero pad {hero['pad_top_px']:.2f} px (capitals {need:.2f} px above)")

        print("[2] the built boxes")
        prs, slide = build(plan)
        shapes = {s.name: s for s in slide.shapes}
        for name in ("hero", "label", "pts"):
            o, sh = by[name], shapes[name]
            pad_emu = int(round(o["pad_top_px"] * 9525))
            assert pad_emu % 360 == 0, pad_emu
            assert sh.text_frame.margin_top == pad_emu, (name, sh.text_frame.margin_top, pad_emu)
            assert int(sh.top) == int(round(o["y"] * 9525)) - pad_emu, name
            assert int(sh.height) == int(round(o["h"] * 9525)) + pad_emu, name
        tbl = shapes["tbl"]
        assert tbl.has_table and tbl.top == int(round(next(o for o in plan["ops"] if o["op"] == "table")["y"] * 9525))
        print("    ok")

        print("[3] the advisory")
        assert T.caps_above_frame(slide) == [], T.caps_above_frame(slide)
        _p0, old = build(_strip(plan))
        hits = T.caps_above_frame(old)
        assert {h["shape"] for h in hits} >= {"hero", "label"}, hits
        assert not any(w["code"] == "TEXT_ABOVE_FRAME" for w in rep["warnings"]), rep["warnings"]
        print(f"    ok: {len(hits)} box(es) flagged without the pad, none with it")

        print("[4] the letters don't move")
        import render_slides
        import translate_alarm as A
        engines = ["libreoffice"]
        if os.environ.get("SLIDE_LAB_SKIP_POWERPOINT") != "1" and render_slides.powerpoint_available():
            engines.append("powerpoint")
        a, b = td / "pad.pptx", td / "nopad.pptx"
        prs.save(str(a))
        build(_strip(plan))[0].save(str(b))
        for eng in engines:
            got = A.render_full([a, b], engine=eng)
            ca, cb = got[0][1], got[1][1]
            assert len(ca) == len(cb) and ca, (eng, len(ca), len(cb))
            worst = max(abs(x.get("y0", x["base"]) - y.get("y0", y["base"])) for x, y in zip(ca, cb))
            assert worst <= 0.5, (eng, worst)
            print(f"    ok: {eng}: {len(ca)} letters, largest baseline move {worst:.2f} px")
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
