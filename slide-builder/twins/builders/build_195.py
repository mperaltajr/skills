"""
Builder for pattern 195: Risk vs. Opportunity Matrix.

Two panels (Risks / Opportunities) with badge + desc + note items.
Center divider with scales icon. Bottom convergence bar.

Source HTML: _pattern-library/195_risk-vs-opportunity-matrix.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, CARD_BG, CARD_BORDER,
    TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

RED = RGBColor(0xDC, 0x26, 0x26)
RED_BG = RGBColor(0xFE, 0xF2, 0xF2)
RED_BORDER = RGBColor(0xFE, 0xCA, 0xCA)
ORANGE = RGBColor(0xF9, 0x73, 0x16)
AMBER = RGBColor(0xEA, 0xB3, 0x08)
GREEN = RGBColor(0x16, 0xA3, 0x4A)
GREEN_BG = RGBColor(0xF0, 0xFD, 0xF4)
GREEN_BORDER = RGBColor(0xBB, 0xF7, 0xD0)
LIME = RGBColor(0x65, 0xA3, 0x0D)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Opportunity <strong>outweighs</strong> risk — with the right mitigations",
        subtitle="Risk vs. Opportunity Matrix · Strategic initiative assessment",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    body_top = 168
    body_bot = 560  # leave room for convergence bar
    body_h = body_bot - body_top
    divider_w = 48
    panel_w = (1280 - 128 - divider_w) // 2

    # Risk panel (left)
    left_x = 64
    risk_bg = add_rect(slide, "panel-1-bg", left_x, body_top, panel_w, body_h, RED_BG)
    risk_bg.line.color.rgb = RED_BORDER
    risk_bg.line.width = 9525
    add_rect(slide, "panel-1-header-bg", left_x, body_top, panel_w, 36, RED)
    add_icon(slide, "panel-1-icon", left_x + 12, body_top + 8, 20, "⚠", color=WHITE)
    add_text(slide, "panel-1-header", "Risks",
             x_px=left_x + 40, y_px=body_top + 10, w_px=panel_w - 60, h_px=18,
             font_size_px=11, color=WHITE, bold=True, uppercase=True, letter_spacing_px=2)

    risks = [
        ("Critical", "Regulatory non-compliance in target markets",
         "Mitigation: engage legal counsel Q1; complete gap analysis before go-live", RED),
        ("High", "Key talent attrition during transition period",
         "Mitigation: retention bonuses + accelerated role clarity by month 2", ORANGE),
        ("High", "Data migration integrity and system downtime",
         "Mitigation: parallel-run legacy systems for 60 days; automated reconciliation", ORANGE),
        ("Medium", "Stakeholder resistance slowing adoption curve",
         "Mitigation: executive sponsorship + change-champion network in place", AMBER),
    ]
    item_top = body_top + 50
    item_h = (body_h - 60) // 4
    for i, (badge, desc, note, badge_color) in enumerate(risks):
        n = i + 1
        iy = item_top + i * item_h
        ig = add_rect(slide, f"risk-{n}-bg", left_x + 12, iy, panel_w - 24, item_h - 8, WHITE)
        add_rect(slide, f"risk-{n}-accent", left_x + 12, iy, 3, item_h - 8, RED)
        add_text(slide, f"risk-{n}-badge", badge,
                 x_px=left_x + 24, y_px=iy + 8, w_px=70, h_px=14,
                 font_size_px=8, color=WHITE, bold=True, align="center", uppercase=True,
                 bg_fill=badge_color, padding_px=(2, 4, 2, 4))
        add_text(slide, f"risk-{n}-desc", desc,
                 x_px=left_x + 100, y_px=iy + 8, w_px=panel_w - 120, h_px=20,
                 font_size_px=11, color=TEXT_DARK, bold=True)
        add_text(slide, f"risk-{n}-note", note,
                 x_px=left_x + 24, y_px=iy + 30, w_px=panel_w - 40, h_px=24,
                 font_size_px=10, color=TEXT_FAINT)

    # Divider with scales icon
    div_x = left_x + panel_w
    add_rect(slide, "divider-line", div_x + divider_w // 2, body_top, 1, body_h, CARD_BORDER)
    div_icon_y = body_top + body_h // 2 - 16
    add_rect(slide, "divider-icon-bg", div_x + (divider_w - 32) // 2, div_icon_y, 32, 32, WHITE)
    add_icon(slide, "divider-icon", div_x + (divider_w - 32) // 2, div_icon_y, 32, "⚖", color=BRAND_PRIMARY)

    # Opportunity panel (right)
    right_x = div_x + divider_w
    opp_bg = add_rect(slide, "panel-2-bg", right_x, body_top, panel_w, body_h, GREEN_BG)
    opp_bg.line.color.rgb = GREEN_BORDER
    opp_bg.line.width = 9525
    add_rect(slide, "panel-2-header-bg", right_x, body_top, panel_w, 36, GREEN)
    add_icon(slide, "panel-2-icon", right_x + 12, body_top + 8, 20, "★", color=WHITE)
    add_text(slide, "panel-2-header", "Opportunities",
             x_px=right_x + 40, y_px=body_top + 10, w_px=panel_w - 60, h_px=18,
             font_size_px=11, color=WHITE, bold=True, uppercase=True, letter_spacing_px=2)

    opps = [
        ("High", "35% cost reduction through process automation",
         "Capture action: pilot automation in Finance by Q2; scale post-validation", GREEN),
        ("High", "New revenue stream via platform-as-a-service model",
         "Capture action: identify anchor client for beta; target $8M ARR by year 2", GREEN),
        ("Medium", "First-mover advantage in underserved mid-market segment",
         "Capture action: accelerate GTM launch; lock in 3 lighthouse accounts in H1", LIME),
        ("Medium", "Talent brand uplift attracting next-gen engineering talent",
         "Capture action: publish case study post-launch; partner with 2 universities", LIME),
    ]
    for i, (badge, desc, note, badge_color) in enumerate(opps):
        n = i + 1
        iy = item_top + i * item_h
        add_rect(slide, f"opp-{n}-bg", right_x + 12, iy, panel_w - 24, item_h - 8, WHITE)
        add_rect(slide, f"opp-{n}-accent", right_x + 12, iy, 3, item_h - 8, GREEN)
        add_text(slide, f"opp-{n}-badge", badge,
                 x_px=right_x + 24, y_px=iy + 8, w_px=70, h_px=14,
                 font_size_px=8, color=WHITE, bold=True, align="center", uppercase=True,
                 bg_fill=badge_color, padding_px=(2, 4, 2, 4))
        add_text(slide, f"opp-{n}-desc", desc,
                 x_px=right_x + 100, y_px=iy + 8, w_px=panel_w - 120, h_px=20,
                 font_size_px=11, color=TEXT_DARK, bold=True)
        add_text(slide, f"opp-{n}-note", note,
                 x_px=right_x + 24, y_px=iy + 30, w_px=panel_w - 40, h_px=24,
                 font_size_px=10, color=TEXT_FAINT)

    # Convergence bar
    conv_y = body_bot + 8
    add_rect(slide, "convergence-bg", 64, conv_y, 1280 - 128, 44, CARD_BG)
    add_rect(slide, "convergence-accent", 64, conv_y, 4, 44, BRAND_ACCENT)
    add_text(slide, "convergence-mark", "NET ASSESSMENT",
             x_px=78, y_px=conv_y + 8, w_px=130, h_px=14,
             font_size_px=9, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "convergence",
             "Opportunity outweighs risk if regulatory compliance and talent retention risks are mitigated by end of Q1 — estimated net value upside of $12–15M over 24 months.",
             x_px=216, y_px=conv_y + 6, w_px=1280 - 64 - 216, h_px=36,
             font_size_px=11, color=TEXT_DARK)

    add_footer(slide, page_num=195)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "195_risk-vs-opportunity-matrix.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
