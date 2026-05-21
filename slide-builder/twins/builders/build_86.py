"""
Builder for pattern 86: Risk register table (6 rows, RAG status pills).

Source HTML: _pattern-library/86_risk-register-table.html
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
RED_SOFT = RGBColor(0xFD, 0xEC, 0xEC)
AMBER_SOFT = RGBColor(0xFE, 0xF3, 0xC7)
GREEN_SOFT = RGBColor(0xDC, 0xFC, 0xE7)
RED_TXT = RGBColor(0x9B, 0x1C, 0x1C)
AMBER_TXT = RGBColor(0x8A, 0x5A, 0x0B)
GREEN_TXT = RGBColor(0x15, 0x7A, 0x43)
RED_ROW_BG = RGBColor(0xFD, 0xF2, 0xF2)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Eyebrow + title block — compact so brand-rule sits near y≈128
    add_text(slide, "eyebrow", "Risk register · pilot",
             x_px=48, y_px=50, w_px=400, h_px=14,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "title",
             "Risk register — six tracked, two reds with mitigation owners.",
             x_px=48, y_px=66, w_px=820, h_px=44,
             font_size_px=24, color=TEXT_DARK, bold=True)
    add_text(slide, "subtitle",
             "Detail backing the heat map: each risk has impact/likelihood, current RAG, owned mitigation, and a single accountable name. Ordered by RAG, reds on top.",
             x_px=48, y_px=110, w_px=820, h_px=18,
             font_size_px=12, color=TEXT_MID)
    add_rect(slide, "brand-rule", 48, 134, 56, 3, BRAND_ACCENT)

    # RAG legend — below subheadline+brand-rule, right-aligned (right edge ≈ 1216)
    leg_w = 380
    leg_h = 40
    leg_x = 1216 - leg_w
    leg_y = 160
    leg = add_rect(slide, "rag-legend", leg_x, leg_y, leg_w, leg_h, RGBColor(0xFB, 0xFA, 0xFD))
    leg.line.color.rgb = CARD_BORDER
    leg.line.width = 9525
    add_text(slide, "legend-title", "RAG",
             x_px=leg_x + 10, y_px=leg_y + 13, w_px=30, h_px=14,
             font_size_px=9, color=TEXT_MID, bold=True, uppercase=True, align="left")

    legend_items = [
        ("Green", RAG_GREEN),
        ("Amber", RAG_AMBER),
        ("Red", RAG_RED),
    ]
    li_x = leg_x + 50
    li_y = leg_y + 13
    for i, (label, color) in enumerate(legend_items):
        n = i + 1
        ix = li_x + i * 110
        add_rect(slide, f"legend-{n}-swatch", ix, li_y + 3, 10, 10, color)
        add_text(slide, f"legend-{n}-label", label,
                 x_px=ix + 16, y_px=li_y, w_px=80, h_px=14,
                 font_size_px=9, color=TEXT_DARK, bold=True, uppercase=True)

    # Table — pushed down to clear legend (legend bottom ≈ 200)
    tbl_left = 48
    tbl_top = 218
    tbl_w = 1280 - 96  # 1184
    # Column widths (percent → px)
    col_pct = [0.04, 0.26, 0.07, 0.09, 0.11, 0.28, 0.15]
    col_w = [int(tbl_w * p) for p in col_pct]
    # Adjust last col to absorb rounding
    col_w[-1] = tbl_w - sum(col_w[:-1])
    col_x = [tbl_left]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    headers = ["#", "Risk description", "Impact", "Likelihood", "RAG", "Mitigation", "Owner"]
    centered = {0, 2, 3, 4}
    header_h = 32
    add_rect(slide, "table-head-bg", tbl_left, tbl_top, tbl_w, header_h, BRAND_PRIMARY)
    for i, h in enumerate(headers):
        align = "center" if i in centered else "left"
        add_text(slide, f"table-col-{i+1}-header", h,
                 x_px=col_x[i] + 8, y_px=tbl_top + 8, w_px=col_w[i] - 16, h_px=18,
                 font_size_px=9, color=WHITE, bold=True, align=align, uppercase=True)

    # Rows
    rows = [
        ("R1", "Stakeholder withdrawal mid-pilot", "H", "M", "Red",
         "MD weekly check-in", "MP", "Mario"),
        ("R2", "Scope creep beyond pilot charter", "H", "H", "Red",
         "Charter signed at kickoff", "MR", "Maria"),
        ("R3", "Tooling provisioning delay", "M", "L", "Amber",
         "Pre-arranged with IT", "PM", "PMO"),
        ("R4", "Vendor (Claude) outage", "H", "L", "Amber",
         "Offline mode for build", "EN", "Engineering"),
        ("R5", "Resistance from senior consultants", "M", "M", "Amber",
         "Coach pairing", "MP", "Mario"),
        ("R6", "Junior team can't ramp on toolchain", "M", "M", "Green",
         "Onboarding session run W1", "CO", "Coach"),
    ]
    row_h = 44
    body_top = tbl_top + header_h
    for ri, (num, risk, impact, lik, rag, mit, av, owner) in enumerate(rows):
        n = ri + 1
        ry = body_top + ri * row_h
        # Row background — red tint for above-red
        is_red = rag == "Red"
        row_bg = RED_ROW_BG if is_red else WHITE
        add_rect(slide, f"table-row-{n}-bg", tbl_left, ry, tbl_w, row_h, row_bg)
        # Left bar for above-red
        if is_red:
            add_rect(slide, f"table-row-{n}-flag", tbl_left, ry, 3, row_h, RAG_RED)
        # Row top border
        add_rect(slide, f"table-row-{n}-divider", tbl_left, ry, tbl_w, 1, CARD_BORDER)

        # Cell 1: num
        add_text(slide, f"table-row-{n}-num", num,
                 x_px=col_x[0], y_px=ry + 10, w_px=col_w[0], h_px=20,
                 font_size_px=11, color=BRAND_ACCENT, bold=True, align="center")
        # Cell 2: risk description
        add_text(slide, f"table-row-{n}-cell-2", risk,
                 x_px=col_x[1] + 8, y_px=ry + 10, w_px=col_w[1] - 16, h_px=28,
                 font_size_px=11, color=TEXT_DARK, bold=True)
        # Cell 3: impact pill
        if impact == "H":
            ibg, itxt = RED_SOFT, RED_TXT
        elif impact == "M":
            ibg, itxt = AMBER_SOFT, AMBER_TXT
        else:
            ibg, itxt = GREEN_SOFT, GREEN_TXT
        add_text(slide, f"table-row-{n}-cell-3", impact,
                 x_px=col_x[2] + (col_w[2] - 32) // 2, y_px=ry + 12, w_px=32, h_px=18,
                 font_size_px=10, color=itxt, bold=True, align="center",
                 bg_fill=ibg, padding_px=(2, 4, 2, 4))
        # Cell 4: likelihood pill
        if lik == "H":
            lbg, ltxt = RED_SOFT, RED_TXT
        elif lik == "M":
            lbg, ltxt = AMBER_SOFT, AMBER_TXT
        else:
            lbg, ltxt = GREEN_SOFT, GREEN_TXT
        add_text(slide, f"table-row-{n}-cell-4", lik,
                 x_px=col_x[3] + (col_w[3] - 32) // 2, y_px=ry + 12, w_px=32, h_px=18,
                 font_size_px=10, color=ltxt, bold=True, align="center",
                 bg_fill=lbg, padding_px=(2, 4, 2, 4))
        # Cell 5: RAG status pill
        if rag == "Red":
            rbg, rtxt, rdot = RED_SOFT, RED_TXT, RAG_RED
        elif rag == "Amber":
            rbg, rtxt, rdot = AMBER_SOFT, AMBER_TXT, RAG_AMBER
        else:
            rbg, rtxt, rdot = GREEN_SOFT, GREEN_TXT, RAG_GREEN
        pill_x = col_x[4] + (col_w[4] - 80) // 2
        add_text(slide, f"table-row-{n}-status-pill", rag,
                 x_px=pill_x, y_px=ry + 12, w_px=80, h_px=18,
                 font_size_px=9, color=rtxt, bold=True, align="center", uppercase=True,
                 bg_fill=rbg, padding_px=(2, 18, 2, 4))
        add_rect(slide, f"table-row-{n}-rag-dot", pill_x + 6, ry + 16, 9, 9, rdot)
        # Cell 6: mitigation
        add_text(slide, f"table-row-{n}-cell-6", f"“{mit}”",
                 x_px=col_x[5] + 8, y_px=ry + 12, w_px=col_w[5] - 16, h_px=28,
                 font_size_px=11, color=TEXT_DARK, italic=True)
        # Cell 7: owner
        add_rect(slide, f"table-row-{n}-avatar", col_x[6] + 8, ry + 12, 22, 22, CARD_BG)
        add_text(slide, f"table-row-{n}-avatar-text", av,
                 x_px=col_x[6] + 8, y_px=ry + 12, w_px=22, h_px=22,
                 font_size_px=9, color=BRAND_PRIMARY, bold=True,
                 align="center", anchor="middle")
        add_text(slide, f"table-row-{n}-cell-7", owner,
                 x_px=col_x[6] + 36, y_px=ry + 14, w_px=col_w[6] - 44, h_px=20,
                 font_size_px=11, color=TEXT_DARK, bold=True)

    # Table outer border
    add_rect(slide, "table-border-top", tbl_left, tbl_top, tbl_w, 1, CARD_BORDER)
    add_rect(slide, "table-border-left", tbl_left, tbl_top, 1, header_h + row_h * len(rows), CARD_BORDER)
    add_rect(slide, "table-border-right", tbl_left + tbl_w - 1, tbl_top, 1,
             header_h + row_h * len(rows), CARD_BORDER)
    add_rect(slide, "table-border-bottom",
             tbl_left, tbl_top + header_h + row_h * len(rows), tbl_w, 1, CARD_BORDER)

    # Convergence — gradient feel emulated by solid brand-primary; left accent
    conv_y = 720 - 56 - 56
    conv_h = 50
    conv_w = 1280 - 96
    add_rect(slide, "convergence-bg", 48, conv_y, conv_w, conv_h, BRAND_PRIMARY)
    add_text(slide, "convergence-mark", "SO WHAT",
             x_px=48 + 14, y_px=conv_y + 14, w_px=80, h_px=22,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center",
             bg_fill=BRAND_PRIMARY_MID, padding_px=(3, 6, 3, 6))
    add_text(
        slide, "convergence",
        "Two reds, both with mitigation owners assigned. Watch for week-3 status — if either stays red, escalate to steering.",
        x_px=48 + 110, y_px=conv_y, w_px=conv_w - 130, h_px=conv_h,
        font_size_px=13, color=WHITE, anchor="middle",
    )

    add_footer(slide, page_num=86)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "86_risk-register-table.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
