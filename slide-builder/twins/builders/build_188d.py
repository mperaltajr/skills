"""
Builder for pattern 188d: Go-to-Market Motion — DARK variant.

Light source: twins/builders/build_188.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Go-to-Market <strong>Motion</strong>",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Four-stage demand engine — from awareness to action, with channel orchestration",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    body_top = 220
    body_bot = 620
    body_h = body_bot - body_top
    stages_h = body_h - 64
    cont_left = 64
    cont_right = 1280 - 64
    cont_w = cont_right - cont_left
    stage_w = (cont_w - 3 * 28) // 4
    stage_top = body_top
    stage_h = stages_h

    # In dark mode, lighten stage headers as we move right (mirror of light's darkening)
    stage_colors = [
        RGBColor(0x55, 0x36, 0x77),
        RGBColor(0x6E, 0x3D, 0x9A),
        RGBColor(0x8B, 0x5C, 0xC4),
        BRAND_ACCENT,
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
        body_shape = add_rect(slide, f"step-{n}-body-bg", x, stage_top, stage_w, stage_h, CARD_BG_DARK)
        body_shape.line.color.rgb = CARD_BORDER_DARK
        body_shape.line.width = 9525
        add_rect(slide, f"step-{n}-header-bg", x, stage_top, stage_w, 36, stage_colors[i])
        add_text(slide, f"step-{n}-num", str(n),
                 x_px=x + 10, y_px=stage_top + 8, w_px=20, h_px=20,
                 font_size_px=11, color=BRAND_PRIMARY, bold=True, align="center",
                 bg_fill=BRAND_ACCENT_SOFT, padding_px=(2, 0, 2, 0))
        add_text(slide, f"step-{n}-name", name,
                 x_px=x + 38, y_px=stage_top + 8, w_px=stage_w - 50, h_px=20,
                 font_size_px=14, color=WHITE, bold=True, uppercase=True)
        bx = x + 14
        for j, b in enumerate(bullets):
            by = stage_top + 50 + j * 56
            add_rect(slide, f"step-{n}-bullet-{j+1}-dot", bx, by + 6, 4, 4, BRAND_ACCENT_SOFT)
            add_text(slide, f"step-{n}-body-{j+1}" if j > 0 else f"step-{n}-body", b,
                     x_px=bx + 10, y_px=by, w_px=stage_w - 32, h_px=50,
                     font_size_px=11, color=TEXT_ON_DARK_MID)
        add_rect(slide, f"step-{n}-metric-rule", x + 12, stage_top + stage_h - 30, stage_w - 24, 1, CARD_BORDER_DARK)
        add_text(slide, f"step-{n}-meta-right", metric,
                 x_px=x + 12, y_px=stage_top + stage_h - 24, w_px=stage_w - 24, h_px=16,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True)
        if i < 3:
            arr_x = x + stage_w + 4
            arr_y = stage_top + stage_h // 2 - 10
            add_icon(slide, f"arrow-{n}-to-{n+1}", arr_x, arr_y, 20, "→", color=BRAND_ACCENT_SOFT)

    ch_top = stage_top + stage_h + 12
    # Channels backdrop band so the pills sit on a defined surface, not floating.
    add_rect(slide, "channels-band-bg", cont_left, ch_top, cont_w, 40, CARD_BG_DARK)
    add_text(slide, "channels-label", "CHANNELS",
             x_px=cont_left + 14, y_px=ch_top + 12, w_px=80, h_px=14,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True)

    channel_groups = [
        ["Paid", "Organic", "Social"],
        ["Events", "Partner", "Email"],
        ["SDR", "Demo", "Trial"],
        ["CS", "Onboard", "Upsell"],
    ]
    # Dark pill colors: dark saturated bg + light fg
    pill_colors = [
        (RGBColor(0x5C, 0x2D, 0x87), RGBColor(0xED, 0xE7, 0xF6)),
        (RGBColor(0x2E, 0x7D, 0x32), RGBColor(0xE8, 0xF5, 0xE9)),
        (RGBColor(0xE6, 0x51, 0x00), RGBColor(0xFF, 0xF3, 0xE0)),
        (RGBColor(0x15, 0x65, 0xC0), RGBColor(0xE3, 0xF2, 0xFD)),
    ]
    group_start_x = cont_left + 100
    group_w = (cont_w - 100) // 4
    for i, group in enumerate(channel_groups):
        gx = group_start_x + i * group_w
        pill_w = 60
        pill_gap = 6
        total_pills_w = len(group) * pill_w + (len(group) - 1) * pill_gap
        start = gx + (group_w - total_pills_w) // 2
        for j, pill in enumerate(group):
            bg_c, txt = pill_colors[(i + j) % len(pill_colors)]
            add_text(slide, f"step-{i+1}-channel-{j+1}", pill,
                     x_px=start + j * (pill_w + pill_gap), y_px=ch_top + 11,
                     w_px=pill_w, h_px=18,
                     font_size_px=9, color=txt, bold=True, align="center",
                     bg_fill=bg_c, padding_px=(2, 6, 2, 6))

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "188",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "188d_go-to-market-motion-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
