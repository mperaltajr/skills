"""
Builder for pattern 321: 4-bucket horizontal strip.

Four bucket cards side-by-side, each with ghost number background + bucket title +
bullets + stat with label.

Source HTML: _pattern-library/321_4bucket-horizontal-strip.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def _bucket_card(slide, n, x, y, w, h, *, num, title, bullets, stat, stat_label):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG)
    card.line.color.rgb = CARD_BORDER
    card.line.width = 9525
    # Ghost number (large pale)
    add_text(
        slide, f"bucket-{n}-ghost", num,
        x_px=x + 14, y_px=y + 8, w_px=80, h_px=58,
        font_size_px=58, color=BRAND_ACCENT_SOFT, bold=True,
    )
    # Visible number small badge
    add_text(
        slide, f"bucket-{n}-num", num,
        x_px=x + w - 50, y_px=y + 14, w_px=36, h_px=18,
        font_size_px=11, color=BRAND_ACCENT, bold=True, align="right",
        letter_spacing_px=1.0,
    )
    # Title
    add_text(
        slide, f"bucket-{n}-title", title,
        x_px=x + 14, y_px=y + 76, w_px=w - 28, h_px=42,
        font_size_px=15, color=BRAND_PRIMARY, bold=True,
    )
    # Rule
    add_rect(slide, f"bucket-{n}-rule", x + 14, y + 124, w - 28, 3, BRAND_ACCENT)
    # Bullets
    bullets_y = y + 142
    for bi, b in enumerate(bullets):
        bn = bi + 1
        by = bullets_y + bi * 42
        add_rect(slide, f"bucket-{n}-bullet-{bn}-dot",
                 x + 14, by + 7, 5, 5, BRAND_ACCENT_SOFT)
        add_text(
            slide, f"bucket-{n}-bullet-{bn}-text", b,
            x_px=x + 26, y_px=by, w_px=w - 40, h_px=40,
            font_size_px=11, color=TEXT_MID,
        )
    # Stat
    stat_y = y + h - 60
    add_text(
        slide, f"bucket-{n}-stat", stat,
        x_px=x + 14, y_px=stat_y, w_px=w - 28, h_px=30,
        font_size_px=24, color=BRAND_ACCENT, bold=True,
    )
    add_text(
        slide, f"bucket-{n}-stat-label", stat_label.upper(),
        x_px=x + 14, y_px=stat_y + 30, w_px=w - 28, h_px=14,
        font_size_px=9, color=TEXT_FAINT, letter_spacing_px=1.2,
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Four pillars driving <strong>sustainable growth</strong> in 2026",
        subtitle="Each dimension reflects a distinct lever with measurable outcomes and clear ownership",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap = 12
    card_w = (body_w - 3 * gap) // 4

    buckets = [
        ("01", "Market Expansion",
         ["Enter three new geographic corridors by Q3",
          "Leverage existing channel partner network",
          "Localise go-to-market playbook per segment"],
         "+34%", "Addressable reach"),
        ("02", "Product Velocity",
         ["Reduce release cycle from 8 weeks to 3",
          "Ship modular feature sets for faster adoption",
          "Implement continuous deployment pipeline"],
         "3×", "Faster time-to-market"),
        ("03", "Talent & Culture",
         ["Upskill 60% of workforce in AI-adjacent roles",
          "Introduce structured cross-functional rotations",
          "Tie performance KPIs to innovation outcomes"],
         "↑18 pts", "Engagement score"),
        ("04", "Operational Efficiency",
         ["Automate 40% of repetitive back-office tasks",
          "Consolidate vendor portfolio by 25% in year one",
          "Standardise reporting across all business units"],
         "$12M", "Projected annual savings"),
    ]
    for i, (num, title, bullets, stat, stat_label) in enumerate(buckets):
        n = i + 1
        cx = body_left + i * (card_w + gap)
        _bucket_card(
            slide, n, cx, body_top, card_w, body_h,
            num=num, title=title, bullets=bullets, stat=stat, stat_label=stat_label,
        )

    add_footer(slide, page_num=321)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "321_4bucket-horizontal-strip.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
