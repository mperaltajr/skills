#!/usr/bin/env python3
"""Smoke test: translate_html.py turns a design into native PowerPoint the way
the agent's rules say, and its self-check works.

One small design exercises the rules that went wrong in real decks:
  - weight 800 is drawn by Chrome with the family's heavy face (Arial Black),
    not Arial Bold: the numerals came out thin and ~7px low
  - two pieces set side by side with a margin ("$1.2B" "to" "$4.8B", one
    32px and one 16px) keep their gap; they used to run together
  - text hidden behind a band in the design is not drawn; text that is merely
    under a transparent container is drawn (it used to be skipped)
  - lines and connectors carry no theme shadow (effectRef idx="0")
  - a linear gradient is drawn as a native gradient (stops and direction);
    a radial one is flattened to one color
  - a curved SVG path is left for the agent (FALLBACK_PENDING), not guessed
  - the report has its fixed schema, the self-check ran and found nothing on
    this clean design, and a deliberately broken plan does trip it
  - weight mapping: 400 regular, 600/700 bold, 800+ heavy face when installed

Needs Playwright's Chromium and LibreOffice, like the other render smokes.
Run:  py -3 slide-builder/tests/run_translate_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(SKILL.parent / "slide-qc" / "scripts"))

import translate_html as T  # noqa: E402
import translate_alarm as A  # noqa: E402

DESIGN = """<!doctype html><html><head><meta charset="utf-8"><style>
body { margin: 0; }
.slide-canvas { position: relative; width: 1280px; height: 720px; background: #fff;
  font-family: Arial, sans-serif; color: #1a1a1a; overflow: hidden; }
.title { position: absolute; left: 53px; top: 40px; font-size: 36px; font-weight: 700; }
.num { position: absolute; left: 60px; top: 150px; font-size: 64px; font-weight: 800;
  color: #c9d2dc; line-height: 0.9; letter-spacing: -2px; }
.figs { position: absolute; left: 220px; top: 160px; white-space: nowrap; }
.figs .a { font-size: 32px; font-weight: 700; color: #1f4e79; }
.figs .to { font-size: 16px; color: #777; margin: 0 8px; }
.figs .b { font-size: 32px; font-weight: 700; color: #2e75b6; }
.card { position: absolute; left: 53px; top: 260px; width: 360px; height: 160px;
  background: #f2f4f7; border: 1px solid #d3d1c7; border-radius: 8px; }
.card p { margin: 0; position: absolute; left: 20px; top: 20px; width: 320px;
  font-size: 15px; line-height: 1.4; }
.band { position: absolute; left: 500px; top: 260px; width: 700px; height: 60px;
  background: #0b1f33; }
.hidden { position: absolute; left: 520px; top: 275px; font-size: 18px; z-index: 0; }
.band-text { position: absolute; left: 520px; top: 278px; font-size: 18px; color: #fff; }
.overlay { position: absolute; left: 500px; top: 340px; width: 700px; height: 80px; }
.under { position: absolute; left: 520px; top: 360px; font-size: 16px; }
svg { position: absolute; left: 53px; top: 460px; }
.gbar { position: absolute; left: 700px; top: 450px; width: 400px; height: 20px;
  background: linear-gradient(90deg, rgb(91, 45, 144) 0%, rgb(255, 102, 0) 100%); }
.rbar { position: absolute; left: 700px; top: 490px; width: 400px; height: 20px;
  background: radial-gradient(rgb(91, 45, 144), rgb(255, 102, 0)); }
</style></head><body><div class="slide-canvas">
<div class="title" data-template-field="title">Smoke title</div>
<div class="num" data-shape-id="num-01">01</div>
<div class="figs" data-shape-id="figs"><span class="a">$1.2B</span><span class="to">to</span><span class="b">$4.8B</span></div>
<div class="card" data-shape-id="card"><p data-shape-id="card-body">Three service lines drawn from one shared base so every unit of work is used.</p></div>
<div class="hidden" data-shape-id="hidden-text">This text is behind the band</div>
<div class="band" data-shape-id="band"></div>
<div class="band-text" data-shape-id="band-text">Shown on the band</div>
<div class="under" data-shape-id="under-text">Visible under a clear container</div>
<div class="overlay" data-shape-id="overlay"></div>
<div class="gbar" data-shape-id="gbar"></div>
<div class="rbar" data-shape-id="rbar"></div>
<svg width="600" height="40" viewBox="0 0 600 40">
  <line x1="0" y1="20" x2="580" y2="20" stroke="#1f4e79" stroke-width="2"/>
</svg>
<svg width="600" height="120" viewBox="0 0 600 120" style="top: 520px;">
  <path d="M0 100 C 150 40, 300 40, 580 100" stroke="#2e75b6" stroke-width="3" fill="none"/>
</svg>
</div></body></html>"""


WEIGHTS = """<!doctype html><html><head><meta charset="utf-8"><style>
body { margin: 0; }
.slide-canvas { position: relative; width: 1280px; height: 720px; background: #fff;
  font-family: Arial, sans-serif; color: #1a1a1a; }
p { position: absolute; left: 80px; margin: 0; font-size: 28px; white-space: nowrap; }
</style></head><body><div class="slide-canvas">
<p data-shape-id="w400" style="top:120px;font-weight:400">Weight four hundred</p>
<p data-shape-id="w600" style="top:200px;font-weight:600">Weight six hundred</p>
<p data-shape-id="w700" style="top:280px;font-weight:700">Weight seven hundred</p>
<p data-shape-id="w800" style="top:360px;font-weight:800">Weight eight hundred</p>
<p data-shape-id="w900" style="top:440px;font-weight:900">Weight nine hundred</p>
</div></body></html>"""


def _run_props(shape):
    from pptx.oxml.ns import qn
    out = []
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            rpr = r._r.find(qn("a:rPr"))
            lat = rpr.find(qn("a:latin")) if rpr is not None else None
            out.append((lat.get("typeface") if lat is not None else None,
                        rpr.get("b") if rpr is not None else None))
    return out


def _weights_survive_theme() -> None:
    """Weights 600-900 come out bold on the theme font after finalize's theme
    pass (2026-10-06: weight 800 shipped regular, in PowerPoint too)."""
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from twins.client_theme import apply_theme_to_shape_xml
    print("[weights] 600/700/800/900 stay bold through the theme font swap")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        html = td / "option_W.html"
        html.write_text(WEIGHTS, encoding="utf-8")
        rep = T.translate_many([(html, td, "W", True)])[0]
        assert not rep["fallback"], f"plain text went to the agent: {rep['fallback']}"
        r = subprocess.run([sys.executable, str(td / "option_W_native.py")], cwd=str(td),
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-800:]
        prs = Presentation(str(td / "option_W_native.pptx"))
        slide = prs.slides[0]
        # the template's theme font differs from the design's, as on a client template
        for sh in list(slide.shapes):
            apply_theme_to_shape_xml(sh.element, {}, major_font="Georgia",
                                     minor_font="Calibri")
        by = {sh.name: _run_props(sh) for sh in slide.shapes if sh.has_text_frame}
        for w in ("w600", "w700", "w800", "w900"):
            assert by[w] and all(f == "+mn-lt" and b == "1" for f, b in by[w]), (w, by[w])
        assert all(b != "1" for _f, b in by["w400"]), by["w400"]
        prs.save(str(td / "themed.pptx"))

        # backstop: a deck built the other way (a heavy face named as its own
        # font, bold off) keeps its weight when the theme swaps the name
        prs2 = Presentation()
        s2 = prs2.slides.add_slide(prs2.slide_layouts[6])
        faces = {"black": "Arial Black", "semi": "Smoke Sans Semibold",
                 "xbold": "Smoke Sans ExtraBold", "medium": "Smoke Sans Medium",
                 "light": "Smoke Sans Light", "theme": "Calibri"}
        for i, (name, face) in enumerate(faces.items()):
            tb = s2.shapes.add_textbox(Inches(1), Inches(0.5 + i * 0.8), Inches(6), Inches(0.6))
            tb.name = name
            run = tb.text_frame.paragraphs[0].add_run()
            run.text = f"Face {name}"
            run.font.name = face
            run.font.bold = False
            run.font.size = Pt(20)
        for sh in list(s2.shapes):
            apply_theme_to_shape_xml(sh.element, {}, major_font="Georgia",
                                     minor_font="Calibri")
        by2 = {sh.name: _run_props(sh)[0] for sh in s2.shapes}
        for name in ("black", "semi", "xbold"):
            assert by2[name] == ("+mn-lt", "1"), (name, by2[name])
        for name in ("medium", "light", "theme"):
            assert by2[name][1] != "1", (name, by2[name])
    print("    ok: bold on the theme font for 600-900; Medium, Light and 400 stay regular")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        html = td / "option_A.html"
        html.write_text(DESIGN, encoding="utf-8")
        rep = T.translate_many([(html, td, "A", True)])[0]

        # report schema
        for key in ("translator", "css_kill_list_applied", "warnings", "counts", "fallback",
                    "self_check", "needs_agent", "template_fields", "visible_text_chars"):
            assert key in rep, f"report is missing {key!r}"
        assert rep["template_fields"].get("title") == "Smoke title", rep["template_fields"]

        plan = json.loads((td / "option_A_native.plan.json").read_text(encoding="utf-8"))
        ops = plan["ops"]
        texts = {o.get("name"): o for o in ops if o["op"] == "text"}

        # weight 800 -> the base family with bold on (a heavy face's own name
        # does not survive finalize's theme font swap)
        num = texts["num-01"]["paragraphs"][0][0]
        assert num["font"] == "Arial" and num["bold"] is True, num
        # gap between side-by-side pieces kept
        figs = "".join(r["t"] for p in texts["figs"]["paragraphs"] for r in p)
        assert "$1.2B to" in figs.replace("  ", " ") and "to $4.8B" in figs.replace("  ", " "), figs
        # hidden text skipped, text under a transparent container kept
        assert "hidden-text" not in texts, "text hidden behind the band was drawn"
        assert any(w["code"] == "TEXT_HIDDEN_IN_DESIGN" for w in rep["warnings"])
        assert "under-text" in texts, "text under a transparent container was skipped"
        # linear gradient drawn natively, radial flattened
        gbar = next(o for o in ops if o.get("name") == "gbar")
        assert gbar.get("gradient") and gbar["gradient"]["angle"] == 90.0, gbar
        assert [s_[1] for s_ in gbar["gradient"]["stops"]] == ["5B2D90", "FF6600"], gbar
        rbar = next(o for o in ops if o.get("name") == "rbar")
        assert not rbar.get("gradient") and rbar["fill"], rbar
        assert rep["css_kill_list_applied"]["gradients_flattened"] == 1, rep["css_kill_list_applied"]
        # the curve goes to the agent, the straight line is drawn
        assert any(f["kind"] == "svg" or "curve" in (f.get("reason") or "") for f in rep["fallback"]), \
            rep["fallback"]
        assert any(o["op"] == "connector" for o in ops), "the straight SVG line was not drawn"
        head = (td / "option_A_native.py").read_text(encoding="utf-8")
        assert "# FALLBACK_PENDING:" in head

        # the self-check ran and found nothing else on this clean design
        assert rep["self_check"]["ran"], rep["self_check"]
        assert not rep["self_check"]["fired"], rep["self_check"]

        # the script builds; no theme shadow on anything; the file opens
        r = subprocess.run([sys.executable, str(td / "option_A_native.py")], cwd=str(td),
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-800:]
        from pptx import Presentation
        from pptx.oxml.ns import qn
        from pptx_openability import check_openability
        prs = Presentation(str(td / "option_A_native.pptx"))
        assert not check_openability(prs), check_openability(prs)
        g_sh = next(sh for sh in prs.slides[0].shapes if sh.name == "gbar")
        gf = g_sh._element.spPr.find(qn("a:gradFill"))
        assert gf is not None and len(gf.find(qn("a:gsLst"))) == 2, "gradient not native"
        assert gf.find(qn("a:lin")).get("ang") == "0", "90deg (left to right) must be ang 0"
        for sh in prs.slides[0].shapes:
            eff = sh._element.find(".//" + qn("a:effectRef"))
            assert eff is None or eff.get("idx") == "0", f"{sh.name} keeps the theme shadow"

        # a broken translation trips the self-check
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            page = br.new_page(viewport={"width": 1280, "height": 720})
            data = T.extract(page, html, True)
            br.close()
        good, _ = T.plan_from_extract(data, True)
        bad = copy.deepcopy(good)
        target = next(i for i, o in enumerate(bad.ops) if o.get("name") == "card-body")
        bad.ops[target]["x"] += 14
        T.self_check([(bad, data)])
        assert any(f["kind"] == "self-check" and f["id"] == "card-body" for f in bad.fallbacks), \
            bad.self_check

    # weight mapping: 600 and up is the base family + bold, never a heavy face
    assert T._face("Arial", "400") == ("Arial", False)
    assert T._face("Arial", "600") == ("Arial", True)
    assert T._face("Arial", "700") == ("Arial", True)
    assert T._face('"Arial", sans-serif', "800") == ("Arial", True)
    assert T._face('"Arial", sans-serif', "900") == ("Arial", True)
    assert T._face("Calibri", "800")[1] is True   # no heavy face installed: bold
    # a family with its own Semibold face (a made-up family, so the test does
    # not depend on what is installed)
    saved = T._FACES
    try:
        T._FACES = dict(T._face_table())
        T._FACES["smoke sans"] = [
            {"path": "", "weight": 400, "width": 5, "italic": False,
             "ppt_name": "Smoke Sans", "ppt_bold": False},
            {"path": "", "weight": 500, "width": 5, "italic": False,
             "ppt_name": "Smoke Sans Medium", "ppt_bold": False},
            {"path": "", "weight": 600, "width": 5, "italic": False,
             "ppt_name": "Smoke Sans Semibold", "ppt_bold": False},
            {"path": "", "weight": 700, "width": 5, "italic": False,
             "ppt_name": "Smoke Sans", "ppt_bold": True}]
        assert T._face("Smoke Sans", "600") == ("Smoke Sans", True), T._face("Smoke Sans", "600")
        assert T._face("Smoke Sans", "500") == ("Smoke Sans Medium", False)
    finally:
        T._FACES = saved

    _weights_survive_theme()

    # alarm limits are the calibrated ones (a change here needs a re-run of
    # translate_alarm_calibrate.py and translate_alarm_seeded.py)
    assert A.SCALE_LIMIT == 0.04 and A.TEXT_SHIFT_X == 3.0 and A.TEXT_SHIFT_Y == 4.0

    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
