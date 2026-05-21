"""
Builder for pattern 176d: Cover — Minimalist type-only, DARK variant.

Light source: twins/builders/build_176.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    cx = 1280 // 2
    block_top = 200

    add_rect(slide, "cover-rule-top", cx - 60, block_top, 120, 2, BRAND_ACCENT_SOFT)
    title_y = block_top + 50
    add_text(slide, "cover-deck-title",
             "A <strong>Focused</strong> Approach to Transforming Enterprise Performance",
             x_px=cx - 400, y_px=title_y, w_px=800, h_px=160,
             font_size_px=42, color=WHITE, bold=True, align="center",
             emphasis_color=BRAND_ACCENT_SOFT)
    add_rect(slide, "cover-rule-bottom", cx - 40, title_y + 180, 80, 3, BRAND_ACCENT_SOFT)
    sub_y = title_y + 200
    add_text(slide, "cover-tagline", "Strategic Priorities and Path to Value Creation",
             x_px=cx - 350, y_px=sub_y, w_px=700, h_px=26,
             font_size_px=18, color=TEXT_ON_DARK_MID, italic=True, align="center")
    meta_y = sub_y + 40
    add_text(slide, "cover-client-name", "Client Name",
             x_px=cx - 110, y_px=meta_y, w_px=110, h_px=18,
             font_size_px=14, color=BRAND_ACCENT_SOFT, bold=True, align="right")
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                  px_to_emu(cx - 2), px_to_emu(meta_y + 6),
                                  px_to_emu(4), px_to_emu(4))
    dot.name = "cover-meta-sep"
    dot.fill.solid()
    dot.fill.fore_color.rgb = TEXT_ON_DARK_FAINT
    dot.line.fill.background()
    add_text(slide, "cover-date", "May 2026",
             x_px=cx + 12, y_px=meta_y, w_px=110, h_px=18,
             font_size_px=12, color=TEXT_ON_DARK_FAINT, align="left")

    add_text(slide, "page-number", "176",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "176d_cover-minimalist-type-only-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
