"""
Builder for pattern 02d: Three pillars with icons + outputs strip — DARK variant.

Light source: twins/builders/build_02.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
HEADER_FILL = RGBColor(0x14, 0x05, 0x28)  # darker than card for header

PILLAR_GLYPHS = ["◇", "⊕", "⊞"]


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title block (inline dark)
    add_text(
        slide, "title", "Three skill domains — connected, not stacked.",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Strategy work requires all three. Weakness in one cascades to the others — and the deck pays the price.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    grid_left = 56
    pillar_w = (1280 - 112 - 44) // 3
    gap = 22
    pillar_header_h = 52
    pillar_body_h = 200
    pillar_top = 232

    pillar_data = [
        ("Think",
         "Frame the problem before reaching for the slide\nGovern the argument with a single thought\nApply MECE structure — not just bullet points\nTest the so what before drafting\nIdentify decisions vs context"),
        ("Argue",
         "Build the logic chain before the visuals\nPressure-test claims against counterexamples\nSharpen the headline until it stands alone\nAnticipate the senior partner's first question\nDistinguish evidence from assertion"),
        ("Build",
         "Match the right page type to the argument\nKeep the action title doing the work\nUse chart only when chart adds signal\nRespect the invariant footer zone\nRender in PowerPoint, not Word"),
    ]

    for i, (name, body) in enumerate(pillar_data):
        n = i + 1
        cx = grid_left + i * (pillar_w + gap)

        # Header (darker than card to read as a band)
        add_rect(slide, f"pillar-{n}-header", cx, pillar_top, pillar_w, pillar_header_h, HEADER_FILL)
        add_icon(slide, f"pillar-{n}-icon", cx + 20, pillar_top + 8, 32,
                 PILLAR_GLYPHS[i], color=BRAND_ACCENT_SOFT)
        add_text(
            slide, f"pillar-{n}-name", name,
            x_px=cx + 60, y_px=pillar_top + 14, w_px=pillar_w - 80, h_px=28,
            font_size_px=18, color=WHITE, bold=True,
        )

        body_y = pillar_top + pillar_header_h
        body_rect = add_rect(slide, f"pillar-{n}-body-bg", cx, body_y, pillar_w, pillar_body_h, CARD_BG_DARK)
        body_rect.line.color.rgb = CARD_BORDER_DARK
        body_rect.line.width = 9525

        add_text(
            slide, f"pillar-{n}-body", body,
            x_px=cx + 20, y_px=body_y + 16, w_px=pillar_w - 36, h_px=pillar_body_h - 24,
            font_size_px=12, color=WHITE,
        )

    # Outputs strip
    strip_top = pillar_top + pillar_header_h + pillar_body_h + 22
    strip_h = 60

    outputs = [
        "A governing thought + structured argument",
        "A defensible logic chain, claim by claim",
        "A real PPTX, not a wall of text in a box",
    ]
    for i, txt in enumerate(outputs):
        n = i + 1
        cx = grid_left + i * (pillar_w + gap)
        cell = add_rect(slide, f"output-{n}-bg", cx, strip_top, pillar_w, strip_h, CARD_BG_DARK)
        cell.line.color.rgb = CARD_BORDER_DARK
        cell.line.width = 9525
        add_rect(slide, f"output-{n}-accent", cx, strip_top, pillar_w, 2, BRAND_ACCENT_SOFT)
        add_text(
            slide, f"output-{n}-label", "PRODUCES",
            x_px=cx + 18, y_px=strip_top + 10, w_px=pillar_w - 36, h_px=14,
            font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"output-{n}-text", txt,
            x_px=cx + 18, y_px=strip_top + 26, w_px=pillar_w - 36, h_px=28,
            font_size_px=12, color=WHITE, bold=True,
        )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "5",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "02d_three-pillars-icons-outputs.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
