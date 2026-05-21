"""
Builder for pattern 48d: Venn overlap insight (dark variant).

Dark recolor of build_48.py — BRAND_PRIMARY background + token swaps.

Source HTML: _pattern-library/48_venn-overlap-insight-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Dark color tokens
TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def _add_oval(slide, shape_id, x, y, w, h, fill, transparency=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        px_to_emu(x), px_to_emu(y),
        px_to_emu(w), px_to_emu(h),
    )
    shape.name = shape_id
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    if transparency is not None:
        from pptx.oxml.ns import qn
        sppr = shape.fill._xPr.find(qn("a:solidFill"))
        if sppr is not None:
            srgb = sppr.find(qn("a:srgbClr"))
            if srgb is not None:
                alpha = srgb.makeelement(qn("a:alpha"), {"val": str(int((1 - transparency) * 100000))})
                srgb.append(alpha)
    return shape


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # --- Canonical chrome (inline) ---
    add_text(
        slide, "title",
        "Knowledge alone doesn't change behavior — only the intersection of both creates durable advantage.",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Each circle solves one gap on its own. The insight lives where they overlap.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    # Venn canvas
    venn_left = (1280 - 880) // 2
    venn_top = 220

    add_text(
        slide, "venn-circle-left-label", "GAP 1 — KNOWLEDGE",
        x_px=venn_left + 56, y_px=venn_top, w_px=300, h_px=14,
        font_size_px=11, color=TEXT_ON_DARK_MID, bold=True, uppercase=True,
    )
    add_text(
        slide, "venn-circle-right-label", "GAP 2 — BEHAVIOR",
        x_px=venn_left + 880 - 56 - 300, y_px=venn_top, w_px=300, h_px=14,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, align="right", uppercase=True,
    )

    circle_d = 300
    left_cx = venn_left + 100
    right_cx = venn_left + 880 - 100 - circle_d
    circ_y = venn_top

    _add_oval(slide, "venn-circle-left", left_cx, circ_y, circle_d, circle_d, BRAND_PRIMARY_MID, transparency=0.12)
    _add_oval(slide, "venn-circle-right", right_cx, circ_y, circle_d, circle_d, BRAND_ACCENT, transparency=0.18)

    add_text(
        slide, "venn-circle-left-tag", "SOLVES THE KNOWLEDGE GAP",
        x_px=left_cx + 50, y_px=circ_y + 90, w_px=180, h_px=14,
        font_size_px=10, color=WHITE, bold=True, uppercase=True,
    )
    add_text(
        slide, "venn-circle-left-head", "What we know",
        x_px=left_cx + 50, y_px=circ_y + 110, w_px=180, h_px=24,
        font_size_px=18, color=WHITE, bold=True,
    )
    add_text(
        slide, "venn-circle-left-body",
        "Understanding how the business actually makes money — sort, linehaul, clearance economics.",
        x_px=left_cx + 50, y_px=circ_y + 140, w_px=180, h_px=64,
        font_size_px=11, color=WHITE,
    )

    add_text(
        slide, "venn-circle-right-tag", "SOLVES THE BEHAVIOR GAP",
        x_px=right_cx + circle_d - 50 - 180, y_px=circ_y + 90, w_px=180, h_px=14,
        font_size_px=10, color=WHITE, bold=True, align="right", uppercase=True,
    )
    add_text(
        slide, "venn-circle-right-head", "How we think",
        x_px=right_cx + circle_d - 50 - 180, y_px=circ_y + 110, w_px=180, h_px=24,
        font_size_px=18, color=WHITE, bold=True, align="right",
    )
    add_text(
        slide, "venn-circle-right-body",
        "Teams that frame problems and challenge thinking — not order-takers.",
        x_px=right_cx + circle_d - 50 - 180, y_px=circ_y + 140, w_px=180, h_px=64,
        font_size_px=11, color=WHITE, align="right",
    )

    # Overlap lens
    lens_d = 130
    lens_x = venn_left + (880 - lens_d) // 2
    lens_y = venn_top + (circle_d - lens_d) // 2
    _add_oval(slide, "venn-overlap", lens_x, lens_y, lens_d, lens_d, BRAND_PRIMARY)

    add_text(
        slide, "venn-overlap-label", "BOTH TOGETHER",
        x_px=lens_x, y_px=lens_y + 28, w_px=lens_d, h_px=12,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True,
    )
    add_text(
        slide, "venn-overlap-text", "Durable advantage",
        x_px=lens_x, y_px=lens_y + 46, w_px=lens_d, h_px=24,
        font_size_px=13, color=WHITE, bold=True, align="center",
    )
    add_text(
        slide, "venn-overlap-eq", "Credibility + Influence",
        x_px=lens_x, y_px=lens_y + 76, w_px=lens_d, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, align="center",
    )

    # Implication strip
    imp_y = 720 - 56 - 96
    add_rect(slide, "implication-bg", 56, imp_y, 1280 - 112, 50, CARD_BG_DARK)
    add_rect(slide, "implication-accent", 56, imp_y, 4, 50, BRAND_ACCENT_SOFT)
    add_text(
        slide, "implication-label", "THE IMPLICATION",
        x_px=78, y_px=imp_y, w_px=140, h_px=50,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, anchor="middle", uppercase=True,
    )
    add_text(
        slide, "implication-text",
        "Two parallel prongs — Mindset Shift plus Ops Intelligence Engine — running simultaneously over 90 days.",
        x_px=240, y_px=imp_y, w_px=1280 - 240 - 78, h_px=50,
        font_size_px=13, color=WHITE, bold=True, anchor="middle",
    )

    # Convergence (text-only on dark bg)
    add_text(
        slide, "convergence",
        "Either circle alone solves half the problem. The intersection is the only place the answer lives.",
        x_px=64, y_px=720 - 78 - 30, w_px=1280 - 128, h_px=30,
        font_size_px=13, color=TEXT_ON_DARK_MID, italic=True,
    )

    # Footer — dark variant
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "48",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "48d_venn-overlap-insight.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
