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

    A worker's options in ONE browser run (one render slot; 2026-10-14):
    py -3 scripts/render_html.py slide_NN/option_A.html slide_NN/option_B.html slide_NN/option_C.html
        (each to option_X.sketch.png beside it; or give html/png pairs)

Exit codes
----------
    0 — every PNG written
    2 — bad usage / source HTML missing
    3 — Playwright not installed / Chromium not installed
    4 — a page failed (page goto / screenshot exception, or over its own
        limit), or the run timed out (SLIDE_LAB_RENDER_TIMEOUT seconds,
        default 120, plus SLIDE_LAB_RENDER_PAGE_TIMEOUT, default 60, for each
        page after the first; or one step over 30 s; only this run's own
        browser is ended; re-run). In a batch a failed page fails alone: the
        others are drawn and the message lists the ones to re-run.
    75 — every render slot on this computer stayed busy for 150 s; nothing
        was started (busy, re-run). Waiting for a slot never counts toward
        the time limit (slide-qc/scripts/render_slot.py).

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


def page_timeout() -> float:
    """Seconds each page after the first adds to a batch's time limit, and the
    most one page of a batch may take (SLIDE_LAB_RENDER_PAGE_TIMEOUT, default 60)."""
    import os
    try:
        v = float(os.environ.get("SLIDE_LAB_RENDER_PAGE_TIMEOUT") or 60)
        return v if v > 0 else 60.0
    except ValueError:
        return 60.0


def _missing_playwright(exc) -> None:  # pragma: no cover (setup time only)
    sys.stderr.write(
        "playwright is not installed. Install with:\n"
        "    py -3 -m pip install 'playwright>=1.40,<2.0'\n"
        "    py -3 -m playwright install chromium\n"
        f"underlying error: {exc}\n"
    )
    sys.exit(3)


def _render_one(browser, html_path: Path, png_path: Path, width: int, height: int,
                limit: float) -> None:
    """One page in its own browser context. Raises on failure (the caller
    goes on with the next page). `limit`: the most this page may take; each
    browser step gets what is left of it (never more than the 30 s step
    limit), so a stuck page fails on its own."""
    import time
    from _browser import step, step_timeout
    t0 = time.monotonic()

    def left_ms() -> float:
        left = limit - (time.monotonic() - t0)
        if left <= 0:
            raise TimeoutError(f"{html_path.name} took over {int(limit)} s")
        return max(1000.0, min(step_timeout(), left) * 1000.0)

    png_path.parent.mkdir(parents=True, exist_ok=True)
    ctx = browser.new_context(viewport={"width": width, "height": height},
                              device_scale_factor=1)
    try:
        page = ctx.new_page()
        # file:// URL with the absolute path. Playwright handles the local-file
        # load directly; no need for a server.
        page.set_default_timeout(left_ms())
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        # A page whose own script never ends answers nothing, and the steps
        # below have no time limit of their own: ask it first, with the time
        # this page has left, so a stuck page fails alone instead of ending
        # the whole run.
        page.wait_for_function("() => true", timeout=left_ms())
        # Library icons (`<i data-icon-name>`, or `<img src=".../icons/x.svg">`)
        # are drawn from the shipped SVG previews in the designer's color.
        # They used to render as blank gaps. An unknown name gets a labeled
        # placeholder and a warning here, never a silent gap.
        page.set_default_timeout(left_ms())
        with step("drawing the library icons"):
            icon_warnings = draw_icons_safe(page)
        for w in icon_warnings:
            sys.stderr.write(f"WARNING {w['code']}: {w['detail']}\n")
        # The template's title, takeaway and section tag, last.
        page.set_default_timeout(left_ms())
        chrome_check = apply_chrome_css(page, html_path)
        # `clip` forces the screenshot to exactly the locked canvas box
        # regardless of HTML overflow. `full_page=False` is the default but
        # make it explicit so a future refactor can't silently flip it.
        # Screenshot to a local temp file, then copy into place. Writing
        # straight into a OneDrive folder timed out while OneDrive held the new
        # file, and workers retried renders over and over.
        import tempfile  # noqa: F401  (the folder itself comes from _scratch)
        import _scratch
        page.set_default_timeout(left_ms())
        with _scratch.temp_dir("render_") as td:
            tmp_png = Path(td) / "render.png"
            page.screenshot(
                path=str(tmp_png),
                full_page=False,
                clip={"x": 0, "y": 0, "width": width, "height": height},
            )
            _copy_into_place(tmp_png, png_path)
    finally:
        try:
            with step(f"closing the page {html_path.name}"):
                ctx.close()
        except Exception:
            pass
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


