"""
anchor-with-cards-4 — Four-column SCQA-style executive summary.

Page-type family: Structured text (Executive-summary / four-pillar parallel).

This is the four-column sibling of dark-header-cards and three-column-vanilla.
The classic shape: an action-title thesis up top, then four equal-weight cards
that read left-to-right as a single SCQA-style sentence — Problem, Solution,
Outcomes, Strategic Rationale. The slide IS the executive summary.

Design rationale (rulebook citations):
- Designer Brief § 4 Page types — Structured-text / executive-summary variant
  with four parallel columns. Use when content is genuinely MECE in four parts
  AND each part is short enough to live in ~265px of column width. Five-card
  is over-cap; three-card collapses one of the SCQA beats — four is the
  Goldilocks count for this specific narrative shape.
- Designer Brief § 1 One accent moment: BRAND_ACCENT lives on a single 4px
  top-edge stripe across Card 1 (the "Problem / Situation"). That signals
  "start reading here" without burning the accent across all four cards.
  Cards 2-4 carry a 1px CARD_BORDER outline only.
- Designer Brief § 6 Bold discipline: title (1) + 4 card headings (4) = 5
  bold runs. AT ceiling — no other bold allowed. Eyebrows uppercase NOT bold;
  body NOT bold; meta NOT bold.
- add_title_block: 28pt title bottom-anchored at y=100, 16pt italic subtitle.
  No auto brand-rule (handled by helper). Subtitle here carries the SCQA
  framing in plain English.
- Memory: invariant zone chrome — only add_footer in the bottom zone; no
  ACCENTURE / DRAFT / CONFIDENTIAL tags.
- Memory: TEXT_MID / TEXT_FAINT aliased to TEXT_DARK — hierarchy from size /
  weight / italic only.

Differentiator vs neighbors:
- vs anchor-with-cards (3-row): that layout has a tall left BRAND_PRIMARY
  anchor panel and 3 stacked rows. This one is a flat 4-column grid with no
  anchor panel — equal-weight cards.
- vs dark-header-cards (3-col): three cards with dark caps. This is four
  cards with light bodies and a single accent stripe.
- vs three-column-vanilla: three cards. Same vanilla card treatment, but the
  four-column version reads as the full SCQA arc rather than three parallel
  priorities.
"""
from pathlib import Path
import sys

sys.path.insert(0, r"C:\Users\m.a.peralta\.claude\skills\slide-builder")

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK,
    CARD_BG, CARD_BORDER,
)


def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="[Insight headline placeholder — the executive-summary thesis in one line]",
        subtitle="[Sub-headline placeholder — the SCQA framing in plain English]",
    )

    # ------------------------------------------------------------------
    # Four vertical cards. body_left=48, body_w=1184, gap=16, card_w=287.
    # Cards start below the subtitle (~y=160) and reach to ~y=618 to leave
    # ~50px to the footer.
    # ------------------------------------------------------------------
    body_left = 48
    body_w = 1280 - body_left * 2            # 1184
    gap = 16
    card_w = (body_w - gap * 3) // 4         # 284
    card_top = 168
    card_h = 452                             # bottom @ y=620

    pad_x = 18
    pad_top = 24

    # Card 1 is the load-bearing card — it gets the accent top-stripe.
    accent_card_idx = 0

    cards = [
        ("01  PROBLEM",
         "[Card 1 heading — the problem or opportunity]",
         "[Card 1 body — summarize the underlying problem or opportunity "
         "this business case addresses. Two or three short sentences.]"),
        ("02  SOLUTION",
         "[Card 2 heading — the proposed solution]",
         "[Card 2 body — summarize the suggested solution to the problem or "
         "opportunity above. Two or three short sentences.]"),
        ("03  OUTCOMES",
         "[Card 3 heading — outcomes and benefits]",
         "[Card 3 body — summarize the outcomes and benefits that can be "
         "expected from successful execution. Two or three short sentences.]"),
        ("04  RATIONALE",
         "[Card 4 heading — strategic rationale]",
         "[Card 4 body — summarize the strategic rationale for addressing "
         "the problem now. Two or three short sentences.]"),
    ]

    for i, (eyebrow, heading, body) in enumerate(cards):
        n = i + 1
        cx = body_left + i * (card_w + gap)

        # Card body — CARD_BG fill, 1px CARD_BORDER outline.
        card = add_rect(
            slide, f"card-{n}-bg",
            x_px=cx, y_px=card_top, w_px=card_w, h_px=card_h,
            fill_color=CARD_BG,
        )
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525  # 1px

        # ONE accent moment — 4px top-edge stripe on Card 1 only.
        if i == accent_card_idx:
            add_rect(
                slide, f"card-{n}-accent-stripe",
                x_px=cx, y_px=card_top, w_px=card_w, h_px=4,
                fill_color=BRAND_ACCENT,
            )

        # Eyebrow — uppercase numbered label, BRAND_PRIMARY, NOT bold.
        eyebrow_y = card_top + pad_top
        add_text(
            slide, f"card-{n}-eyebrow", eyebrow,
            x_px=cx + pad_x, y_px=eyebrow_y,
            w_px=card_w - pad_x * 2, h_px=16,
            font_size_px=11, color=BRAND_PRIMARY, bold=False,
            uppercase=True, letter_spacing_px=2, align="left",
        )

        # Heading — 18px bold BRAND_PRIMARY. Slightly smaller than the
        # 3-column vanilla heading (20px) because column width is narrower.
        heading_y = eyebrow_y + 26
        add_text(
            slide, f"card-{n}-heading", heading,
            x_px=cx + pad_x, y_px=heading_y,
            w_px=card_w - pad_x * 2, h_px=64,
            font_size_px=18, color=BRAND_PRIMARY, bold=True, align="left",
        )

        # Body — 13px TEXT_DARK, NOT bold, left-aligned editorial read.
        # 13px (not 14px) keeps the four columns from feeling cramped at this
        # width while staying above the brief's body-floor of 12px.
        body_y = heading_y + 76
        add_text(
            slide, f"card-{n}-body", body,
            x_px=cx + pad_x, y_px=body_y,
            w_px=card_w - pad_x * 2, h_px=card_h - (body_y - card_top) - pad_top,
            font_size_px=13, color=TEXT_DARK, bold=False, align="left",
        )

    add_footer(slide, page_num=1)
    return prs


if __name__ == "__main__":
    build().save(Path(__file__).with_suffix(".pptx"))
