#!/usr/bin/env python3
"""Smoke test: list bullets are measured from the marker itself, never from
the page beside a panel or from the first letter.

A <ul> 20 px inside a dark panel came out with giant white dots straddling the
panel's edge (900-1,200% of the text size, 2026-10-13): the strip read for the
bullet crossed the panel's edge, so the panel became "background" and the
light page beside it "the bullet". An item starting with "A" also read the
letter's smoothed foot as part of its bullet (404%) on any background. All
content is made up.

  1. list 20 px inside a navy panel: every bullet inside the panel, 60-200%
     of the text size, the first no bigger than the others
  2. first item starting with "A" on white: its bullet the same size as the rest
  3. control, 40 px inside the panel: as before (inside, normal size)
  4. a reading outside 60-200% falls back to the browser's marker with a
     BULLET_FALLBACK warning (forced by planting a bad picture)
  5. the self-check rule: a bullet at 900% or outside its panel is flagged

Needs Playwright's Chromium (the self-check render is not needed).
Run:  py -3 slide-builder/tests/run_list_bullets_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import copy
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))

import translate_html as T  # noqa: E402

PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
body {{ margin: 0; }}
.slide-canvas {{ position: relative; width: 1280px; height: 720px; background: #eef2f6;
  font-family: Arial, sans-serif; color: #1a1a1a; overflow: hidden; }}
.panel {{ position: absolute; left: 440px; top: 150px; width: 420px; height: 300px; background: #0B1F33; }}
ul.net {{ position: absolute; left: {left}px; top: 180px; width: 360px; margin: 0; padding-left: 18px;
  font-size: 16px; line-height: 24px; color: #fff; }}
ul.net li {{ margin-bottom: 8px; }}
ul.w {{ position: absolute; left: 80px; top: 180px; width: 300px; margin: 0; padding-left: 24px;
  font-size: 16px; line-height: 24px; }}
</style></head><body><div class="slide-canvas">
<div class="panel" data-shape-id="network"></div>
<ul class="net" data-shape-id="network-list">
<li>Every site on one shared order book</li>
<li>Regional teams see the same queue</li>
<li>Spare parts move between sites overnight</li>
</ul>
<ul class="w" data-shape-id="white-list">
<li>All requests go through one form</li>
<li>Each team reviews its queue weekly</li>
<li>Budgets are released in stages</li>
</ul>
</div></body></html>"""


def _plan(td: Path, left: int, tag: str):
    from playwright.sync_api import sync_playwright
    html = td / f"{tag}.html"
    html.write_text(PAGE.format(left=left), encoding="utf-8")
    with sync_playwright() as pw:
        from _browser import launch
        br = launch(pw)
        page = br.new_page(viewport={"width": 1280, "height": 720})
        data = T.extract(page, html, True)
        br.close()
    plan, _ = T.plan_from_extract(data, True)
    return plan, data


def _bullets(plan, name):
    op = next(o for o in plan.ops if o.get("op") == "text" and o.get("name") == name and o.get("para"))
    out = []
    for pr in op["para"]:
        if pr.get("bullet"):
            out.append((op["x"] + pr["marL_px"] + pr["indent_px"], float(pr["bullet"]["pct"])))
    return op, out


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for left, tag in ((460, "inset20"), (480, "inset40")):
            print(f"[{tag}] list {left - 440} px inside a navy panel")
            plan, data = _plan(td, left, tag)
            op, bl = _bullets(plan, "network-list")
            assert len(bl) == 3, bl
            for x, pct in bl:
                assert 440 <= x <= 860, (tag, x)
                assert 60 <= pct <= 200, (tag, pct)
            assert bl[0][1] <= 1.2 * min(p for _, p in bl[1:]), (tag, bl)
            assert op["x"] >= 440, (tag, op["x"])
            assert not [w for w in plan.warnings if w["code"] == "BULLET_FALLBACK"], plan.warnings
            print("    ok:", [(round(x, 1), round(p)) for x, p in bl])
            if tag == "inset20":
                print("[A-first] first item starting with 'A' on the page")
                _op, wl = _bullets(plan, "white-list")
                assert len(wl) == 3, wl
                ps = [p for _, p in wl]
                assert max(ps) <= 1.2 * min(ps) and all(60 <= p <= 200 for p in ps), ps
                print("    ok:", [round(p) for p in ps])

                print("[guard] a bad reading falls back to the browser's marker")
                bad = copy.deepcopy(data)
                L = next(x for x in bad["lists"] if x["id"] == "network-list")
                for it in L["items"]:
                    it["marker"]["fs"] = it["marker"]["fs"]           # unchanged size
                # paint a big white block where the first bullet is
                import io
                from PIL import Image, ImageDraw
                im = Image.open(io.BytesIO(bad["_shot"])).convert("RGB")
                m = L["items"][0]["marker"]
                ImageDraw.Draw(im).rectangle([m["x"], m["y"] - 2, m["x"] + m["w"] - 3, m["y"] + m["h"] + 2],
                                             fill=(255, 255, 255))
                buf = io.BytesIO()
                im.save(buf, "PNG")
                bad["_shot"] = buf.getvalue()
                plan2, _ = T.plan_from_extract(bad, True)
                _op, bl2 = _bullets(plan2, "network-list")
                warns = [w for w in plan2.warnings if w["code"] == "BULLET_FALLBACK"]
                assert warns and "browser's marker" in warns[0]["detail"], plan2.warnings
                assert 60 <= bl2[0][1] <= 200 and abs(bl2[0][0] - m["x"]) < 1.0, bl2
                print("    ok:", warns[0]["detail"][:110])

                print("[rule] the self-check flags a 900% bullet and one outside its panel")
                assert not T._bullet_rows(plan), T._bullet_rows(plan)
                p3 = copy.deepcopy(plan)
                o3 = next(o for o in p3.ops if o.get("name") == "network-list" and o.get("para"))
                o3["para"][0]["bullet"]["pct"] = 900.0
                rows = T._bullet_rows(p3)
                assert rows and rows[0]["fired"] == ["bullet"] and "900%" in rows[0]["detail"], rows
                o3["para"][0]["bullet"]["pct"] = 100.0
                o3["para"][0]["indent_px"] = 440 - 30 - o3["x"] - o3["para"][0]["marL_px"]
                rows = T._bullet_rows(p3)
                assert rows and "outside the panel" in rows[0]["detail"], rows
                print("    ok")
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
