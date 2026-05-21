"""
Builder for pattern 130d: Capability ladder — dark variant.

Source HTML: _pattern-library/130_capability-ladder-dark.html
Light template: twins/builders/build_130.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

# Step background colors for dark mode — tier 1 (bottom) is darkest CARD_BG_DARK,
# tier 6 (top) is brightest BRAND_ACCENT.
TIER_BG = {
    6: BRAND_ACCENT,
    5: BRAND_ACCENT_SOFT,
    4: RGBColor(0x7B, 0x4D, 0xB0),
    3: RGBColor(0x5C, 0x2D, 0x87),
    2: RGBColor(0x46, 0x26, 0x68),
    1: CARD_BG_DARK,
}


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(slide, "title",
             "<strong>Accelerated path to Senior requires ML proficiency</strong>",
             x_px=64, y_px=20, w_px=1000, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "70% of recent promotions met the ML competency threshold early — Data Analytics Career Ladder",
             x_px=64, y_px=108, w_px=900, h_px=20,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 130, 64, 3, BRAND_ACCENT_SOFT)

    # Ladder area
    area_x = 48
    area_y = 220
    area_w = 1280 - 96
    area_h = 720 - 100 - 220
    step_h = 64
    step_gap = 5

    widths_pct = {6: 0.42, 5: 0.53, 4: 0.64, 3: 0.75, 2: 0.87, 1: 1.0}

    tier_data = [
        (6, "L6", "Director, Analytics", "12+ yrs",
         ["Enterprise analytics strategy & P&L ownership",
          "C-suite stakeholder management & executive storytelling",
          "Cross-portfolio talent development & org design"], "Target"),
        (5, "L5", "Analytics Manager", "8-12 yrs",
         ["Team leadership & performance management (5-10 reports)",
          "Program-level roadmap planning & budget accountability",
          "Advanced ML deployment & production monitoring"], None),
        (4, "L4", "Lead Analyst", "5-8 yrs",
         ["Cross-functional project leadership & deliverable ownership",
          "ML model development, validation & business interpretation",
          "Mentoring junior analysts & setting team data standards"], None),
        (3, "L3", "Senior Analyst", "3-5 yrs",
         ["End-to-end pipeline ownership in Python / SQL / Spark",
          "ML proficiency (regression, classification, clustering)",
          "Stakeholder-facing insight communication & self-service BI"], "Current Level"),
        (2, "L2", "Analyst II", "1-3 yrs",
         ["Advanced SQL querying, ETL development & data modelling",
          "Dashboard & report development (Tableau / Power BI)",
          "Introduction to statistical analysis & A/B testing"], None),
        (1, "L1", "Analyst I", "0-1 yr",
         ["Foundational SQL & data extraction from structured sources",
          "Excel / Google Sheets proficiency & basic data storytelling",
          "Data quality checks, documentation & process adherence"], None),
    ]

    for idx, (tier, lvl, name, yrs, comps, badge) in enumerate(tier_data):
        sy = area_y + idx * (step_h + step_gap)
        sw = int(area_w * widths_pct[tier])
        bg_color = TIER_BG[tier]

        add_rect(slide, f"tier-{tier}-bg", area_x, sy, sw, step_h, bg_color)

        if tier == 3:
            add_rect(slide, "tier-current-arrow", area_x, sy, 4, step_h, BRAND_ACCENT)

        # All text white on dark mode
        add_text(slide, f"tier-{tier}-label", lvl,
                 x_px=area_x + 14, y_px=sy + 22, w_px=48, h_px=18,
                 font_size_px=9, color=WHITE, bold=True, align="center", uppercase=True)

        add_text(slide, f"tier-{tier}-name", name,
                 x_px=area_x + 78, y_px=sy + 14, w_px=148, h_px=18,
                 font_size_px=13, color=WHITE, bold=True)
        add_text(slide, f"tier-{tier}-desc", yrs,
                 x_px=area_x + 78, y_px=sy + 34, w_px=148, h_px=14,
                 font_size_px=10, color=WHITE)

        comp_text = " · ".join(comps)
        add_text(slide, f"tier-{tier}-body", comp_text,
                 x_px=area_x + 240, y_px=sy + 10, w_px=sw - 360, h_px=48,
                 font_size_px=10, color=WHITE)

        if badge:
            if "Current" in badge:
                add_rect(slide, "tier-current-chip-bg", area_x + sw - 110, sy + 20, 96, 22, BRAND_ACCENT)
                add_text(slide, "tier-current-chip", badge,
                         x_px=area_x + sw - 110, y_px=sy + 20, w_px=96, h_px=22,
                         font_size_px=9, color=WHITE, bold=True, align="center",
                         anchor="middle", uppercase=True)
            else:
                add_text(slide, "tier-target-chip", badge,
                         x_px=area_x + sw - 90, y_px=sy + 22, w_px=72, h_px=18,
                         font_size_px=9, color=WHITE, bold=True, align="center",
                         uppercase=True)

    # Progression arrow at right
    arrow_x = 1280 - 48 - 30
    add_rect(slide, "progression-arrow", arrow_x, area_y + 20, 2, area_h - 60, BRAND_ACCENT_SOFT)
    add_text(slide, "progression-arrow-label", "PROGRESSION",
             x_px=arrow_x - 30, y_px=area_y + area_h // 2 - 8, w_px=60, h_px=16,
             font_size_px=8, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True, align="center")

    add_text(slide, "convergence",
             "70% of promotions to Senior Analyst met the ML proficiency threshold "
             "before the standard tenure — accelerated path is ML-gated.",
             x_px=64, y_px=720 - 60, w_px=1280 - 128, h_px=18,
             font_size_px=12, color=BRAND_ACCENT_SOFT, italic=True, align="center")

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "130",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "130d_capability-ladder-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
