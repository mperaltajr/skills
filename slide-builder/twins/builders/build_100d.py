"""
Builder for pattern 100d: Pareto 80/20 chart — dark variant.

Source HTML: _pattern-library/100_pareto-80-20-dark.html
Light template: twins/builders/build_100.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(slide, "title",
             "Where rework comes from — three sources cause 80% of it.",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Hours of deck rework in Q1 by root cause, sorted descending, with cumulative share.",
             x_px=64, y_px=108, w_px=1030, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 56, 3, BRAND_ACCENT_SOFT)

    # Content block
    block_left = 64
    block_top = 220
    block_bot = 720 - 72
    block_h = block_bot - block_top
    block_w = 1280 - 128
    annot_w = 320
    chart_w = block_w - annot_w - 24

    # Chart zone
    chart_h = block_h - 70
    chart_x = block_left
    chart_y = block_top
    cz = add_rect(slide, "chart-zone", chart_x, chart_y, chart_w, chart_h, CARD_BG_DARK)
    cz.line.color.rgb = CARD_BORDER_DARK
    cz.line.width = 9525

    add_text(slide, "chart-title",
             "Sources of deck rework · Q1 hours, n=100",
             x_px=chart_x + 20, y_px=chart_y + 14, w_px=chart_w - 320, h_px=16,
             font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)

    # Inline legend
    lg_x = chart_x + chart_w - 310
    add_rect(slide, "legend-1-swatch", lg_x, chart_y + 18, 12, 12, BRAND_ACCENT_SOFT)
    add_text(slide, "legend-1-label", "Hours",
             x_px=lg_x + 16, y_px=chart_y + 14, w_px=80, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_MID, bold=True)
    add_rect(slide, "legend-2-swatch", lg_x + 100, chart_y + 24, 14, 2, BRAND_ACCENT)
    add_text(slide, "legend-2-label", "Cumulative %",
             x_px=lg_x + 120, y_px=chart_y + 14, w_px=100, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_MID, bold=True)
    add_rect(slide, "legend-3-swatch", lg_x + 220, chart_y + 24, 14, 2, BRAND_ACCENT_SOFT)
    add_text(slide, "legend-3-label", "80% threshold",
             x_px=lg_x + 240, y_px=chart_y + 14, w_px=80, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_MID, bold=True)

    # Chart canvas placeholder
    canvas_x = chart_x + 20
    canvas_y = chart_y + 44
    canvas_w = chart_w - 40
    canvas_h = chart_h - 64
    add_rect(slide, "chart-canvas", canvas_x, canvas_y, canvas_w, canvas_h, BRAND_PRIMARY)
    add_text(slide, "chart-canvas-placeholder",
             "[ PARETO CHART — 8 bars descending + cumulative % line + 80% threshold ]",
             x_px=canvas_x, y_px=canvas_y, w_px=canvas_w, h_px=canvas_h,
             font_size_px=12, color=TEXT_ON_DARK_FAINT, italic=True,
             align="center", anchor="middle")

    # Annotation panel
    annot_x = chart_x + chart_w + 24
    annot_y = chart_y
    add_rect(slide, "annot-panel", annot_x, annot_y, annot_w, chart_h, BRAND_PRIMARY_MID)

    add_text(slide, "annot-header", "WHERE TO FOCUS",
             x_px=annot_x + 22, y_px=annot_y + 22, w_px=annot_w - 44, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "annot-sub",
             "Top 3 categories drive 80% — focus there.",
             x_px=annot_x + 22, y_px=annot_y + 42, w_px=annot_w - 44, h_px=44,
             font_size_px=15, color=WHITE, bold=True)

    bullets = [
        ("Late stakeholder adds (35%).",
         "Lock the reviewer list at kickoff; freeze content at T-3 days."),
        ("Storyline drift (28%).",
         "Run the narrative gate before any slide is built — not after."),
        ("Brand template mismatch (17%).",
         "Start every deck from the approved skeleton library, not a copy-paste."),
        ("The remaining five causes share only 20%",
         "— defer them until the vital few are fixed."),
    ]
    b_top = annot_y + 100
    b_h = 68
    for i, (lead, body) in enumerate(bullets):
        n = i + 1
        by = b_top + i * b_h
        add_rect(slide, f"annot-{n}-marker", annot_x + 22, by + 4, 8, 8, BRAND_ACCENT_SOFT)
        text = f"{lead} {body}"
        add_text(slide, f"annot-{n}-body", text,
                 x_px=annot_x + 36, y_px=by, w_px=annot_w - 58, h_px=64,
                 font_size_px=11, color=WHITE)

    # Convergence
    conv_y = block_top + chart_h + 14
    conv_h = block_h - chart_h - 14
    add_rect(slide, "convergence-bg", block_left, conv_y, block_w, conv_h, BRAND_PRIMARY_MID)
    add_text(slide, "convergence",
             "Fix the three vital causes and Q2 rework drops by an estimated 64 hours — one full deck cycle reclaimed every month.",
             x_px=block_left + 18, y_px=conv_y, w_px=block_w - 36, h_px=conv_h,
             font_size_px=13, color=WHITE, italic=True, bold=True, anchor="middle")

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "100",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "100d_pareto-80-20-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
