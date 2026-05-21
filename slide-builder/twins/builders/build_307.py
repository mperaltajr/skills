"""
Builder for pattern 307: KPI scorecard 12-up (4x3 grid with sparklines + RAG dots).

LEGEND PLACEMENT: RAG legend sits BELOW the subheadline+brand-rule, right-aligned
to x ≈ 1232. Top-y = 232 (clearly below subheadline y≈220). Body grid is shifted
down (top y=292) to clear the legend.

Source HTML: _pattern-library/307_kpi-scorecard-12up.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
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
        title="Global Programme <strong>KPI Scorecard</strong>",
        subtitle="Q2 2026 · 12 key metrics across delivery, finance, and talent",
        title_x=48, title_y=44, title_w=900, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # ── LEGEND (BELOW SUBHEADLINE, right-aligned) ──
    # subheadline bottom is around y=200; brand-rule at y=216; legend at y=232.
    leg_h = 32
    leg_y = 232
    leg_right_edge = 1232
    # Each item ≈ 88px: dot 9px + 6 gap + label 70px; total 3 items + "RAG STATUS" tag
    items = [("Green", RAG_GREEN), ("Amber", RAG_AMBER), ("Red", RAG_RED)]
    item_w = 86
    title_w = 90
    leg_w = title_w + len(items) * item_w + 16
    leg_x = leg_right_edge - leg_w

    leg_bg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, CARD_BG)
    leg_bg.line.color.rgb = CARD_BORDER
    leg_bg.line.width = 9525
    add_text(
        slide, "legend-title", "RAG STATUS",
        x_px=leg_x + 12, y_px=leg_y, w_px=title_w, h_px=leg_h,
        font_size_px=9, color=TEXT_MID, bold=True, letter_spacing_px=1.4,
        anchor="middle",
    )
    cur_x = leg_x + title_w + 12
    for i, (lbl, col) in enumerate(items):
        n = i + 1
        add_rect(slide, f"legend-{n}-dot", cur_x, leg_y + (leg_h - 8) // 2, 8, 8, col)
        add_text(
            slide, f"legend-{n}-label", lbl,
            x_px=cur_x + 14, y_px=leg_y, w_px=item_w - 18, h_px=leg_h,
            font_size_px=10, color=TEXT_DARK, bold=True, anchor="middle",
        )
        cur_x += item_w

    # ── KPI GRID: 4 cols x 3 rows, body starts y=276 (below legend at 264) ──
    grid_top = 276
    grid_left = 48
    gap = 14
    grid_w = 1184
    tile_w = (grid_w - 3 * gap) // 4  # ≈ 285
    # Body must end ≤ y=670 so it doesn't bleed into the invariant zone (≥672).
    grid_bottom = 670
    grid_h = grid_bottom - grid_top
    tile_h = (grid_h - 2 * gap) // 3  # ≈ 122 with grid_top=276, grid_bottom=670

    tiles = [
        ("Revenue (USD)", "$4.8B", "▲ 6.2% vs Q1", "green"),
        ("EBIT Margin", "14.3%", "▼ 0.4pp vs Q1", "amber"),
        ("Net New Bookings", "$1.2B", "▲ 11.8% vs Q1", "green"),
        ("Cost-to-Serve", "38.7%", "▼ 1.1pp vs target", "red"),
        ("Headcount", "52,410", "▲ 2.1% vs Q1", "green"),
        ("Attrition Rate", "12.4%", "▼ 0.8pp vs Q1", "amber"),
        ("Utilisation", "88.2%", "▲ 1.4pp vs Q1", "green"),
        ("CSAT Score", "8.7", "▲ 0.3 vs Q1", "green"),
        ("SLA Compliance", "96.1%", "▼ 0.9pp vs target", "amber"),
        ("Open Risks", "23", "▼ 8.0% vs Q1", "red"),
        ("Training Hours", "41.2h", "▲ 5.7% vs Q1", "green"),
        ("Cloud Migration", "71%", "▲ 4.0pp vs Q1", "amber"),
    ]
    rag_map = {"green": RAG_GREEN, "amber": RAG_AMBER, "red": RAG_RED}

    for i, (name, value, delta, rag) in enumerate(tiles):
        n = i + 1
        col = i % 4
        row = i // 4
        tx = grid_left + col * (tile_w + gap)
        ty = grid_top + row * (tile_h + gap)
        tile = add_rect(slide, f"tile-{n}-bg", tx, ty, tile_w, tile_h, CARD_BG)
        tile.line.color.rgb = CARD_BORDER
        tile.line.width = 9525
        # RAG dot top-right
        add_rect(slide, f"tile-{n}-rag", tx + tile_w - 18, ty + 12, 8, 8, rag_map[rag])
        # Name
        add_text(
            slide, f"tile-{n}-name", name.upper(),
            x_px=tx + 14, y_px=ty + 10, w_px=tile_w - 36, h_px=14,
            font_size_px=9, color=TEXT_FAINT, bold=True, letter_spacing_px=1.2,
        )
        # Value
        add_text(
            slide, f"tile-{n}-value", value,
            x_px=tx + 14, y_px=ty + 28, w_px=tile_w - 28, h_px=36,
            font_size_px=24, color=BRAND_PRIMARY, bold=True,
        )
        # Delta
        delta_color = RAG_GREEN if delta.startswith("▲") else (TEXT_MID if delta.startswith("■") else RAG_RED)
        add_text(
            slide, f"tile-{n}-delta", delta,
            x_px=tx + 14, y_px=ty + tile_h - 24, w_px=tile_w - 28, h_px=18,
            font_size_px=10, color=delta_color, bold=True,
        )
        # Sparkline placeholder zone (right side of tile)
        spark_x = tx + tile_w - 90
        spark_y = ty + tile_h - 42
        # accent dashed line stand-in
        add_rect(slide, f"tile-{n}-spark-line",
                 spark_x, spark_y + 14, 76, 2, BRAND_ACCENT)
        # endpoint dot
        add_rect(slide, f"tile-{n}-spark-dot",
                 spark_x + 72, spark_y + 10, 6, 6, BRAND_ACCENT)

    add_footer(slide, page_num=307)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "307_kpi-scorecard-12up.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