def render_many(
    pairs: list[tuple[Path, Path]],
    *,
    width: int = DEFAULT_W,
    height: int = DEFAULT_H,
) -> list[tuple[Path, Path, str | None]]:
    """Render each (html, png) pair in ONE browser run, holding ONE render
    slot (owner's decision 2026-10-14). Returns (html, png, error or None) per
    pair: a page that fails, or takes longer than its own limit, fails alone
    and the others are still drawn.

    Time limits: the run as a whole gets SLIDE_LAB_RENDER_TIMEOUT (120 s) for
    the browser start and the first page, plus SLIDE_LAB_RENDER_PAGE_TIMEOUT
    (60 s) for each page after it; in a batch each page gets at most that
    page limit. The slot is taken before the time limit starts, so waiting
    for it is free.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        _missing_playwright(exc)
    for html_path, _png in pairs:
        if not html_path.exists():
            sys.stderr.write(f"HTML source not found: {html_path}\n")
            sys.exit(2)

    from _browser import scratch_env, render_deadline, render_slot, render_timeout
    n = len(pairs)
    per_page = page_timeout()
    whole = render_timeout() + per_page * max(0, n - 1)
    label = pairs[0][0].name if n == 1 else f"{n} pages"
    results: list[tuple[Path, Path, str | None]] = []
    # The slot first (waiting is not render time), then the time limit for
    # the whole run (past it, only this run's own browser is ended and the
    # run exits 4: scripts/_browser.py).
    with render_slot(f"render_html.py ({label})"), \
            render_deadline(f"render_html.py ({label})", seconds=whole), \
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
            for html_path, png_path in pairs:
                try:
                    _render_one(browser, html_path, png_path, width, height,
                                per_page if n > 1 else whole)
                    results.append((html_path, png_path, None))
                except Exception as exc:
                    sys.stderr.write(f"render failed: {html_path.name}: {exc}\n")
                    results.append((html_path, png_path, f"{type(exc).__name__}: {exc}"))
        finally:
            browser.close()
    return results


def render_html_to_png(
    html_path: Path,
    png_path: Path,
    *,
    width: int = DEFAULT_W,
    height: int = DEFAULT_H,
) -> None:
    """Render `html_path` to a PNG of exactly `width`x`height` pixels; exit 4
    when it fails. Several pages go through render_many() (one browser run,
    one render slot)."""
    res = render_many([(html_path, png_path)], width=width, height=height)
    if res[0][2]:
        sys.exit(4)


def pairs_from_args(files: list[Path]) -> list[tuple[Path, Path]]:
    """`a.html a.png` (the old form), `a.html a.png b.html b.png ...`, or
    `a.html b.html ...` (each drawn to <name>.sketch.png beside it)."""
    if any(f.suffix.lower() == ".png" for f in files):
        if len(files) % 2 or any(f.suffix.lower() != ".png" for f in files[1::2]):
            sys.stderr.write(
                "Give HTML and PNG files in pairs (a.html a.png b.html b.png), or only "
                "HTML files (each is drawn to <name>.sketch.png beside it).\n")
            sys.exit(2)
        return list(zip(files[0::2], files[1::2]))
    return [(f, f.with_name(f.stem + ".sketch.png")) for f in files]


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("files", type=Path, nargs="+",
                    help="a.html a.png [b.html b.png ...], or a.html b.html ... "
                         "(each to <name>.sketch.png beside it).")
    ap.add_argument(
        "--width", type=int, default=DEFAULT_W,
        help=f"Canvas width in CSS pixels (default {DEFAULT_W}).",
    )
    ap.add_argument(
        "--height", type=int, default=DEFAULT_H,
        help=f"Canvas height in CSS pixels (default {DEFAULT_H}).",
    )
    args = ap.parse_args()
    pairs = [(h.resolve(), p.resolve()) for h, p in pairs_from_args(args.files)]
    results = render_many(pairs, width=args.width, height=args.height)
    failed = [r for r in results if r[2]]
    for html, png, err in results:
        if not err:
            print(f"Rendered {html.name} -> {png}  ({args.width}x{args.height})")
    if failed:
        here = Path(__file__).resolve()
        again = " ".join(f'"{h}" "{p}"' for h, p, _ in failed)
        sys.stderr.write(
            f"{len(failed)} of {len(results)} page(s) did not render: "
            + ", ".join(h.name for h, _, _ in failed)
            + (". The others were drawn. " if len(failed) < len(results) else ". ")
            + f"Next: re-run just those once:\n  py -3 \"{here}\" {again}\n"
              "If a page fails again, open it and fix what the error names, or report it.\n")
        sys.exit(4)


if __name__ == "__main__":
    main()
