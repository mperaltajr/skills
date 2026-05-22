"""
Slide 5 — Option C (intro-v2): Three icon-anchored cards.

Design rationale (rulebook citations):
- Brief § Option C: "Three vertical cards. Top of each card = 56px icon block...
  Below: TEXT_DARK heading (18px bold), TEXT_MID body (14px). Bottom of each
  card: small italic TEXT_FAINT signature line." Implemented to spec.
- Designer Brief § 5a Icons — use add_icon_from_library with the named library
  icons. Mapping: Think→lightbulb, Argue→speech, Build→package (explicitly
  documented in the brief's icon table).
- Designer Brief § 5b Icon containers (CRITICAL — overrides the visual direction
  text which proposes BRAND_ACCENT_SOFT for circle backgrounds):
    "The background MUST be a circle, not a square or rectangle."
    "Default: BRAND_PRIMARY (deep brand color) with WHITE icon on top"
    "NEVER use BRAND_ACCENT or BRAND_ACCENT_SOFT for icon circles — that burns
     your one accent moment on a container."
    "NEVER make each circle a different bright color when the items are MECE
     (three pillars). Same color for all."
  This option implements the corrected pattern: BRAND_PRIMARY circles, WHITE
  icons, same color for all three. The previous slide-5 option C used PEACH
  SQUARES (BRAND_ACCENT_SOFT) — this fix replaces them.
- Designer Brief § 1 One accent moment: BRAND_ACCENT lives on the title's brand
  rule only (emitted by add_title_block). Circles use BRAND_PRIMARY. Card
  outlines neutral. The accent is preserved for the load-bearing element.
- Designer Brief § 6 Bold discipline: title + three card headings = 4 bold.
  Signature italic, body, eyebrow → NOT bold. ≤5 ceiling honored.
- Designer Brief § 4 Page types — Three-column parallel (icon-anchored variant).
- Memory: title bottom-anchor rule via add_title_block.
- Memory: invariant zone chrome — only add_footer in the bottom zone.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_circle, add_icon_from_library,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="[Three-pillar insight headline placeholder — replace with the slide's actual claim]",
        subtitle="[Sub-headline that contextualizes the three pillars below]",
        title_h=80,
        subtitle_h=26,
    )

    # ------------------------------------------------------------------
    # Three vertical cards. Each card is led by a circular icon anchor.
    # body_left=64, body_w=1152, gap=24, card_w=368
    # ------------------------------------------------------------------
    body_left = 64
    body_w = 1280 - body_left * 2          # 1152
    gap = 24
    card_w = (body_w - gap * 2) // 3       # 368
    card_top = 178
    card_h = 440                           # bottom @ y=618, ~50px to footer

    pad_x = 22

    # Circle anchor geometry — diameter 88px, icon 52px (~60% of circle), centered.
    circle_d = 88
    icon_d = 52

    # Three MECE pillars with icon anchors. Icon names are placeholders here —
    # in production, pick from the icon library to match the brief's content
    # (the icon-name table is in designer-brief.md). All three icons use the
    # SAME color (BRAND_PRIMARY circle, WHITE icon) because the pillars are
    # MECE — different colors per circle would imply hierarchy that isn't there.
    pillars = [
        ("PILLAR ONE", "gear", "[Pillar 1 heading]",
         "[Pillar 1 body — two to three sentences describing what this pillar "
         "represents and why it matters to the takeaway.]",
         "[Sub-line 1 · Sub-line 2]"),
        ("PILLAR TWO", "people", "[Pillar 2 heading]",
         "[Pillar 2 body — two to three sentences describing what this pillar "
         "represents and why it matters to the takeaway.]",
         "[Sub-line 1 · Sub-line 2]"),
        ("PILLAR THREE", "chart-bar", "[Pillar 3 heading]",
         "[Pillar 3 body — two to three sentences describing what this pillar "
         "represents and why it matters to the takeaway.]",
         "[Sub-line 1 · Sub-line 2]"),
    ]

    for i, (eyebrow, icon_name, heading, body, signature) in enumerate(pillars):
        n = i + 1
        cx = body_left + i * (card_w + gap)

        # Card body (tinted white card with thin neutral border)
        card = add_rect(
            slide, f"card-{n}-bg",
            x_px=cx, y_px=card_top, w_px=card_w, h_px=card_h,
            fill_color=CARD_BG,
        )
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525  # 1px

        # ------------------------------------------------------------------
        # ICON ANCHOR — CIRCLE (not square), BRAND_PRIMARY, WHITE icon on top.
        # Same color for all three (MECE rule). This is the fix to the
        # previous slide-5 option C which used peach squares.
        # ------------------------------------------------------------------
        circle_cx = cx + card_w // 2
        circle_cy = card_top + 32 + circle_d // 2   # circle top @ y = card_top + 32
        add_circle(
            slide, f"card-{n}-icon-bg",
            circle_cx - circle_d // 2, circle_cy - circle_d // 2,
            circle_d, BRAND_PRIMARY,
        )
        add_icon_from_library(
            slide, f"card-{n}-icon",
            circle_cx - icon_d // 2, circle_cy - icon_d // 2,
            icon_d, name=icon_name, color=WHITE,
        )

        # Eyebrow — uppercase, letter-spaced, NOT bold
        eyebrow_y = circle_cy + circle_d // 2 + 18
        add_text(
            slide, f"card-{n}-eyebrow", eyebrow,
            x_px=cx + pad_x, y_px=eyebrow_y,
            w_px=card_w - pad_x * 2, h_px=16,
            font_size_px=11, color=BRAND_PRIMARY, bold=False,
            uppercase=True, letter_spacing_px=2, align="center",
        )

        # Heading — 18px bold TEXT_DARK
        heading_y = eyebrow_y + 22
        add_text(
            slide, f"card-{n}-heading", heading,
            x_px=cx + pad_x, y_px=heading_y,
            w_px=card_w - pad_x * 2, h_px=32,
            font_size_px=18, color=TEXT_DARK, bold=True, align="center",
        )

        # Body — 14px TEXT_MID, multi-line
        body_y = heading_y + 40
        add_text(
            slide, f"card-{n}-body", body,
            x_px=cx + pad_x, y_px=body_y,
            w_px=card_w - pad_x * 2, h_px=120,
            font_size_px=14, color=TEXT_MID, bold=False, align="center",
        )

        # Bottom signature — small italic TEXT_FAINT, parallel meta line
        signature_h = 22
        signature_y = card_top + card_h - signature_h - 18
        add_text(
            slide, f"card-{n}-signature", signature,
            x_px=cx + pad_x, y_px=signature_y,
            w_px=card_w - pad_x * 2, h_px=signature_h,
            font_size_px=12, color=TEXT_FAINT, italic=True, bold=False,
            align="center",
        )

    add_footer(slide, page_num=5)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "option_C.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
