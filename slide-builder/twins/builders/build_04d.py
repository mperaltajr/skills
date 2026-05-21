"""
Builder for pattern 04d: Comparison matrix + convergence — DARK variant.

Light source: twins/builders/build_04.py
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
ROW_LABEL_BG_DARK = RGBColor(0x14, 0x05, 0x28)
RULE_SOFT_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title (32px, h=68 to match light variant offset)
    add_text(
        slide, "title",
        "Other tools skip the hard part — building the argument first.",
        x_px=64, y_px=32, w_px=1000, h_px=68,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Any tool is only as good as the thinking behind it. Both failure modes share the same root cause.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    grid_left = 64
    grid_w = 1280 - 128
    label_w = 200
    cell_w = (grid_w - label_w) // 2
    matrix_top = 240
    row_h = 70
    header_h = 36

    add_rect(slide, "compare-header-rule",
             x_px=grid_left, y_px=matrix_top + header_h - 2,
             w_px=grid_w, h_px=2, fill_color=BRAND_ACCENT_SOFT)

    add_text(
        slide, "compare-col-1-header", "Training Gap",
        x_px=grid_left + label_w + 50, y_px=matrix_top + 4, w_px=cell_w - 70, h_px=22,
        font_size_px=16, color=WHITE, bold=True,
    )
    add_text(
        slide, "compare-col-2-header", "GenAI Gap",
        x_px=grid_left + label_w + cell_w + 50, y_px=matrix_top + 4, w_px=cell_w - 70, h_px=22,
        font_size_px=16, color=BRAND_ACCENT_SOFT, bold=True,
    )

    row_data = [
        ("Root cause",
         "Most consultants never learned the rigor. McKinsey built it in. Most firms didn't — experienced people skip the sharpening step.",
         "Generic AI does what you say. It generates an answer — not yours. No pushback, no conflict detection, no standard."),
        ("What it produces",
         "Pages made repeatedly without knowing the underlying message. Manual fixes at the end.",
         "A complete slide, regardless of whether the thinking is ready."),
        ("Why it persists",
         "Time pressure + no enforced standard = the shortcut always wins.",
         "Output quality depends entirely on input quality — and no one checks the input."),
    ]
    for i, (label, c1, c2) in enumerate(row_data):
        n = i + 1
        ry = matrix_top + header_h + i * row_h
        add_rect(slide, f"compare-row-{n}-label-bg",
                 x_px=grid_left, y_px=ry, w_px=label_w, h_px=row_h, fill_color=ROW_LABEL_BG_DARK)
        add_text(
            slide, f"compare-row-{n}-label", label,
            x_px=grid_left + 14, y_px=ry, w_px=label_w - 28, h_px=row_h,
            font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
            anchor="middle",
        )
        add_text(
            slide, f"compare-row-{n}-col-1-cell", c1,
            x_px=grid_left + label_w + 20, y_px=ry + 8, w_px=cell_w - 40, h_px=row_h - 16,
            font_size_px=12, color=WHITE,
        )
        add_text(
            slide, f"compare-row-{n}-col-2-cell", c2,
            x_px=grid_left + label_w + cell_w + 20, y_px=ry + 8, w_px=cell_w - 40, h_px=row_h - 16,
            font_size_px=12, color=WHITE,
        )
        if i > 0:
            add_rect(slide, f"compare-row-{n}-sep",
                     x_px=grid_left + label_w, y_px=ry,
                     w_px=grid_w - label_w, h_px=1, fill_color=RULE_SOFT_DARK)

    # Convergence band — brand-accent on dark
    conv_y = matrix_top + header_h + 3 * row_h + 24
    conv_h = 56
    add_rect(slide, "convergence-bg",
             x_px=grid_left, y_px=conv_y, w_px=grid_w, h_px=conv_h, fill_color=BRAND_ACCENT)
    add_rect(slide, "convergence-accent",
             x_px=grid_left, y_px=conv_y, w_px=6, h_px=conv_h, fill_color=WHITE)
    add_text(
        slide, "convergence-mark", "“",
        x_px=grid_left + 16, y_px=conv_y + 6, w_px=40, h_px=conv_h - 12,
        font_size_px=28, color=BRAND_ACCENT_SOFT, bold=True, italic=True,
    )
    add_text(
        slide, "convergence",
        "The tool isn't the problem — the unstructured input is. Both failure modes share the same root cause.",
        x_px=grid_left + 56, y_px=conv_y, w_px=grid_w - 80, h_px=conv_h,
        font_size_px=14, color=WHITE, italic=True, bold=False, anchor="middle",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "3",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "04d_comparison-band-headers.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
