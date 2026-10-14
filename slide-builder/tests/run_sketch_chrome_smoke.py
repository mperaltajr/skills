#!/usr/bin/env python3
"""Smoke test: sketch pictures show the template's real title, takeaway and
section tag (owner's decision, 2026-10-13).

Designers styled the title and takeaway in their sketches by guess, so the
review pictures disagreed with each other and with the finished deck. Now
prep writes slide_NN/_chrome.css from the values finalize uses
(twins/chrome_rules.chrome_style), render_html.py adds it last, and the
review page checks the result against the template, not against the other
pages.

On the bundled test template, through the real scripts:
  1. prep writes slide_NN/_chrome.css and the same values in plain words in
     _context.md ("styled by Slide Lab", the title size, the section tag)
  2. the values are the ones finalize puts on the finished slide: a sketch
     page goes through finalize and compile, and its title box, title size,
     takeaway top, size and color and section tag position and color match
     chrome_style()
  3. a sketch whose designer styled the title and takeaway (green, bold,
     wrong place) renders with the template's title, takeaway and section
     tag; the HTML file is unchanged; nothing is flagged
  4. a 3-line title and a body shape drawn under the title are flagged
     Major on the review card (TITLE_TOO_LONG, BODY_UNDER_CHROME), from the
     render's check file
  5. a folder with no _chrome.css renders as before, and an old check file
     is removed

Needs Playwright's Chromium and LibreOffice or PowerPoint, like the other
render smokes. Fictional content only.
Run:  py -3 slide-builder/tests/run_sketch_chrome_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))

import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402

EMU = 9525
TAG = "Market view"
SLIDE = """
### Slide {n} — Claim number {n} is stated plainly here

**Slide type:** Content
**Section tag:** {tag}
**Governing thought (the claim):** Claim number {n} is stated plainly here.
**The takeaway:** Takeaway {n}.
**Evidence / content:**
- Point one for slide {n}
- Point two for slide {n}
"""

STYLED = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0}
.slide-canvas{position:relative;width:1280px;height:720px;background:#fff;font-family:Arial}
.slide-title{position:absolute;left:58px;top:62px;font-size:26px;color:#C03030;font-weight:400;margin:0}
.slide-subtitle{position:absolute;left:400px;top:300px;font-size:30px;color:#22AA66;font-weight:700;margin:0}
p{margin:0;position:absolute}
</style></head><body><div class="slide-canvas">
<h1 class="slide-title" data-template-field="title">{title}</h1>
<p class="slide-subtitle" data-template-field="subtitle">Takeaway 1.</p>
<p data-shape-id="body" style="left:100px;top:{body_top}px;font-size:16px;width:500px">Body text for the sketch page</p>
<p data-template-field="footer" style="left:60px;top:690px;font-size:12px">made-up figures</p>
</div></body></html>"""

SHORT = "Claim number 1 is stated plainly here"
LONG = ("Claim number 1 is stated plainly here and then it keeps going with more and more "
        "words, far past what two lines of the template's title box can ever hold at its size")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _prep(tmp: Path, n: int) -> Path:
    brief = tmp / "brief.md"
    brief.write_text(H.BRIEF.format(slides="".join(SLIDE.format(n=i, tag=TAG)
                                                    for i in range(1, n + 1))), encoding="utf-8")
    r = H.run("seal_brief.py", "--brief", brief, "--accepted", "test brief")
    assert r.returncode == 0, r.stdout + r.stderr
    out = tmp / "out"
    r = H.run("build_deck.py", "--brief", brief, "--template", H.TEMPLATE,
              "--out", out, "--pattern", "direct", "--confirm-template")
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return out


def _style():
    from pptx import Presentation
    import _paths as _p
    from _chrome_schema import load_chrome_yml
    from twins.chrome_rules import chrome_style, template_takeaway_pt
    from twins.client_theme import resolve_build_template, load_brand_sidecar
    spec = load_chrome_yml(_p.chrome_yml(H.TEMPLATE))
    prs = Presentation(str(resolve_build_template(H.TEMPLATE)))
    accent = (load_brand_sidecar(H.TEMPLATE) or {}).get("accent_hex", "")
    return chrome_style(spec.layouts["body_canonical_light"], prs, accent,
                        page_type="content", takeaway_pt=template_takeaway_pt(prs, spec),
                        section_tag=TAG)


