"""
Builder for pattern 275: Jobs-to-be-done canvas (4 rows × 3 segments).

Source HTML: _pattern-library/275_jobs-to-be-done-canvas.html

Functional / Emotional / Social / Outcome rows × Segment A/B/C columns.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

OUTCOME_BG = RGBColor(0xF0, 0xFD, 0xF4)
OUTCOME_GREEN = RGBColor(0x16, 0x65, 0x34)
OUTCOME_BAR = RGBColor(0x22, 0xC5, 0x5E)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Jobs-to-be-done canvas — <strong>three customer segments</strong>",
        subtitle="Functional, emotional, and social jobs mapped to pain points and desired outcomes by persona",
    )

    # Table area
    t_left = 48
    t_right = 1280 - 48
    t_top = 234
    t_bottom = 720 - 32 - 12
    t_w = t_right - t_left
    t_h = t_bottom - t_top

    label_w = 130
    seg_w = (t_w - label_w) // 3

    # Header row (brand-primary)
    head_h = 50
    add_rect(slide, "table-head-bg", t_left, t_top, t_w, head_h, BRAND_PRIMARY)
    # Corner cell label
    add_text(
        slide, "table-corner", "Job type",
        x_px=t_left + 12, y_px=t_top, w_px=label_w - 12, h_px=head_h,
        font_size_px=9, color=RGBColor(0xFF, 0xFF, 0xFF), bold=False, anchor="middle",
        uppercase=True, letter_spacing_px=1.5,
    )
    segments = [
        ("Segment A", "CFO / Finance"),
        ("Segment B", "CTO / IT"),
        ("Segment C", "COO / Operations"),
    ]
    for i, (head, sub) in enumerate(segments):
        cx = t_left + label_w + i * seg_w
        n = i + 2
        add_text(
            slide, f"table-col-{n}-header", head,
            x_px=cx + 14, y_px=t_top + 8, w_px=seg_w - 28, h_px=18,
            font_size_px=11, color=WHITE, bold=True, uppercase=True,
            letter_spacing_px=1.2,
        )
        add_text(
            slide, f"table-col-{n}-sub", sub,
            x_px=cx + 14, y_px=t_top + 28, w_px=seg_w - 28, h_px=14,
            font_size_px=9, color=RGBColor(0xC7, 0xB0, 0xE0),
        )

    # Body rows
    rows = [
        ("Functional", "What they need to get done", BRAND_ACCENT,
         ["Reduce cost base by 20% without headcount impact",
          "Migrate legacy systems to cloud with zero downtime",
          "Standardize processes across 14 business units"]),
        ("Emotional", "How they want to feel", BRAND_PRIMARY_MID,
         ["Be seen as the leader who fixed the margin problem",
          "Avoid being responsible for a failed transformation",
          "Gain control over fragmented operations"]),
        ("Social", "How they want to be perceived", TEXT_MID,
         ["Demonstrate ROI discipline to the board",
          "Build credibility as a forward-thinking CTO",
          "Earn trust of BU heads to adopt central standards"]),
        ("Outcome", "Desired end state", OUTCOME_BAR,
         ["Approved 3-year efficiency program by Q2",
          "Cloud migration roadmap signed off by end of year",
          "Unified operating model live in 3 pilot BUs"]),
    ]
    row_h = (t_h - head_h) // len(rows)
    body_top = t_top + head_h

    for ri, (tag, desc, bar_color, cells) in enumerate(rows):
        n = ri + 1
        ry = body_top + ri * row_h
        is_outcome = (tag == "Outcome")
        # Row label cell bg
        add_rect(slide, f"row-{n}-label-bg", t_left, ry, label_w, row_h, CARD_BG)
        # 4px accent bar
        add_rect(slide, f"row-{n}-bar", t_left + 6, ry + 8, 4, row_h - 16, bar_color)
        # Tag
        add_text(
            slide, f"row-{n}-tag", tag,
            x_px=t_left + 18, y_px=ry + 12, w_px=label_w - 30, h_px=14,
            font_size_px=10, color=bar_color, bold=True, uppercase=True,
            letter_spacing_px=1.4,
        )
        # Desc
        add_text(
            slide, f"row-{n}-desc", desc,
            x_px=t_left + 18, y_px=ry + 28, w_px=label_w - 30, h_px=row_h - 36,
            font_size_px=9, color=TEXT_FAINT,
        )

        # Row bottom border
        add_rect(slide, f"row-{n}-rule", t_left, ry, t_w, 1, CARD_BORDER)

        # Cells
        for ci, content in enumerate(cells):
            cn = ci + 2
            cx = t_left + label_w + ci * seg_w
            cell_bg = OUTCOME_BG if is_outcome else WHITE
            add_rect(slide, f"row-{n}-cell-{cn}-bg", cx, ry + 1, seg_w, row_h - 1, cell_bg)
            # vertical separator
            if ci < 2:
                add_rect(slide, f"row-{n}-cell-{cn}-sep", cx + seg_w - 1, ry, 1, row_h, CARD_BORDER)
            cell_color = OUTCOME_GREEN if is_outcome else TEXT_DARK
            cell_bold = is_outcome
            add_text(
                slide, f"row-{n}-cell-{cn}-text", content,
                x_px=cx + 14, y_px=ry, w_px=seg_w - 28, h_px=row_h,
                font_size_px=12, color=cell_color, bold=cell_bold, anchor="middle",
            )

    add_footer(slide, page_num=275)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "275_jobs-to-be-done-canvas.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
