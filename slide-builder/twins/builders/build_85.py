"""
Builder for pattern 85: Vision, mission, values — tiered pyramid (3 widths).

Source HTML: _pattern-library/85_vision-mission-values.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Vision, mission, values — why Slide Lab exists.",
        subtitle="Three statements, one stack: where we're going, what we do, how we behave.",
        title_x=56, title_w=1168, title_h=60,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Tiered pyramid stack — widths 760 / 940 / 1120, all centered. Top:170.
    tier_top = 170
    gap = 10
    label_col_w = 110

    # ---- TIER 1: VISION (top, narrowest, brand-accent) ----
    v_w, v_h = 760, 100
    v_x = (1280 - v_w) // 2
    v_y = tier_top
    add_rect(slide, "tier-vision-band", v_x, v_y, v_w, v_h, BRAND_ACCENT)
    # Vision label
    add_text(slide, "tier-vision-label", "VISION",
             x_px=v_x + 22, y_px=v_y + 30, w_px=label_col_w - 22, h_px=20,
             font_size_px=11, color=WHITE, bold=True, uppercase=True)
    add_text(slide, "tier-vision-sublabel", "Where we're going",
             x_px=v_x + 22, y_px=v_y + 54, w_px=label_col_w - 22, h_px=14,
             font_size_px=9, color=WHITE, uppercase=True)
    # Divider line between label and statement
    add_rect(slide, "tier-vision-divider",
             v_x + label_col_w, v_y + 16, 1, v_h - 32, WHITE)
    # Statement
    add_text(
        slide, "tier-vision-statement",
        "“Every consulting deck argued before it's drawn.”",
        x_px=v_x + label_col_w + 26, y_px=v_y, w_px=v_w - label_col_w - 52, h_px=v_h,
        font_size_px=19, color=WHITE, italic=True, bold=True, anchor="middle",
    )

    # ---- TIER 2: MISSION (middle, wider, brand-primary) ----
    m_w, m_h = 940, 120
    m_x = (1280 - m_w) // 2
    m_y = v_y + v_h + gap
    add_rect(slide, "tier-mission-band", m_x, m_y, m_w, m_h, BRAND_PRIMARY)
    add_text(slide, "tier-mission-label", "MISSION",
             x_px=m_x + 22, y_px=m_y + 36, w_px=label_col_w - 22, h_px=20,
             font_size_px=11, color=WHITE, bold=True, uppercase=True)
    add_text(slide, "tier-mission-sublabel", "What we do",
             x_px=m_x + 22, y_px=m_y + 60, w_px=label_col_w - 22, h_px=14,
             font_size_px=9, color=WHITE, uppercase=True)
    add_rect(slide, "tier-mission-divider",
             m_x + label_col_w, m_y + 16, 1, m_h - 32, WHITE)
    add_text(
        slide, "tier-mission-statement",
        "We make structured thinking the default by giving consultants a tool that locks the argument before the first slide is built — so the deck follows the logic, not the other way around.",
        x_px=m_x + label_col_w + 26, y_px=m_y, w_px=m_w - label_col_w - 52, h_px=m_h,
        font_size_px=14, color=WHITE, anchor="middle",
    )

    # ---- TIER 3: VALUES (base, widest, light card with chips) ----
    val_w, val_h = 1120, 130
    val_x = (1280 - val_w) // 2
    val_y = m_y + m_h + gap
    band = add_rect(slide, "tier-values-band", val_x, val_y, val_w, val_h, CARD_BG)
    band.line.color.rgb = CARD_BORDER
    band.line.width = 14288  # 1.5px

    add_text(slide, "tier-values-label", "VALUES",
             x_px=val_x + 22, y_px=val_y + 40, w_px=label_col_w - 22, h_px=20,
             font_size_px=11, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_text(slide, "tier-values-sublabel", "How we behave",
             x_px=val_x + 22, y_px=val_y + 64, w_px=label_col_w - 22, h_px=14,
             font_size_px=9, color=TEXT_MID, uppercase=True)
    add_rect(slide, "tier-values-divider",
             val_x + label_col_w, val_y + 16, 1, val_h - 32, CARD_BORDER)

    # 4 value chips
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
        chip = add_rect(slide, f"value-chip-{n}", chip_x, chip_y, chip_w, chip_h, WHITE)
        chip.line.color.rgb = BRAND_ACCENT_SOFT
        chip.line.width = 14288

        # Icon placeholder (top center)
        add_rect(slide, f"value-chip-{n}-icon",
                 chip_x + (chip_w - 24) // 2, chip_y + 14, 24, 24, BRAND_ACCENT)

        # Name
        add_text(slide, f"value-chip-{n}-name", name,
                 x_px=chip_x, y_px=chip_y + 44, w_px=chip_w, h_px=20,
                 font_size_px=12, color=BRAND_PRIMARY, bold=True,
                 align="center", uppercase=True)
        # Description
        add_text(slide, f"value-chip-{n}-desc", desc,
                 x_px=chip_x + 4, y_px=chip_y + 66, w_px=chip_w - 8, h_px=32,
                 font_size_px=10, color=TEXT_MID, align="center")

    # Convergence — centered italic note above footer rule
    add_text(
        slide, "convergence",
        "The stack reads top-down: vision sets the destination, mission names the work, values govern how the work gets done.",
        x_px=56, y_px=720 - 64, w_px=1280 - 112, h_px=22,
        font_size_px=12, color=BRAND_PRIMARY, italic=True, align="center",
    )

    add_footer(slide, page_num=85)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "85_vision-mission-values.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
