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
        title="Why Existing Tools Don't Fix It",
        subtitle="Any tool is only as good as the thinking behind it — Slide Lab is the only one built to fix the thinking first.",
        brand_rule_w=56,
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

    # ---- PANEL 1: The training gap ----
    add_text(
        slide, "panel-1-label", "THE TRAINING GAP",
        x_px=left_x, y_px=panels_top, w_px=panel_w, h_px=18,
        font_size_px=11, color=TEXT_MID, uppercase=True,
        letter_spacing_px=1,
    )
    add_text(
        slide, "panel-1-heading",
        "Most consultants never learned the rigor.",
        x_px=left_x, y_px=panels_top + 30, w_px=panel_w, h_px=72,
        font_size_px=22, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "panel-1-body",
        "McKinsey built sharpening the argument into its training. "
        "Most firms don't — so even experienced people skip the "
        "sharpening step and go straight to the slide.\n\n"
        "Without that habit, the argument never gets stress-tested. "
        "Pages get made repeatedly without knowing the underlying message.",
        x_px=left_x, y_px=panels_top + 118, w_px=panel_w - 8, h_px=panel_h - 140,
        font_size_px=14, color=TEXT_MID,
    )

    # ---- PANEL 2: The GenAI gap ----
    add_text(
        slide, "panel-2-label", "THE GENAI GAP",
        x_px=right_x, y_px=panels_top, w_px=panel_w, h_px=18,
        font_size_px=11, color=TEXT_MID, uppercase=True,
        letter_spacing_px=1,
    )
    add_text(
        slide, "panel-2-heading",
        "Generic AI does what you say.",
        x_px=right_x, y_px=panels_top + 30, w_px=panel_w, h_px=72,
        font_size_px=22, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "panel-2-body",
        "It generates an answer — not yours. No pushback, no conflict "
        "detection, no standard to compare your thinking against.\n\n"
        "The tool will make the page regardless of whether the thinking "
        "is ready. You ship whatever you walked in with.",
        x_px=right_x, y_px=panels_top + 118, w_px=panel_w - 8, h_px=panel_h - 140,
        font_size_px=14, color=TEXT_MID,
    )

    # ---- Convergence band: the punchline (single BRAND_PRIMARY band) ----
    add_convergence(
        slide,
        "Subpar page, subpar message, manual fixes at the end — the tool "
        "isn't the problem, the unstructured input is.",
    )

    add_footer(slide, page_num=3)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "option_A.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
