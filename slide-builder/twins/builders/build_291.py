"""
Builder for pattern 291: Hypothesis testing dashboard (dark).

2x2 grid of hypothesis cards with status badges and confidence bars,
plus a working-hypothesis strip at bottom.

Source HTML: _pattern-library/291_hypothesis-testing-dark.html
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
CARD_BG = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER = RGBColor(0x55, 0x36, 0x77)
CONFIRMED = RGBColor(0x4A, 0xDE, 0x80)
REFUTED = RGBColor(0xF8, 0x71, 0x71)
TESTING = RGBColor(0xFC, 0xD3, 0x4D)
PENDING_TEXT = TEXT_ON_DARK_MID
PENDING_BG = RGBColor(0x4A, 0x33, 0x6E)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Canonical chrome
    add_text(slide, "title",
             "Hypothesis Testing — <strong>Revenue Leakage Root Causes</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Structured evidence review across four primary hypotheses · Wave 2 fieldwork, May 2026",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 80, 3, BRAND_ACCENT_SOFT)

    # 2x2 grid
    grid_top = 220
    grid_bot = 604
    grid_left = 48
    grid_right = 1232
    gap = 14
    grid_w = grid_right - grid_left - gap
    grid_h = grid_bot - grid_top - gap
    card_w = grid_w // 2
    card_h = grid_h // 2

    hypotheses = [
        ("Pricing exceptions granted outside policy are the primary driver of margin erosion",
         "CONFIRMED", CONFIRMED,
         ["43% of deals in sample had at least one unauthorized discount applied post-approval",
          "Average exception size 18pp below floor; finance reconciliation shows $12M gap YTD",
          "Three BUs confirmed no escalation path exists for field-level overrides"],
         87, CONFIRMED),
        ("Contract renewal delays are caused by legal review bottlenecks in the approval chain",
         "REFUTED", REFUTED,
         ["Legal turnaround avg 2.1 days vs. 11.4-day total cycle; not the binding constraint",
          "Root cause traced to incomplete commercial data packages submitted by sales ops",
          "Interviews with 8 legal reviewers confirmed consistent SLA adherence"],
         91, REFUTED),
        ("Rebate accrual mismatches stem from ERP configuration gaps introduced in 2024 migration",
         "TESTING", TESTING,
         ["Preliminary data pull shows 7 accrual rule sets not migrated from legacy SAP",
          "IT team validating scope; full reconciliation expected by 23 May",
          "Two customer complaints referencing incorrect rebate statements support the signal"],
         54, TESTING),
        ("Channel partner invoicing errors account for a material share of unreconciled cash items",
         "PENDING", PENDING_TEXT,
         ["Partner billing data access requested; awaiting NDA countersignature from 3 partners",
          "Internal AR flags suggest ~$4M in disputed items; attribution unconfirmed",
          "Scoping interview with channel ops scheduled for 27 May"],
         22, TEXT_ON_DARK_FAINT),
    ]

    for idx, (stmt, status, status_col, evidence, conf, fill_col) in enumerate(hypotheses):
        col = idx % 2
        row = idx // 2
        cx = grid_left + col * (card_w + gap)
        cy = grid_top + row * (card_h + gap)
        add_rect(slide, f"hyp-{idx+1}-bg", cx, cy, card_w, card_h, CARD_BG)
        # Statement
        add_text(slide, f"hyp-{idx+1}-statement", stmt,
                 x_px=cx + 18, y_px=cy + 14, w_px=card_w - 110, h_px=44,
                 font_size_px=12, color=WHITE, bold=True)
        # Status pill
        pill_x = cx + card_w - 92
        pill_y = cy + 14
        pill_bg = RGBColor(0x4A, 0x33, 0x6E)
        add_rect(slide, f"hyp-{idx+1}-pill", pill_x, pill_y, 78, 18, pill_bg)
        add_text(slide, f"hyp-{idx+1}-status", status,
                 x_px=pill_x, y_px=pill_y, w_px=78, h_px=18,
                 font_size_px=8, color=status_col, bold=True,
                 align="center", anchor="middle", letter_spacing_px=1.2)
        # Evidence list
        ey = cy + 66
        for j, ev in enumerate(evidence):
            add_rect(slide, f"hyp-{idx+1}-ev-{j+1}-dot", cx + 18, ey + 6, 4, 4,
                     TEXT_ON_DARK_FAINT)
            add_text(slide, f"hyp-{idx+1}-ev-{j+1}", ev,
                     x_px=cx + 30, y_px=ey, w_px=card_w - 48, h_px=34,
                     font_size_px=10, color=TEXT_ON_DARK_MID)
            ey += 36
        # Confidence bar at bottom
        cb_y = cy + card_h - 24
        add_text(slide, f"hyp-{idx+1}-conf-label", "CONFIDENCE",
                 x_px=cx + 18, y_px=cb_y - 12, w_px=120, h_px=12,
                 font_size_px=8, color=TEXT_ON_DARK_FAINT, bold=True, letter_spacing_px=0.8)
        add_text(slide, f"hyp-{idx+1}-conf-pct", f"{conf}%",
                 x_px=cx + card_w - 50, y_px=cb_y - 12, w_px=32, h_px=12,
                 font_size_px=9, color=WHITE, bold=True, align="right")
        # Track
        track_w = card_w - 36
        add_rect(slide, f"hyp-{idx+1}-track", cx + 18, cb_y, track_w, 4,
                 RGBColor(0x3D, 0x25, 0x5C))
        # Fill
        add_rect(slide, f"hyp-{idx+1}-fill", cx + 18, cb_y, int(track_w * conf / 100), 4,
                 fill_col)

    # Working hypothesis strip
    ws_y = grid_bot + 6
    ws_h = 56
    add_rect(slide, "working-strip-bg", 48, ws_y, 1184, ws_h,
             RGBColor(0x4A, 0x29, 0x76))
    add_text(slide, "strip-label", "WORKING HYPOTHESIS",
             x_px=64, y_px=ws_y + 8, w_px=160, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1.6)
    add_rect(slide, "strip-divider", 230, ws_y + 18, 1, 20, CARD_BORDER)
    add_text(slide, "strip-text",
             "Revenue leakage is primarily structural — driven by policy gaps and data quality failures — not by deliberate misconduct or external market factors, and is therefore recoverable through process and system controls.",
             x_px=246, y_px=ws_y + 8, w_px=970, h_px=44,
             font_size_px=12, color=WHITE)

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "291",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "291_hypothesis-testing-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
