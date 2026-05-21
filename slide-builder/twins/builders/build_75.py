"""
Builder for pattern 75: Quote stack (3 voices).

Source HTML: _pattern-library/75_quote-stack-3.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_MID,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="What the pilot team is saying — three voices, one pattern.",
        subtitle="Different roles, different decks, same shift: the unlock was sharper thinking before building, not faster building.",
        title_h=64,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # 3 quote cards
    card_top = 198
    card_h = 388
    card_w = (1280 - 128 - 40) // 3  # 370
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

        # Card body
        body = add_rect(slide, f"quote-{n}-card", cx, card_top, card_w, card_h, CARD_BG)
        body.line.color.rgb = CARD_BORDER
        body.line.width = 9525

        # Big leading quote mark (Georgia 56px accent)
        add_text(
            slide, f"quote-{n}-mark", "“",
            x_px=cx + 22, y_px=card_top + 18, w_px=60, h_px=50,
            font_size_px=56, color=BRAND_ACCENT, bold=False,
            font_name="Georgia",
        )

        # Quote text (italic, brand-primary)
        add_text(
            slide, f"quote-{n}-text", text,
            x_px=cx + 22, y_px=card_top + 76, w_px=card_w - 44, h_px=200,
            font_size_px=17, color=BRAND_PRIMARY, italic=True, bold=True,
        )

        # Accent rule above attribution
        add_rect(slide, f"quote-{n}-rule",
                 cx + 22, card_top + card_h - 88, 48, 3, BRAND_ACCENT)

        # Attribution name
        add_text(
            slide, f"quote-{n}-attribution-name", name,
            x_px=cx + 22, y_px=card_top + card_h - 70, w_px=card_w - 44, h_px=20,
            font_size_px=14, color=BRAND_PRIMARY, bold=True,
        )
        # Attribution role
        add_text(
            slide, f"quote-{n}-attribution-role", role,
            x_px=cx + 22, y_px=card_top + card_h - 48, w_px=card_w - 44, h_px=18,
            font_size_px=12, color=TEXT_MID, italic=True,
        )

    add_convergence(
        slide,
        "The pattern across all three: structure-first work is what the tool unlocked — speed is the side effect.",
        bottom_px=70, height_px=42,
    )

    add_footer(slide, page_num=75)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "75_quote-stack-3.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
