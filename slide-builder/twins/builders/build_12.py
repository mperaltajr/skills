"""
Builder for pattern 12: KPI tile dashboard (6 tiles, 3 cols x 2 rows).

Source HTML: _pattern-library/12_kpi-tile-dashboard.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Pattern 12 uses smaller title (27px not 32px). Override default title block.
    add_title_block(
        slide,
        title="Four weeks in — every metric is moving in the right direction.",
        subtitle="Pilot scorecard for the Slide Lab workstream pilot, weeks 1-4.",
        title_h=64,  # 27px × 2 lines × 1.2 ≈ 65
        subtitle_h=20,
        brand_rule_w=56,
    )

    # 6 tiles in 3x2 grid. Container: left:64, right:64, top:188, ~360px tall.
    # Tile width = (1280 - 128 - 36) / 3 = 372
    # Tile height = (360 - 18) / 2 = 171
    tile_w = 372
    tile_h = 171
    tile_gap = 18
    grid_left = 64
    grid_top = 200

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

        # Tile body
        tile = add_rect(slide, f"metric-{n}-tile", tx, ty, tile_w, tile_h, CARD_BG)
        tile.line.color.rgb = CARD_BORDER
        tile.line.width = 9525  # 1px

        # Label (top)
        add_text(
            slide, f"metric-{n}-label", label,
            x_px=tx + 26, y_px=ty + 24, w_px=tile_w - 52, h_px=16,
            font_size_px=10, color=TEXT_MID, bold=True, uppercase=True,
        )

        # Value (centered vertically in tile)
        add_text(
            slide, f"metric-{n}-value", value,
            x_px=tx + 26, y_px=ty + 50, w_px=tile_w - 52, h_px=64,
            font_size_px=44, color=BRAND_PRIMARY, bold=True,
        )

        # Delta (bottom)
        add_text(
            slide, f"metric-{n}-delta", delta,
            x_px=tx + 26, y_px=ty + tile_h - 32, w_px=tile_w - 52, h_px=16,
            font_size_px=11, color=TEXT_MID,
        )

    add_convergence(
        slide,
        "Two more weeks of pilot data and we move to a Q3 rollout decision.",
    )

    add_footer(slide, page_num=12)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "12_kpi-tile-dashboard.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
