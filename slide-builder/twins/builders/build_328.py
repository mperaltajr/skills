"""
Builder for pattern 328: 6-bucket 2x3 grid (2 rows × 3 cols).

Compact reference grid: numbered badge, title, 2 bullets, metric label.

Source HTML: _pattern-library/328_6bucket-2x3-grid.html
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


def _bucket_card(slide, n, x, y, w, h, *, num, title, bullets, metric):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG)
    card.line.color.rgb = CARD_BORDER
    card.line.width = 9525
    # Top accent rule (small)
    add_rect(slide, f"bucket-{n}-top", x, y, w, 2, BRAND_ACCENT)
    # Number badge
    bsize = 24
    bx = x + 14
    by = y + 12
    add_rect(slide, f"bucket-{n}-badge-bg", bx, by, bsize, bsize, BRAND_PRIMARY)
    add_text(slide, f"bucket-{n}-badge", num,
             x_px=bx, y_px=by, w_px=bsize, h_px=bsize,
             font_size_px=10, color=WHITE, bold=True,
             align="center", anchor="middle")
    # Title
    add_text(slide, f"bucket-{n}-title", title,
             x_px=bx + bsize + 10, y_px=by + 2, w_px=w - bsize - 40, h_px=20,
             font_size_px=12, color=BRAND_PRIMARY, bold=True)
    # Bullets
    by_text = y + 50
    for bi, b in enumerate(bullets):
        bn = bi + 1
        add_text(slide, f"bucket-{n}-bullet-{bn}", "– " + b,
                 x_px=x + 14, y_px=by_text + bi * 22, w_px=w - 28, h_px=22,
                 font_size_px=10, color=TEXT_MID)
    # Metric label
    add_text(slide, f"bucket-{n}-metric", metric,
             x_px=x + 14, y_px=y + h - 24, w_px=w - 28, h_px=16,
             font_size_px=10, color=BRAND_ACCENT, bold=True)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Six dimensions that define <strong>transformation readiness</strong>",
        subtitle="A compact reference grid across all capability buckets",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap_x = 14
    gap_y = 14
    cols = 3
    rows = 2
    card_w = (body_w - (cols - 1) * gap_x) // cols
    card_h = (body_h - (rows - 1) * gap_y) // rows

    buckets = [
        ("01", "Strategic Alignment",
         ["Leadership vision linked to delivery roadmap",
          "KPIs cascade from enterprise objectives"],
         "Avg. maturity: 3.2 / 5"),
        ("02", "Data & Analytics",
         ["Unified data platform with governed access",
          "Self-serve BI adoption above 60%"],
         "Coverage: 74% of domains"),
        ("03", "Technology & Architecture",
         ["Cloud-native services as default deployment target",
          "API-first integration fabric in place"],
         "Cloud spend: 48% of IT"),
        ("04", "Talent & Skills",
         ["Reskilling pathways funded at programme level",
          "Digital fluency baseline assessed annually"],
         "Skill gap: 22% workforce"),
        ("05", "Operating Model",
         ["Product-aligned squads with clear P&L ownership",
          "Agile at scale frameworks adopted enterprise-wide"],
         "Squad velocity: +18% YoY"),
        ("06", "Change & Culture",
         ["Structured OCM programme with executive sponsor",
          "Adoption tracked via utilisation dashboards"],
         "Adoption score: 67 / 100"),
    ]
    for i, (num, title, bullets, metric) in enumerate(buckets):
        n = i + 1
        col = i % cols
        row = i // cols
        cx = body_left + col * (card_w + gap_x)
        cy = body_top + row * (card_h + gap_y)
        _bucket_card(slide, n, cx, cy, card_w, card_h,
                     num=num, title=title, bullets=bullets, metric=metric)

    add_footer(slide, page_num=328)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "328_6bucket-2x3-grid.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
