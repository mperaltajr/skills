"""
Builder for pattern 59d: Stat bank (dark variant).

Source HTML: _pattern-library/59_stat-bank-dark.html
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
FEATURED_BG = RGBColor(0x1A, 0x05, 0x30)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Six numbers from four weeks — the pilot in shorthand.",
        x_px=64, y_px=20, w_px=1180, h_px=80,
        font_size_px=26, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Each tile is a single measured fact from the twelve decks built during the controlled rollout.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=13, color=TEXT_ON_DARK_MID,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    g_top = 220
    g_left = 48
    g_right = 1280 - 48
    g_w = g_right - g_left
    g_h = 420
    gap = 16
    tile_w = (g_w - 2 * gap) // 3
    tile_h = (g_h - gap) // 2

    tiles = [
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

        bg_c = FEATURED_BG if featured else CARD_BG_DARK
        tile = add_rect(slide, f"metric-{n}-tile", tx, ty, tile_w, tile_h, bg_c)
        if not featured:
            tile.line.color.rgb = CARD_BORDER_DARK
            tile.line.width = 9525

        val_color = WHITE
        unit_color = BRAND_ACCENT_SOFT if featured else BRAND_ACCENT
        label_color = BRAND_ACCENT_SOFT if featured else TEXT_ON_DARK_MID

        cx = tx + 28
        cur_x = cx
        val_y = ty + 32
        if pre:
            add_text(
                slide, f"metric-{n}-prefix", pre,
                x_px=cur_x, y_px=val_y + 14, w_px=40, h_px=44,
                font_size_px=36, color=unit_color, bold=True,
            )
            cur_x += 28
        add_text(
            slide, f"metric-{n}-value", val,
            x_px=cur_x, y_px=val_y, w_px=200, h_px=80,
            font_size_px=72, color=val_color, bold=True,
        )
        if suf:
            suf_off = int(len(val) * 72 * 0.62) + 4
            add_text(
                slide, f"metric-{n}-unit", suf,
                x_px=cur_x + suf_off, y_px=val_y + 14, w_px=60, h_px=44,
                font_size_px=36, color=unit_color, bold=True,
            )

        add_text(
            slide, f"metric-{n}-label", label,
            x_px=tx + 28, y_px=ty + tile_h - 56, w_px=tile_w - 56, h_px=44,
            font_size_px=11, color=label_color, bold=True, uppercase=True,
        )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "59",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "59d_stat-bank.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
