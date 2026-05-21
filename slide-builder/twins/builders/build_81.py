"""
Builder for pattern 81: Target Operating Model (TOM) — 3x2 card grid.

Source HTML: _pattern-library/81_operating-model-tom.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Slide Lab target operating model — six dimensions, one method.",
        subtitle="A TOM is only useful when every dimension reinforces the others. Six dimensions, each with three to four components, define how Slide Lab runs as the default deck-building method across the practice.",
        title_x=48, title_w=1180, title_h=60,
        subtitle_h=40,
        brand_rule_w=56,
    )

    # 3 cols x 2 rows. left:48, right:48, top:176, height:410
    grid_left = 48
    grid_top = 176
    grid_w = 1280 - 96  # 1184
    grid_h = 410
    cols, rows = 3, 2
    gap = 14
    card_w = (grid_w - gap * (cols - 1)) // cols  # ~385
    card_h = (grid_h - gap) // 2  # 198

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

        # Card body
        fill = WHITE if focal else CARD_BG
        card = add_rect(slide, f"card-{n}-shape", cx, cy, card_w, card_h, fill)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525

        # Top accent strip
        accent_color = BRAND_ACCENT if focal else BRAND_ACCENT_SOFT
        add_rect(slide, f"card-{n}-accent", cx, cy, card_w, 3, accent_color)

        # FOCUS badge (top-right) for focal card
        if focal:
            add_text(slide, f"card-{n}-focus", "FOCUS",
                     x_px=cx + card_w - 60, y_px=cy + 10, w_px=50, h_px=14,
                     font_size_px=8, color=BRAND_ACCENT, bold=True,
                     align="center", uppercase=True,
                     bg_fill=BRAND_ACCENT_SOFT, padding_px=(2, 4, 2, 4))

        # Number
        add_text(slide, f"card-{n}-num", num,
                 x_px=cx + 18, y_px=cy + 16, w_px=32, h_px=24,
                 font_size_px=20, color=BRAND_ACCENT, bold=True)

        # Icon placeholder (22px square)
        add_rect(slide, f"card-{n}-icon", cx + 54, cy + 18, 22, 22, BRAND_ACCENT)

        # Heading (uppercase)
        add_text(slide, f"card-{n}-heading", name,
                 x_px=cx + 82, y_px=cy + 18, w_px=card_w - 96, h_px=22,
                 font_size_px=13, color=BRAND_PRIMARY, bold=True, uppercase=True)

        # Tagline (italic)
        add_text(slide, f"card-{n}-tagline", tagline,
                 x_px=cx + 18, y_px=cy + 50, w_px=card_w - 36, h_px=22,
                 font_size_px=11, color=TEXT_MID, italic=True)

        # Components list
        list_top = cy + 78
        for j, item in enumerate(items):
            iy = list_top + j * 22
            # Bullet dot
            add_rect(slide, f"card-{n}-component-{j+1}-dot",
                     cx + 18, iy + 8, 4, 4, BRAND_ACCENT)
            # Component text
            add_text(slide, f"card-{n}-component-{j+1}", item,
                     x_px=cx + 28, y_px=iy, w_px=card_w - 46, h_px=20,
                     font_size_px=11, color=TEXT_DARK)

    # Convergence (small uppercase text, no band)
    add_text(
        slide, "convergence",
        "Six dimensions · one operating model · one method.",
        x_px=48, y_px=720 - 64, w_px=1280 - 96, h_px=20,
        font_size_px=11, color=BRAND_PRIMARY_MID, bold=True,
        align="center", uppercase=True,
    )

    add_footer(slide, page_num=81)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "81_operating-model-tom.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
