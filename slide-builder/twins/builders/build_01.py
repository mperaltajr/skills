"""
Builder for pattern 01: Anchor with cards + icons.

Source HTML: _pattern-library/01_anchor-with-cards-icons.html
"""
from pathlib import Path
import sys

# Allow running directly
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_MID,
)


def build():
    """Construct pattern 01's PPTX twin. Returns the Presentation."""
    prs, slide = new_slide()

    add_chrome(slide)

    add_title_block(
        slide,
        title="Consultants rarely lack ideas — they struggle to <strong>cut through them</strong>.",
        subtitle="Not a knowledge gap. Not a skill deficit. A structural one — and structural problems have structural solutions.",
    )

    card_glyphs = ["☰", "✦", "→"]

    # Cards grid: 3 columns at top: 290px, left: 64, right: 64, gap: 24
    # Card width = (1280 - 128 - 48) / 3 = 368
    card_y = 290
    card_w = 368
    card_h = 200
    gap = 24

    for i in range(3):
        cx = 64 + i * (card_w + gap)
        n = i + 1

        # Card body (background + border)
        body = add_rect(slide, f"card-{n}-body-bg", cx, card_y, card_w, card_h, CARD_BG)
        body.line.color.rgb = CARD_BORDER
        body.line.width = 9525  # 1px

        # Top accent strip (2px tall, brand-accent-soft)
        add_rect(slide, f"card-{n}-accent", cx, card_y, card_w, 2, BRAND_ACCENT_SOFT)

        # Icon (Unicode glyph in brand-accent)
        add_icon(slide, f"card-{n}-icon", cx + 22, card_y + 22, 30, card_glyphs[i],
                 color=BRAND_ACCENT)

        # Card heading
        add_text(
            slide, f"card-{n}-heading",
            ["Too much to say", "Too many cooks", "The audience needs what's next"][i],
            x_px=cx + 22, y_px=card_y + 22 + 30 + 14,
            w_px=card_w - 44, h_px=22,
            font_size_px=16, color=BRAND_PRIMARY, bold=True,
        )

        # Card body text
        add_text(
            slide, f"card-{n}-body",
            [
                "Knowing what to cut is harder than knowing what to include. Every workstream produces legitimate findings, and not all of them belong on the page.",
                "Every collaborator has a view on what belongs on the page. More opinions mean harder choices, not a richer argument.",
                "They don't need to understand all the work. They need to understand the next step — and most decks bury it.",
            ][i],
            x_px=cx + 22, y_px=card_y + 22 + 30 + 14 + 22 + 8,
            w_px=card_w - 44, h_px=card_h - (22 + 30 + 14 + 22 + 8) - 22,
            font_size_px=13, color=TEXT_MID,
        )

    add_convergence(
        slide,
        "The fix is a structured way to think, argue, and build — not another tool that produces slides faster.",
    )

    add_footer(slide, page_num=2)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "01_anchor-with-cards-icons.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
