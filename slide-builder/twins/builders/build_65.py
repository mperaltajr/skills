"""
Builder for pattern 65: Capability heatmap.

Title + right-aligned Low→High legend swatch strip + 6-row × 4-column heatmap
(capabilities × seniority levels) with 5-step color ramp. Convergence band below.

Source HTML: _pattern-library/65_heatmap-capability.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

# Heat ramp
HEAT_1 = RGBColor(0xF8, 0xF4, 0xFC)  # card-bg
HEAT_2 = RGBColor(0xE5, 0xD5, 0xF0)  # card-border
HEAT_3 = BRAND_ACCENT_SOFT
HEAT_4 = BRAND_ACCENT
HEAT_5 = BRAND_PRIMARY_MID


def heat_color(level):
    return [HEAT_1, HEAT_2, HEAT_3, HEAT_4, HEAT_5][level - 1]


def heat_text_color(level):
    return [BRAND_PRIMARY_MID, BRAND_PRIMARY, WHITE, WHITE, WHITE][level - 1]


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # --- Title block --- (widened + sized to keep title on one line)
    # Font dropped to 20px so the full sentence with strong emphasis fits one line at w=1152.
    add_text(
        slide, "title",
        "Practice capability heatmap — <strong>where Slide Lab adds the most lift.</strong>",
        x_px=64, y_px=50, w_px=1152, h_px=36,
        font_size_px=20, color=TEXT_DARK, bold=True,
        emphasis_color=BRAND_PRIMARY,
    )
    add_text(
        slide, "subtitle",
        "Self-rated proficiency across six capabilities by seniority level. Storyline coaching and strategy framing show the steepest gap at Manager.",
        x_px=64, y_px=96, w_px=1152, h_px=40,
        font_size_px=13, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=148, w_px=56, h_px=3, fill_color=BRAND_ACCENT)

    # --- Legend — BELOW subheadline (HARD RULE: top-y >= 230, right-aligned to x ~1240) ---
    leg_y = 232
    leg_x = 1280 - 64 - 220
    add_text(
        slide, "legend-low", "Low",
        x_px=leg_x, y_px=leg_y, w_px=30, h_px=18,
        font_size_px=10, color=TEXT_MID, bold=True,
        letter_spacing_px=1.5, uppercase=True, anchor="middle",
    )
    sw_w = 22
    sw_h = 14
    for i in range(5):
        n = i + 1
        sx = leg_x + 36 + i * (sw_w + 2)
        sw = add_rect(slide, f"legend-sw-{n}", sx, leg_y + 2, sw_w, sw_h, heat_color(n))
        sw.line.color.rgb = CARD_BORDER
        sw.line.width = 6350
    add_text(
        slide, "legend-high", "High",
        x_px=leg_x + 36 + 5 * (sw_w + 2) + 6, y_px=leg_y, w_px=40, h_px=18,
        font_size_px=10, color=TEXT_MID, bold=True,
        letter_spacing_px=1.5, uppercase=True, anchor="middle",
    )

    # --- Heatmap grid (6 rows × 4 cols + 1 row-label col) ---
    # grid_top shifted to clear legend (legend at y=232, ~20px tall, bottom ~252)
    grid_top = 262
    grid_left = 150
    grid_right = 1130
    grid_w = grid_right - grid_left
    row_label_w = 200
    col_count = 4
    col_gap = 4
    row_gap = 4
    cell_w = (grid_w - row_label_w - (col_count - 1) * col_gap) // col_count
    cell_h = 42

    cols = ["Manager", "Senior Manager", "Director", "Partner"]
    rows = [
        ("Strategy framing",   [2, 3, 4, 5]),
        ("Storyline coaching", [1, 2, 4, 5]),
        ("Visual design",      [3, 3, 2, 2]),
        ("Data analysis",      [4, 4, 3, 2]),
        ("Brand application",  [4, 3, 3, 3]),
        ("Client communication", [2, 3, 4, 5]),
    ]

    # Column headers
    header_h = 32
    for ci, cname in enumerate(cols):
        n = ci + 1
        cx = grid_left + row_label_w + ci * (cell_w + col_gap)
        add_text(
            slide, f"col-header-{n}", cname,
            x_px=cx, y_px=grid_top, w_px=cell_w, h_px=header_h,
            font_size_px=10, color=BRAND_PRIMARY_MID, bold=True,
            letter_spacing_px=2, uppercase=True, align="center", anchor="middle",
        )
    add_rect(slide, "col-header-rule", grid_left + row_label_w, grid_top + header_h,
             grid_w - row_label_w, 2, CARD_BORDER)

    # Row cells
    grid_body_top = grid_top + header_h + 6
    for ri, (rname, values) in enumerate(rows):
        rn = ri + 1
        ry = grid_body_top + ri * (cell_h + row_gap)
        # Row label
        add_text(
            slide, f"row-label-{rn}", rname,
            x_px=grid_left, y_px=ry, w_px=row_label_w - 12, h_px=cell_h,
            font_size_px=12, color=BRAND_PRIMARY_MID, bold=True,
            letter_spacing_px=1.5, uppercase=True, align="right", anchor="middle",
        )
        for ci, v in enumerate(values):
            cn = ci + 1
            cx = grid_left + row_label_w + ci * (cell_w + col_gap)
            cell = add_rect(slide, f"cell-{rn}-{cn}", cx, ry, cell_w, cell_h, heat_color(v))
            cell.line.color.rgb = WHITE
            cell.line.width = 6350
            add_text(
                slide, f"cell-{rn}-{cn}-text", str(v),
                x_px=cx, y_px=ry, w_px=cell_w, h_px=cell_h,
                font_size_px=20, color=heat_text_color(v), bold=True,
                align="center", anchor="middle",
            )

    # --- Convergence band ---
    add_convergence(
        slide,
        "Biggest lift opportunity sits at Manager level — storyline coaching and strategy framing are the weakest cells across the practice.",
    )
    add_footer(slide, page_num=65)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "65_heatmap-capability.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
