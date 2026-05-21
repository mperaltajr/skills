"""
Builder for pattern 61: Trade-off pros and cons (3 rows, recommended highlight).

4 columns: option / pros / cons / recommendation.

Source HTML: _pattern-library/61_tradeoff-pros-cons.html
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

PROS_TINT = RGBColor(0xDC, 0xFC, 0xE7)
CONS_TINT = RGBColor(0xFE, 0xCA, 0xCA)
CHECK_GOOD = RGBColor(0x16, 0xA3, 0x4A)
CHECK_NO = RGBColor(0xDC, 0x26, 0x26)
PROS_TEXT = RGBColor(0x14, 0x53, 0x2D)
CONS_TEXT = RGBColor(0x7F, 0x1D, 0x1D)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_text(
        slide, "title",
        "Three rollout options — pros and cons, with our recommendation.",
        x_px=56, y_px=50, w_px=1100, h_px=64,
        font_size_px=26, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Pick option B — the cons are addressable; the pros are not replaceable.",
        x_px=56, y_px=116, w_px=1000, h_px=22,
        font_size_px=13, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 56, 152, 56, 3, BRAND_ACCENT)

    # Content
    g_top = 170
    g_left = 56
    g_right = 1280 - 56
    g_bottom = 720 - 80 - 56  # leave room for convergence (~44) + footer
    g_w = g_right - g_left
    g_h = g_bottom - g_top

    col_gap = 10
    opt_w = 280
    rec_w = 150
    pc_w = (g_w - opt_w - rec_w - 3 * col_gap) // 2

    # Column header strip (22px)
    head_h = 22
    cx = g_left
    add_text(
        slide, "compare-col-1-header", "OPTION",
        x_px=cx + 14, y_px=g_top, w_px=opt_w - 14, h_px=head_h,
        font_size_px=10, color=TEXT_MID, bold=True, uppercase=True,
    )
    cx += opt_w + col_gap
    add_text(
        slide, "compare-col-2-header", "PROS",
        x_px=cx + 14, y_px=g_top, w_px=pc_w - 14, h_px=head_h,
        font_size_px=10, color=CHECK_GOOD, bold=True, uppercase=True,
    )
    cx += pc_w + col_gap
    add_text(
        slide, "compare-col-3-header", "CONS",
        x_px=cx + 14, y_px=g_top, w_px=pc_w - 14, h_px=head_h,
        font_size_px=10, color=CHECK_NO, bold=True, uppercase=True,
    )
    cx += pc_w + col_gap
    add_text(
        slide, "compare-col-4-header", "RECOMMENDATION",
        x_px=cx, y_px=g_top, w_px=rec_w, h_px=head_h,
        font_size_px=10, color=BRAND_ACCENT, bold=True, align="center", uppercase=True,
    )

    # Rows
    rows_top = g_top + head_h + 4
    rows_h = g_h - head_h - 4
    row_gap = 8
    row_h = (rows_h - 2 * row_gap) // 3

    rows = [
        ("Option A", "Internal pilot", "Run inside one practice; stay quiet externally.",
         ["Low risk, reversible",
          "Internal-only — no external exposure",
          "Cheap to start"],
         ["Limited learning — small sample",
          "Slow ramp to firm-wide value",
          "No firm-wide signal of commitment"],
         "—", "Too small to learn from", False),
        ("Option B · Recommended", "Full practice rollout", "Ship to the whole practice; measure and publish.",
         ["Real measurement at meaningful N",
          "Builds the case for firm-wide scale",
          "Demonstrates leadership commitment"],
         ["Higher initial investment",
          "Exposes early failure visibly",
          "Requires onboarding bandwidth"],
         "PICK", "Best risk-adjusted learning", True),
        ("Option C", "Firm-wide license", "Buy a vendor product; deploy everywhere.",
         ["Vendor support out of the box",
          "Scale is immediate",
          "Predictable cost line"],
         ["No internal IP — nothing proprietary",
          "Vendor lock-in on roadmap & price",
          "Can't tune to our taste or templates"],
         "—", "Surrenders the IP advantage", False),
    ]

    for ri, (letter, name, desc, pros, cons, rmark, rnote, is_pick) in enumerate(rows):
        n = ri + 1
        ry = rows_top + ri * (row_h + row_gap)

        # Option cell
        opt = add_rect(slide, f"row-{n}-opt-bg", g_left, ry, opt_w, row_h,
                       WHITE if is_pick else CARD_BG)
        opt.line.color.rgb = BRAND_ACCENT if is_pick else CARD_BORDER
        opt.line.width = 25400 if is_pick else 9525
        # Left stripe (4px)
        add_rect(slide, f"row-{n}-opt-stripe", g_left, ry, 4,
                 row_h, BRAND_ACCENT if is_pick else BRAND_PRIMARY_MID)

        add_text(
            slide, f"compare-row-{n}-letter", letter.upper(),
            x_px=g_left + 14, y_px=ry + 12, w_px=opt_w - 28, h_px=12,
            font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"compare-row-{n}-label", name.upper(),
            x_px=g_left + 14, y_px=ry + 28, w_px=opt_w - 28, h_px=22,
            font_size_px=14, color=BRAND_PRIMARY, bold=True, uppercase=True,
        )
        add_text(
            slide, f"compare-row-{n}-desc", desc,
            x_px=g_left + 14, y_px=ry + 54, w_px=opt_w - 28, h_px=row_h - 64,
            font_size_px=11, color=TEXT_MID,
        )

        # Pros cell
        cx = g_left + opt_w + col_gap
        pros_bg = add_rect(slide, f"row-{n}-pros-bg", cx, ry, pc_w, row_h, PROS_TINT)
        pros_bg.line.color.rgb = CHECK_GOOD
        pros_bg.line.width = 9525
        for pi, p in enumerate(pros):
            pn = pi + 1
            py = ry + 10 + pi * ((row_h - 20) // len(pros))
            add_text(
                slide, f"compare-row-{n}-pros-item-{pn}", f"✓  {p}",
                x_px=cx + 14, y_px=py, w_px=pc_w - 28, h_px=24,
                font_size_px=11, color=PROS_TEXT,
            )

        # Cons cell
        cx += pc_w + col_gap
        cons_bg = add_rect(slide, f"row-{n}-cons-bg", cx, ry, pc_w, row_h, CONS_TINT)
        cons_bg.line.color.rgb = CHECK_NO
        cons_bg.line.width = 9525
        for ci, c in enumerate(cons):
            cn = ci + 1
            cy = ry + 10 + ci * ((row_h - 20) // len(cons))
            add_text(
                slide, f"compare-row-{n}-cons-item-{cn}", f"✕  {c}",
                x_px=cx + 14, y_px=cy, w_px=pc_w - 28, h_px=24,
                font_size_px=11, color=CONS_TEXT,
            )

        # Recommendation cell
        cx += pc_w + col_gap
        rec_bg_color = BRAND_ACCENT if is_pick else WHITE
        rec = add_rect(slide, f"compare-row-{n}-rec", cx, ry, rec_w, row_h, rec_bg_color)
        if not is_pick:
            rec.line.color.rgb = CARD_BORDER
            rec.line.width = 9525
        add_text(
            slide, f"compare-row-{n}-rec-mark", rmark,
            x_px=cx, y_px=ry + 12, w_px=rec_w, h_px=28,
            font_size_px=18 if is_pick else 16,
            color=WHITE if is_pick else TEXT_FAINT,
            bold=True, align="center", uppercase=True,
        )
        add_text(
            slide, f"compare-row-{n}-rec-note", rnote,
            x_px=cx + 8, y_px=ry + 48, w_px=rec_w - 16, h_px=row_h - 60,
            font_size_px=10,
            color=WHITE if is_pick else TEXT_FAINT,
            italic=not is_pick,
            bold=is_pick,
            align="center",
        )

    # Convergence
    cv_y = g_bottom + 4
    cv_h = 38
    add_rect(slide, "convergence-bg", g_left, cv_y, g_w, cv_h, BRAND_PRIMARY)
    add_rect(slide, "convergence-accent", g_left, cv_y, 3, cv_h, BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "Pick option B — the cons are addressable; the pros are not replaceable.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_w - 44, h_px=cv_h,
        font_size_px=13, color=WHITE, italic=True, bold=True, anchor="middle",
    )

    add_footer(slide, page_num=61)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "61_tradeoff-pros-cons.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
