"""
Builder for pattern 193: Benefits Realization Tracker.

7-row table with progress bars, RAG pills, owner column, total row.
Summary stat top-right.

Source HTML: _pattern-library/193_benefits-realization-tracker.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

GREEN = RGBColor(0x22, 0xC5, 0x5E)
GREEN_BG = RGBColor(0xDC, 0xFC, 0xE7)
GREEN_TXT = RGBColor(0x16, 0x65, 0x34)
AMBER = RGBColor(0xEA, 0xB3, 0x08)
AMBER_BG = RGBColor(0xFE, 0xF9, 0xC3)
AMBER_TXT = RGBColor(0x85, 0x4D, 0x0E)
RED = RGBColor(0xEF, 0x44, 0x44)
RED_BG = RGBColor(0xFE, 0xE2, 0xE2)
RED_TXT = RGBColor(0x99, 0x1B, 0x1B)
ORANGE = RGBColor(0xF5, 0x9E, 0x0B)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Benefits Realization <strong>Tracker</strong>",
        subtitle="YTD performance against committed benefit targets across all workstreams",
        title_h=42, subtitle_h=20, brand_rule_w=64, title_w=900,
    )

    # Summary stat top-right
    add_text(slide, "summary-stat-value", "$42M",
             x_px=1280 - 64 - 220, y_px=60, w_px=220, h_px=28,
             font_size_px=20, color=BRAND_ACCENT, bold=True, align="right")
    add_text(slide, "summary-stat-label", "benefits realized YTD",
             x_px=1280 - 64 - 220, y_px=88, w_px=220, h_px=18,
             font_size_px=11, color=TEXT_MID, align="right")

    # Table
    tbl_top = 168
    tbl_bot = 600
    tbl_left = 64
    tbl_w = 1280 - 128
    # Column widths (in %): 26 / 12 / 13 / 18 / 16 / 15
    col_pcts = [26, 12, 13, 18, 16, 15]
    col_xs = [tbl_left]
    for p in col_pcts[:-1]:
        col_xs.append(col_xs[-1] + int(tbl_w * p / 100))
    col_widths = [int(tbl_w * p / 100) for p in col_pcts]

    # Header
    hdr_h = 32
    add_rect(slide, "table-header-bg", tbl_left, tbl_top, tbl_w, hdr_h, BRAND_PRIMARY)
    headers = ["Benefit", "Target", "Actual (YTD)", "% Achieved", "Status", "Owner"]
    aligns = ["left", "right", "right", "right", "center", "center"]
    for i, (h, a) in enumerate(zip(headers, aligns)):
        add_text(slide, f"table-col-{i+1}-header", h,
                 x_px=col_xs[i] + 10, y_px=tbl_top + 8, w_px=col_widths[i] - 20, h_px=18,
                 font_size_px=10, color=WHITE, bold=True, uppercase=True, align=a)

    # Rows
    rows = [
        ("Procurement Cost Savings", "Cost Reduction", "$18.0M", "$15.3M", 85, "on", "J. Reeves"),
        ("New Revenue Streams", "Revenue Growth", "$12.0M", "$7.2M", 60, "risk", "S. Patel"),
        ("Process Automation Gains", "Efficiency / FTE", "$9.5M", "$8.6M", 91, "on", "L. Tran"),
        ("Regulatory Penalty Avoidance", "Compliance / Risk", "$5.0M", "$2.1M", 42, "behind", "A. Mwangi"),
        ("Customer Satisfaction Uplift", "NPS / Experience", "$6.0M", "$5.5M", 92, "on", "C. Okonkwo"),
        ("Talent Retention Value", "People / Attrition", "$6.2M", "$3.3M", 53, "risk", "D. Flores"),
        ("Total Benefits", "All workstreams", "$56.7M", "$42.0M", 74, "on", "PMO"),
    ]
    row_h = (tbl_bot - tbl_top - hdr_h) // 7
    for i, (name, typ, tgt, act, pct, status, owner) in enumerate(rows):
        ry = tbl_top + hdr_h + i * row_h
        n = i + 1
        is_total = (i == 6)
        bg = BRAND_PRIMARY if is_total else (CARD_BG if i % 2 == 0 else WHITE)
        add_rect(slide, f"table-row-{n}-bg", tbl_left, ry, tbl_w, row_h, bg)
        # Cell 1: name + type
        n_color = WHITE if is_total else BRAND_PRIMARY
        t_color = RGBColor(0xCC, 0xCC, 0xDD) if is_total else TEXT_FAINT
        add_text(slide, f"table-row-{n}-cell-1-name", name,
                 x_px=col_xs[0] + 10, y_px=ry + 8, w_px=col_widths[0] - 20, h_px=18,
                 font_size_px=12, color=n_color, bold=True)
        add_text(slide, f"table-row-{n}-cell-1-type", typ,
                 x_px=col_xs[0] + 10, y_px=ry + 28, w_px=col_widths[0] - 20, h_px=14,
                 font_size_px=10, color=t_color)
        # Cell 2: target
        c_color = WHITE if is_total else TEXT_MID
        add_text(slide, f"table-row-{n}-cell-2", tgt,
                 x_px=col_xs[1] + 8, y_px=ry + 14, w_px=col_widths[1] - 16, h_px=20,
                 font_size_px=12, color=c_color, align="right")
        # Cell 3: actual
        add_text(slide, f"table-row-{n}-cell-3", act,
                 x_px=col_xs[2] + 8, y_px=ry + 14, w_px=col_widths[2] - 16, h_px=20,
                 font_size_px=12, color=c_color, align="right")
        # Cell 4: progress bar
        pct_color = WHITE if is_total else TEXT_DARK
        add_text(slide, f"table-row-{n}-cell-4-pct", f"{pct}%",
                 x_px=col_xs[3] + 8, y_px=ry + 14, w_px=36, h_px=18,
                 font_size_px=11, color=pct_color, bold=True, align="right")
        track_x = col_xs[3] + 56
        track_w = col_widths[3] - 64
        add_rect(slide, f"table-row-{n}-cell-4-track", track_x, ry + 18, track_w, 8,
                 RGBColor(0xED, 0xE9, 0xF4) if not is_total else RGBColor(0x55, 0x44, 0x6B))
        fill_color = BRAND_ACCENT if status == "on" else (ORANGE if status == "risk" else RED)
        if is_total:
            fill_color = BRAND_ACCENT_SOFT
        add_rect(slide, f"table-row-{n}-cell-4-bar", track_x, ry + 18,
                 int(track_w * pct / 100), 8, fill_color)
        # Cell 5: status pill
        if status == "on":
            pill_bg = GREEN_BG; pill_txt = GREEN_TXT; dot_c = GREEN; label = "On Track"
        elif status == "risk":
            pill_bg = AMBER_BG; pill_txt = AMBER_TXT; dot_c = AMBER; label = "At Risk"
        else:
            pill_bg = RED_BG; pill_txt = RED_TXT; dot_c = RED; label = "Behind"
        if is_total:
            pill_bg = RGBColor(0x55, 0x44, 0x6B); pill_txt = WHITE; dot_c = RGBColor(0x86, 0xEF, 0xAC)
        pill_x = col_xs[4] + (col_widths[4] - 90) // 2
        add_text(slide, f"table-row-{n}-status-pill", label,
                 x_px=pill_x + 14, y_px=ry + 12, w_px=72, h_px=20,
                 font_size_px=10, color=pill_txt, bold=True, align="center",
                 bg_fill=pill_bg, padding_px=(2, 6, 2, 18))
        add_rect(slide, f"table-row-{n}-rag-dot", pill_x + 18, ry + 19, 7, 7, dot_c)
        # Owner
        add_text(slide, f"table-row-{n}-cell-6", owner,
                 x_px=col_xs[5] + 8, y_px=ry + 14, w_px=col_widths[5] - 16, h_px=20,
                 font_size_px=11, color=c_color, align="center")

    add_footer(slide, page_num=193)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "193_benefits-realization-tracker.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
