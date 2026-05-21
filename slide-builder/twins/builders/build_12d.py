"""
Builder for pattern 12d: KPI tile dashboard — DARK variant.

Light source: twins/builders/build_12.py
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
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Four weeks in — every metric is moving in the right direction.",
        x_px=64, y_px=36, w_px=1000, h_px=64,
        font_size_px=27, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Pilot scorecard for the Slide Lab workstream pilot, weeks 1-4.",
        x_px=64, y_px=108, w_px=880, h_px=20,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    tile_w = 372
    tile_h = 171
    tile_gap = 18
    grid_left = 64
    grid_top = 220

    tile_data = [
        ("Cycle time", "-62%", "▼ vs baseline · 14d → 5d"),
        ("Partner edits", "1.4×", "▼ fewer rounds · 3.2 → 1.4 per deck"),
        ("Stakeholder sign-off", "94%", "▲ vs Q1 · 60% → 94%"),
        ("Deck length", "11 slides", "▼ tighter · 19 → 11 avg"),
        ("Storyline gate pass rate", "8/10", "▲ first-pass · 4/10 → 8/10"),
        ("Build errors", "0", "● sustained · 4 consecutive weeks clean"),
    ]

    for i, (label, value, delta) in enumerate(tile_data):
        n = i + 1
        col = i % 3
        row = i // 3
        tx = grid_left + col * (tile_w + tile_gap)
        ty = grid_top + row * (tile_h + tile_gap)

        tile = add_rect(slide, f"metric-{n}-tile", tx, ty, tile_w, tile_h, CARD_BG_DARK)
        tile.line.color.rgb = CARD_BORDER_DARK
        tile.line.width = 9525

        add_text(
            slide, f"metric-{n}-label", label,
            x_px=tx + 26, y_px=ty + 24, w_px=tile_w - 52, h_px=16,
            font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, uppercase=True,
        )
        add_text(
            slide, f"metric-{n}-value", value,
            x_px=tx + 26, y_px=ty + 50, w_px=tile_w - 52, h_px=64,
            font_size_px=44, color=WHITE, bold=True,
        )
        add_text(
            slide, f"metric-{n}-delta", delta,
            x_px=tx + 26, y_px=ty + tile_h - 32, w_px=tile_w - 52, h_px=16,
            font_size_px=11, color=BRAND_ACCENT_SOFT,
        )

    conv_y = 720 - 78 - 42
    add_rect(slide, "convergence-bg",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42, fill_color=BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "Two more weeks of pilot data and we move to a Q3 rollout decision.",
        x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42,
        font_size_px=14, color=WHITE, italic=True,
        anchor="middle", padding_px=(0, 22, 0, 22),
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "12",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "12d_kpi-tile-dashboard.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
