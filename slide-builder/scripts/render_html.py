#!/usr/bin/env python3
"""Render an HTML file to a 1280×720 PNG via headless Chromium.

The sketch-path HTML build path uses
this to turn worker-authored HTML into the reviewable PNG the operator
picks from. The canvas size is locked at 1280×720 so the
1 px ↔ 9525 EMU mapping (per `_chrome_schema.EMU_PER_PX_AT_1280`) is
exact when the translator later converts coordinates back to native
python-pptx shapes.

Usage
-----
    py -3 scripts/render_html.py path/to/option_A.html path/to/option_A.png
    py -3 scripts/render_html.py --width 1280 --height 720 ... (defaults)

Exit codes
----------
    0 — PNG written successfully
    2 — bad usage / source HTML missing
    3 — Playwright not installed / Chromium not installed
    4 — render failed (page goto / screenshot exception), or timed out
        (whole render over SLIDE_LAB_RENDER_TIMEOUT seconds, default 120, or
        one step over 30 s; only this run's own browser is ended; re-run)

Install
-------
    pip install playwright>=1.40
    playwright install chromium

Notes
-----
- Canvas and CSS conventions are fixed at 1280×720.
- The PNG this produces is what gets compared via SSIM.
- When the HTML's folder holds `_chrome.css` (prep writes one per slide,
  2026-10-13), it is added last, so the picture shows the template's real
  title, takeaway and section tag; the title's line count and any body shape
  they cover go in `<png stem>.chrome.json` for the review page, and are
  printed as warnings (TITLE_TOO_LONG, BODY_UNDER_CHROME).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_W = 1280
DEFAULT_H = 720


def _copy_into_place(src: Path, dst: Path, tries: int = 6) -> None:
    """Copy a finished file to its destination, waiting out a short sync lock."""
    import shutil
    import time
    for i in range(tries):
        try:
            shutil.copyfile(src, dst)
            return
        except PermissionError:
            if i == tries - 1:
                raise
            time.sleep(0.5 * (i + 1))


def draw_icons_safe(page) -> list[dict]:
    """Draw the page's library icons (scripts/icon_svg.py). A failure here
    must not stop the render; it is reported as a warning instead."""
    try:
        here = str(Path(__file__).resolve().parent)
        if here not in sys.path:
            sys.path.insert(0, here)
        import icon_svg
        return icon_svg.draw_icons(page)
    except Exception as exc:  # pragma: no cover
        return [{"code": "ICON_DRAW_FAILED", "name": "",
                 "detail": f"could not draw the library icons ({type(exc).__name__}: {exc})"}]


# ---------------------------------------------------------------------------
# The template's title, takeaway and section tag (2026-10-13)
# ---------------------------------------------------------------------------
# Prep writes slide_NN/_chrome.css (twins/chrome_rules.chrome_css): the
# values finalize uses for the title, the takeaway and the section tag on
# this slide's layout. It is added LAST, just before the screenshot, so the
# sketch picture shows them as the finished slide will, whatever the
# designer's own CSS says. The HTML file is never changed (the converter
# reads it without this sheet). After it is added, the title's line count
# and any body shape the title or takeaway now covers are measured and
# written next to the picture (option_X.sketch.chrome.json) for the review
# page (build_review.py).
CHROME_CSS_NAME = "_chrome.css"

_WRAP_TITLE_JS = """() => {
  for (const el of document.querySelectorAll('[data-template-field="title"]')) {
    if (el.querySelector(':scope > [data-chrome-inner]')) continue;
    const s = document.createElement('span');
    s.setAttribute('data-chrome-inner', '');
    while (el.firstChild) s.appendChild(el.firstChild);
    el.appendChild(s);
  }
}"""

_MEASURE_JS = """() => {
  const visible = el => { const cs = getComputedStyle(el);
    return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity || '1') > 0; };
  const textRects = el => { const rg = document.createRange(); rg.selectNodeContents(el);
    return Array.from(rg.getClientRects()).filter(r => r.width > 0.5 && r.height > 0.5); };
  const lineCount = rects => { const bottoms = [];
    for (const r of rects) if (!bottoms.some(b => Math.abs(b - r.bottom) < 3)) bottoms.push(r.bottom);
    return bottoms.length; };
  const union = rects => rects.length ? {
    l: Math.min(...rects.map(r => r.left)), t: Math.min(...rects.map(r => r.top)),
    r: Math.max(...rects.map(r => r.right)), b: Math.max(...rects.map(r => r.bottom))} : null;
  const title = document.querySelector('[data-template-field="title"]');
  const take = document.querySelector('[data-template-field="subtitle"]')
            || document.querySelector('[data-shape-id="subtitle"]');
  const out = {title_lines: 0, title_box: null, takeaway_lines: 0, takeaway_box: null, covered: []};
  if (title && (title.textContent || '').trim()) {
    const rs = textRects(title); out.title_lines = lineCount(rs); out.title_box = union(rs); }
  if (take && (take.textContent || '').trim()) {
    const rs = textRects(take); out.takeaway_lines = lineCount(rs); out.takeaway_box = union(rs); }
  const boxes = [['title', out.title_box], ['takeaway', out.takeaway_box]].filter(b => b[1]);
  const reserved = /^(subtitle$|footnote|source|page-number|section-tag)/i;
  for (const el of document.querySelectorAll('[data-shape-id]')) {
    const id = el.getAttribute('data-shape-id') || '';
    if (reserved.test(id) || !visible(el)) continue;
    if ((title && (el.contains(title) || title.contains(el))) ||
        (take && (el.contains(take) || take.contains(el)))) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    if (r.width >= 1200 && r.height >= 600) continue;          // a backdrop
    for (const [by, b] of boxes) {
      const w = Math.min(r.right, b.r) - Math.max(r.left, b.l);
      const h = Math.min(r.bottom, b.b) - Math.max(r.top, b.t);
      if (w > 2 && h > 2) { out.covered.push({id: id, by: by, top: Math.round(r.top)}); break; }
    }
  }
  return out;
}"""


def chrome_check_path(png_path: Path) -> Path:
    """option_A.sketch.png -> option_A.sketch.chrome.json"""
    return png_path.with_name(png_path.stem + ".chrome.json")


def apply_chrome_css(page, html_path: Path):
    """Add the slide's _chrome.css (when prep wrote one) last, and measure
    what it changed. Returns the measurement, or None when there is no
    sheet. A failure is a warning, never a stopped render."""
    css_path = html_path.parent / CHROME_CSS_NAME
    if not css_path.exists():
        return None
    try:
        css = css_path.read_text(encoding="utf-8")
        page.evaluate(_WRAP_TITLE_JS)
        page.add_style_tag(content=css)
        try:
            page.evaluate("() => document.fonts.ready.then(() => true)")
        except Exception:
            pass
        data = page.evaluate(_MEASURE_JS) or {}
        data["chrome_css"] = str(css_path.name)
        m = re.search(r"--chrome-body-top:\s*([\d.]+)px", css)
        data["body_top"] = float(m.group(1)) if m else None
        return data
    except Exception as exc:  # pragma: no cover
        sys.stderr.write(f"WARNING CHROME_CSS_FAILED: could not apply {css_path.name} "
                         f"({type(exc).__name__}: {exc}); the picture shows the design's own "
                         f"title and takeaway styling. Re-run this render; if it fails again, "
                         f"re-run prep for this slide (build_deck.py) to rewrite {css_path.name}\n")
        return None


def render_html_to_png(
    html_path: Path,
    png_path: Path,
    *,
    width: int = DEFAULT_W,
    height: int = DEFAULT_H,
) -> None:
    """Render `html_path` to a PNG of exactly `width`×`height` pixels.

    Imports Playwright lazily so the rest of the slide-builder pipeline
    doesn't pay the import cost on every invocation. Uses a fresh browser
    per call (simple + deterministic; later milestones can batch).
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover — exercised only at setup time
        sys.stderr.write(
            "playwright is not installed. Install with:\n"
            "    py -3 -m pip install 'playwright>=1.40,<2.0'\n"
            "    py -3 -m playwright install chromium\n"
            f"underlying error: {exc}\n"
        )
        sys.exit(3)

    if not html_path.exists():
        sys.stderr.write(f"HTML source not found: {html_path}\n")
        sys.exit(2)

    png_path.parent.mkdir(parents=True, exist_ok=True)

    from _browser import scratch_env, render_deadline, step
    # A time limit for the whole render (120 s, SLIDE_LAB_RENDER_TIMEOUT) and
    # each slow step (30 s): past it, only this run's own browser is ended and
    # the run exits 4 (scripts/_browser.py).
    with render_deadline(f"render_html.py ({html_path.name})"), \
            scratch_env(), sync_playwright() as pw:
        try:
            from _browser import launch
            browser = launch(pw, headless=True)
        except Exception as exc:
            sys.stderr.write(
                "No browser to render with: Playwright's Chromium is not installed\n"
                "and neither Microsoft Edge nor Google Chrome could be started.\n"
                "Install Chromium with:\n"
                "    py -3 -m playwright install chromium\n"
                f"underlying error: {exc}\n"
            )
            sys.exit(3)
        try:
            ctx = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=1,
            )
            page = ctx.new_page()
            try:
                # file:// URL with the absolute path. Playwright handles
                # the local-file load directly; no need for a server.
                page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
                # Library icons (`<i data-icon-name>`, or `<img src=".../icons/x.svg">`)
                # are drawn from the shipped SVG previews in the designer's color.
                # They used to render as blank gaps. An unknown name gets a
                # labeled placeholder and a warning here, never a silent gap.
                with step("drawing the library icons"):
                    icon_warnings = draw_icons_safe(page)
                for w in icon_warnings:
                    sys.stderr.write(f"WARNING {w['code']}: {w['detail']}\n")
                # The template's title, takeaway and section tag, last.
                chrome_check = apply_chrome_css(page, html_path)
                # `clip` forces the screenshot to exactly the locked canvas
                # box regardless of HTML overflow. `full_page=False` is the
                # default but make it explicit so a future refactor can't
                # silently flip it.
                # Screenshot to a local temp file, then copy into place. Writing
                # straight into a OneDrive folder timed out while OneDrive held
                # the new file, and workers retried renders over and over.
                import tempfile  # noqa: F401  (the folder itself comes from _scratch)
                import _scratch
                with _scratch.temp_dir("render_") as td:
                    tmp_png = Path(td) / "render.png"
                    page.screenshot(
                        path=str(tmp_png),
                        full_page=False,
                        clip={"x": 0, "y": 0, "width": width, "height": height},
                    )
                    _copy_into_place(tmp_png, png_path)
                check_path = chrome_check_path(png_path)
                if chrome_check is not None:
                    import json
                    check_path.write_text(json.dumps(chrome_check, indent=1), encoding="utf-8")
                    if chrome_check.get("title_lines", 0) > 2:
                        sys.stderr.write(
                            f"WARNING TITLE_TOO_LONG: in the template's title style the title "
                            f"takes {chrome_check['title_lines']} lines; the template holds 2. "
                            f"Shorten the title (ask the user before changing the brief's "
                            f"wording)\n")
                    for c in chrome_check.get("covered") or []:
                        sys.stderr.write(
                            f"WARNING BODY_UNDER_CHROME: shape {c['id']!r} sits under the "
                            f"template's {c['by']}. Move it down to --body-top or lower\n")
                elif check_path.exists():
                    check_path.unlink()      # no sheet now: an old check would mislead
            except Exception as exc:
                sys.stderr.write(f"render failed: {exc}\n")
                sys.exit(4)
        finally:
            browser.close()


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("html", type=Path, help="Source HTML file.")
    ap.add_argument("png", type=Path, help="Destination PNG file.")
    ap.add_argument(
        "--width", type=int, default=DEFAULT_W,
        help=f"Canvas width in CSS pixels (default {DEFAULT_W}).",
    )
    ap.add_argument(
        "--height", type=int, default=DEFAULT_H,
        help=f"Canvas height in CSS pixels (default {DEFAULT_H}).",
    )
    args = ap.parse_args()

    render_html_to_png(
        args.html.resolve(),
        args.png.resolve(),
        width=args.width,
        height=args.height,
    )
    print(f"Rendered {args.html.name} -> {args.png}  ({args.width}x{args.height})")


if __name__ == "__main__":
    main()
