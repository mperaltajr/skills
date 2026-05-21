"""
Builder for pattern 77: Multi-image grid with captions (3x2 = 6 cards).

Source HTML: _pattern-library/77_multi-image-grid.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

IMAGE_BG = RGBColor(0xF1, 0xF5, 0xF9)
IMAGE_BORDER = RGBColor(0xCB, 0xD5, 0xE1)
FEATURED_BG = RGBColor(0xFA, 0xF5, 0xFF)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Pilot deck galleries — six pages, six redos.",
        subtitle="Side-by-side before and after for the three slides reviewers flagged hardest. One redo carries the deck.",
        title_h=60,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Grid 3 cols x 2 rows. left:64, right:64, top:178, bottom:132
    grid_left = 64
    grid_top = 178
    grid_right = 1280 - 64
    grid_bot = 720 - 132
    grid_w = grid_right - grid_left  # 1152
    grid_h = grid_bot - grid_top  # 410
    gap = 18
    card_w = (grid_w - gap * 2) // 3  # 372
    card_h = (grid_h - gap) // 2  # 196

    items = [
        ("SLIDE 2 · BEFORE", "[ Wall-of-bullets layout, no visual hierarchy ]",
         "Slide 2 — Before", "Wall of bullets, no structure.", False),
        ("SLIDE 2 · AFTER", "[ Anchor statement with three supporting cards ]",
         "Slide 2 — After", "Anchor + three cards.", False),
        ("SLIDE 5 · BEFORE", "[ Three-column table, undifferentiated rows ]",
         "Slide 5 — Before", "3-col table, no story.", False),
        ("SLIDE 5 · AFTER", "[ Three vertical pillars, headline-first logic ]",
         "Slide 5 — After", "Vertical pillars, clear logic.", True),
        ("SLIDE 7 · BEFORE", "[ Generic ask slide, mixed formats ]",
         "Slide 7 — Before", "Generic ask, generic format.", False),
        ("SLIDE 7 · AFTER", "[ Single focal-point ask, isolated on slide ]",
         "Slide 7 — After", "Single focal point ask.", False),
    ]

    for i, (corner, label, cap_head, cap_desc, featured) in enumerate(items):
        n = i + 1
        row = i // 3
        col = i % 3
        cx = grid_left + col * (card_w + gap)
        cy = grid_top + row * (card_h + gap)

        # Card body
        card_fill = WHITE if featured else CARD_BG
        card = add_rect(slide, f"photo-{n}-card", cx, cy, card_w, card_h, card_fill)
        if featured:
            card.line.color.rgb = BRAND_ACCENT
            card.line.width = 19050  # 2px
        else:
            card.line.color.rgb = CARD_BORDER
            card.line.width = 9525

        # Image zone (top portion of card)
        img_x = cx + 10
        img_y = cy + 10
        img_w = card_w - 20
        img_h = card_h - 70  # leave room for caption
        zone_fill = FEATURED_BG if featured else IMAGE_BG
        zone = add_rect(slide, f"photo-{n}-zone", img_x, img_y, img_w, img_h, zone_fill)
        zone.line.color.rgb = BRAND_ACCENT_SOFT if featured else IMAGE_BORDER
        zone.line.width = 14288  # 1.5px

        # Image corner tag
        add_text(
            slide, f"photo-{n}-corner-tag", corner,
            x_px=img_x + 8, y_px=img_y + 6, w_px=160, h_px=18,
            font_size_px=9, color=WHITE if featured else BRAND_ACCENT, bold=True,
            bg_fill=BRAND_ACCENT if featured else WHITE,
            padding_px=(2, 6, 2, 6),
        )

        # Featured flag
        if featured:
            add_text(
                slide, f"photo-{n}-featured-flag", "FEATURED",
                x_px=img_x + img_w - 78, y_px=img_y + 6, w_px=70, h_px=18,
                font_size_px=9, color=WHITE, bold=True, align="center",
                bg_fill=BRAND_ACCENT, padding_px=(2, 6, 2, 6),
            )

        # Image label (centered in zone)
        add_text(
            slide, f"photo-{n}-label", label,
            x_px=img_x, y_px=img_y, w_px=img_w, h_px=img_h,
            font_size_px=11, color=TEXT_FAINT, bold=True,
            align="center", anchor="middle",
        )

        # Caption head + desc
        cap_y = img_y + img_h + 10
        add_text(
            slide, f"photo-{n}-caption", cap_head,
            x_px=cx + 12, y_px=cap_y, w_px=card_w - 24, h_px=18,
            font_size_px=12, color=BRAND_PRIMARY, bold=True,
        )
        add_text(
            slide, f"photo-{n}-caption-desc", cap_desc,
            x_px=cx + 12, y_px=cap_y + 20, w_px=card_w - 24, h_px=18,
            font_size_px=11, color=TEXT_MID,
        )

    # Convergence with left-accent border
    add_convergence(
        slide,
        "Slide 5 is the one that flipped the room — pillars beat tables when the audience has to repeat the argument later.",
        bottom_px=70, height_px=46,
    )
    add_rect(slide, "convergence-accent", 64, 720 - 70 - 46, 4, 46, BRAND_ACCENT)

    add_footer(slide, page_num=77)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "77_multi-image-grid.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
