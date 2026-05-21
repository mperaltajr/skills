"""
Builder for pattern 52: Numbered tile rail (5 tiles) with bottom statement.

Source HTML: _pattern-library/52_numbered-tile-rail-with-statement.html
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
from pptx.dml.color import RGBColor

GHOST_NUMERAL = RGBColor(0xE5, 0xD5, 0xF0)
STATEMENT_BG = RGBColor(0x1A, 0x1A, 0x2E)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title block (with eyebrow)
    add_text(
        slide, "eyebrow", "WHAT MUST BE TRUE",
        x_px=48, y_px=48, w_px=900, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True,
    )
    add_text(
        slide, "title",
        "Five conditions that turn this from a training exercise into a growth engine.",
        x_px=48, y_px=66, w_px=1180, h_px=68,
        font_size_px=26, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Each is non-negotiable. Missing one collapses the others — together they hold up the operating model.",
        x_px=48, y_px=140, w_px=940, h_px=20,
        font_size_px=13, color=TEXT_MID,
    )
    add_rect(slide, "brand-rule", 48, 168, 56, 3, BRAND_ACCENT)

    # 5-tile rail
    rail_top = 196
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
         BRAND_PRIMARY),
        ("02", "All insights grounded in real operations",
         "Pickup, delivery, sort, linehaul, clearance — not analyst frameworks. Every POV anchored to how the business actually works.",
         BRAND_PRIMARY),
        ("03", "Every output tied to revenue, cost, or margin",
         "No exceptions. If we can't connect it to financial impact, we don't ship it. This is the non-negotiable filter.",
         BRAND_ACCENT),
        ("04", "Capability embedded into live sales & governance",
         "Not a standalone program. Embedded into how we sell, how we deliver, how we govern — not optional.",
         BRAND_ACCENT),
        ("05", "Scales with standardized tools & required adoption",
         "Playbooks, templates, and adoption are required — not optional. This scales across the account, not just one team.",
         BRAND_PRIMARY),
    ]

    for i, (num, heading, body, top_color) in enumerate(tile_data):
        n = i + 1
        tx = rail_left + i * (tile_w + gap)
        # Tile body
        bg = CARD_BG if (i % 2 == 0) else WHITE
        tile = add_rect(slide, f"card-{n}-body-bg", tx, rail_top, tile_w, rail_h, bg)
        tile.line.color.rgb = CARD_BORDER
        tile.line.width = 9525
        # Top accent (4px)
        add_rect(slide, f"card-{n}-accent", tx, rail_top, tile_w, 4, top_color)

        # Numeral (ghost)
        add_text(
            slide, f"card-{n}-num", num,
            x_px=tx + 18, y_px=rail_top + 22, w_px=tile_w - 36, h_px=56,
            font_size_px=56, color=GHOST_NUMERAL, bold=True,
        )
        # Heading
        add_text(
            slide, f"card-{n}-heading", heading,
            x_px=tx + 18, y_px=rail_top + 92, w_px=tile_w - 36, h_px=70,
            font_size_px=14, color=TEXT_DARK, bold=True,
        )
        # Tile rule
        add_rect(slide, f"card-{n}-rule", tx + 18, rail_top + 168, 32, 2, BRAND_ACCENT)
        # Body
        add_text(
            slide, f"card-{n}-body", body,
            x_px=tx + 18, y_px=rail_top + 184, w_px=tile_w - 36, h_px=rail_h - 200,
            font_size_px=11, color=TEXT_MID,
        )

    # Bottom statement bar
    st_y = 720 - 56 - 50
    add_rect(slide, "convergence-bg", 48, st_y, 1280 - 96, 50, STATEMENT_BG)
    add_text(
        slide, "convergence",
        "These five ensure this becomes a growth engine for the account — not an internal capability exercise.",
        x_px=70, y_px=st_y, w_px=1280 - 140, h_px=50,
        font_size_px=13, color=WHITE, bold=True, anchor="middle",
    )

    # Footer
    add_footer(slide, page_num=52)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "52_numbered-tile-rail-with-statement.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
