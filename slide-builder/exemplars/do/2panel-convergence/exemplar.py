"""
Slide 3 — Option A: Symmetric 2-column with vertical divider.

Layout family: split-panel (Comparison page-type, page-types.md §4).
Editorial emphasis (brief): contrast dominates — two failure modes (training
gap / GenAI gap) converging on the same root cause. Brief is symmetric, so
both panels carry equal visual weight. Neutral chrome on both sides.

Rules honored:
- Designer Brief §1: title bottom-anchored at y≈100 via add_title_block.
- Designer Brief §1: brand palette only — no raw hex literals.
- Designer Brief §1: one accent moment — the convergence band (BRAND_PRIMARY
  band, brand-rule under title uses BRAND_ACCENT exactly once — same accent
  hits one element, the brand-rule, per the helper's default; the band stays
  BRAND_PRIMARY to keep the rule as the only ACCENT-coloured shape).
- Designer Brief §6 bold discipline: title (1) + 2 panel headings (2) = 3
  bold runs. Eyebrows + body never bold. Hard ceiling of 5 respected.
- Designer Brief §6 title length cap: brief's slide title is 30 chars
  (≤90), passed verbatim.
- Designer Brief §1: body floor 14px. Eyebrows 11px (label slot).
- Designer Brief §1: 1280×720 canvas; new_slide() handles this.
- Designer Brief §2: no personal contact info, no DRAFT/CONFIDENTIAL.
- Memory: title bottom-anchor + invariant-zone-chrome rules honored.
"""
from pathlib import Path
import sys

# slide-builder is the package root for twins.helpers
_SKILL = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_SKILL))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID,
    CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="[Two-panel comparison headline — name the contrast the panels deliver]",
        subtitle="[Sub-headline that sets up what the two panels are comparing]",
    )

    # ---- Two-panel symmetric grid with central vertical divider ----
    panels_top = 180
    panel_h = 412
    gutter = 32
    panel_w = (1280 - 128 - gutter) // 2
    left_x = 64
    right_x = left_x + panel_w + gutter

    # Vertical divider — 2px CARD_BORDER, centered in the gutter
    divider_x = left_x + panel_w + (gutter // 2) - 1
    add_rect(
        slide, "divider",
        x_px=divider_x, y_px=panels_top + 24, w_px=2, h_px=panel_h - 48,
        fill_color=CARD_BORDER,
    )

    # ---- PANEL 1 ----
    add_text(
        slide, "panel-1-label", "[PANEL 1 LABEL]",
        x_px=left_x, y_px=panels_top, w_px=panel_w, h_px=18,
        font_size_px=11, color=TEXT_DARK, uppercase=True,
        letter_spacing_px=1,
    )
    add_text(
        slide, "panel-1-heading",
        "[Panel 1 heading — one declarative sentence.]",
        x_px=left_x, y_px=panels_top + 30, w_px=panel_w, h_px=72,
        font_size_pt=20, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "panel-1-body",
        "[Panel 1 body — two or three sentences supporting the panel heading. "
        "Keep parallel structure with Panel 2 so the eye reads them as a "
        "comparison.]\n\n[Second paragraph if needed.]",
        x_px=left_x, y_px=panels_top + 118, w_px=panel_w - 8, h_px=panel_h - 140,
        font_size_px=14, color=TEXT_DARK,
    )

    # ---- PANEL 2 ----
    add_text(
        slide, "panel-2-label", "[PANEL 2 LABEL]",
        x_px=right_x, y_px=panels_top, w_px=panel_w, h_px=18,
        font_size_px=11, color=TEXT_DARK, uppercase=True,
        letter_spacing_px=1,
    )
    add_text(
        slide, "panel-2-heading",
        "[Panel 2 heading — declarative, parallel to Panel 1.]",
        x_px=right_x, y_px=panels_top + 30, w_px=panel_w, h_px=72,
        font_size_pt=20, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "panel-2-body",
        "[Panel 2 body — two or three sentences. Parallel structure with "
        "Panel 1 — same sentence shape, same number of clauses, same length.]"
        "\n\n[Second paragraph if needed.]",
        x_px=right_x, y_px=panels_top + 118, w_px=panel_w - 8, h_px=panel_h - 140,
        font_size_px=14, color=TEXT_DARK,
    )

    # ---- Convergence band: the punchline (single BRAND_PRIMARY band) ----
    add_convergence(
        slide,
        "[Convergence punchline — the so-what that ties Panel 1 and Panel 2 "
        "together. White italic on BRAND_PRIMARY band.]",
    )

    add_footer(slide, page_num=3)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "option_A.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
