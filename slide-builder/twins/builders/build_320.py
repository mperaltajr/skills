"""
Builder for pattern 320: 4-bucket 2×2 grid.

Four numbered bucket cards arranged 2×2. First card is accent-highlighted.

Source HTML: _pattern-library/320_4bucket-2x2-grid.html
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


def _bucket_card(slide, n, x, y, w, h, *, num, title, bullets, chip, accented):
    fill = WHITE if accented else CARD_BG
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, fill)
    card.line.color.rgb = BRAND_ACCENT if accented else CARD_BORDER
    card.line.width = 19050 if accented else 9525
    # Number
    add_text(
        slide, f"bucket-{n}-num", num,
        x_px=x + 22, y_px=y + 14, w_px=60, h_px=28,
        font_size_px=22, color=BRAND_ACCENT_SOFT, bold=True,
    )
    # Title
    add_text(
        slide, f"bucket-{n}-title", title,
        x_px=x + 22, y_px=y + 46, w_px=w - 44, h_px=24,
        font_size_px=14, color=BRAND_PRIMARY, bold=True,
    )
    # Rule
    add_rect(slide, f"bucket-{n}-rule", x + 22, y + 76, 36, 2, BRAND_ACCENT)
    # Bullets
    bullets_y = y + 90
    for bi, b in enumerate(bullets):
        bn = bi + 1
        by = bullets_y + bi * 30
        add_text(
            slide, f"bucket-{n}-bullet-{bn}-dot", "·",
            x_px=x + 22, y_px=by - 2, w_px=8, h_px=18,
            font_size_px=14, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"bucket-{n}-bullet-{bn}-text", b,
            x_px=x + 34, y_px=by, w_px=w - 60, h_px=28,
            font_size_px=11, color=TEXT_MID,
        )
    # Chip
    chip_w = min(w - 44, len(chip) * 7 + 24)
    chip_h = 20
    chip_y = y + h - 30
    chip_bg = add_rect(slide, f"bucket-{n}-chip", x + 22, chip_y, chip_w, chip_h, CARD_BORDER)
    chip_bg.line.fill.background()
    add_text(
        slide, f"bucket-{n}-chip-text", chip,
        x_px=x + 22, y_px=chip_y, w_px=chip_w, h_px=chip_h,
        font_size_px=10, color=BRAND_PRIMARY_MID, bold=True,
        align="center", anchor="middle",
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Four pillars of <strong>operational excellence</strong> demand equal investment",
        subtitle="Each quadrant represents a distinct capability bucket — gaps in any one constrain overall performance",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap = 14
    card_w = (body_w - gap) // 2
    card_h = (body_h - gap) // 2

    buckets = [
        ("01", "Strategy & Governance",
         ["Align executive sponsorship with programme KPIs",
          "Establish decision-rights matrix across workstreams",
          "Conduct quarterly strategic fit reviews"],
         "Maturity target: Level 4", True),
        ("02", "Talent & Capability",
         ["Map skills gaps against future-state operating model",
          "Deploy targeted upskilling pathways by role cluster",
          "Embed change champions in each business unit"],
         "~340 FTE affected", False),
        ("03", "Process & Automation",
         ["Prioritise high-volume, rule-based tasks for RPA",
          "Re-engineer end-to-end flows before automating",
          "Measure cycle-time reduction at each release gate"],
         "Est. 30% efficiency gain", False),
        ("04", "Data & Technology",
         ["Consolidate data sources into a single source of truth",
          "Enforce API-first integration standards across platforms",
          "Build real-time dashboards for operational visibility"],
         "12 systems in scope", False),
    ]
    for i, (num, title, bullets, chip, accented) in enumerate(buckets):
        n = i + 1
        col = i % 2
        row = i // 2
        cx = body_left + col * (card_w + gap)
        cy = body_top + row * (card_h + gap)
        _bucket_card(
            slide, n, cx, cy, card_w, card_h,
            num=num, title=title, bullets=bullets, chip=chip, accented=accented,
        )

    add_footer(slide, page_num=320)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "320_4bucket-2x2-grid.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
