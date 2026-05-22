"""
Cover - full-bleed dark with bottom footer band (third cover variant).

Distinct signature vs the other two covers in do/:
- cover-fullbleed-dark: full-bleed dark, eyebrow top, hero MID-canvas, accent rule
  under tagline, three definition rows, presenter line. Editorial / content-rich.
- dark-hero-foil: 35/65 asymmetric dark left + white right. Cover that ALSO has
  to list scope/audience/date as a 3-col meta block. Contrast IS the visual.
- THIS variant (cover-band-footer): full-bleed dark, NO eyebrow, NO definition
  rows, hero title sits LOWER (~60% canvas height), subtitle + byline stack
  directly under it, and a distinct DARK FOOTER STRIP runs across the bottom
  carrying ONLY source / footnote (invariant zone - no branding tags). Quiet,
  conventional client-deliverable cover.

Why a third variant earns its keep:
- Some decks need the cover to be a NAMEPLATE, not an editorial spread. No
  supporting rows, no scope columns - just title, line, byline. The footer
  strip gives the eye a stable base and reserves the invariant zone for
  source/footnote without intruding on the title's silence.

Rulebook citations:
- visual-treatment-library.md Full-bleed dark: BRAND_PRIMARY paints the
  canvas; typography is the visual.
- page-types.md Cover/Divider: 36-48px for multi-word titles; 60-96px reserved
  for single-numeral hero. 44px is the sweet spot for a 4-7 word client title.
- slot-design-rules.md Bold discipline: bold count = 1 (title only).
- slot-design-rules.md Accent discipline: ONE accent moment - a 64px
  BRAND_ACCENT rule under the title, sitting on the dark ground where it pops.
- Invariant zone rule: footer band carries ONLY source / footnote -
  no ACCENTURE / DRAFT / CONFIDENTIAL tags.
- COVER bypass: title uses direct add_text at hero scale, NOT add_title_block.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)


def build():
    prs, slide = new_slide()

    # --- Full-bleed BRAND_PRIMARY canvas ---
    add_rect(
        slide, "cover-bg",
        x_px=0, y_px=0, w_px=1280, h_px=720,
        fill_color=BRAND_PRIMARY,
    )

    # --- Dark footer band - slightly lifted tone for separation ---
    # Runs full canvas width, ~48px tall, sits at the very bottom (invariant
    # zone). Carries ONLY source/footnote - no branding tags, no page number
    # (cover/divider doesn't require one).
    band_top = 672
    band_h = 48
    add_rect(
        slide, "cover-footer-band",
        x_px=0, y_px=band_top, w_px=1280, h_px=band_h,
        fill_color=BRAND_PRIMARY_MID,
    )

    # --- Hero title - bottom-anchored, sits ~60% down the canvas ---
    # 44px bold WHITE. Sits LOWER than cover-fullbleed-dark's mid-canvas hero,
    # because subtitle + byline stack BELOW it (not definition rows).
    add_text(
        slide, "cover-title", "[Presentation Title]",
        x_px=72, y_px=300, w_px=1136, h_px=120,
        font_size_px=44, color=WHITE, bold=True,
        anchor="bottom",
    )

    # --- Single accent moment - 64px BRAND_ACCENT rule under the title ---
    add_rect(
        slide, "cover-accent-rule",
        x_px=72, y_px=438, w_px=64, h_px=4,
        fill_color=BRAND_ACCENT,
    )

    # --- Subtitle / context line - BRAND_ACCENT_SOFT, NOT bold ---
    add_text(
        slide, "cover-subtitle", "[Subtitle / Context Line]",
        x_px=72, y_px=458, w_px=1136, h_px=30,
        font_size_px=18, color=BRAND_ACCENT_SOFT, bold=False,
    )

    # --- Byline: client + date - single line, WHITE, NOT bold ---
    add_text(
        slide, "cover-byline", "[Client Name]   .   [Date]",
        x_px=72, y_px=498, w_px=1136, h_px=22,
        font_size_px=14, color=WHITE, bold=False, letter_spacing_px=1,
    )

    # --- Footer band content: footnote + source (invariant zone) ---
    # NO branding tags. NO page number (cover bypass). Just sources/notes.
    add_text(
        slide, "footer-footnote", "[1. Insert Footnote]",
        x_px=72, y_px=684, w_px=600, h_px=14,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=False,
    )
    add_text(
        slide, "footer-source", "[Source: Insert Source]",
        x_px=72, y_px=700, w_px=900, h_px=14,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=False,
    )

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
