#!/usr/bin/env python3
"""Smoke test: library icons show on the sketch and land on the finished slide.

Before 2026-10-08 a sketch's `<i data-icon-name="gear">` rendered as a blank
gap on the review page, and the translator dropped it from the editable slide
without a word. This checks, on a fictional sketch with a known icon, an icon
written as `<img src="icons/x.svg">` on a dark card, and an unknown name:

  1. the shipped SVG previews cover the library and stay a reasonable size,
     and every name on the checked list has one;
  2. render_html draws icon pixels in each icon's box, in the designer's
     color (white on the dark card), and a labeled placeholder plus a
     warning for the unknown name;
  3. the translator plans an icon step per icon (none silently dropped), at
     the right box and color, and warns about the unknown name;
  4. the finished slide has the real vector icon (a group named icon-<name>)
     at that box, tinted, with unique shape ids, and a labeled placeholder for
     the unknown name;
  5. translate_html.py --emit creates a missing output folder.

Run:  py -3 slide-builder/tests/run_icons_smoke.py
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
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "scripts"))

import icon_svg  # noqa: E402

SKETCH = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body{margin:0}
.slide-canvas{width:1280px;height:720px;position:relative;background:#fff;font-family:Arial}
.ic{width:48px;height:48px}
</style></head><body><div class="slide-canvas" data-visual-form="cards">
<div style="position:absolute;left:100px;top:200px;width:300px;height:200px;border:1px solid #ccc;padding:20px">
  <i class="ic" data-icon-name="gear" style="color:#1F3A93"></i>
  <p style="margin:10px 0 0;font-size:16px">Known icon</p></div>
<div style="position:absolute;left:480px;top:200px;width:300px;height:200px;background:#1F3A93;padding:20px;color:#FFFFFF">
  <img src="icons/globe.svg" class="ic" alt="">
  <p style="margin:10px 0 0;font-size:16px">On a dark card</p></div>
<div style="position:absolute;left:860px;top:200px;width:300px;height:200px;border:1px solid #ccc;padding:20px">
  <i class="ic" data-icon-name="no-such-icon" data-icon-color="#C00000"></i>
  <p style="margin:10px 0 0;font-size:16px">Unknown icon</p></div>
</div></body></html>
"""
# Each icon's 48 px box: card left/top + 20 px padding (+1 px border).
BOX = {"gear": (121, 221), "globe": (500, 220), "no-such-icon": (881, 221)}


def run(*args):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "SLIDE_LAB_NO_OPEN": "1"}
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True,
                          env=env, encoding="utf-8", errors="replace")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="icons_smoke_"))
    try:
        print("[1] previews ship for the library; the checked list is covered")
        xml = len(list(icon_svg.ICONS.glob("*.xml")))
        svgs = list(icon_svg.SVG_DIR.glob("*.svg"))
        assert len(svgs) >= xml - 3, (len(svgs), xml)
        size = sum(p.stat().st_size for p in svgs)
        assert size < 4_000_000, f"previews are {size / 1e6:.1f} MB"
        ck = icon_svg.checked()
        assert len(ck) >= 30, len(ck)
        for name in ck:
            assert icon_svg.status(name) == "checked", name
        assert icon_svg.status("no-such-icon") == "unknown"
        # The preview is the slide's geometry: converting again gives the same file.
        assert icon_svg.xml_to_svg(icon_svg.ICONS / "gear.xml") == icon_svg.svg_for("gear")
        print(f"    ok: {len(svgs)} previews, {size / 1e6:.1f} MB; {len(ck)} checked names")

        print("[2] the sketch render draws the icons, in color, and marks the unknown one")
        html = tmp / "option_A.html"
        html.write_text(SKETCH, encoding="utf-8")
        png = tmp / "option_A.sketch.png"
        r = run(SKILL / "scripts" / "render_html.py", html, png)
        assert r.returncode == 0, r.stderr[-800:]
        assert "ICON_UNKNOWN" in r.stderr and "no-such-icon" in r.stderr, r.stderr
        from PIL import Image
        im = Image.open(png).convert("RGB")

        def pixels(name, test):
            x0, y0 = BOX[name]
            return sum(1 for x in range(x0, x0 + 48) for y in range(y0, y0 + 48)
                       if test(im.getpixel((x, y))))
        blue = pixels("gear", lambda p: p[2] > 100 and p[0] < 90 and p[1] < 110)
        white = pixels("globe", lambda p: min(p) > 200)
        grey = pixels("no-such-icon", lambda p: abs(p[0] - p[2]) < 20 and 100 < p[0] < 200)
        assert blue > 80, f"gear box has {blue} icon pixels"
        assert white > 80, f"globe box on the dark card has {white} white pixels"
        assert grey > 20, f"unknown icon box has {grey} placeholder pixels"
        print(f"    ok: {blue} / {white} / {grey} icon pixels")

        print("[3] the translator plans every icon; [5] --emit creates its folder")
        emit = tmp / "not" / "yet" / "there"
        r = run(SKILL / "scripts" / "translate_html.py", "--html", html, "--emit", emit)
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-800:]
        plan = json.loads((emit / "option_A_native.plan.json").read_text(encoding="utf-8"))
        icons = {o["name"]: o for o in plan["ops"] if o["op"] == "icon"}
        assert set(icons) == set(BOX), icons.keys()
        assert icons["gear"]["color"] == "1F3A93" and icons["globe"]["color"] == "FFFFFF"
        assert icons["no-such-icon"]["placeholder"] and not icons["gear"]["placeholder"]
        for name, (x0, y0) in BOX.items():
            o = icons[name]
            assert x0 - 1 <= o["x"] and o["x"] + o["w"] <= x0 + 49, (name, o)
            assert y0 - 1 <= o["y"] and o["y"] + o["h"] <= y0 + 49, (name, o)
        rep = json.loads((emit / "option_A_translation_report.json").read_text(encoding="utf-8"))
        assert any(w["code"] == "ICON_UNKNOWN" for w in rep["warnings"]), rep["warnings"]
        print(f"    ok: {len(icons)} icon steps; warning for the unknown name; folder made")

        print("[4] the finished slide has the vector icons at their boxes, tinted")
        r = run(emit / "option_A_native.py")
        assert r.returncode == 0, r.stderr[-800:]
        from pptx import Presentation
        from pptx.oxml.ns import qn
        prs = Presentation(str(emit / "option_A_native.pptx"))
        slide = prs.slides[0]
        by_name = {s.name: s for s in slide.shapes}
        for name in ("gear", "globe"):
            sh = by_name.get(f"icon-{name}")
            assert sh is not None, f"icon-{name} missing: {list(by_name)}"
            o = icons[name]
            assert abs(sh.left / 9525 - o["x"]) < 1 and abs(sh.width / 9525 - o["w"]) < 1, name
            fills = {c.get("val") for c in sh._element.iter(qn("a:srgbClr"))}
            assert ("#" + o["color"]).lstrip("#") in fills, (name, fills)
        ph = by_name.get("icon-no-such-icon")
        assert ph is not None and "[no-such-icon]" in ph.text_frame.text
        ids = [int(e.get("id")) for e in slide.shapes._spTree.iter(qn("p:cNvPr"))]
        assert len(ids) == len(set(ids)), "duplicate shape ids"
        print("    ok")
        print("SMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
