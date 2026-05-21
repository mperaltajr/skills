"""
Builder for pattern 47: Strategy house — roof + two pillars + foundation.

Source HTML: _pattern-library/47_strategy-house.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Inline title block — title font reduced to 28 so 2-line wrap fits;
    # subtitle and brand-rule positioned below to avoid overlap with the house.
    add_text(
        slide, "title",
        "Our approach rests on two pillars supporting one integrated outcome — remove either pillar and the house falls.",
        x_px=64, y_px=50, w_px=1000, h_px=82,
        font_size_px=28, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Roof = the outcome we are committing to. Pillars = the two mutually-reinforcing prongs. Foundation = what happens without both.",
        x_px=64, y_px=144, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=178, w_px=48, h_px=3, fill_color=BRAND_ACCENT)

    # House canvas — centered 880x360 at top=190
    house_left = (1280 - 880) // 2  # 200
    house_top = 190

    # Roof: triangle approximated as rectangle on top of the pillars (no triangle clip in PPTX)
    # We'll render as a brand-primary band with the outcome text
    roof_left = house_left + 80
    roof_w = 880 - 160  # 720
    add_rect(slide, "roof", roof_left, house_top, roof_w, 88, BRAND_PRIMARY)
    add_text(
        slide, "roof-label", "INTEGRATED OUTCOME",
        x_px=roof_left, y_px=house_top + 14, w_px=roof_w, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True,
    )
    add_text(
        slide, "roof-name", "Durable advantage — new and expanded opportunities",
        x_px=roof_left, y_px=house_top + 36, w_px=roof_w, h_px=42,
        font_size_px=14, color=WHITE, bold=True, align="center",
    )

    # Pillars at top=house_top+100, height 180
    pillars_top = house_top + 100
    pillar_h = 180
    pillar_gap = 18
    pillar_w = (880 - 16 - pillar_gap) // 2  # ~423
    # left padding 8 on each side
    pillar_left_x = house_left + 8

    pillar_data = [
        ("Pillar 1", "Mindset shift", "How we think and operate",
         BRAND_PRIMARY,
         [("Moves us from a delivery mindset to a value mindset"),
          ("Frames problems and engages at the right level"),
          ("Builds trusted relationships that produce influence")]),
        ("Pillar 2", "Ops intelligence engine", "What we know and deliver",
         BRAND_ACCENT,
         [("Builds deep understanding of how the business actually works"),
          ("Quantifies and captures value at decision time"),
          ("Generates insights that earn credibility")]),
    ]

    for i, (tag, name, sub, color, bullets) in enumerate(pillar_data):
        n = i + 1
        px = pillar_left_x + i * (pillar_w + pillar_gap)

        # Pillar top header band
        head_h = 64
        add_rect(slide, f"pillar-{n}-header", px, pillars_top, pillar_w, head_h, color)
        add_text(
            slide, f"pillar-{n}-tag", tag.upper(),
            x_px=px, y_px=pillars_top + 8, w_px=pillar_w, h_px=12,
            font_size_px=10, color=WHITE, bold=True, align="center", uppercase=True,
        )
        add_text(
            slide, f"pillar-{n}-name", name,
            x_px=px, y_px=pillars_top + 22, w_px=pillar_w, h_px=22,
            font_size_px=16, color=WHITE, bold=True, align="center",
        )
        add_text(
            slide, f"pillar-{n}-sub", sub,
            x_px=px, y_px=pillars_top + 46, w_px=pillar_w, h_px=14,
            font_size_px=10, color=WHITE, align="center",
        )

        # Pillar body
        body_y = pillars_top + head_h
        body_h = pillar_h - head_h
        body = add_rect(slide, f"pillar-{n}-body", px, body_y, pillar_w, body_h, WHITE)
        body.line.color.rgb = color
        body.line.width = 25400  # ~2px

        # Bullets
        for bi, btxt in enumerate(bullets):
            bn = bi + 1
            row_y = body_y + 12 + bi * 32
            add_text(
                slide, f"pillar-{n}-bullet-{bn}-num", str(bn),
                x_px=px + 14, y_px=row_y, w_px=20, h_px=20,
                font_size_px=10, color=WHITE, bold=True, align="center",
                bg_fill=color,
            )
            add_text(
                slide, f"pillar-{n}-bullet-{bn}-text", btxt,
                x_px=px + 42, y_px=row_y, w_px=pillar_w - 56, h_px=28,
                font_size_px=11, color=TEXT_DARK,
            )

    # Foundation bar at bottom of house — height 70
    foundation_y = house_top + 360 - 70  # 480
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

    add_footer(slide, page_num=47)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "47_strategy-house.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
