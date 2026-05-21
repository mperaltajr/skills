"""
Builder for pattern 59: Stat bank — 3x2 grid of stat tiles.

Source HTML: _pattern-library/59_stat-bank.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title block
    add_text(
        slide, "title",
        "Six numbers from four weeks — the pilot in shorthand.",
        x_px=48, y_px=48, w_px=1180, h_px=40,
        font_size_px=26, color=BRAND_PRIMARY, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Each tile is a single measured fact from the twelve decks built during the controlled rollout. "
        "No trends, no projections beyond what is noted — just where the meter currently reads.",
        x_px=48, y_px=96, w_px=880, h_px=42,
        font_size_px=13, color=TEXT_MID,
    )
    add_rect(slide, "brand-rule", 48, 152, 56, 3, BRAND_ACCENT)

    # 3x2 stat grid
    g_top = 188
    g_left = 48
    g_right = 1280 - 48
    g_w = g_right - g_left
    g_h = 420
    gap = 16
    tile_w = (g_w - 2 * gap) // 3
    tile_h = (g_h - gap) // 2

    tiles = [
        # (value, suffix, prefix, label, featured)
        ("5", "d", None, "Cycle time, median\nbrief to final deck", False),
        ("94", "%", None, "First-review sign-off\nno revision loop", True),
        ("12", None, None, "Pilot decks measured\nacross four practices", False),
        ("420", "K", "$", "Annualized savings\nprojected at scale", False),
        ("3", None, None, "Partner edits per deck\ndown from eight", False),
        ("0", None, None, "Build errors\nin production", False),
    ]

    for i, (val, suf, pre, label, featured) in enumerate(tiles):
        n = i + 1
        col = i % 3
        row = i // 3
        tx = g_left + col * (tile_w + gap)
        ty = g_top + row * (tile_h + gap)

        bg = BRAND_PRIMARY if featured else CARD_BG
        tile = add_rect(slide, f"metric-{n}-tile", tx, ty, tile_w, tile_h, bg)
        if not featured:
            tile.line.color.rgb = CARD_BORDER
            tile.line.width = 9525

        val_color = WHITE if featured else BRAND_PRIMARY
        unit_color = BRAND_ACCENT_SOFT if featured else BRAND_ACCENT
        label_color = BRAND_ACCENT_SOFT if featured else TEXT_MID

        # Compose value with prefix + value + suffix
        # We'll lay them out as separate text boxes for ID addressability
        cx = tx + 28
        cur_x = cx
        val_y = ty + 32
        # Prefix
        if pre:
            add_text(
                slide, f"metric-{n}-prefix", pre,
                x_px=cur_x, y_px=val_y + 14, w_px=40, h_px=44,
                font_size_px=36, color=unit_color, bold=True,
            )
            cur_x += 28
        # Value
        add_text(
            slide, f"metric-{n}-value", val,
            x_px=cur_x, y_px=val_y, w_px=200, h_px=80,
            font_size_px=72, color=val_color, bold=True,
        )
        # Suffix
        if suf:
            # Approx width of value text: chars * font * 0.55 + small pad
            suf_off = int(len(val) * 72 * 0.62) + 4
            add_text(
                slide, f"metric-{n}-unit", suf,
                x_px=cur_x + suf_off, y_px=val_y + 14, w_px=60, h_px=44,
                font_size_px=36, color=unit_color, bold=True,
            )

        # Label — anchored to bottom of tile
        add_text(
            slide, f"metric-{n}-label", label,
            x_px=tx + 28, y_px=ty + tile_h - 56, w_px=tile_w - 56, h_px=44,
            font_size_px=11, color=label_color, bold=True, uppercase=True,
        )

    # Footer rule + footer
    add_text(slide, "page-number", "59",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_MID, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "59_stat-bank.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
