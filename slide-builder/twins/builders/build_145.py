"""
Builder for pattern 145: Capability vs requirement gap (10-row table with pills).

Source HTML: _pattern-library/145_capability-vs-requirement-gap.html
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


LVL_COLORS = {
    "Expert":     (RGBColor(0x2D, 0x0A, 0x4E), WHITE),
    "Proficient": (RGBColor(0x5C, 0x2D, 0x87), WHITE),
    "Advanced":   (RGBColor(0x1E, 0x40, 0xAF), WHITE),
    "Basic":      (RGBColor(0xB4, 0x53, 0x09), WHITE),
    "Awareness":  (RGBColor(0x64, 0x74, 0x8B), WHITE),
}
GAP_COLORS = {
    "None":        (RGBColor(0xDC, 0xFC, 0xE7), RGBColor(0x15, 0x80, 0x3D)),
    "Minor":       (RGBColor(0xFE, 0xF9, 0xC3), RGBColor(0x85, 0x4D, 0x0E)),
    "Moderate":    (RGBColor(0xFE, 0xF3, 0xC7), RGBColor(0x92, 0x40, 0x0E)),
    "Significant": (RGBColor(0xFE, 0xE2, 0xE2), RGBColor(0xB9, 0x1C, 0x1C)),
    "Critical":    (RGBColor(0xFE, 0xE2, 0xE2), RGBColor(0x99, 0x1B, 0x1B)),
}
PRIO_COLORS = {
    "High":   (RGBColor(0xFE, 0xE2, 0xE2), RGBColor(0x99, 0x1B, 0x1B)),
    "Medium": (RGBColor(0xFE, 0xF3, 0xC7), RGBColor(0x92, 0x40, 0x0E)),
    "Low":    (RGBColor(0xF0, 0xFD, 0xF4), RGBColor(0x16, 0x65, 0x34)),
    "—":      (RGBColor(0xF1, 0xF5, 0xF9), RGBColor(0x94, 0xA3, 0xB8)),
}
CRIT_ROW_TINT = RGBColor(0xFD, 0xF2, 0xF2)
CRIT_BORDER = RGBColor(0xDC, 0x26, 0x26)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Eyebrow + title block
    add_text(slide, "eyebrow", "Capability assessment · Phase 2 readiness",
             x_px=48, y_px=56, w_px=600, h_px=14,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "title",
             "<strong>AI and UX are critical gaps</strong> — must close before Phase 2 begins in Q3",
             x_px=48, y_px=74, w_px=900, h_px=40,
             font_size_px=22, color=TEXT_DARK, bold=True,
             emphasis_color=BRAND_PRIMARY)
    add_text(slide, "subtitle",
             "Current team capability mapped against client requirements across 10 delivery areas. Three critical gaps identified; training plan in progress.",
             x_px=48, y_px=116, w_px=860, h_px=22,
             font_size_px=12, color=TEXT_MID)
    add_rect(slide, "brand-rule", 48, 144, 56, 3, BRAND_ACCENT)

    # Table: top:158 left:48 right:48 bottom:100
    tbl_x = 48
    tbl_y = 158
    tbl_w = 1280 - 96
    tbl_h = 720 - 100 - 158
    col_pct = [0.24, 0.16, 0.16, 0.24, 0.20]
    col_w = [int(tbl_w * p) for p in col_pct]
    col_w[-1] = tbl_w - sum(col_w[:-1])
    col_x = [tbl_x]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    headers = ["Capability Area", "Required Level", "Current Level", "Gap", "Priority to Close"]
    centered_cols = {1, 2, 4}
    header_h = 28
    add_rect(slide, "table-head-bg", tbl_x, tbl_y, tbl_w, header_h, BRAND_PRIMARY)
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
        # Row background
        if crit:
            add_rect(slide, f"table-row-{n}-bg", tbl_x, ry, tbl_w, row_h, CRIT_ROW_TINT)
            add_rect(slide, f"table-row-{n}-flag", tbl_x, ry, 4, row_h, CRIT_BORDER)
        # Top divider
        add_rect(slide, f"table-row-{n}-divider", tbl_x, ry, tbl_w, 1, CARD_BORDER)
        # Area name
        add_text(slide, f"table-row-{n}-cell-1", area,
                 x_px=col_x[0] + 14, y_px=ry + 10, w_px=col_w[0] - 28, h_px=20,
                 font_size_px=11, color=TEXT_DARK, bold=True, anchor="middle")
        # Required pill
        rbg, rfg = LVL_COLORS[req]
        pw = 78
        px = col_x[1] + (col_w[1] - pw) // 2
        add_text(slide, f"table-row-{n}-cell-2", req,
                 x_px=px, y_px=ry + 10, w_px=pw, h_px=18,
                 font_size_px=9, color=rfg, bold=True, align="center", uppercase=True,
                 bg_fill=rbg, padding_px=(2, 6, 2, 6))
        # Current pill
        cbg, cfg = LVL_COLORS[cur]
        px = col_x[2] + (col_w[2] - pw) // 2
        add_text(slide, f"table-row-{n}-cell-3", cur,
                 x_px=px, y_px=ry + 10, w_px=pw, h_px=18,
                 font_size_px=9, color=cfg, bold=True, align="center", uppercase=True,
                 bg_fill=cbg, padding_px=(2, 6, 2, 6))
        # Gap badge
        gbg, gfg = GAP_COLORS[gap]
        add_text(slide, f"table-row-{n}-gap-badge", gap,
                 x_px=col_x[3] + 14, y_px=ry + 10, w_px=96, h_px=18,
                 font_size_px=9, color=gfg, bold=True, align="center", uppercase=True,
                 bg_fill=gbg, padding_px=(2, 6, 2, 6))
        # Priority pill
        pbg, pfg = PRIO_COLORS[prio]
        px = col_x[4] + (col_w[4] - pw) // 2
        add_text(slide, f"table-row-{n}-cell-5", prio,
                 x_px=px, y_px=ry + 10, w_px=pw, h_px=18,
                 font_size_px=9, color=pfg, bold=True, align="center", uppercase=True,
                 bg_fill=pbg, padding_px=(2, 6, 2, 6))

    # Convergence band
    conv_y = 720 - 76
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, 38, BRAND_PRIMARY)
    add_text(slide, "convergence-mark", "DELIVERY RISK",
             x_px=60, y_px=conv_y + 10, w_px=100, h_px=18,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True)
    add_text(slide, "convergence",
             "3 critical gaps — training plan in progress; delivery risk remains until Q3 2025. "
             "AI/ML and Compliance require external hires or accelerated upskilling before Phase 2 kickoff.",
             x_px=174, y_px=conv_y, w_px=1280 - 222, h_px=38,
             font_size_px=12, color=WHITE, anchor="middle")

    add_footer(slide, page_num=145)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "145_capability-vs-requirement-gap.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
