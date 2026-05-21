"""
Dark variant of pattern 27: Case study — Situation / Action / Result.

Source HTML: _pattern-library/27_case-study-sar-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
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

    # Title block (inline, bottom-anchored)
    add_text(
        slide, "title",
        "Case study — a 30-person practice cut deck cycle time from 14 to 5 days (-64%).",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Same pattern we apply everywhere: storyline first, structured measurement, no bespoke heroics.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    # Cards row at y=220
    grid_left = 56
    card_w = (1280 - 112 - 44) // 3
    card_h = 310
    gap = 22
    card_top = 220

    headers = ["SITUATION", "ACTION", "RESULT"]
    bodies = [
        "A 30-person strategy practice was producing decks in 12–14 days median, with 8 rounds of partner edits per deck. The bottleneck wasn't talent — it was the assembly process.",
        "Ran a four-week pilot with Slide Lab on one priority workstream. Replaced the partner pre-read meeting with a coached storyline session. Measured every deck against the baseline.",
        "Cycle time dropped from 14 to 5 days — a 64% reduction. Partner edits fell from 8 to 3 per deck, and 94% of decks earned stakeholder sign-off on first review.",
    ]
    foot_labels = ["BASELINE", "APPROACH", "AFTER"]
    foot_values = [
        "14 days median · 8 partner edits",
        "4 weeks · 12 decks measured",
        "5 days median · 3 edits · 94% sign-off",
    ]

    for i in range(3):
        n = i + 1
        cx = grid_left + i * (card_w + gap)

        header_h = 50
        is_result = (i == 2)
        header_fill = BRAND_ACCENT_SOFT if is_result else BRAND_PRIMARY_MID
        add_rect(slide, f"card-{n}-header-bg", cx, card_top, card_w, header_h, header_fill)
        add_text(
            slide, f"card-{n}-heading", headers[i],
            x_px=cx + 20, y_px=card_top, w_px=card_w - 40, h_px=header_h,
            font_size_px=13, color=WHITE if not is_result else BRAND_PRIMARY,
            bold=True, anchor="middle", uppercase=True, letter_spacing_px=3,
        )

        body = add_rect(slide, f"card-{n}-body-bg", cx, card_top + header_h, card_w, card_h - header_h, CARD_BG_DARK)
        if is_result:
            body.line.color.rgb = BRAND_ACCENT_SOFT
            body.line.width = 25400
        else:
            body.line.color.rgb = CARD_BORDER_DARK
            body.line.width = 9525

        add_text(
            slide, f"card-{n}-body", bodies[i],
            x_px=cx + 22, y_px=card_top + header_h + 22, w_px=card_w - 44, h_px=card_h - header_h - 100,
            font_size_px=13, color=WHITE,
        )

        rule_y = card_top + card_h - 70

        add_text(
            slide, f"card-{n}-footer-label", foot_labels[i],
            x_px=cx + 22, y_px=rule_y + 14, w_px=card_w - 44, h_px=14,
            font_size_px=9, color=BRAND_ACCENT_SOFT if is_result else TEXT_ON_DARK_FAINT,
            bold=True, uppercase=True, letter_spacing_px=1.4,
        )
        add_text(
            slide, f"card-{n}-footer-value", foot_values[i],
            x_px=cx + 22, y_px=rule_y + 32, w_px=card_w - 44, h_px=22,
            font_size_px=14, color=WHITE, bold=True,
        )

    add_convergence(
        slide,
        "Same pattern, different client. Repeatable, not bespoke.",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(
        slide, "source", "Source: [add source here or delete]",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
    )
    add_text(
        slide, "page-number", "27",
        x_px=1170, y_px=688, w_px=52, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right",
    )
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "27d_case-study-sar.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
