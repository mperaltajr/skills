"""
Builder for pattern 70: Radar capability chart with delta rail.

SVG-driven radar (picture-asset per SHAPE-ROLES): chart-canvas placeholder.
Delta rail with delta-N-* and legend-N-* IDs is addressable.

Source HTML: _pattern-library/70_radar-capability.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

CHART_PLACEHOLDER = RGBColor(0xF4, 0xF4, 0xF6)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_text(
        slide, "title",
        "Capability radar — baseline vs pilot week 4 across six dimensions.",
        x_px=56, y_px=50, w_px=1100, h_px=40,
        font_size_px=27, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Every dimension moved up; cycle time and stakeholder sign-off jumped the most — "
        "both are where Slide Lab automation lands hardest.",
        x_px=56, y_px=98, w_px=1100, h_px=22,
        font_size_px=14, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 56, 140, 56, 3, BRAND_ACCENT)

    # Body grid
    g_top = 180
    g_left = 56
    g_right = 1280 - 56
    g_bottom = 720 - 60 - 48  # leave room for convergence + footer
    g_w = g_right - g_left
    g_h = g_bottom - g_top
    radar_w = int(g_w * 0.55)
    annot_w = g_w - radar_w - 24

    # Radar placeholder (chart-canvas)
    radar_size = min(radar_w, g_h) - 30
    rx = g_left + (radar_w - radar_size) // 2
    ry = g_top + (g_h - radar_size) // 2
    add_rect(slide, "chart-canvas", rx, ry, radar_size, radar_size, CHART_PLACEHOLDER)

    # Annotation panel (right)
    ap_x = g_left + radar_w + 24
    add_text(
        slide, "annot-header", "BEFORE VS AFTER, BY DIMENSION",
        x_px=ap_x, y_px=g_top + 4, w_px=annot_w, h_px=18,
        font_size_px=13, color=BRAND_PRIMARY, bold=True, uppercase=True,
    )

    # Legend (under header)
    leg_y = g_top + 28
    add_rect(slide, "legend-1-swatch", ap_x, leg_y + 4, 14, 14, BRAND_PRIMARY_MID)
    add_text(
        slide, "legend-1-label", "Week 0",
        x_px=ap_x + 20, y_px=leg_y + 2, w_px=80, h_px=18,
        font_size_px=11, color=TEXT_MID, bold=True,
    )
    add_rect(slide, "legend-2-swatch", ap_x + 100, leg_y + 4, 14, 14, BRAND_ACCENT)
    add_text(
        slide, "legend-2-label", "Week 4",
        x_px=ap_x + 120, y_px=leg_y + 2, w_px=80, h_px=18,
        font_size_px=11, color=TEXT_MID, bold=True,
    )

    # Delta rows: 6 dims, each with before, arrow, after
    dim_data = [
        ("Structure clarity", "2", "4", False),
        ("Argument sharpness", "2", "4", False),
        ("Visual polish", "3", "4", False),
        ("Cycle time", "2", "5", True),
        ("Reviewer alignment", "2", "4", False),
        ("Stakeholder sign-off", "2", "5", True),
    ]
    rows_top = leg_y + 30
    rows_h = g_h - (rows_top - g_top) - 8
    row_h = rows_h // 6

    for ri, (name, before, after, hot) in enumerate(dim_data):
        n = ri + 1
        dy = rows_top + ri * row_h

        # Name
        add_text(
            slide, f"delta-{n}-name", name,
            x_px=ap_x, y_px=dy + (row_h - 18) // 2, w_px=annot_w - 130, h_px=18,
            font_size_px=12, color=BRAND_PRIMARY if hot else TEXT_DARK, bold=True,
        )
        # Before
        add_text(
            slide, f"delta-{n}-before", before,
            x_px=ap_x + annot_w - 120, y_px=dy + (row_h - 18) // 2, w_px=30, h_px=18,
            font_size_px=13, color=TEXT_MID, bold=True, align="center",
        )
        # Arrow
        add_text(
            slide, f"delta-{n}-arrow", "→",
            x_px=ap_x + annot_w - 86, y_px=dy + (row_h - 18) // 2, w_px=24, h_px=18,
            font_size_px=12, color=TEXT_FAINT, bold=True, align="center",
        )
        # After
        add_text(
            slide, f"delta-{n}-after", after,
            x_px=ap_x + annot_w - 58, y_px=dy + (row_h - 18) // 2, w_px=30, h_px=18,
            font_size_px=13, color=BRAND_ACCENT, bold=True, align="center",
        )

    # Convergence band
    cv_y = g_bottom + 6
    cv_h = 40
    add_rect(slide, "convergence-bg", g_left, cv_y, g_w, cv_h, BRAND_PRIMARY)
    add_text(
        slide, "convergence",
        "Pilot polygon engulfs the baseline on every axis — cycle time and stakeholder sign-off each "
        "gained three points, the largest single-dimension lifts.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_w - 44, h_px=cv_h,
        font_size_px=13, color=WHITE, italic=True, anchor="middle",
    )

    add_footer(slide, page_num=70)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "70_radar-capability.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
