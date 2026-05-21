"""
Builder for pattern 339: 8-bucket dark (4x2 grid on dark BRAND_PRIMARY background).

Compact cards with number, title, 2 bullets — no metric line.

Source HTML: _pattern-library/339_8bucket-dark.html
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


def _bucket_card(slide, n, x, y, w, h, *, num, title, bullets):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG_DARK)
    card.line.color.rgb = CARD_BORDER_DARK
    card.line.width = 9525
    add_rect(slide, f"bucket-{n}-top", x, y, w, 2, BRAND_ACCENT_SOFT)
    add_text(slide, f"bucket-{n}-num", num,
             x_px=x + 12, y_px=y + 10, w_px=40, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1.2)
    add_text(slide, f"bucket-{n}-title", title,
             x_px=x + 12, y_px=y + 28, w_px=w - 24, h_px=24,
             font_size_px=12, color=WHITE, bold=True)
    by_text = y + 60
    for bi, b in enumerate(bullets):
        bn = bi + 1
        add_text(slide, f"bucket-{n}-bullet-{bn}", "– " + b,
                 x_px=x + 12, y_px=by_text + bi * 24, w_px=w - 24, h_px=24,
                 font_size_px=11, color=TEXT_ON_DARK_MID)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(slide, "title",
             "Eight dimensions of <strong>strategic impact</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=28, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "A structured view across capabilities, delivery, and outcomes",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=13, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

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
        ("01", "Strategic Alignment",
         ["Anchored to executive priorities",
          "Mapped to value drivers"]),
        ("02", "Operating Model",
         ["Roles and accountability clarity",
          "Cross-functional integration"]),
        ("03", "Technology Foundation",
         ["Core platform modernisation",
          "API-first architecture"]),
        ("04", "Data & Intelligence",
         ["Governed data products",
          "Real-time decision signals"]),
        ("05", "Talent & Capability",
         ["Skills gap remediation",
          "Continuous learning culture"]),
        ("06", "Change & Adoption",
         ["Stakeholder engagement plan",
          "Adoption metrics tracked"]),
        ("07", "Risk & Compliance",
         ["Regulatory control mapping",
          "Proactive issue escalation"]),
        ("08", "Value Realisation",
         ["Benefits tracked to baseline",
          "Steering-ready dashboards"]),
    ]
    for i, (num, title, bullets) in enumerate(buckets):
        n = i + 1
        col = i % cols
        row = i // cols
        cx = body_left + col * (card_w + gap_x)
        cy = body_top + row * (card_h + gap_y)
        _bucket_card(slide, n, cx, cy, card_w, card_h,
                     num=num, title=title, bullets=bullets)

    # Footer (dark)
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "339",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "339_8bucket-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
