"""
Builder for pattern 44: KPI scorecard table.

7 columns: Pillar / KPI / Actual / Target / Status / Trend / Comments.
7 KPI rows grouped under 4 pillars. RAG legend in top-right corner.

Source HTML: _pattern-library/44_kpi-scorecard-table.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

RAG_GREEN = RGBColor(0x2E, 0xCC, 0x71)
RAG_AMBER = RGBColor(0xF3, 0x9C, 0x12)
RAG_RED = RGBColor(0xDC, 0x26, 0x26)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title block (smaller, with eyebrow)
    add_text(
        slide, "eyebrow", "Pilot scorecard · week 4",
        x_px=48, y_px=50, w_px=900, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=2, uppercase=True,
    )
    add_text(
        slide, "title",
        "Slide Lab scorecard — week 4, three pillars green, one to watch.",
        x_px=48, y_px=66, w_px=900, h_px=44,
        font_size_px=24, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Four strategic pillars, seven KPIs. Status and trend versus baseline; comments flag where steering attention is needed.",
        x_px=48, y_px=112, w_px=900, h_px=36,
        font_size_px=12, color=TEXT_MID,
    )
    add_rect(slide, "brand-rule", x_px=48, y_px=148, w_px=56, h_px=3, fill_color=BRAND_ACCENT)

    # RAG legend — below subheadline+brand-rule, right-aligned (right edge ≈ 1216)
    leg_w = 270
    leg_h = 44
    leg_x = 1216 - leg_w
    leg_y = 160
    leg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, RGBColor(0xFB, 0xFA, 0xFD))
    leg.line.color.rgb = CARD_BORDER
    leg.line.width = 9525
    add_text(
        slide, "legend-title", "RAG",
        x_px=leg_x + 10, y_px=leg_y + 15, w_px=30, h_px=14,
        font_size_px=8, color=TEXT_MID, bold=True,
        letter_spacing_px=1.2, uppercase=True, align="left",
    )
    swatches = [(RAG_GREEN, "Green"), (RAG_AMBER, "Amber"), (RAG_RED, "Red")]
    item_y = leg_y + 14
    item_x = leg_x + 50
    for li, (col, lbl) in enumerate(swatches):
        n = li + 1
        add_rect(slide, f"legend-{n}-swatch", item_x, item_y + 4, 8, 8, col)
        add_text(
            slide, f"legend-{n}-label", lbl,
            x_px=item_x + 12, y_px=item_y, w_px=60, h_px=18,
            font_size_px=9, color=TEXT_DARK, bold=True, anchor="middle",
            letter_spacing_px=1, uppercase=True,
        )
        item_x += 72

    # Table — pushed down to clear legend (legend bottom ≈ 204)
    table_top = 220
    table_left = 48
    table_right = 1280 - 48
    table_w = table_right - table_left
    col_widths_pct = [14, 24, 9, 9, 10, 10, 24]
    col_widths = [int(table_w * p / 100) for p in col_widths_pct]
    col_x = [table_left]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)

    # Header row (brand-primary, white text)
    header_h = 32
    add_rect(slide, "table-header-bg", table_left, table_top, table_w, header_h, BRAND_PRIMARY)
    headers = ["Strategy pillar", "KPI", "Actual", "Target", "Status", "Trend", "Comments"]
    for ci, h in enumerate(headers):
        cn = ci + 1
        align = "center" if 2 <= ci <= 5 else "left"
        add_text(
            slide, f"table-col-{cn}-header", h,
            x_px=col_x[ci] + 10, y_px=table_top, w_px=col_widths[ci] - 20, h_px=header_h,
            font_size_px=9, color=WHITE, bold=True, anchor="middle",
            letter_spacing_px=1.4, uppercase=True, align=align,
        )

    # Rows data (7 rows, 4 pillar groupings)
    rows = [
        # (pillar_n, kpi, actual, target, rag, trend_text, comment)
        (1, "Cycle time", "Days to partner-ready", "5d", "<7d", "green", "▼ -64%", "Holding under baseline since W2"),
        (1, "Cycle time", "First-review pass rate", "94%", ">85%", "green", "▲ +34pp", "Driven by storyline coaching"),
        (2, "Quality", "Partner edits per deck", "3", "<4", "green", "▼ -63%", "Edits now sharpening, not redoing"),
        (2, "Quality", "Stakeholder sign-off rate", "94%", ">80%", "green", "■ stable", "Maintained through wave 1"),
        (3, "Adoption", "Active users vs target", "4/4", "4/4", "green", "■ flat", "Full pilot team engaged"),
        (3, "Adoption", "Sessions per user / week", "1.8", ">2", "amber", "▼ slightly", "Senior users less consistent — coach by Wed"),
        (4, "Cost", "Hours per deck saved", "18h", ">12h", "green", "▲ +6h", "Net of onboarding"),
    ]
    rag_color_map = {"green": RAG_GREEN, "amber": RAG_AMBER, "red": RAG_RED}
    rag_pill_bg_map = {
        "green": RGBColor(0xDC, 0xF4, 0xE0),
        "amber": RGBColor(0xFD, 0xF1, 0xD7),
        "red": RGBColor(0xFA, 0xDD, 0xDD),
    }

    row_h = 50
    body_top = table_top + header_h

    # Detect pillar group spans
    prev_pillar = 0
    pillar_start_row = 0
    pillar_groups = []  # (pillar_n, pillar_name, start_idx, count)
    for i, r in enumerate(rows):
        p_n, p_name = r[0], r[1]
        if p_n != prev_pillar:
            if prev_pillar > 0:
                pillar_groups.append((prev_pillar, rows[pillar_start_row][1], pillar_start_row, i - pillar_start_row))
            prev_pillar = p_n
            pillar_start_row = i
    pillar_groups.append((prev_pillar, rows[pillar_start_row][1], pillar_start_row, len(rows) - pillar_start_row))

    # Draw rows
    for i, (p_n, p_name, kpi, actual, target, rag, trend, comment) in enumerate(rows):
        ry = body_top + i * row_h
        # Row background (focal=amber row)
        is_focal = (rag == "amber")
        row_bg = RGBColor(0xFD, 0xF7, 0xE8) if is_focal else WHITE
        add_rect(slide, f"table-row-{i+1}-bg", table_left, ry, table_w, row_h, row_bg)
        # Row top divider
        add_rect(slide, f"table-row-{i+1}-rule", table_left, ry, table_w, 1, CARD_BORDER)

        # KPI label
        add_text(
            slide, f"table-row-{i+1}-cell-2", kpi,
            x_px=col_x[1] + 10, y_px=ry, w_px=col_widths[1] - 20, h_px=row_h,
            font_size_px=12, color=BRAND_PRIMARY_MID if is_focal else TEXT_DARK,
            bold=True, anchor="middle",
        )
        # Actual
        add_text(
            slide, f"table-row-{i+1}-cell-3", actual,
            x_px=col_x[2], y_px=ry, w_px=col_widths[2], h_px=row_h,
            font_size_px=13, color=TEXT_DARK, bold=True, align="center", anchor="middle",
        )
        # Target
        add_text(
            slide, f"table-row-{i+1}-cell-4", target,
            x_px=col_x[3], y_px=ry, w_px=col_widths[3], h_px=row_h,
            font_size_px=12, color=TEXT_MID, align="center", anchor="middle",
        )
        # Status pill
        pill_x = col_x[4] + (col_widths[4] - 70) // 2
        pill_y = ry + (row_h - 18) // 2
        add_rect(slide, f"table-row-{i+1}-status-pill", pill_x, pill_y, 70, 18, rag_pill_bg_map[rag])
        add_rect(slide, f"table-row-{i+1}-rag-dot", pill_x + 6, pill_y + 6, 6, 6, rag_color_map[rag])
        add_text(
            slide, f"table-row-{i+1}-status-pill-text", rag.upper(),
            x_px=pill_x + 14, y_px=pill_y, w_px=56, h_px=18,
            font_size_px=9, color=rag_color_map[rag], bold=True, align="center", anchor="middle",
            letter_spacing_px=1.2,
        )
        # Trend
        add_text(
            slide, f"table-row-{i+1}-cell-6", trend,
            x_px=col_x[5], y_px=ry, w_px=col_widths[5], h_px=row_h,
            font_size_px=11, color=TEXT_DARK, bold=True, align="center", anchor="middle",
        )
        # Comments
        add_text(
            slide, f"table-row-{i+1}-cell-7", comment,
            x_px=col_x[6] + 10, y_px=ry, w_px=col_widths[6] - 20, h_px=row_h,
            font_size_px=11, color=TEXT_MID, anchor="middle",
        )

    # Pillar cells (rowspan groupings)
    for p_n, p_name, start, count in pillar_groups:
        py = body_top + start * row_h
        ph = count * row_h
        add_rect(slide, f"table-pillar-{p_n}-cell", table_left, py, col_widths[0], ph, CARD_BG)
        add_text(
            slide, f"table-pillar-{p_n}-num", f"Pillar {p_n}",
            x_px=table_left + 12, y_px=py + 8, w_px=col_widths[0] - 24, h_px=14,
            font_size_px=9, color=BRAND_ACCENT, bold=True,
            letter_spacing_px=1.6, uppercase=True,
        )
        add_text(
            slide, f"table-pillar-{p_n}-name", p_name,
            x_px=table_left + 12, y_px=py + 24, w_px=col_widths[0] - 24, h_px=ph - 30,
            font_size_px=11, color=BRAND_PRIMARY, bold=True,
            letter_spacing_px=1.2, uppercase=True,
        )

    # Convergence (special gradient/band in pattern 44)
    conv_y = 632
    conv_h = 50
    add_rect(slide, "convergence-bg", x_px=48, y_px=conv_y, w_px=1280 - 96, h_px=conv_h,
             fill_color=BRAND_PRIMARY)
    add_rect(slide, "convergence-mark", x_px=64, y_px=conv_y + 14, w_px=80, h_px=22,
             fill_color=BRAND_PRIMARY)
    add_text(
        slide, "convergence-mark-text", "SO WHAT",
        x_px=64, y_px=conv_y + 14, w_px=80, h_px=22,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center", anchor="middle",
        letter_spacing_px=1.6, uppercase=True,
    )
    add_text(
        slide, "convergence",
        "Three pillars green, one amber. The amber one — senior-user session frequency — is where steering should focus this week.",
        x_px=160, y_px=conv_y, w_px=1280 - 96 - 112, h_px=conv_h,
        font_size_px=13, color=WHITE, anchor="middle",
    )

    add_footer(slide, page_num=44)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "44_kpi-scorecard-table.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
