"""
Builder for pattern 175d: Cover — Full-Bleed Photo, DARK variant.

Light source: twins/builders/build_175.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

PHOTO_DARK = RGBColor(0x1A, 0x05, 0x33)
TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)


def build():
    prs, slide = new_slide()

    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = PHOTO_DARK

    add_rect(slide, "cover-photo-bg", 0, 0, 1280, 720, PHOTO_DARK)
    add_rect(slide, "cover-bottom-overlay", 0, 380, 1280, 340, RGBColor(0x08, 0x02, 0x14))

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
             fill_color=BRAND_ACCENT_SOFT)
    add_text(slide, "cover-meta", "CLIENT NAME · MAY 2026",
             x_px=title_x, y_px=title_y + 162, w_px=680, h_px=18,
             font_size_px=11, color=TEXT_ON_DARK_MID, uppercase=True)

    add_text(slide, "page-number", "175",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "175d_cover-full-bleed-photo-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
