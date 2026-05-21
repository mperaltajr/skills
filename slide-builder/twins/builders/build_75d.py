"""
Builder for pattern 75d: Quote stack (3 voices) — dark variant.

Source HTML: _pattern-library/75_quote-stack-3-dark.html
Light template: twins/builders/build_75.py
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


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Inline dark chrome
    add_text(slide, "title",
             "What the pilot team is saying — three voices, one pattern.",
             x_px=64, y_px=20, w_px=1000, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Different roles, different decks, same shift: the unlock was sharper thinking before building, not faster building.",
             x_px=64, y_px=108, w_px=880, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 56, 3, BRAND_ACCENT_SOFT)

    # 3 quote cards
    card_top = 220
    card_h = 380
    card_w = (1280 - 128 - 40) // 3
    gap = 20

    quotes = [
        ("I spend more time on slide structure than slide content. That's backwards.",
         "Sarah Kim", "Senior Manager"),
        ("The first time the model pushed back on my own thinking. That moment was the unlock.",
         "David Chen", "Partner"),
        ("My junior built a partner-ready deck in week 2 — that didn't used to happen.",
         "Maria Rivera", "Director"),
    ]

    for i, (text, name, role) in enumerate(quotes):
        n = i + 1
        cx = 64 + i * (card_w + gap)

        body = add_rect(slide, f"quote-{n}-card", cx, card_top, card_w, card_h, CARD_BG_DARK)
        body.line.color.rgb = CARD_BORDER_DARK
        body.line.width = 9525

        add_text(slide, f"quote-{n}-mark", "“",
                 x_px=cx + 22, y_px=card_top + 18, w_px=60, h_px=50,
                 font_size_px=56, color=BRAND_ACCENT_SOFT, bold=False,
                 font_name="Georgia")

        add_text(slide, f"quote-{n}-text", text,
                 x_px=cx + 22, y_px=card_top + 76, w_px=card_w - 44, h_px=200,
                 font_size_px=17, color=WHITE, italic=True, bold=True)

        add_rect(slide, f"quote-{n}-rule",
                 cx + 22, card_top + card_h - 88, 48, 3, BRAND_ACCENT_SOFT)

        add_text(slide, f"quote-{n}-attribution-name", name,
                 x_px=cx + 22, y_px=card_top + card_h - 70, w_px=card_w - 44, h_px=20,
                 font_size_px=14, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"quote-{n}-attribution-role", role,
                 x_px=cx + 22, y_px=card_top + card_h - 48, w_px=card_w - 44, h_px=18,
                 font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)

    # Convergence band (dark mode: lighter mid + soft text)
    conv_y = 720 - 70 - 42
    conv_h = 42
    add_rect(slide, "convergence-bg", 64, conv_y, 1280 - 128, conv_h, BRAND_PRIMARY_MID)
    add_text(slide, "convergence",
             "The pattern across all three: structure-first work is what the tool unlocked — speed is the side effect.",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=conv_h,
             font_size_px=14, color=WHITE, italic=True, anchor="middle",
             padding_px=(0, 22, 0, 22))

    # Dark footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "75",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "75d_quote-stack-3-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
