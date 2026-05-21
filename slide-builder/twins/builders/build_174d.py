"""
Builder for pattern 174d: Appendix Divider with Sub-List — DARK variant.

Light source: twins/builders/build_174.py
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


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Appendix — <strong>Supporting Materials</strong>",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Reference documentation, data exhibits, and methodology notes",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    body_top = 220
    body_bottom = 720 - 56
    left_w = 480

    # Left panel — deeper dark card panel (since BG is already brand-primary)
    add_rect(slide, "left-panel-bg", 0, body_top, left_w, body_bottom - body_top, CARD_BG_DARK)
    add_rect(slide, "left-panel-accent", left_w - 4, body_top, 4, body_bottom - body_top, BRAND_ACCENT_SOFT)
    label_y = body_top + (body_bottom - body_top - 160) // 2
    add_text(slide, "appendix-label", "APPENDIX",
             0, label_y, left_w, 32,
             font_size_px=24, color=WHITE, bold=True, align="center", uppercase=True)
    add_text(slide, "appendix-letter", "A",
             0, label_y + 38, left_w, 120,
             font_size_px=96, color=BRAND_ACCENT_SOFT, bold=True, align="center")

    right_x = left_w + 24
    right_w = 1280 - right_x - 48
    right_top = body_top + 8

    add_text(slide, "contains-header", "This appendix contains:",
             right_x, right_top, right_w, 22,
             font_size_px=16, color=BRAND_ACCENT_SOFT, bold=True)

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
        add_rect(slide, f"item-{n}-rule", right_x, y, right_w, 1, CARD_BORDER_DARK)
        add_text(slide, f"item-{n}-num", num,
                 right_x, y + 6, 30, 18,
                 font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"item-{n}-title", title,
                 right_x + 38, y + 6, right_w - 110, 16,
                 font_size_px=13, color=WHITE, bold=True)
        add_text(slide, f"item-{n}-subtitle", sub,
                 right_x + 38, y + 24, right_w - 110, 14,
                 font_size_px=11, color=TEXT_ON_DARK_MID)
        add_text(slide, f"item-{n}-page", page,
                 right_x + right_w - 70, y + 6, 70, 18,
                 font_size_px=11, color=TEXT_ON_DARK_FAINT, bold=True, align="right")
        y += item_h
    add_rect(slide, "items-bottom-rule", right_x, y, right_w, 1, CARD_BORDER_DARK)

    add_text(slide, "page-range", "PAGES A1 – A12",
             right_x + right_w - 160, body_bottom - 28, 160, 18,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, align="right", uppercase=True)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "174",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "174d_appendix-divider-sub-list-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
