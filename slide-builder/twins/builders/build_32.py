"""
Builder for pattern 32: SWOT analysis (2x2 matrix).

Quadrants use tl/tr/bl/br canonical suffixes. Each quadrant has a header
(name + meta) and 4 chip bullets in the body.

Source HTML: _pattern-library/32_swot-analysis.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT,
    CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

SWOT_STRENGTH = RGBColor(0xDC, 0xFC, 0xE7)
SWOT_WEAKNESS = RGBColor(0xFE, 0xCA, 0xCA)
SWOT_OPPORTUNITY = RGBColor(0xF8, 0xF4, 0xFC)
SWOT_THREAT = RGBColor(0xFE, 0xF3, 0xC7)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Slide Lab SWOT — building from strengths, naming the work.",
        subtitle="Internal advantages compound with external opportunities; the rest is the work ahead.",
        title_h=68,
        subtitle_h=22,
    )

    # Content block: 56..1224 wide, 200..580 tall = 1168 × 380
    block_left = 56
    block_top = 200
    block_w = 1168
    block_h = 360  # leaves room for convergence

    # Axis labels
    # Y axis (left, vertical writing): "Internal" top, "External" bottom
    add_text(
        slide, "quadrant-y-high", "INTERNAL",
        x_px=block_left - 8, y_px=block_top + 40, w_px=28, h_px=120,
        font_size_px=9, color=TEXT_MID, bold=True,
        letter_spacing_px=1.5, uppercase=True,
    )
    add_text(
        slide, "quadrant-y-low", "EXTERNAL",
        x_px=block_left - 8, y_px=block_top + 200, w_px=28, h_px=120,
        font_size_px=9, color=TEXT_MID, bold=True,
        letter_spacing_px=1.5, uppercase=True,
    )

    # X axis (top): "Positive" / "Negative"
    grid_left = block_left + 38
    grid_w = block_w - 38
    add_text(
        slide, "quadrant-x-low", "POSITIVE",
        x_px=grid_left, y_px=block_top, w_px=grid_w // 2, h_px=16,
        font_size_px=9, color=TEXT_MID, bold=True, align="center",
        letter_spacing_px=2, uppercase=True,
    )
    add_text(
        slide, "quadrant-x-high", "NEGATIVE",
        x_px=grid_left + grid_w // 2, y_px=block_top, w_px=grid_w // 2, h_px=16,
        font_size_px=9, color=TEXT_MID, bold=True, align="center",
        letter_spacing_px=2, uppercase=True,
    )

    # Grid 2x2 starts at y=block_top + 22, fills remaining vertical
    g_top = block_top + 22
    g_h = block_h - 22
    cell_w = (grid_w - 8) // 2
    cell_h = (g_h - 8) // 2

    quad_specs = [
        ("tl", "Strengths", "Internal · Positive", SWOT_STRENGTH,
         ["Real measured cycle-time gains (-64% in pilot)",
          "Compounds with existing consultant skills",
          "Drops into any brand template",
          "Internal IP — no vendor dependency"]),
        ("tr", "Weaknesses", "Internal · Negative", SWOT_WEAKNESS,
         ["Pattern library still expanding",
          "HTML→PPTX translator not yet built",
          "Limited brand templates currently themed",
          "Requires ~90 min onboarding per user"]),
        ("bl", "Opportunities", "External · Positive", SWOT_OPPORTUNITY,
         ["Q3 rollout to 3 more practice areas",
          "License opportunity to peer firms",
          "Underlying patterns publishable as IP",
          "Train juniors faster on structured argument"]),
        ("br", "Threats", "External · Negative", SWOT_THREAT,
         ["Generic GenAI tools becoming default",
          "Senior consultants resist new tooling",
          "Vendor lock-in risk if scaled wrong",
          "Quality erodes if pattern library bloats"]),
    ]

    for idx, (pos, name, meta, fill, chips) in enumerate(quad_specs):
        col = idx % 2
        row = idx // 2
        x = grid_left + col * (cell_w + 8)
        y = g_top + row * (cell_h + 8)

        # Quadrant background
        q = add_rect(slide, f"quadrant-{pos}", x, y, cell_w, cell_h, fill)
        q.line.color.rgb = CARD_BORDER
        q.line.width = 9525
        # Special focal border on top-left (strengths)
        if pos == "tl":
            q.line.color.rgb = BRAND_PRIMARY
            q.line.width = 25400  # ~2.5pt

        # Header (name + meta)
        add_text(
            slide, f"quadrant-{pos}-name", name,
            x_px=x + 16, y_px=y + 8, w_px=cell_w - 32, h_px=22,
            font_size_px=13, color=BRAND_PRIMARY, bold=True,
            letter_spacing_px=3, uppercase=True,
        )
        add_text(
            slide, f"quadrant-{pos}-label", meta,
            x_px=x + 16, y_px=y + 30, w_px=cell_w - 32, h_px=14,
            font_size_px=8, color=TEXT_MID, bold=True,
            letter_spacing_px=1.2, uppercase=True,
        )

        # Chips (4 bullets)
        body_top = y + 50
        chip_h = (cell_h - 50) // 4
        for ci, text in enumerate(chips):
            cn = ci + 1
            add_text(
                slide, f"quadrant-{pos}-chip-{cn}", "•  " + text,
                x_px=x + 16, y_px=body_top + ci * chip_h, w_px=cell_w - 32, h_px=chip_h,
                font_size_px=11, color=BRAND_PRIMARY,
            )

    add_convergence(
        slide,
        "Strengths and opportunities are stackable. Weaknesses and threats are the work.",
    )

    add_footer(slide, page_num=32)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "32_swot-analysis.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
