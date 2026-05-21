"""
Builder for pattern 144d: Proof points / mini case studies (3x2 grid) — dark.

Source HTML: _pattern-library/144_proof-points-compilation-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
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

    # Canonical chrome
    add_text(slide, "title",
             "<strong>Six comparable programs delivered</strong> — each with measurable outcomes traceable to transformation levers",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Reference cases drawn from the last 36 months · independently validated outcomes",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # 3x2 grid
    grid_x = 48
    grid_y = 220
    grid_w = 1280 - 96
    grid_h = 664 - grid_y
    gap = 14
    card_w = (grid_w - 2 * gap) // 3
    card_h = (grid_h - gap) // 2

    cards = [
        ("Global Retail Bank", "Legacy core migration at scale",
         "+47% straight-through processing",
         "3-year program, 220+ APIs modernized across payment and lending domains.",
         "Source: Program closeout report, Q4 2024"),
        ("Insurance Carrier", "Claims AI modernization",
         "$28M annual savings",
         "Computer vision reduced manual review by 80%; redeployed 140 FTEs to complex cases.",
         "Source: CFO-validated business case, 2025"),
        ("Healthcare System", "EHR consolidation",
         "94% user adoption",
         "12-hospital network, 18-month program; adoption measured at 90 days post go-live.",
         "Source: Post-implementation review, 2024"),
        ("Energy Utility", "Field workforce transformation",
         "3.2× productivity",
         "4,000 field workers, mobile-first platform; jobs per shift up from 4.1 to 13.2.",
         "Source: Workforce analytics dashboard, Q1 2025"),
        ("Consumer Goods", "Supply chain AI",
         "−32% inventory waste",
         "6-country rollout, ML-driven demand sensing; SKU forecast accuracy up to 91%.",
         "Source: Supply chain COE benchmark, 2025"),
        ("Government Agency", "Digital services platform",
         "7.8M citizens served",
         "Full GDS standard compliance, 99.9% uptime; avg. transaction time cut from 22 min to 4 min.",
         "Source: Cabinet Office assurance review, 2025"),
    ]

    for i, (badge, heading, stat, body, source) in enumerate(cards):
        n = i + 1
        col = i % 3
        row = i // 3
        cx = grid_x + col * (card_w + gap)
        cy = grid_y + row * (card_h + gap)

        # Card body + top accent
        card = add_rect(slide, f"card-{n}-bg", cx, cy, card_w, card_h, CARD_BG_DARK)
        card.line.color.rgb = CARD_BORDER_DARK
        card.line.width = 9525
        add_rect(slide, f"card-{n}-accent", cx, cy, card_w, 3, BRAND_ACCENT)

        # Client tag pill
        add_text(slide, f"card-{n}-badge", badge,
                 x_px=cx + 14, y_px=cy + 14, w_px=card_w - 28, h_px=18,
                 font_size_px=9, color=WHITE, bold=True, align="left", uppercase=True,
                 bg_fill=BRAND_ACCENT, padding_px=(2, 8, 2, 8))

        # Challenge / heading
        add_text(slide, f"card-{n}-heading", heading,
                 x_px=cx + 14, y_px=cy + 40, w_px=card_w - 28, h_px=18,
                 font_size_px=12, color=WHITE, bold=True)

        # Stat (big number)
        add_text(slide, f"card-{n}-stat", stat,
                 x_px=cx + 14, y_px=cy + 62, w_px=card_w - 28, h_px=40,
                 font_size_px=22, color=BRAND_ACCENT_SOFT, bold=True)

        # Context body
        add_text(slide, f"card-{n}-body", body,
                 x_px=cx + 14, y_px=cy + 108, w_px=card_w - 28, h_px=card_h - 138,
                 font_size_px=11, color=TEXT_ON_DARK_MID)

        # Source footnote
        add_rect(slide, f"card-{n}-divider", cx + 14, cy + card_h - 28, card_w - 28, 1, CARD_BORDER_DARK)
        add_text(slide, f"card-{n}-footer", source,
                 x_px=cx + 14, y_px=cy + card_h - 22, w_px=card_w - 28, h_px=14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT)

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "144",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "144d_proof-points-compilation.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
