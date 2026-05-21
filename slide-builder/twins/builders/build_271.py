"""
Builder for pattern 271: Competitive landscape (dark).

3-column layout: market context | our position | competitive field.
No legend.

Source HTML: _pattern-library/271_competitive-landscape-dark.html
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
RED_LIGHT = RGBColor(0xFF, 0x6B, 0x6B)
AMBER_LIGHT = RGBColor(0xF4, 0xA6, 0x23)
GREEN_LIGHT = RGBColor(0x4A, 0xDE, 0x80)
OUR_POS_BG = RGBColor(0x52, 0x2A, 0x82)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Title — canonical chrome
    add_text(slide, "title",
             "Competitive Landscape · <strong>Where we stand and where we win.</strong>",
             x_px=40, y_px=20, w_px=1200, h_px=80,
             font_size_px=20, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Market context, our position, and the three competitors shaping the field — as of Q2 2026",
             x_px=40, y_px=108, w_px=1200, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 40, 132, 80, 3, BRAND_ACCENT_SOFT)

    # 3-column body (no legend in this pattern)
    body_top = 220
    body_bot = 670
    body_h = body_bot - body_top
    body_left = 40
    body_right = 1240
    gap = 20
    body_w = body_right - body_left - 2 * gap
    col_w = [int(body_w * 0.32), int(body_w * 0.36), 0]
    col_w[2] = body_w - col_w[0] - col_w[1]
    col_x = [body_left, body_left + col_w[0] + gap, body_left + col_w[0] + col_w[1] + 2 * gap]

    # Column dividers
    add_rect(slide, "divider-1", col_x[1] - gap // 2, body_top, 1, body_h, CARD_BORDER)
    add_rect(slide, "divider-2", col_x[2] - gap // 2, body_top, 1, body_h, CARD_BORDER)

    # ---- LEFT: Market Context ----
    cx, cw = col_x[0], col_w[0]
    add_text(slide, "market-label", "MARKET CONTEXT",
             x_px=cx, y_px=body_top, w_px=cw, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=2)
    add_text(slide, "context-p1",
             "The managed services market is consolidating rapidly. Buyers are reducing vendor panels and demanding deeper integration capability, sector expertise, and outcome-based commercials.",
             x_px=cx, y_px=body_top + 22, w_px=cw, h_px=130,
             font_size_px=12, color=TEXT_ON_DARK_MID)
    add_text(slide, "context-p2",
             "Cloud-native challengers have compressed margins in the mid-market, forcing tier-1 competitors to pivot upmarket. This creates an acquisition window in the large-enterprise segment.",
             x_px=cx, y_px=body_top + 154, w_px=cw, h_px=130,
             font_size_px=12, color=TEXT_ON_DARK_MID)
    # Stat block at bottom
    sb_h = 90
    sb_y = body_bot - sb_h
    add_rect(slide, "stat-block-bg", cx, sb_y, cw, sb_h, CARD_BG)
    add_rect(slide, "stat-block-accent", cx, sb_y, 4, sb_h, BRAND_ACCENT_SOFT)
    add_text(slide, "stat-figure", "$18.4B",
             x_px=cx + 16, y_px=sb_y + 14, w_px=cw - 24, h_px=34,
             font_size_px=22, color=WHITE, bold=True)
    add_text(slide, "stat-label", "TOTAL ADDRESSABLE MARKET · GROWING 14% CAGR",
             x_px=cx + 16, y_px=sb_y + 50, w_px=cw - 24, h_px=30,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1)

    # ---- CENTER: Our Position ----
    cx, cw = col_x[1], col_w[1]
    add_text(slide, "position-label", "OUR POSITION",
             x_px=cx, y_px=body_top, w_px=cw, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=2)
    pc_y = body_top + 22
    pc_h = body_bot - pc_y
    add_rect(slide, "our-position-card-bg", cx, pc_y, cw, pc_h, OUR_POS_BG)
    # Border accent
    add_rect(slide, "our-position-border", cx, pc_y, cw, 4, BRAND_ACCENT)
    add_text(slide, "position-headline", "3rd in revenue,\n#1 in client satisfaction.",
             x_px=cx + 18, y_px=pc_y + 16, w_px=cw - 36, h_px=60,
             font_size_px=16, color=WHITE, bold=True)
    strengths = [
        "Highest NPS in the sector for 3 consecutive years — clients renew at 91% rate",
        "Fastest time-to-value: avg 6-week onboarding vs. 14-week industry norm",
        "Only competitor with FedRAMP Moderate + ISO 27001 across all delivery regions",
    ]
    sy = pc_y + 88
    for i, s in enumerate(strengths):
        add_rect(slide, f"strength-{i+1}-dot", cx + 18, sy + 6, 6, 6, BRAND_ACCENT_SOFT)
        add_text(slide, f"strength-{i+1}", s,
                 x_px=cx + 32, y_px=sy, w_px=cw - 48, h_px=44,
                 font_size_px=11, color=TEXT_ON_DARK_MID)
        sy += 48
    # Win rate row at bottom of card
    wr_h = 56
    wr_y = pc_y + pc_h - wr_h - 16
    add_rect(slide, "win-rate-bg", cx + 14, wr_y, cw - 28, wr_h,
             RGBColor(0x6B, 0x2B, 0xA8))
    add_text(slide, "win-rate-number", "64%",
             x_px=cx + 22, y_px=wr_y + 8, w_px=80, h_px=40,
             font_size_px=28, color=BRAND_ACCENT_SOFT, bold=True)
    add_text(slide, "win-rate-label", "COMPETITIVE\nWIN RATE",
             x_px=cx + 108, y_px=wr_y + 8, w_px=cw - 130, h_px=40,
             font_size_px=10, color=WHITE, bold=True, letter_spacing_px=1)

    # ---- RIGHT: Competitive Field ----
    cx, cw = col_x[2], col_w[2]
    add_text(slide, "field-label", "COMPETITIVE FIELD",
             x_px=cx, y_px=body_top, w_px=cw, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=2)
    comps = [
        ("Apex Global Services", "HIGH", RED_LIGHT,
         "Market revenue leader; strong in FSI and public sector. Pursuing aggressive M&A. Primary displacement risk above $50M TCV."),
        ("Northfield Digital", "MED", AMBER_LIGHT,
         "Cloud-native challenger with strong APAC presence. Competitive on price and speed but thin on compliance and global scale."),
        ("Meridian Solutions", "LOW", GREEN_LIGHT,
         "Niche player in retail and CPG verticals. Strong product but no global delivery; rarely seen in cross-sector enterprise bids."),
    ]
    ct_y = body_top + 22
    ct_h_total = body_bot - ct_y
    ch = (ct_h_total - 2 * 14) // 3
    for i, (name, threat, threat_col, desc) in enumerate(comps):
        cy = ct_y + i * (ch + 14)
        add_rect(slide, f"comp-{i+1}-bg", cx, cy, cw, ch, CARD_BG)
        add_text(slide, f"comp-{i+1}-name", name,
                 x_px=cx + 14, y_px=cy + 12, w_px=cw - 80, h_px=18,
                 font_size_px=11, color=WHITE, bold=True)
        # Threat pill
        add_rect(slide, f"comp-{i+1}-pill", cx + cw - 58, cy + 12, 44, 16, CARD_BORDER)
        add_text(slide, f"comp-{i+1}-threat", threat,
                 x_px=cx + cw - 58, y_px=cy + 12, w_px=44, h_px=16,
                 font_size_px=8, color=threat_col, bold=True,
                 align="center", anchor="middle", letter_spacing_px=1.2)
        add_text(slide, f"comp-{i+1}-desc", desc,
                 x_px=cx + 14, y_px=cy + 34, w_px=cw - 28, h_px=ch - 40,
                 font_size_px=11, color=TEXT_ON_DARK_MID)

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "271",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "271_competitive-landscape-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
