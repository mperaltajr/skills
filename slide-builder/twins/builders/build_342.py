"""
Builder for pattern 342: Dark Capability Maturity grid.

Source HTML: _pattern-library/342_dark-capability-maturity.html
Standalone — closest light reference: 222_maturity-model-assessment.

Layout: 6-row × 5-col maturity grid (left), with current/target dots per row;
right sidebar with 3 priority gap cards. Legend top-right per rule.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
CURRENT_COLOR = RGBColor(0xC7, 0x80, 0xFF)  # accent soft
TARGET_COLOR = RGBColor(0x22, 0xC5, 0x5E)
CELL_BORDER = RGBColor(0x44, 0x2A, 0x66)
CURRENT_COL_HIGHLIGHT = RGBColor(0x37, 0x1B, 0x55)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title block
    add_text(slide, "title",
             "Capability Maturity: <strong>Current vs. Target State</strong>",
             x_px=64, y_px=20, w_px=900, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Across six domains — three priority gaps require immediate intervention",
             x_px=64, y_px=108, w_px=900, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # --- Legend (top-right) ---
    leg_y = 232
    add_rect(slide, "legend-current-dot", 850, leg_y + 4, 10, 10, CURRENT_COLOR)
    add_text(slide, "legend-current", "Current level",
             x_px=866, y_px=leg_y, w_px=110, h_px=18,
             font_size_px=11, color=TEXT_ON_DARK_MID, anchor="middle")
    add_rect(slide, "legend-target-dot", 982, leg_y + 4, 10, 10, TARGET_COLOR)
    add_text(slide, "legend-target", "Target level",
             x_px=998, y_px=leg_y, w_px=110, h_px=18,
             font_size_px=11, color=TEXT_ON_DARK_MID, anchor="middle")
    add_rect(slide, "legend-col-swatch", 1118, leg_y + 4, 18, 10, CURRENT_COL_HIGHLIGHT)
    add_text(slide, "legend-col", "Current column",
             x_px=1140, y_px=leg_y, w_px=80, h_px=18,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, anchor="middle")

    # --- Maturity grid ---
    grid_x = 64
    grid_y = 260
    row_label_w = 130
    col_w = 100
    row_h = 50
    levels = ["Initial", "Managed", "Defined", "Quantified", "Optimizing"]
    rows = [
        ("Data", 2, 4),
        ("Process", 3, 5),
        ("Technology", 2, 5),
        ("People", 3, 4),
        ("Governance", 1, 3),
        ("Culture", 2, 3),
    ]

    # Column headers
    for j, lvl in enumerate(levels):
        cx = grid_x + row_label_w + j * col_w
        add_text(slide, f"col-header-{j+1}", f"L{j+1} · {lvl}",
                 x_px=cx, y_px=grid_y, w_px=col_w, h_px=22,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", anchor="middle", uppercase=True,
                 letter_spacing_px=0.5)

    # Rows
    body_y = grid_y + 26
    for i, (label, cur, tgt) in enumerate(rows):
        ry = body_y + i * row_h
        # Row header
        add_text(slide, f"row-header-{i+1}", label,
                 x_px=grid_x, y_px=ry, w_px=row_label_w - 8, h_px=row_h - 4,
                 font_size_px=12, color=WHITE, bold=True, anchor="middle")
        for j in range(5):
            cx = grid_x + row_label_w + j * col_w
            # cell bg — highlight current column
            cell_bg = CURRENT_COL_HIGHLIGHT if (j + 1) == cur else CARD_BG_DARK
            cell = add_rect(slide, f"cell-{i+1}-{j+1}", cx, ry, col_w - 4, row_h - 4,
                            cell_bg)
            cell.line.color.rgb = CELL_BORDER
            cell.line.width = 6350
            if (j + 1) == cur:
                add_rect(slide, f"dot-cur-{i+1}",
                         cx + (col_w - 4) // 2 - 7, ry + (row_h - 4) // 2 - 7,
                         14, 14, CURRENT_COLOR)
            if (j + 1) == tgt:
                add_rect(slide, f"dot-tgt-{i+1}",
                         cx + (col_w - 4) // 2 - 7, ry + (row_h - 4) // 2 - 7,
                         14, 14, TARGET_COLOR)

    # --- Sidebar: Priority gaps ---
    side_x = 830
    side_y = 260
    side_w = 386
    add_text(slide, "sidebar-label", "GAP SUMMARY — PRIORITY ACTIONS",
             x_px=side_x, y_px=side_y, w_px=side_w, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    gaps = [
        ("P1 · High Impact", "Technology Modernisation",
         "3-level gap; legacy stack blocks scalability. Initiate cloud migration roadmap Q3."),
        ("P2 · High Impact", "Governance Framework",
         "Initial-state governance creates regulatory exposure. Define policies and ownership by Q4."),
        ("P3 · Medium Impact", "Data Capability Uplift",
         "Move from ad-hoc to quantified. Invest in data platform and literacy programme."),
    ]
    gap_top = side_y + 24
    gap_h = 108
    for i, (pri, title, body) in enumerate(gaps):
        gy = gap_top + i * (gap_h + 6)
        c = add_rect(slide, f"gap-{i+1}-bg", side_x, gy, side_w, gap_h, CARD_BG_DARK)
        c.line.color.rgb = CARD_BORDER_DARK
        c.line.width = 9525
        add_rect(slide, f"gap-{i+1}-accent", side_x, gy, 3, gap_h, BRAND_ACCENT)
        add_text(slide, f"gap-{i+1}-pri", pri,
                 x_px=side_x + 14, y_px=gy + 10, w_px=side_w - 22, h_px=14,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
                 uppercase=True, letter_spacing_px=1)
        add_text(slide, f"gap-{i+1}-title", title,
                 x_px=side_x + 14, y_px=gy + 28, w_px=side_w - 22, h_px=20,
                 font_size_px=14, color=WHITE, bold=True)
        add_text(slide, f"gap-{i+1}-body", body,
                 x_px=side_x + 14, y_px=gy + 50, w_px=side_w - 22, h_px=54,
                 font_size_px=11, color=TEXT_ON_DARK_MID)

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "342",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "342_dark-capability-maturity.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
