"""
Builder for pattern 173: References & Further Reading — 2-col ref cards + internal chips strip.

Source HTML: _pattern-library/173_reference-further-reading.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

CHIP_TAG_BG = RGBColor(0xED, 0xE0, 0xFA)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="References &amp; <strong>Further Reading</strong>",
        subtitle="Curated sources, frameworks, and internal materials supporting this analysis",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

    content_top = 156
    content_left = 48
    content_w = 1280 - 96
    gap = 20
    col_w = (content_w - gap) // 2

    refs_left = [
        ("📄", "The State of AI in Enterprise 2025", "McKinsey Global Institute", "2025"),
        ("📄", "Digital Transformation Maturity Index", "Gartner Research", "2025"),
        ("📄", "Future of Work: Workforce Reinvention", "World Economic Forum", "2024"),
        ("📄", "Technology Vision 2026: Human by Design", "Accenture Research", "2026"),
    ]
    refs_right = [
        ("📰", "Competing on Customer Journeys", "Harvard Business Review · David C. Edelman", "2024"),
        ("📰", "Jobs-to-Be-Done Theory: A Primer", "Clayton Christensen Institute", "2023"),
        ("📁", "OKR Framework — Measure What Matters", "John Doerr · Penguin Business", "2023"),
        ("📁", "Platform Strategy Design Principles", "MIT Sloan Management Review", "2025"),
    ]

    headers = ["Reports & Research", "Articles & Frameworks"]
    item_h = 64
    item_gap = 8

    for col_idx, (refs, header) in enumerate(zip([refs_left, refs_right], headers)):
        col_x = content_left + col_idx * (col_w + gap)
        # Column header
        add_text(slide, f"col-{col_idx+1}-header", header,
                 col_x, content_top, col_w, 18,
                 font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
        add_rect(slide, f"col-{col_idx+1}-header-rule", col_x, content_top + 18, col_w, 1, CARD_BORDER)

        y = content_top + 28
        for i, (icon, title, source, year) in enumerate(refs):
            n = col_idx * 4 + i + 1
            item = add_rect(slide, f"ref-{n}-card", col_x, y, col_w, item_h, CARD_BG)
            item.line.color.rgb = CARD_BORDER
            item.line.width = 9525
            add_rect(slide, f"ref-{n}-accent", col_x, y, 2, item_h, BRAND_ACCENT)
            # Icon
            add_text(slide, f"ref-{n}-icon", icon,
                     col_x + 10, y + 8, 24, 24, font_size_px=18, color=TEXT_DARK)
            # Title
            add_text(slide, f"ref-{n}-title", title,
                     col_x + 40, y + 6, col_w - 50, 18,
                     font_size_px=12, color=TEXT_DARK, bold=True)
            # Source
            add_text(slide, f"ref-{n}-source", source,
                     col_x + 40, y + 26, col_w - 50, 14,
                     font_size_px=11, color=TEXT_MID)
            # Year
            add_text(slide, f"ref-{n}-year", year,
                     col_x + 40, y + 42, col_w - 50, 14,
                     font_size_px=10, color=TEXT_FAINT)
            y += item_h + item_gap

    # Internal strip
    strip_y = 720 - 64 - 38
    strip_x = content_left
    strip_w = content_w
    add_rect(slide, "internal-strip-bg", strip_x, strip_y, strip_w, 32, CARD_BG)
    add_text(slide, "internal-strip-label", "INTERNAL RESOURCES",
             strip_x + 12, strip_y, 160, 32,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True, anchor="middle")
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
        c = add_rect(slide, f"chip-{n}-bg", cx, strip_y + 6, cw, 20, WHITE)
        c.line.color.rgb = CARD_BORDER
        c.line.width = 9525
        add_text(slide, f"chip-{n}-name", name,
                 cx + 8, strip_y + 6, cw - 60, 20,
                 font_size_px=11, color=TEXT_DARK, bold=True, anchor="middle")
        add_rect(slide, f"chip-{n}-tag-bg", cx + cw - 56, strip_y + 9, 50, 14, CHIP_TAG_BG)
        add_text(slide, f"chip-{n}-tag", tag,
                 cx + cw - 56, strip_y + 9, 50, 14,
                 font_size_px=8, color=BRAND_ACCENT, bold=True, align="center", anchor="middle", uppercase=True)

    add_footer(slide, page_num=173)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "173_reference-further-reading.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
