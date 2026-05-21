"""
Builder for pattern 54: Scenario comparison ledger (5-col table).

Source HTML: _pattern-library/54_scenario-comparison-ledger.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

GOOD_BG = RGBColor(0xEC, 0xFD, 0xF3)
GOOD_INK = RGBColor(0x02, 0x7A, 0x48)
WARN_BG = RGBColor(0xFF, 0xFA, 0xEB)
WARN_INK = RGBColor(0xB5, 0x47, 0x08)
BAD_BG = RGBColor(0xFE, 0xF3, 0xF2)
BAD_INK = RGBColor(0xB4, 0x23, 0x18)
ZEBRA = RGBColor(0xFB, 0xF8, 0xFE)
BAR_TRACK = RGBColor(0xEE, 0xE6, 0xF5)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_text(
        slide, "title",
        "Four scenarios, one comparison — Scenario 1 is the only viable path.",
        x_px=56, y_px=50, w_px=1050, h_px=66,
        font_size_px=27, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Same KPIs, same rules, line them up side-by-side. Verdict reflects feasibility "
        "against transition risk and cash impact.",
        x_px=56, y_px=120, w_px=1050, h_px=22,
        font_size_px=14, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 56, 168, 56, 3, BRAND_ACCENT)

    g_left = 56
    g_right = 1280 - 56
    g_top = 196
    g_w = g_right - g_left
    g_bottom = 720 - 80 - 56  # leave room for footnote and footer
    g_h = g_bottom - g_top

    # Columns: 1.4fr 1fr 1fr 1.1fr 1.2fr (total 5.7)
    fr_units = [1.4, 1.0, 1.0, 1.1, 1.2]
    total_fr = sum(fr_units)
    col_widths = [int(g_w * fr / total_fr) for fr in fr_units]
    col_widths[-1] = g_w - sum(col_widths[:-1])

    # Header row
    head_h = 42
    add_rect(slide, "ledger-head-bg", g_left, g_top, g_w, head_h, BRAND_PRIMARY)
    headers = ["SCENARIO", "EXIT COMPLETION", "SAVINGS AT RISK", "FINAL EXIT", "VERDICT"]
    cx = g_left
    for i, hdr in enumerate(headers):
        add_text(
            slide, f"table-col-{i + 1}-header", hdr,
            x_px=cx + 18, y_px=g_top, w_px=col_widths[i] - 36, h_px=head_h,
            font_size_px=10, color=WHITE, bold=True, anchor="middle", uppercase=True,
        )
        cx += col_widths[i]

    # 4 data rows
    row_h = (g_h - head_h) // 4
    rows = [
        # (tag, name, sub, comp_val, comp_unit, imp_amt, imp_color, timing, timing_note,
        #  verdict_pill_text, verdict_color, verdict_note, zebra)
        ("REFERENCE", "Base case", "Planned glide path",
         "100%", "530 FTE exit by Apr 30",
         "$0", BRAND_PRIMARY, "Apr 30", "Within window",
         "Baseline", GOOD_BG, GOOD_INK, "Target outcome — no slip.", False),
        ("MODERATE SLIP", "Scenario 1", "Phased through June",
         "100%", "531 FTE by Jun 16",
         "$5.0M", BAD_INK, "Jun 16", "+47 days",
         "Recommended", GOOD_BG, GOOD_INK, "Preserves transition quality.", True),
        ("HEAVY SLIP", "Scenario 2", "Compressed late-window",
         "100%", "530 FTE by Jun 16",
         "$6.4M", BAD_INK, "Jun 16", "+47 days",
         "Viable", WARN_BG, WARN_INK, "Same end date, worse cash.", False),
        ("ACCELERATED", "Scenario 3", "All exits by Apr 9",
         "100%", "530 FTE by Apr 9",
         "$343K", BAD_INK, "Apr 9", "−21 days",
         "Not viable", BAD_BG, BAD_INK, "Breaks knowledge transfer.", True),
    ]

    for ri, (tag, name, sub, cv, cu, ia, ic, tv, tn, vp, vbg, vink, vnote, zebra) in enumerate(rows):
        n = ri + 1
        ry = g_top + head_h + ri * row_h
        bg = ZEBRA if zebra else WHITE

        # Row background across all cells
        add_rect(slide, f"row-{n}-bg", g_left, ry, g_w, row_h, bg)
        # Row separator (top border)
        add_rect(slide, f"row-{n}-rule", g_left, ry, g_w, 1, CARD_BORDER)

        # Cell 1: label (with CARD_BG override for non-zebra)
        cx = g_left
        if not zebra:
            add_rect(slide, f"row-{n}-label-bg", cx, ry, col_widths[0], row_h, CARD_BG)
        # tag
        add_text(
            slide, f"scenario-{n}-tag", tag,
            x_px=cx + 18, y_px=ry + 14, w_px=col_widths[0] - 36, h_px=14,
            font_size_px=10, color=BRAND_PRIMARY if ri == 0 else BRAND_PRIMARY_MID,
            bold=True, uppercase=True,
        )
        # name
        add_text(
            slide, f"scenario-{n}-name", name,
            x_px=cx + 18, y_px=ry + 32, w_px=col_widths[0] - 36, h_px=22,
            font_size_px=17, color=TEXT_DARK, bold=True,
        )
        # sub
        add_text(
            slide, f"scenario-{n}-sub", sub,
            x_px=cx + 18, y_px=ry + 58, w_px=col_widths[0] - 36, h_px=18,
            font_size_px=11, color=TEXT_MID,
        )
        cx += col_widths[0]

        # Cell 2: completion (value + unit + bar)
        add_text(
            slide, f"scenario-{n}-completion-value", cv,
            x_px=cx + 18, y_px=ry + 14, w_px=col_widths[1] - 36, h_px=28,
            font_size_px=22, color=BRAND_PRIMARY, bold=True,
        )
        add_text(
            slide, f"scenario-{n}-completion-unit", cu,
            x_px=cx + 18, y_px=ry + 44, w_px=col_widths[1] - 36, h_px=16,
            font_size_px=11, color=TEXT_MID, bold=True,
        )
        # bar (full width, since all 100%)
        bar_y = ry + 64
        add_rect(slide, f"row-{n}-bar-track", cx + 18, bar_y, col_widths[1] - 36, 6, BAR_TRACK)
        add_rect(slide, f"scenario-{n}-completion-bar", cx + 18, bar_y, col_widths[1] - 36, 6, BRAND_ACCENT)
        cx += col_widths[1]

        # Cell 3: savings at risk
        add_text(
            slide, f"scenario-{n}-impact-amount", ia,
            x_px=cx + 18, y_px=ry + 14, w_px=col_widths[2] - 36, h_px=28,
            font_size_px=22, color=ic, bold=True,
        )
        add_text(
            slide, f"scenario-{n}-impact-note",
            "— on plan" if ia == "$0" else "▼ vs. base",
            x_px=cx + 18, y_px=ry + 44, w_px=col_widths[2] - 36, h_px=16,
            font_size_px=11, color=TEXT_MID if ia == "$0" else BAD_INK, bold=True,
        )
        cx += col_widths[2]

        # Cell 4: timing
        add_text(
            slide, f"scenario-{n}-timing-value", tv,
            x_px=cx + 18, y_px=ry + 14, w_px=col_widths[3] - 36, h_px=28,
            font_size_px=22, color=BRAND_PRIMARY, bold=True,
        )
        add_text(
            slide, f"scenario-{n}-timing-note", tn,
            x_px=cx + 18, y_px=ry + 44, w_px=col_widths[3] - 36, h_px=16,
            font_size_px=11, color=TEXT_MID, bold=True,
        )
        cx += col_widths[3]

        # Cell 5: verdict pill + note
        add_text(
            slide, f"scenario-{n}-verdict-pill", vp.upper(),
            x_px=cx + 18, y_px=ry + 16, w_px=col_widths[4] - 36, h_px=22,
            font_size_px=11, color=vink, bold=True, align="center", uppercase=True,
            bg_fill=vbg, padding_px=(3, 12, 3, 12),
        )
        add_text(
            slide, f"scenario-{n}-verdict-note", vnote,
            x_px=cx + 18, y_px=ry + 46, w_px=col_widths[4] - 36, h_px=32,
            font_size_px=11, color=TEXT_MID,
        )

    # Footnote strip / convergence
    fn_y = g_bottom + 8
    fn_h = 40
    add_rect(slide, "convergence-bg", g_left, fn_y, g_w, fn_h, CARD_BG)
    add_rect(slide, "convergence-accent", g_left, fn_y, 4, fn_h, BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "Read: rows are scenarios, columns are the same four lenses. "
        "Verdict combines cash impact with transition feasibility — not just dollars.",
        x_px=g_left + 18, y_px=fn_y, w_px=g_w - 36, h_px=fn_h,
        font_size_px=12, color=TEXT_MID, anchor="middle",
    )

    add_footer(slide, page_num=54)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "54_scenario-comparison-ledger.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
