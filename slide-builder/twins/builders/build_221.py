"""
Builder for pattern 221: KPI Dashboard 6-up (3x2 grid with status dots and deltas).

Source HTML: _pattern-library/221_kpi-dashboard-6up.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, TEXT_MID, TEXT_FAINT, CARD_BG, CARD_BORDER, WHITE,
)
from pptx.dml.color import RGBColor

RAG_GREEN = RGBColor(0x16, 0xA3, 0x4A)
RAG_AMBER = RGBColor(0xD9, 0x77, 0x06)
RAG_RED = RGBColor(0xDC, 0x26, 0x26)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Performance at a Glance — <strong>KPI Dashboard</strong>",
        subtitle="FY2026 · Q2  |  As of May 2026 · All figures consolidated",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # 6 tiles in 3x2 grid: top:154, left:48, w=1184, h=494
    grid_top = 154
    grid_left = 48
    grid_w = 1184
    grid_h = 494
    tile_gap = 14
    tile_w = (grid_w - 2 * tile_gap) // 3  # 385
    tile_h = (grid_h - tile_gap) // 2  # 240

    tiles = [
        ("Revenue", "$2.4", "B", "Target: $2.3B", "▲ +4.3% vs Q1", RAG_GREEN, "up", 1.04),
        ("EBITDA", "18.2", "%", "Target: 20.0%", "▼ −1.8pp vs Q1", RAG_AMBER, "down", 0.91),
        ("NPS", "67", "pts", "Target: 60 pts", "▲ +5 pts vs Q1", RAG_GREEN, "up", 1.00),
        ("SLA Uptime", "99.7", "%", "Target: 99.5%", "▲ +0.2pp vs Q1", RAG_GREEN, "up", 1.00),
        ("Headcount", "4,812", "FTE", "Target: 5,000 FTE", "▼ −188 vs target", RAG_AMBER, "down", 0.96),
        ("Cost Savings", "$38", "M", "Target: $60M", "▼ −$22M vs target", RAG_RED, "down", 0.63),
    ]

    for i, (label, value, unit, target, delta, dot_color, direction, fill_pct) in enumerate(tiles):
        n = i + 1
        col = i % 3
        row = i // 3
        tx = grid_left + col * (tile_w + tile_gap)
        ty = grid_top + row * (tile_h + tile_gap)
        # Tile body
        tile = add_rect(slide, f"metric-{n}-tile", tx, ty, tile_w, tile_h, CARD_BG)
        tile.line.color.rgb = CARD_BORDER
        tile.line.width = 9525
        # Status dot (top-right)
        add_rect(slide, f"metric-{n}-status", tx + tile_w - 24, ty + 12, 10, 10, dot_color)
        # Label
        add_text(slide, f"metric-{n}-label", label,
                 x_px=tx + 16, y_px=ty + 14, w_px=tile_w - 40, h_px=16,
                 font_size_px=11, color=BRAND_PRIMARY, bold=True, uppercase=True)
        # Value + unit
        add_text(slide, f"metric-{n}-value", value,
                 x_px=tx + 16, y_px=ty + 50, w_px=tile_w - 40, h_px=72,
                 font_size_px=40, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"metric-{n}-unit", unit,
                 x_px=tx + 16, y_px=ty + 100, w_px=tile_w - 40, h_px=22,
                 font_size_px=14, color=TEXT_MID)
        # Sublabel (target)
        add_text(slide, f"metric-{n}-sublabel", target,
                 x_px=tx + 16, y_px=ty + 138, w_px=tile_w - 40, h_px=16,
                 font_size_px=10, color=TEXT_FAINT)
        # Delta
        delta_color = RAG_GREEN if direction == "up" else (RAG_RED if direction == "down" else TEXT_MID)
        add_text(slide, f"metric-{n}-delta", delta,
                 x_px=tx + 16, y_px=ty + 158, w_px=tile_w - 40, h_px=18,
                 font_size_px=12, color=delta_color, bold=True)
        # Progress bar at bottom (5px tall)
        add_rect(slide, f"metric-{n}-progress-bg", tx, ty + tile_h - 5, tile_w, 5, CARD_BORDER)
        fill_w = int(tile_w * min(fill_pct, 1.0))
        add_rect(slide, f"metric-{n}-progress", tx, ty + tile_h - 5, fill_w, 5, dot_color)

    add_footer(slide, page_num=221)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "221_kpi-dashboard-6up.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
