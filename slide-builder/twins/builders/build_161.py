"""
Builder for pattern 161: 2x2 quadrant with deep axis labels (Market Attractiveness × Competitive Strength).

Source HTML: _pattern-library/161_2x2-deep-axis-labels.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

TL_BG = RGBColor(0xF0, 0xEB, 0xF8)
TR_BG = CARD_BG
BL_BG = RGBColor(0xFA, 0xFA, 0xFA)
BR_BG = RGBColor(0xF5, 0xF5, 0xF5)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title (28px brand-primary)
    add_text(slide, "title", "Portfolio Positioning Across <strong>Attractiveness & Strength</strong>",
             x_px=48, y_px=58, w_px=1100, h_px=36,
             font_size_px=26, color=BRAND_PRIMARY, bold=True,
             emphasis_color=BRAND_ACCENT)
    add_text(slide, "subtitle",
             "Strategic quadrant view — prioritize investment, harvest, or exit decisions by axis position",
             x_px=48, y_px=96, w_px=1100, h_px=18,
             font_size_px=12, color=TEXT_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 122, 64, 3, BRAND_ACCENT)

    # Matrix area: top:130 left:48 right:48 bottom:60
    ma_x = 48
    ma_y = 138
    ma_w = 1280 - 96
    ma_h = 720 - 60 - ma_y

    # Y-axis strip (left 88px)
    ya_w = 88
    grid_x = ma_x + ya_w + 4
    grid_y = ma_y
    grid_w = ma_w - ya_w - 4
    grid_h = ma_h - 32  # leave room for x-axis strip
    cell_w = grid_w // 2
    cell_h = grid_h // 2

    # Y-axis labels
    add_text(slide, "quadrant-y-high", "STRONG",
             x_px=ma_x, y_px=grid_y + 6, w_px=ya_w, h_px=14,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, align="center", uppercase=True)
    add_text(slide, "quadrant-y-high-desc",
             "Structural cost & capability lead",
             x_px=ma_x, y_px=grid_y + 22, w_px=ya_w, h_px=28,
             font_size_px=8, color=TEXT_MID, align="center")
    add_text(slide, "quadrant-y-low", "WEAK",
             x_px=ma_x, y_px=grid_y + grid_h - 40, w_px=ya_w, h_px=14,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, align="center", uppercase=True)
    add_text(slide, "quadrant-y-low-desc",
             "Scale disadvantage, limited differentiation",
             x_px=ma_x, y_px=grid_y + grid_h - 24, w_px=ya_w, h_px=22,
             font_size_px=8, color=TEXT_MID, align="center")
    # Y-axis title (rotated — we'll approximate horizontal centered)
    add_text(slide, "quadrant-y-axis-label", "COMPETITIVE STRENGTH",
             x_px=ma_x, y_px=grid_y + grid_h // 2 - 8, w_px=ya_w, h_px=16,
             font_size_px=8, color=BRAND_PRIMARY, bold=True, align="center", uppercase=True)

    # Quadrants
    quadrants = [
        ("tl", "Q2", "Harvest & Defend",
         "Protect margin in a low-growth market. Minimize new spend; extract value from existing position.",
         ["Tighten cost structure, renegotiate vendor contracts",
          "Defend key accounts with loyalty programs",
          "Harvest cash to fund star quadrant growth"], TL_BG, BRAND_PRIMARY),
        ("tr", "Q1", "Invest & Grow",
         "Prime strategic territory. Double down on capability advantage in high-attractiveness segments.",
         ["Accelerate M&A and organic expansion",
          "Lock in long-term customer agreements",
          "Build moats through IP and ecosystem plays"], TR_BG, BRAND_ACCENT),
        ("bl", "Q3", "Divest or Exit",
         "Unattractive market with weak competitive position. Reallocate capital unless turnaround is credible.",
         ["Run structured divestiture or wind-down process",
          "Explore JV to share stranded costs",
          "Retain only if strategic linkage is critical"], BL_BG, BRAND_PRIMARY),
        ("br", "Q4", "Selective / Niche",
         "Attractive market, but position is weak. Invest selectively or find a defensible niche to enter.",
         ["Identify micro-segment where scale less critical",
          "Partner or license to acquire position faster",
          "Set clear go/no-go milestones at 12 months"], BR_BG, BRAND_PRIMARY),
    ]
    positions = {"tl": (0, 0), "tr": (1, 0), "bl": (0, 1), "br": (1, 1)}
    for pos, label, name, directive, items, bg, name_color in quadrants:
        col, row = positions[pos]
        qx = grid_x + col * cell_w
        qy = grid_y + row * cell_h
        cell = add_rect(slide, f"quadrant-{pos}-bg", qx, qy, cell_w, cell_h, bg)
        cell.line.color.rgb = CARD_BORDER
        cell.line.width = 9525
        # Corner badge
        add_text(slide, f"quadrant-{pos}-label", label,
                 x_px=qx + cell_w - 40, y_px=qy + 8, w_px=32, h_px=14,
                 font_size_px=8, color=TEXT_FAINT, bold=True, align="right", uppercase=True)
        # Name
        add_text(slide, f"quadrant-{pos}-name", name,
                 x_px=qx + 16, y_px=qy + 14, w_px=cell_w - 60, h_px=22,
                 font_size_px=14, color=name_color, bold=True)
        # Directive
        add_text(slide, f"quadrant-{pos}-directive", directive,
                 x_px=qx + 16, y_px=qy + 40, w_px=cell_w - 32, h_px=38,
                 font_size_px=11, color=TEXT_MID)
        # Items
        items_text = "\n".join("· " + it for it in items)
        add_text(slide, f"quadrant-{pos}-body", items_text,
                 x_px=qx + 16, y_px=qy + 84, w_px=cell_w - 32, h_px=cell_h - 96,
                 font_size_px=10, color=TEXT_DARK)

    # Crosshair lines
    cx = grid_x + grid_w // 2
    cy = grid_y + grid_h // 2
    add_rect(slide, "crosshair-v", cx - 1, grid_y, 2, grid_h, BRAND_ACCENT)
    add_rect(slide, "crosshair-h", grid_x, cy - 1, grid_w, 2, BRAND_ACCENT)

    # X-axis strip
    xa_y = grid_y + grid_h + 4
    add_text(slide, "quadrant-x-low", "LOW",
             x_px=grid_x + 10, y_px=xa_y, w_px=120, h_px=14,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
    add_text(slide, "quadrant-x-low-desc",
             "Slow growth, commoditized, margin pressure",
             x_px=grid_x + 10, y_px=xa_y + 14, w_px=240, h_px=14,
             font_size_px=8, color=TEXT_MID)
    add_text(slide, "quadrant-x-axis-label", "MARKET ATTRACTIVENESS",
             x_px=grid_x, y_px=xa_y + 6, w_px=grid_w, h_px=14,
             font_size_px=10, color=BRAND_PRIMARY, bold=True, align="center", uppercase=True)
    add_text(slide, "quadrant-x-high", "HIGH",
             x_px=grid_x + grid_w - 120, y_px=xa_y, w_px=110, h_px=14,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, align="right", uppercase=True)
    add_text(slide, "quadrant-x-high-desc",
             "Fast-growing, profitable, structural tailwinds",
             x_px=grid_x + grid_w - 260, y_px=xa_y + 14, w_px=248, h_px=14,
             font_size_px=8, color=TEXT_MID, align="right")

    add_footer(slide, page_num=161)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "161_2x2-deep-axis-labels.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
