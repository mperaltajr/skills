"""
Builder for pattern 269: Competitor SWOT 4-up.

Source HTML: _pattern-library/269_competitor-swot-4up.html

Layout: title + 2x2 grid of competitor cards. Each card has a header (name +
threat badge) and a 2x2 SWOT grid (Strengths, Weaknesses, Opportunities, Threats).

No legend at slide level — each card is self-contained.
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

THREAT_HIGH = RGBColor(0xE5, 0x39, 0x35)
THREAT_MED = RGBColor(0xF5, 0x9E, 0x0B)
THREAT_LOW = RGBColor(0x22, 0xC5, 0x5E)

S_BG = RGBColor(0xE8, 0xF5, 0xE9)
W_BG = RGBColor(0xFF, 0xEB, 0xEE)
O_BG = RGBColor(0xE3, 0xF2, 0xFD)
T_BG = RGBColor(0xFF, 0xF3, 0xE0)

S_LBL = RGBColor(0x16, 0x65, 0x34)
W_LBL = RGBColor(0xB7, 0x1C, 0x1C)
O_LBL = RGBColor(0x1E, 0x40, 0xAF)
T_LBL = RGBColor(0x92, 0x40, 0x0E)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Competitor landscape — <strong>where each rival is vulnerable and where they threaten us.</strong>",
        subtitle="Threat level reflects likelihood of near-term displacement; SWOT zones flag where to compete and where to avoid.",
    )

    # Body
    body_top = 230
    body_bottom = 632
    body_h = body_bottom - body_top
    left_x = 48
    right_x = 1280 - 48
    body_w = right_x - left_x

    # 2x2 grid
    col_gap = 14
    row_gap = 14
    card_w = (body_w - col_gap) // 2
    card_h = (body_h - row_gap) // 2

    competitors = [
        ("CompetitorOne", "HIGH", THREAT_HIGH,
         ["Global scale", "Brand recognition"],
         ["Slow innovation", "High price"],
         ["Mid-market gap"],
         ["Our agility"]),
        ("CompetitorTwo", "MEDIUM", THREAT_MED,
         ["Tech platform", "Low cost"],
         ["No services layer"],
         ["Upsell potential"],
         ["Our relationships"]),
        ("CompetitorThree", "LOW", THREAT_LOW,
         ["Niche depth"],
         ["Single geography"],
         ["Partnership"],
         ["Our scale"]),
        ("CompetitorFour", "MEDIUM", THREAT_MED,
         ["VC-backed", "Agile"],
         ["No enterprise refs"],
         ["New entrant"],
         ["Our reputation"]),
    ]

    for idx, (name, threat, threat_c, S, W, O, T) in enumerate(competitors):
        n = idx + 1
        r = idx // 2
        c = idx % 2
        cx = left_x + c * (card_w + col_gap)
        cy = body_top + r * (card_h + row_gap)
        # card outline
        card = add_rect(slide, f"card-{n}", cx, cy, card_w, card_h, WHITE)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # header
        hdr_h = 36
        add_rect(slide, f"card-{n}-header", cx, cy, card_w, hdr_h, CARD_BG)
        add_text(slide, f"card-{n}-name", name,
                 x_px=cx + 14, y_px=cy, w_px=card_w - 130, h_px=hdr_h,
                 font_size_px=14, color=BRAND_PRIMARY, bold=True, anchor="middle")
        # threat badge
        badge_w = 80
        badge_h = 20
        badge_x = cx + card_w - badge_w - 14
        badge_y = cy + (hdr_h - badge_h) // 2
        add_rect(slide, f"card-{n}-threat-bg", badge_x, badge_y, badge_w, badge_h, threat_c)
        add_text(slide, f"card-{n}-threat", threat,
                 x_px=badge_x, y_px=badge_y, w_px=badge_w, h_px=badge_h,
                 font_size_px=9, color=WHITE, bold=True, align="center", anchor="middle",
                 letter_spacing_px=1.2)

        # 2x2 swot grid inside card body
        body_pad = 10
        sx = cx + body_pad
        sy = cy + hdr_h + body_pad
        sw = card_w - 2 * body_pad
        sh = card_h - hdr_h - 2 * body_pad
        zone_w = (sw - 6) // 2
        zone_h = (sh - 6) // 2
        zones = [
            ("Strengths", S, S_BG, S_LBL, 0, 0),
            ("Weaknesses", W, W_BG, W_LBL, 1, 0),
            ("Opportunities", O, O_BG, O_LBL, 0, 1),
            ("Threats", T, T_BG, T_LBL, 1, 1),
        ]
        for zi, (lbl, items, bg, lbl_c, gc, gr) in enumerate(zones):
            zx = sx + gc * (zone_w + 6)
            zy = sy + gr * (zone_h + 6)
            add_rect(slide, f"card-{n}-zone-{zi+1}", zx, zy, zone_w, zone_h, bg)
            add_text(slide, f"card-{n}-zone-{zi+1}-label", lbl.upper(),
                     x_px=zx + 8, y_px=zy + 4, w_px=zone_w - 16, h_px=12,
                     font_size_px=8, color=lbl_c, bold=True,
                     letter_spacing_px=1.2, uppercase=True)
            for bi, b in enumerate(items):
                add_text(slide, f"card-{n}-zone-{zi+1}-b{bi+1}", "• " + b,
                         x_px=zx + 8, y_px=zy + 18 + bi * 16, w_px=zone_w - 16, h_px=14,
                         font_size_px=10, color=TEXT_DARK)

    add_footer(slide, page_num=269)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "269_competitor-swot-4up.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
