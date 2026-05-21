"""
Builder for pattern 327: 5-bucket dark.

Five cards in a horizontal strip on dark BRAND_PRIMARY background; alternating
accent/muted top bar, numbered badge, title, dash-prefixed bullets, big stat.

Source HTML: _pattern-library/327_5bucket-dark.html
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
MUTED_BAR = RGBColor(0x77, 0x66, 0x99)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title block (inline for dark)
    add_text(slide, "title",
             "Five pillars of <strong>platform transformation</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=28, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Each workstream delivers measurable outcomes across people, process, and technology.",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=13, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Cards row
    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap = 14
    card_w = (body_w - 4 * gap) // 5
    card_h = body_h

    buckets = [
        ("01", True, "Foundation & Architecture",
         ["Cloud-native core platform build-out",
          "API mesh and integration layer"],
         "38%", "cost reduction"),
        ("02", False, "Data & Intelligence",
         ["Unified data fabric deployment",
          "ML pipeline and model ops"],
         "2.4×", "faster insights"),
        ("03", True, "Security & Compliance",
         ["Zero-trust identity framework",
          "Automated controls monitoring"],
         "99.7%", "audit pass rate"),
        ("04", False, "Experience & Adoption",
         ["Role-based UX redesign",
          "Change management playbook"],
         "+41pts", "NPS lift"),
        ("05", True, "Operations & Scale",
         ["AIOps and auto-remediation",
          "Multi-region resilience design"],
         "6 min", "mean time to restore"),
    ]
    for i, (num, accent, title, bullets, stat, stat_lbl) in enumerate(buckets):
        n = i + 1
        cx = body_left + i * (card_w + gap)
        card = add_rect(slide, f"card-{n}-bg", cx, body_top, card_w, card_h, CARD_BG_DARK)
        card.line.color.rgb = CARD_BORDER_DARK
        card.line.width = 9525
        # Top bar
        bar_color = BRAND_ACCENT if accent else MUTED_BAR
        add_rect(slide, f"card-{n}-top", cx, body_top, card_w, 3, bar_color)
        # Number badge
        bsize = 26
        bx = cx + 16
        by = body_top + 18
        add_rect(slide, f"card-{n}-badge-bg", bx, by, bsize, bsize, BRAND_ACCENT)
        add_text(slide, f"card-{n}-badge", num,
                 x_px=bx, y_px=by, w_px=bsize, h_px=bsize,
                 font_size_px=10, color=WHITE, bold=True,
                 align="center", anchor="middle")
        # Title
        add_text(slide, f"card-{n}-title", title,
                 x_px=cx + 16, y_px=body_top + 56, w_px=card_w - 32, h_px=44,
                 font_size_px=13, color=WHITE, bold=True)
        # Bullets
        by_text = body_top + 116
        for bi, b in enumerate(bullets):
            bn = bi + 1
            add_text(slide, f"card-{n}-bullet-{bn}", "– " + b,
                     x_px=cx + 16, y_px=by_text + bi * 36, w_px=card_w - 32, h_px=34,
                     font_size_px=11, color=TEXT_ON_DARK_MID)
        # Stat
        add_text(slide, f"card-{n}-stat", stat,
                 x_px=cx + 16, y_px=body_top + card_h - 60, w_px=card_w - 32, h_px=28,
                 font_size_px=20, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"card-{n}-stat-label", stat_lbl,
                 x_px=cx + 16, y_px=body_top + card_h - 28, w_px=card_w - 32, h_px=16,
                 font_size_px=10, color=TEXT_ON_DARK_FAINT)

    # Footer (dark)
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "327",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "327_5bucket-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
