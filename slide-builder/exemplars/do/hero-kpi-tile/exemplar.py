"""
Slide 2 — Option C: Hero number + supporting chart strip.

Layout family: Hero stat + supporting (visual-treatment-library.md
"Hero stat + supporting"). Distinct from A (split-panel) and B
(full-width chart).

Page-type: Hero number / Data-with-takeaway (page-types.md). The
$10.2M gap IS the slide; the chart strip below proves it.

Rules honored:
  - §1 Hard constraints: 1280×720; add_title_block; add_footer page_num=2;
    brand palette; body ≥14px.
  - §3a Chart-honoring: explicit "waterfall" → compact horizontal bar
    strip evidencing the three numbers ($68M / $55.8M / $66M commitment).
    Not a full waterfall but a structured comparison strip — the hero
    number is the headline, the chart is the evidence.
  - §6 Bold discipline: ≤5 bold. Title (1) + hero numeral (1) + supporting
    claim heading (1) + accent-bar value label (1). Eyebrows / body NOT
    bold (new designer-brief rule).
  - §1 One accent moment: BRAND_ACCENT on the single "post-change" bar in
    the strip — the load-bearing data point. Hero numeral uses
    BRAND_PRIMARY (not accent) per brief direction.
  - Title length 80 chars.
"""
from pathlib import Path
import sys

_SKILL = Path(__file__).resolve().parents[3]
if str(_SKILL) not in sys.path:
    sys.path.insert(0, str(_SKILL))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="[Hero-stat headline — name the metric and the takeaway in one line]",
        subtitle="[Sub-headline that frames why this number matters]",
    )

    # ===== Top half: HERO =====
    hero_top = 172
    hero_h = 260

    # Eyebrow
    add_text(
        slide, "hero-eyebrow", "[METRIC LABEL — UPPERCASE]",
        x_px=64, y_px=hero_top, w_px=1152, h_px=18,
        font_size_px=11, color=BRAND_PRIMARY, uppercase=True, letter_spacing_px=2,
    )

    # Hero numeral (96px BRAND_PRIMARY)
    add_text(
        slide, "hero-number", "$X.XM",
        x_px=64, y_px=hero_top + 28, w_px=560, h_px=132,
        font_size_px=96, color=BRAND_PRIMARY, bold=True,
    )

    # Small label under the hero numeral
    add_text(
        slide, "hero-label",
        "[Short context line under the hero numeral]",
        x_px=64, y_px=hero_top + 168, w_px=560, h_px=22,
        font_size_px=16, color=BRAND_PRIMARY, letter_spacing_px=1,
    )

    # Supporting claim — right of hero (18px TEXT_DARK)
    add_text(
        slide, "hero-claim",
        "[Supporting claim — two or three sentences explaining the hero number "
        "and what it implies. Use <strong>inline emphasis</strong> for the "
        "load-bearing values within the prose.]",
        x_px=664, y_px=hero_top + 36, w_px=552, h_px=200,
        font_size_px=18, color=TEXT_DARK, emphasis_color=BRAND_PRIMARY,
    )

    # ===== Bottom half: SUPPORTING CHART STRIP =====
    # Thin horizontal bar chart, height ~180px, three rows.
    strip_x = 64
    strip_w = 1152
    strip_top = 452
    strip_h = 148

    add_text(
        slide, "strip-eyebrow",
        "[CHART EYEBROW — WHAT THIS CHART SHOWS, UPPERCASE]",
        x_px=strip_x, y_px=strip_top, w_px=strip_w, h_px=16,
        font_size_px=11, color=TEXT_DARK, uppercase=True, letter_spacing_px=1,
    )

    # Bar plot region
    bars_left = strip_x + 220          # leave room for left-side labels
    bars_right = strip_x + strip_w - 80  # leave room for value labels at right
    bars_width = bars_right - bars_left
    bars_top = strip_top + 28
    row_h = 28
    row_gap = 12

    val_max = 80.0
    def bar_w_for(val):
        return int((val / val_max) * bars_width)

    rows = [
        # (label, value, color, value_label, is_accent)
        ("[Comparison row 1]", 68.0, TEXT_DARK, "[$XXM]", False),
        ("[Comparison row 2]", 66.0, BRAND_PRIMARY_MID, "[$XXM]", False),
        ("[Load-bearing row]", 55.8, BRAND_ACCENT, "[$XXM]", True),
    ]

    for i, (label, val, color, vlabel, is_accent) in enumerate(rows):
        ry = bars_top + i * (row_h + row_gap)
        # Left-side row label
        add_text(
            slide, f"row-{i}-lbl", label,
            x_px=strip_x, y_px=ry + 4, w_px=200, h_px=row_h,
            font_size_px=14, color=TEXT_DARK,
        )
        # Faint track behind bar
        add_rect(slide, f"row-{i}-track", bars_left, ry + row_h // 2 - 1,
                 bars_width, 2, CARD_BORDER)
        # Bar
        bw = bar_w_for(val)
        add_rect(slide, f"row-{i}-bar", bars_left, ry, bw, row_h, color)
        # Value label on the right of the bar
        add_text(
            slide, f"row-{i}-val", vlabel,
            x_px=bars_left + bw + 8, y_px=ry + 4, w_px=84, h_px=row_h,
            font_size_px=14,
            color=BRAND_ACCENT if is_accent else TEXT_DARK,
            bold=is_accent,
        )

    add_footer(slide, page_num=2)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "option_C.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
