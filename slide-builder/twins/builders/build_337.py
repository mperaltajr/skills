"""
Builder for pattern 337: 8-bucket 2x4 grid (2 rows × 4 cols ≡ 4 cols × 2 rows but HTML
labels it 2x4; same arrangement as 336 but body bullets without metric strip).

Compact cards with number, title, 2 bullets. No bottom metric line.

Source HTML: _pattern-library/337_8bucket-2x4-grid.html
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
    bsize = 26
    bx = x + 18
    by = y + 16
    add_rect(slide, f"bucket-{n}-badge-bg", bx, by, bsize, bsize, BRAND_PRIMARY)
    add_text(slide, f"bucket-{n}-badge", num,
             x_px=bx, y_px=by, w_px=bsize, h_px=bsize,
             font_size_px=10, color=WHITE, bold=True,
             align="center", anchor="middle")
    # Title
    add_text(slide, f"bucket-{n}-title", title,
             x_px=bx + bsize + 12, y_px=by + 2, w_px=w - bsize - 50, h_px=22,
             font_size_px=13, color=BRAND_PRIMARY, bold=True)
    # Bullets
    by_text = y + 60
    for bi, b in enumerate(bullets):
        bn = bi + 1
        add_text(slide, f"bucket-{n}-bullet-{bn}-dot", "·",
                 x_px=x + 18, y_px=by_text + bi * 24 - 2, w_px=10, h_px=22,
                 font_size_px=14, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"bucket-{n}-bullet-{bn}", b,
                 x_px=x + 30, y_px=by_text + bi * 24, w_px=w - 44, h_px=22,
                 font_size_px=11, color=TEXT_MID)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Eight workstreams, <strong>one integrated program</strong>",
        subtitle="Each bucket represents a discrete delivery scope with clear ownership and outcomes.",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap_x = 12
    gap_y = 12
    cols = 4
    rows = 2
    card_w = (body_w - (cols - 1) * gap_x) // cols
    card_h = (body_h - (rows - 1) * gap_y) // rows

    buckets = [
        ("01", "Strategy & Vision",
         ["Define north-star outcomes and success metrics",
          "Align executive sponsors on program charter"]),
        ("02", "Governance & Controls",
         ["Establish steering committee cadence and RACI",
          "Set escalation paths and decision rights"]),
        ("03", "Data & Architecture",
         ["Audit current-state data lineage and quality",
          "Design target-state platform blueprint"]),
        ("04", "Process Redesign",
         ["Map end-to-end processes and identify waste",
          "Co-design future-state operating model"]),
        ("05", "Technology Enablement",
         ["Configure and integrate core platform modules",
          "Validate integrations in staging environment"]),
        ("06", "Change & Adoption",
         ["Develop impact assessments by persona",
          "Execute training and readiness campaigns"]),
        ("07", "Testing & Quality",
         ["Run UAT cycles with business-owned test scripts",
          "Track defect resolution to agreed exit criteria"]),
        ("08", "Cutover & Hypercare",
         ["Execute go-live runbook with rollback triggers",
          "Stabilise operations through 30-day hypercare"]),
    ]
    for i, (num, title, bullets) in enumerate(buckets):
        n = i + 1
        col = i % cols
        row = i // cols
        cx = body_left + col * (card_w + gap_x)
        cy = body_top + row * (card_h + gap_y)
        _bucket_card(slide, n, cx, cy, card_w, card_h,
                     num=num, title=title, bullets=bullets)

    add_footer(slide, page_num=337)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "337_8bucket-2x4-grid.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
