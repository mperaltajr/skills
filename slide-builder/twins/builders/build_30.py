"""
Builder for pattern 30: Verbatim pull-quote / voice-of-client.

Dark-mode pattern — brand-primary background. Hero quote left, side-context
card right.

Pattern-local IDs: quote-attribution-context, side-context-label, side-context-body.

Source HTML: _pattern-library/30_verbatim-pull-quote.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = BRAND_ACCENT_SOFT
TEXT_ON_DARK_FAINT = RGBColor(0xB8, 0xA5, 0xD9)
SIDE_CARD_BG = RGBColor(0x42, 0x24, 0x68)  # rgba(255,255,255,0.06) approximation on dark


def build():
    prs, slide = new_slide()

    # Dark background
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Variant chrome

    # Stage: top=80, bottom=80, left=88, right=88 → content 1104w × 560h
    # Two cols: quote (flex 1) + 280 side-card, gap 64
    quote_left = 88
    quote_w = 1104 - 280 - 64  # 760
    side_left = 88 + quote_w + 64  # 912
    side_w = 280
    stage_top = 80
    stage_h = 560

    # ---- Quote column ----
    # Pre-label
    pre_y = stage_top + 60
    add_text(
        slide, "eyebrow", "Voice of the practice",
        x_px=quote_left, y_px=pre_y, w_px=quote_w, h_px=16,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
        uppercase=True, letter_spacing_px=3,
    )

    # Big quote mark (decorative)
    add_text(
        slide, "quote-mark", "“",
        x_px=quote_left - 8, y_px=pre_y - 30, w_px=200, h_px=180,
        font_size_px=160, color=BRAND_ACCENT, font_name="Georgia",
    )

    # Quote text (36px italic)
    quote_y = pre_y + 16 + 28 + 56
    add_text(
        slide, "quote-text",
        "I didn’t realize how much of the deck-cycle pain was on me. I thought the tools were broken. Turns out the tool was fine — I just never had a way to sharpen the thinking before I started building.",
        x_px=quote_left, y_px=quote_y, w_px=quote_w, h_px=200,
        font_size_px=32, color=WHITE, italic=True, bold=False,
    )

    # Quote rule (60x3 accent)
    rule_y = quote_y + 200 + 16
    add_rect(slide, "quote-rule", quote_left, rule_y, 60, 3, BRAND_ACCENT)

    # Attribution
    add_text(
        slide, "quote-attribution-name", "Anna Reyes",
        x_px=quote_left, y_px=rule_y + 22, w_px=quote_w, h_px=22,
        font_size_px=16, color=WHITE, bold=True,
    )
    add_text(
        slide, "quote-attribution-role", "Senior Manager, Strategy Practice",
        x_px=quote_left, y_px=rule_y + 46, w_px=quote_w, h_px=20,
        font_size_px=14, color=BRAND_ACCENT_SOFT, italic=True,
    )
    add_text(
        slide, "quote-attribution-context",
        "Week 3 of the four-week Slide Lab pilot · May 2026",
        x_px=quote_left, y_px=rule_y + 70, w_px=quote_w, h_px=18,
        font_size_px=12, color=TEXT_ON_DARK_FAINT,
    )

    # ---- Side context card ----
    side_top = stage_top + 300
    side_h = 180
    add_rect(slide, "side-context-bg", side_left, side_top, side_w, side_h, SIDE_CARD_BG)
    # Accent left border
    add_rect(slide, "side-context-border", side_left, side_top, 3, side_h, BRAND_ACCENT)

    add_text(
        slide, "side-context-label", "Context",
        x_px=side_left + 22, y_px=side_top + 22, w_px=side_w - 44, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        uppercase=True, letter_spacing_px=2.5,
    )
    add_text(
        slide, "side-context-body",
        "Said unprompted in the post-deck retro. Permission granted to share this quote for internal pitch use.",
        x_px=side_left + 22, y_px=side_top + 50, w_px=side_w - 44, h_px=side_h - 70,
        font_size_px=13, color=WHITE,
    )

    # ---- Footer (variant) ----
    add_text(slide, "page-number", "30",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_MID, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "30_verbatim-pull-quote.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
