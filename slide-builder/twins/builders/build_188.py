"""
Builder for pattern 188: Go-to-Market Motion.

Four-stage funnel with darkening header colors + bullets + target metric + channel pill strip.

Source HTML: _pattern-library/188_go-to-market-motion.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Go-to-Market <strong>Motion</strong>",
        subtitle="Four-stage demand engine — from awareness to action, with channel orchestration",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    # Stages row
    body_top = 170
    body_bot = 620
    body_h = body_bot - body_top  # 450
    stages_h = body_h - 60  # leave room for channel strip
    cont_left = 64
    cont_right = 1280 - 64
    cont_w = cont_right - cont_left  # 1152
    # 4 stages + 3 arrow gaps (each 28px wide)
    stage_w = (cont_w - 3 * 28) // 4  # ~267
    stage_top = body_top
    stage_h = stages_h

    # Stage header colors — darkening from light to dark
    stage_colors = [
        RGBColor(0x7B, 0x3F, 0xBF),
        RGBColor(0x5C, 0x2D, 0x87),
        RGBColor(0x43, 0x1F, 0x6B),
        BRAND_PRIMARY,
    ]
    stages = [
        ("Awareness", ["Broad-reach brand campaigns across digital and offline",
                       "Thought leadership content & SEO-optimised publishing",
                       "Paid social targeting lookalike audiences",
                       "Analyst relations & industry conference presence"],
         "Target: 500K reach / qtr"),
        ("Interest", ["Gated content, webinars & virtual events",
                      "Partner co-marketing and referral activation",
                      "Retargeting sequences for engaged visitors",
                      "Account-based marketing for top 200 accounts"],
         "Target: 12K MQLs / qtr"),
        ("Decision", ["SDR outreach, discovery calls & product demos",
                      "Free-trial or POC with success milestones",
                      "Competitive battle-cards & ROI calculators",
                      "Executive briefings & reference customer calls"],
         "Target: 2.4K SQLs / qtr"),
        ("Action", ["Structured onboarding & customer success handoff",
                    "Expansion plays: upsell, cross-sell, renewal",
                    "NPS loop feeding advocacy & referral programs",
                    "Quarterly business reviews with named CSMs"],
         "Target: 480 closed-won / qtr"),
    ]

    for i, (name, bullets, metric) in enumerate(stages):
        n = i + 1
        x = cont_left + i * (stage_w + 28)
        # Body bg
        body = add_rect(slide, f"step-{n}-body-bg", x, stage_top, stage_w, stage_h, CARD_BG)
        body.line.color.rgb = CARD_BORDER
        body.line.width = 9525
        # Header
        add_rect(slide, f"step-{n}-header-bg", x, stage_top, stage_w, 36, stage_colors[i])
        # Number circle (white text on translucent bg → simulate with brand-accent-soft)
        add_text(slide, f"step-{n}-num", str(n),
                 x_px=x + 10, y_px=stage_top + 8, w_px=20, h_px=20,
                 font_size_px=11, color=WHITE, bold=True, align="center",
                 bg_fill=BRAND_ACCENT_SOFT, padding_px=(2, 0, 2, 0))
        add_text(slide, f"step-{n}-name", name,
                 x_px=x + 38, y_px=stage_top + 8, w_px=stage_w - 50, h_px=20,
                 font_size_px=14, color=WHITE, bold=True, uppercase=True)
        # Bullets
        bx = x + 14
        for j, b in enumerate(bullets):
            by = stage_top + 50 + j * 50
            add_rect(slide, f"step-{n}-bullet-{j+1}-dot", bx, by + 6, 4, 4, BRAND_ACCENT_SOFT)
            add_text(slide, f"step-{n}-body-{j+1}" if j > 0 else f"step-{n}-body", b,
                     x_px=bx + 10, y_px=by, w_px=stage_w - 32, h_px=44,
                     font_size_px=11, color=TEXT_DARK)
        # Metric at bottom
        add_rect(slide, f"step-{n}-metric-rule", x + 12, stage_top + stage_h - 30, stage_w - 24, 1, CARD_BORDER)
        add_text(slide, f"step-{n}-meta-right", metric,
                 x_px=x + 12, y_px=stage_top + stage_h - 24, w_px=stage_w - 24, h_px=16,
                 font_size_px=10, color=BRAND_PRIMARY_MID, bold=True)
        # Arrow connector
        if i < 3:
            arr_x = x + stage_w + 4
            arr_y = stage_top + stage_h // 2 - 10
            add_icon(slide, f"arrow-{n}-to-{n+1}", arr_x, arr_y, 20, "→", color=BRAND_ACCENT)

    # Channel strip
    ch_top = stage_top + stage_h + 8
    add_text(slide, "channels-label", "CHANNELS",
             x_px=cont_left, y_px=ch_top + 6, w_px=80, h_px=14,
             font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True)

    # Channel pill groups
    channel_groups = [
        ["Paid", "Organic", "Social"],
        ["Events", "Partner", "Email"],
        ["SDR", "Demo", "Trial"],
        ["CS", "Onboard", "Upsell"],
    ]
    pill_colors = [
        (RGBColor(0xED, 0xE7, 0xF6), RGBColor(0x5C, 0x2D, 0x87)),
        (RGBColor(0xE8, 0xF5, 0xE9), RGBColor(0x2E, 0x7D, 0x32)),
        (RGBColor(0xFF, 0xF3, 0xE0), RGBColor(0xE6, 0x51, 0x00)),
        (RGBColor(0xE3, 0xF2, 0xFD), RGBColor(0x15, 0x65, 0xC0)),
    ]
    # Distribute groups under each stage column
    group_start_x = cont_left + 76
    group_w = (cont_w - 76) // 4
    for i, group in enumerate(channel_groups):
        gx = group_start_x + i * group_w
        # Center pills within the group width
        pill_w = 60
        pill_gap = 6
        total_pills_w = len(group) * pill_w + (len(group) - 1) * pill_gap
        start = gx + (group_w - total_pills_w) // 2
        for j, pill in enumerate(group):
            bg, txt = pill_colors[(i + j) % len(pill_colors)]
            add_text(slide, f"step-{i+1}-channel-{j+1}", pill,
                     x_px=start + j * (pill_w + pill_gap), y_px=ch_top + 6,
                     w_px=pill_w, h_px=18,
                     font_size_px=9, color=txt, bold=True, align="center",
                     bg_fill=bg, padding_px=(2, 6, 2, 6))

    add_footer(slide, page_num=188)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "188_go-to-market-motion.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
