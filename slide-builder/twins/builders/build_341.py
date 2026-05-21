"""
Builder for pattern 341: Dark Strategic Options.

Source HTML: _pattern-library/341_dark-strategic-options.html
Standalone — closest light reference: 250_strategic-options-comparison.

Layout: 3 option cards side by side with criteria rows (dot strength rating
+ value text), risk pill + timeline chip footer; recommended banner on Option B;
bottom recommendation strip.
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
DOT_EMPTY = RGBColor(0x4A, 0x2E, 0x66)

RISK_LOW = RGBColor(0x22, 0xC5, 0x5E)
RISK_MED = RGBColor(0xF5, 0x9E, 0x0B)
RISK_HIGH = RGBColor(0xEF, 0x44, 0x44)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title block
    add_text(slide, "title",
             "Evaluating <strong>Three Strategic Paths</strong> Forward",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Each option assessed across cost, speed, risk, and strategic fit — recommendation follows",
             x_px=64, y_px=108, w_px=1100, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Option cards
    body_top = 160
    card_h = 410
    card_w = 376
    gap = 16
    start_x = 64

    options = [
        {
            "label": "Option A",
            "name": "Organic Build",
            "strip": BRAND_ACCENT_SOFT,
            "dot_color": BRAND_ACCENT_SOFT,
            "recommended": False,
            "criteria": [
                ("Cost to Implement", "$8–12M capex", 1),
                ("Speed to Value", "18–24 months", 1),
                ("Capability Control", "Full ownership", 3),
                ("Strategic Fit", "High alignment", 2),
            ],
            "risk": ("Medium Risk", RISK_MED),
            "timeline": "20 mo. avg",
        },
        {
            "label": "Option B",
            "name": "Acquire & Integrate",
            "strip": BRAND_ACCENT,
            "dot_color": WHITE,
            "recommended": True,
            "criteria": [
                ("Cost to Implement", "$18–25M total", 2),
                ("Speed to Value", "6–9 months", 3),
                ("Capability Control", "Near-full post-close", 3),
                ("Strategic Fit", "Very high alignment", 3),
            ],
            "risk": ("Low Risk", RISK_LOW),
            "timeline": "8 mo. avg",
        },
        {
            "label": "Option C",
            "name": "Partnership / JV",
            "strip": RGBColor(0x9C, 0x88, 0xB8),
            "dot_color": RGBColor(0x9C, 0x88, 0xB8),
            "recommended": False,
            "criteria": [
                ("Cost to Implement", "$4–6M shared", 3),
                ("Speed to Value", "12–15 months", 2),
                ("Capability Control", "Shared governance", 1),
                ("Strategic Fit", "Moderate alignment", 2),
            ],
            "risk": ("High Risk", RISK_HIGH),
            "timeline": "13 mo. avg",
        },
    ]

    for i, opt in enumerate(options):
        x = start_x + i * (card_w + gap)
        n = i + 1
        # Card body
        c = add_rect(slide, f"option-{n}-bg", x, body_top, card_w, card_h, CARD_BG_DARK)
        c.line.color.rgb = CARD_BORDER_DARK if not opt["recommended"] else BRAND_ACCENT
        c.line.width = 9525 if not opt["recommended"] else 19050
        # Top strip
        add_rect(slide, f"option-{n}-strip", x, body_top, card_w, 4, opt["strip"])
        # Recommended banner
        body_y = body_top + 18
        if opt["recommended"]:
            add_rect(slide, f"option-{n}-rec-bg", x, body_top + 4, card_w, 22, BRAND_ACCENT)
            add_text(slide, f"option-{n}-rec", "RECOMMENDED",
                     x_px=x, y_px=body_top + 4, w_px=card_w, h_px=22,
                     font_size_px=10, color=WHITE, bold=True,
                     align="center", anchor="middle", letter_spacing_px=2)
            body_y = body_top + 36
        # Label + name
        add_text(slide, f"option-{n}-label", opt["label"],
                 x_px=x + 18, y_px=body_y, w_px=card_w - 36, h_px=16,
                 font_size_px=10, color=opt["strip"], bold=True,
                 uppercase=True, letter_spacing_px=1.5)
        add_text(slide, f"option-{n}-name", opt["name"],
                 x_px=x + 18, y_px=body_y + 18, w_px=card_w - 36, h_px=24,
                 font_size_px=18, color=WHITE, bold=True)
        # Criteria
        crit_top = body_y + 56
        crit_h = 64
        for j, (lbl, val, strength) in enumerate(opt["criteria"]):
            cy = crit_top + j * crit_h
            add_text(slide, f"option-{n}-crit-{j+1}-lbl", lbl,
                     x_px=x + 18, y_px=cy, w_px=card_w - 36, h_px=14,
                     font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=False,
                     uppercase=True, letter_spacing_px=1)
            add_text(slide, f"option-{n}-crit-{j+1}-val", val,
                     x_px=x + 18, y_px=cy + 16, w_px=card_w - 100, h_px=18,
                     font_size_px=13, color=WHITE, bold=True)
            # Dots
            dot_size = 8
            dot_gap = 4
            dot_x_start = x + card_w - 18 - (3 * dot_size + 2 * dot_gap)
            for k in range(3):
                dx = dot_x_start + k * (dot_size + dot_gap)
                col = opt["dot_color"] if k < strength else DOT_EMPTY
                add_rect(slide, f"option-{n}-crit-{j+1}-dot-{k+1}",
                         dx, cy + 20, dot_size, dot_size, col)
            # divider
            if j < len(opt["criteria"]) - 1:
                add_rect(slide, f"option-{n}-crit-{j+1}-div",
                         x + 18, cy + crit_h - 4, card_w - 36, 1,
                         CARD_BORDER_DARK)
        # Footer (risk pill + timeline)
        foot_y = body_top + card_h - 38
        risk_label, risk_col = opt["risk"]
        pill = add_rect(slide, f"option-{n}-risk-bg", x + 18, foot_y, 100, 22,
                        RGBColor(0x2D, 0x0A, 0x4E))
        pill.line.color.rgb = risk_col
        pill.line.width = 9525
        add_text(slide, f"option-{n}-risk", risk_label,
                 x_px=x + 18, y_px=foot_y, w_px=100, h_px=22,
                 font_size_px=10, color=risk_col, bold=True,
                 align="center", anchor="middle", uppercase=True)
        add_text(slide, f"option-{n}-timeline", opt["timeline"],
                 x_px=x + card_w - 110, y_px=foot_y, w_px=92, h_px=22,
                 font_size_px=11, color=TEXT_ON_DARK_MID, bold=True,
                 align="right", anchor="middle")

    # Recommendation strip
    rec_y = 600
    rec_h = 44
    add_rect(slide, "rec-bg", 64, rec_y, 1152, rec_h, BRAND_PRIMARY_MID)
    add_rect(slide, "rec-accent", 64, rec_y, 4, rec_h, BRAND_ACCENT)
    add_text(slide, "rec-label", "OUR VIEW",
             x_px=80, y_px=rec_y, w_px=120, h_px=rec_h,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=2, anchor="middle")
    add_text(slide, "rec-text",
             "Option B offers the fastest path to capability with acceptable cost — pursue targeted acquisition of a mid-market platform player in Q3.",
             x_px=204, y_px=rec_y, w_px=1000, h_px=rec_h,
             font_size_px=13, color=WHITE, italic=True, anchor="middle")

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "341",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "341_dark-strategic-options.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
