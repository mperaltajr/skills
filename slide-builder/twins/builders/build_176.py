"""
Builder for pattern 176: Cover — Minimalist type-only, centered title between rules.

Source HTML: _pattern-library/176_cover-minimalist-type-only.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    DRAFT_BG, DRAFT_TEXT, TEXT_MID, TEXT_FAINT, CARD_BORDER,
)
from pptx.enum.shapes import MSO_SHAPE


def build():
    prs, slide = new_slide()


    # Centered content — vertical center
    cx = 1280 // 2
    block_top = 200

    # Rule top
    add_rect(slide, "cover-rule-top", cx - 60, block_top, 120, 2, BRAND_ACCENT)
    # Title
    title_y = block_top + 50
    add_text(slide, "cover-deck-title",
             "A <strong>Focused</strong> Approach to Transforming Enterprise Performance",
             x_px=cx - 400, y_px=title_y, w_px=800, h_px=160,
             font_size_px=42, color=BRAND_PRIMARY, bold=True, align="center",
             emphasis_color=BRAND_ACCENT)
    # Rule bottom
    add_rect(slide, "cover-rule-bottom", cx - 40, title_y + 180, 80, 3, BRAND_ACCENT)
    # Subtitle
    sub_y = title_y + 200
    add_text(slide, "cover-tagline", "Strategic Priorities and Path to Value Creation",
             x_px=cx - 350, y_px=sub_y, w_px=700, h_px=26,
             font_size_px=18, color=TEXT_MID, italic=True, align="center")
    # Meta
    meta_y = sub_y + 40
    add_text(slide, "cover-client-name", "Client Name",
             x_px=cx - 110, y_px=meta_y, w_px=110, h_px=18,
             font_size_px=14, color=BRAND_PRIMARY_MID, bold=True, align="right")
    # Meta separator dot
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                  px_to_emu(cx - 2), px_to_emu(meta_y + 6),
                                  px_to_emu(4), px_to_emu(4))
    dot.name = "cover-meta-sep"
    dot.fill.solid()
    dot.fill.fore_color.rgb = TEXT_FAINT
    dot.line.fill.background()
    add_text(slide, "cover-date", "May 2026",
             x_px=cx + 12, y_px=meta_y, w_px=110, h_px=18,
             font_size_px=12, color=TEXT_FAINT, align="left")

    # Footer
    add_text(slide, "page-number", "176",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "176_cover-minimalist-type-only.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
