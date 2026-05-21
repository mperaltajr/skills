"""
Builder for pattern 04: Comparison matrix + convergence.

Source HTML: _pattern-library/04_comparison-band-headers.html
2-column comparison with row labels + a convergence band at the bottom.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

ROW_LABEL_BG = RGBColor(0xF5, 0xF0, 0xFA)
RULE_SOFT = RGBColor(0xEA, 0xDC, 0xF3)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Other tools skip the hard part — building the argument first.",
        subtitle="Any tool is only as good as the thinking behind it. Both failure modes share the same root cause.",
        title_h=68,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Matrix layout: 200px row-label column + 2 equal cells
    grid_left = 64
    grid_w = 1280 - 128
    label_w = 200
    cell_w = (grid_w - label_w) // 2
    matrix_top = 240
    row_h = 70
    header_h = 36

    # Header row (2px brand-primary bottom border)
    # Blank header for row-label column (just bottom border)
    add_rect(slide, "compare-header-rule",
             x_px=grid_left, y_px=matrix_top + header_h - 2,
             w_px=grid_w, h_px=2, fill_color=BRAND_PRIMARY)

    # Column header 1
    add_text(
        slide, "compare-col-1-icon", "",
        x_px=grid_left + label_w + 22, y_px=matrix_top + 4, w_px=22, h_px=22,
    )
    add_text(
        slide, "compare-col-1-header", "Training Gap",
        x_px=grid_left + label_w + 50, y_px=matrix_top + 4, w_px=cell_w - 70, h_px=22,
        font_size_px=16, color=BRAND_PRIMARY, bold=True,
    )

    # Column header 2
    add_text(
        slide, "compare-col-2-icon", "",
        x_px=grid_left + label_w + cell_w + 22, y_px=matrix_top + 4, w_px=22, h_px=22,
    )
    add_text(
        slide, "compare-col-2-header", "GenAI Gap",
        x_px=grid_left + label_w + cell_w + 50, y_px=matrix_top + 4, w_px=cell_w - 70, h_px=22,
        font_size_px=16, color=BRAND_PRIMARY_MID, bold=True,
    )

    # Rows
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
        # Row label background
        add_rect(slide, f"compare-row-{n}-label-bg",
                 x_px=grid_left, y_px=ry, w_px=label_w, h_px=row_h, fill_color=ROW_LABEL_BG)
        add_text(
            slide, f"compare-row-{n}-label", label,
            x_px=grid_left + 14, y_px=ry, w_px=label_w - 28, h_px=row_h,
            font_size_px=11, color=BRAND_PRIMARY, bold=True, uppercase=True,
            anchor="middle",
        )
        # Cell 1
        add_text(
            slide, f"compare-row-{n}-col-1-cell", c1,
            x_px=grid_left + label_w + 20, y_px=ry + 8, w_px=cell_w - 40, h_px=row_h - 16,
            font_size_px=12, color=TEXT_DARK,
        )
        # Cell 2
        add_text(
            slide, f"compare-row-{n}-col-2-cell", c2,
            x_px=grid_left + label_w + cell_w + 20, y_px=ry + 8, w_px=cell_w - 40, h_px=row_h - 16,
            font_size_px=12, color=TEXT_DARK,
        )
        # Row separator
        if i > 0:
            add_rect(slide, f"compare-row-{n}-sep",
                     x_px=grid_left + label_w, y_px=ry,
                     w_px=grid_w - label_w, h_px=1, fill_color=RULE_SOFT)

    # Convergence band — brand-primary, 60px, left accent
    conv_y = matrix_top + header_h + 3 * row_h + 24
    conv_h = 56
    add_rect(slide, "convergence-bg",
             x_px=grid_left, y_px=conv_y, w_px=grid_w, h_px=conv_h, fill_color=BRAND_PRIMARY)
    # Left 6px brand-accent strip
    add_rect(slide, "convergence-accent",
             x_px=grid_left, y_px=conv_y, w_px=6, h_px=conv_h, fill_color=BRAND_ACCENT)
    # Convergence mark
    add_text(
        slide, "convergence-mark", "“",
        x_px=grid_left + 16, y_px=conv_y + 6, w_px=40, h_px=conv_h - 12,
        font_size_px=28, color=BRAND_ACCENT_SOFT, bold=True, italic=True,
    )
    # Convergence text
    add_text(
        slide, "convergence",
        "The tool isn't the problem — the unstructured input is. Both failure modes share the same root cause.",
        x_px=grid_left + 56, y_px=conv_y, w_px=grid_w - 80, h_px=conv_h,
        font_size_px=14, color=WHITE, italic=True, bold=False, anchor="middle",
    )

    add_footer(slide, page_num=3)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "04_comparison-band-headers.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
