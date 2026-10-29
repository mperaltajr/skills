#!/usr/bin/env python3
"""Smoke test: fewer elements go to the translator agent for nothing.

Of 19 elements handed to the agent on three pages of the 10/12 deck only 6
were real gaps: 13 were self-check false alarms (a photo on a card made the
card and its pill "look wrong"; thin arrow glyphs the converter drew right),
and the photos and the straight arrow were things the converter can draw
itself. Made-up content throughout.

  1. agent areas left out of the self-check: a card holding a picture the
     agent draws (a filtered one) is not handed over
  2. native pictures: a round photo cropped from a wide picture is ONE
     picture shape, an oval, cropped as the browser showed it; a web
     address or a filter stays with the agent
  3. native arrowheads: a straight line with a triangle marker is a line
     with a PowerPoint arrowhead (tail at its end, head at its start), its
     tip where the design's tip is; arrow_ends reads it; a head far bigger
     than PowerPoint's largest is a filled triangle; a marker in another
     color, or on a curve, stays with the agent
  4. thin letters: a lighter render of the same color passes, another
     color still fails
  5. short arrows (15 px, 10 px heads, 2 px line; 10/26 deck, page 7) rendered
     with the default renderer: native, none handed to the agent; one
     recolored in the slide still fires "color"

Needs Playwright's Chromium and LibreOffice (the self-check renders with
LibreOffice here).
Run:  py -3 slide-builder/tests/run_native_pictures_arrows_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(SKILL.parent / "slide-qc" / "scripts"))

import numpy as np  # noqa: E402
import translate_alarm as A  # noqa: E402
import translate_html as T  # noqa: E402
from twins.html_emit import build  # noqa: E402

HEAD = """<!doctype html><html><head><meta charset="utf-8"><style>
body { margin: 0; }
.slide-canvas { position: relative; width: 1280px; height: 720px; background: #eef2f6;
  font-family: Arial, sans-serif; color: #1a1a1a; overflow: hidden; }
.a { position: absolute; margin: 0; }
.card { position: absolute; background: #fff; border-top: 3px solid #0B1F33; }
.pill { position: absolute; background: #2f5d8a; color: #fff; font-size: 12px; font-weight: 700;
  padding: 2px 8px; border-radius: 10px; }
</style></head><body><div class="slide-canvas">
"""
TAIL = "</div></body></html>"


def _extract(html: Path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        from _browser import launch
        br = launch(pw)
        page = br.new_page(viewport={"width": 1280, "height": 720})
        data = T.extract(page, html, True)
        br.close()
    return data


def main() -> int:
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # a 200x100 picture: left quarter red, middle half green, right quarter blue
        pic = np.zeros((100, 200, 3), dtype=np.uint8)
        pic[:, :50] = (200, 40, 40)
        pic[:, 50:150] = (40, 160, 70)
        pic[:, 150:] = (40, 60, 200)
        Image.fromarray(pic).save(td / "wide.png")
        uri = (td / "wide.png").as_uri()

        body = (
            # 1 + 2: a card with a round photo and a pill over it, and a card
            # with a filtered (agent) photo and a pill over it
            '<div class="card" data-shape-id="card-a" style="left:60px;top:120px;width:300px;height:160px"></div>'
            f'<img class="a" data-shape-id="photo-a" src="{uri}" style="left:76px;top:140px;width:100px;'
            'height:100px;border-radius:50%;object-fit:cover">'
            '<div class="pill" data-shape-id="pill-a" style="left:70px;top:226px">25+ years</div>'
            '<div class="a" data-shape-id="name-a" style="left:190px;top:150px;font-size:16px;font-weight:700">Sam Rivera</div>'
            '<div class="card" data-shape-id="card-b" style="left:400px;top:120px;width:300px;height:160px"></div>'
            f'<img class="a" data-shape-id="photo-b" src="{uri}" style="left:416px;top:140px;width:100px;'
            'height:100px;object-fit:cover;filter:grayscale(1)">'
            '<div class="pill" data-shape-id="pill-b" style="left:410px;top:226px">20+ years</div>'
            '<img class="a" data-shape-id="photo-web" src="https://example.invalid/p.png" '
            'style="left:740px;top:140px;width:60px;height:60px">'
            # 3: arrows
            '<svg class="a" data-shape-id="arrow-up" style="left:0;top:0" width="1280" height="720">'
            '<defs><marker id="m1" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" '
            'markerUnits="userSpaceOnUse"><path d="M0,0 L10,5 L0,10 z" fill="#3A6EA5"/></marker></defs>'
            '<line x1="100" y1="600" x2="500" y2="420" stroke="#3A6EA5" stroke-width="2.5" '
            'marker-end="url(#m1)"/></svg>'
            '<svg class="a" data-shape-id="arrow-back" style="left:0;top:0" width="1280" height="720">'
            '<defs><marker id="m2" markerWidth="10" markerHeight="10" refX="2" refY="5" orient="auto" '
            'markerUnits="userSpaceOnUse"><path d="M10,0 L0,5 L10,10 z" fill="#333"/></marker></defs>'
            '<line x1="700" y1="500" x2="900" y2="500" stroke="#333" stroke-width="2.5" '
            'marker-start="url(#m2)"/></svg>'
            '<svg class="a" data-shape-id="arrow-big" style="left:600px;top:600px" viewBox="0 0 36 20" width="36" height="20">'
            '<defs><marker id="m3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
            '<path d="M0,0 L8,4 L0,8 z" fill="#0B1F33"/></marker></defs>'
            '<line x1="9" y1="10" x2="26" y2="10" stroke="#0B1F33" stroke-width="2" marker-end="url(#m3)"/></svg>'
            '<svg class="a" data-shape-id="arrow-red" style="left:0;top:0" width="1280" height="720">'
            '<defs><marker id="m4" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" '
            'markerUnits="userSpaceOnUse"><path d="M0,0 L10,5 L0,10 z" fill="#C00000"/></marker></defs>'
            '<line x1="1000" y1="400" x2="1200" y2="400" stroke="#333" stroke-width="2.5" '
            'marker-end="url(#m4)"/></svg>'
            '<svg class="a" data-shape-id="arrow-curve" style="left:0;top:0" width="1280" height="720">'
            '<defs><marker id="m5" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" '
            'markerUnits="userSpaceOnUse"><path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs>'
            '<path d="M1000 600 Q 1100 520 1200 600" fill="none" stroke="#333" stroke-width="2.5" '
            'marker-end="url(#m5)"/></svg>'
        )
        html = td / "option_A.html"
        html.write_text(HEAD + body + TAIL, encoding="utf-8")
        data = _extract(html)
        plan, _ = T.plan_from_extract(data, True)
        fb = {f["id"]: f for f in plan.fallbacks}

        print("[2] native pictures")
        pics = [o for o in plan.ops if o["op"] == "picture"]
        assert [o["name"] for o in pics] == ["photo-a"], pics
        pa = pics[0]
        assert pa["geom"] == "ellipse", pa
        assert all(abs(c - e) < 0.01 for c, e in zip(pa["crop"], [0.25, 0, 0.25, 0])), pa["crop"]
        assert "filtered" in fb["photo-b"]["reason"] and "web address" in fb["photo-web"]["reason"], fb
        prs, slide = build(T._public_plan(plan))
        sh = next(s for s in slide.shapes if s.name == "photo-a")
        assert sh.shape_type == 13 and abs(sh.crop_left - 0.25) < 0.01 and abs(sh.crop_right - 0.25) < 0.01
        from pptx.oxml.ns import qn
        assert sh._element.spPr.find(qn("a:prstGeom")).get("prst") == "ellipse"
        print("    ok: oval picture, cropped 25% each side; filtered and web pictures stay with the agent")

        print("[3] native arrowheads")
        con = {o.get("name"): o for o in plan.ops if o["op"] == "connector"}
        up = con["arrow-up"]
        assert up["line"].get("tail", {}).get("type") == "triangle" and not up["line"].get("head"), up
        (x1, y1), (x2, y2) = up["points"]
        d = np.hypot(500 - 100, 420 - 600)
        assert abs(x2 - (500 + 2 * 400 / d)) < 0.3 and abs(y2 - (420 - 2 * 180 / d)) < 0.3, up["points"]
        back = con["arrow-back"]
        assert back["line"].get("head", {}).get("type") == "triangle" and not back["line"].get("tail"), back
        assert abs(back["points"][0][0] - 698) < 0.3, back["points"]
        big = con["arrow-big"]
        assert not big["line"].get("tail"), big
        tri = [o for o in plan.ops if o.get("name") == "arrow-big-head-1"]
        assert tri and tri[0]["op"] == "freeform" and tri[0]["closed"], tri
        assert "arrow-red" in fb and "another color" in fb["arrow-red"]["reason"], fb.get("arrow-red")
        assert "arrow-curve" in fb and "curved" in fb["arrow-curve"]["reason"], fb.get("arrow-curve")
        import arrow_ends as AE
        arrows, _boxes = AE.read_slide(slide)
        names = {a["name"]: a for a in arrows}
        assert "arrow-up" in names and names["arrow-up"]["heads"][0][2] == "end", arrows
        hx, hy, _w = names["arrow-up"]["heads"][0]
        assert abs(hx - x2) < 0.5 and abs(hy - y2) < 0.5, (hx, hy, x2, y2)
        assert names["arrow-back"]["heads"][0][2] == "start", names["arrow-back"]
        print("    ok: tail and head arrows, tips in place; big head drawn as a triangle; "
              "other markers stay with the agent")

        print("[1] areas the agent draws are left out of the self-check")
        T.self_check([(plan, data)], engine="libreoffice")
        handed = [f["id"] for f in plan.fallbacks if f["kind"] == "self-check"]
        assert not handed, (handed, plan.self_check)
        masks = T._agent_masks(plan)
        assert any(m[0] <= 416 and m[2] >= 516 for m in masks), masks
        print("    ok: nothing handed over; agent areas", len(masks))

        print("[5] short arrows (10/26 deck, page 7, 2026-10-26)")
        # 15 px arrows with 10 px heads on a 2 px line: PowerPoint's large
        # head draws a little bigger (accepted, owner 2026-10-27), which moved
        # the small box's average color past the limit while the arrow's own
        # color matched. Rendered with the default renderer (PowerPoint on
        # Windows when installed).
        lines = "".join(
            f'<line x1="{x}" y1="316" x2="{x + 15}" y2="316" stroke="#1A1A1A" stroke-width="2" '
            'marker-end="url(#ah)"/>' for x in (412, 710, 965))
        lines += ('<line x1="293" y1="461" x2="293" y2="428" stroke="#1A1A1A" stroke-width="2" '
                  'marker-end="url(#ah)"/>'
                  '<line x1="849" y1="546" x2="805" y2="546" stroke="#1A1A1A" stroke-width="2" '
                  'marker-end="url(#ah)"/>')
        # as on the page: steps (white, 1px gray border) on a gray lane, the
        # short arrows in the 15 px gaps between them
        step = ('<div class="a" data-shape-id="step-{n}" style="left:{x}px;top:290px;width:{w}px;'
                'height:52px;background:#fff;border:1px solid #8C8C8C;box-sizing:border-box"></div>')
        short = (
            '<div class="a" data-shape-id="lane" style="left:167px;top:262px;width:1059px;height:108px;'
            'background:#E6E6E6"></div>'
            + "".join(step.format(n=n, x=x, w=w) for n, (x, w) in
                      enumerate(((172, 240), (427, 283), (725, 240), (980, 240))))
            + '<div class="a" data-shape-id="lane-2" style="left:167px;top:400px;width:1059px;'
            'height:180px;background:#E6E6E6"></div>'
            + '<svg class="a" data-shape-id="flow-arrows" style="left:0;top:0" width="1280" height="720" '
            'viewBox="0 0 1280 720"><defs><marker id="ah" markerUnits="userSpaceOnUse" markerWidth="10" '
            'markerHeight="10" refX="10" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 Z" '
            'fill="#1A1A1A"/></marker></defs>' + lines + '</svg>')
        html7 = td / "s7" / "option_A.html"
        html7.parent.mkdir()
        html7.write_text(HEAD + short + TAIL, encoding="utf-8")
        data7 = _extract(html7)
        plan7, _ = T.plan_from_extract(data7, True)
        assert plan7.counts.get("native_arrowheads") == 5, plan7.counts
        assert not plan7.fallbacks, plan7.fallbacks
        T.self_check([(plan7, data7)])
        assert plan7.self_check["ran"], plan7.warnings
        assert not plan7.fallbacks, (plan7.fallbacks, plan7.self_check)
        assert sum(1 for o in plan7.ops if o["op"] == "connector") == 5
        print("    ok: 5 short native arrows, none handed to the agent")
        # one arrow recolored in the slide (planted): still caught
        plan8, _ = T.plan_from_extract(data7, True)
        cons = [o for o in plan8.ops if o["op"] == "connector"]
        cons[1]["line"] = dict(cons[1]["line"], color="C00000")
        T.self_check([(plan8, data7)], hand_over=False)
        fired = [f for f in plan8.self_check["fired"] if "color" in f["what"]]
        assert len(fired) == 1, plan8.self_check
        print("    ok: one arrow recolored red: its color still fires")

    print("[4] thin letters")
    bg = np.array([255.0, 255.0, 255.0])
    op = {"op": "text", "paragraphs": [[{"t": "→", "color": "3A6EA5"}]]}

    def img(core, w):
        D = np.ones((10, 10, 3), dtype=np.float32) * 255
        D[4:6, 2:8] = core
        W = np.zeros((10, 10), dtype=np.float32)
        W[4:6, 2:8] = w
        return D, W
    D, wD = img([68, 118, 173], 1.0)
    N, wN = img([110, 148, 189], 0.74)
    assert A._core_distance(D, N, wD, wN) > A.TEXT_INK_COLOR_LIMIT       # the old reading
    assert A._ink_color(op, D, N, wD, wN, bg) <= A.TEXT_INK_COLOR_LIMIT, A._ink_color(op, D, N, wD, wN, bg)
    R, wR = img([200, 120, 120], 0.6)                                     # a thin red instead
    assert A._ink_color(op, D, R, wD, wR, bg) > A.TEXT_INK_COLOR_LIMIT
    S, wS = img([30, 30, 30], 1.0)                                        # solid, wrong color
    assert A._ink_color(op, D, S, wD, wS, bg) > A.TEXT_INK_COLOR_LIMIT
    print("    ok")
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
