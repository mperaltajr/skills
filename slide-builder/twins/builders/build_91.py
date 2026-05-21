"""
Builder for pattern 91: North star metric (dark mode hero stat + 4 input cards).

Source HTML: _pattern-library/91_north-star-metric.html

Dark mode: brand-primary background, white/accent-soft text.
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

TEXT_ON_DARK_FAINT = RGBColor(0xB8, 0xA5, 0xD9)
CARD_BG_DARK = RGBColor(0x3D, 0x1A, 0x5E)  # subtle lighter brand for cards
CARD_BORDER_DARK = RGBColor(0x55, 0x32, 0x82)


def build():
    prs, slide = new_slide()

    # Dark background
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Dark-variant chrome

    # Title block — eyebrow + title + subtitle + rule
    add_text(slide, "eyebrow", "Slide Lab · Operating metric",
             x_px=64, y_px=64, w_px=600, h_px=14,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "title",
             "Our north star — partner-ready deck sign-off rate.",
             x_px=64, y_px=86, w_px=1100, h_px=66,
             font_size_px=26, color=WHITE, bold=True)
    add_text(slide, "subtitle",
             "One number we optimize for. Everything else is an input that moves it.",
             x_px=64, y_px=160, w_px=1100, h_px=22,
             font_size_px=13, color=TEXT_ON_DARK_FAINT, italic=True)
    add_rect(slide, "brand-rule", 64, 192, 56, 3, BRAND_ACCENT)

    # Hero stat — centered
    hero_top = 220
    add_text(slide, "hero-stat-label", "OUR NORTH STAR",
             x_px=64, y_px=hero_top, w_px=1280 - 128, h_px=18,
             font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True,
             align="center", uppercase=True)
    add_text(slide, "hero-stat-value", "94%",
             x_px=64, y_px=hero_top + 30, w_px=1280 - 128, h_px=180,
             font_size_px=168, color=WHITE, bold=True, align="center")
    add_text(slide, "hero-stat-caption",
             "Decks that pass first partner review without rework.",
             x_px=64, y_px=hero_top + 220, w_px=1280 - 128, h_px=28,
             font_size_px=19, color=BRAND_ACCENT_SOFT, italic=True, align="center")
    # Hero rule (centered)
    add_rect(slide, "hero-rule",
             (1280 - 96) // 2, hero_top + 256, 96, 3, BRAND_ACCENT)

    # Inputs row — 4 cards, top:528
    inputs_top = 510
    inputs_header_y = inputs_top
    add_text(slide, "inputs-header",
             "INPUT METRICS — WHAT WE ACTUALLY MOVE WEEK TO WEEK",
             x_px=64, y_px=inputs_header_y, w_px=1280 - 128, h_px=14,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True,
             align="center", uppercase=True)

    cards_top = inputs_header_y + 24
    card_h = 96
    card_w = (1280 - 128 - 48) // 4  # 264
    gap = 16

    inputs = [
        ("5", "days", "Median cycle time, brief to final deck"),
        ("80", "%", "Decks with pre-build storyline coaching"),
        ("100", "patterns", "Live in the slide pattern library"),
        ("4", "coaches", "Senior reviewers certified on the method"),
    ]
    for i, (val, unit, label) in enumerate(inputs):
        n = i + 1
        cx = 64 + i * (card_w + gap)
        card = add_rect(slide, f"input-{n}", cx, cards_top, card_w, card_h, CARD_BG_DARK)
        card.line.color.rgb = CARD_BORDER_DARK
        card.line.width = 9525
        # Top accent strip
        add_rect(slide, f"input-{n}-accent", cx, cards_top, card_w, 2, BRAND_ACCENT)

        add_text(slide, f"input-{n}-value", val,
                 x_px=cx + 18, y_px=cards_top + 14, w_px=120, h_px=40,
                 font_size_px=32, color=WHITE, bold=True)
        add_text(slide, f"input-{n}-unit", unit,
                 x_px=cx + 18 + min(70, len(val) * 22), y_px=cards_top + 28,
                 w_px=card_w - 100, h_px=22,
                 font_size_px=13, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"input-{n}-label", label,
                 x_px=cx + 18, y_px=cards_top + 56, w_px=card_w - 36, h_px=36,
                 font_size_px=11, color=TEXT_ON_DARK_FAINT, bold=True)

    # Convergence (small italic, centered)
    add_text(slide, "convergence",
             "Move the input metrics; the north star moves.",
             x_px=64, y_px=cards_top + card_h + 18, w_px=1280 - 128, h_px=18,
             font_size_px=12, color=TEXT_ON_DARK_FAINT, italic=True, align="center")

    # Dark footer
    add_text(slide, "page-number", "91",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "91_north-star-metric.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
