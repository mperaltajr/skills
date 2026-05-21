"""
Builder for pattern 76: Logo wall (4x3 = 12 tiles).

Source HTML: _pattern-library/76_logo-wall.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_FAINT, WHITE, SLIDE_BG,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Where Slide Lab has worked — twelve practices, eight industries.",
        subtitle="Engagements span Fortune 500 and category leaders across four continents. Logos shown as placeholders pending client approval — full reference list available on request.",
        title_x=48, title_w=1180, title_h=60,
        subtitle_h=40,
        brand_rule_w=56,
    )

    # 4x3 grid of logo tiles, left:48, right:48, top:184, height:408
    grid_left = 48
    grid_top = 184
    grid_w = 1280 - 96  # 1184
    grid_h = 408
    cols, rows = 4, 3
    gap = 14
    tile_w = (grid_w - gap * (cols - 1)) // cols  # ((1184 - 42) / 4) = ~285
    tile_h = (grid_h - gap * (rows - 1)) // rows  # ((408 - 28) / 3) = ~126

    logos = [
        "ACME CORP", "GLOBEX", "INITECH", "UMBRELLA",
        "WEYLAND", "TYRELL", "STARK", "WAYNE",
        "SOYLENT", "CYBERDYNE", "MASSIVE", "OMNI",
    ]
    featured = {2, 7}  # 1-indexed featured tiles

    for i, label in enumerate(logos):
        n = i + 1
        row = i // cols
        col = i % cols
        tx = grid_left + col * (tile_w + gap)
        ty = grid_top + row * (tile_h + gap)

        is_featured = n in featured
        fill = WHITE if is_featured else CARD_BG
        tile = add_rect(slide, f"logo-{n}-tile", tx, ty, tile_w, tile_h, fill)
        if is_featured:
            tile.line.color.rgb = BRAND_ACCENT
            tile.line.width = 19050  # 2px
            text_color = BRAND_PRIMARY
            bold = True
        else:
            tile.line.color.rgb = CARD_BORDER
            tile.line.width = 9525
            text_color = TEXT_FAINT
            bold = True

        add_text(
            slide, f"logo-{n}-text", label,
            x_px=tx, y_px=ty, w_px=tile_w, h_px=tile_h,
            font_size_px=13, color=text_color, bold=bold,
            align="center", anchor="middle", uppercase=True,
        )

    add_convergence(
        slide,
        "12 practices, 8 industries, 3 continents — common pattern.",
        bottom_px=56, height_px=42,
    )

    add_footer(slide, page_num=76)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "76_logo-wall.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
