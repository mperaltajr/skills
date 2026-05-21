"""
Option C — Asymmetric split: brand block left + content right (cover).

Rulebook citations:
- DESIGNER BRIEF § 5 Visual treatments — Two-column with insight panel (variant
  applied as cover): left 35% BRAND_PRIMARY block carries the title; right 65%
  white panel carries supporting definitions and the meta block. The contrast
  IS the cover's visual interest.
- DESIGNER BRIEF § 4 Page types — Cover/Divider: hero title cap 36-48px for
  multi-word titles. Hero here is 40px to fit the narrower left block.
- DESIGNER BRIEF § 1 — Brand palette only; one accent moment per slide. The
  single 64px BRAND_ACCENT rule sits at the seam between the brand block and
  the white panel (under the tagline, inside the dark block).
- DESIGNER BRIEF § 6 — Bold discipline: ≤5 bold elements. Bold runs here:
  (1) hero title, (2-4) the three sub-headings. Eyebrow, tagline, body, and
  meta values are NOT bold.
- DESIGNER BRIEF § 6 — Eyebrow / label NEVER bold.
- DESIGNER BRIEF § 2 — No personal email; no DRAFT/CONFIDENTIAL.
- Side panel runs full canvas height (720px) per § 6 slot rules.
- Title length: 36 chars, well under 90.

Layout: left 448px (35%) BRAND_PRIMARY block running full canvas height. White
title at 40px (≤48). Tagline below in BRAND_ACCENT_SOFT italic. 64px
BRAND_ACCENT accent rule under the tagline (the single accent). Right 832px
(65%) white panel with three stacked definition rows. Meta block at bottom of
right panel.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT,
    WHITE,
)


def build():
    prs, slide = new_slide()

    # --- Left block (35% × full canvas height) ---
    left_w = 448
    add_rect(slide, "left-block-bg",
             x_px=0, y_px=0, w_px=left_w, h_px=720,
             fill_color=BRAND_PRIMARY)

    # Left-block eyebrow — NOT bold.
    add_text(
        slide, "left-eyebrow", "REDESIGN BC  /  DIAGNOSTIC",
        x_px=40, y_px=72, w_px=left_w - 80, h_px=18,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=False, uppercase=True,
        letter_spacing_px=2,
    )

    # Hero title — 40px, white, bold. Bottom-anchored within a tall box.
    add_text(
        slide, "left-title", "The mix moved the wrong way",
        x_px=40, y_px=180, w_px=left_w - 80, h_px=180,
        font_size_px=40, color=WHITE, bold=True,
        anchor="bottom",
    )

    # Tagline — italic, BRAND_ACCENT_SOFT, NOT bold.
    add_text(
        slide, "left-tagline",
        "−87 FTEs, +$12.2M cost — the issue isn't headcount.",
        x_px=40, y_px=372, w_px=left_w - 80, h_px=70,
        font_size_px=18, color=BRAND_ACCENT_SOFT, italic=True, bold=False,
    )

    # Single accent moment — 64px BRAND_ACCENT rule inside the dark block,
    # under the tagline.
    add_rect(
        slide, "cover-accent-rule",
        x_px=40, y_px=460, w_px=64, h_px=4,
        fill_color=BRAND_ACCENT,
    )

    # Left-block footnote-style supporting line — NOT bold.
    add_text(
        slide, "left-support",
        "A two-scenario read of the redesign's outcome on FTE and cost.",
        x_px=40, y_px=480, w_px=left_w - 80, h_px=60,
        font_size_px=14, color=BRAND_ACCENT_SOFT, bold=False,
    )

    # --- Right white panel content ---
    right_x = left_w + 56  # 56px gutter inside the right panel
    right_w = 1280 - right_x - 56

    # Eyebrow on right side — NOT bold.
    add_text(
        slide, "right-eyebrow", "WHAT THIS DECK COVERS",
        x_px=right_x, y_px=80, w_px=right_w, h_px=18,
        font_size_px=11, color=TEXT_MID, bold=False, uppercase=True,
        letter_spacing_px=2,
    )

    # Three stacked definition rows. Sub-heading is bold; body is not.
    rows = [
        ("Two-scenario read",
         "Fact base vs. future state, side by side."),
        ("Headcount vs. cost",
         "−87 FTEs is real; +$12.2M is the cost story."),
        ("Mix shift",
         "Work moved from low-cost GCC to HQ/Local."),
    ]
    base_y = 130
    row_h = 84
    for i, (head, body) in enumerate(rows):
        y = base_y + i * row_h
        # Small numeric label — NOT bold; uppercase + spacing do the work.
        add_text(
            slide, f"def-{i+1}-num", f"0{i+1}",
            x_px=right_x, y_px=y, w_px=44, h_px=24,
            font_size_px=14, color=TEXT_FAINT, bold=False,
            letter_spacing_px=1,
        )
        # Sub-heading — bold; counts against the 5-bold ceiling.
        add_text(
            slide, f"def-{i+1}-head", head,
            x_px=right_x + 52, y_px=y - 2, w_px=right_w - 52, h_px=26,
            font_size_px=20, color=TEXT_DARK, bold=True,
        )
        # Body — NOT bold.
        add_text(
            slide, f"def-{i+1}-body", body,
            x_px=right_x + 52, y_px=y + 28, w_px=right_w - 52, h_px=40,
            font_size_px=14, color=TEXT_MID, bold=False,
        )

    # Meta block at the bottom of the right panel — NOT bold.
    meta_y = 612
    cols = [
        ("PREPARED BY", "Redesign Working Team"),
        ("FOR", "Steering Committee"),
        ("DATE", "May 2026"),
    ]
    col_w = (right_w - 32) // 3
    for i, (label, value) in enumerate(cols):
        x = right_x + i * (col_w + 16)
        add_text(
            slide, f"right-meta-{i+1}-label", label,
            x_px=x, y_px=meta_y, w_px=col_w, h_px=14,
            font_size_px=10, color=TEXT_FAINT, bold=False, uppercase=True,
            letter_spacing_px=1,
        )
        add_text(
            slide, f"right-meta-{i+1}-value", value,
            x_px=x, y_px=meta_y + 18, w_px=col_w, h_px=20,
            font_size_px=14, color=TEXT_DARK, bold=False,
        )

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "option_C.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
