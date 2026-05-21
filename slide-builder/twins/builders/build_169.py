"""
Builder for pattern 169: Recognition Hall of Fame — 3 large + 4 small person cards.

Source HTML: _pattern-library/169_recognition-hall-of-fame.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

GOLD = RGBColor(0xB8, 0x86, 0x0B)
AVATAR_BG = RGBColor(0xD4, 0xC5, 0xE8)


def _avatar(slide, shape_id, x, y, size, initials):
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                     px_to_emu(x), px_to_emu(y),
                                     px_to_emu(size), px_to_emu(size))
    circle.name = shape_id + "-bg"
    circle.fill.solid()
    circle.fill.fore_color.rgb = AVATAR_BG
    circle.line.fill.background()
    add_text(slide, shape_id, initials,
             x_px=x, y_px=y, w_px=size, h_px=size,
             font_size_px=int(size * 0.32), color=BRAND_PRIMARY_MID, bold=True,
             align="center", anchor="middle")


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Celebrating Our <strong>Outstanding Performers</strong>",
        subtitle="Recognizing individuals who exemplify excellence, innovation, and impact across the organization.",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

    top_data = [
        ("JR", "Jamie Rodriguez", "Senior Manager, Strategy & Consulting", "Employee of the Quarter — Q1 2026"),
        ("TN", "Tariq Nkosi", "Principal Architect, Cloud Engineering", "Innovation Award — Client Impact"),
        ("SP", "Sunita Patel", "Director, People & Change", "Leadership Excellence — 2026"),
    ]
    bot_data = [
        ("MK", "Maya Kim", "Tech Lead, Data & AI", "Rising Star — Q1 2026"),
        ("LB", "Luca Bianchi", "Analyst, Finance Transformation", "Client Commendation"),
        ("AO", "Amara Osei", "Manager, Digital Products", "Delivery Excellence Award"),
        ("DW", "Dana Walsh", "Consultant, Sustainability", "Community Impact — 2026"),
    ]

    grid_left = 48
    grid_w = 1280 - 96
    grid_top = 156

    # Top row — 3 large cards
    row1_h = 260
    gap = 14
    card_w_top = (grid_w - 2 * gap) // 3
    for i, (ini, name, role, note) in enumerate(top_data):
        n = i + 1
        cx = grid_left + i * (card_w_top + gap)
        card = add_rect(slide, f"person-{n}-card", cx, grid_top, card_w_top, row1_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        add_rect(slide, f"person-{n}-accent", cx, grid_top, 4, row1_h, GOLD)
        # Avatar centered horizontally
        avatar_size = 64
        _avatar(slide, f"person-{n}-avatar",
                cx + (card_w_top - avatar_size) // 2, grid_top + 30, avatar_size, ini)
        add_text(slide, f"person-{n}-name", name,
                 cx + 12, grid_top + 108, card_w_top - 24, 22,
                 font_size_px=15, color=TEXT_DARK, bold=True, align="center")
        add_text(slide, f"person-{n}-role", role,
                 cx + 12, grid_top + 134, card_w_top - 24, 36,
                 font_size_px=12, color=TEXT_MID, align="center")
        add_text(slide, f"person-{n}-note", note,
                 cx + 12, grid_top + 188, card_w_top - 24, 36,
                 font_size_px=11, color=TEXT_FAINT, italic=True, align="center")

    # Divider
    div_y = grid_top + row1_h + 14
    add_rect(slide, "row-divider", grid_left, div_y, grid_w, 2, BRAND_ACCENT)

    # Bottom row — 4 small cards
    row2_top = div_y + 24
    row2_h = 205
    card_w_bot = (grid_w - 3 * gap) // 4
    for i, (ini, name, role, note) in enumerate(bot_data):
        n = i + 4
        cx = grid_left + i * (card_w_bot + gap)
        card = add_rect(slide, f"person-{n}-card", cx, row2_top, card_w_bot, row2_h, WHITE)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        avatar_size = 52
        _avatar(slide, f"person-{n}-avatar",
                cx + (card_w_bot - avatar_size) // 2, row2_top + 20, avatar_size, ini)
        add_text(slide, f"person-{n}-name", name,
                 cx + 8, row2_top + 84, card_w_bot - 16, 20,
                 font_size_px=13, color=TEXT_DARK, bold=True, align="center")
        add_text(slide, f"person-{n}-role", role,
                 cx + 8, row2_top + 108, card_w_bot - 16, 32,
                 font_size_px=11, color=TEXT_MID, align="center")
        add_text(slide, f"person-{n}-note", note,
                 cx + 8, row2_top + 152, card_w_bot - 16, 34,
                 font_size_px=10, color=TEXT_FAINT, italic=True, align="center")

    add_footer(slide, page_num=169)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "169_recognition-hall-of-fame.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
