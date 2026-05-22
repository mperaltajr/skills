"""
midpoint-accent-splits-slide — ANTI-EXEMPLAR.

Family: any (chrome-level failure — page-type independent)
Variant: a hero takeaway + 3 supporting cards layout, sabotaged by a full-width
         accent bar planted at the body-area midpoint.

The failure:
- A full-width (1152px) BRAND_ACCENT rectangle sits at y≈336, roughly halfway
  between the title block (top, y≈20–134) and the bottom of the body content.
- That bar acts as a visual page break. The eye reads the slide as TWO STACKED
  HALF-PAGES:
    Upper half = title + subtitle + hero takeaway → looks like its own slide
                 with a chunky bottom rule.
    Lower half = three supporting cards → looks like a separate slide whose
                 page header is the accent bar.
- One coherent slide is destroyed into two competing pages.

What "correct" placement of an accent bar looks like (NOT this file):
- Directly under the title block (≤ y=140), tied visually to the title — the
  accent reads as title-block underline.
- On a load-bearing body element: left edge of a card, top stripe of a column,
  cap above a chart row. The accent is ATTACHED to content, not floating in
  empty space.
- Body-area midpoint (y≈300–400) is FORBIDDEN for a full-width accent — that's
  exactly where it splits the slide.

Rule violated:
- slot-design-rules.md § Accent discipline: one accent moment, and it must
  ATTACH to a load-bearing element (title block or specific body element). A
  full-width accent floating in body whitespace creates a false page break.
- visual-treatment-library.md § Dividers: full-width horizontal rules are
  reserved for between-section dividers in dense decks — never inside a single
  body composition.

Why this is a teaching anti-exemplar:
- Agents sometimes add their own "decorative" bars to fill perceived empty
  space without considering placement. The result is a slide that LOOKS
  designed at first glance but reads as two slides stacked once a viewer
  spends more than a second on it.
- The fix is not "remove decoration" — it's "attach the accent to something".

ALL CONTENT IS PLACEHOLDER. Do not lift copy from this file.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID,
    CARD_BG,
)


def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="[Title placeholder: the one-sentence governing thought]",
        subtitle="[Sub-headline placeholder: the qualifying context, period, or scope]",
    )

    # ── Hero takeaway zone (upper body) ──
    # In a well-designed slide this would flow naturally into the cards below.
    # Here it gets cut off from them by the offending midpoint bar.
    add_text(
        slide, "hero-takeaway",
        "[Hero takeaway placeholder: a bold one-line restatement of the so-what]",
        x_px=64, y_px=168, w_px=1152, h_px=80,
        font_size_px=28, color=TEXT_DARK, bold=True,
    )

    add_text(
        slide, "hero-claim",
        "[Supporting line placeholder: one or two sentences expanding the hero "
        "takeaway with the qualifying detail the audience needs to internalize "
        "before reading the supporting cards below.]",
        x_px=64, y_px=252, w_px=1152, h_px=60,
        font_size_px=14, color=TEXT_MID,
    )

    # ── THE FAILURE ──
    # Full-width BRAND_ACCENT bar at the body-area midpoint. 1152px wide × 6px
    # tall, sitting at y=336 — roughly halfway between the title block bottom
    # (y≈134) and the bottom of the body content (y≈560). This bar is not
    # attached to ANYTHING. It floats in whitespace and visually severs the
    # slide into an upper "page" and a lower "page".
    add_rect(
        slide, "midpoint-splitter-bar",
        x_px=64, y_px=336, w_px=1152, h_px=6,
        fill_color=BRAND_ACCENT,
    )

    # ── Three supporting cards (lower body) ──
    # These should read as the body of ONE slide. Because of the bar above,
    # they instead read as the entire content of a SECOND slide.
    card_y = 376
    card_h = 168
    card_w = 368
    gap = 24
    card_x0 = 64

    cards = [
        ("[Card label A]", "[Card body placeholder A: one-sentence description of the first supporting point underneath the hero takeaway.]"),
        ("[Card label B]", "[Card body placeholder B: one-sentence description of the second supporting point underneath the hero takeaway.]"),
        ("[Card label C]", "[Card body placeholder C: one-sentence description of the third supporting point underneath the hero takeaway.]"),
    ]

    for i, (label, body) in enumerate(cards):
        n = i + 1
        cx = card_x0 + i * (card_w + gap)

        # Card background
        add_rect(
            slide, f"card-{n}-bg",
            x_px=cx, y_px=card_y, w_px=card_w, h_px=card_h,
            fill_color=CARD_BG,
        )

        # Card label
        add_text(
            slide, f"card-{n}-label", label,
            x_px=cx + 20, y_px=card_y + 20, w_px=card_w - 40, h_px=28,
            font_size_px=16, color=BRAND_PRIMARY, bold=True,
        )

        # Card body
        add_text(
            slide, f"card-{n}-body", body,
            x_px=cx + 20, y_px=card_y + 56, w_px=card_w - 40, h_px=card_h - 76,
            font_size_px=14, color=TEXT_MID,
        )

    add_footer(slide, page_num=4)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
