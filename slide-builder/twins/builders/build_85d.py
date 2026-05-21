"""
Builder for pattern 85d: Vision, mission, values — tiered pyramid — dark variant.

Source HTML: _pattern-library/85_vision-mission-values-dark.html
Light template: twins/builders/build_85.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
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

    add_text(slide, "title",
             "Vision, mission, values — why Slide Lab exists.",
             x_px=56, y_px=20, w_px=1168, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Three statements, one stack: where we're going, what we do, how we behave.",
             x_px=56, y_px=108, w_px=1048, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 56, 132, 56, 3, BRAND_ACCENT_SOFT)

    # Tiered pyramid stack — pushed down to y=220+
    tier_top = 220
    gap = 8
    label_col_w = 110

    # TIER 1: VISION
    v_w, v_h = 760, 95
    v_x = (1280 - v_w) // 2
    v_y = tier_top
    add_rect(slide, "tier-vision-band", v_x, v_y, v_w, v_h, BRAND_ACCENT)
    add_text(slide, "tier-vision-label", "VISION",
             x_px=v_x + 22, y_px=v_y + 28, w_px=label_col_w - 22, h_px=20,
             font_size_px=11, color=WHITE, bold=True, uppercase=True)
    add_text(slide, "tier-vision-sublabel", "Where we're going",
             x_px=v_x + 22, y_px=v_y + 52, w_px=label_col_w - 22, h_px=14,
             font_size_px=9, color=WHITE, uppercase=True)
    add_rect(slide, "tier-vision-divider",
             v_x + label_col_w, v_y + 16, 1, v_h - 32, WHITE)
    add_text(slide, "tier-vision-statement",
             "“Every consulting deck argued before it's drawn.”",
             x_px=v_x + label_col_w + 26, y_px=v_y, w_px=v_w - label_col_w - 52, h_px=v_h,
             font_size_px=19, color=WHITE, italic=True, bold=True, anchor="middle")

    # TIER 2: MISSION
    m_w, m_h = 940, 115
    m_x = (1280 - m_w) // 2
    m_y = v_y + v_h + gap
    add_rect(slide, "tier-mission-band", m_x, m_y, m_w, m_h, BRAND_PRIMARY_MID)
    add_text(slide, "tier-mission-label", "MISSION",
             x_px=m_x + 22, y_px=m_y + 34, w_px=label_col_w - 22, h_px=20,
             font_size_px=11, color=WHITE, bold=True, uppercase=True)
    add_text(slide, "tier-mission-sublabel", "What we do",
             x_px=m_x + 22, y_px=m_y + 58, w_px=label_col_w - 22, h_px=14,
             font_size_px=9, color=WHITE, uppercase=True)
    add_rect(slide, "tier-mission-divider",
             m_x + label_col_w, m_y + 16, 1, m_h - 32, WHITE)
    add_text(slide, "tier-mission-statement",
             "We make structured thinking the default by giving consultants a tool that locks the argument before the first slide is built — so the deck follows the logic, not the other way around.",
             x_px=m_x + label_col_w + 26, y_px=m_y, w_px=m_w - label_col_w - 52, h_px=m_h,
             font_size_px=14, color=WHITE, anchor="middle")

    # TIER 3: VALUES
    val_w, val_h = 1120, 130
    val_x = (1280 - val_w) // 2
    val_y = m_y + m_h + gap
    band = add_rect(slide, "tier-values-band", val_x, val_y, val_w, val_h, CARD_BG_DARK)
    band.line.color.rgb = CARD_BORDER_DARK
    band.line.width = 14288

    add_text(slide, "tier-values-label", "VALUES",
             x_px=val_x + 22, y_px=val_y + 40, w_px=label_col_w - 22, h_px=20,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "tier-values-sublabel", "How we behave",
             x_px=val_x + 22, y_px=val_y + 64, w_px=label_col_w - 22, h_px=14,
             font_size_px=9, color=TEXT_ON_DARK_MID, uppercase=True)
    add_rect(slide, "tier-values-divider",
             val_x + label_col_w, val_y + 16, 1, val_h - 32, CARD_BORDER_DARK)

    chips = [
        ("Rigor", "Argument before aesthetics"),
        ("Speed", "Hours, not weeks"),
        ("Reusability", "Build once, ship many"),
        ("Internal IP", "Our craft, our edge"),
    ]
    chips_left = val_x + label_col_w + 16
    chips_right = val_x + val_w - 16
    chips_total_w = chips_right - chips_left
    chip_gap = 14
    chip_w = (chips_total_w - chip_gap * 3) // 4
    chip_h = val_h - 32

    for i, (name, desc) in enumerate(chips):
        n = i + 1
        chip_x = chips_left + i * (chip_w + chip_gap)
        chip_y = val_y + 16
        chip = add_rect(slide, f"value-chip-{n}", chip_x, chip_y, chip_w, chip_h, BRAND_PRIMARY_MID)
        chip.line.color.rgb = BRAND_ACCENT_SOFT
        chip.line.width = 14288

        add_rect(slide, f"value-chip-{n}-icon",
                 chip_x + (chip_w - 24) // 2, chip_y + 14, 24, 24, BRAND_ACCENT_SOFT)

        add_text(slide, f"value-chip-{n}-name", name,
                 x_px=chip_x, y_px=chip_y + 44, w_px=chip_w, h_px=20,
                 font_size_px=12, color=WHITE, bold=True,
                 align="center", uppercase=True)
        add_text(slide, f"value-chip-{n}-desc", desc,
                 x_px=chip_x + 4, y_px=chip_y + 66, w_px=chip_w - 8, h_px=32,
                 font_size_px=10, color=TEXT_ON_DARK_MID, align="center")

    add_text(slide, "convergence",
             "The stack reads top-down: vision sets the destination, mission names the work, values govern how the work gets done.",
             x_px=56, y_px=720 - 64, w_px=1280 - 112, h_px=22,
             font_size_px=12, color=BRAND_ACCENT_SOFT, italic=True, align="center")

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "85",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "85d_vision-mission-values-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
