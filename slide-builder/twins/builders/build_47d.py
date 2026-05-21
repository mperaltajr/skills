"""
Dark variant of pattern 47: Strategy house.

Source HTML: _pattern-library/47_strategy-house-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Our approach rests on two pillars supporting one integrated outcome — remove either pillar and the house falls.",
        x_px=64, y_px=50, w_px=1000, h_px=82,
        font_size_px=28, color=WHITE, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Roof = the outcome we are committing to. Pillars = the two mutually-reinforcing prongs. Foundation = what happens without both.",
        x_px=64, y_px=144, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=178, w_px=48, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    house_left = (1280 - 880) // 2
    house_top = 190

    # Roof — brand-accent-soft band on dark bg, text dark for contrast
    roof_left = house_left + 80
    roof_w = 880 - 160
    add_rect(slide, "roof", roof_left, house_top, roof_w, 88, BRAND_ACCENT_SOFT)
    add_text(
        slide, "roof-label", "INTEGRATED OUTCOME",
        x_px=roof_left, y_px=house_top + 14, w_px=roof_w, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True, align="center", uppercase=True,
    )
    add_text(
        slide, "roof-name", "Durable advantage — new and expanded opportunities",
        x_px=roof_left, y_px=house_top + 36, w_px=roof_w, h_px=42,
        font_size_px=14, color=BRAND_PRIMARY, bold=True, align="center",
    )

    pillars_top = house_top + 100
    pillar_h = 180
    pillar_gap = 18
    pillar_w = (880 - 16 - pillar_gap) // 2
    pillar_left_x = house_left + 8

    # In dark mode pillars use brand-accent and brand-primary-mid as accents
    pillar_data = [
        ("Pillar 1", "Mindset shift", "How we think and operate",
         BRAND_PRIMARY_MID,
         [("Moves us from a delivery mindset to a value mindset"),
          ("Frames problems and engages at the right level"),
          ("Builds trusted relationships that produce influence")]),
        ("Pillar 2", "Ops intelligence engine", "What we know and deliver",
         BRAND_ACCENT_SOFT,
         [("Builds deep understanding of how the business actually works"),
          ("Quantifies and captures value at decision time"),
          ("Generates insights that earn credibility")]),
    ]

    for i, (tag, name, sub, color, bullets) in enumerate(pillar_data):
        n = i + 1
        px = pillar_left_x + i * (pillar_w + pillar_gap)
        is_light_head = (color == BRAND_ACCENT_SOFT)

        head_h = 64
        add_rect(slide, f"pillar-{n}-header", px, pillars_top, pillar_w, head_h, color)
        head_text_color = BRAND_PRIMARY if is_light_head else WHITE
        add_text(
            slide, f"pillar-{n}-tag", tag.upper(),
            x_px=px, y_px=pillars_top + 8, w_px=pillar_w, h_px=12,
            font_size_px=10, color=head_text_color, bold=True, align="center", uppercase=True,
        )
        add_text(
            slide, f"pillar-{n}-name", name,
            x_px=px, y_px=pillars_top + 22, w_px=pillar_w, h_px=22,
            font_size_px=16, color=head_text_color, bold=True, align="center",
        )
        add_text(
            slide, f"pillar-{n}-sub", sub,
            x_px=px, y_px=pillars_top + 46, w_px=pillar_w, h_px=14,
            font_size_px=10, color=head_text_color, align="center",
        )

        body_y = pillars_top + head_h
        body_h = pillar_h - head_h
        body = add_rect(slide, f"pillar-{n}-body", px, body_y, pillar_w, body_h, CARD_BG_DARK)
        body.line.color.rgb = color
        body.line.width = 25400

        for bi, btxt in enumerate(bullets):
            bn = bi + 1
            row_y = body_y + 12 + bi * 32
            add_text(
                slide, f"pillar-{n}-bullet-{bn}-num", str(bn),
                x_px=px + 14, y_px=row_y, w_px=20, h_px=20,
                font_size_px=10, color=head_text_color, bold=True, align="center",
                bg_fill=color,
            )
            add_text(
                slide, f"pillar-{n}-bullet-{bn}-text", btxt,
                x_px=px + 42, y_px=row_y, w_px=pillar_w - 56, h_px=28,
                font_size_px=11, color=WHITE,
            )

    foundation_y = house_top + 360 - 70
    add_rect(slide, "foundation", house_left, foundation_y, 880, 70, BRAND_PRIMARY_MID)
    add_text(
        slide, "foundation-label", "THE FOUNDATION — WITHOUT BOTH",
        x_px=house_left + 22, y_px=foundation_y + 10, w_px=880 - 44, h_px=12,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "foundation-name", "We leave value on the table",
        x_px=house_left + 22, y_px=foundation_y + 24, w_px=880 - 44, h_px=18,
        font_size_px=14, color=WHITE, bold=True,
    )
    add_text(
        slide, "foundation-desc",
        "One prong alone gets halfway: smart assets that nobody uses, or confident people without substance. "
        "Both together = credibility plus influence.",
        x_px=house_left + 22, y_px=foundation_y + 44, w_px=880 - 44, h_px=24,
        font_size_px=11, color=WHITE,
    )

    add_convergence(
        slide,
        "Two pillars, one roof, one foundation — the house only stands if both prongs hold.",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(
        slide, "source", "Source: [add source here or delete]",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
    )
    add_text(
        slide, "page-number", "47",
        x_px=1170, y_px=688, w_px=52, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right",
    )
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "47d_strategy-house.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
