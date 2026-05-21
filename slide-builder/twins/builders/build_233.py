"""
Builder for pattern 233: Closing next steps / action register table with grouped rows.

Source HTML: _pattern-library/233_closing-next-steps.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)
from pptx.dml.color import RGBColor

OVERDUE = RGBColor(0xDC, 0x26, 0x26)
UPCOMING = RGBColor(0xD9, 0x77, 0x06)
FUTURE = RGBColor(0x16, 0xA3, 0x4A)
PILL_NOT = RGBColor(0xF1, 0xF5, 0xF9)
PILL_NOT_TXT = RGBColor(0x64, 0x74, 0x8B)
PILL_IP = RGBColor(0xEF, 0xF6, 0xFF)
PILL_IP_TXT = RGBColor(0x1D, 0x4E, 0xD8)
PILL_DONE = RGBColor(0xF0, 0xFD, 0xF4)
PILL_DONE_TXT = RGBColor(0x15, 0x80, 0x3D)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Agreed <strong>Next Steps</strong> &amp; Action Register",
        subtitle="Owners, due dates, and current status — agreed as of 19 May 2026",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Table: top:138, left:48, w=1184, bottom 80
    tbl_left = 48
    tbl_top = 138
    tbl_w = 1184
    col_w = [36, 580, 180, 110, 130]
    col_w[1] = tbl_w - sum(col_w) + col_w[1] - 148  # absorb extra
    col_x = [tbl_left]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    # Header row
    header_h = 26
    add_rect(slide, "table-head-bg", tbl_left, tbl_top, tbl_w, header_h, BRAND_PRIMARY)
    headers = ["#", "Action", "Owner", "Due", "Status"]
    align_centers = [0]
    for i, h in enumerate(headers):
        align = "center" if i in align_centers else "left"
        add_text(slide, f"table-col-{i+1}-header", h,
                 x_px=col_x[i] + 8, y_px=tbl_top + 6, w_px=col_w[i] - 16, h_px=16,
                 font_size_px=9, color=WHITE, bold=True, align=align, uppercase=True)

    # Rows grouped
    rows = [
        ("__GROUP__", "Accenture Actions", "accenture"),
        ("1", "Finalise data architecture blueprint and share with client integration lead",
         "S. Okafor", ("12 May 26", OVERDUE), ("In Progress", PILL_IP, PILL_IP_TXT)),
        ("2", "Conduct UAT kick-off session and distribute test scripts to business users",
         "R. Lindqvist", ("23 May 26", UPCOMING), ("Not Started", PILL_NOT, PILL_NOT_TXT)),
        ("3", "Submit revised commercial proposal reflecting agreed scope reductions",
         "M. Peralta", ("06 Jun 26", FUTURE), ("Done", PILL_DONE, PILL_DONE_TXT)),
        ("__GROUP__", "Client Actions", "client"),
        ("4", "Provide sign-off on target operating model v3 document",
         "J. Tran", ("09 May 26", OVERDUE), ("In Progress", PILL_IP, PILL_IP_TXT)),
        ("5", "Confirm access credentials for legacy ERP environment ahead of migration sprint",
         "A. Mensah", ("21 May 26", UPCOMING), ("Not Started", PILL_NOT, PILL_NOT_TXT)),
        ("6", "Circulate and obtain legal sign-off on data-sharing agreement annex",
         "P. Kowalski", ("30 May 26", FUTURE), ("Done", PILL_DONE, PILL_DONE_TXT)),
        ("7", "Nominate two business SMEs to join the change network and attend onboarding",
         "B. Nakamura", ("13 Jun 26", FUTURE), ("Done", PILL_DONE, PILL_DONE_TXT)),
    ]
    group_h = 22
    row_h = 42
    y = tbl_top + header_h
    n_data = 0
    g_idx = 0
    for row in rows:
        if row[0] == "__GROUP__":
            g_idx += 1
            label = row[1]
            kind = row[2]
            if kind == "accenture":
                bg = BRAND_PRIMARY_MID
                fg = WHITE
            else:
                bg = CARD_BG
                fg = BRAND_ACCENT
            add_rect(slide, f"group-{g_idx}-header-bg", tbl_left, y, tbl_w, group_h, bg)
            add_text(slide, f"group-{g_idx}-header", f"▪ {label}",
                     x_px=tbl_left + 12, y_px=y + 4, w_px=tbl_w - 24, h_px=14,
                     font_size_px=9, color=fg, bold=True, uppercase=True)
            y += group_h
            continue
        n_data += 1
        num, action, owner, (due, due_color), (status, pill_bg, pill_txt) = row
        row_bg = RGBColor(0xFA, 0xFA, 0xFA) if (n_data % 2 == 1) else WHITE
        add_rect(slide, f"table-row-{n_data}-bg", tbl_left, y, tbl_w, row_h, row_bg)
        # Num
        add_text(slide, f"table-row-{n_data}-num", num,
                 x_px=col_x[0], y_px=y + 12, w_px=col_w[0], h_px=18,
                 font_size_px=13, color=BRAND_ACCENT, bold=True, align="center")
        # Action
        add_text(slide, f"table-row-{n_data}-cell-2", action,
                 x_px=col_x[1] + 8, y_px=y + 8, w_px=col_w[1] - 16, h_px=row_h - 12,
                 font_size_px=11, color=TEXT_DARK)
        # Owner pill (chip)
        chip_w = 110
        add_text(slide, f"table-row-{n_data}-cell-3", owner,
                 x_px=col_x[2] + 8, y_px=y + 12, w_px=chip_w, h_px=18,
                 font_size_px=10, color=WHITE, bold=True, align="center",
                 bg_fill=BRAND_PRIMARY_MID, padding_px=(3, 6, 3, 6))
        # Due
        add_text(slide, f"table-row-{n_data}-cell-4", due,
                 x_px=col_x[3] + 8, y_px=y + 12, w_px=col_w[3] - 16, h_px=18,
                 font_size_px=11, color=due_color, bold=True)
        # Status pill
        add_text(slide, f"table-row-{n_data}-status-pill", status,
                 x_px=col_x[4] + 8, y_px=y + 12, w_px=col_w[4] - 16, h_px=18,
                 font_size_px=9, color=pill_txt, bold=True, align="center",
                 bg_fill=pill_bg, padding_px=(2, 6, 2, 6), uppercase=True)
        # Row divider
        add_rect(slide, f"table-row-{n_data}-divider",
                 tbl_left, y + row_h - 1, tbl_w, 1, RGBColor(0xF0, 0xEB, 0xF8))
        y += row_h

    # Summary chips
    sum_y = y + 12
    add_text(slide, "summary-label", "SUMMARY",
             x_px=tbl_left, y_px=sum_y, w_px=80, h_px=18,
             font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True)
    chips = [
        ("3 this week", RGBColor(0xD9, 0x77, 0x06)),
        ("4 complete", RGBColor(0x16, 0xA3, 0x4A)),
        ("0 blocked", RGBColor(0xDC, 0x26, 0x26)),
    ]
    cx = tbl_left + 88
    for i, (label, dot_c) in enumerate(chips):
        n = i + 1
        add_rect(slide, f"summary-chip-{n}-dot", cx + 8, sum_y + 6, 6, 6, dot_c)
        add_text(slide, f"summary-chip-{n}", label,
                 x_px=cx + 20, y_px=sum_y, w_px=110, h_px=18,
                 font_size_px=10, color=BRAND_PRIMARY_MID, bold=True,
                 bg_fill=CARD_BG, padding_px=(3, 8, 3, 4))
        cx += 130

    add_footer(slide, page_num=233)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "233_closing-next-steps.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
