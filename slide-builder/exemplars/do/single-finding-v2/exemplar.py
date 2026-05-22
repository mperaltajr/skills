"""
single-finding-v2 — Hero METRIC variant (quantitative hero-stat / big-number).

This is structurally distinct from the existing `single-finding` exemplar
(which is a qualitative hero-takeaway CLAIM + 3 supporting bullets). The
skeleton's page_types are "finding | hero-stat | big-number | insight |
key-metric" — i.e. the slide IS one massive number, and a one-sentence
supporting line restates what the number means.

Editorial emphasis: a single quantitative finding dominates. The metric is the
visual anchor; everything else is subordinate scaffolding.

Layout family: hero-stat (single dominant number, one supporting sentence).
Distinct from single-finding (hero takeaway + parallel bullets) and from
two-column-comparison (paired metrics).

Rulebook citations:
- Bold discipline (slot-design § 6): the hero metric is the ONE dominant
  visual; title is bold (1); metric is bold (1); supporting line is NOT bold;
  section label is NOT bold. Total bold runs = 2.
- One accent moment: the metric itself is rendered in BRAND_ACCENT (the
  ONLY accent on the slide). The section label, supporting line, and footer
  are all TEXT_DARK. No accent rule, no accent square — just the number.
- Title length cap: short headline framing what the metric measures.
- Body floor 14px: supporting line is 18px (well above the floor; it's the
  hero's lieutenant, not body copy).
- Footer = add_footer; invariant zones clean.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_title_block, add_footer,
    BRAND_ACCENT, TEXT_DARK,
)


def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="One number captures the shift.",
        subtitle="The finding that reframes the conversation.",
    )

    # === Section label (small, uppercase, tracked) ===
    # Sits above the hero metric, anchors the metric in a category.
    add_text(
        slide, "section-label",
        "KEY FINDING",
        x_px=64, y_px=192, w_px=1152, h_px=24,
        font_size_px=14, color=TEXT_DARK,
        uppercase=True, letter_spacing_px=2,
    )

    # === Hero metric — THE finding ===
    # Massive number, brand-accent, top-aligned. This is the slide.
    # Sized at 180pt — big enough to dominate the canvas without crowding the
    # supporting line below.
    add_text(
        slide, "hero-metric",
        "73%",
        x_px=64, y_px=220, w_px=1152, h_px=260,
        font_size_pt=180, color=BRAND_ACCENT, bold=True,
        anchor="top",
    )

    # === Supporting line — one sentence, why the number matters ===
    # 18px, TEXT_DARK, NOT bold. Sits below the metric with breathing room.
    # ~70% width so it reads as a statement, not a paragraph.
    add_text(
        slide, "supporting-line",
        "of executives say their teams ship slides faster than they sharpen the "
        "argument behind them — the gap Slide Lab closes.",
        x_px=64, y_px=508, w_px=int(1152 * 0.78), h_px=80,
        font_size_px=18, color=TEXT_DARK,
    )

    add_footer(slide, page_num=1)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
