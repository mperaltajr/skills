"""
Builder for pattern 329: 6-bucket 3x2 grid (3 rows × 2 cols, taller cards with more bullets).

Source HTML: _pattern-library/329_6bucket-3x2-grid.html
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


def _bucket_card(slide, n, x, y, w, h, *, num, title, bullets):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG)
    card.line.color.rgb = CARD_BORDER
    card.line.width = 9525
    # Left accent strip
    add_rect(slide, f"bucket-{n}-accent", x, y, 3, h, BRAND_ACCENT)
    # Number badge
    bsize = 28
    bx = x + 18
    by = y + (h - bsize) // 2 - 14
    add_rect(slide, f"bucket-{n}-badge-bg", bx, by, bsize, bsize, BRAND_PRIMARY)
    add_text(slide, f"bucket-{n}-badge", num,
             x_px=bx, y_px=by, w_px=bsize, h_px=bsize,
             font_size_px=11, color=WHITE, bold=True,
             align="center", anchor="middle")
    # Title
    add_text(slide, f"bucket-{n}-title", title,
             x_px=bx + bsize + 14, y_px=by, w_px=w - bsize - 60, h_px=24,
             font_size_px=14, color=BRAND_PRIMARY, bold=True)
    # Bullets
    by_text = by + 34
    for bi, b in enumerate(bullets):
        bn = bi + 1
        add_text(slide, f"bucket-{n}-bullet-{bn}-dot", "·",
                 x_px=bx + bsize + 14, y_px=by_text + bi * 18 - 2, w_px=10, h_px=18,
                 font_size_px=14, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"bucket-{n}-bullet-{bn}", b,
                 x_px=bx + bsize + 26, y_px=by_text + bi * 18, w_px=w - bsize - 70, h_px=18,
                 font_size_px=11, color=TEXT_MID)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Six dimensions that <strong>define the transformation</strong>",
        subtitle="Each bucket represents a workstream with discrete deliverables and ownership",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap_x = 16
    gap_y = 12
    cols = 2
    rows = 3
    card_w = (body_w - (cols - 1) * gap_x) // cols
    card_h = (body_h - (rows - 1) * gap_y) // rows

    buckets = [
        ("01", "Strategy & Vision",
         ["Define north-star objectives and success metrics",
          "Align leadership on transformation scope",
          "Establish governance and decision rights"]),
        ("02", "Operating Model",
         ["Redesign org structure for agility",
          "Map roles, spans, and layers to future state",
          "Define cross-functional teaming principles"]),
        ("03", "Technology & Data",
         ["Assess current-state architecture gaps",
          "Prioritise platform and data investments",
          "Build integration and interoperability roadmap"]),
        ("04", "Process Excellence",
         ["Identify high-impact process automation targets",
          "Standardise end-to-end value streams",
          "Embed continuous improvement mechanisms"]),
        ("05", "Talent & Culture",
         ["Build capability frameworks for new ways of working",
          "Launch reskilling and change readiness programmes",
          "Measure cultural adoption through pulse surveys"]),
        ("06", "Value Realisation",
         ["Track benefits against baseline projections",
          "Govern investment-to-outcome traceability",
          "Iterate priorities based on realised impact"]),
    ]
    for i, (num, title, bullets) in enumerate(buckets):
        n = i + 1
        col = i % cols
        row = i // cols
        cx = body_left + col * (card_w + gap_x)
        cy = body_top + row * (card_h + gap_y)
        _bucket_card(slide, n, cx, cy, card_w, card_h,
                     num=num, title=title, bullets=bullets)

    add_footer(slide, page_num=329)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "329_6bucket-3x2-grid.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
