"""
Builder for pattern 154d: Implementation tracker — 10-row milestone table — dark.

Source HTML: _pattern-library/154_implementation-tracker-dark.html
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

RAG_GREEN = RGBColor(0x16, 0xA3, 0x4A)
RAG_BLUE = RGBColor(0x60, 0xA5, 0xFA)
RAG_AMBER = RGBColor(0xFC, 0xD3, 0x4D)
RAG_RED = RGBColor(0xF8, 0x71, 0x71)
RAG_GRAY = TEXT_ON_DARK_FAINT

STATUS_COLORS = {
    "Complete":       (RGBColor(0x14, 0x4E, 0x2A), RGBColor(0x86, 0xEF, 0xAC), RAG_GREEN),
    "Complete (late)":(RGBColor(0x57, 0x40, 0x12), RAG_AMBER, RAG_AMBER),
    "On Track":       (RGBColor(0x1E, 0x3A, 0x5C), RAG_BLUE, RAG_BLUE),
    "At Risk":        (RGBColor(0x57, 0x40, 0x12), RAG_AMBER, RAG_AMBER),
    "Delayed":        (RGBColor(0x5C, 0x1F, 0x1F), RAG_RED, RAG_RED),
    "Not started":    (CARD_BG_DARK, RAG_GRAY, RAG_GRAY),
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
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title",
             "<strong>Integration testing is the critical path risk</strong> — Phase 2 go-live slides to Q4 2025 if not resolved by Week 3",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Implementation tracker · 10 milestones across 5 workstreams · target vs. actual/forecast",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Table
    tbl_x = 48
    tbl_y = 220
    tbl_w = 1280 - 96
    tbl_h = 596 - tbl_y
    col_pct = [0.04, 0.27, 0.12, 0.11, 0.13, 0.13, 0.20]
    col_w = [int(tbl_w * p) for p in col_pct]
    col_w[-1] = tbl_w - sum(col_w[:-1])
    col_x = [tbl_x]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    headers = ["#", "Milestone", "Workstream", "Target date", "Actual / Forecast", "Status", "% Complete"]
    centered_cols = {0}
    header_h = 26
    add_rect(slide, "table-head-bg", tbl_x, tbl_y, tbl_w, header_h, BRAND_PRIMARY_MID)
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
        if ri % 2 == 1:
            add_rect(slide, f"table-row-{n}-bg", tbl_x, ry, tbl_w, row_h, RGBColor(0x35, 0x1A, 0x52))
        if crit:
            add_rect(slide, f"table-row-{n}-flag", tbl_x, ry, 3, row_h, CRIT_BORDER)
        add_rect(slide, f"table-row-{n}-divider", tbl_x, ry, tbl_w, 1, CARD_BORDER_DARK)
        add_text(slide, f"table-row-{n}-num", num,
                 x_px=col_x[0], y_px=ry + 8, w_px=col_w[0], h_px=20,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, align="center")
        add_text(slide, f"table-row-{n}-cell-2", name,
                 x_px=col_x[1] + 8, y_px=ry + 8, w_px=col_w[1] - 16, h_px=20,
                 font_size_px=11, color=WHITE, bold=True)
        dot_color = WS_DOT_COLORS.get(ws, BRAND_ACCENT)
        add_rect(slide, f"table-row-{n}-ws-dot", col_x[2] + 8, ry + 14, 8, 8, dot_color)
        add_text(slide, f"table-row-{n}-cell-3", ws,
                 x_px=col_x[2] + 22, y_px=ry + 8, w_px=col_w[2] - 30, h_px=20,
                 font_size_px=10, color=TEXT_ON_DARK_MID)
        add_text(slide, f"table-row-{n}-cell-4", target,
                 x_px=col_x[3] + 4, y_px=ry + 8, w_px=col_w[3] - 8, h_px=20,
                 font_size_px=10, color=WHITE)
        actual_color = WHITE
        if "TBD" in actual:
            actual_color = TEXT_ON_DARK_FAINT
        elif actual != target:
            actual_color = RAG_AMBER
        add_text(slide, f"table-row-{n}-cell-5", actual,
                 x_px=col_x[4] + 4, y_px=ry + 8, w_px=col_w[4] - 8, h_px=20,
                 font_size_px=10, color=actual_color, bold=(actual != target and "TBD" not in actual),
                 italic=("TBD" in actual))
        sbg, sfg, sdot = STATUS_COLORS[status]
        pill_w = col_w[5] - 12
        add_text(slide, f"table-row-{n}-pill", status,
                 x_px=col_x[5] + 6, y_px=ry + 8, w_px=pill_w, h_px=18,
                 font_size_px=8, color=sfg, bold=True, align="center", uppercase=True,
                 bg_fill=sbg, padding_px=(2, 4, 2, 12))
        add_rect(slide, f"table-row-{n}-rag-dot", col_x[5] + 10, ry + 13, 6, 6, sdot)
        pct_x = col_x[6] + 6
        pct_w = col_w[6] - 60
        add_text(slide, f"table-row-{n}-pct-label", f"{pct}%",
                 x_px=col_x[6] + col_w[6] - 50, y_px=ry + 8, w_px=44, h_px=18,
                 font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, align="right")
        add_rect(slide, f"table-row-{n}-bar-bg", pct_x, ry + 14, pct_w, 6,
                 CARD_BG_DARK)
        if pct > 0:
            fill_color = sdot
            add_rect(slide, f"table-row-{n}-bar-fill", pct_x, ry + 14,
                     int(pct_w * pct / 100), 6, fill_color)

    # Convergence
    conv_y = 610
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, 40, BRAND_ACCENT)
    add_text(slide, "convergence-mark", "CRITICAL PATH",
             x_px=60, y_px=conv_y + 12, w_px=110, h_px=16,
             font_size_px=9, color=WHITE, bold=True, uppercase=True)
    add_text(slide, "convergence",
             "Integration testing is the critical path risk — Phase 2 go-live slides to Q4 2025 if not resolved by Week 3.",
             x_px=184, y_px=conv_y, w_px=1280 - 232, h_px=40,
             font_size_px=12, color=WHITE, anchor="middle")

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "154",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "154d_implementation-tracker.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
