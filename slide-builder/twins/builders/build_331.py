"""
Builder for pattern 331: 6-bucket dark (3x2 grid on dark BRAND_PRIMARY background).

Source HTML: _pattern-library/331_6bucket-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def _bucket_card(slide, n, x, y, w, h, *, num, title, bullets, metric):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG_DARK)
    card.line.color.rgb = CARD_BORDER_DARK
    card.line.width = 9525
    # Top accent strip
    add_rect(slide, f"bucket-{n}-top", x, y, w, 3, BRAND_ACCENT_SOFT)
    # Number badge
    bsize = 26
    bx = x + 16
    by = y + 16
    add_rect(slide, f"bucket-{n}-badge-bg", bx, by, bsize, bsize, BRAND_ACCENT)
    add_text(slide, f"bucket-{n}-badge", num,
             x_px=bx, y_px=by, w_px=bsize, h_px=bsize,
             font_size_px=10, color=WHITE, bold=True,
             align="center", anchor="middle")
    # Title
    add_text(slide, f"bucket-{n}-title", title,
             x_px=bx + bsize + 12, y_px=by + 2, w_px=w - bsize - 50, h_px=22,
             font_size_px=13, color=WHITE, bold=True)
    # Bullets
    by_text = y + 60
    for bi, b in enumerate(bullets):
        bn = bi + 1
        add_text(slide, f"bucket-{n}-bullet-{bn}", "– " + b,
                 x_px=x + 16, y_px=by_text + bi * 22, w_px=w - 32, h_px=22,
                 font_size_px=11, color=TEXT_ON_DARK_MID)
    # Metric
    add_text(slide, f"bucket-{n}-metric", metric,
             x_px=x + 16, y_px=y + h - 26, w_px=w - 32, h_px=18,
             font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title block (inline)
    add_text(slide, "title",
             "Six <strong>strategic levers</strong> driving transformation",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=28, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Prioritized initiative clusters mapped to business value and delivery readiness",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=13, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap_x = 16
    gap_y = 12
    cols = 3
    rows = 2
    card_w = (body_w - (cols - 1) * gap_x) // cols
    card_h = (body_h - (rows - 1) * gap_y) // rows

    buckets = [
        ("01", "Data Foundation & Governance",
         ["Unified data catalog across 14 source systems",
          "Master data management framework deployed"],
         "84% coverage"),
        ("02", "Cloud Migration & Modernisation",
         ["Lift-and-shift Phase 1 completed on schedule",
          "Containerisation of 60+ legacy workloads"],
         "$3.2M savings"),
        ("03", "AI & Analytics Enablement",
         ["Predictive demand models in 3 business units",
          "GenAI pilot: 40% reduction in report cycle"],
         "+27% throughput"),
        ("04", "Operating Model Redesign",
         ["Product-aligned squads replacing functional silos",
          "RACI refreshed for 8 critical decision domains"],
         "18 wks to go-live"),
        ("05", "Cybersecurity & Resilience",
         ["Zero-trust architecture rollout across core zones",
          "MTTD reduced from 72h to under 4h"],
         "Risk: Medium → Low"),
        ("06", "Change & Capability Building",
         ["Digital fluency programme reaching 4,200 staff",
          "Adoption index up 22 pts since Q1 baseline"],
         "92% enrolment"),
    ]
    for i, (num, title, bullets, metric) in enumerate(buckets):
        n = i + 1
        col = i % cols
        row = i // cols
        cx = body_left + col * (card_w + gap_x)
        cy = body_top + row * (card_h + gap_y)
        _bucket_card(slide, n, cx, cy, card_w, card_h,
                     num=num, title=title, bullets=bullets, metric=metric)

    # Footer (dark)
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "331",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "331_6bucket-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
