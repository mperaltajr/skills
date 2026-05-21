"""
Builder for pattern 173d: References & Further Reading — DARK variant.

Light source: twins/builders/build_173.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

CHIP_TAG_BG = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "References &amp; <strong>Further Reading</strong>",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Curated sources, frameworks, and internal materials supporting this analysis",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    content_top = 220
    content_left = 48
    content_w = 1280 - 96
    gap = 20
    col_w = (content_w - gap) // 2

    refs_left = [
        ("•", "The State of AI in Enterprise 2025", "McKinsey Global Institute", "2025"),
        ("•", "Digital Transformation Maturity Index", "Gartner Research", "2025"),
        ("•", "Future of Work: Workforce Reinvention", "World Economic Forum", "2024"),
        ("•", "Technology Vision 2026: Human by Design", "Accenture Research", "2026"),
    ]
    refs_right = [
        ("•", "Competing on Customer Journeys", "Harvard Business Review · David C. Edelman", "2024"),
        ("•", "Jobs-to-Be-Done Theory: A Primer", "Clayton Christensen Institute", "2023"),
        ("•", "OKR Framework — Measure What Matters", "John Doerr · Penguin Business", "2023"),
        ("•", "Platform Strategy Design Principles", "MIT Sloan Management Review", "2025"),
    ]

    headers = ["Reports & Research", "Articles & Frameworks"]
    item_h = 64
    item_gap = 8

    for col_idx, (refs, header) in enumerate(zip([refs_left, refs_right], headers)):
        col_x = content_left + col_idx * (col_w + gap)
        add_text(slide, f"col-{col_idx+1}-header", header,
                 col_x, content_top, col_w, 18,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
        add_rect(slide, f"col-{col_idx+1}-header-rule", col_x, content_top + 18, col_w, 1, CARD_BORDER_DARK)

        y = content_top + 28
        for i, (icon, title, source, year) in enumerate(refs):
            n = col_idx * 4 + i + 1
            item = add_rect(slide, f"ref-{n}-card", col_x, y, col_w, item_h, CARD_BG_DARK)
            item.line.color.rgb = CARD_BORDER_DARK
            item.line.width = 9525
            add_rect(slide, f"ref-{n}-accent", col_x, y, 2, item_h, BRAND_ACCENT_SOFT)
            add_text(slide, f"ref-{n}-icon", icon,
                     col_x + 10, y + 8, 24, 24, font_size_px=18, color=BRAND_ACCENT_SOFT)
            add_text(slide, f"ref-{n}-title", title,
                     col_x + 40, y + 6, col_w - 50, 18,
                     font_size_px=12, color=WHITE, bold=True)
            add_text(slide, f"ref-{n}-source", source,
                     col_x + 40, y + 26, col_w - 50, 14,
                     font_size_px=11, color=TEXT_ON_DARK_MID)
            add_text(slide, f"ref-{n}-year", year,
                     col_x + 40, y + 42, col_w - 50, 14,
                     font_size_px=10, color=TEXT_ON_DARK_FAINT)
            y += item_h + item_gap

    strip_y = 720 - 64 - 38
    strip_x = content_left
    strip_w = content_w
    add_rect(slide, "internal-strip-bg", strip_x, strip_y, strip_w, 32, CARD_BG_DARK)
    add_text(slide, "internal-strip-label", "INTERNAL RESOURCES",
             strip_x + 12, strip_y, 160, 32,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True, anchor="middle")
    chip_x = strip_x + 188
    chips = [
        ("AI Readiness Playbook v3", "Internal"),
        ("Client Benchmark Database 2025", "Restricted"),
        ("Digital Strategy Toolkit — FS", "Internal"),
    ]
    for i, (name, tag) in enumerate(chips):
        n = i + 1
        cw = 280
        cx = chip_x + i * (cw + 10)
        c = add_rect(slide, f"chip-{n}-bg", cx, strip_y + 6, cw, 20, BRAND_PRIMARY)
        c.line.color.rgb = CARD_BORDER_DARK
        c.line.width = 9525
        add_text(slide, f"chip-{n}-name", name,
                 cx + 8, strip_y + 6, cw - 60, 20,
                 font_size_px=11, color=WHITE, bold=True, anchor="middle")
        add_rect(slide, f"chip-{n}-tag-bg", cx + cw - 56, strip_y + 9, 50, 14, CHIP_TAG_BG)
        add_text(slide, f"chip-{n}-tag", tag,
                 cx + cw - 56, strip_y + 9, 50, 14,
                 font_size_px=8, color=BRAND_ACCENT_SOFT, bold=True, align="center", anchor="middle", uppercase=True)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "173",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "173d_reference-further-reading-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
