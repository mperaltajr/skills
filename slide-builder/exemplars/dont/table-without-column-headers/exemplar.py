"""
Data Tables / table-without-column-headers — anti-exemplar.

Family: Data Tables (also relevant to Comparison)
Verdict: dont

What this slide does WRONG:
- Renders 4 parallel rows of numeric data in a 4-column grid with NO header row.
- The reader sees a wall of cells like "[Workstream A]  [$X.XM]  [Y FTE]  [Z%]"
  but cannot tell what each column is supposed to represent. Is the first
  number annual cost? Run-rate? Forecast? Is the percentage utilization,
  variance, or share? The grid is unparsable.
- A "[Total]" row appears at the bottom with three numbers but no label
  cell saying "Total" — the totals just float, anchored to nothing.

This is a deliberate reproduction of a real failure from a build run where
parallel rows of structured numeric data were rendered as a bare grid.

What this slide should have done instead — see WHY.md:
- Use the `add_table(slide, headers=[...], rows=[...])` helper, which REQUIRES
  a `headers` argument (no default) so the failure is impossible by construction.
- If hand-building parallel rows with `add_rect` + `add_text`, the first row
  must be an explicit header row labelling each column, and the totals row
  must have a "Total" label cell aligned with the rest of the grid.

Rulebook citations (what is being violated):
- designer-brief.md § 4 Data Tables: "Parallel rows of numeric values that don't
  strictly use `add_table` still need labeled column headers — the rule applies
  to any tabular content."
- designer-brief.md § 4 Data Tables: "Header row in BRAND_PRIMARY band with
  WHITE text, banded rows for legibility…" — this slide has no header at all.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY,
    TEXT_DARK, TEXT_MID,
    CARD_BORDER,
)


def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="[Workstream cost comparison placeholder]",
        subtitle="[Sub-headline placeholder: what is being compared, over what period]",
    )

    # === Parallel 4-column grid — built with add_rect dividers + add_text cells ===
    # 4 columns: row label | metric 1 | metric 2 | metric 3
    # NO HEADER ROW — this is the failure being illustrated.
    grid_x = 64
    grid_y = 180
    grid_w = 1280 - 128             # 1152 px
    col_label_w = 360
    col_metric_w = (grid_w - col_label_w) // 3   # 264 px each
    row_h = 56

    col_x = [
        grid_x,
        grid_x + col_label_w,
        grid_x + col_label_w + col_metric_w,
        grid_x + col_label_w + 2 * col_metric_w,
    ]
    col_w = [col_label_w, col_metric_w, col_metric_w, col_metric_w]

    # Five rows of parallel numeric data — bare cells, no header row above them.
    rows = [
        ("[Workstream A]", "[$X.XM]", "[Y FTE]",   "[Z%]"),
        ("[Workstream B]", "[$X.XM]", "[Y FTE]",   "[Z%]"),
        ("[Workstream C]", "[$X.XM]", "[Y FTE]",   "[Z%]"),
        ("[Workstream D]", "[$X.XM]", "[Y FTE]",   "[Z%]"),
        ("[Workstream E]", "[$X.XM]", "[Y FTE]",   "[Z%]"),
    ]

    for i, row_cells in enumerate(rows):
        n = i + 1
        ry = grid_y + i * row_h

        # Hairline divider above each row (except the first)
        if i > 0:
            add_rect(
                slide, f"row-{n}-divider",
                x_px=grid_x, y_px=ry, w_px=grid_w, h_px=1,
                fill_color=CARD_BORDER,
            )

        for c, cell_text in enumerate(row_cells):
            align = "left" if c == 0 else "right"
            color = TEXT_DARK if c == 0 else TEXT_MID
            add_text(
                slide, f"row-{n}-col-{c}", cell_text,
                x_px=col_x[c] + (8 if c == 0 else 0),
                y_px=ry + 16,
                w_px=col_w[c] - (16 if c == 0 else 16),
                h_px=row_h - 16,
                font_size_px=14, color=color, align=align,
            )

    # Divider below the last data row
    rows_bottom_y = grid_y + len(rows) * row_h
    add_rect(
        slide, "rows-bottom-divider",
        x_px=grid_x, y_px=rows_bottom_y, w_px=grid_w, h_px=1,
        fill_color=CARD_BORDER,
    )

    # === Floating totals row — three numbers, NO "Total" label cell ===
    # The totals appear in the metric columns but the first column (where
    # "Total" should live) is left blank. The numbers float without anchor.
    totals_y = rows_bottom_y + 16
    totals = ("", "[$XX.XM]", "[YY FTE]", "[ZZ%]")
    for c, cell_text in enumerate(totals):
        if not cell_text:
            continue
        add_text(
            slide, f"totals-col-{c}", cell_text,
            x_px=col_x[c], y_px=totals_y,
            w_px=col_w[c] - 16, h_px=32,
            font_size_px=18, color=BRAND_PRIMARY, bold=True,
            align="right",
        )

    add_footer(slide, page_num=2)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
