"""
Builder for pattern 81d: Target Operating Model (TOM) — dark variant.

Source HTML: _pattern-library/81_operating-model-tom-dark.html
Light template: twins/builders/build_81.py
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

    add_text(slide, "title",
             "Slide Lab target operating model — six dimensions, one method.",
             x_px=48, y_px=20, w_px=1180, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "A TOM is only useful when every dimension reinforces the others. Six dimensions, each with three to four components, define how Slide Lab runs as the default deck-building method across the practice.",
             x_px=48, y_px=108, w_px=1060, h_px=40,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 152, 56, 3, BRAND_ACCENT_SOFT)

    # 3 cols x 2 rows
    grid_left = 48
    grid_top = 220
    grid_w = 1280 - 96
    grid_h = 386
    cols, rows = 3, 2
    gap = 14
    card_w = (grid_w - gap * (cols - 1)) // cols
    card_h = (grid_h - gap) // 2

    cards = [
        ("01", "Strategy", "Vision, priorities, value bundles",
         ["Slide Lab as default method for client work",
          "Pattern library as practice IP",
          "Brand portability across client templates"], False),
        ("02", "Process", "How work flows, gates, hand-offs",
         ["Storyline session before drafting",
          "Gated by QC checklist before delivery",
          "Coach pairing on first three decks"], False),
        ("03", "Organization", "Roles, structure, decision rights",
         ["Coach role — embedded per practice",
          "Pattern librarian — owns the catalog",
          "Practice champions — one per team"], True),
        ("04", "People", "Skills, learning, performance",
         ["90-min onboarding for every consultant",
          "Practice champion certification",
          "Coach development track — quarterly"], False),
        ("05", "Technology", "Platforms, tools, integration",
         ["Claude Code as the substrate",
          "HTML → PPTX render engine",
          "Pattern library — versioned, shared"], False),
        ("06", "Governance", "Cadence, escalation, decision forums",
         ["Weekly pilot review",
          "Monthly practice forum",
          "Quarterly evolution & roadmap"], False),
    ]

    for i, (num, name, tagline, items, focal) in enumerate(cards):
        n = i + 1
        row = i // cols
        col = i % cols
        cx = grid_left + col * (card_w + gap)
        cy = grid_top + row * (card_h + gap)

        fill = BRAND_PRIMARY_MID if focal else CARD_BG_DARK
        card = add_rect(slide, f"card-{n}-shape", cx, cy, card_w, card_h, fill)
        card.line.color.rgb = CARD_BORDER_DARK
        card.line.width = 9525

        accent_color = BRAND_ACCENT if focal else BRAND_ACCENT_SOFT
        add_rect(slide, f"card-{n}-accent", cx, cy, card_w, 3, accent_color)

        if focal:
            add_text(slide, f"card-{n}-focus", "FOCUS",
                     x_px=cx + card_w - 60, y_px=cy + 10, w_px=50, h_px=14,
                     font_size_px=8, color=WHITE, bold=True,
                     align="center", uppercase=True,
                     bg_fill=BRAND_ACCENT, padding_px=(2, 4, 2, 4))

        add_text(slide, f"card-{n}-num", num,
                 x_px=cx + 18, y_px=cy + 16, w_px=32, h_px=24,
                 font_size_px=20, color=BRAND_ACCENT_SOFT, bold=True)

        add_rect(slide, f"card-{n}-icon", cx + 54, cy + 18, 22, 22, BRAND_ACCENT_SOFT)

        add_text(slide, f"card-{n}-heading", name,
                 x_px=cx + 82, y_px=cy + 18, w_px=card_w - 96, h_px=22,
                 font_size_px=13, color=WHITE, bold=True, uppercase=True)

        add_text(slide, f"card-{n}-tagline", tagline,
                 x_px=cx + 18, y_px=cy + 50, w_px=card_w - 36, h_px=22,
                 font_size_px=11, color=TEXT_ON_DARK_MID, italic=True)

        list_top = cy + 78
        for j, item in enumerate(items):
            iy = list_top + j * 22
            add_rect(slide, f"card-{n}-component-{j+1}-dot",
                     cx + 18, iy + 8, 4, 4, BRAND_ACCENT_SOFT)
            add_text(slide, f"card-{n}-component-{j+1}", item,
                     x_px=cx + 28, y_px=iy, w_px=card_w - 46, h_px=20,
                     font_size_px=11, color=WHITE)

    add_text(slide, "convergence",
             "Six dimensions · one operating model · one method.",
             x_px=48, y_px=720 - 64, w_px=1280 - 96, h_px=20,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
             align="center", uppercase=True)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "81",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "81d_operating-model-tom-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
