"""
Builder for pattern 316: 3-bucket horizontal cards.

Bucket family treatment: card with bucket number (01/02/03), title, bullets, and
a large metric. Three cards side-by-side.

Source HTML: _pattern-library/316_3bucket-horizontal-cards.html
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


def _bucket_card(slide, n, x, y, w, h, *, num, title, bullets, metric, metric_label,
                 metric_color):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG)
    card.line.color.rgb = CARD_BORDER
    card.line.width = 9525
    # Top accent strip
    add_rect(slide, f"bucket-{n}-accent", x, y, w, 4, BRAND_ACCENT)
    # Number
    add_text(
        slide, f"bucket-{n}-num", num,
        x_px=x + 24, y_px=y + 22, w_px=80, h_px=28,
        font_size_px=24, color=BRAND_ACCENT_SOFT, bold=True,
    )
    # Title
    add_text(
        slide, f"bucket-{n}-title", title,
        x_px=x + 24, y_px=y + 56, w_px=w - 48, h_px=44,
        font_size_px=15, color=BRAND_PRIMARY, bold=True,
    )
    # Rule under title
    add_rect(slide, f"bucket-{n}-rule", x + 24, y + 104, 40, 2, BRAND_ACCENT)
    # Bullets
    bullets_y = y + 122
    for bi, b in enumerate(bullets):
        bn = bi + 1
        by = bullets_y + bi * 40
        add_text(
            slide, f"bucket-{n}-bullet-{bn}-dash", "–",
            x_px=x + 24, y_px=by, w_px=12, h_px=20,
            font_size_px=12, color=TEXT_FAINT,
        )
        add_text(
            slide, f"bucket-{n}-bullet-{bn}-text", b,
            x_px=x + 38, y_px=by, w_px=w - 60, h_px=38,
            font_size_px=11, color=TEXT_MID,
        )
    # Metric
    metric_y = y + h - 70
    add_text(
        slide, f"bucket-{n}-metric", metric,
        x_px=x + 24, y_px=metric_y, w_px=w - 48, h_px=36,
        font_size_px=28, color=metric_color, bold=True,
    )
    add_text(
        slide, f"bucket-{n}-metric-label", metric_label.upper(),
        x_px=x + 24, y_px=metric_y + 38, w_px=w - 48, h_px=14,
        font_size_px=10, color=TEXT_FAINT, letter_spacing_px=1.2,
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Three levers drive <strong>sustained margin expansion</strong>",
        subtitle="Priority focus areas for Q3–Q4 execution across the portfolio",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap = 18
    card_w = (body_w - 2 * gap) // 3

    buckets = [
        ("01", "Cost Structure Optimisation",
         ["Consolidate tier-2 vendor roster from 47 to 18 strategic partners",
          "Migrate 60% of on-prem workloads to managed cloud by Q4",
          "Standardise procurement across BUs to unlock volume rebates",
          "Automate AP/AR reconciliation — 80% straight-through processing"],
         "$42M", "Identified savings potential", BRAND_PRIMARY),
        ("02", "Revenue Mix Improvement",
         ["Shift product revenue toward higher-margin SaaS subscription tiers",
          "Expand managed services attach rate from 31% to 55% by year-end",
          "Retire tail SKUs representing <2% revenue but 18% support load",
          "Re-price legacy contracts at renewal using updated benchmarks"],
         "+8.4pp", "Gross margin uplift target", BRAND_PRIMARY_MID),
        ("03", "Operational Velocity",
         ["Reduce quote-to-cash cycle from 22 days to under 9 days",
          "Deploy AI-assisted demand forecasting to cut excess inventory 35%",
          "Implement unified delivery dashboard across all regional teams",
          "Establish bi-weekly leadership cadence on leading indicators"],
         "2.1×", "Throughput improvement target", BRAND_ACCENT),
    ]
    for i, (num, title, bullets, metric, lbl, mcolor) in enumerate(buckets):
        n = i + 1
        cx = body_left + i * (card_w + gap)
        _bucket_card(
            slide, n, cx, body_top, card_w, body_h,
            num=num, title=title, bullets=bullets,
            metric=metric, metric_label=lbl, metric_color=mcolor,
        )

    add_footer(slide, page_num=316)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "316_3bucket-horizontal-cards.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
