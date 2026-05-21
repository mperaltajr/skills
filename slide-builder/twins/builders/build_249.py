"""
Builder for pattern 249: Risk register mini-dashboard (heat map + table + KPI tiles).

Heat map is chart-canvas (SVG). Table is hand-positioned. KPI tiles use metric-* vocab.

Source HTML: _pattern-library/249_risk-register-mini-dashboard.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)
from pptx.dml.color import RGBColor

RAG_RED = RGBColor(0xDC, 0x26, 0x26)
RAG_AMBER = RGBColor(0xD9, 0x77, 0x06)
RAG_GREEN = RGBColor(0x16, 0xA3, 0x4A)
H_BG = RGBColor(0xFD, 0xEC, 0xEC)
H_TXT = RGBColor(0x9B, 0x1C, 0x1C)
M_BG = RGBColor(0xFE, 0xF3, 0xC7)
M_TXT = RGBColor(0x78, 0x35, 0x0F)
L_BG = RGBColor(0xDC, 0xFC, 0xE7)
L_TXT = RGBColor(0x14, 0x53, 0x2D)
RED_ROW_BG = RGBColor(0xFD, 0xF2, 0xF2)
RED_KPI_BG = RGBColor(0xFD, 0xEC, 0xEC)
AMBER_KPI_BG = RGBColor(0xFE, 0xF3, 0xC7)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Risk <strong>exposure</strong> at a glance — mini dashboard.",
        subtitle="Heat map, top 5 risks, and period-on-period trend for the program risk register.",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Body: top:152, left:48, right:48, bottom 32 (small footer in source)
    body_top = 152
    body_h = 530
    gap = 28
    # 38% / 62% split
    left_w = int((1184 - gap) * 0.38)
    right_w = 1184 - gap - left_w
    left_x = 48
    right_x = left_x + left_w + gap

    # Left: heat map
    add_text(slide, "chart-title", "RISK EXPOSURE MAP",
             x_px=left_x, y_px=body_top, w_px=left_w, h_px=16,
             font_size_px=10, color=BRAND_PRIMARY, bold=True, uppercase=True)

    map_top = body_top + 24
    map_h = body_h - 60
    # Chart-canvas placeholder
    canvas = add_rect(slide, "chart-canvas", left_x + 44, map_top, left_w - 44, map_h, CARD_BG)
    canvas.line.color.rgb = CARD_BORDER
    canvas.line.width = 9525
    add_text(slide, "chart-canvas-label",
             "[ 5×5 risk heat map SVG — rendered at twin-gen time ]",
             x_px=left_x + 44, y_px=map_top + map_h // 2 - 12, w_px=left_w - 44, h_px=24,
             font_size_px=10, color=TEXT_MID, italic=True, align="center")
    # Axis labels
    add_text(slide, "quadrant-y-axis-label", "IMPACT",
             x_px=left_x, y_px=map_top + map_h // 2 - 8, w_px=44, h_px=16,
             font_size_px=9, color=TEXT_MID, bold=True, uppercase=True)
    add_text(slide, "quadrant-y-high", "5",
             x_px=left_x + 24, y_px=map_top, w_px=20, h_px=12,
             font_size_px=8, color=TEXT_FAINT, bold=True)
    add_text(slide, "quadrant-y-low", "1",
             x_px=left_x + 24, y_px=map_top + map_h - 14, w_px=20, h_px=12,
             font_size_px=8, color=TEXT_FAINT, bold=True)
    add_text(slide, "quadrant-x-axis-label", "LIKELIHOOD",
             x_px=left_x + 44, y_px=map_top + map_h + 16, w_px=left_w - 44, h_px=16,
             font_size_px=9, color=TEXT_MID, bold=True, uppercase=True, align="center")
    add_text(slide, "quadrant-x-low", "1",
             x_px=left_x + 44, y_px=map_top + map_h + 2, w_px=20, h_px=12,
             font_size_px=8, color=TEXT_FAINT, bold=True)
    add_text(slide, "quadrant-x-high", "5",
             x_px=left_x + left_w - 18, y_px=map_top + map_h + 2, w_px=20, h_px=12,
             font_size_px=8, color=TEXT_FAINT, bold=True)

    # Right: table + KPI tiles
    # Table
    tbl_x = right_x
    tbl_w = right_w
    tbl_top = body_top
    tbl_h = body_h - 110

    # Borders
    tbl_border = add_rect(slide, "table-border", tbl_x, tbl_top, tbl_w, tbl_h, WHITE)
    tbl_border.line.color.rgb = CARD_BORDER
    tbl_border.line.width = 9525

    col_pct = [0.08, 0.36, 0.10, 0.10, 0.22, 0.14]
    col_w = [int(tbl_w * p) for p in col_pct]
    col_w[-1] = tbl_w - sum(col_w[:-1])
    col_x_arr = [tbl_x]
    for w in col_w[:-1]:
        col_x_arr.append(col_x_arr[-1] + w)

    # Header
    header_h = 30
    add_rect(slide, "table-head-bg", tbl_x, tbl_top, tbl_w, header_h, BRAND_PRIMARY)
    headers = ["ID", "Description", "Impact", "Likelihood", "Owner", "Trend"]
    centered = {0, 2, 3, 5}
    for i, h in enumerate(headers):
        align = "center" if i in centered else "left"
        add_text(slide, f"table-col-{i+1}-header", h,
                 x_px=col_x_arr[i] + 8, y_px=tbl_top + 8, w_px=col_w[i] - 16, h_px=14,
                 font_size_px=9, color=WHITE, bold=True, align=align, uppercase=True)

    # Rows
    rows = [
        ("R1", "Stakeholder withdrawal mid-programme", "H", "H", "M. Peralta", "↑", True, RAG_RED),
        ("R2", "Scope creep beyond programme charter", "H", "H", "A. Singh", "↑", True, RAG_RED),
        ("R3", "Resource constraints in Wave 2", "M", "M", "J. Torres", "→", False, RAG_AMBER),
        ("R4", "Vendor tooling provisioning delay", "M", "H", "PMO", "→", False, RAG_AMBER),
        ("R5", "Change management adoption lag", "M", "L", "L. Reyes", "↓", False, RAG_GREEN),
    ]
    row_h = (tbl_h - header_h) // len(rows)
    body_y = tbl_top + header_h
    for i, (rid, desc, imp, lik, owner, trend, is_red, trend_color) in enumerate(rows):
        n = i + 1
        ry = body_y + i * row_h
        row_bg = RED_ROW_BG if is_red else WHITE
        add_rect(slide, f"table-row-{n}-bg", tbl_x, ry, tbl_w, row_h, row_bg)
        if is_red:
            add_rect(slide, f"table-row-{n}-flag", tbl_x, ry, 3, row_h, RAG_RED)
        # ID
        add_text(slide, f"table-row-{n}-num", rid,
                 x_px=col_x_arr[0], y_px=ry + row_h // 2 - 9, w_px=col_w[0], h_px=18,
                 font_size_px=11, color=BRAND_ACCENT, bold=True, align="center")
        # Desc
        add_text(slide, f"table-row-{n}-cell-2", desc,
                 x_px=col_x_arr[1] + 8, y_px=ry + 8, w_px=col_w[1] - 16, h_px=row_h - 12,
                 font_size_px=11, color=TEXT_DARK, bold=True)
        # Impact pill
        if imp == "H":
            ibg, itxt = H_BG, H_TXT
        elif imp == "M":
            ibg, itxt = M_BG, M_TXT
        else:
            ibg, itxt = L_BG, L_TXT
        add_text(slide, f"table-row-{n}-cell-3", imp,
                 x_px=col_x_arr[2] + (col_w[2] - 28) // 2, y_px=ry + row_h // 2 - 8, w_px=28, h_px=16,
                 font_size_px=10, color=itxt, bold=True, align="center",
                 bg_fill=ibg, padding_px=(2, 4, 2, 4))
        # Likelihood pill
        if lik == "H":
            lbg, ltxt = H_BG, H_TXT
        elif lik == "M":
            lbg, ltxt = M_BG, M_TXT
        else:
            lbg, ltxt = L_BG, L_TXT
        add_text(slide, f"table-row-{n}-cell-4", lik,
                 x_px=col_x_arr[3] + (col_w[3] - 28) // 2, y_px=ry + row_h // 2 - 8, w_px=28, h_px=16,
                 font_size_px=10, color=ltxt, bold=True, align="center",
                 bg_fill=lbg, padding_px=(2, 4, 2, 4))
        # Owner
        add_text(slide, f"table-row-{n}-cell-5", owner,
                 x_px=col_x_arr[4] + 8, y_px=ry + row_h // 2 - 9, w_px=col_w[4] - 16, h_px=18,
                 font_size_px=11, color=TEXT_DARK)
        # Trend
        add_text(slide, f"table-row-{n}-cell-6", trend,
                 x_px=col_x_arr[5], y_px=ry + row_h // 2 - 10, w_px=col_w[5], h_px=20,
                 font_size_px=15, color=trend_color, bold=True, align="center")
        # Row divider
        if i < len(rows) - 1:
            add_rect(slide, f"table-row-{n}-divider", tbl_x, ry + row_h - 1, tbl_w, 1, CARD_BORDER)

    # KPI tiles row (3 tiles below table)
    kpi_top = tbl_top + tbl_h + 14
    kpi_h = body_h - tbl_h - 14
    kpi_gap = 10
    kpi_w = (tbl_w - 2 * kpi_gap) // 3

    kpis = [
        ("metric-1", "2", "HIGH RISKS", RED_KPI_BG, RAG_RED, H_TXT),
        ("metric-2", "3", "MEDIUM RISKS", AMBER_KPI_BG, RAG_AMBER, M_TXT),
        ("metric-3", "↑ INCREASING", "RISK TREND", RED_KPI_BG, RAG_RED, H_TXT),
    ]
    for i, (prefix, val, lab, bg, accent, txt_c) in enumerate(kpis):
        n = i + 1
        kx = tbl_x + i * (kpi_w + kpi_gap)
        add_rect(slide, f"{prefix}-tile", kx, kpi_top, kpi_w, kpi_h, bg)
        add_rect(slide, f"{prefix}-bar", kx, kpi_top, 3, kpi_h, accent)
        if i == 2:
            # Label on top, value below for trend
            add_text(slide, f"{prefix}-label", lab,
                     x_px=kx + 14, y_px=kpi_top + 10, w_px=kpi_w - 28, h_px=14,
                     font_size_px=9, color=txt_c, bold=True, uppercase=True)
            add_text(slide, f"{prefix}-value", val,
                     x_px=kx + 14, y_px=kpi_top + 26, w_px=kpi_w - 28, h_px=30,
                     font_size_px=14, color=accent, bold=True)
        else:
            add_text(slide, f"{prefix}-value", val,
                     x_px=kx + 14, y_px=kpi_top + 10, w_px=kpi_w - 28, h_px=30,
                     font_size_px=22, color=accent, bold=True)
            add_text(slide, f"{prefix}-label", lab,
                     x_px=kx + 14, y_px=kpi_top + 42, w_px=kpi_w - 28, h_px=16,
                     font_size_px=10, color=txt_c, bold=True, uppercase=True)

    add_footer(slide, page_num=249)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "249_risk-register-mini-dashboard.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
