"""
Builder for pattern 97: Mission statement slide (hero pattern, light variant).

Source HTML: _pattern-library/97_mission-statement-slide.html

Pure hero (per spec). No standard title block — just a small action title +
brand-rule chrome at top, then a centered stage with hero-statement, hero-rule,
and two sub-points (by / measured by).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    CARD_BORDER, TEXT_DARK,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Compact action title + brand rule (no subtitle)
    add_text(slide, "title",
             "Our mission — sharp thinking, every time.",
             x_px=56, y_px=58, w_px=1168, h_px=40,
             font_size_px=26, color=TEXT_DARK, bold=True)
    add_rect(slide, "brand-rule", 56, 110, 56, 3, BRAND_ACCENT)

    # Centered hero stage — top:170 bottom:80
    stage_top = 170
    stage_bot = 720 - 80
    stage_h = stage_bot - stage_top  # 470
    stage_x = 56
    stage_w = 1280 - 112

    # Pre-label
    pre_y = stage_top + 80
    add_text(slide, "hero-statement-label", "OUR MISSION",
             x_px=stage_x, y_px=pre_y, w_px=stage_w, h_px=18,
             font_size_px=12, color=BRAND_ACCENT, bold=True,
             align="center", uppercase=True)

    # Hero statement (big brand-primary)
    add_text(slide, "hero-statement",
             "Make structured thinking the default for every consulting deck.",
             x_px=stage_x + 80, y_px=pre_y + 50, w_px=stage_w - 160, h_px=160,
             font_size_px=48, color=BRAND_PRIMARY, align="center", bold=False)

    # Hero rule (centered)
    add_rect(slide, "hero-rule",
             (1280 - 120) // 2, pre_y + 230, 120, 3, BRAND_ACCENT)

    # Sub-points row
    sub_y = pre_y + 274
    sub_block_w = 980
    sub_block_x = (1280 - sub_block_w) // 2
    half_w = (sub_block_w - 64) // 2  # gap 64

    # Left sub-point
    add_text(slide, "hero-sub-1-label", "WE DO THIS BY",
             x_px=sub_block_x, y_px=sub_y, w_px=half_w, h_px=14,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "hero-sub-1-text",
             "Locking the argument in a coached storyline session before any slide is built.",
             x_px=sub_block_x, y_px=sub_y + 22, w_px=half_w, h_px=60,
             font_size_px=14, color=TEXT_DARK, bold=True)

    # Divider line
    add_rect(slide, "hero-sub-divider",
             sub_block_x + half_w + 32, sub_y, 1, 80, CARD_BORDER)

    # Right sub-point
    right_x = sub_block_x + half_w + 64
    add_text(slide, "hero-sub-2-label", "WE MEASURE IT BY",
             x_px=right_x, y_px=sub_y, w_px=half_w, h_px=14,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "hero-sub-2-text",
             "Deck cycle time and first-review partner sign-off rate.",
             x_px=right_x, y_px=sub_y + 22, w_px=half_w, h_px=60,
             font_size_px=14, color=TEXT_DARK, bold=True)

    add_footer(slide, page_num=97)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "97_mission-statement-slide.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
