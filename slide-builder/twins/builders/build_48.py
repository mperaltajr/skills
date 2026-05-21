"""
Builder for pattern 48: Venn overlap insight — two circles + center lens.

SVG-decompose pattern (per SHAPE-ROLES table): build venn primitives natively.

Source HTML: _pattern-library/48_venn-overlap-insight.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu, px_to_pt,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.enum.shapes import MSO_SHAPE


def _add_oval(slide, shape_id, x, y, w, h, fill, transparency=None):
    """Add an oval (circle) shape with given fill."""
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
        # Set fill transparency via XML
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
    add_chrome(slide)

    add_title_block(
        slide,
        title="Knowledge alone doesn't change behavior — only the intersection of both creates durable advantage.",
        subtitle="Each circle solves one gap on its own. The insight lives where they overlap.",
        title_h=64,
        subtitle_h=22,
        brand_rule_w=48,
    )

    # Venn canvas: 880x340 centered, top=190
    venn_left = (1280 - 880) // 2  # 200
    venn_top = 190

    # Side labels above circles
    add_text(
        slide, "venn-circle-left-label", "GAP 1 — KNOWLEDGE",
        x_px=venn_left + 56, y_px=venn_top, w_px=300, h_px=14,
        font_size_px=11, color=BRAND_PRIMARY, bold=True, uppercase=True,
    )
    add_text(
        slide, "venn-circle-right-label", "GAP 2 — BEHAVIOR",
        x_px=venn_left + 880 - 56 - 300, y_px=venn_top, w_px=300, h_px=14,
        font_size_px=11, color=BRAND_ACCENT, bold=True, align="right", uppercase=True,
    )

    # Circles: 340x340. Left circle at x=venn_left+100, right at venn_left+880-100-340
    circle_d = 340
    left_cx = venn_left + 100
    right_cx = venn_left + 880 - 100 - circle_d
    circ_y = venn_top

    _add_oval(slide, "venn-circle-left", left_cx, circ_y, circle_d, circle_d, BRAND_PRIMARY, transparency=0.12)
    _add_oval(slide, "venn-circle-right", right_cx, circ_y, circle_d, circle_d, BRAND_ACCENT, transparency=0.18)

    # Left circle text (anchored in left lobe — not under center overlap)
    add_text(
        slide, "venn-circle-left-tag", "SOLVES THE KNOWLEDGE GAP",
        x_px=left_cx + 50, y_px=circ_y + 110, w_px=180, h_px=14,
        font_size_px=10, color=WHITE, bold=True, uppercase=True,
    )
    add_text(
        slide, "venn-circle-left-head", "What we know",
        x_px=left_cx + 50, y_px=circ_y + 130, w_px=180, h_px=24,
        font_size_px=18, color=WHITE, bold=True,
    )
    add_text(
        slide, "venn-circle-left-body",
        "Understanding how the business actually makes money — sort, linehaul, clearance economics.",
        x_px=left_cx + 50, y_px=circ_y + 160, w_px=180, h_px=64,
        font_size_px=11, color=WHITE,
    )

    # Right circle text (anchored in right lobe)
    add_text(
        slide, "venn-circle-right-tag", "SOLVES THE BEHAVIOR GAP",
        x_px=right_cx + circle_d - 50 - 180, y_px=circ_y + 110, w_px=180, h_px=14,
        font_size_px=10, color=WHITE, bold=True, align="right", uppercase=True,
    )
    add_text(
        slide, "venn-circle-right-head", "How we think",
        x_px=right_cx + circle_d - 50 - 180, y_px=circ_y + 130, w_px=180, h_px=24,
        font_size_px=18, color=WHITE, bold=True, align="right",
    )
    add_text(
        slide, "venn-circle-right-body",
        "Teams that frame problems and challenge thinking — not order-takers.",
        x_px=right_cx + circle_d - 50 - 180, y_px=circ_y + 160, w_px=180, h_px=64,
        font_size_px=11, color=WHITE, align="right",
    )

    # Overlap lens — 150x150 centered
    lens_d = 150
    lens_x = venn_left + (880 - lens_d) // 2
    lens_y = venn_top + (circle_d - lens_d) // 2
    _add_oval(slide, "venn-overlap", lens_x, lens_y, lens_d, lens_d, BRAND_PRIMARY)

    add_text(
        slide, "venn-overlap-label", "BOTH TOGETHER",
        x_px=lens_x, y_px=lens_y + 38, w_px=lens_d, h_px=12,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True,
    )
    add_text(
        slide, "venn-overlap-text", "Durable advantage",
        x_px=lens_x, y_px=lens_y + 56, w_px=lens_d, h_px=24,
        font_size_px=13, color=WHITE, bold=True, align="center",
    )
    add_text(
        slide, "venn-overlap-eq", "Credibility + Influence",
        x_px=lens_x, y_px=lens_y + 86, w_px=lens_d, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, align="center",
    )

    # Implication strip at bottom
    imp_y = 720 - 56 - 96
    add_rect(slide, "implication-bg", 56, imp_y, 1280 - 112, 50, BRAND_PRIMARY)
    add_rect(slide, "implication-accent", 56, imp_y, 4, 50, BRAND_ACCENT)
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

    add_convergence(
        slide,
        "Either circle alone solves half the problem. The intersection is the only place the answer lives.",
    )

    add_footer(slide, page_num=48)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "48_venn-overlap-insight.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
