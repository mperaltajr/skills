"""
Builder for pattern 330: 6-bucket icon strip.

Horizontal row of 6 narrow cards with icon glyph at top, numbered badge, title, 2 short bullets.

Source HTML: _pattern-library/330_6bucket-icon-strip.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Six capability areas <strong>drive the transformation</strong>",
        subtitle="Each dimension is independently assessed and sequenced for maximum impact",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap = 12
    cols = 6
    card_w = (body_w - (cols - 1) * gap) // cols
    card_h = body_h

    buckets = [
        ("01", "★", "Strategy & Vision",
         ["North-star alignment", "Roadmap sequencing"]),
        ("02", "◆", "Talent & Skills",
         ["Workforce upskilling", "Role re-architecture"]),
        ("03", "▲", "Risk & Control",
         ["Compliance posture", "Residual risk scoring"]),
        ("04", "→", "Speed & Agility",
         ["Delivery velocity", "Cycle-time reduction"]),
        ("05", "⊞", "Operations",
         ["Process automation", "Cost optimisation"]),
        ("06", "✦", "Value & Impact",
         ["Benefit realisation", "KPI governance"]),
    ]
    for i, (num, glyph, title, bullets) in enumerate(buckets):
        n = i + 1
        cx = body_left + i * (card_w + gap)
        card = add_rect(slide, f"bucket-{n}-card", cx, body_top, card_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Icon
        icon_size = 44
        add_icon(slide, f"bucket-{n}-icon",
                 cx + (card_w - icon_size) // 2, body_top + 22, icon_size, glyph,
                 color=BRAND_ACCENT)
        # Number
        add_text(slide, f"bucket-{n}-num", num,
                 x_px=cx, y_px=body_top + 80, w_px=card_w, h_px=18,
                 font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", letter_spacing_px=1.4)
        # Title
        add_text(slide, f"bucket-{n}-title", title,
                 x_px=cx + 10, y_px=body_top + 104, w_px=card_w - 20, h_px=44,
                 font_size_px=13, color=BRAND_PRIMARY, bold=True, align="center")
        # Rule
        rule_w = 36
        add_rect(slide, f"bucket-{n}-rule",
                 cx + (card_w - rule_w) // 2, body_top + 156, rule_w, 2, BRAND_ACCENT)
        # Bullets
        by_text = body_top + 178
        for bi, b in enumerate(bullets):
            bn = bi + 1
            add_text(slide, f"bucket-{n}-bullet-{bn}", b,
                     x_px=cx + 10, y_px=by_text + bi * 38, w_px=card_w - 20, h_px=36,
                     font_size_px=11, color=TEXT_MID, align="center")

    add_footer(slide, page_num=330)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "330_6bucket-icon-strip.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
