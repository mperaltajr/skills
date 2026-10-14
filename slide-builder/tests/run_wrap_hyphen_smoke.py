#!/usr/bin/env python3
"""Smoke test: the line-break predictor breaks after hyphens as PowerPoint
does, and never shrinks text silently.

"Whole fleets, under multi-year supply agreements" at 16 px in a 184 px box
breaks after "multi-" in Chrome and PowerPoint (2 lines). The predictor broke
only at spaces, saw 3 lines, and stepped the text down from 12 pt to 11 pt
with nothing but a WRAP_ADJUSTED note (2026-10-13). All content is made up.

  1. hyphen_pieces: after a hyphen between letters, after en/em dashes; not
     in "2025-2030", "-5%", "and/or", nor at a non-breaking hyphen
  2. that phrase: predicted 2 lines (the design's), kept at 12 pt, no
     warning; the fit check (_fit_wrap) agrees
  3. "and/or" and "2025-2030" still don't break
  4. when widening can't save the line count: the size is kept and a
     WRAP_RISK warning (shown on the review page as Major) says what to do

Needs Playwright's Chromium (no renderer).
Run:  py -3 slide-builder/tests/run_wrap_hyphen_smoke.py
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

import translate_html as T  # noqa: E402
from _chrome_schema import _fit_wrap, hyphen_pieces  # noqa: E402

PHRASE = "Whole fleets, under multi-year supply agreements"
PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
body { margin: 0; }
.slide-canvas { position: relative; width: 1280px; height: 720px; background: #fff;
  font-family: Arial, sans-serif; color: #1a1a1a; overflow: hidden; }
.d { position: absolute; width: 184px; font-size: 16px; line-height: 22px; margin: 0; }
</style></head><body><div class="slide-canvas">
<p class="d" data-shape-id="desc-fleets" style="left:60px;top:200px">""" + PHRASE + """</p>
<p class="d" data-shape-id="desc-slash" style="left:300px;top:200px;width:120px">Owners and/or partners</p>
<p class="d" data-shape-id="desc-years" style="left:500px;top:200px;width:110px">Plan for 2025-2030 builds</p>
</div></body></html>"""


def _extract(td: Path):
    from playwright.sync_api import sync_playwright
    html = td / "wrap.html"
    html.write_text(PAGE, encoding="utf-8")
    with sync_playwright() as pw:
        from _browser import launch
        br = launch(pw)
        page = br.new_page(viewport={"width": 1280, "height": 720})
        data = T.extract(page, html, True)
        br.close()
    return data


def main() -> int:
    print("[1] where a word may break")
    assert hyphen_pieces("multi-year") == ["multi-", "year"]
    assert hyphen_pieces("well-known-ish") == ["well-", "known-", "ish"]
    assert hyphen_pieces("2025-2030") == ["2025-2030"]
    assert hyphen_pieces("-5%") == ["-5%"]
    assert hyphen_pieces("and/or") == ["and/or"]
    assert hyphen_pieces("co‑op") == ["co‑op"]
    assert hyphen_pieces("north–south") == ["north–", "south"]
    assert hyphen_pieces("now—later") == ["now—", "later"]
    print("    ok")

    with tempfile.TemporaryDirectory() as td:
        data = _extract(Path(td))
        texts = {t["id"]: t for t in data["texts"]}
        assert texts["desc-fleets"]["lines"] == 2, texts["desc-fleets"]["lines"]

        print("[2] the 10/13 phrase: 2 lines, kept at 12 pt, no warning")
        plan, _ = T.plan_from_extract(data, True)
        op = next(o for o in plan.ops if o.get("name") == "desc-fleets")
        assert T._wrapped_lines(op["paragraphs"], op["w"]) == 2, op["w"]
        assert all(abs(r["size_px"] - 16.0) < 1e-6 for p in op["paragraphs"] for r in p), op["paragraphs"]
        codes = {w["code"] for w in plan.warnings if "desc-fleets" in w["detail"]}
        assert not codes & {"WRAP_ADJUSTED", "WRAP_RISK"}, plan.warnings
        r0 = op["paragraphs"][0][0]
        m = T._font(r0["font"], r0["bold"], T._snapped_px(r0["size_px"]))
        widths, widest = _fit_wrap(PHRASE, m, op["w"])
        assert len(widths) == 2 and widest <= op["w"], (widths, widest, op["w"])
        print(f"    ok: {op['w']:.1f} px box, lines {[round(w_) for w_ in widths]}")

        print("[3] 'and/or' and '2025-2030' are not broken")
        for name in ("desc-slash", "desc-years"):
            o = next(o for o in plan.ops if o.get("name") == name)
            joined = "".join(r["t"] for p in o["paragraphs"] for r in p)
            words = [w_ for w_ in joined.split() if "/" in w_ or "-" in w_]
            assert words and all(hyphen_pieces(w_) == [w_] for w_ in words), words
        print("    ok")

        print("[4] no fit even widened: size kept, WRAP_RISK")
        real = T._wrapped_lines
        try:
            T._wrapped_lines = lambda paras, w: 3          # PowerPoint would always need 3
            plan2, _ = T.plan_from_extract(data, True)
        finally:
            T._wrapped_lines = real
        op2 = next(o for o in plan2.ops if o.get("name") == "desc-fleets")
        assert all(abs(r["size_px"] - 16.0) < 1e-6 for p in op2["paragraphs"] for r in p), \
            "the font was stepped down"
        risk = [w for w in plan2.warnings if w["code"] == "WRAP_RISK" and "desc-fleets" in w["detail"]]
        assert risk and "kept at the design's size" in risk[0]["detail"] \
            and "shorten it" in risk[0]["detail"], plan2.warnings
        assert not any("stepped down" in w["detail"] for w in plan2.warnings)
        src = (SKILL / "scripts" / "build_review.py").read_text(encoding="utf-8")
        assert 'code == "WRAP_RISK"' in src
        print("    ok:", risk[0]["detail"][:90])
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
