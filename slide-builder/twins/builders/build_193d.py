"""
Builder for pattern 193d: Benefits Realization Tracker — DARK variant.

Light source: twins/builders/build_193.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

GREEN = RGBColor(0x4A, 0xDE, 0x80)
GREEN_BG = RGBColor(0x06, 0x5F, 0x46)
GREEN_TXT = RGBColor(0xD7, 0xF1, 0xDA)
AMBER = RGBColor(0xFB, 0xBF, 0x24)
AMBER_BG = RGBColor(0x85, 0x4D, 0x0E)
AMBER_TXT = RGBColor(0xFE, 0xF9, 0xC3)
RED = RGBColor(0xFB, 0x72, 0x85)
RED_BG = RGBColor(0x99, 0x1B, 0x1B)
RED_TXT = RGBColor(0xFE, 0xE2, 0xE2)
ORANGE = RGBColor(0xF5, 0x9E, 0x0B)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Benefits Realization <strong>Tracker</strong>",
        x_px=64, y_px=20, w_px=900, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "YTD performance against committed benefit targets across all workstreams",
        x_px=64, y_px=108, w_px=820, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    # Summary stat — move below brand-rule into legend area
    add_text(slide, "summary-stat-value", "$42M",
             x_px=1280 - 64 - 220, y_px=232, w_px=220, h_px=28,
             font_size_px=20, color=BRAND_ACCENT_SOFT, bold=True, align="right")
    add_text(slide, "summary-stat-label", "benefits realized YTD",
             x_px=1280 - 64 - 220, y_px=232 + 28, w_px=220, h_px=18,
             font_size_px=11, color=TEXT_ON_DARK_MID, align="right")

    tbl_top = 282
    tbl_bot = 660
    tbl_left = 64
    tbl_w = 1280 - 128
    col_pcts = [26, 12, 13, 18, 16, 15]
    col_xs = [tbl_left]
    for p in col_pcts[:-1]:
        col_xs.append(col_xs[-1] + int(tbl_w * p / 100))
    col_widths = [int(tbl_w * p / 100) for p in col_pcts]

    hdr_h = 32
    add_rect(slide, "table-header-bg", tbl_left, tbl_top, tbl_w, hdr_h, BRAND_ACCENT)
    headers = ["Benefit", "Target", "Actual (YTD)", "% Achieved", "Status", "Owner"]
    aligns = ["left", "right", "right", "right", "center", "center"]
    for i, (h, a) in enumerate(zip(headers, aligns)):
        add_text(slide, f"table-col-{i+1}-header", h,
                 x_px=col_xs[i] + 10, y_px=tbl_top + 8, w_px=col_widths[i] - 20, h_px=18,
                 font_size_px=10, color=WHITE, bold=True, uppercase=True, align=a)

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
        bg_c = BRAND_ACCENT if is_total else (CARD_BG_DARK if i % 2 == 0 else BRAND_PRIMARY)
        add_rect(slide, f"table-row-{n}-bg", tbl_left, ry, tbl_w, row_h, bg_c)
        n_color = WHITE
        t_color = (RGBColor(0xEE, 0xDD, 0xFF) if is_total else TEXT_ON_DARK_FAINT)
        add_text(slide, f"table-row-{n}-cell-1-name", name,
                 x_px=col_xs[0] + 10, y_px=ry + 8, w_px=col_widths[0] - 20, h_px=18,
                 font_size_px=12, color=n_color, bold=True)
        add_text(slide, f"table-row-{n}-cell-1-type", typ,
                 x_px=col_xs[0] + 10, y_px=ry + 28, w_px=col_widths[0] - 20, h_px=14,
                 font_size_px=10, color=t_color)
        c_color = WHITE if is_total else TEXT_ON_DARK_MID
        add_text(slide, f"table-row-{n}-cell-2", tgt,
                 x_px=col_xs[1] + 8, y_px=ry + 14, w_px=col_widths[1] - 16, h_px=20,
                 font_size_px=12, color=c_color, align="right")
        add_text(slide, f"table-row-{n}-cell-3", act,
                 x_px=col_xs[2] + 8, y_px=ry + 14, w_px=col_widths[2] - 16, h_px=20,
                 font_size_px=12, color=c_color, align="right")
        pct_color = WHITE
        add_text(slide, f"table-row-{n}-cell-4-pct", f"{pct}%",
                 x_px=col_xs[3] + 8, y_px=ry + 14, w_px=36, h_px=18,
                 font_size_px=11, color=pct_color, bold=True, align="right")
        track_x = col_xs[3] + 56
        track_w = col_widths[3] - 64
        add_rect(slide, f"table-row-{n}-cell-4-track", track_x, ry + 18, track_w, 8,
                 CARD_BORDER_DARK)
        fill_color = BRAND_ACCENT_SOFT if status == "on" else (ORANGE if status == "risk" else RED)
        if is_total:
            fill_color = WHITE
        add_rect(slide, f"table-row-{n}-cell-4-bar", track_x, ry + 18,
                 int(track_w * pct / 100), 8, fill_color)
        if status == "on":
            pill_bg = GREEN_BG; pill_txt = GREEN_TXT; dot_c = GREEN; label = "On Track"
        elif status == "risk":
            pill_bg = AMBER_BG; pill_txt = AMBER_TXT; dot_c = AMBER; label = "At Risk"
        else:
            pill_bg = RED_BG; pill_txt = RED_TXT; dot_c = RED; label = "Behind"
        if is_total:
            pill_bg = BRAND_PRIMARY; pill_txt = WHITE; dot_c = GREEN
        pill_x = col_xs[4] + (col_widths[4] - 90) // 2
        add_text(slide, f"table-row-{n}-status-pill", label,
                 x_px=pill_x + 14, y_px=ry + 12, w_px=72, h_px=20,
                 font_size_px=10, color=pill_txt, bold=True, align="center",
                 bg_fill=pill_bg, padding_px=(2, 6, 2, 18))
        add_rect(slide, f"table-row-{n}-rag-dot", pill_x + 18, ry + 19, 7, 7, dot_c)
        add_text(slide, f"table-row-{n}-cell-6", owner,
                 x_px=col_xs[5] + 8, y_px=ry + 14, w_px=col_widths[5] - 16, h_px=20,
                 font_size_px=11, color=c_color, align="center")

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "193",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "193d_benefits-realization-tracker-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
