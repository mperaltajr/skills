"""
three-column-vanilla — Three parallel text cards, NO icons.

The text-only sibling of 3pillar-icon-circles. Same three-card parallel layout,
but each card is led by a typographic heading instead of a circle-icon anchor.

Design rationale (rulebook citations):
- Designer Brief § 4 Page types — Three-column parallel (vanilla / no-icon
  variant). Reach for this when content is text-heavy and an icon would
  compete with the heading, OR when the client template has no icon
  precedent and dropping in a glyph would feel imported rather than native.
- Designer Brief § 1 One accent moment: BRAND_ACCENT lives on ONE element
  only. This exemplar puts the accent on a 3px top-edge stripe on the
  load-bearing column (column 1). The other two columns get a neutral
  CARD_BORDER outline. Title block deliberately carries NO accent (the new
  add_title_block emits no brand-rule) so the column stripe owns the moment.
- Designer Brief § 6 Bold discipline: title + 3 column headings = 4 bold
  elements. Eyebrow uppercase NOT bold; body NOT bold. ≤5 ceiling honored.
- Memory: title bottom-anchor — handled by add_title_block (28pt title,
  16pt italic subtitle, no auto brand-rule).
- Memory: invariant zone chrome — only add_footer in the bottom zone; no
  ACCENTURE / DRAFT / CONFIDENTIAL tags.
- Memory: TEXT_MID / TEXT_FAINT aliased to TEXT_DARK — hierarchy comes from
  size + weight + italic, not from gray gradients.

Differentiator vs 3pillar-icon-circles:
- No circles, no icons, no eyebrow-over-icon stack. The card opens with a
  typographic heading. This produces a calmer, more editorial three-column
  read suited to text-dense pillars (e.g., three objectives with rationale,
  three strategic priorities with measurable detail).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK,
    CARD_BG, CARD_BORDER,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="[Action title — three parallel priorities and why they matter together]",
        subtitle="[Sub-headline — one sentence framing the trio]",
    )

    # ------------------------------------------------------------------
    # Three vertical cards. body_left=64, body_w=1152, gap=24, card_w=368.
    # Cards start below the subtitle (~y=160) and reach to ~y=618 to leave
    # ~50px to the footer.
    # ------------------------------------------------------------------
    body_left = 64
    body_w = 1280 - body_left * 2          # 1152
    gap = 24
    card_w = (body_w - gap * 2) // 3       # 368
    card_top = 178
    card_h = 440

    pad_x = 24
    pad_top = 28

    # Column 1 is the load-bearing column — it gets the accent stripe.
    # Columns 2 and 3 are neutral. (If the brief's load-bearing column is a
    # different one, swap the index — there must be EXACTLY ONE.)
    accent_col_idx = 0

    columns = [
        ("PRIORITY 01", "[Heading 1 — the load-bearing column]",
         "[Body content for column 1 — one to three sentences on what we "
         "achieve, the measurable target, and who owns delivery.]"),
        ("PRIORITY 02", "[Heading 2]",
         "[Body content for column 2 — parallel structure to column 1: "
         "what we achieve, target, owner.]"),
        ("PRIORITY 03", "[Heading 3]",
         "[Body content for column 3 — parallel structure: what we achieve, "
         "target, owner.]"),
    ]

    for i, (eyebrow, heading, body) in enumerate(columns):
        n = i + 1
        cx = body_left + i * (card_w + gap)

        # Card body — tinted CARD_BG fill, thin CARD_BORDER outline.
        card = add_rect(
            slide, f"card-{n}-bg",
            x_px=cx, y_px=card_top, w_px=card_w, h_px=card_h,
            fill_color=CARD_BG,
        )
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525  # 1px

        # ONE accent moment — 3px top-edge stripe on the load-bearing column.
        # Drawn AFTER the card so it paints over the top border edge.
        if i == accent_col_idx:
            add_rect(
                slide, f"card-{n}-accent-stripe",
                x_px=cx, y_px=card_top, w_px=card_w, h_px=3,
                fill_color=BRAND_ACCENT,
            )

        # Eyebrow — uppercase, letter-spaced, BRAND_PRIMARY, NOT bold.
        eyebrow_y = card_top + pad_top
        add_text(
            slide, f"card-{n}-eyebrow", eyebrow,
            x_px=cx + pad_x, y_px=eyebrow_y,
            w_px=card_w - pad_x * 2, h_px=16,
            font_size_px=11, color=BRAND_PRIMARY, bold=False,
            uppercase=True, letter_spacing_px=2, align="left",
        )

        # Column heading — 20px bold BRAND_PRIMARY. This is the dominant
        # typographic element of each card; with no icon to compete, the
        # heading can run a touch larger than the icon-variant's 18px.
        heading_y = eyebrow_y + 26
        add_text(
            slide, f"card-{n}-heading", heading,
            x_px=cx + pad_x, y_px=heading_y,
            w_px=card_w - pad_x * 2, h_px=64,
            font_size_px=20, color=BRAND_PRIMARY, bold=True, align="left",
        )

        # Body — 14px TEXT_DARK, NOT bold, left-aligned for editorial read.
        body_y = heading_y + 72
        add_text(
            slide, f"card-{n}-body", body,
            x_px=cx + pad_x, y_px=body_y,
            w_px=card_w - pad_x * 2, h_px=card_h - (body_y - card_top) - pad_top,
            font_size_px=14, color=TEXT_DARK, bold=False, align="left",
        )

    add_footer(slide, page_num=1)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
