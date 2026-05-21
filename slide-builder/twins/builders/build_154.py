"""
Builder for pattern 154: Implementation tracker — 10-row milestone table with progress bars.

Source HTML: _pattern-library/154_implementation-tracker.html
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

RAG_GREEN = RGBColor(0x16, 0xA3, 0x4A)
RAG_BLUE = RGBColor(0x1D, 0x6F, 0xBE)
RAG_AMBER = RGBColor(0xF3, 0x9C, 0x12)
RAG_RED = RGBColor(0xDC, 0x26, 0x26)
RAG_GRAY = TEXT_MID

STATUS_COLORS = {
    "Complete":       (RGBColor(0xDC, 0xFC, 0xE7), RGBColor(0x15, 0x80, 0x3D), RAG_GREEN),
    "Complete (late)":(RGBColor(0xFE, 0xF3, 0xC7), RGBColor(0xB8, 0x77, 0x0A), RAG_AMBER),
    "On Track":       (RGBColor(0xDB, 0xEA, 0xFE), RAG_BLUE, RAG_BLUE),
    "At Risk":        (RGBColor(0xFE, 0xF3, 0xC7), RGBColor(0xB8, 0x77, 0x0A), RAG_AMBER),
    "Delayed":        (RGBColor(0xFE, 0xE2, 0xE2), RGBColor(0xB9, 0x1C, 0x1C), RAG_RED),
    "Not started":    (RGBColor(0xF1, 0xF5, 0xF9), RAG_GRAY, RAG_GRAY),
}

WS_DOT_COLORS = {
    "All": BRAND_ACCENT,
    "Technology": RAG_BLUE,
    "Operations": RAG_GREEN,
    "Data": RAG_AMBER,
    "People": RGBColor(0xE0, 0x44, 0x7C),
    "Program": RAG_GRAY,
}


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Eyebrow + title
    add_text(slide, "eyebrow", "Implementation tracker — milestones × status",
             x_px=48, y_px=56, w_px=560, h_px=14,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "title",
             "<strong>Integration testing is the critical path risk</strong> — Phase 2 go-live slides to Q4 2025 if not resolved by Week 3",
             x_px=48, y_px=74, w_px=1100, h_px=42,
             font_size_px=22, color=TEXT_DARK, bold=True,
             emphasis_color=BRAND_PRIMARY)
    add_text(slide, "subtitle",
             "10 program milestones tracked across five workstreams. Target vs. actual/forecast dates; status and percent complete as of today.",
             x_px=48, y_px=116, w_px=960, h_px=24,
             font_size_px=12, color=TEXT_MID)
    add_rect(slide, "brand-rule", 48, 144, 56, 3, BRAND_ACCENT)

    # Table: top:158 left:48 right:48 bottom:90
    tbl_x = 48
    tbl_y = 158
    tbl_w = 1280 - 96
    tbl_h = 720 - 90 - tbl_y
    col_pct = [0.04, 0.27, 0.12, 0.11, 0.13, 0.13, 0.20]
    col_w = [int(tbl_w * p) for p in col_pct]
    col_w[-1] = tbl_w - sum(col_w[:-1])
    col_x = [tbl_x]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    headers = ["#", "Milestone", "Workstream", "Target date", "Actual / Forecast", "Status", "% Complete"]
    centered_cols = {0}
    header_h = 26
    add_rect(slide, "table-head-bg", tbl_x, tbl_y, tbl_w, header_h, BRAND_PRIMARY)
    for i, h in enumerate(headers):
        align = "center" if i in centered_cols else "left"
        add_text(slide, f"table-col-{i+1}-header", h,
                 x_px=col_x[i] + 8, y_px=tbl_y + 6, w_px=col_w[i] - 16, h_px=18,
                 font_size_px=8, color=WHITE, bold=True, align=align, uppercase=True)

    rows = [
        ("01", "Project kickoff",            "All",        "15 Jan 2025", "15 Jan 2025", "Complete",        100, False),
        ("02", "Architecture design approved","Technology","28 Feb 2025", "7 Mar 2025",  "Complete (late)", 100, True),
        ("03", "Phase 1 pilot launch",       "Operations", "1 Apr 2025",  "1 Apr 2025",  "Complete",        100, False),
        ("04", "Data migration Wave 1",      "Data",       "15 May 2025", "20 May 2025", "Complete (late)", 100, True),
        ("05", "Training program begins",    "People",     "1 Jun 2025",  "1 Jun 2025",  "On Track",         65, False),
        ("06", "Integration testing complete","Technology","15 Jul 2025", "1 Aug 2025",  "At Risk",          30, True),
        ("07", "Phase 2 UAT",                "All",        "1 Sep 2025",  "TBD",         "Delayed",           0, True),
        ("08", "Phase 2 go-live",            "All",        "1 Oct 2025",  "TBD",         "Delayed",           0, True),
        ("09", "Phase 3 planning",           "Program",    "1 Nov 2025",  "TBD",         "Not started",       0, False),
        ("10", "Program closure",            "All",        "31 Mar 2026", "TBD",         "Not started",       0, False),
    ]
    avail_h = tbl_h - header_h
    row_h = avail_h // len(rows)
    body_top = tbl_y + header_h
    CRIT_BORDER = RAG_RED

    for ri, (num, name, ws, target, actual, status, pct, crit) in enumerate(rows):
        n = ri + 1
        ry = body_top + ri * row_h
        # Alternate row tint
        if ri % 2 == 1:
            add_rect(slide, f"table-row-{n}-bg", tbl_x, ry, tbl_w, row_h, RGBColor(0xFB, 0xFA, 0xFD))
        # Critical row left bar
        if crit:
            add_rect(slide, f"table-row-{n}-flag", tbl_x, ry, 3, row_h, CRIT_BORDER)
        # Top divider
        add_rect(slide, f"table-row-{n}-divider", tbl_x, ry, tbl_w, 1, CARD_BORDER)

        # Num
        add_text(slide, f"table-row-{n}-num", num,
                 x_px=col_x[0], y_px=ry + 8, w_px=col_w[0], h_px=20,
                 font_size_px=10, color=BRAND_ACCENT, bold=True, align="center")
        # Milestone name
        add_text(slide, f"table-row-{n}-cell-2", name,
                 x_px=col_x[1] + 8, y_px=ry + 8, w_px=col_w[1] - 16, h_px=20,
                 font_size_px=11, color=TEXT_DARK, bold=True)
        # Workstream with dot
        dot_color = WS_DOT_COLORS.get(ws, BRAND_ACCENT)
        add_rect(slide, f"table-row-{n}-ws-dot", col_x[2] + 8, ry + 14, 8, 8, dot_color)
        add_text(slide, f"table-row-{n}-cell-3", ws,
                 x_px=col_x[2] + 22, y_px=ry + 8, w_px=col_w[2] - 30, h_px=20,
                 font_size_px=10, color=TEXT_MID)
        # Target date
        add_text(slide, f"table-row-{n}-cell-4", target,
                 x_px=col_x[3] + 4, y_px=ry + 8, w_px=col_w[3] - 8, h_px=20,
                 font_size_px=10, color=TEXT_DARK)
        # Actual date (late highlighted amber if target != actual & not TBD)
        actual_color = TEXT_DARK
        if "TBD" in actual:
            actual_color = TEXT_FAINT
        elif actual != target:
            actual_color = RGBColor(0xB8, 0x77, 0x0A)
        add_text(slide, f"table-row-{n}-cell-5", actual,
                 x_px=col_x[4] + 4, y_px=ry + 8, w_px=col_w[4] - 8, h_px=20,
                 font_size_px=10, color=actual_color, bold=(actual != target and "TBD" not in actual),
                 italic=("TBD" in actual))
        # Status pill
        sbg, sfg, sdot = STATUS_COLORS[status]
        pill_w = col_w[5] - 12
        add_text(slide, f"table-row-{n}-pill", status,
                 x_px=col_x[5] + 6, y_px=ry + 8, w_px=pill_w, h_px=18,
                 font_size_px=8, color=sfg, bold=True, align="center", uppercase=True,
                 bg_fill=sbg, padding_px=(2, 4, 2, 12))
        add_rect(slide, f"table-row-{n}-rag-dot", col_x[5] + 10, ry + 13, 6, 6, sdot)
        # % bar
        pct_x = col_x[6] + 6
        pct_w = col_w[6] - 60
        add_text(slide, f"table-row-{n}-pct-label", f"{pct}%",
                 x_px=col_x[6] + col_w[6] - 50, y_px=ry + 8, w_px=44, h_px=18,
                 font_size_px=10, color=TEXT_MID, bold=True, align="right")
        add_rect(slide, f"table-row-{n}-bar-bg", pct_x, ry + 14, pct_w, 6,
                 RGBColor(0xED, 0xE8, 0xF4))
        if pct > 0:
            fill_color = sdot
            add_rect(slide, f"table-row-{n}-bar-fill", pct_x, ry + 14,
                     int(pct_w * pct / 100), 6, fill_color)

    # Convergence
    conv_y = 720 - 76
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, 40, BRAND_PRIMARY)
    add_text(slide, "convergence-mark", "CRITICAL PATH",
             x_px=60, y_px=conv_y + 12, w_px=110, h_px=16,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "convergence",
             "Integration testing is the critical path risk — Phase 2 go-live slides to Q4 2025 if not resolved by Week 3.",
             x_px=184, y_px=conv_y, w_px=1280 - 232, h_px=40,
             font_size_px=12, color=WHITE, anchor="middle")

    add_footer(slide, page_num=154)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "154_implementation-tracker.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
