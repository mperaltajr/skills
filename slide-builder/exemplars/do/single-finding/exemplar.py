"""
Slide 4 — Option A: Hero takeaway + 3 supporting bullets.

Editorial emphasis: conclusion dominates ("thought partner, not slide machine")
as the visual anchor. The hero takeaway claim sits in the top half at 36px, with
three subordinate supporting bullets below — each prefixed by a small brand-
primary square. One accent moment = a 56px brand-accent rule under the hero
takeaway.

Layout family: hero-takeaway + bullets (single dominant claim, parallel
subordinate evidence). Distinct from B (parallel-rows) and C (pull-quote).

Rulebook citations:
- Title length cap (slot-design rules § 6): Governing thought is ~110 chars,
  so the title here is a shortened headline (~70 chars). The fuller claim
  lives in the subtitle / hero-claim slot — never as a 4-line title.
- Bold discipline (§ 6): hero claim is the dominant bold; bullets are NOT bold;
  eyebrow is NOT bold. Total bold runs ≤ 5: title (1) + hero-claim emphasis (1)
  + 3 small bullet-square fill rects (visual, not bold text). 2 bold text runs.
- One accent moment: the 56px BRAND_ACCENT rule under the hero takeaway. Bullet
  squares are BRAND_PRIMARY (not accent) so the rule is the sole accent.
- Body floor 14px (§ 1): bullets are 14px TEXT_MID.
- Footer = add_footer(slide, page_num=4). Invariant top/bottom zones clean.
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

    # Title ≤90 chars; the fuller claim lives in subtitle.
    add_title_block(
        slide,
        title="[Single-finding insight headline placeholder]",
        subtitle="[Sub-headline that frames the finding]",
    )

    # === Hero takeaway zone ===
    # Body zone runs y≈152 → y≈630. Hero occupies top ~60% (152 → 410).
    hero_x = 64
    hero_y = 168
    hero_w = int((1280 - 128) * 0.78)  # ~70% width per brief; allow a touch more

    add_text(
        slide, "hero-takeaway",
        "[Hero takeaway placeholder — one declarative sentence with "
        "<strong>inline emphasis</strong> on the load-bearing words.]",
        x_px=hero_x, y_px=hero_y, w_px=hero_w, h_px=120,
        font_size_px=36, color=TEXT_DARK, bold=True,
        emphasis_color=BRAND_PRIMARY,
    )

    # Single accent moment: 56px BRAND_ACCENT rule under the hero takeaway.
    add_rect(
        slide, "hero-accent-rule",
        x_px=hero_x, y_px=hero_y + 132, w_px=56, h_px=4,
        fill_color=BRAND_ACCENT,
    )

    # Hero supporting claim (the so-what restated, larger than bullets)
    add_text(
        slide, "hero-claim",
        "[Hero supporting claim — two sentences explaining the takeaway above. "
        "Larger than the bullets that follow, but smaller than the takeaway.]",
        x_px=hero_x, y_px=hero_y + 150, w_px=hero_w, h_px=80,
        font_size_px=16, color=TEXT_DARK,
    )

    # === 3 supporting bullets ===
    # Below hero: y=420 → y=620. Three rows, each 60px tall.
    bullets = [
        "[Supporting bullet 1 — one declarative sentence backing the takeaway.]",
        "[Supporting bullet 2 — one declarative sentence backing the takeaway.]",
        "[Supporting bullet 3 — one declarative sentence backing the takeaway.]",
    ]

    bullet_x = 64
    bullet_y0 = 432
    row_h = 54
    square_size = 12

    for i, text in enumerate(bullets):
        n = i + 1
        ry = bullet_y0 + i * row_h
        # BRAND_PRIMARY square marker (not BRAND_ACCENT — accent is the rule above)
        add_rect(
            slide, f"bullet-{n}-marker",
            x_px=bullet_x, y_px=ry + 6, w_px=square_size, h_px=square_size,
            fill_color=BRAND_PRIMARY,
        )
        # Bullet body — NEVER bold per new designer-brief rule.
        add_text(
            slide, f"bullet-{n}-body", text,
            x_px=bullet_x + square_size + 14, y_px=ry,
            w_px=1280 - 128 - square_size - 14, h_px=row_h,
            font_size_px=14, color=TEXT_MID,
        )

    add_footer(slide, page_num=4)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "option_A.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
