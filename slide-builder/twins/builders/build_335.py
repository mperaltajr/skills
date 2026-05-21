"""
Builder for pattern 335: 7-bucket dark.

One large hero card (item 01 with deep description + big stat) plus 6 compact
cards in a 3×2 grid on the right — same shape as 332 but dark.

Source HTML: _pattern-library/335_7bucket-dark.html
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


def _small_card(slide, n, x, y, w, h, *, num, title, bullets):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG_DARK)
    card.line.color.rgb = CARD_BORDER_DARK
    card.line.width = 9525
    add_rect(slide, f"bucket-{n}-top", x, y, w, 2, BRAND_ACCENT_SOFT)
    add_text(slide, f"bucket-{n}-num", num,
             x_px=x + 12, y_px=y + 10, w_px=40, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1.2)
    add_text(slide, f"bucket-{n}-title", title,
             x_px=x + 12, y_px=y + 28, w_px=w - 24, h_px=22,
             font_size_px=11, color=WHITE, bold=True)
    by_text = y + 54
    for bi, b in enumerate(bullets):
        bn = bi + 1
        add_text(slide, f"bucket-{n}-bullet-{bn}", "– " + b,
                 x_px=x + 12, y_px=by_text + bi * 22, w_px=w - 24, h_px=22,
                 font_size_px=10, color=TEXT_ON_DARK_MID)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(slide, "title",
             "Seven Pillars of <strong>Transformation</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=28, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Strategic priorities mapped across the full programme lifecycle",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=13, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top

    # Hero card (left)
    hero_w = 420
    hero_h = body_h
    hx = body_left
    hy = body_top
    hero = add_rect(slide, "hero-card", hx, hy, hero_w, hero_h, CARD_BG_DARK)
    hero.line.color.rgb = BRAND_ACCENT
    hero.line.width = 19050
    add_rect(slide, "hero-top", hx, hy, hero_w, 4, BRAND_ACCENT)
    add_text(slide, "hero-label", "PRIMARY · 01",
             x_px=hx + 22, y_px=hy + 20, w_px=hero_w - 44, h_px=18,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1.6)
    add_text(slide, "hero-title", "Executive Alignment & Sponsorship",
             x_px=hx + 22, y_px=hy + 46, w_px=hero_w - 44, h_px=70,
             font_size_px=21, color=WHITE, bold=True)
    add_rect(slide, "hero-rule", hx + 22, hy + 128, 48, 3, BRAND_ACCENT)
    add_text(slide, "hero-desc",
             "Sustained C-suite commitment is the single strongest predictor of "
             "programme success. Establish a governance cadence that surfaces "
             "blockers before they become escalations.",
             x_px=hx + 22, y_px=hy + 146, w_px=hero_w - 44, h_px=160,
             font_size_px=13, color=TEXT_ON_DARK_MID)
    # Hero metric value (large)
    add_text(slide, "hero-metric", "87%",
             x_px=hx + 22, y_px=hy + hero_h - 130, w_px=hero_w - 44, h_px=70,
             font_size_px=52, color=BRAND_ACCENT_SOFT, bold=True)
    add_text(slide, "hero-metric-label",
             "of stalled programmes cite misaligned sponsorship",
             x_px=hx + 22, y_px=hy + hero_h - 56, w_px=hero_w - 44, h_px=36,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, italic=True)

    # Right grid 3×2
    right_x = hx + hero_w + 16
    right_w = body_w - hero_w - 16
    cols = 3
    rows = 2
    gap_x = 12
    gap_y = 12
    sw = (right_w - (cols - 1) * gap_x) // cols
    sh = (body_h - (rows - 1) * gap_y) // rows

    cards = [
        ("02", "Operating Model Design",
         ["Define target-state org structure and spans",
          "Align roles to value-stream accountabilities"]),
        ("03", "Data & Analytics Foundation",
         ["Establish single source of truth for KPIs",
          "Govern data quality at ingestion layer"]),
        ("04", "Technology Enablement",
         ["Retire shadow systems blocking adoption",
          "Phase cloud migration to de-risk cutover"]),
        ("05", "Change & Capability Build",
         ["Run impact assessments per stakeholder cohort",
          "Embed learning in the flow of work"]),
        ("06", "Value Realisation Tracking",
         ["Link milestones to measurable business outcomes",
          "Monthly benefit harvest reviews with CFO office"]),
        ("07", "Continuous Improvement",
         ["Formalise retrospective loop post each phase",
          "Capture and broadcast what good looks like"]),
    ]
    for i, (num, title, bullets) in enumerate(cards):
        n = i + 2
        col = i % cols
        row = i // cols
        cx = right_x + col * (sw + gap_x)
        cy = body_top + row * (sh + gap_y)
        _small_card(slide, n, cx, cy, sw, sh, num=num, title=title, bullets=bullets)

    # Footer (dark)
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "335",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "335_7bucket-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