def _render(html: Path, png: Path):
    r = H.run("render_html.py", html, png)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    return r


def _pixels(png: Path):
    from PIL import Image
    im = Image.open(png).convert("RGB")
    return im


def _has_color(im, box, rgb, tol=40) -> bool:
    x0, y0, x1, y1 = (int(v) for v in box)
    for y in range(max(0, y0), min(im.height, y1), 2):
        for x in range(max(0, x0), min(im.width, x1), 2):
            p = im.getpixel((x, y))
            if all(abs(a - b) <= tol for a, b in zip(p, rgb)):
                return True
    return False


def _hex(h: str) -> tuple:
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="slidelab_sketch_chrome_"))
    saved = os.environ.get("SLIDE_LAB_TRANSLATOR")
    os.environ["SLIDE_LAB_TRANSLATOR"] = "script"
    try:
        out = _prep(tmp, 2)
        st = _style()
        assert st is not None, "no chrome style for the body layout"

        print("[1] prep writes _chrome.css and the values in plain words")
        css = out / "slide_01" / "_chrome.css"
        assert css.exists(), "prep did not write slide_01/_chrome.css"
        text = css.read_text(encoding="utf-8")
        assert '[data-template-field="title"]' in text and "!important" in text
        assert f'content: "{TAG}"' in text, "the section tag is not drawn by the sheet"
        ctx = (out / "slide_01" / "_context.md").read_text(encoding="utf-8")
        assert "styled by Slide Lab" in ctx, "the context does not say the pipeline styles these"
        assert f"**Title:** {st['title']['size_pt']:g} pt" in ctx, ctx[-2500:]
        assert f'"{TAG}"' in ctx and "do not style them" in ctx
        print(f"    ok: title {st['title']['size_pt']:g} pt at top {st['title']['top']:g} px, "
              f"takeaway {st['takeaway']['size_pt']:g} pt at {st['takeaway']['top']:g} px, "
              f"tag at {st['section_tag']['top']:g} px")

        print("[2] the values are the ones finalize puts on the slide")
        html1 = out / "slide_01" / "option_A.html"
        html1.write_text(STYLED.replace("{title}", SHORT).replace("{body_top}", "300"),
                         encoding="utf-8")
        H.write_option(out, 2)
        r = H.run("build_review.py", "--out", out)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
        tok = _state.read_state(out)["review"]["token"]
        body = _state.canonical_picks({"slide_01": "A", "slide_02": "A"})
        r = H.run("record_picks.py", "--out", out, "--approved",
                  f"PICKS {body} CHECK {_state.approval_check(tok, body)}")
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
        r = H.finalize(out)
        assert r.returncode == 0, r.stdout[-2500:] + r.stderr[-2500:]
        from pptx import Presentation
        from pptx.oxml.ns import qn
        from twins.chrome_rules import _ph_type, _inset
        prs = Presentation(str(out / "slide_01" / "option_A.pptx"))
        s = prs.slides[0]
        title = next(sh for sh in s.shapes if _ph_type(sh) in (1, 3))
        t = st["title"]
        assert abs(int(title.left) / EMU - t["left"]) < 1 and abs(int(title.top) / EMU - t["top"]) < 1, \
            (int(title.left) / EMU, int(title.top) / EMU, t)
        assert abs(int(title.width) / EMU - t["width"]) < 1 and abs(int(title.height) / EMU - t["height"]) < 1
        sizes = {int(r_.get("sz")) / 100 for r_ in title._element.iter(qn("a:rPr")) if r_.get("sz")}
        assert sizes == {t["size_pt"]}, (sizes, t["size_pt"])
        take = next(sh for sh in s.shapes if getattr(sh, "has_text_frame", False)
                    and sh.text_frame.text.strip().startswith("Takeaway 1"))
        k = st["takeaway"]
        tl = (int(take.left) + _inset(take, "lIns")) / EMU
        assert abs(tl - k["left"]) < 1 and abs(int(take.top) / EMU - k["top"]) < 1, \
            (tl, int(take.top) / EMU, k)
        tsz = {int(r_.get("sz")) / 100 for r_ in take._element.iter(qn("a:rPr")) if r_.get("sz")}
        assert tsz == {k["size_pt"]}, (tsz, k)
        tag = next(sh for sh in s.shapes if sh.name == "section-tag")
        g = st["section_tag"]
        assert abs(int(tag.left) / EMU - g["left"]) < 1 and abs(int(tag.top) / EMU - g["top"]) < 1, \
            (int(tag.left) / EMU, int(tag.top) / EMU, g)
        tag_color = [c.get("val") for c in tag._element.iter(qn("a:srgbClr"))]
        assert tag_color == [g["color"]], (tag_color, g["color"])
        print("    ok: title box and size, takeaway place and size, section tag place and color match")

        print("[3] a styled sketch renders in the template's style; the HTML is unchanged")
        d3 = tmp / "r3" / "slide_01"
        d3.mkdir(parents=True)
        shutil.copy2(css, d3 / "_chrome.css")
        h3 = d3 / "option_A.html"
        h3.write_text(STYLED.replace("{title}", SHORT).replace("{body_top}", "300"), encoding="utf-8")
        before = _md5(h3)
        png3 = d3 / "option_A.sketch.png"
        _render(h3, png3)
        assert _md5(h3) == before, "the render changed the HTML file"
        im = _pixels(png3)
        title_box = (t["left"], t["top"], t["left"] + t["width"], t["top"] + t["height"])
        assert _has_color(im, title_box, _hex(t["color"]), tol=60), "no title text in the title box"
        assert not _has_color(im, (0, 0, 1280, 720), (0xC0, 0x30, 0x30), tol=30), \
            "the designer's red title color survived"
        assert not _has_color(im, (0, 0, 1280, 720), (0x22, 0xAA, 0x66), tol=30), \
            "the designer's green takeaway survived"
        take_box = (k["left"], k["top"], k["left"] + 300, k["top"] + 30)
        assert _has_color(im, take_box, _hex(k["color"]), tol=60), "no takeaway under the title"
        tag_box = (g["left"], g["top"], g["left"] + 200, g["top"] + g["height"] + 4)
        assert _has_color(im, tag_box, _hex(g["color"]), tol=60), "no section tag above the title"
        chk = json.loads((d3 / "option_A.sketch.chrome.json").read_text(encoding="utf-8"))
        assert chk["title_lines"] == 1 and chk["covered"] == [], chk
        # the title's text sits at the bottom of its box (bottom-aligned)
        assert chk["title_box"]["b"] > t["top"] + t["height"] - t["pad_b"] - 3, chk["title_box"]
        import build_review as BR
        _form, notes = BR.sketch_facts(h3, {"source": "made-up figures"})
        assert not [n for n in notes if n["code"] in ("TITLE_TOO_LONG", "BODY_UNDER_CHROME")], notes
        print("    ok: the template's title, takeaway and tag are drawn; nothing flagged")

        print("[4] a 3-line title and a body shape under the title are Major")
        h4 = d3 / "option_B.html"
        h4.write_text(STYLED.replace("{title}", LONG).replace("{body_top}", "60"), encoding="utf-8")
        r = _render(h4, d3 / "option_B.sketch.png")
        assert "TITLE_TOO_LONG" in r.stderr and "BODY_UNDER_CHROME" in r.stderr, r.stderr[-1500:]
        _form, notes = BR.sketch_facts(h4, {"source": "made-up figures"})
        codes = {n["code"]: n["severity"] for n in notes}
        assert codes.get("TITLE_TOO_LONG") == "Major", notes
        assert codes.get("BODY_UNDER_CHROME") == "Major", notes
        print("    ok: " + "; ".join(f"{n['code']}: {n['detail'][:60]}..." for n in notes
                                    if n["code"] in ("TITLE_TOO_LONG", "BODY_UNDER_CHROME")))

        print("[5] no _chrome.css: rendered as before, an old check file removed")
        (d3 / "_chrome.css").unlink()
        _render(h4, d3 / "option_B.sketch.png")
        assert not (d3 / "option_B.sketch.chrome.json").exists(), "a stale check file was kept"
        im5 = _pixels(d3 / "option_B.sketch.png")
        assert _has_color(im5, (0, 0, 1280, 720), (0xC0, 0x30, 0x30), tol=30), \
            "without the sheet the design's own title should show"
        print("    ok")
    finally:
        if saved is None:
            os.environ.pop("SLIDE_LAB_TRANSLATOR", None)
        else:
            os.environ["SLIDE_LAB_TRANSLATOR"] = saved
        shutil.rmtree(tmp, ignore_errors=True)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
