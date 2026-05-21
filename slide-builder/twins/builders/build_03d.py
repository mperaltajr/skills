"""
Builder for pattern 03d: Hero statement + 4 supporting cards — DARK variant.

Light source: twins/builders/build_03.py
Note: 03 doesn't use the canonical title block (has eyebrow + 38px hero).
For 03d we KEEP the editorial layout but apply canonical chrome y positions:
title remains hero-style (large), but anchor=bottom and a brand-rule below subtitle.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
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

    # Eyebrow
    add_text(
        slide, "eyebrow", "What Slide Lab actually is",
        x_px=64, y_px=64, w_px=600, h_px=18,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )

    # Hero / title (38px, white, bold)
    add_text(
        slide, "title", "A thought partner — not a slide machine.",
        x_px=64, y_px=88, w_px=1000, h_px=92,
        font_size_px=38, color=WHITE, bold=True,
    )

    # Hero rule
    add_rect(slide, "brand-rule", x_px=64, y_px=188, w_px=80, h_px=4, fill_color=BRAND_ACCENT_SOFT)

    # Subtitle
    add_text(
        slide, "subtitle",
        "It sharpens your thinking before it builds anything. Four mechanisms make that work — every session, every deck, every time.",
        x_px=64, y_px=210, w_px=880, h_px=44,
        font_size_px=16, color=TEXT_ON_DARK_MID, italic=True,
    )

    # Spacer-rule
    add_rect(slide, "spacer-rule", x_px=64, y_px=340, w_px=40, h_px=1, fill_color=CARD_BORDER_DARK)

    cards_top = 400
    card_h = 170
    gap = 20
    card_w = (1280 - 128 - 3 * gap) // 4

    card_data = [
        ("01", "Sharpens the thesis",
         "Pulls the governing thought out of the raw work before you touch a slide. Forces the headline to do the work."),
        ("02", "Challenges the structure",
         "Tests MECE before drafting. Names the gaps. Refuses to build a slide on top of a weak frame."),
        ("03", "Argues with you",
         "Pushes back on weak claims and surfaces counterexamples. No yes-and energy that bloats decks."),
        ("04", "Builds when ready",
         "Renders a real PPTX in your brand template — not a screenshot, not a markdown export. A deck you can present."),
    ]
    for i, (num, heading, body) in enumerate(card_data):
        n = i + 1
        cx = 64 + i * (card_w + gap)
        bg2 = add_rect(slide, f"card-{n}-bg", cx, cards_top, card_w, card_h, CARD_BG_DARK)
        bg2.line.color.rgb = CARD_BORDER_DARK
        bg2.line.width = 9525
        add_rect(slide, f"card-{n}-accent", cx, cards_top, card_w, 3, BRAND_ACCENT_SOFT)
        add_text(
            slide, f"card-{n}-num", num,
            x_px=cx + 18, y_px=cards_top + 16, w_px=card_w - 36, h_px=28,
            font_size_px=22, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"card-{n}-heading", heading,
            x_px=cx + 18, y_px=cards_top + 48, w_px=card_w - 36, h_px=22,
            font_size_px=14, color=WHITE, bold=True,
        )
        add_text(
            slide, f"card-{n}-body", body,
            x_px=cx + 18, y_px=cards_top + 72, w_px=card_w - 36, h_px=card_h - 80,
            font_size_px=12, color=TEXT_ON_DARK_MID,
        )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "4",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "03d_hero-statement-supporting-cards.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
