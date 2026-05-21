"""
Builder for pattern 54d: Scenario comparison ledger (dark variant).

Source HTML: _pattern-library/54_scenario-comparison-ledger-dark.html
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

GOOD_BG = RGBColor(0x10, 0x4A, 0x28)
GOOD_INK = RGBColor(0x6E, 0xE0, 0x9E)
WARN_BG = RGBColor(0x6E, 0x44, 0x10)
WARN_INK = RGBColor(0xFF, 0xC7, 0x6E)
BAD_BG = RGBColor(0x66, 0x1A, 0x15)
BAD_INK = RGBColor(0xFF, 0x8A, 0x82)
ZEBRA = RGBColor(0x36, 0x18, 0x55)
BAR_TRACK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Four scenarios, one comparison — Scenario 1 is the only viable path.",
        x_px=64, y_px=20, w_px=1050, h_px=80,
        font_size_px=27, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Same KPIs, same rules, line them up side-by-side. Verdict reflects feasibility against transition risk and cash impact.",
        x_px=64, y_px=108, w_px=1050, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    g_left = 56
    g_right = 1280 - 56
    g_top = 220
    g_w = g_right - g_left
    g_bottom = 720 - 80 - 56
    g_h = g_bottom - g_top

    fr_units = [1.4, 1.0, 1.0, 1.1, 1.2]
    total_fr = sum(fr_units)
    col_widths = [int(g_w * fr / total_fr) for fr in fr_units]
    col_widths[-1] = g_w - sum(col_widths[:-1])

    head_h = 42
    add_rect(slide, "ledger-head-bg", g_left, g_top, g_w, head_h, RGBColor(0x1A, 0x05, 0x30))
    headers = ["SCENARIO", "EXIT COMPLETION", "SAVINGS AT RISK", "FINAL EXIT", "VERDICT"]
    cx = g_left
    for i, hdr in enumerate(headers):
        add_text(
            slide, f"table-col-{i + 1}-header", hdr,
            x_px=cx + 18, y_px=g_top, w_px=col_widths[i] - 36, h_px=head_h,
            font_size_px=10, color=WHITE, bold=True, anchor="middle", uppercase=True,
        )
        cx += col_widths[i]

    row_h = (g_h - head_h) // 4
    rows = [
        ("REFERENCE", "Base case", "Planned glide path",
         "100%", "530 FTE exit by Apr 30",
         "$0", BRAND_ACCENT_SOFT, "Apr 30", "Within window",
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
        bg_c = ZEBRA if zebra else CARD_BG_DARK

        add_rect(slide, f"row-{n}-bg", g_left, ry, g_w, row_h, bg_c)
        add_rect(slide, f"row-{n}-rule", g_left, ry, g_w, 1, CARD_BORDER_DARK)

        cx = g_left
        add_text(
            slide, f"scenario-{n}-tag", tag,
            x_px=cx + 18, y_px=ry + 14, w_px=col_widths[0] - 36, h_px=14,
            font_size_px=10, color=BRAND_ACCENT_SOFT if ri == 0 else BRAND_ACCENT,
            bold=True, uppercase=True,
        )
        add_text(
            slide, f"scenario-{n}-name", name,
            x_px=cx + 18, y_px=ry + 32, w_px=col_widths[0] - 36, h_px=22,
            font_size_px=17, color=WHITE, bold=True,
        )
        add_text(
            slide, f"scenario-{n}-sub", sub,
            x_px=cx + 18, y_px=ry + 58, w_px=col_widths[0] - 36, h_px=18,
            font_size_px=11, color=TEXT_ON_DARK_MID,
        )
        cx += col_widths[0]

        add_text(
            slide, f"scenario-{n}-completion-value", cv,
            x_px=cx + 18, y_px=ry + 14, w_px=col_widths[1] - 36, h_px=28,
            font_size_px=22, color=WHITE, bold=True,
        )
        add_text(
            slide, f"scenario-{n}-completion-unit", cu,
            x_px=cx + 18, y_px=ry + 44, w_px=col_widths[1] - 36, h_px=16,
            font_size_px=11, color=TEXT_ON_DARK_MID, bold=True,
        )
        bar_y = ry + 64
        add_rect(slide, f"row-{n}-bar-track", cx + 18, bar_y, col_widths[1] - 36, 6, BAR_TRACK)
        add_rect(slide, f"scenario-{n}-completion-bar", cx + 18, bar_y, col_widths[1] - 36, 6, BRAND_ACCENT_SOFT)
        cx += col_widths[1]

        add_text(
            slide, f"scenario-{n}-impact-amount", ia,
            x_px=cx + 18, y_px=ry + 14, w_px=col_widths[2] - 36, h_px=28,
            font_size_px=22, color=ic, bold=True,
        )
        add_text(
            slide, f"scenario-{n}-impact-note",
            "— on plan" if ia == "$0" else "▼ vs. base",
            x_px=cx + 18, y_px=ry + 44, w_px=col_widths[2] - 36, h_px=16,
            font_size_px=11, color=TEXT_ON_DARK_MID if ia == "$0" else BAD_INK, bold=True,
        )
        cx += col_widths[2]

        add_text(
            slide, f"scenario-{n}-timing-value", tv,
            x_px=cx + 18, y_px=ry + 14, w_px=col_widths[3] - 36, h_px=28,
            font_size_px=22, color=WHITE, bold=True,
        )
        add_text(
            slide, f"scenario-{n}-timing-note", tn,
            x_px=cx + 18, y_px=ry + 44, w_px=col_widths[3] - 36, h_px=16,
            font_size_px=11, color=TEXT_ON_DARK_MID, bold=True,
        )
        cx += col_widths[3]

        add_text(
            slide, f"scenario-{n}-verdict-pill", vp.upper(),
            x_px=cx + 18, y_px=ry + 16, w_px=col_widths[4] - 36, h_px=22,
            font_size_px=11, color=vink, bold=True, align="center", uppercase=True,
            bg_fill=vbg, padding_px=(3, 12, 3, 12),
        )
        add_text(
            slide, f"scenario-{n}-verdict-note", vnote,
            x_px=cx + 18, y_px=ry + 46, w_px=col_widths[4] - 36, h_px=32,
            font_size_px=11, color=TEXT_ON_DARK_MID,
        )

    fn_y = g_bottom + 8
    fn_h = 40
    add_rect(slide, "convergence-bg", g_left, fn_y, g_w, fn_h, CARD_BG_DARK)
    add_rect(slide, "convergence-accent", g_left, fn_y, 4, fn_h, BRAND_ACCENT_SOFT)
    add_text(
        slide, "convergence",
        "Read: rows are scenarios, columns are the same four lenses. Verdict combines cash impact with transition feasibility.",
        x_px=g_left + 18, y_px=fn_y, w_px=g_w - 36, h_px=fn_h,
        font_size_px=12, color=TEXT_ON_DARK_MID, anchor="middle",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "54",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "54d_scenario-comparison-ledger.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
