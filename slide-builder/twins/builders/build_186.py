"""
Builder for pattern 186: Problem / Opportunity Statement.

Two-panel hero with stat blocks + center arrow + gradient convergence band.

Source HTML: _pattern-library/186_problem-opportunity-statement.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="The <strong>Problem</strong> and the Opportunity",
        subtitle="Framing the challenge and the strategic upside of acting now",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    # Two panels with arrow in between.
    # Content: left:64, right:64, top:170, bottom: 78+42 (convergence) = 120 → body bottom 600
    body_top = 170
    body_bot = 580
    body_h = body_bot - body_top  # 410
    panel_w = (1280 - 128 - 64) // 2  # 544
    left_x = 64
    right_x = 1280 - 64 - panel_w
    arrow_x = left_x + panel_w + (64 - 40) // 2

    # Problem panel
    p1 = add_rect(slide, "panel-1-bg", left_x, body_top, panel_w, body_h, CARD_BG)
    p1.line.color.rgb = CARD_BORDER
    p1.line.width = 9525
    add_rect(slide, "panel-1-header-bg", left_x, body_top, panel_w, 36, BRAND_PRIMARY)
    add_text(slide, "panel-1-header", "The Problem",
             x_px=left_x + 18, y_px=body_top + 8, w_px=panel_w - 36, h_px=20,
             font_size_px=14, color=WHITE, bold=True, uppercase=True)
    # Bullets
    bullets_1 = [
        "Fragmented legacy systems create data silos that delay decision-making by an average of 4-6 weeks per cycle.",
        "Manual reconciliation processes consume an estimated 30% of analyst capacity, crowding out higher-value work.",
        "Rising regulatory complexity exposes the organisation to compounding compliance risk with each quarterly reporting period.",
    ]
    bullet_y = body_top + 50
    for i, b in enumerate(bullets_1):
        by = bullet_y + i * 56
        add_rect(slide, f"panel-1-bullet-{i+1}-dot", left_x + 18, by + 6, 5, 5, BRAND_PRIMARY)
        add_text(slide, f"panel-1-bullet-{i+1}", b,
                 x_px=left_x + 32, y_px=by, w_px=panel_w - 52, h_px=52,
                 font_size_px=12, color=TEXT_DARK)
    # Stat block at bottom
    stat_y = body_top + body_h - 92
    add_rect(slide, "panel-1-stat-rule", left_x + 18, stat_y - 12, panel_w - 36, 1, CARD_BORDER)
    add_text(slide, "panel-1-stat", "$120M+",
             x_px=left_x + 18, y_px=stat_y, w_px=panel_w - 36, h_px=32,
             font_size_px=24, color=BRAND_PRIMARY_MID, bold=True)
    add_text(slide, "panel-1-stat-label",
             "estimated annual cost of operational inefficiency and rework",
             x_px=left_x + 18, y_px=stat_y + 32, w_px=panel_w - 36, h_px=18,
             font_size_px=11, color=TEXT_MID)
    add_text(slide, "panel-1-source", "Source: Internal operations audit, Q1 2026",
             x_px=left_x + 18, y_px=stat_y + 52, w_px=panel_w - 36, h_px=14,
             font_size_px=9, color=TEXT_FAINT, italic=True)

    # Arrow icon
    add_icon(slide, "transformation-arrow", arrow_x - 12, body_top + body_h // 2 - 24, 48, "→",
             color=BRAND_ACCENT)

    # Opportunity panel
    p2 = add_rect(slide, "panel-2-bg", right_x, body_top, panel_w, body_h, CARD_BG)
    p2.line.color.rgb = CARD_BORDER
    p2.line.width = 9525
    add_rect(slide, "panel-2-header-bg", right_x, body_top, panel_w, 36, BRAND_ACCENT)
    add_text(slide, "panel-2-header", "The Opportunity",
             x_px=right_x + 18, y_px=body_top + 8, w_px=panel_w - 36, h_px=20,
             font_size_px=14, color=WHITE, bold=True, uppercase=True)
    bullets_2 = [
        "A unified data platform reduces cycle time by up to 70%, enabling real-time insight and faster strategic response.",
        "Automating reconciliation and reporting frees analyst bandwidth to focus on analysis, modelling, and stakeholder value.",
        "Embedded compliance controls reduce regulatory exposure and build audit-readiness into every process by default.",
    ]
    for i, b in enumerate(bullets_2):
        by = bullet_y + i * 56
        add_rect(slide, f"panel-2-bullet-{i+1}-dot", right_x + 18, by + 6, 5, 5, BRAND_ACCENT)
        add_text(slide, f"panel-2-bullet-{i+1}", b,
                 x_px=right_x + 32, y_px=by, w_px=panel_w - 52, h_px=52,
                 font_size_px=12, color=TEXT_DARK)
    add_rect(slide, "panel-2-stat-rule", right_x + 18, stat_y - 12, panel_w - 36, 1, CARD_BORDER)
    add_text(slide, "panel-2-stat", "3.4× ROI",
             x_px=right_x + 18, y_px=stat_y, w_px=panel_w - 36, h_px=32,
             font_size_px=24, color=BRAND_ACCENT, bold=True)
    add_text(slide, "panel-2-stat-label",
             "projected return over 36 months with phased modernisation",
             x_px=right_x + 18, y_px=stat_y + 32, w_px=panel_w - 36, h_px=18,
             font_size_px=11, color=TEXT_MID)
    add_text(slide, "panel-2-source", "Basis: Accenture benchmark, Finance Transformation 2025",
             x_px=right_x + 18, y_px=stat_y + 52, w_px=panel_w - 36, h_px=14,
             font_size_px=9, color=TEXT_FAINT, italic=True)

    # Convergence bar (gradient → brand-primary fill)
    conv_y = body_bot + 12
    add_rect(slide, "convergence-bg", 64, conv_y, 1280 - 128, 40, BRAND_PRIMARY)
    add_text(slide, "convergence",
             "Addressing operational fragmentation unlocks $400M+ in recoverable enterprise value over three years",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=40,
             font_size_px=12, color=WHITE, bold=True, align="center", anchor="middle")

    add_footer(slide, page_num=186)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "186_problem-opportunity-statement.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
