"""
Builder for pattern 175: Cover — Full-Bleed Photo with title overlay.

Source HTML: _pattern-library/175_cover-full-bleed-photo.html

Cover-only chrome — no standard title block.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

PHOTO_DARK = RGBColor(0x1A, 0x05, 0x33)


def build():
    prs, slide = new_slide()

    # Full-bleed photo simulation (dark gradient → solid PHOTO_DARK as placeholder)
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = PHOTO_DARK

    # Photo bg rect (acts as picture-insertion target placeholder)
    add_rect(slide, "cover-photo-bg", 0, 0, 1280, 720, PHOTO_DARK)
    # Bottom overlay darker for legibility
    add_rect(slide, "cover-bottom-overlay", 0, 380, 1280, 340, RGBColor(0x08, 0x02, 0x14))

    # Accenture wordmark top-right
    add_text(slide, "cover-wordmark", "ACCENTURE",
             x_px=1280 - 24 - 200, y_px=24, w_px=200, h_px=18,
             font_size_px=14, color=WHITE, bold=True, align="right", uppercase=True)

    # Title block bottom-left
    title_x = 56
    title_y = 460
    add_text(slide, "cover-eyebrow", "Driving Resilience in a Volatile World",
             x_px=title_x, y_px=title_y, w_px=680, h_px=24,
             font_size_px=16, color=RGBColor(0xE0, 0xD0, 0xF0), italic=True)
    add_text(slide, "cover-deck-title", "The Future of <strong>Enterprise</strong>\nDigital Transformation",
             x_px=title_x, y_px=title_y + 30, w_px=680, h_px=110,
             font_size_px=40, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT)
    add_rect(slide, "cover-rule",
             x_px=title_x, y_px=title_y + 148, w_px=80, h_px=3,
             fill_color=RGBColor(0xE0, 0xE0, 0xF0))
    add_text(slide, "cover-meta", "CLIENT NAME · MAY 2026 · CONFIDENTIAL",
             x_px=title_x, y_px=title_y + 162, w_px=680, h_px=18,
             font_size_px=11, color=RGBColor(0xA0, 0x90, 0xB8), uppercase=True)

    add_text(slide, "page-number", "175",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=RGBColor(0xA0, 0x90, 0xB8), align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "175_cover-full-bleed-photo.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
