"""
Builder for pattern 17: Before-after transformation.

Source HTML: _pattern-library/17_before-after-transformation.html
3-column: BEFORE (42%) | ARROW (16%) | AFTER (42%).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.enum.shapes import MSO_SHAPE


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="What changed in four weeks of pilot.",
        subtitle="Same teams, same deck volume. Different discipline — and the workflow followed.",
        title_h=68,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Transformation grid: 42/16/42
    grid_left = 56
    grid_w = 1280 - 112
    arrow_w = int(grid_w * 16 / 100)
    panel_w = (grid_w - arrow_w) // 2
    panel_top = 220
    panel_h = 340
    after_overlap = 10  # AFTER pops up 10px

    # BEFORE panel
    before_x = grid_left
    bp = add_rect(slide, "before-panel-bg", before_x, panel_top, panel_w, panel_h, CARD_BG)
    bp.line.color.rgb = CARD_BORDER
    bp.line.width = 9525
    add_text(
        slide, "before-panel-label", "BEFORE · WEEK 0",
        x_px=before_x + 24, y_px=panel_top + 18, w_px=panel_w - 48, h_px=16,
        font_size_px=11, color=TEXT_MID, bold=True, uppercase=True,
    )
    add_text(
        slide, "before-panel-heading", "Disconnected deck workflow",
        x_px=before_x + 24, y_px=panel_top + 42, w_px=panel_w - 48, h_px=28,
        font_size_px=20, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "before-panel-body",
        "• Slide deck assembled bottom-up from workstream findings\n"
        "• Argument lost as bullets compound across review cycles\n"
        "• Three rounds of partner edits per deck typical\n"
        "• 11 days median from kickoff to final",
        x_px=before_x + 24, y_px=panel_top + 86, w_px=panel_w - 48, h_px=panel_h - 100,
        font_size_px=13, color=TEXT_MID,
    )

    # ARROW column
    arrow_x = before_x + panel_w
    add_text(
        slide, "transformation-arrow-label-top", "PILOT",
        x_px=arrow_x, y_px=panel_top + panel_h // 2 - 56, w_px=arrow_w, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True, align="center",
    )
    # Arrow shape (RIGHT_ARROW)
    arrow_shape_w = arrow_w - 16
    arrow_shape_h = 50
    arrow_sx = arrow_x + 8
    arrow_sy = panel_top + panel_h // 2 - 25
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW,
        px_to_emu(arrow_sx), px_to_emu(arrow_sy),
        px_to_emu(arrow_shape_w), px_to_emu(arrow_shape_h),
    )
    arrow.name = "transformation-arrow"
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = BRAND_ACCENT
    arrow.line.fill.background()
    add_text(
        slide, "transformation-arrow-label-bottom", "WEEKS 1–4",
        x_px=arrow_x, y_px=panel_top + panel_h // 2 + 36, w_px=arrow_w, h_px=14,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True, align="center",
    )

    # AFTER panel (brand-primary, white text, pops up)
    after_x = arrow_x + arrow_w
    after_y = panel_top - after_overlap
    after_h = panel_h + after_overlap
    add_rect(slide, "after-panel-bg", after_x, after_y, panel_w, after_h, BRAND_PRIMARY)
    add_text(
        slide, "after-panel-label", "AFTER · WEEK 4",
        x_px=after_x + 24, y_px=after_y + 24, w_px=panel_w - 48, h_px=16,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "after-panel-heading", "Structured argument-first workflow",
        x_px=after_x + 24, y_px=after_y + 48, w_px=panel_w - 48, h_px=28,
        font_size_px=20, color=WHITE, bold=True,
    )
    add_text(
        slide, "after-panel-body",
        "• Governing thought drives the deck structure\n"
        "• Each slide carries one argument; reviews sharpen, not pile on\n"
        "• One round of partner edits\n"
        "• 5 days median from kickoff to final",
        x_px=after_x + 24, y_px=after_y + 92, w_px=panel_w - 48, h_px=after_h - 110,
        font_size_px=13, color=WHITE,
    )

    add_convergence(
        slide,
        "The change isn't a tool — it's a discipline. The tool just enforces it.",
    )

    add_footer(slide, page_num=17)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "17_before-after-transformation.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
