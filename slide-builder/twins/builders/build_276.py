"""
Builder for pattern 276: Problem → Solution → Benefit (dark).

3-panel layout with arrow connectors. No legend.

Source HTML: _pattern-library/276_problem-solution-benefit-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
PROBLEM_BG = RGBColor(0x55, 0x1F, 0x2E)
PROBLEM_LINE = RGBColor(0xE5, 0x3E, 0x3E)
PROBLEM_TEXT = RGBColor(0xFF, 0x8A, 0x8A)
SOLUTION_BG = RGBColor(0x55, 0x22, 0x80)
SOLUTION_LINE = BRAND_ACCENT
BENEFIT_BG = RGBColor(0x1D, 0x4D, 0x36)
BENEFIT_LINE = RGBColor(0x38, 0xA1, 0x69)
BENEFIT_TEXT = RGBColor(0x6E, 0xD8, 0x9A)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Title — canonical chrome
    add_text(slide, "title",
             "From <strong>Problem</strong> to Solution — and Measurable Benefit",
             x_px=40, y_px=20, w_px=1200, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "How structural data fragmentation is being resolved — and what it returns",
             x_px=40, y_px=108, w_px=1200, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 40, 132, 80, 3, BRAND_ACCENT_SOFT)

    # Three panels with arrows
    body_top = 220
    body_bot = 660
    body_h = body_bot - body_top
    body_left = 40
    body_right = 1240
    arrow_w = 44
    panel_w = (body_right - body_left - 2 * arrow_w) // 3
    panels = [
        ("⚠ THE PROBLEM", "Fragmented data across 23 systems generating $8M in annual reconciliation cost",
         [
             "No single source of truth across finance, ops and supply chain platforms",
             "Manual reconciliation consuming 1,200 FTE-hours per month",
             "Reporting latency of 48+ hours causing missed decision windows",
         ],
         "$8M / year", "ESTIMATED ANNUAL RECONCILIATION COST",
         PROBLEM_BG, PROBLEM_LINE, PROBLEM_TEXT),
        ("✦ THE SOLUTION", "Unified data platform with single master record and automated reconciliation",
         [
             "Cloud-native data lakehouse consolidating all 23 source systems",
             "Automated reconciliation engine with rule-based exception handling",
             "Real-time data streaming with sub-minute latency to all consumers",
         ],
         "6-month implementation", "PHASED DELIVERY WITH ZERO BUSINESS DISRUPTION",
         SOLUTION_BG, SOLUTION_LINE, BRAND_ACCENT_SOFT),
        ("✓ THE BENEFIT", "$11M recovered, data latency reduced from 48 hours to real-time",
         [
             "$11M in annual cost recovery including $8M reconciliation and $3M in error rework",
             "Real-time reporting enabling same-day executive decision-making",
             "1,200 FTE-hours per month redeployed to higher-value analysis",
         ],
         "3.2× ROI", "RETURN ON TOTAL PLATFORM INVESTMENT",
         BENEFIT_BG, BENEFIT_LINE, BENEFIT_TEXT),
    ]

    for i, (eyebrow, heading, bullets, stat_num, stat_lbl, bgcol, linecol, statcol) in enumerate(panels):
        px = body_left + i * (panel_w + arrow_w)
        # Panel
        add_rect(slide, f"panel-{i+1}-bg", px, body_top, panel_w, body_h, bgcol)
        add_rect(slide, f"panel-{i+1}-top", px, body_top, panel_w, 3, linecol)
        # Eyebrow
        add_text(slide, f"panel-{i+1}-eyebrow", eyebrow,
                 x_px=px + 18, y_px=body_top + 16, w_px=panel_w - 36, h_px=14,
                 font_size_px=9, color=linecol, bold=True, letter_spacing_px=1.6)
        # Heading
        add_text(slide, f"panel-{i+1}-heading", heading,
                 x_px=px + 18, y_px=body_top + 36, w_px=panel_w - 36, h_px=80,
                 font_size_px=13, color=WHITE, bold=True)
        # Bullets
        by = body_top + 130
        for j, b in enumerate(bullets):
            add_text(slide, f"panel-{i+1}-bullet-{j+1}", "– " + b,
                     x_px=px + 18, y_px=by, w_px=panel_w - 36, h_px=66,
                     font_size_px=11, color=TEXT_ON_DARK_MID)
            by += 70
        # Stat callout at bottom (after horizontal rule)
        callout_y = body_bot - 76
        add_rect(slide, f"panel-{i+1}-rule", px + 18, callout_y, panel_w - 36, 1,
                 RGBColor(0x55, 0x36, 0x77))
        add_text(slide, f"panel-{i+1}-stat-number", stat_num,
                 x_px=px + 18, y_px=callout_y + 10, w_px=panel_w - 36, h_px=32,
                 font_size_px=20, color=statcol, bold=True)
        add_text(slide, f"panel-{i+1}-stat-label", stat_lbl,
                 x_px=px + 18, y_px=callout_y + 44, w_px=panel_w - 36, h_px=24,
                 font_size_px=8, color=TEXT_ON_DARK_FAINT, letter_spacing_px=1)

        # Arrow after panel (except last)
        if i < 2:
            ax = px + panel_w
            add_text(slide, f"arrow-{i+1}", "→",
                     x_px=ax, y_px=body_top + body_h // 2 - 20, w_px=arrow_w, h_px=40,
                     font_size_px=24, color=BRAND_ACCENT_SOFT, align="center", anchor="middle")

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "276",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "276_problem-solution-benefit-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
