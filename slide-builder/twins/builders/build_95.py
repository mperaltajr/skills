"""
Builder for pattern 95: Action register (8-row table with status pills).

Source HTML: _pattern-library/95_action-register.html
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
PILL_OPEN_BG = RGBColor(0xFD, 0xEC, 0xEC)
PILL_PROG_BG = RGBColor(0xFE, 0xF3, 0xC7)
PILL_DONE_BG = RGBColor(0xDC, 0xFC, 0xE7)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Eyebrow + title
    add_text(slide, "eyebrow", "Action register",
             x_px=48, y_px=58, w_px=400, h_px=16,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "title",
             "Action register — eight items from kickoff, three by Friday.",
             x_px=48, y_px=78, w_px=900, h_px=36,
             font_size_px=26, color=TEXT_DARK, bold=True)
    add_text(slide, "subtitle",
             "Ordered by due date. Owners named, status colour-coded. Anything still OPEN on Thursday end-of-day escalates to the weekly review.",
             x_px=48, y_px=118, w_px=900, h_px=40,
             font_size_px=12, color=TEXT_MID)
    add_rect(slide, "brand-rule", 48, 170, 56, 3, BRAND_ACCENT)

    # Status legend (top-right, below title row)
    leg_x = 880
    leg_y = 170
    leg_w = 352
    leg_h = 36
    leg = add_rect(slide, "legend", leg_x, leg_y, leg_w, leg_h, RGBColor(0xFB, 0xFA, 0xFD))
    leg.line.color.rgb = CARD_BORDER
    leg.line.width = 9525
    add_text(slide, "legend-title", "STATUS KEY",
             x_px=leg_x + 12, y_px=leg_y + 12, w_px=80, h_px=14,
             font_size_px=9, color=TEXT_MID, bold=True, uppercase=True)
    legend_items = [("Open", RAG_RED), ("In progress", RAG_AMBER), ("Done", RAG_GREEN)]
    li_x = leg_x + 100
    for i, (label, color) in enumerate(legend_items):
        n = i + 1
        add_rect(slide, f"legend-{n}-swatch", li_x, leg_y + 14, 9, 9, color)
        add_text(slide, f"legend-{n}-label", label,
                 x_px=li_x + 14, y_px=leg_y + 12, w_px=86, h_px=14,
                 font_size_px=10, color=TEXT_DARK, bold=True, uppercase=True)
        li_x += 90

    # Table — top:224
    tbl_left = 48
    tbl_top = 224
    tbl_w = 1280 - 96
    # Cols: num 6%, action 50%, owner 16%, due 12%, status 16%
    col_pct = [0.06, 0.50, 0.16, 0.12, 0.16]
    col_w = [int(tbl_w * p) for p in col_pct]
    col_w[-1] = tbl_w - sum(col_w[:-1])
    col_x = [tbl_left]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    header_h = 28
    headers = ["#", "Action", "Owner", "Due", "Status"]
    add_rect(slide, "table-head-bg", tbl_left, tbl_top, tbl_w, header_h, BRAND_PRIMARY)
    for i, h in enumerate(headers):
        align = "center" if i == 0 else "left"
        add_text(slide, f"table-col-{i+1}-header", h,
                 x_px=col_x[i] + 8, y_px=tbl_top + 7, w_px=col_w[i] - 16, h_px=16,
                 font_size_px=9, color=WHITE, bold=True, align=align, uppercase=True)

    rows = [
        ("02", "Send pre-read deck on Slide Lab method", "Mario", "Mon", "Done", "done"),
        ("03", "Schedule kickoff workshop", "PMO", "Mon", "Done", "done"),
        ("07", "Print QC checklist for pilot users", "Coach", "Mon", "Done", "done"),
        ("01", "Provision Claude Code access for 4 pilot users", "IT lead", "Tue", "Open", "open"),
        ("05", "Set up weekly review slot", "Mario", "Wed", "Open", "open"),
        ("04", "Identify 12 sample decks for baseline", "Maria", "Fri", "In progress", "prog"),
        ("06", "Brief skeptical seniors 1:1", "MD", "Next week", "Open", "open"),
        ("08", "Finalize Wave 2 scope memo", "Maria", "2 weeks", "Open", "open"),
    ]
    row_h = 38
    body_top = tbl_top + header_h
    for ri, (num, action, owner, due, status, kind) in enumerate(rows):
        n = ri + 1
        ry = body_top + ri * row_h
        # Alternating row bg
        if ri % 2 == 1:
            add_rect(slide, f"table-row-{n}-bg", tbl_left, ry, tbl_w, row_h,
                     RGBColor(0xFB, 0xFA, 0xFD))
        # Top border
        add_rect(slide, f"table-row-{n}-divider", tbl_left, ry, tbl_w, 1, CARD_BORDER)

        # Num cell (card-bg fill, accent text)
        add_rect(slide, f"table-row-{n}-num-bg",
                 col_x[0], ry, col_w[0], row_h, CARD_BG)
        add_text(slide, f"table-row-{n}-num", num,
                 x_px=col_x[0], y_px=ry + 11, w_px=col_w[0], h_px=18,
                 font_size_px=11, color=BRAND_ACCENT, bold=True, align="center")
        # Action
        add_text(slide, f"table-row-{n}-cell-2", action,
                 x_px=col_x[1] + 12, y_px=ry + 11, w_px=col_w[1] - 24, h_px=20,
                 font_size_px=12, color=TEXT_DARK, bold=True)
        # Owner
        add_text(slide, f"table-row-{n}-cell-3", owner,
                 x_px=col_x[2] + 12, y_px=ry + 11, w_px=col_w[2] - 24, h_px=20,
                 font_size_px=11, color=BRAND_PRIMARY)
        # Due
        due_color = RAG_RED if due in ("Tue", "Wed", "Fri") else TEXT_DARK
        add_text(slide, f"table-row-{n}-cell-4", due,
                 x_px=col_x[3] + 12, y_px=ry + 11, w_px=col_w[3] - 24, h_px=20,
                 font_size_px=11, color=due_color, bold=True)
        # Status pill
        if kind == "open":
            pbg, ptxt, pdot = PILL_OPEN_BG, RAG_RED, RAG_RED
        elif kind == "prog":
            pbg, ptxt, pdot = PILL_PROG_BG, RGBColor(0xB8, 0x77, 0x0A), RAG_AMBER
        else:
            pbg, ptxt, pdot = PILL_DONE_BG, RGBColor(0x1E, 0x84, 0x49), RAG_GREEN
        pill_x = col_x[4] + 8
        add_text(slide, f"table-row-{n}-status-pill", status,
                 x_px=pill_x, y_px=ry + 10, w_px=col_w[4] - 16, h_px=18,
                 font_size_px=9, color=ptxt, bold=True, align="center", uppercase=True,
                 bg_fill=pbg, padding_px=(2, 16, 2, 14))
        add_rect(slide, f"table-row-{n}-status-dot",
                 pill_x + 8, ry + 15, 7, 7, pdot)

    # Table outer border
    total_h = header_h + row_h * len(rows)
    add_rect(slide, "table-border-bottom", tbl_left, tbl_top + total_h, tbl_w, 1, CARD_BORDER)
    add_rect(slide, "table-border-left", tbl_left, tbl_top, 1, total_h, CARD_BORDER)
    add_rect(slide, "table-border-right", tbl_left + tbl_w - 1, tbl_top, 1, total_h, CARD_BORDER)

    # Convergence
    conv_y = 720 - 56 - 56
    conv_h = 52
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, conv_h, BRAND_PRIMARY)
    add_text(slide, "convergence-mark", "SO WHAT",
             x_px=48 + 14, y_px=conv_y + 16, w_px=80, h_px=20,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center",
             bg_fill=BRAND_PRIMARY_MID, padding_px=(3, 6, 3, 6))
    add_text(
        slide, "convergence",
        "Three actions due by Friday. Four for next week. The Friday batch unblocks baseline measurement — if IT access slips past Tuesday, sample decks slip too.",
        x_px=48 + 110, y_px=conv_y, w_px=1280 - 96 - 130, h_px=conv_h,
        font_size_px=13, color=WHITE, anchor="middle",
    )

    add_footer(slide, page_num=95)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "95_action-register.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
