"""
Builder for pattern 21: Stakeholder map (Mendelow influence-by-interest grid).

Source HTML: _pattern-library/21_stakeholder-map.html
2x2 grid with chips inside each quadrant.
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


def _chips(slide, prefix, x, y, width_avail, chips, on_dark=True, accent=False):
    """Lay out chips wrapping horizontally. Returns next available y."""
    cx = x
    cy = y
    chip_h = 22
    row_gap = 6
    for i, label in enumerate(chips):
        n = i + 1
        # Estimate width: 8px per char + 20 padding
        chip_w = min(8 * len(label) + 24, 200)
        if cx + chip_w > x + width_avail:
            cx = x
            cy += chip_h + row_gap
        # Fill colors
        if accent:
            fill = BRAND_ACCENT
            txt = WHITE
        elif on_dark:
            fill = BRAND_PRIMARY_MID  # subdued
            txt = WHITE
        else:
            fill = WHITE
            txt = TEXT_DARK
        chip_rect = add_rect(slide, f"{prefix}-chip-{n}-bg", cx, cy, chip_w, chip_h, fill)
        add_text(
            slide, f"{prefix}-chip-{n}", label,
            x_px=cx, y_px=cy, w_px=chip_w, h_px=chip_h,
            font_size_px=10, color=txt, bold=True,
            align="center", anchor="middle",
        )
        cx += chip_w + 6
    return cy + chip_h


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Stakeholder map — who needs what, when.",
        subtitle="Mendelow's influence-by-interest grid, applied to the pilot's named stakeholders.",
        title_h=68,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Matrix geometry
    grid_left = 64
    y_axis_w = 40
    grid_x = grid_left + y_axis_w
    grid_w = 1280 - 128 - y_axis_w
    grid_top = 230
    grid_h = 320
    cell_w = (grid_w - 6) // 2
    cell_h = (grid_h - 6) // 2

    # Y-axis label and ticks
    add_text(
        slide, "quadrant-y-axis-label", "INFLUENCE",
        x_px=grid_left, y_px=grid_top + grid_h // 2 - 8, w_px=y_axis_w, h_px=16,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True, align="center",
    )
    add_text(
        slide, "quadrant-y-high", "HIGH",
        x_px=grid_left, y_px=grid_top + 4, w_px=y_axis_w, h_px=14,
        font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True, align="center",
    )
    add_text(
        slide, "quadrant-y-low", "LOW",
        x_px=grid_left, y_px=grid_top + grid_h - 18, w_px=y_axis_w, h_px=14,
        font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True, align="center",
    )

    # TL: Keep Satisfied — brand-primary-mid
    tl_x, tl_y = grid_x, grid_top
    add_rect(slide, "quadrant-tl-bg", tl_x, tl_y, cell_w, cell_h, BRAND_PRIMARY_MID)
    add_text(
        slide, "quadrant-tl-label", "HIGH INFLUENCE · LOW INTEREST",
        x_px=tl_x + 14, y_px=tl_y + 12, w_px=cell_w - 28, h_px=14,
        font_size_px=10, color=WHITE, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-tl-name", "KEEP SATISFIED",
        x_px=tl_x + 14, y_px=tl_y + 28, w_px=cell_w - 28, h_px=24,
        font_size_px=17, color=WHITE, bold=True,
    )
    _chips(slide, "quadrant-tl", tl_x + 14, tl_y + 64, cell_w - 28,
           ["Steering Committee", "IT Security", "Legal"], on_dark=True)

    # TR: Manage Closely — brand-primary (focal)
    tr_x, tr_y = grid_x + cell_w + 6, grid_top
    add_rect(slide, "quadrant-tr-bg", tr_x, tr_y, cell_w, cell_h, BRAND_PRIMARY)
    add_text(
        slide, "quadrant-tr-label", "HIGH INFLUENCE · HIGH INTEREST",
        x_px=tr_x + 14, y_px=tr_y + 12, w_px=cell_w - 28, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-tr-name", "MANAGE CLOSELY",
        x_px=tr_x + 14, y_px=tr_y + 28, w_px=cell_w - 28, h_px=24,
        font_size_px=17, color=WHITE, bold=True,
    )
    # FOCUS badge top-right
    add_rect(slide, "quadrant-tr-focus-bg", tr_x + cell_w - 60, tr_y + 10, 50, 18, BRAND_ACCENT)
    add_text(
        slide, "quadrant-tr-focus", "FOCUS",
        x_px=tr_x + cell_w - 60, y_px=tr_y + 10, w_px=50, h_px=18,
        font_size_px=9, color=WHITE, bold=True,
        align="center", anchor="middle",
    )
    _chips(slide, "quadrant-tr", tr_x + 14, tr_y + 64, cell_w - 28,
           ["Program MD", "Practice Lead", "Client Engagement Partner", "CFO"], accent=True)

    # BL: Monitor — card-bg
    bl_x, bl_y = grid_x, grid_top + cell_h + 6
    bl_bg = add_rect(slide, "quadrant-bl-bg", bl_x, bl_y, cell_w, cell_h, CARD_BG)
    bl_bg.line.color.rgb = CARD_BORDER
    bl_bg.line.width = 9525
    add_text(
        slide, "quadrant-bl-label", "LOW INFLUENCE · LOW INTEREST",
        x_px=bl_x + 14, y_px=bl_y + 12, w_px=cell_w - 28, h_px=14,
        font_size_px=10, color=TEXT_FAINT, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-bl-name", "MONITOR",
        x_px=bl_x + 14, y_px=bl_y + 28, w_px=cell_w - 28, h_px=24,
        font_size_px=17, color=TEXT_MID, bold=True,
    )
    _chips(slide, "quadrant-bl", bl_x + 14, bl_y + 64, cell_w - 28,
           ["Vendor PMs", "External advisors"], on_dark=False)

    # BR: Keep Informed — brand-accent-soft
    br_x, br_y = grid_x + cell_w + 6, grid_top + cell_h + 6
    add_rect(slide, "quadrant-br-bg", br_x, br_y, cell_w, cell_h, BRAND_ACCENT_SOFT)
    add_text(
        slide, "quadrant-br-label", "LOW INFLUENCE · HIGH INTEREST",
        x_px=br_x + 14, y_px=br_y + 12, w_px=cell_w - 28, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-br-name", "KEEP INFORMED",
        x_px=br_x + 14, y_px=br_y + 28, w_px=cell_w - 28, h_px=24,
        font_size_px=17, color=TEXT_DARK, bold=True,
    )
    _chips(slide, "quadrant-br", br_x + 14, br_y + 64, cell_w - 28,
           ["Workstream analysts", "Adjacent project leads", "HR"], on_dark=False)

    # X-axis below grid
    xax_y = grid_top + grid_h + 6
    add_text(
        slide, "quadrant-x-low", "LOW",
        x_px=grid_x, y_px=xax_y, w_px=80, h_px=14,
        font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True,
    )
    add_text(
        slide, "quadrant-x-axis-label", "INTEREST",
        x_px=grid_x, y_px=xax_y, w_px=grid_w, h_px=14,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True, align="center",
    )
    add_text(
        slide, "quadrant-x-high", "HIGH",
        x_px=grid_x + grid_w - 80, y_px=xax_y, w_px=80, h_px=14,
        font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True, align="right",
    )

    add_convergence(
        slide,
        "The pilot stands or falls on the four \"Manage Closely\" stakeholders — own those relationships personally.",
    )

    add_footer(slide, page_num=21)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "21_stakeholder-map.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
