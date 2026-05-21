"""
Builder for pattern 10d: Evidence chart with annotation panel — DARK variant.

Light source: twins/builders/build_10.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
ANNOT_BG_DARK = RGBColor(0x14, 0x05, 0x28)
UP_GOOD = RGBColor(0x4A, 0xD4, 0x80)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "eyebrow", "Pilot · Week 4 readout",
        x_px=64, y_px=64, w_px=600, h_px=18,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "title",
        "Four weeks in — every metric is moving in the right direction.",
        x_px=64, y_px=86, w_px=1050, h_px=72,
        font_size_px=26, color=WHITE, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Baseline versus week-4 pilot, same teams and deck types. The pattern matters more than any single line.",
        x_px=64, y_px=164, w_px=1050, h_px=24,
        font_size_px=13, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=200, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    body_top = 230
    body_h = 360
    left_x = 64
    grid_w = 1280 - 128
    gap = 36
    left_w = int((grid_w - gap) * 57 / 100)
    right_w = grid_w - gap - left_w
    right_x = left_x + left_w + gap

    add_text(
        slide, "chart-title", "Pilot vs baseline — week 4 vs week 0",
        x_px=left_x, y_px=body_top, w_px=left_w - 240, h_px=22,
        font_size_px=16, color=WHITE, bold=True,
    )
    legend_x = left_x + left_w - 240
    add_rect(slide, "legend-1-swatch", x_px=legend_x, y_px=body_top + 6, w_px=11, h_px=11, fill_color=TEXT_ON_DARK_FAINT)
    add_text(
        slide, "legend-1-label", "BASELINE",
        x_px=legend_x + 18, y_px=body_top + 4, w_px=80, h_px=14,
        font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, uppercase=True,
    )
    add_rect(slide, "legend-2-swatch", x_px=legend_x + 110, y_px=body_top + 6, w_px=11, h_px=11, fill_color=BRAND_ACCENT)
    add_text(
        slide, "legend-2-label", "PILOT · WK 4",
        x_px=legend_x + 128, y_px=body_top + 4, w_px=110, h_px=14,
        font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, uppercase=True,
    )

    add_text(
        slide, "chart-subtitle", "12 decks, matched by type and partner reviewer.",
        x_px=left_x, y_px=body_top + 22, w_px=left_w, h_px=18,
        font_size_px=12, color=TEXT_ON_DARK_MID, italic=True,
    )

    bars_top = body_top + 50
    bars_h = 220
    row_h = bars_h // 4
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
        add_text(
            slide, f"bar-{n}-label", label,
            x_px=left_x, y_px=ry + 4, w_px=128, h_px=16,
            font_size_px=10, color=WHITE, bold=True, uppercase=True,
        )
        add_text(
            slide, f"bar-{n}-unit", unit,
            x_px=left_x, y_px=ry + 20, w_px=128, h_px=14,
            font_size_px=10, color=TEXT_ON_DARK_FAINT,
        )
        bw = max(int(track_w * base_pct), 12)
        add_rect(slide, f"bar-{n}-baseline-bar", track_x, ry + 5, bw, 14, TEXT_ON_DARK_FAINT)
        add_text(
            slide, f"bar-{n}-baseline-val", base_val,
            x_px=track_x, y_px=ry + 5, w_px=bw - 6, h_px=14,
            font_size_px=9, color=WHITE, bold=True, align="right", anchor="middle",
        )
        pw = max(int(track_w * pilot_pct), 12)
        add_rect(slide, f"bar-{n}-pilot-bar", track_x, ry + 23, pw, 14, BRAND_ACCENT)
        add_text(
            slide, f"bar-{n}-pilot-val", pilot_val,
            x_px=track_x, y_px=ry + 23, w_px=pw - 6, h_px=14,
            font_size_px=9, color=WHITE, bold=True, align="right", anchor="middle",
        )
        add_text(
            slide, f"bar-{n}-delta", delta,
            x_px=delta_x, y_px=ry + 4, w_px=70, h_px=18,
            font_size_px=13, color=UP_GOOD, bold=True, align="right",
        )
        add_text(
            slide, f"bar-{n}-delta-cap", cap,
            x_px=delta_x, y_px=ry + 22, w_px=70, h_px=14,
            font_size_px=8, color=TEXT_ON_DARK_FAINT, bold=True, align="right", uppercase=True,
        )

    add_text(
        slide, "chart-source",
        "Source: 12 decks measured Apr–May 2026; baseline = pre-Slide Lab same teams, matched by deck type and partner reviewer.",
        x_px=left_x, y_px=bars_top + bars_h + 14, w_px=left_w, h_px=28,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
    )

    # RIGHT — annotation panel (deeper than slide bg to read)
    add_rect(slide, "annot-bg", right_x, body_top, right_w, body_h, ANNOT_BG_DARK)

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

    annot_data = [
        ("Worth a partner-meeting",
         "Cycle-time gain alone recovers roughly 3 senior hours per deck — a meaningful line item at the practice level."),
        ("Compounds across the workstream",
         "Patterns lock in after week 2; fewer late-stage rewrites, faster analyst onboarding, cleaner builds downstream."),
        ("Trigger for Q3 rollout",
         "Data supports expanding to 3 more practice areas — staged, with the same baseline-tracking discipline."),
    ]
    rows_top = body_top + 100
    rows_h = body_h - 110
    row_h2 = rows_h // 3
    for i, (label, body2) in enumerate(annot_data):
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
            slide, f"annot-{n}-body", body2,
            x_px=right_x + 46, y_px=ay + 22, w_px=right_w - 70, h_px=row_h2 - 24,
            font_size_px=11, color=BRAND_ACCENT_SOFT,
        )

    add_text(
        slide, "convergence",
        "Four independent measures, same direction — this is a pattern, not a single lucky data point.",
        x_px=64, y_px=body_top + body_h + 28, w_px=1280 - 128, h_px=28,
        font_size_px=12, color=TEXT_ON_DARK_MID, italic=True, align="center",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "10",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "10d_hero-stat-annotated.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
