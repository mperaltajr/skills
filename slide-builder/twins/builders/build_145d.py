"""
Builder for pattern 145d: Capability vs requirement gap (10-row table) — dark.

Source HTML: _pattern-library/145_capability-vs-requirement-gap-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

LVL_COLORS = {
    "Expert":     (BRAND_ACCENT, WHITE),
    "Proficient": (BRAND_PRIMARY_MID, WHITE),
    "Advanced":   (RGBColor(0x1E, 0x40, 0xAF), WHITE),
    "Basic":      (RGBColor(0xB4, 0x53, 0x09), WHITE),
    "Awareness":  (TEXT_ON_DARK_FAINT, WHITE),
}
GAP_COLORS = {
    "None":        (RGBColor(0x16, 0x4E, 0x2A), RGBColor(0x86, 0xEF, 0xAC)),
    "Minor":       (RGBColor(0x57, 0x40, 0x12), RGBColor(0xFC, 0xD3, 0x4D)),
    "Moderate":    (RGBColor(0x57, 0x40, 0x12), RGBColor(0xFC, 0xD3, 0x4D)),
    "Significant": (RGBColor(0x5C, 0x1F, 0x1F), RGBColor(0xF8, 0x71, 0x71)),
    "Critical":    (RGBColor(0x5C, 0x1F, 0x1F), RGBColor(0xF8, 0x71, 0x71)),
}
PRIO_COLORS = {
    "High":   (RGBColor(0x5C, 0x1F, 0x1F), RGBColor(0xF8, 0x71, 0x71)),
    "Medium": (RGBColor(0x57, 0x40, 0x12), RGBColor(0xFC, 0xD3, 0x4D)),
    "Low":    (RGBColor(0x16, 0x4E, 0x2A), RGBColor(0x86, 0xEF, 0xAC)),
    "—":      (CARD_BG_DARK, TEXT_ON_DARK_FAINT),
}
CRIT_ROW_TINT = RGBColor(0x4A, 0x29, 0x76)
CRIT_BORDER = RGBColor(0xF8, 0x71, 0x71)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome (eyebrow inline above title-row)
    add_text(slide, "title",
             "<strong>AI and UX are critical gaps</strong> — must close before Phase 2 begins in Q3",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Current team capability mapped against client requirements across 10 delivery areas",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Table
    tbl_x = 48
    tbl_y = 220
    tbl_w = 1280 - 96
    tbl_h = 600 - tbl_y
    col_pct = [0.24, 0.16, 0.16, 0.24, 0.20]
    col_w = [int(tbl_w * p) for p in col_pct]
    col_w[-1] = tbl_w - sum(col_w[:-1])
    col_x = [tbl_x]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    headers = ["Capability Area", "Required Level", "Current Level", "Gap", "Priority to Close"]
    centered_cols = {1, 2, 4}
    header_h = 28
    add_rect(slide, "table-head-bg", tbl_x, tbl_y, tbl_w, header_h, BRAND_PRIMARY_MID)
    for i, h in enumerate(headers):
        align = "center" if i in centered_cols else "left"
        add_text(slide, f"table-col-{i+1}-header", h,
                 x_px=col_x[i] + 10, y_px=tbl_y + 6, w_px=col_w[i] - 20, h_px=18,
                 font_size_px=9, color=WHITE, bold=True, align=align, uppercase=True)

    rows = [
        ("Cloud Architecture",       "Expert",     "Proficient",  "Minor",       "Low",    False),
        ("Data Engineering",         "Expert",     "Expert",      "None",        "—",      False),
        ("AI/ML Production",         "Expert",     "Basic",       "Critical",    "High",   True),
        ("Change Management",        "Advanced",   "Expert",      "None",        "—",      False),
        ("Cyber Security",           "Advanced",   "Proficient",  "Moderate",    "Medium", False),
        ("Program Delivery",         "Expert",     "Expert",      "None",        "—",      False),
        ("Business Analysis",        "Advanced",   "Proficient",  "Minor",       "Low",    False),
        ("UX / Design",              "Advanced",   "Basic",       "Significant", "High",   True),
        ("Financial Modeling",       "Proficient", "Proficient",  "None",        "—",      False),
        ("Regulatory / Compliance",  "Advanced",   "Awareness",   "Critical",    "High",   True),
    ]
    avail_h = tbl_h - header_h
    row_h = avail_h // len(rows)
    body_top = tbl_y + header_h
    for ri, (area, req, cur, gap, prio, crit) in enumerate(rows):
        n = ri + 1
        ry = body_top + ri * row_h
        if crit:
            add_rect(slide, f"table-row-{n}-bg", tbl_x, ry, tbl_w, row_h, CRIT_ROW_TINT)
            add_rect(slide, f"table-row-{n}-flag", tbl_x, ry, 4, row_h, CRIT_BORDER)
        add_rect(slide, f"table-row-{n}-divider", tbl_x, ry, tbl_w, 1, CARD_BORDER_DARK)
        add_text(slide, f"table-row-{n}-cell-1", area,
                 x_px=col_x[0] + 14, y_px=ry + 10, w_px=col_w[0] - 28, h_px=20,
                 font_size_px=11, color=WHITE, bold=True, anchor="middle")
        rbg, rfg = LVL_COLORS[req]
        pw = 78
        px = col_x[1] + (col_w[1] - pw) // 2
        add_text(slide, f"table-row-{n}-cell-2", req,
                 x_px=px, y_px=ry + 10, w_px=pw, h_px=18,
                 font_size_px=9, color=rfg, bold=True, align="center", uppercase=True,
                 bg_fill=rbg, padding_px=(2, 6, 2, 6))
        cbg, cfg = LVL_COLORS[cur]
        px = col_x[2] + (col_w[2] - pw) // 2
        add_text(slide, f"table-row-{n}-cell-3", cur,
                 x_px=px, y_px=ry + 10, w_px=pw, h_px=18,
                 font_size_px=9, color=cfg, bold=True, align="center", uppercase=True,
                 bg_fill=cbg, padding_px=(2, 6, 2, 6))
        gbg, gfg = GAP_COLORS[gap]
        add_text(slide, f"table-row-{n}-gap-badge", gap,
                 x_px=col_x[3] + 14, y_px=ry + 10, w_px=96, h_px=18,
                 font_size_px=9, color=gfg, bold=True, align="center", uppercase=True,
                 bg_fill=gbg, padding_px=(2, 6, 2, 6))
        pbg, pfg = PRIO_COLORS[prio]
        px = col_x[4] + (col_w[4] - pw) // 2
        add_text(slide, f"table-row-{n}-cell-5", prio,
                 x_px=px, y_px=ry + 10, w_px=pw, h_px=18,
                 font_size_px=9, color=pfg, bold=True, align="center", uppercase=True,
                 bg_fill=pbg, padding_px=(2, 6, 2, 6))

    # Convergence band
    conv_y = 614
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, 38, BRAND_PRIMARY_MID)
    add_text(slide, "convergence-mark", "DELIVERY RISK",
             x_px=60, y_px=conv_y + 10, w_px=100, h_px=18,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True)
    add_text(slide, "convergence",
             "3 critical gaps — training plan in progress; delivery risk remains until Q3 2025. "
             "AI/ML and Compliance require external hires or accelerated upskilling before Phase 2 kickoff.",
             x_px=174, y_px=conv_y, w_px=1280 - 222, h_px=38,
             font_size_px=12, color=WHITE, anchor="middle")

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "145",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "145d_capability-vs-requirement-gap.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
