"""
Builder for pattern 78: Weighted decision matrix.

Title + right-pushed score-scale legend. 5×5 table: Criteria, Weight%, Option A,
Option B (Winner highlighted), Option C. Each score cell shows raw + weighted.
Bottom: total row (winner column gets accent fill), then convergence band.

Source HTML: _pattern-library/78_decision-matrix-weighted.html
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

WINNER_TINT = RGBColor(0xF7, 0xEC, 0xFE)
LEG_BG = RGBColor(0xFB, 0xFA, 0xFD)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # --- Title block ---
    add_text(
        slide, "eyebrow", "Weighted decision matrix",
        x_px=48, y_px=50, w_px=900, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=2, uppercase=True,
    )
    add_text(
        slide, "title",
        "Three rollout options, scored — Option B wins on weighted total.",
        x_px=48, y_px=70, w_px=900, h_px=42,
        font_size_px=24, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Five criteria, weighted by strategic importance. Each option scored 1–5 on raw merit; weighted scores roll up to a single comparable total.",
        x_px=48, y_px=118, w_px=900, h_px=36,
        font_size_px=12, color=TEXT_MID,
    )
    add_rect(slide, "brand-rule", x_px=48, y_px=158, w_px=56, h_px=3, fill_color=BRAND_ACCENT)

    # --- Scoring legend — BELOW subheadline (HARD RULE: top-y >= 230, right-aligned to x ~1240)
    # Compact horizontal layout: title | pips | anchors, so the legend fits in the band above
    # the matrix without forcing the table off the slide.
    leg_w = 380
    leg_h = 40
    leg_x = 1240 - leg_w  # right edge at 1240 (HARD RULE)
    leg_y = 230
    leg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, LEG_BG)
    leg.line.color.rgb = CARD_BORDER
    leg.line.width = 9525
    add_text(
        slide, "legend-title", "Raw score",
        x_px=leg_x + 10, y_px=leg_y, w_px=64, h_px=leg_h,
        font_size_px=8, color=TEXT_MID, bold=True,
        letter_spacing_px=1.2, uppercase=True, anchor="middle",
    )
    # 5 pips, sized to fit horizontally next to the title and anchor labels
    pip_w = 20
    pip_gap = 3
    pip_total = 5 * pip_w + 4 * pip_gap
    pip_band_x = leg_x + 80
    px_start = pip_band_x + (200 - pip_total) // 2  # center pips inside a 200-wide band
    py = leg_y + (leg_h - 20) // 2  # vertical center
    for i in range(5):
        n = i + 1
        pix = px_start + i * (pip_w + pip_gap)
        pip = add_rect(slide, f"legend-pip-{n}", pix, py, pip_w, 20, CARD_BG)
        pip.line.color.rgb = CARD_BORDER
        pip.line.width = 6350
        add_text(
            slide, f"legend-pip-{n}-text", str(n),
            x_px=pix, y_px=py, w_px=pip_w, h_px=20,
            font_size_px=10, color=BRAND_PRIMARY, bold=True,
            align="center", anchor="middle",
        )
    add_text(
        slide, "legend-anchor-low", "Poor",
        x_px=pip_band_x - 6, y_px=leg_y, w_px=30, h_px=leg_h,
        font_size_px=8, color=TEXT_FAINT, bold=True,
        letter_spacing_px=0.4, uppercase=True, anchor="middle", align="right",
    )
    add_text(
        slide, "legend-anchor-high", "Excellent",
        x_px=pip_band_x + 200, y_px=leg_y, w_px=70, h_px=leg_h,
        font_size_px=8, color=TEXT_FAINT, bold=True, align="left",
        letter_spacing_px=0.4, uppercase=True, anchor="middle",
    )

    # --- Table --- (shifted to clear legend at y=230..270)
    table_top = 280
    table_left = 48
    table_w = 1280 - 96
    col_pct = [0.30, 0.10, 0.20, 0.20, 0.20]
    col_widths = [int(table_w * p) for p in col_pct]
    col_x = [table_left]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)

    # Header row
    header_h = 42
    add_rect(slide, "table-header-bg", table_left, table_top, table_w, header_h, BRAND_PRIMARY)
    headers = [
        ("Criteria", None, False),
        ("Weight", "%", False),
        ("Option A", "Big bang", False),
        ("Option B", "Phased rollout", True),
        ("Option C", "Pilot only", False),
    ]
    for i, (h, sub, is_winner) in enumerate(headers):
        n = i + 1
        if is_winner:
            # Slightly different background for winner
            add_rect(slide, f"col-{n}-winner-bg", col_x[i], table_top, col_widths[i], header_h, BRAND_PRIMARY_MID)
            # Winner badge
            add_rect(slide, f"col-{n}-winner-badge-bg", col_x[i] + col_widths[i] - 56, table_top + 4, 50, 14, BRAND_ACCENT)
            add_text(
                slide, f"col-{n}-winner-badge", "Winner",
                x_px=col_x[i] + col_widths[i] - 56, y_px=table_top + 4, w_px=50, h_px=14,
                font_size_px=7, color=WHITE, bold=True, align="center", anchor="middle",
                letter_spacing_px=1, uppercase=True,
            )
        align = "left" if i == 0 else "center"
        add_text(
            slide, f"col-header-{n}", h,
            x_px=col_x[i] + 12, y_px=table_top + 4, w_px=col_widths[i] - 24, h_px=18,
            font_size_px=10, color=WHITE, bold=True, align=align,
            letter_spacing_px=1.2, uppercase=True,
        )
        if sub:
            add_text(
                slide, f"col-subhead-{n}", sub,
                x_px=col_x[i] + 12, y_px=table_top + 22, w_px=col_widths[i] - 24, h_px=16,
                font_size_px=8, color=BRAND_ACCENT_SOFT, align=align,
                letter_spacing_px=1, uppercase=True,
            )

    # Body rows
    rows = [
        ("Criterion 1", "Cycle time impact",      "30%", ("3", "0.90"), ("5", "1.50"), ("4", "1.20")),
        ("Criterion 2", "Cost",                   "20%", ("5", "1.00"), ("3", "0.60"), ("2", "0.40")),
        ("Criterion 3", "Risk",                   "20%", ("5", "1.00"), ("4", "0.80"), ("2", "0.40")),
        ("Criterion 4", "Strategic optionality",  "15%", ("2", "0.30"), ("4", "0.60"), ("3", "0.45")),
        ("Criterion 5", "Time-to-impact",         "15%", ("4", "0.60"), ("3", "0.45"), ("2", "0.30")),
    ]
    row_h = 42
    body_top = table_top + header_h
    winner_col = 3  # index in col_x for Option B
    for ri, (crit_num, crit_name, weight, a, b, c) in enumerate(rows):
        n = ri + 1
        ry = body_top + ri * row_h
        # Criteria cell bg
        add_rect(slide, f"row-{n}-crit-bg", col_x[0], ry, col_widths[0], row_h, CARD_BG)
        add_rect(slide, f"row-{n}-crit-rule-r", col_x[0] + col_widths[0] - 1, ry, 2, row_h, CARD_BORDER)
        add_text(
            slide, f"row-{n}-crit-num", crit_num,
            x_px=col_x[0] + 14, y_px=ry + 4, w_px=col_widths[0] - 28, h_px=12,
            font_size_px=7, color=BRAND_ACCENT, bold=True,
            letter_spacing_px=1.4, uppercase=True,
        )
        add_text(
            slide, f"row-{n}-crit-name", crit_name,
            x_px=col_x[0] + 14, y_px=ry + 18, w_px=col_widths[0] - 28, h_px=20,
            font_size_px=11, color=BRAND_PRIMARY, bold=True,
        )
        # Weight cell
        add_rect(slide, f"row-{n}-weight-bg", col_x[1], ry, col_widths[1], row_h, LEG_BG)
        add_text(
            slide, f"row-{n}-weight", weight,
            x_px=col_x[1], y_px=ry, w_px=col_widths[1], h_px=row_h,
            font_size_px=13, color=BRAND_PRIMARY, bold=True, align="center", anchor="middle",
        )
        # Option cells
        for oi, (raw, wt) in enumerate([a, b, c]):
            cn = oi + 2  # col index 2,3,4
            cx = col_x[cn]
            cw = col_widths[cn]
            is_winner_col = (cn == winner_col)
            cell_bg = WINNER_TINT if is_winner_col else WHITE
            add_rect(slide, f"row-{n}-opt-{oi+1}-bg", cx, ry, cw, row_h, cell_bg)
            if is_winner_col:
                add_rect(slide, f"row-{n}-opt-{oi+1}-left", cx, ry, 2, row_h, BRAND_ACCENT)
                add_rect(slide, f"row-{n}-opt-{oi+1}-right", cx + cw - 2, ry, 2, row_h, BRAND_ACCENT)
            # Top rule
            add_rect(slide, f"row-{n}-opt-{oi+1}-toprule", cx, ry, cw, 1, CARD_BORDER)
            raw_color = BRAND_PRIMARY if is_winner_col else TEXT_DARK
            wt_color = BRAND_ACCENT if is_winner_col else TEXT_MID
            add_text(
                slide, f"row-{n}-opt-{oi+1}-raw", raw,
                x_px=cx, y_px=ry + 4, w_px=cw, h_px=20,
                font_size_px=16, color=raw_color, bold=True, align="center", anchor="middle",
            )
            add_text(
                slide, f"row-{n}-opt-{oi+1}-wt", wt,
                x_px=cx, y_px=ry + 24, w_px=cw, h_px=14,
                font_size_px=9, color=wt_color, align="center", anchor="middle",
            )

    # Total row
    total_y = body_top + len(rows) * row_h
    total_h = 42
    # label
    add_rect(slide, "total-label-bg", col_x[0], total_y, col_widths[0], total_h, BRAND_PRIMARY)
    add_text(
        slide, "total-label", "Weighted total",
        x_px=col_x[0] + 14, y_px=total_y, w_px=col_widths[0] - 28, h_px=total_h,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, anchor="middle",
        letter_spacing_px=1.6, uppercase=True,
    )
    # weight
    add_rect(slide, "total-weight-bg", col_x[1], total_y, col_widths[1], total_h, BRAND_PRIMARY_MID)
    add_text(
        slide, "total-weight", "100%",
        x_px=col_x[1], y_px=total_y, w_px=col_widths[1], h_px=total_h,
        font_size_px=12, color=WHITE, bold=True, align="center", anchor="middle",
    )
    # totals
    totals = ["3.65", "4.05", "2.75"]
    for oi, val in enumerate(totals):
        cn = oi + 2
        cx = col_x[cn]
        cw = col_widths[cn]
        is_winner_col = (cn == winner_col)
        bg = BRAND_ACCENT if is_winner_col else BRAND_PRIMARY
        add_rect(slide, f"total-opt-{oi+1}-bg", cx, total_y, cw, total_h, bg)
        add_text(
            slide, f"total-opt-{oi+1}-val", val,
            x_px=cx, y_px=total_y, w_px=cw - 18, h_px=total_h,
            font_size_px=22, color=WHITE, bold=True, align="center", anchor="middle",
        )
        add_text(
            slide, f"total-opt-{oi+1}-out", "/5",
            x_px=cx + cw - 28, y_px=total_y + 14, w_px=28, h_px=22,
            font_size_px=10, color=BRAND_ACCENT_SOFT if is_winner_col else BRAND_ACCENT_SOFT,
            anchor="middle",
        )

    # --- Convergence band --- (sits below total row at y=574)
    conv_y = 590
    conv_h = 40
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, conv_h, BRAND_PRIMARY)
    add_rect(slide, "convergence-tag-bg", 60, conv_y + 10, 60, 20, BRAND_PRIMARY)
    add_text(
        slide, "convergence-tag", "So what",
        x_px=60, y_px=conv_y + 10, w_px=60, h_px=20,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center", anchor="middle",
        letter_spacing_px=1.6, uppercase=True,
    )
    add_text(
        slide, "convergence",
        "Option B wins on <strong>three of five criteria</strong>, including the heaviest — cycle time impact at 30%. A's cost advantage isn't enough to close the gap.",
        x_px=130, y_px=conv_y, w_px=1280 - 96 - 90, h_px=conv_h,
        font_size_px=12, color=WHITE, anchor="middle",
        emphasis_color=BRAND_ACCENT_SOFT,
    )

    add_footer(slide, page_num=78)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "78_decision-matrix-weighted.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
