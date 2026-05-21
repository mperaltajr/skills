"""
Builder for pattern 03: Hero statement + 4 supporting cards.

Source HTML: _pattern-library/03_hero-statement-supporting-cards.html
Variant — uses an eyebrow + larger hero "title" + spacer-rule + 4 numbered cards.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Eyebrow (brand-accent, uppercase, 11px)
    add_text(
        slide, "eyebrow", "What Slide Lab actually is",
        x_px=64, y_px=64, w_px=600, h_px=18,
        font_size_px=11, color=BRAND_ACCENT, bold=True, uppercase=True,
    )

    # Hero / title (38px, brand-primary, bold)
    add_text(
        slide, "title", "A thought partner — not a slide machine.",
        x_px=64, y_px=88, w_px=1000, h_px=92,
        font_size_px=38, color=BRAND_PRIMARY, bold=True,
    )

    # Hero rule — 80x4 brand-accent
    add_rect(slide, "brand-rule", x_px=64, y_px=188, w_px=80, h_px=4, fill_color=BRAND_ACCENT)

    # Subtitle (italic 16px, text-mid)
    add_text(
        slide, "subtitle",
        "It sharpens your thinking before it builds anything. Four mechanisms make that work — every session, every deck, every time.",
        x_px=64, y_px=210, w_px=880, h_px=44,
        font_size_px=16, color=TEXT_MID, italic=True,
    )

    # Spacer-rule (40x1, card-border) ~ centered at y=340
    add_rect(slide, "spacer-rule", x_px=64, y_px=340, w_px=40, h_px=1, fill_color=CARD_BORDER)

    # 4-card row (170h, grid-template-columns:repeat(4,1fr) gap:20)
    cards_top = 400
    card_h = 170
    gap = 20
    card_w = (1280 - 128 - 3 * gap) // 4  # = 273

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
        # Card bg
        bg = add_rect(slide, f"card-{n}-bg", cx, cards_top, card_w, card_h, CARD_BG)
        bg.line.color.rgb = CARD_BORDER
        bg.line.width = 9525
        # 3px brand-accent top
        add_rect(slide, f"card-{n}-accent", cx, cards_top, card_w, 3, BRAND_ACCENT)
        # Card num (22px brand-accent-soft, bold)
        add_text(
            slide, f"card-{n}-num", num,
            x_px=cx + 18, y_px=cards_top + 16, w_px=card_w - 36, h_px=28,
            font_size_px=22, color=BRAND_ACCENT_SOFT, bold=True,
        )
        # Heading (14px brand-primary, bold)
        add_text(
            slide, f"card-{n}-heading", heading,
            x_px=cx + 18, y_px=cards_top + 48, w_px=card_w - 36, h_px=22,
            font_size_px=14, color=BRAND_PRIMARY, bold=True,
        )
        # Body
        add_text(
            slide, f"card-{n}-body", body,
            x_px=cx + 18, y_px=cards_top + 72, w_px=card_w - 36, h_px=card_h - 80,
            font_size_px=12, color=TEXT_DARK,
        )

    add_footer(slide, page_num=4)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "03_hero-statement-supporting-cards.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
