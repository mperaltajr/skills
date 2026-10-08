#!/usr/bin/env python3
"""Smoke test: a design's @font-face rule cannot swap an installed font for a file.

A designer pointed the installed brand family at a copied font file that held
its narrow face. The review picture and the conversion were then drawn about a
quarter narrower than the finished slide, and the self-check blamed its own
renderer ("not a defect") (2026-10-08).

On a made-up sketch that points the installed family Arial at a narrow
made-up font file:
  - the browser Slide Lab renders with removes the rule, inline and in a
    linked stylesheet, so text measures as wide as with no rule at all; a
    family that is NOT installed keeps its @font-face rule
  - the review render (render_html.py) prints the warning, and its picture
    matches the picture of the same design without the rule
  - the conversion (translate_html.py) records FONT_FACE_REMOVED and gives no
    RENDER_FONT_RATIO warning
  - the RENDER_FONT_RATIO wording: a design issue when the font is installed,
    a stand-in when it is not

Needs Playwright's Chromium and LibreOffice, like the other render smokes.
Run:  py -3 slide-builder/tests/run_font_face_rule_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(SKILL.parent / "slide-qc" / "scripts"))
sys.path.insert(0, str(HERE))

from _fake_fonts import make_font  # noqa: E402

PAGE = """<!doctype html><html><head><meta charset="utf-8">{head}
<style>
html,body{{margin:0;padding:0}}
.slide-canvas{{position:relative;width:1280px;height:720px;background:#ffffff;overflow:hidden}}
.t{{position:absolute;left:80px;font-family:{family};font-size:24px;color:#1a1a2e;white-space:nowrap}}
</style></head><body><div class="slide-canvas">
<div class="t" id="t1" data-shape-id="label-1" style="top:120px">Quarterly revenue grew across every region</div>
<div class="t" id="t2" data-shape-id="label-2" style="top:200px">Operating margin held steady through the year</div>
<div class="t" id="t3" data-shape-id="label-3" style="top:280px">New customers came mostly from referrals</div>
<div class="t" id="t4" data-shape-id="label-4" style="top:360px">Costs fell after the second quarter review</div>
</div></body></html>"""

RULE = '<style>@font-face{font-family:"__FAM__";src:url("narrow.ttf") format("truetype");}</style>'


def _widths(page, html: Path) -> list[float]:
    page.goto(html.resolve().as_uri())
    page.wait_for_load_state("load")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(100)
    return page.evaluate("() => [1,2,3,4].map(i => document.getElementById('t'+i)"
                         ".getBoundingClientRect().width)")


def main() -> int:
    from _chrome_schema import installed_families
    if "arial" not in installed_families():
        print("Arial is not installed on this computer; nothing to test here.")
        print("\nSMOKE PASSED.")
        return 0
    from playwright.sync_api import sync_playwright
    from _browser import launch
    import translate_html as T
    import translate_alarm as A

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        make_font(td / "narrow.ttf", family="Fict Narrow", width=3, scale=0.6)
        clean = td / "clean.html"
        clean.write_text(PAGE.format(head="", family="Arial"), encoding="utf-8")
        inline = td / "option_A.html"
        inline.write_text(PAGE.format(head=RULE.replace("__FAM__", "Arial"), family="Arial"),
                          encoding="utf-8")
        (td / "fonts.css").write_text(
            '@font-face{font-family:"Arial";src:url("narrow.ttf");}', encoding="utf-8")
        linked = td / "linked.html"
        linked.write_text(PAGE.format(head='<link rel="stylesheet" href="fonts.css">',
                                      family="Arial"), encoding="utf-8")
        foreign = td / "foreign.html"
        foreign.write_text(PAGE.format(head=RULE.replace("__FAM__", "Fict Narrow"),
                                       family='"Fict Narrow"'), encoding="utf-8")

        print("[1] the rendering browser removes the rule for an installed font")
        with sync_playwright() as pw:
            b = launch(pw)
            page = b.new_page(viewport={"width": 1280, "height": 720})
            w_clean = _widths(page, clean)
            w_inline = _widths(page, inline)
            removed = page.evaluate("() => window.__slidelabFontFaceRemoved")
            w_linked = _widths(page, linked)
            removed_l = page.evaluate("() => window.__slidelabFontFaceRemoved")
            w_foreign = _widths(page, foreign)
            kept = page.evaluate("() => window.__slidelabFontFaceRemoved")
            b.close()
        for a, c in zip(w_inline + w_linked, w_clean + w_clean):
            assert abs(a - c) < 1.0, (w_inline, w_linked, w_clean)
        assert removed == ["arial"] and removed_l == ["arial"], (removed, removed_l)
        assert kept == [], kept
        assert all(f < 0.8 * c for f, c in zip(w_foreign, w_clean)), (w_foreign, w_clean)
        print(f"    ok: widths {w_inline[0]:.0f}px with the rule = {w_clean[0]:.0f}px without; "
              f"the narrow file alone draws {w_foreign[0]:.0f}px")

        print("[2] the review render prints the warning and matches the clean design")
        r = subprocess.run([sys.executable, str(SKILL / "scripts" / "render_html.py"),
                            str(inline), str(td / "option_A.sketch.png")],
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr[-800:]
        assert "@font-face" in r.stderr and "'arial'" in r.stderr, r.stderr
        r2 = subprocess.run([sys.executable, str(SKILL / "scripts" / "render_html.py"),
                             str(clean), str(td / "clean.png")],
                            capture_output=True, text=True, timeout=300)
        assert r2.returncode == 0, r2.stderr[-800:]
        import numpy as np
        a = A.load_rgb(str(td / "option_A.sketch.png"))
        c = A.load_rgb(str(td / "clean.png"))
        diff = float(np.abs(a - c).max())
        assert diff < 1.0, f"review picture differs from the clean design (max {diff})"
        print("    ok: same picture as the design without the rule")

        print("[3] the conversion records the removal and gives no font-ratio warning")
        rep = T.translate_many([(inline, td, "A", True)])[0]
        codes = [w["code"] for w in rep["warnings"]]
        assert "FONT_FACE_REMOVED" in codes, codes
        assert "RENDER_FONT_RATIO" not in codes, rep["warnings"]
        assert rep["self_check"].get("ran"), rep["self_check"]
        assert not rep["fallback"], rep["fallback"]
        print(f"    ok: warnings {sorted(set(codes))}; 0 elements to the agent")

    print("[4] RENDER_FONT_RATIO wording")
    m1 = T.font_ratio_message("Fict Sans", 1.3, installed=True)
    assert "different version of Fict Sans" in m1 and "30% wider" in m1, m1
    assert "not a defect" not in m1 and "design issue" in m1, m1
    m2 = T.font_ratio_message("Fict Sans bold", 1.12, installed=False)
    assert "lacks Fict Sans bold" in m2 and "stand-in 12% wider" in m2, m2
    assert "not judged" in m2, m2
    print("    ok")

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
