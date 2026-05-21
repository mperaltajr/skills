"""
Builder for pattern 53: Scenario timeline — shared axis + impact rail (table).

5 columns: scenario label | month-bar (4 segments) | impact.
4 data rows. Manual table placement.

Source HTML: _pattern-library/53_scenario-timeline-impact-rail.html
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

SC_BASE = RGBColor(0x2D, 0x0A, 0x4E)
SC_1 = RGBColor(0x5C, 0x2D, 0x87)
SC_2 = RGBColor(0x8E, 0x3F, 0xB8)
SC_3 = RGBColor(0xA1, 0x00, 0xFF)
SC_BASE_TINT = RGBColor(0xF0, 0xEA, 0xF6)
SC_1_TINT = RGBColor(0xF0, 0xE5, 0xF8)
SC_2_TINT = RGBColor(0xF4, 0xE6, 0xFB)
SC_3_TINT = RGBColor(0xF7, 0xEA, 0xFF)
ZEBRA = RGBColor(0xFB, 0xF8, 0xFE)
RISK_BG = RGBColor(0xFE, 0xF3, 0xF2)
RISK_INK = RGBColor(0xB4, 0x23, 0x18)
RISK_BORDER = RGBColor(0xDC, 0x26, 0x26)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_text(
        slide, "title",
        "Four exit scenarios on one timeline — delay multiplies the risk.",
        x_px=56, y_px=50, w_px=1050, h_px=66,
        font_size_px=27, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "~530 FTEs in scope across all scenarios. Each waypoint is a decision point; "
        "the slope of exits drives savings at risk.",
        x_px=56, y_px=120, w_px=1050, h_px=22,
        font_size_px=14, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 56, 168, 56, 3, BRAND_ACCENT)

    # Grid: scenario(160) | timeline(1fr) | impact(168)
    g_left = 56
    g_right = 1280 - 56
    g_top = 196
    g_bottom = 720 - 80 - 72  # leave room for takeaway (~60) + footer
    g_w = g_right - g_left
    g_h = g_bottom - g_top

    sc_w = 160
    imp_w = 168
    tl_w = g_w - sc_w - imp_w

    # Header row (36px)
    head_h = 36
    add_rect(slide, "h-scenario", g_left, g_top, sc_w, head_h, BRAND_PRIMARY)
    add_rect(slide, "month-bar", g_left + sc_w, g_top, tl_w, head_h, BRAND_PRIMARY)
    add_rect(slide, "h-impact", g_left + sc_w + tl_w, g_top, imp_w, head_h, BRAND_PRIMARY)

    add_text(
        slide, "table-col-1-header", "SCENARIO",
        x_px=g_left, y_px=g_top, w_px=sc_w, h_px=head_h,
        font_size_px=11, color=WHITE, bold=True, anchor="middle", align="center", uppercase=True,
    )
    # Month segments — flex: 17.7, 32.3, 32.3, 17.7 (sums 100)
    flex_pcts = [17.7, 32.3, 32.3, 17.7]
    months = ["MARCH", "APRIL", "MAY", "JUNE"]
    seg_x = g_left + sc_w
    seg_widths = []
    total = 0.0
    for f in flex_pcts:
        w = int(tl_w * f / 100.0)
        seg_widths.append(w)
        total += w
    # Adjust last to fill
    seg_widths[-1] += tl_w - total
    sx = seg_x
    for i, (mw, mname) in enumerate(zip(seg_widths, months)):
        n = i + 1
        add_text(
            slide, f"timeline-tick-{n}-label", mname,
            x_px=sx, y_px=g_top, w_px=mw, h_px=head_h,
            font_size_px=11, color=WHITE, bold=True, anchor="middle", align="center",
        )
        sx += mw

    add_text(
        slide, "table-col-3-header", "IMPACT",
        x_px=g_left + sc_w + tl_w, y_px=g_top, w_px=imp_w, h_px=head_h,
        font_size_px=11, color=WHITE, bold=True, anchor="middle", align="center", uppercase=True,
    )

    # Body rows
    row_h = (g_h - head_h) // 4
    rows = [
        ("Base case", "Reference", SC_BASE, SC_BASE_TINT, False,
         [(5, "327"), (20.5, "60"), (49.5, "143")], "$0", "vs. plan"),
        ("Scenario 1", "Moderate slip", SC_1, SC_1_TINT, True,
         [(10.8, "106"), (48.5, "382"), (95, "43")], "$5.0M", "savings at risk"),
        ("Scenario 2", "Heavy slip", SC_2, SC_2_TINT, False,
         [(44.7, "477"), (95, "53")], "$6.4M", "savings at risk"),
        ("Scenario 3", "Accelerated", SC_3, SC_3_TINT, True,
         [(10.8, "424"), (29.2, "106")], "$343K", "savings at risk"),
    ]

    timeline_x0 = g_left + sc_w
    for ri, (name, tag, color, tint, zebra, dots, imp_amt, imp_note) in enumerate(rows):
        n = ri + 1
        ry = g_top + head_h + ri * row_h

        # Scenario label cell
        add_rect(slide, f"scenario-{n}-label-bg", g_left, ry, sc_w, row_h, CARD_BG)
        add_text(
            slide, f"scenario-{n}-name", name,
            x_px=g_left + 14, y_px=ry + 18, w_px=sc_w - 28, h_px=22,
            font_size_px=14, color=color, bold=True,
        )
        add_text(
            slide, f"scenario-{n}-tag", tag.upper(),
            x_px=g_left + 14, y_px=ry + 42, w_px=sc_w - 28, h_px=14,
            font_size_px=10, color=color, bold=True, uppercase=True,
        )

        # Timeline cell (zebra or white)
        tl_bg = ZEBRA if zebra else WHITE
        add_rect(slide, f"scenario-{n}-timeline", timeline_x0, ry, tl_w, row_h, tl_bg)

        # Draw track from first dot to last dot
        if dots:
            first_pct = dots[0][0]
            last_pct = dots[-1][0]
            track_x = timeline_x0 + int(tl_w * first_pct / 100.0)
            track_xe = timeline_x0 + int(tl_w * last_pct / 100.0)
            cy = ry + row_h // 2
            add_rect(slide, f"scenario-{n}-track", track_x, cy - 1, track_xe - track_x, 3, color)

            for di, (pct, fte) in enumerate(dots):
                dn = di + 1
                dx = timeline_x0 + int(tl_w * pct / 100.0)
                is_final = (di == len(dots) - 1)
                d_w = 18 if is_final else 11
                add_rect(slide, f"scenario-{n}-dot-{dn}",
                         dx - d_w // 2, cy - d_w // 2, d_w, d_w, color)
                add_text(
                    slide, f"scenario-{n}-fte-{dn}", fte,
                    x_px=dx - 30, y_px=cy + 12, w_px=60, h_px=16,
                    font_size_px=12, color=color, bold=True, align="center",
                )

        # Impact cell
        ix = g_left + sc_w + tl_w
        add_rect(slide, f"scenario-{n}-impact-bg", ix, ry, imp_w, row_h, tint)
        add_text(
            slide, f"scenario-{n}-impact-amount", imp_amt,
            x_px=ix, y_px=ry + row_h // 2 - 22, w_px=imp_w, h_px=28,
            font_size_px=22, color=color, bold=True, align="center",
        )
        add_text(
            slide, f"scenario-{n}-impact-note", imp_note,
            x_px=ix, y_px=ry + row_h // 2 + 8, w_px=imp_w, h_px=14,
            font_size_px=10, color=TEXT_MID, bold=True, align="center",
        )

    # Takeaway alert strip
    ta_y = g_bottom + 8
    add_rect(slide, "convergence-bg", g_left, ta_y, g_w, 44, RISK_BG)
    add_rect(slide, "convergence-accent", g_left, ta_y, 4, 44, RISK_BORDER)
    add_text(
        slide, "convergence-mark", "KEY RISK",
        x_px=g_left + 18, y_px=ta_y, w_px=80, h_px=44,
        font_size_px=10, color=RISK_INK, bold=True, anchor="middle", uppercase=True,
    )
    add_text(
        slide, "convergence",
        "A smooth transition is the priority — exit timing, however, matters. "
        "Delays cost up to $1.2M / week of foregone savings.",
        x_px=g_left + 110, y_px=ta_y, w_px=g_w - 130, h_px=44,
        font_size_px=13, color=TEXT_DARK, anchor="middle",
    )

    add_footer(slide, page_num=53)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "53_scenario-timeline-impact-rail.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
