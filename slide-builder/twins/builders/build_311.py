"""
Builder for pattern 311: Leading vs Lagging indicators — two columns with center arrow.

Includes a green/amber status legend below the subheadline (right-aligned) for the
indicator rows on both sides.

Source HTML: _pattern-library/311_leading-lagging-indicators.html
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

STATUS_GREEN = RGBColor(0x22, 0xC5, 0x5E)
STATUS_AMBER = RGBColor(0xF5, 0x9E, 0x0B)
STATUS_RED = RGBColor(0xEF, 0x44, 0x44)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Leading vs <strong>Lagging Indicators</strong>",
        subtitle="Predictive signals that shape outcomes — and the results that confirm them",
        title_x=48, title_y=44, title_w=900, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # ── Legend (below subheadline, right-aligned) ──
    leg_h = 32
    leg_y = 232
    leg_right = 1232
    items = [("On Plan", STATUS_GREEN), ("Watch", STATUS_AMBER)]
    item_w = 92
    leg_w = len(items) * item_w + 16
    leg_x = leg_right - leg_w
    leg_bg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, CARD_BG)
    leg_bg.line.color.rgb = CARD_BORDER
    leg_bg.line.width = 9525
    cur_x = leg_x + 12
    for i, (lbl, col) in enumerate(items):
        n = i + 1
        add_rect(slide, f"legend-{n}-swatch", cur_x, leg_y + (leg_h - 8) // 2, 14, 8, col)
        add_text(
            slide, f"legend-{n}-label", lbl,
            x_px=cur_x + 22, y_px=leg_y, w_px=item_w - 26, h_px=leg_h,
            font_size_px=10, color=TEXT_DARK, bold=True, anchor="middle",
        )
        cur_x += item_w

    # ── Body: two columns + center divider with arrow ──
    body_top = 280
    body_bottom = 670  # stay clear of invariant zone (≥672)
    body_h = body_bottom - body_top
    left_x = 48
    center_x = 600
    center_w = 80
    right_x = center_x + center_w
    col_w = (1280 - 48 * 2 - center_w) // 2

    # Column headers
    for ci, (cx, head, sub) in enumerate([
        (left_x, "Leading Indicators", "Predictive · Forward-looking"),
        (right_x, "Lagging Indicators", "Outcome · Backward-looking"),
    ]):
        cn = ci + 1
        # header band
        hdr_h = 40
        head_bg = add_rect(slide, f"col-{cn}-header-bg", cx, body_top, col_w, hdr_h, CARD_BG)
        head_bg.line.color.rgb = CARD_BORDER
        head_bg.line.width = 9525
        add_text(
            slide, f"col-{cn}-header", head,
            x_px=cx + 14, y_px=body_top + 4, w_px=col_w - 28, h_px=20,
            font_size_px=14, color=BRAND_PRIMARY, bold=True,
        )
        add_text(
            slide, f"col-{cn}-sub", sub,
            x_px=cx + 14, y_px=body_top + 22, w_px=col_w - 28, h_px=14,
            font_size_px=10, color=TEXT_FAINT, italic=True,
        )

    # Rows
    leading_rows = [
        ("Pipeline Coverage Ratio", "3.8× target · ↑ from 3.2×", "green"),
        ("Qualified Leads / Week", "42 leads · +18% WoW", "green"),
        ("Training Completion %", "67% · target 80%", "amber"),
        ("Net Promoter Score", "NPS +52 · ↑ 4pts QoQ", "green"),
        ("Avg. Response Time", "4.2 hrs · SLA = 3.0 hrs", "amber"),
    ]
    lagging_rows = [
        ("Quarterly Revenue", "$4.2M · +11% vs plan", "green"),
        ("Win Rate", "38% · ↑ from 31%", "green"),
        ("Employee Attrition", "14% annual · target 10%", "amber"),
        ("Customer Retention", "91% · ↑ 3pts YoY", "green"),
        ("Cost per Acquisition", "$1,840 · target $1,500", "amber"),
    ]
    status_map = {"green": STATUS_GREEN, "amber": STATUS_AMBER, "red": STATUS_RED}

    rows_top = body_top + 50
    rows_h = body_h - 50
    row_h = (rows_h - 8) // 5

    for side_idx, (cx, rows) in enumerate([(left_x, leading_rows), (right_x, lagging_rows)]):
        side = "L" if side_idx == 0 else "R"
        for ri, (name, value, status) in enumerate(rows):
            rn = ri + 1
            ry = rows_top + ri * row_h
            # row background alt
            row_bg = WHITE if ri % 2 == 0 else CARD_BG
            row = add_rect(slide, f"col-{side}-row-{rn}-bg", cx, ry, col_w, row_h - 4, row_bg)
            row.line.fill.background()
            # status bar (left edge, vertical)
            add_rect(slide, f"col-{side}-row-{rn}-bar",
                     cx, ry, 4, row_h - 4, status_map[status])
            # Indicator name
            add_text(
                slide, f"col-{side}-row-{rn}-name", name,
                x_px=cx + 14, y_px=ry + 8, w_px=col_w - 30, h_px=20,
                font_size_px=12, color=TEXT_DARK, bold=True,
            )
            # value
            add_text(
                slide, f"col-{side}-row-{rn}-value", value,
                x_px=cx + 14, y_px=ry + 28, w_px=col_w - 30, h_px=16,
                font_size_px=10, color=TEXT_MID,
            )

    # ── Center divider: DRIVE label + arrow ──
    add_text(
        slide, "drive-label", "DRIVE",
        x_px=center_x, y_px=rows_top + rows_h // 2 - 24, w_px=center_w, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True, letter_spacing_px=1.6,
        align="center",
    )
    # Arrow rectangle stand-in for SVG: horizontal line + chevron rect
    arr_y = rows_top + rows_h // 2 - 4
    add_rect(slide, "drive-arrow-shaft", center_x + 12, arr_y, center_w - 40, 4, BRAND_ACCENT)
    add_rect(slide, "drive-arrow-head1", center_x + center_w - 32, arr_y - 6, 4, 16, BRAND_ACCENT)
    add_rect(slide, "drive-arrow-head2", center_x + center_w - 24, arr_y - 4, 4, 12, BRAND_ACCENT)
    add_rect(slide, "drive-arrow-head3", center_x + center_w - 16, arr_y - 2, 4, 8, BRAND_ACCENT)

    add_footer(slide, page_num=311)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "311_leading-lagging-indicators.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
