"""
Anti-exemplar / title-narrower-than-accent-bar — accent bar dominates title.

Family: any (chrome-level failure — can occur on any page type)
Verdict: dont

The failure (deliberate):
- The title text is short ("[Short title]") and its rendered width is far
  narrower than the full-bleed BRAND_ACCENT bar drawn directly beneath it.
- The accent bar spans the entire body content area (1152px wide), so it
  visually outweighs the title. The eye lands on the bar first; the title
  reads as a small footnote sitting on top of an accent block.
- Visual hierarchy is inverted: an ornament out-shouts the primary text.

What this teaches:
- Agents who replace the small default accent rule (≤64px) with a custom
  full-width band — without checking the title's rendered width — produce
  this inversion. If you want a wider accent moment, put it somewhere other
  than directly beneath a short title (e.g., a card border, a column
  stripe, a recommendation band at the bottom of the slide).
- Rule: any accent bar/rule placed underneath a title must be ≤ the title
  text's visual width. The title must dominate.

Layout shape (intentionally broken):
- Title block at top (y≈20–100), short title — narrow rendered width.
- BRAND_ACCENT bar at y=140, x=64, w=1152, h=6 — FULL BODY WIDTH.
- Placeholder body content below.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID,
)


def build():
    prs, slide = new_slide()

    # Title block — deliberately SHORT title so the accent bar below
    # visibly overhangs the title text on both sides.
    add_title_block(
        slide,
        title="[Short title]",
        subtitle="[Sub-headline placeholder line for context]",
    )

    # === THE FAILURE ===
    # Full-width BRAND_ACCENT bar directly under the title block.
    # 1152px wide × 6px tall. Far wider than the title text it sits beneath.
    # This is exactly the inversion: the ornament becomes the primary element.
    add_rect(
        slide, "accent-bar-too-wide",
        x_px=64, y_px=140, w_px=1152, h_px=6,
        fill_color=BRAND_ACCENT,
    )

    # === Placeholder body content (so the slide isn't empty) ===
    # Three generic placeholder rows so the failure is the title/bar
    # relationship, not body emptiness.
    body_x = 64
    body_y0 = 200
    row_h = 64
    marker_size = 10

    placeholder_rows = [
        "[Placeholder body line one — supporting point]",
        "[Placeholder body line two — supporting point]",
        "[Placeholder body line three — supporting point]",
    ]

    for i, text in enumerate(placeholder_rows):
        n = i + 1
        ry = body_y0 + i * row_h
        add_rect(
            slide, f"body-{n}-marker",
            x_px=body_x, y_px=ry + 8, w_px=marker_size, h_px=marker_size,
            fill_color=BRAND_PRIMARY,
        )
        add_text(
            slide, f"body-{n}-text", text,
            x_px=body_x + marker_size + 14, y_px=ry,
            w_px=1280 - 128 - marker_size - 14, h_px=row_h,
            font_size_px=16, color=TEXT_DARK,
        )

    # Placeholder so-what line at bottom of body zone
    add_text(
        slide, "body-sowhat",
        "[Placeholder so-what restatement of the takeaway]",
        x_px=body_x, y_px=520, w_px=1152, h_px=40,
        font_size_px=14, color=TEXT_MID, italic=True,
    )

    add_footer(slide, page_num=1)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
