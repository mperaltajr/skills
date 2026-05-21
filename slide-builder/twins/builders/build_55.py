"""
Builder for pattern 55: Delay sensitivity — burn scale.

Left: dark hero burn-rate card ($1.2M/wk) with derivation strip at bottom.
Right: panel head + 8-row burn scale (+1wk..+8wk) with colored bars + $ values
+ horizontal scale axis + threshold callout.

Source HTML: _pattern-library/55_delay-sensitivity-burn-scale.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

# Heat ramp
BURN_1 = RGBColor(0xFE, 0xE4, 0xE2)
BURN_2 = RGBColor(0xFD, 0xA2, 0x9B)
BURN_3 = RGBColor(0xF0, 0x44, 0x38)
BURN_4 = RGBColor(0xB4, 0x23, 0x18)
BURN_5 = RGBColor(0x7A, 0x27, 0x1A)
BAD_BG = RGBColor(0xFE, 0xF3, 0xF2)
BAD_INK = RGBColor(0xB4, 0x23, 0x18)
WHITE_70 = RGBColor(0xCB, 0xC1, 0xD9)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # --- Title block ---
    add_text(
        slide, "title",
        "Every week of delay costs <strong>$1.2M</strong> — the cost compounds linearly.",
        x_px=56, y_px=50, w_px=1168, h_px=44,
        font_size_px=26, color=TEXT_DARK, bold=True,
        emphasis_color=BRAND_PRIMARY,
    )
    add_text(
        slide, "subtitle",
        "Sensitivity of foregone savings to exit-window slip. Read the scale; pick a tolerance.",
        x_px=56, y_px=100, w_px=1168, h_px=22,
        font_size_px=14, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=56, y_px=140, w_px=56, h_px=3, fill_color=BRAND_ACCENT)

    # --- Body grid ---
    body_top = 196
    body_bottom = 640
    body_h = body_bottom - body_top
    gap = 24
    left_w = 540
    right_x = 56 + left_w + gap
    right_w = 1280 - 56 - right_x

    # === LEFT: Hero burn card ===
    add_rect(slide, "hero-burn-bg", 56, body_top, left_w, body_h, BRAND_PRIMARY)
    add_rect(slide, "hero-burn-accent", 56, body_top, 5, body_h, BRAND_ACCENT)

    add_text(
        slide, "hero-eyebrow", "Burn rate — per week of delay",
        x_px=88, y_px=body_top + 28, w_px=left_w - 64, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        letter_spacing_px=1.8, uppercase=True,
    )
    add_text(
        slide, "hero-value", "$1.2M",
        x_px=88, y_px=body_top + 56, w_px=left_w - 64, h_px=100,
        font_size_px=72, color=WHITE, bold=True,
    )
    add_text(
        slide, "hero-unit", "per week of slipped exit",
        x_px=88, y_px=body_top + 158, w_px=left_w - 64, h_px=22,
        font_size_px=20, color=BRAND_ACCENT_SOFT, bold=True,
    )

    # Divider
    add_rect(slide, "hero-divider-1", 88, body_top + 200, left_w - 64, 1, WHITE_70)
    add_text(
        slide, "hero-claim",
        "Foregone savings accrue <strong>linearly</strong> from the planned exit date. There is no “free” week — every Friday past the baseline burns the same $1.2M.",
        x_px=88, y_px=body_top + 214, w_px=left_w - 64, h_px=80,
        font_size_px=12, color=WHITE,
        emphasis_color=WHITE,
    )

    # Derivation strip
    deriv_y = body_top + body_h - 96
    add_rect(slide, "hero-divider-2", 88, deriv_y, left_w - 64, 1, WHITE_70)
    deriv_items = [
        ("Headcount", "~530 FTE", "across all exits"),
        ("Fully-loaded", "~$118K/FTE/yr", "blended rate"),
        ("Implied", "$1.2M / wk", "linear at this scale"),
    ]
    col_w = (left_w - 64) // 3
    for i, (label, value, note) in enumerate(deriv_items):
        n = i + 1
        dx = 88 + i * col_w
        add_text(
            slide, f"deriv-{n}-label", label,
            x_px=dx, y_px=deriv_y + 14, w_px=col_w - 12, h_px=12,
            font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True,
            letter_spacing_px=1.4, uppercase=True,
        )
        add_text(
            slide, f"deriv-{n}-value", value,
            x_px=dx, y_px=deriv_y + 30, w_px=col_w - 12, h_px=20,
            font_size_px=14, color=WHITE, bold=True,
        )
        add_text(
            slide, f"deriv-{n}-note", note,
            x_px=dx, y_px=deriv_y + 52, w_px=col_w - 12, h_px=14,
            font_size_px=10, color=WHITE_70,
        )

    # === RIGHT: Burn scale ===
    # Panel head
    add_text(
        slide, "panel-title", "Cumulative cost by weeks of delay",
        x_px=right_x, y_px=body_top, w_px=right_w, h_px=18,
        font_size_px=12, color=BRAND_PRIMARY, bold=True,
        letter_spacing_px=1.2, uppercase=True,
    )
    add_text(
        slide, "panel-sub",
        "Each row adds one week past the planned exit. Bar length and color scale with the dollar impact.",
        x_px=right_x, y_px=body_top + 20, w_px=right_w, h_px=28,
        font_size_px=11, color=TEXT_MID, italic=True,
    )

    # Burn scale table
    scale_top = body_top + 60
    scale_bottom = body_top + body_h - 80
    scale_h = scale_bottom - scale_top
    label_w = 64
    bar_x = right_x + label_w + 4
    bar_zone_w = right_w - label_w - 4
    rows = [
        ("+1 wk", 0.12, "$1.2M", BURN_1),
        ("+2 wk", 0.24, "$2.4M", BURN_1),
        ("+3 wk", 0.36, "$3.6M", BURN_2),
        ("+4 wk", 0.48, "$4.8M", BURN_2),
        ("+5 wk", 0.60, "$6.0M", BURN_3),
        ("+6 wk", 0.72, "$7.2M", BURN_3),
        ("+7 wk", 0.84, "$8.4M", BURN_4),
        ("+8 wk", 0.96, "$9.6M", BURN_5),
    ]
    row_h = scale_h // len(rows)

    # Outer frame
    frame = add_rect(slide, "burn-scale-frame", right_x, scale_top, right_w, scale_h, WHITE)
    frame.line.color.rgb = CARD_BORDER
    frame.line.width = 9525

    for i, (lbl, pct, val, color) in enumerate(rows):
        n = i + 1
        ry = scale_top + i * row_h
        # Top divider
        if i > 0:
            add_rect(slide, f"burn-row-{n}-rule", right_x, ry, right_w, 1, CARD_BORDER)
        # Label cell bg
        add_rect(slide, f"burn-row-{n}-lbl-bg", right_x, ry, label_w, row_h, CARD_BG)
        add_rect(slide, f"burn-row-{n}-lbl-rule", right_x + label_w, ry, 1, row_h, CARD_BORDER)
        add_text(
            slide, f"burn-row-{n}-lbl", lbl,
            x_px=right_x + 6, y_px=ry, w_px=label_w - 12, h_px=row_h,
            font_size_px=11, color=BRAND_PRIMARY, bold=True,
            align="right", anchor="middle",
        )
        # Bar
        bar_w_px = int(bar_zone_w * pct * 0.85)
        bar_h = 12
        add_rect(
            slide, f"burn-row-{n}-bar",
            bar_x + 4, ry + (row_h - bar_h) // 2, bar_w_px, bar_h, color,
        )
        # Value
        add_text(
            slide, f"burn-row-{n}-val", val,
            x_px=bar_x + bar_w_px + 12, y_px=ry, w_px=80, h_px=row_h,
            font_size_px=11, color=TEXT_DARK, bold=True, anchor="middle",
        )

    # Scale axis
    axis_y = scale_bottom + 4
    axis_labels = ["$0", "$2.5M", "$5.0M", "$7.5M", "$10M"]
    axis_zone_x = bar_x
    axis_zone_w = bar_zone_w
    for i, t in enumerate(axis_labels):
        n = i + 1
        ax = axis_zone_x + int((axis_zone_w / (len(axis_labels) - 1)) * i)
        add_text(
            slide, f"axis-{n}", t,
            x_px=ax - 22, y_px=axis_y, w_px=44, h_px=14,
            font_size_px=9, color=TEXT_FAINT, bold=True,
            align="center" if 0 < i < len(axis_labels) - 1 else ("left" if i == 0 else "right"),
        )

    # Threshold callout
    th_y = body_top + body_h - 32
    add_rect(slide, "threshold-bg", right_x, th_y, right_w, 30, BAD_BG)
    add_rect(slide, "threshold-accent", right_x, th_y, 3, 30, BAD_INK)
    add_text(
        slide, "threshold-text",
        "<strong>Tolerance threshold:</strong> past +4 weeks ($4.8M), foregone savings exceed annual program budget.",
        x_px=right_x + 14, y_px=th_y, w_px=right_w - 24, h_px=30,
        font_size_px=10, color=BAD_INK, bold=False,
        emphasis_color=BAD_INK, anchor="middle",
    )

    add_footer(slide, page_num=55)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "55_delay-sensitivity-burn-scale.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
