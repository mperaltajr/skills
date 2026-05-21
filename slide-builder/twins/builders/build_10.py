"""
Builder for pattern 10: Evidence chart with annotation panel.

Source HTML: _pattern-library/10_hero-stat-annotated.html
Left: horizontal bar chart (4 rows, baseline + pilot bars).
Right: dark annotation panel ("WHAT THIS MEANS") with 3 rows.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

UP_GOOD = RGBColor(0x16, 0xA3, 0x4A)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Custom title block (eyebrow + 26px title)
    add_text(
        slide, "eyebrow", "Pilot · Week 4 readout",
        x_px=64, y_px=64, w_px=600, h_px=18,
        font_size_px=11, color=BRAND_ACCENT, bold=True, uppercase=True,
    )
    add_text(
        slide, "title",
        "Four weeks in — every metric is moving in the right direction.",
        x_px=64, y_px=86, w_px=1050, h_px=72,
        font_size_px=26, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Baseline versus week-4 pilot, same teams and deck types. The pattern matters more than any single line.",
        x_px=64, y_px=164, w_px=1050, h_px=24,
        font_size_px=13, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=200, w_px=56, h_px=3, fill_color=BRAND_ACCENT)

    # Body grid: 57/43 with 36px gap, occupies y 220-580
    body_top = 230
    body_h = 360
    left_x = 64
    grid_w = 1280 - 128
    gap = 36
    left_w = int((grid_w - gap) * 57 / 100)
    right_w = grid_w - gap - left_w
    right_x = left_x + left_w + gap

    # LEFT — chart header
    add_text(
        slide, "chart-title", "Pilot vs baseline — week 4 vs week 0",
        x_px=left_x, y_px=body_top, w_px=left_w - 200, h_px=22,
        font_size_px=16, color=BRAND_PRIMARY, bold=True,
    )
    # Legend (top-right of left column)
    legend_x = left_x + left_w - 220
    # Baseline swatch
    add_rect(slide, "legend-1-swatch", x_px=legend_x, y_px=body_top + 6, w_px=11, h_px=11, fill_color=TEXT_FAINT)
    add_text(
        slide, "legend-1-label", "BASELINE",
        x_px=legend_x + 18, y_px=body_top + 4, w_px=80, h_px=14,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True,
    )
    add_rect(slide, "legend-2-swatch", x_px=legend_x + 110, y_px=body_top + 6, w_px=11, h_px=11, fill_color=BRAND_ACCENT)
    add_text(
        slide, "legend-2-label", "PILOT · WK 4",
        x_px=legend_x + 128, y_px=body_top + 4, w_px=100, h_px=14,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True,
    )

    add_text(
        slide, "chart-subtitle", "12 decks, matched by type and partner reviewer.",
        x_px=left_x, y_px=body_top + 22, w_px=left_w, h_px=18,
        font_size_px=12, color=TEXT_MID, italic=True,
    )

    # Bar rows: 4 rows in y range body_top+50 to body_top+260
    bars_top = body_top + 50
    bars_h = 220
    row_h = bars_h // 4
    # bar-row: 130px label | track | 70px delta
    track_x = left_x + 130 + 14
    track_w = left_w - 130 - 14 - 70 - 14
    delta_x = left_x + left_w - 70

    bar_data = [
        ("CYCLE TIME", "days", 1.0, 0.357, "14", "5", "−64%", "FASTER"),
        ("PARTNER EDITS", "per deck", 0.571, 0.214, "8", "3", "−63%", "FEWER"),
        ("SIGN-OFF RATE", "first-pass", 0.60, 0.94, "60%", "94%", "+34 pts", "HIGHER"),
        ("BUILD ERRORS", "per deck", 0.286, 0.12, "4", "0", "−100%", "CLEARED"),
    ]
    for i, (label, unit, base_pct, pilot_pct, base_val, pilot_val, delta, cap) in enumerate(bar_data):
        n = i + 1
        ry = bars_top + i * row_h
        # Label
        add_text(
            slide, f"bar-{n}-label", label,
            x_px=left_x, y_px=ry + 4, w_px=128, h_px=16,
            font_size_px=10, color=TEXT_DARK, bold=True, uppercase=True,
        )
        add_text(
            slide, f"bar-{n}-unit", unit,
            x_px=left_x, y_px=ry + 20, w_px=128, h_px=14,
            font_size_px=10, color=TEXT_FAINT,
        )
        # Baseline bar
        bw = max(int(track_w * base_pct), 12)
        add_rect(slide, f"bar-{n}-baseline-bar", track_x, ry + 5, bw, 14, TEXT_FAINT)
        add_text(
            slide, f"bar-{n}-baseline-val", base_val,
            x_px=track_x, y_px=ry + 5, w_px=bw - 6, h_px=14,
            font_size_px=9, color=WHITE, bold=True, align="right", anchor="middle",
        )
        # Pilot bar
        pw = max(int(track_w * pilot_pct), 12)
        add_rect(slide, f"bar-{n}-pilot-bar", track_x, ry + 23, pw, 14, BRAND_ACCENT)
        add_text(
            slide, f"bar-{n}-pilot-val", pilot_val,
            x_px=track_x, y_px=ry + 23, w_px=pw - 6, h_px=14,
            font_size_px=9, color=WHITE, bold=True, align="right", anchor="middle",
        )
        # Delta
        add_text(
            slide, f"bar-{n}-delta", delta,
            x_px=delta_x, y_px=ry + 4, w_px=70, h_px=18,
            font_size_px=13, color=UP_GOOD, bold=True, align="right",
        )
        add_text(
            slide, f"bar-{n}-delta-cap", cap,
            x_px=delta_x, y_px=ry + 22, w_px=70, h_px=14,
            font_size_px=8, color=TEXT_FAINT, bold=True, align="right", uppercase=True,
        )

    # Chart source line
    add_text(
        slide, "chart-source",
        "Source: 12 decks measured Apr–May 2026; baseline = pre-Slide Lab same teams, matched by deck type and partner reviewer.",
        x_px=left_x, y_px=bars_top + bars_h + 14, w_px=left_w, h_px=28,
        font_size_px=10, color=TEXT_FAINT, italic=True,
    )

    # RIGHT — annotation panel
    annot_h = body_h
    add_rect(slide, "annot-bg", right_x, body_top, right_w, annot_h, BRAND_PRIMARY)

    add_text(
        slide, "annot-header", "WHAT THIS MEANS",
        x_px=right_x + 24, y_px=body_top + 22, w_px=right_w - 48, h_px=16,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "annot-sub",
        "Three reads — partner time, compounding effect, rollout signal.",
        x_px=right_x + 24, y_px=body_top + 42, w_px=right_w - 48, h_px=32,
        font_size_px=12, color=BRAND_ACCENT_SOFT, italic=True,
    )
    add_rect(slide, "annot-rule", x_px=right_x + 24, y_px=body_top + 82, w_px=36, h_px=2, fill_color=BRAND_ACCENT)

    # 3 annotation rows
    annot_data = [
        ("Worth a partner-meeting",
         "Cycle-time gain alone recovers roughly 3 senior hours per deck — a meaningful line item at the practice level."),
        ("Compounds across the workstream",
         "Patterns lock in after week 2; fewer late-stage rewrites, faster analyst onboarding, cleaner builds downstream."),
        ("Trigger for Q3 rollout",
         "Data supports expanding to 3 more practice areas — staged, with the same baseline-tracking discipline."),
    ]
    rows_top = body_top + 100
    rows_h = annot_h - 110
    row_h2 = rows_h // 3
    for i, (label, body) in enumerate(annot_data):
        n = i + 1
        ay = rows_top + i * row_h2
        add_text(
            slide, f"annot-{n}-marker", "▸",
            x_px=right_x + 24, y_px=ay, w_px=18, h_px=20,
            font_size_px=14, color=BRAND_ACCENT, bold=True,
        )
        add_text(
            slide, f"annot-{n}-label", label,
            x_px=right_x + 46, y_px=ay, w_px=right_w - 70, h_px=20,
            font_size_px=13, color=WHITE, bold=True,
        )
        add_text(
            slide, f"annot-{n}-body", body,
            x_px=right_x + 46, y_px=ay + 22, w_px=right_w - 70, h_px=row_h2 - 24,
            font_size_px=11, color=BRAND_ACCENT_SOFT,
        )

    # Convergence — italic centered text (not the standard band, per HTML)
    add_text(
        slide, "convergence",
        "Four independent measures, same direction — this is a pattern, not a single lucky data point.",
        x_px=64, y_px=body_top + body_h + 28, w_px=1280 - 128, h_px=28,
        font_size_px=12, color=TEXT_MID, italic=True, align="center",
    )

    add_footer(slide, page_num=10)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "10_hero-stat-annotated.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
