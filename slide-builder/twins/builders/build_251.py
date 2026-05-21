"""
Builder for pattern 251: Problem + 3 forces split panel (dark left, light right with 3 cards).

Source HTML: _pattern-library/251_problem-3-forces-split.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT, CARD_BG, CARD_BORDER, WHITE,
    DRAFT_BG, DRAFT_TEXT,
)


def build():
    prs, slide = new_slide()

    # Layout: left 32% (≈410px), right 68% (≈870px). Slide is 1280 wide.
    left_w = 410
    right_w = 1280 - left_w
    panel_top = 0
    panel_h = 720 - 32  # leave 32px footer

    # Left dark panel
    add_rect(slide, "hero-panel", 0, panel_top, left_w, panel_h, BRAND_PRIMARY)

    # Variant chrome inside left panel

    # Left content
    add_text(slide, "eyebrow", "The Problem",
             x_px=40, y_px=82, w_px=left_w - 80, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "hero-statement",
             "Consultants rarely lack ideas — they struggle to cut through them.",
             x_px=40, y_px=116, w_px=left_w - 80, h_px=240,
             font_size_px=32, color=WHITE, bold=True)
    add_rect(slide, "hero-rule", 40, 376, 40, 3, BRAND_ACCENT)
    add_text(slide, "hero-context",
             "Not a knowledge gap. Not a skill deficit. A structural problem — and structural problems have structural solutions.",
             x_px=40, y_px=400, w_px=left_w - 80, h_px=200,
             font_size_px=15, color=BRAND_ACCENT_SOFT)

    # Right light panel: 3 cards
    add_text(slide, "forces-label", "THREE COMPOUNDING FORCES",
             x_px=left_w + 40, y_px=82, w_px=right_w - 80, h_px=14,
             font_size_px=9, color=BRAND_ACCENT, bold=True, uppercase=True)

    # Cards
    cards_top = 110
    cards_h_area = panel_h - 110 - 40
    card_h = (cards_h_area - 20) // 3
    card_gap = 10
    cards = [
        ("Too much to say", "Knowing what to cut is harder than knowing what to include. Every workstream generates legitimate findings.", "📄"),
        ("Too many cooks", "Every collaborator has a view on what belongs on the page — more opinions mean harder choices, not a richer argument.", "👥"),
        ("The audience needs what's next", "They don't need to understand all the work — they need to understand the next step.", "→"),
    ]
    for i, (title, body, glyph) in enumerate(cards):
        n = i + 1
        cy = cards_top + i * (card_h + card_gap)
        cx = left_w + 40
        cw = right_w - 80
        # Card with brand-accent left border
        card = add_rect(slide, f"card-{n}-body-bg", cx, cy, cw, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        add_rect(slide, f"card-{n}-accent", cx, cy, 4, card_h, BRAND_ACCENT)
        # Icon circle
        ic_size = 48
        ic_x = cx + 24
        ic_y = cy + (card_h - ic_size) // 2
        add_rect(slide, f"card-{n}-icon-bg", ic_x, ic_y, ic_size, ic_size, BRAND_ACCENT)
        add_icon(slide, f"card-{n}-icon", ic_x, ic_y, ic_size, glyph, color=WHITE,
                 font_name="Segoe UI Symbol")
        # Text
        text_x = ic_x + ic_size + 18
        text_w = cw - (ic_size + 60)
        add_text(slide, f"card-{n}-heading", title,
                 x_px=text_x, y_px=cy + 18, w_px=text_w, h_px=24,
                 font_size_px=18, color=BRAND_ACCENT, bold=True)
        add_text(slide, f"card-{n}-body", body,
                 x_px=text_x, y_px=cy + 46, w_px=text_w, h_px=card_h - 56,
                 font_size_px=14, color=TEXT_DARK)

    # Footer
    add_text(slide, "page-number", "251",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "251_problem-3-forces-split.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
