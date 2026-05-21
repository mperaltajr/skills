"""
Builder for pattern 52d: Numbered tile rail with statement (dark variant).

Source HTML: _pattern-library/52_numbered-tile-rail-with-statement-dark.html
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
GHOST_NUMERAL = RGBColor(0x55, 0x36, 0x77)
STATEMENT_BG = RGBColor(0x1A, 0x05, 0x30)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome inline (title bottom-anchored y=20 h=80, subtitle y=108, brand-rule y=132)
    add_text(
        slide, "eyebrow", "WHAT MUST BE TRUE",
        x_px=64, y_px=0, w_px=900, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "title",
        "Five conditions that turn this from a training exercise into a growth engine.",
        x_px=64, y_px=20, w_px=1180, h_px=80,
        font_size_px=26, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Each is non-negotiable. Missing one collapses the others — together they hold up the operating model.",
        x_px=64, y_px=108, w_px=940, h_px=22,
        font_size_px=13, color=TEXT_ON_DARK_MID,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # 5-tile rail
    rail_top = 220
    rail_left = 48
    rail_right = 1280 - 48
    rail_w = rail_right - rail_left
    rail_bottom = 720 - 122
    rail_h = rail_bottom - rail_top
    gap = 14
    tile_w = (rail_w - 4 * gap) // 5

    tile_data = [
        ("01", "Leadership treats this as a commercial priority",
         "Not a training initiative. This lives in the account P&L conversation — owned at the top and funded accordingly.",
         BRAND_ACCENT_SOFT),
        ("02", "All insights grounded in real operations",
         "Pickup, delivery, sort, linehaul, clearance — not analyst frameworks. Every POV anchored to how the business actually works.",
         BRAND_ACCENT_SOFT),
        ("03", "Every output tied to revenue, cost, or margin",
         "No exceptions. If we can't connect it to financial impact, we don't ship it. This is the non-negotiable filter.",
         BRAND_ACCENT),
        ("04", "Capability embedded into live sales & governance",
         "Not a standalone program. Embedded into how we sell, how we deliver, how we govern — not optional.",
         BRAND_ACCENT),
        ("05", "Scales with standardized tools & required adoption",
         "Playbooks, templates, and adoption are required — not optional. This scales across the account, not just one team.",
         BRAND_ACCENT_SOFT),
    ]

    for i, (num, heading, body, top_color) in enumerate(tile_data):
        n = i + 1
        tx = rail_left + i * (tile_w + gap)
        tile = add_rect(slide, f"card-{n}-body-bg", tx, rail_top, tile_w, rail_h, CARD_BG_DARK)
        tile.line.color.rgb = CARD_BORDER_DARK
        tile.line.width = 9525
        add_rect(slide, f"card-{n}-accent", tx, rail_top, tile_w, 4, top_color)

        add_text(
            slide, f"card-{n}-num", num,
            x_px=tx + 18, y_px=rail_top + 22, w_px=tile_w - 36, h_px=56,
            font_size_px=56, color=GHOST_NUMERAL, bold=True,
        )
        add_text(
            slide, f"card-{n}-heading", heading,
            x_px=tx + 18, y_px=rail_top + 92, w_px=tile_w - 36, h_px=70,
            font_size_px=14, color=WHITE, bold=True,
        )
        add_rect(slide, f"card-{n}-rule", tx + 18, rail_top + 168, 32, 2, BRAND_ACCENT_SOFT)
        add_text(
            slide, f"card-{n}-body", body,
            x_px=tx + 18, y_px=rail_top + 184, w_px=tile_w - 36, h_px=rail_h - 200,
            font_size_px=11, color=TEXT_ON_DARK_MID,
        )

    st_y = 720 - 56 - 50
    add_rect(slide, "convergence-bg", 48, st_y, 1280 - 96, 50, STATEMENT_BG)
    add_text(
        slide, "convergence",
        "These five ensure this becomes a growth engine for the account — not an internal capability exercise.",
        x_px=70, y_px=st_y, w_px=1280 - 140, h_px=50,
        font_size_px=13, color=WHITE, bold=True, anchor="middle",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "52",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "52d_numbered-tile-rail-with-statement.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
