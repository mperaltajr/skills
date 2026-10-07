#!/usr/bin/env python3
"""Smoke test: sketches are drawn on the template's real background.

Designs were drawn and approved on a hard-coded white canvas, but a template's
master can be a light gray-blue, so a pale panel vanished only in the finished
slide; designers were not given the side margins either (2026-10-06).

On a COPY of Slide Lab's own test template with its master background made a
made-up light gray (the fixture is never changed):
  1. the background is read from the template: the master's color for a
     layout that sets none, a layout's own color where it sets one
  2. registration records it per layout in chrome.yml (background_hex,
     background_kind, body_left_px, body_right_px) and brand.css's canvas is
     the default content layout's background, not #FFFFFF
  3. the designer's _context.md carries --slide-canvas-bg and the side margins;
     an older chrome.yml without these fields gets them from the template
  4. the translator leaves a canvas of the template's color to the template
     (no full-slide rectangle), still draws a canvas of another color, and
     keeps the old behavior for a loose file with no template
  5. a large panel within a few shades of the background raises a
     PALE_FILL_ON_BACKGROUND advisory, and so does a panel designed on white
     in exactly the template's color; a white card, a white card on a white
     canvas, and an outlined pale panel do not
  6. the self-check compares like with like: a design on the gray canvas
     converts with nothing handed to the agent (without the template's color
     on the check's slide, the loose text came out "wrong color" and went to
     the agent)

Run:  py -3 slide-builder/tests/run_template_background_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(HERE))

from lxml import etree  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402

import _paths as _p  # noqa: E402
import run_layout_inheritance_smoke as fixture  # noqa: E402
from _chrome_schema import dump_chrome_yml, load_chrome_yml  # noqa: E402

GRAY = "E9EDF2"          # a made-up light gray master
LAYOUT = "body_canonical_light"
DARK = "cover_dark"


def _gray_master_copy(dst: Path) -> None:
    prs = Presentation(str(fixture.FIXTURE_PPTX))
    csld = prs.slide_masters[0].element.find(qn("p:cSld"))
    old = csld.find(qn("p:bg"))
    if old is not None:
        csld.remove(old)
    bg = etree.Element(qn("p:bg"))
    pr = etree.SubElement(bg, qn("p:bgPr"))
    sf = etree.SubElement(pr, qn("a:solidFill"))
    etree.SubElement(sf, qn("a:srgbClr"), val=GRAY)
    etree.SubElement(pr, qn("a:effectLst"))
    csld.insert(0, bg)
    prs.save(str(dst))


def _register(tpl: Path) -> None:
    """register_fixture, with a default content layout (so brand.css is written for it)."""
    import register_template as rt
    sha = hashlib.sha256(tpl.read_bytes()).hexdigest()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rt._write_outputs(
            tpl, sha, sha[:8], primary_hex="1F2937", primary_slot="dk2",
            accent_hex="F59E0B", accent_slot="lt2", cover_bg_hex="0A1A2E",
            cover_bg_slot="dk2", dark_bg_hex="0A1A2E", dark_bg_slot="dk2",
            font_heading="Arial", font_body="Arial", strip_master_backgrounds=False,
            colors={"dk1": "000000", "lt1": "FFFFFF", "dk2": "1F2937", "lt2": "F59E0B",
                    "accent1": "1F2937", "accent2": "F59E0B"},
            n_master=1, n_layout=len(fixture.TARGET_LAYOUTS),
            default_content_layout=LAYOUT)
        overrides = {name: klass for name, klass, _bg in fixture.TARGET_LAYOUTS}
        spec = rt.extract_chrome_spec(Presentation(str(tpl)), sha8=sha[:8],
                                      classifications_override=overrides)
        dump_chrome_yml(spec, _p.chrome_yml(tpl))


DESIGN = """<!doctype html><html><head><style>
*{box-sizing:border-box} html,body{margin:0;padding:0}
.slide-canvas{width:1280px;height:720px;position:relative;overflow:hidden;background:#{CANVAS};font-family:Arial}
.p{position:absolute;font-size:16px;color:#1A1A1A}
</style></head><body><div class="slide-canvas">
<div data-template-field="title" style="position:absolute;left:60px;top:30px;font-size:28px">A made-up title</div>
<div class="p" data-shape-id="loose-text" style="left:60px;top:140px;width:600px;height:30px">Loose text sitting on the canvas itself</div>
<div class="p" data-shape-id="white-card" style="left:60px;top:200px;width:340px;height:300px;background:#FFFFFF">White card</div>
<div class="p" data-shape-id="pale-panel" style="left:460px;top:200px;width:340px;height:300px;background:#EBEFF4">Pale panel</div>
<div class="p" data-shape-id="outlined-pale" style="left:860px;top:200px;width:340px;height:300px;background:#EBEFF4;border:2px solid #5F5E5A">Outlined pale</div>
</div></body></html>"""


def _plan(page, html: Path, template_bg):
    import translate_html as T
    data = T.extract(page, html, True)
    return T.plan_from_extract(data, True, template_bg)[0]


def _full_slide(plan) -> list:
    return [o for o in plan.ops if o.get("op") == "shape"
            and o.get("w", 0) >= 1279 and o.get("h", 0) >= 719]


def main() -> int:
    if not fixture.FIXTURE_PPTX.exists():
        fixture.build_fixture(fixture.FIXTURE_PPTX)
    tmp = Path(tempfile.mkdtemp(prefix="slidelab_template_bg_"))
    try:
        tpl = tmp / "gray_master.pptx"
        _gray_master_copy(tpl)

        print("[1] the background is read from the template")
        import _template_bg as TB
        f = TB.template_layout_facts(tpl, LAYOUT)
        assert f["background"] == {"hex": GRAY, "kind": "solid", "from": "master"}, f
        assert TB.template_layout_facts(tpl, DARK)["background"]["from"] == "layout"
        assert f["margins"] and f["margins"][0] < f["margins"][1], f
        print(f"    ok: {LAYOUT} #{GRAY} from the master, margins {f['margins']}")

        print("[2] registration records it per layout; brand.css's canvas is the template's")
        _register(tpl)
        lc = load_chrome_yml(_p.chrome_yml(tpl)).layouts[LAYOUT]
        assert (lc.background_hex, lc.background_kind) == (GRAY, "solid"), lc
        assert (lc.body_left_px, lc.body_right_px) == tuple(f["margins"]), lc
        dark = load_chrome_yml(_p.chrome_yml(tpl)).layouts[DARK]
        assert dark.background_hex not in (None, GRAY), dark.background_hex
        css = _p.brand_css(tpl).read_text(encoding="utf-8")
        assert f"--slide-canvas-bg:      #{GRAY};" in css, css
        print("    ok")

        print("[3] the designer's context carries the background and margins")
        import build_deck as BD
        BD._CHROME_SPEC_CACHE.clear()
        block = BD._body_geometry_block(tpl, LAYOUT)
        assert f"--slide-canvas-bg: #{GRAY};" in block, block
        assert f"--body-left: {f['margins'][0]}px;" in block, block
        assert f"--body-right: {f['margins'][1]}px;" in block, block
        import yaml
        cy = _p.chrome_yml(tpl)
        raw = yaml.safe_load(cy.read_text(encoding="utf-8"))
        for d in raw["layouts"].values():
            for k in ("background_hex", "background_kind", "body_left_px", "body_right_px"):
                d.pop(k, None)
        cy.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
        BD._CHROME_SPEC_CACHE.clear()
        block_old = BD._body_geometry_block(tpl, LAYOUT)
        assert f"--slide-canvas-bg: #{GRAY};" in block_old, "older registration lost it"
        print("    ok (also from an older chrome.yml)")

        print("[4] the translator leaves the template's own background to the template")
        from playwright.sync_api import sync_playwright
        from _browser import launch
        on_gray = tmp / "option_B.html"
        on_gray.write_text(DESIGN.replace("{CANVAS}", GRAY), encoding="utf-8")
        on_dark = tmp / "dark.html"
        on_dark.write_text(DESIGN.replace("{CANVAS}", "0B1F33"), encoding="utf-8")
        # designed on white, with a panel in exactly the template's color
        on_white = tmp / "white.html"
        on_white.write_text(DESIGN.replace("{CANVAS}", "FFFFFF").replace("#EBEFF4", f"#{GRAY}"),
                            encoding="utf-8")
        with sync_playwright() as pw:
            br = launch(pw)
            page = br.new_page(viewport={"width": 1280, "height": 720})
            gray_plan = _plan(page, on_gray, GRAY)
            loose_plan = _plan(page, on_gray, None)
            dark_plan = _plan(page, on_dark, GRAY)
            white_plan = _plan(page, on_white, GRAY)
            white_loose = _plan(page, on_white, None)
            br.close()
        assert _full_slide(gray_plan) == [] and gray_plan.canvas_bg == GRAY, _full_slide(gray_plan)
        assert gray_plan.counts.get("canvas_left_to_template") == 1
        assert len(_full_slide(dark_plan)) == 1, "a canvas of another color is the design's own"
        assert len(_full_slide(loose_plan)) == 1, "a loose file keeps the old behavior"
        print("    ok")

        print("[5] a pale panel on the background raises an advisory")
        pale = [w for w in gray_plan.warnings if w["code"] == "PALE_FILL_ON_BACKGROUND"]
        assert len(pale) == 1 and "pale-panel" in pale[0]["detail"], gray_plan.warnings
        assert "template's background" in pale[0]["detail"], pale
        # a panel designed on white in exactly the template's color vanishes in the deck
        pw_ = [w for w in white_plan.warnings if w["code"] == "PALE_FILL_ON_BACKGROUND"]
        assert len(pw_) == 1 and "pale-panel" in pw_[0]["detail"], white_plan.warnings
        # a white card on a white canvas is deliberate: no advisory
        assert not [w for w in white_loose.warnings if w["code"] == "PALE_FILL_ON_BACKGROUND"
                    and "white-card" in w["detail"]], white_loose.warnings
        print(f"    ok: {pale[0]['detail'][:90]}...")

        print("[6] the self-check compares like with like")
        import translate_html as T
        emit = tmp / "emit"
        emit.mkdir()
        rep = T.translate_many([(on_gray, emit, "B", True, None, GRAY)])[0]
        if any(w["code"] == "SELF_CHECK_SKIPPED" for w in rep["warnings"]):
            print("    skipped: no renderer on this machine")
        else:
            assert rep["self_check"]["ran"] and rep["self_check"]["fired"] == [], rep["self_check"]
            assert not rep["needs_agent"], rep["fallback"]
            print("    ok: nothing handed to the agent")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
