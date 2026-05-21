"""
Builder for pattern 344: Dark Risk Heat Map.

Source HTML: _pattern-library/344_dark-risk-heat-map.html
Standalone — no light counterpart (light pattern 20 was rejected); structural
ref: 195_risk-vs-opportunity-matrix.

Layout: 5x5 likelihood/impact grid (left) with discrete colored cells (low,
medium, high, critical) and labeled risk bubbles; risk register table (right).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

CELL_LOW = RGBColor(0x1E, 0x4E, 0x3A)        # green tint
CELL_MED = RGBColor(0x6E, 0x52, 0x1E)        # amber tint
CELL_HIGH = RGBColor(0x7A, 0x3E, 0x1E)       # orange tint
CELL_CRIT = RGBColor(0x6E, 0x22, 0x2C)       # red tint
CELL_BORDER = RGBColor(0x44, 0x2A, 0x66)

R1 = RGBColor(0xEF, 0x44, 0x44)
R2 = RGBColor(0xF9, 0x73, 0x16)
R3 = RGBColor(0xDC, 0x26, 0x26)
R4 = RGBColor(0xA1, 0x00, 0xFF)
R5 = RGBColor(0xC7, 0x80, 0xFF)
R6 = RGBColor(0xF5, 0x9E, 0x0B)
R7 = RGBColor(0x38, 0xBD, 0xF8)
R8 = RGBColor(0x4A, 0xDE, 0x80)


def add_oval(slide, name, x, y, size, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                 px_to_emu(x), px_to_emu(y),
                                 px_to_emu(size), px_to_emu(size))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title
    add_text(slide, "title",
             "Program <strong>Risk Heat Map</strong>",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Risk register mapped by likelihood and impact — Q2 2026 snapshot",
             x_px=64, y_px=108, w_px=1100, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Legend
    leg_y = 232
    leg_items = [
        ("Low (1–4)", CELL_LOW), ("Medium (5–9)", CELL_MED),
        ("High (10–14)", CELL_HIGH), ("Critical (15–25)", CELL_CRIT),
    ]
    lx0 = 720
    for i, (lbl, col) in enumerate(leg_items):
        add_rect(slide, f"leg-{i+1}-sw", lx0 + i * 120, leg_y + 4, 14, 10, col)
        add_text(slide, f"leg-{i+1}-lbl", lbl,
                 x_px=lx0 + i * 120 + 18, y_px=leg_y, w_px=100, h_px=18,
                 font_size_px=10, color=TEXT_ON_DARK_MID, anchor="middle")

    # --- Heat map (5x5) ---
    grid_x = 130
    grid_y = 270
    cell_w = 80
    cell_h = 58
    likelihood_labels = ["Almost Certain", "Likely", "Possible", "Unlikely", "Rare"]
    impact_labels = ["Low", "Minor", "Moderate", "Major", "Critical"]

    def cell_class(score):
        if score <= 4:
            return CELL_LOW
        elif score <= 9:
            return CELL_MED
        elif score <= 14:
            return CELL_HIGH
        return CELL_CRIT

    # Cells (row r=5 top → r=1 bottom; col c=1 left → c=5 right)
    for r_idx, r in enumerate([5, 4, 3, 2, 1]):  # top→bottom
        for c_idx, c in enumerate([1, 2, 3, 4, 5]):
            x = grid_x + c_idx * cell_w
            y = grid_y + r_idx * cell_h
            cell = add_rect(slide, f"cell-r{r}-c{c}", x, y, cell_w - 2, cell_h - 2,
                            cell_class(r * c))
            cell.line.color.rgb = CELL_BORDER
            cell.line.width = 6350

    # Y-axis labels (likelihood)
    for r_idx, lbl in enumerate(likelihood_labels):
        y = grid_y + r_idx * cell_h
        add_text(slide, f"y-{r_idx+1}", lbl,
                 x_px=grid_x - 130, y_px=y, w_px=126, h_px=cell_h - 2,
                 font_size_px=10, color=TEXT_ON_DARK_FAINT, anchor="middle",
                 align="right")
    # X-axis labels (impact)
    for c_idx, lbl in enumerate(impact_labels):
        x = grid_x + c_idx * cell_w
        add_text(slide, f"x-{c_idx+1}", lbl,
                 x_px=x, y_px=grid_y + 5 * cell_h + 6, w_px=cell_w - 2, h_px=16,
                 font_size_px=10, color=TEXT_ON_DARK_FAINT, align="center")

    # Axis title
    add_text(slide, "x-title", "IMPACT →",
             x_px=grid_x, y_px=grid_y + 5 * cell_h + 26, w_px=cell_w * 5, h_px=14,
             font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, align="center",
             letter_spacing_px=1.5)
    add_text(slide, "y-title", "↑ LIKELIHOOD",
             x_px=grid_x - 130, y_px=grid_y, w_px=126, h_px=cell_h * 5,
             font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, align="center",
             anchor="middle", letter_spacing_px=1.5)

    # Risk bubbles (R1..R8) — cell center
    def cell_center(c, r):
        x = grid_x + (c - 1) * cell_w + (cell_w - 2) // 2
        y = grid_y + (5 - r) * cell_h + (cell_h - 2) // 2
        return x, y

    risks_on_grid = [
        ("R1", R1, 5, 5),
        ("R2", R2, 4, 5),
        ("R3", R3, 5, 4),
        ("R4", R4, 3, 5),
        ("R5", R5, 4, 4),
        ("R6", R6, 3, 3),
        ("R7", R7, 2, 4),
        ("R8", R8, 2, 2),
    ]
    bub = 22
    for name, col, c, r in risks_on_grid:
        cx, cy = cell_center(c, r)
        add_oval(slide, f"bub-{name}", cx - bub // 2, cy - bub // 2, bub, col)
        add_text(slide, f"bub-{name}-lbl", name,
                 x_px=cx - bub // 2, y_px=cy - bub // 2, w_px=bub, h_px=bub,
                 font_size_px=9, color=WHITE, bold=True,
                 align="center", anchor="middle")

    # --- Risk register (right) ---
    rx, ry, rw = 720, 270, 496
    add_text(slide, "reg-label", "RISK REGISTER — SORTED BY SEVERITY",
             x_px=rx, y_px=ry - 8, w_px=rw, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    risks_full = [
        ("R1", R1, "Data Breach / Regulatory Exposure", "Critical", "Almost Certain", "JK"),
        ("R2", R2, "Third-Party Vendor Failure", "Major", "Almost Certain", "SR"),
        ("R3", R3, "Core Platform Outage", "Critical", "Likely", "MP"),
        ("R4", R4, "Scope Creep — Programme Delay", "Moderate", "Almost Certain", "LT"),
        ("R5", R5, "Key Talent Attrition", "Major", "Likely", "AN"),
        ("R6", R6, "Budget Overrun — Integration Layer", "Moderate", "Possible", "CB"),
        ("R7", R7, "Change Management Resistance", "Minor", "Likely", "PW"),
        ("R8", R8, "Licensing Cost Variance", "Minor", "Unlikely", "HG"),
    ]
    row_top = ry + 14
    row_h = 42
    for i, (rid, col, nm, imp, lik, owner) in enumerate(risks_full):
        y = row_top + i * row_h
        c = add_rect(slide, f"rr-{rid}-bg", rx, y, rw, row_h - 4, CARD_BG_DARK)
        c.line.color.rgb = CARD_BORDER_DARK
        c.line.width = 6350
        add_rect(slide, f"rr-{rid}-strip", rx, y, 3, row_h - 4, col)
        # Badge
        add_rect(slide, f"rr-{rid}-badge", rx + 12, y + 8, 26, row_h - 20, col)
        add_text(slide, f"rr-{rid}-badge-lbl", rid,
                 x_px=rx + 12, y_px=y + 8, w_px=26, h_px=row_h - 20,
                 font_size_px=10, color=WHITE, bold=True,
                 align="center", anchor="middle")
        # Name
        add_text(slide, f"rr-{rid}-name", nm,
                 x_px=rx + 46, y_px=y + 4, w_px=240, h_px=row_h - 8,
                 font_size_px=11, color=WHITE, bold=True, anchor="middle")
        # Chips
        add_text(slide, f"rr-{rid}-imp", imp,
                 x_px=rx + 290, y_px=y + 4, w_px=80, h_px=row_h - 8,
                 font_size_px=9, color=TEXT_ON_DARK_MID, bold=True,
                 align="center", anchor="middle", uppercase=True,
                 letter_spacing_px=0.5)
        add_text(slide, f"rr-{rid}-lik", lik,
                 x_px=rx + 372, y_px=y + 4, w_px=80, h_px=row_h - 8,
                 font_size_px=9, color=TEXT_ON_DARK_MID, bold=True,
                 align="center", anchor="middle", uppercase=True,
                 letter_spacing_px=0.5)
        # Owner
        add_oval(slide, f"rr-{rid}-owner-bg", rx + rw - 28, y + 8, 22, BRAND_PRIMARY)
        # ring effect via line
        add_text(slide, f"rr-{rid}-owner", owner,
                 x_px=rx + rw - 28, y_px=y + 8, w_px=22, h_px=22,
                 font_size_px=8, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", anchor="middle")

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "344",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "344_dark-risk-heat-map.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
