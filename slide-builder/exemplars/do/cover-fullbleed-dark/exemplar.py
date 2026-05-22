"""
Option A — Dark full-bleed minimal type.

Cover design rationale (rulebook citations):
- visual-treatment-library.md § Full-bleed dark: BRAND_PRIMARY fills the canvas;
  typography IS the visual on cover slides.
- page-types.md § Cover/Divider: "Hero title size cap: 36-48px for multi-word
  titles. 60-96px is reserved for single-numeral hero slides." This file caps
  the hero at 48px even though "Slide Lab" is only two words — keeping the deck
  editorial rather than chunky.
- slot-design-rules.md § Bold discipline: cover hero is the only bold title;
  eyebrow + tagline + body lines are NOT bold (uppercase + letter-spacing carry
  the eyebrow; italic carries the tagline). Total bold count = 1 (title only).
- slot-design-rules.md § Accent discipline: ONE accent moment — the 64px
  BRAND_ACCENT rule directly under the tagline. Everything else is BRAND_PRIMARY
  ground, WHITE type, or BRAND_ACCENT_SOFT (tagline + meta labels).
- Invariant zones: cover keeps the bottom invariant zone clean (no footer here —
  cover/divider page-type does not require page numbers; meta block sits ABOVE
  the invariant line at y=612).

Layout: full-bleed BRAND_PRIMARY fill. Eyebrow top-left. Hero title at ~48% of
canvas height (y≈345 bottom-anchor inside a 360y/100h box → text bottom at 460,
which is roughly canvas mid). Tagline immediately below in BRAND_ACCENT_SOFT
italic. A single 64px BRAND_ACCENT rule under the tagline = the lone accent.
Faint meta lines bottom-left.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)


def build():
    prs, slide = new_slide()

    # Full-bleed brand-primary fill
    add_rect(
        slide, "cover-bg",
        x_px=0, y_px=0, w_px=1280, h_px=720,
        fill_color=BRAND_PRIMARY,
    )

    # Eyebrow — top-left, NOT bold (uppercase + letter-spacing carry it)
    add_text(
        slide, "cover-eyebrow", "SLIDE LAB",
        x_px=72, y_px=80, w_px=600, h_px=18,
        font_size_px=11, color=BRAND_ACCENT_SOFT,
        bold=False, uppercase=True, letter_spacing_px=2,
    )

    # Hero title — bottom-anchored inside its 100h box; bottom of text at y≈340
    # (≈47% canvas height). 48px is the cap for multi-word cover titles per the
    # designer brief.
    add_text(
        slide, "cover-title", "[Deck title placeholder]",
        x_px=72, y_px=240, w_px=1136, h_px=100,
        font_size_px=48, color=WHITE, bold=True,
        anchor="bottom",
    )

    # Tagline — italic, BRAND_ACCENT_SOFT, directly below title. NOT bold.
    add_text(
        slide, "cover-tagline", "[Tagline placeholder — short, declarative]",
        x_px=72, y_px=356, w_px=900, h_px=36,
        font_size_pt=16, color=BRAND_ACCENT_SOFT, italic=True, bold=False,
    )

    # Single accent moment — 64px BRAND_ACCENT rule directly under the tagline
    add_rect(
        slide, "cover-accent-rule",
        x_px=72, y_px=406, w_px=64, h_px=4,
        fill_color=BRAND_ACCENT,
    )

    # Three optional sub-tagline definitions (genericized) — faint, NOT bold.
    # In production, these can be the deck's three main themes / sections.
    defs = [
        ("[Word 1]", "[One-line definition or sub-statement supporting the tagline.]"),
        ("[Word 2]", "[One-line definition or sub-statement supporting the tagline.]"),
        ("[Word 3]", "[One-line definition or sub-statement supporting the tagline.]"),
    ]
    row_y = 444
    row_h = 22
    for i, (word, body) in enumerate(defs):
        y = row_y + i * (row_h + 6)
        # Label — NOT bold; relies on color contrast against body text
        add_text(
            slide, f"cover-def-{i+1}-word", word,
            x_px=72, y_px=y, w_px=90, h_px=row_h,
            font_size_px=14, color=BRAND_ACCENT_SOFT, italic=True, bold=False,
        )
        # Body — never bold; ≥14px floor
        add_text(
            slide, f"cover-def-{i+1}-body", body,
            x_px=170, y_px=y, w_px=900, h_px=row_h,
            font_size_px=14, color=WHITE, bold=False,
        )

    # Presenter meta — bottom-left, faint, NOT bold (eyebrow style)
    add_text(
        slide, "cover-presenter-label", "PRESENTED BY",
        x_px=72, y_px=628, w_px=300, h_px=14,
        font_size_px=11, color=BRAND_ACCENT_SOFT,
        bold=False, uppercase=True, letter_spacing_px=2,
    )
    add_text(
        slide, "cover-presenter-name", "Mario Peralta",
        x_px=72, y_px=646, w_px=400, h_px=20,
        font_size_px=14, color=WHITE, bold=False,
    )

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "option_A.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
