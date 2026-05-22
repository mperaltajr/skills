"""
Three-column parallel / dark-header-cards — Option B variant.

Family: Three-column parallel
Variant: Dark BRAND_PRIMARY header cap on each card (top 35% of card height).
         White hero label + heading text inside the dark cap. Light body below.
         This is structurally distinct from 3pillar-icon-circles (which uses
         circle icon containers) — here the entire card TOP is the dark color
         block.

Layout shape: Three equal-width cards spanning full body width.
              Each card: dark header cap (top ~155px, BRAND_PRIMARY fill, WHITE
              text) + light card body (CARD_BG fill, TEXT_DARK/TEXT_MID).
              Body zone: y=152→620. Cards run full body height.

Content treatment: Eyebrow label (uppercase) + bold heading inside the dark cap.
                   Three body bullets + a bottom meta line in the light section.

Visual differentiator: The DARK CAP replaces the icon circle. Cards are banded
                       (dark top / light bottom) giving a strong horizontal rhythm.
                       One accent moment: BRAND_ACCENT 4px horizontal rule at the
                       bottom edge of each dark cap — acting as the "hinge" line.
                       Wait — that would be THREE accent moments (one per card).
                       Rule: the accent appears on the LEFT EDGE of the first card
                       only (load-bearing element, as a 6px strip). Other cards
                       get 1px TEXT_FAINT lines instead.

Rulebook citations:
- Bold discipline (§ 6): title (1) + 3 card headings = 4 bold runs. ≤5 ceiling.
  Eyebrows, bullet text, meta lines all NOT bold.
- One accent moment: BRAND_ACCENT 6px left-edge strip on card 1 only.
  Other cards use CARD_BORDER 1px. The accent marks card-1 as primary — useful
  for "Pillar 1 is the big one" layouts.
- Body font floor: bullets at 14px TEXT_DARK. Meta line at 12px italic TEXT_FAINT.
- Eyebrows at 11px uppercase.
- No icons — purely typographic inside the dark cap. Structural delta from
  3pillar-icon-circles is clear at thumbnail size: color band vs. circle.
- Bottom of body cards at y≈620 — no dead space below.
- Footer = add_footer(slide, page_num=2).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="[Pillar headline — the unifying so-what across all three]",
        subtitle="[Sub-headline: what these three areas have in common, or why they matter together]",
    )

    # ── Card geometry ──
    body_left = 64
    body_w = 1280 - body_left * 2   # 1152
    gap = 20
    card_w = (body_w - gap * 2) // 3  # 370
    card_top = 152
    card_h = 468                      # bottom @ y=620
    cap_h = 155                       # dark header cap height
    pad_x = 20
    pad_y = 16

    # Pillar data — all placeholder content
    pillars = [
        ("PILLAR ONE",   "[Heading: first pillar]",
         ["[Key point A for pillar one]",
          "[Key point B for pillar one]",
          "[Key point C for pillar one]"],
         "[Meta: supporting reference or call-to-action]"),
        ("PILLAR TWO",   "[Heading: second pillar]",
         ["[Key point A for pillar two]",
          "[Key point B for pillar two]",
          "[Key point C for pillar two]"],
         "[Meta: supporting reference or call-to-action]"),
        ("PILLAR THREE", "[Heading: third pillar]",
         ["[Key point A for pillar three]",
          "[Key point B for pillar three]",
          "[Key point C for pillar three]"],
         "[Meta: supporting reference or call-to-action]"),
    ]

    for i, (eyebrow, heading, bullets, meta) in enumerate(pillars):
        n = i + 1
        cx = body_left + i * (card_w + gap)

        # ── Full card background (light section bottom) ──
        add_rect(
            slide, f"card-{n}-bg",
            x_px=cx, y_px=card_top, w_px=card_w, h_px=card_h,
            fill_color=CARD_BG, no_line=True,
        )

        # ── Card outline ──
        # Card 1: accent left-edge 6px strip (the ONE accent moment for this family)
        # Cards 2-3: 1px CARD_BORDER outline drawn as a thin rect on left edge only
        if n == 1:
            add_rect(
                slide, f"card-{n}-accent-strip",
                x_px=cx, y_px=card_top, w_px=6, h_px=card_h,
                fill_color=BRAND_ACCENT,
            )
        else:
            add_rect(
                slide, f"card-{n}-left-rule",
                x_px=cx, y_px=card_top, w_px=1, h_px=card_h,
                fill_color=CARD_BORDER,
            )

        # ── Dark header cap ──
        add_rect(
            slide, f"card-{n}-cap",
            x_px=cx, y_px=card_top, w_px=card_w, h_px=cap_h,
            fill_color=BRAND_PRIMARY,
        )

        # Eyebrow inside cap
        add_text(
            slide, f"card-{n}-eyebrow", eyebrow,
            x_px=cx + pad_x, y_px=card_top + pad_y,
            w_px=card_w - pad_x * 2, h_px=16,
            font_size_px=11, color=WHITE, bold=False,
            uppercase=True, letter_spacing_px=2,
        )

        # Heading inside cap — bold WHITE
        add_text(
            slide, f"card-{n}-heading", heading,
            x_px=cx + pad_x, y_px=card_top + pad_y + 22,
            w_px=card_w - pad_x * 2, h_px=80,
            font_size_px=18, color=WHITE, bold=True,
        )

        # ── Light body section (bullets) ──
        bullet_y0 = card_top + cap_h + 16
        row_h = 50
        sq = 8

        for j, bullet_text in enumerate(bullets):
            by = bullet_y0 + j * row_h
            add_rect(
                slide, f"card-{n}-bullet-{j+1}-marker",
                x_px=cx + pad_x, y_px=by + 5, w_px=sq, h_px=sq,
                fill_color=BRAND_PRIMARY,
            )
            add_text(
                slide, f"card-{n}-bullet-{j+1}-text", bullet_text,
                x_px=cx + pad_x + sq + 10, y_px=by,
                w_px=card_w - pad_x * 2 - sq - 10, h_px=row_h,
                font_size_px=14, color=TEXT_DARK, bold=False,
            )

        # ── Bottom meta line ──
        meta_y = card_top + card_h - 30
        add_text(
            slide, f"card-{n}-meta", meta,
            x_px=cx + pad_x, y_px=meta_y,
            w_px=card_w - pad_x * 2, h_px=22,
            font_size_px=12, color=TEXT_FAINT, italic=True, bold=False,
        )

    add_footer(slide, page_num=2)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
