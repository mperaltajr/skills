"""
Builder for pattern 174: Appendix Divider with Sub-List — left dark panel + right list.

Source HTML: _pattern-library/174_appendix-divider-sub-list.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Appendix — <strong>Supporting Materials</strong>",
        subtitle="Reference documentation, data exhibits, and methodology notes",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

    # Body area
    body_top = 142
    body_bottom = 720 - 56
    left_w = 480

    # Left panel — brand-primary
    add_rect(slide, "left-panel-bg", 0, body_top, left_w, body_bottom - body_top, BRAND_PRIMARY)
    add_rect(slide, "left-panel-accent", left_w - 4, body_top, 4, body_bottom - body_top, BRAND_ACCENT)
    # Appendix label
    label_y = body_top + (body_bottom - body_top - 160) // 2
    add_text(slide, "appendix-label", "APPENDIX",
             0, label_y, left_w, 32,
             font_size_px=24, color=WHITE, bold=True, align="center", uppercase=True)
    # Big letter A
    add_text(slide, "appendix-letter", "A",
             0, label_y + 38, left_w, 120,
             font_size_px=96, color=BRAND_ACCENT_SOFT, bold=True, align="center")

    # Right panel
    right_x = left_w + 24
    right_w = 1280 - right_x - 48
    right_top = body_top + 32

    add_text(slide, "contains-header", "This appendix contains:",
             right_x, right_top, right_w, 22,
             font_size_px=16, color=BRAND_PRIMARY, bold=True)

    items = [
        ("01", "Detailed Financial Model", "Five-year P&L projections with sensitivity tables", "A1 – A3"),
        ("02", "Market Sizing & Benchmarks", "TAM/SAM/SOM analysis and competitive landscape", "A4 – A5"),
        ("03", "Stakeholder Interview Summary", "Key themes from 24 structured interviews", "A6 – A7"),
        ("04", "Technology Architecture Overview", "Current-state and target-state system diagrams", "A8 – A9"),
        ("05", "Risk Register & Mitigation Plan", "RAG-rated risks with owners and response actions", "A10 – A11"),
        ("06", "Data Sources & Methodology", "Reference list and analytical approach notes", "A12"),
    ]
    item_h = 46
    y = right_top + 36
    for i, (num, title, sub, page) in enumerate(items):
        n = i + 1
        # Top border
        add_rect(slide, f"item-{n}-rule", right_x, y, right_w, 1, CARD_BORDER)
        # Number
        add_text(slide, f"item-{n}-num", num,
                 right_x, y + 6, 30, 18,
                 font_size_px=11, color=BRAND_ACCENT, bold=True)
        # Title
        add_text(slide, f"item-{n}-title", title,
                 right_x + 38, y + 6, right_w - 110, 16,
                 font_size_px=13, color=TEXT_DARK, bold=True)
        # Subtitle
        add_text(slide, f"item-{n}-subtitle", sub,
                 right_x + 38, y + 24, right_w - 110, 14,
                 font_size_px=11, color=TEXT_MID)
        # Page
        add_text(slide, f"item-{n}-page", page,
                 right_x + right_w - 70, y + 6, 70, 18,
                 font_size_px=11, color=TEXT_FAINT, bold=True, align="right")
        y += item_h
    # Bottom border
    add_rect(slide, "items-bottom-rule", right_x, y, right_w, 1, CARD_BORDER)

    # Page range bottom-right
    add_text(slide, "page-range", "PAGES A1 – A12",
             right_x + right_w - 160, body_bottom - 28, 160, 18,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, align="right", uppercase=True)

    add_footer(slide, page_num=174)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "174_appendix-divider-sub-list.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
