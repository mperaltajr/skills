"""
Builder for pattern 13: 2x2 framework quadrants (Quick wins / Strategic bets / Fillers / Avoid).

Source HTML: _pattern-library/13_2x2-framework-quadrants.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Where to focus first — high-impact, low-effort wins.",
        subtitle="Bank credibility in the top-left before spending capital on the strategic bet.",
        title_h=68,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Matrix: y-axis 40px + grid + x-axis
    grid_left = 56
    y_axis_w = 40
    grid_x = grid_left + y_axis_w + 14
    grid_w = 1280 - 112 - y_axis_w - 14
    grid_top = 230
    grid_h = 320
    cell_w = (grid_w - 4) // 2
    cell_h = (grid_h - 4) // 2

    # Y-axis label (vertical text — approximate as rotated text via wide narrow box)
    add_text(
        slide, "quadrant-y-axis-label", "IMPACT",
        x_px=grid_left, y_px=grid_top + grid_h // 2 - 8, w_px=y_axis_w, h_px=16,
        font_size_px=10, color=BRAND_PRIMARY, bold=True, uppercase=True, align="center",
    )
    # Y ticks
    add_text(
        slide, "quadrant-y-high", "HIGH",
        x_px=grid_left, y_px=grid_top + 6, w_px=y_axis_w, h_px=14,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True, align="center",
    )
    add_text(
        slide, "quadrant-y-low", "LOW",
        x_px=grid_left, y_px=grid_top + grid_h - 22, w_px=y_axis_w, h_px=14,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True, align="center",
    )

    # TL: Quick wins — brand-accent fill with brand-primary outline
    tl_x = grid_x
    tl_y = grid_top
    tl_rect = add_rect(slide, "quadrant-tl-bg", tl_x, tl_y, cell_w, cell_h, BRAND_ACCENT)
    tl_rect.line.color.rgb = BRAND_PRIMARY
    tl_rect.line.width = 28575  # ~3px
    add_text(
        slide, "quadrant-tl-label", "START HERE",
        x_px=tl_x + 18, y_px=tl_y + 14, w_px=cell_w - 36, h_px=14,
        font_size_px=9, color=WHITE, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-tl-name", "Quick wins",
        x_px=tl_x + 18, y_px=tl_y + 32, w_px=cell_w - 36, h_px=28,
        font_size_px=20, color=WHITE, bold=True,
    )
    add_text(
        slide, "quadrant-tl-directive", "Ship in weeks. Earn the right to do the hard work.",
        x_px=tl_x + 18, y_px=tl_y + 62, w_px=cell_w - 36, h_px=22,
        font_size_px=12, color=WHITE, italic=True,
    )
    add_text(
        slide, "quadrant-tl-body",
        "• Pilot Slide Lab on one live engagement\n"
        "• Roll out QC framework to two teams\n"
        "• Publish the pattern library internally",
        x_px=tl_x + 18, y_px=tl_y + 92, w_px=cell_w - 36, h_px=cell_h - 100,
        font_size_px=12, color=WHITE,
    )

    # TR: Strategic bets — brand-primary fill
    tr_x = grid_x + cell_w + 4
    tr_y = grid_top
    add_rect(slide, "quadrant-tr-bg", tr_x, tr_y, cell_w, cell_h, BRAND_PRIMARY)
    add_text(
        slide, "quadrant-tr-label", "PLAN DELIBERATELY",
        x_px=tr_x + 18, y_px=tr_y + 14, w_px=cell_w - 36, h_px=14,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-tr-name", "Strategic bets",
        x_px=tr_x + 18, y_px=tr_y + 32, w_px=cell_w - 36, h_px=28,
        font_size_px=20, color=WHITE, bold=True,
    )
    add_text(
        slide, "quadrant-tr-directive",
        "Sequence after wins land. Requires sponsor air-cover.",
        x_px=tr_x + 18, y_px=tr_y + 62, w_px=cell_w - 36, h_px=22,
        font_size_px=12, color=BRAND_ACCENT_SOFT, italic=True,
    )
    add_text(
        slide, "quadrant-tr-body",
        "• Rebuild brand asset system\n"
        "• Firm-wide narrative coaching program",
        x_px=tr_x + 18, y_px=tr_y + 92, w_px=cell_w - 36, h_px=cell_h - 100,
        font_size_px=12, color=WHITE,
    )

    # BL: Fillers — card-bg
    bl_x = grid_x
    bl_y = grid_top + cell_h + 4
    add_rect(slide, "quadrant-bl-bg", bl_x, bl_y, cell_w, cell_h, CARD_BG)
    add_text(
        slide, "quadrant-bl-label", "FIT IN THE GAPS",
        x_px=bl_x + 18, y_px=bl_y + 14, w_px=cell_w - 36, h_px=14,
        font_size_px=9, color=TEXT_MID, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-bl-name", "Fillers",
        x_px=bl_x + 18, y_px=bl_y + 32, w_px=cell_w - 36, h_px=28,
        font_size_px=20, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "quadrant-bl-directive",
        "Low cost, low signal. Use only when capacity is idle.",
        x_px=bl_x + 18, y_px=bl_y + 62, w_px=cell_w - 36, h_px=22,
        font_size_px=12, color=TEXT_MID, italic=True,
    )
    add_text(
        slide, "quadrant-bl-body",
        "• Refresh internal slide template\n"
        "• Tidy shared drive folder structure",
        x_px=bl_x + 18, y_px=bl_y + 92, w_px=cell_w - 36, h_px=cell_h - 100,
        font_size_px=12, color=TEXT_DARK,
    )

    # BR: Avoid — card-bg faded
    br_x = grid_x + cell_w + 4
    br_y = grid_top + cell_h + 4
    add_rect(slide, "quadrant-br-bg", br_x, br_y, cell_w, cell_h, CARD_BG)
    add_text(
        slide, "quadrant-br-label", "DECLINE POLITELY",
        x_px=br_x + 18, y_px=br_y + 14, w_px=cell_w - 36, h_px=14,
        font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-br-name", "Avoid",
        x_px=br_x + 18, y_px=br_y + 32, w_px=cell_w - 36, h_px=28,
        font_size_px=20, color=TEXT_MID, bold=True,
    )
    add_text(
        slide, "quadrant-br-directive",
        "Costly distractions dressed up as priorities.",
        x_px=br_x + 18, y_px=br_y + 62, w_px=cell_w - 36, h_px=22,
        font_size_px=12, color=TEXT_FAINT, italic=True,
    )
    add_text(
        slide, "quadrant-br-body",
        "• Custom AI model fine-tuning\n"
        "• Bespoke per-partner UI themes",
        x_px=br_x + 18, y_px=br_y + 92, w_px=cell_w - 36, h_px=cell_h - 100,
        font_size_px=12, color=TEXT_FAINT,
    )

    # X-axis below grid
    x_axis_y = grid_top + grid_h + 8
    add_text(
        slide, "quadrant-x-low", "LOW",
        x_px=grid_x, y_px=x_axis_y, w_px=80, h_px=14,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-x-high", "HIGH",
        x_px=grid_x + grid_w - 80, y_px=x_axis_y, w_px=80, h_px=14,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True, align="right",
    )
    add_text(
        slide, "quadrant-x-axis-label", "EFFORT",
        x_px=grid_x, y_px=x_axis_y + 14, w_px=grid_w, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True, uppercase=True, align="center",
    )

    add_convergence(
        slide,
        "Start with quick wins; bank credibility before the strategic bet.",
    )

    add_footer(slide, page_num=13)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "13_2x2-framework-quadrants.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
