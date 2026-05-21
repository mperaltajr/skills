"""
Builder for pattern 308: Balanced scorecard (4 perspectives × 2 measures each).

Per pattern review feedback: 4 perspectives are arranged HORIZONTALLY as bigger
column cards (not a vertical table). Each perspective is one wide column with
its label + 2 measure rows inside. RAG legend below subheadline.

Source HTML: _pattern-library/308_balanced-scorecard.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

RAG_GREEN = RGBColor(0x16, 0xA3, 0x4A)
RAG_AMBER = RGBColor(0xD9, 0x77, 0x06)
RAG_RED = RGBColor(0xDC, 0x26, 0x26)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Balanced Scorecard — <strong>Strategic Performance Overview</strong>",
        subtitle="Objectives, measures, and initiative status across all four perspectives · FY 2026 Q2",
        title_x=48, title_y=44, title_w=900, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # ── RAG LEGEND (below subheadline) ──
    leg_h = 32
    leg_y = 232
    leg_right = 1232
    items = [("On Track", RAG_GREEN), ("At Risk", RAG_AMBER), ("Off Track", RAG_RED)]
    item_w = 96
    leg_w = len(items) * item_w + 16
    leg_x = leg_right - leg_w
    leg_bg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, CARD_BG)
    leg_bg.line.color.rgb = CARD_BORDER
    leg_bg.line.width = 9525
    cur_x = leg_x + 12
    for i, (lbl, col) in enumerate(items):
        n = i + 1
        add_rect(slide, f"legend-{n}-dot", cur_x, leg_y + (leg_h - 9) // 2, 9, 9, col)
        add_text(
            slide, f"legend-{n}-label", lbl,
            x_px=cur_x + 16, y_px=leg_y, w_px=item_w - 20, h_px=leg_h,
            font_size_px=10, color=TEXT_DARK, bold=True, anchor="middle",
        )
        cur_x += item_w

    # ── 4 PERSPECTIVE COLUMNS (horizontal, bigger) ──
    body_top = 280
    body_left = 48
    body_w = 1184
    # Body must end ≤ y=670 to stay clear of invariant zone (≥672).
    body_h = 670 - body_top
    gap = 14
    col_w = (body_w - 3 * gap) // 4

    perspectives = [
        ("Financial", BRAND_PRIMARY, [
            ("Grow revenue by expanding key accounts", "YoY revenue growth", "+12%",
             "Key Account Acceleration Program", "green", "On Track"),
            ("Improve operating margin", "Operating margin", "18%",
             "Cost Efficiency & Automation Drive", "amber", "At Risk"),
        ]),
        ("Customer", BRAND_PRIMARY_MID, [
            ("Increase client satisfaction", "Net Promoter Score (NPS)", "≥ 55",
             "Voice of Client Feedback Loop", "green", "On Track"),
            ("Reduce client churn", "Annual retention rate", "92%",
             "Proactive Renewal Engagement", "green", "On Track"),
        ]),
        ("Internal Process", BRAND_PRIMARY, [
            ("Accelerate delivery cycle time", "Avg. delivery (weeks)", "≤ 14 wks",
             "Agile Delivery Framework Rollout", "amber", "At Risk"),
            ("Reduce delivery defect rate", "Defects per 1,000 deliverables", "< 5",
             "Quality Gate Standardisation", "red", "Off Track"),
        ]),
        ("Learning & Growth", BRAND_PRIMARY_MID, [
            ("Build AI & data capability at scale", "Certified practitioners", "500",
             "AI Talent Academy Launch", "green", "On Track"),
            ("Improve employee engagement", "Engagement index score", "≥ 78%",
             "Flexible Career Pathway Program", "amber", "At Risk"),
        ]),
    ]
    rag_map = {"green": RAG_GREEN, "amber": RAG_AMBER, "red": RAG_RED}

    header_h = 56
    measure_h = (body_h - header_h - 8) // 2

    for ci, (persp_name, persp_color, measures) in enumerate(perspectives):
        cn = ci + 1
        cx = body_left + ci * (col_w + gap)
        # Header band
        add_rect(slide, f"persp-{cn}-header", cx, body_top, col_w, header_h, persp_color)
        add_text(
            slide, f"persp-{cn}-header-text", persp_name.upper(),
            x_px=cx + 12, y_px=body_top, w_px=col_w - 24, h_px=header_h,
            font_size_px=15, color=WHITE, bold=True,
            letter_spacing_px=1.6, anchor="middle", align="center",
        )
        # Two measure cards
        for mi, (obj, measure, target, init, rag, rag_lbl) in enumerate(measures):
            mn = mi + 1
            my = body_top + header_h + 8 + mi * (measure_h + 4)
            mh = measure_h - 4
            card = add_rect(slide, f"persp-{cn}-measure-{mn}-bg", cx, my, col_w, mh, CARD_BG)
            card.line.color.rgb = CARD_BORDER
            card.line.width = 9525
            # Objective heading
            add_text(
                slide, f"persp-{cn}-measure-{mn}-obj", obj,
                x_px=cx + 12, y_px=my + 10, w_px=col_w - 24, h_px=34,
                font_size_px=11, color=BRAND_PRIMARY, bold=True,
            )
            # Measure / target line
            add_text(
                slide, f"persp-{cn}-measure-{mn}-measure",
                f"<strong>Measure:</strong> {measure}",
                x_px=cx + 12, y_px=my + 50, w_px=col_w - 24, h_px=18,
                font_size_px=10, color=TEXT_MID, emphasis_color=TEXT_DARK,
            )
            add_text(
                slide, f"persp-{cn}-measure-{mn}-target",
                f"<strong>Target:</strong> {target}",
                x_px=cx + 12, y_px=my + 68, w_px=col_w - 24, h_px=18,
                font_size_px=10, color=BRAND_PRIMARY_MID, bold=True,
                emphasis_color=TEXT_DARK,
            )
            # Initiative
            add_text(
                slide, f"persp-{cn}-measure-{mn}-init", init,
                x_px=cx + 12, y_px=my + 90, w_px=col_w - 24, h_px=36,
                font_size_px=10, color=TEXT_MID, italic=True,
            )
            # Status pill at bottom
            pill_y = my + mh - 28
            pill_h = 18
            # measure pill width by label text length
            pill_w = min(col_w - 24, len(rag_lbl) * 6 + 36)
            pill_x = cx + 12
            add_rect(slide, f"persp-{cn}-measure-{mn}-pill",
                     pill_x, pill_y, pill_w, pill_h, CARD_BORDER)
            add_rect(slide, f"persp-{cn}-measure-{mn}-pill-dot",
                     pill_x + 8, pill_y + (pill_h - 8) // 2, 8, 8, rag_map[rag])
            add_text(
                slide, f"persp-{cn}-measure-{mn}-pill-text", rag_lbl.upper(),
                x_px=pill_x + 20, y_px=pill_y, w_px=pill_w - 24, h_px=pill_h,
                font_size_px=9, color=TEXT_DARK, bold=True, anchor="middle",
                letter_spacing_px=1.2,
            )

    add_footer(slide, page_num=308)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "308_balanced-scorecard.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
