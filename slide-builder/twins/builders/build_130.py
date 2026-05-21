"""
Builder for pattern 130: Capability ladder (6-tier staircase, widest at bottom).

Source HTML: _pattern-library/130_capability-ladder.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

# Step background colors (per tier, top L6 → bottom L1)
TIER_BG = {
    6: BRAND_PRIMARY,
    5: BRAND_PRIMARY_MID,
    4: RGBColor(0xB6, 0x80, 0xDE),  # accent rgba(161,0,255,0.30)
    3: RGBColor(0xDF, 0xBF, 0xEE),  # rgba(199,128,255,0.40)
    2: RGBColor(0xED, 0xE0, 0xF8),
    1: CARD_BG,
}
DARK_TEXT_TIERS = {1, 2, 3}  # light bg, dark text


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="<strong>Accelerated path to Senior requires ML proficiency</strong>",
        subtitle="70% of recent promotions met the ML competency threshold early — Data Analytics Career Ladder",
        title_h=58, subtitle_h=20, brand_rule_w=64,
    )

    # Ladder area: top:148 left:48 right:48 bottom:100
    area_x = 48
    area_y = 148
    area_w = 1280 - 96
    area_h = 720 - 100 - 148
    step_h = 72
    step_gap = 5

    # Width % per tier (top to bottom)
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
        bg = TIER_BG[tier]
        is_dark = tier not in DARK_TEXT_TIERS

        # Step background
        add_rect(slide, f"tier-{tier}-bg", area_x, sy, sw, step_h, bg)

        # Current-level left accent (tier 3)
        if tier == 3:
            add_rect(slide, "tier-current-arrow", area_x, sy, 4, step_h, BRAND_ACCENT)

        # Level badge (pill)
        label_color = WHITE if is_dark else BRAND_PRIMARY
        add_text(slide, f"tier-{tier}-label", lvl,
                 x_px=area_x + 14, y_px=sy + 22, w_px=48, h_px=18,
                 font_size_px=9, color=label_color, bold=True, align="center", uppercase=True)

        # Title + years
        text_color = WHITE if is_dark else BRAND_PRIMARY
        years_color = WHITE if is_dark else TEXT_MID
        add_text(slide, f"tier-{tier}-name", name,
                 x_px=area_x + 78, y_px=sy + 18, w_px=148, h_px=18,
                 font_size_px=13, color=text_color, bold=True)
        add_text(slide, f"tier-{tier}-desc", yrs,
                 x_px=area_x + 78, y_px=sy + 38, w_px=148, h_px=14,
                 font_size_px=10, color=years_color)

        # Competencies (body)
        comp_text = " · ".join(comps)
        body_color = WHITE if is_dark else TEXT_MID
        add_text(slide, f"tier-{tier}-body", comp_text,
                 x_px=area_x + 240, y_px=sy + 14, w_px=sw - 360, h_px=48,
                 font_size_px=10, color=body_color)

        # Status badge (right end)
        if badge:
            if "Current" in badge:
                add_rect(slide, "tier-current-chip-bg", area_x + sw - 110, sy + 22, 96, 22, BRAND_ACCENT)
                add_text(slide, "tier-current-chip", badge,
                         x_px=area_x + sw - 110, y_px=sy + 22, w_px=96, h_px=22,
                         font_size_px=9, color=WHITE, bold=True, align="center",
                         anchor="middle", uppercase=True)
            else:
                add_text(slide, "tier-target-chip", badge,
                         x_px=area_x + sw - 90, y_px=sy + 24, w_px=72, h_px=18,
                         font_size_px=9, color=WHITE, bold=True, align="center",
                         uppercase=True)

    # Progression arrow at right edge
    arrow_x = 1280 - 48 - 30
    add_rect(slide, "progression-arrow", arrow_x, area_y + 20, 2, area_h - 60, BRAND_PRIMARY_MID)
    add_text(slide, "progression-arrow-label", "PROGRESSION",
             x_px=arrow_x - 30, y_px=area_y + area_h // 2 - 8, w_px=60, h_px=16,
             font_size_px=8, color=TEXT_FAINT, bold=True, uppercase=True, align="center")

    # Convergence (centered italic, brand-primary text — uses a custom rendering)
    conv_y = 720 - 60
    add_text(slide, "convergence",
             "70% of promotions to Senior Analyst met the ML proficiency threshold "
             "before the standard tenure — accelerated path is ML-gated.",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=18,
             font_size_px=12, color=BRAND_PRIMARY, italic=True, align="center")

    add_footer(slide, page_num=130)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "130_capability-ladder.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
