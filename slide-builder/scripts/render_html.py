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
    4 — render failed (page goto / screenshot exception)

Install
-------
    pip install playwright>=1.40
    playwright install chromium

Notes
-----
- Canvas and CSS conventions are fixed at 1280×720.
- The PNG this produces is what gets compared via SSIM.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_W = 1280
DEFAULT_H = 720


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

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=True)
        except Exception as exc:
            sys.stderr.write(
                "Chromium not installed for Playwright. Install with:\n"
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
                # `clip` forces the screenshot to exactly the locked canvas
                # box regardless of HTML overflow. `full_page=False` is the
                # default but make it explicit so a future refactor can't
                # silently flip it.
                page.screenshot(
                    path=str(png_path),
                    full_page=False,
                    clip={"x": 0, "y": 0, "width": width, "height": height},
                )
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
