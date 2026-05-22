"""
Hero numeral divider — light-canvas numbered section divider.

Page-type: Cover/Divider — numbered section divider. Distinct from
hero-kpi-tile (a BODY page-type that names a single metric + supporting
chart); this is a CHAPTER BREAK with no body content, no chart, no claim
prose. The numeral here is a wayfinding marker ("you are entering
section 02"), not a measured quantity.

Layout rationale (rulebook citations):
- visual-treatment-library.md § Cover/Divider — light variant: white canvas
  with two horizontal hairlines framing a single editorial composition.
  Numeral RIGHT, title LEFT, baseline-aligned. The cleaner light/right-
  numeral cousin of the dark/left-numeral divider.
- page-types.md § Cover/Divider: "60-96px is reserved for single-numeral
  hero slides." This file pushes to 128px because the numeral is the
  entire slide — no claim prose competes with it.
- slot-design-rules.md § Bold discipline: bold count = 2 (numeral + section
  title). Eyebrow is uppercase+letter-spaced, NOT bold. No footer, no body.
- slot-design-rules.md § One accent moment: a single 64px BRAND_ACCENT
  mark sits on the bottom hairline directly under the title — the lone
  chromatic event in an otherwise BRAND_PRIMARY / monochrome composition.
- Invariant zone rule: no footer / page number on a divider — dividers
  are wayfinding, not content. The bottom invariant zone stays empty.
- This builder bypasses add_title_block (the standard 28pt title helper)
  because the divider's "title" IS the section name at 36pt aligned to
  the hero numeral's baseline — not the top-of-slide deck title.
"""
from pathlib import Path
import sys

_SKILL = Path(__file__).resolve().parents[3]
if str(_SKILL) not in sys.path:
    sys.path.insert(0, str(_SKILL))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, CARD_BORDER,
)


def build():
    prs, slide = new_slide()

    # ===== Framing hairlines (1px CARD_BORDER, top + bottom) =====
    # Two horizontal rules frame the composition. The numeral + title sit
    # inside this band; the bottom rule carries the single accent mark.
    add_rect(
        slide, "divider-rule-top",
        x_px=64, y_px=140, w_px=1152, h_px=1,
        fill_color=CARD_BORDER,
    )
    add_rect(
        slide, "divider-rule-bottom",
        x_px=64, y_px=520, w_px=1152, h_px=1,
        fill_color=CARD_BORDER,
    )

    # ===== Eyebrow (top, above the upper hairline) =====
    # 11px BRAND_PRIMARY uppercase, letter-spaced, NOT bold.
    add_text(
        slide, "divider-eyebrow", "SECTION",
        x_px=64, y_px=112, w_px=600, h_px=18,
        font_size_px=11, color=BRAND_PRIMARY,
        bold=False, uppercase=True, letter_spacing_px=2,
    )

    # ===== Hero numeral (RIGHT, 128px BRAND_PRIMARY bold) =====
    # Right-aligned inside its box so the numeral's right edge lines up
    # with the right end of the framing hairlines (x=1216). Bottom-
    # anchored so the numeral's baseline lands just above the bottom
    # hairline (box bottom = 480, hairline at 520 → 40px of breathing
    # room between glyph baseline and rule).
    add_text(
        slide, "hero-numeral", "[02]",
        x_px=816, y_px=300, w_px=400, h_px=180,
        font_size_px=128, color=BRAND_PRIMARY, bold=True,
        align="right", anchor="bottom",
    )

    # ===== Section title (LEFT, 36px BRAND_PRIMARY bold) =====
    # Baseline-aligned with the numeral (same box bottom = 480, same
    # bottom anchor). The title and the numeral read as one composition,
    # not two stacked elements.
    add_text(
        slide, "section-title", "[Section name]",
        x_px=64, y_px=420, w_px=720, h_px=60,
        font_size_px=36, color=BRAND_PRIMARY, bold=True,
        anchor="bottom",
    )

    # ===== Accent moment — 64px BRAND_ACCENT mark on the bottom hairline =====
    # Sits directly under the title's left edge, overlapping the bottom
    # CARD_BORDER hairline. The only chromatic event on the slide.
    add_rect(
        slide, "divider-accent-mark",
        x_px=64, y_px=518, w_px=64, h_px=4,
        fill_color=BRAND_ACCENT,
    )

    # NOTE: no add_footer — divider slides do not carry page numbers,
    # sources, or footnotes (page-types.md § Cover/Divider).
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
