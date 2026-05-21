"""
Builder for pattern 61d: Trade-off pros and cons (dark variant).

Source HTML: _pattern-library/61_tradeoff-pros-cons-dark.html
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

PROS_TINT = RGBColor(0x10, 0x4A, 0x28)
CONS_TINT = RGBColor(0x66, 0x1A, 0x15)
CHECK_GOOD = RGBColor(0x6E, 0xE0, 0x9E)
CHECK_NO = RGBColor(0xFF, 0x8A, 0x82)
PROS_TEXT = RGBColor(0xB4, 0xF0, 0xC9)
CONS_TEXT = RGBColor(0xFF, 0xC9, 0xC4)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Three rollout options — pros and cons, with our recommendation.",
        x_px=64, y_px=20, w_px=1100, h_px=80,
        font_size_px=26, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Pick option B — the cons are addressable; the pros are not replaceable.",
        x_px=64, y_px=108, w_px=1000, h_px=22,
        font_size_px=13, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    g_top = 188
    g_left = 56
    g_right = 1280 - 56
    g_bottom = 720 - 80 - 56
    g_w = g_right - g_left
    g_h = g_bottom - g_top

    col_gap = 10
    opt_w = 280
    rec_w = 150
    pc_w = (g_w - opt_w - rec_w - 3 * col_gap) // 2

    head_h = 22
    cx = g_left
    add_text(
        slide, "compare-col-1-header", "OPTION",
        x_px=cx + 14, y_px=g_top, w_px=opt_w - 14, h_px=head_h,
        font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, uppercase=True,
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
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True,
    )

    rows_top = g_top + head_h + 4
    rows_h = g_h - head_h - 4
    row_gap = 8
    row_h = (rows_h - 2 * row_gap) // 3

    rows = [
        ("Option A", "Internal pilot", "Run inside one practice; stay quiet externally.",
         ["Low risk, reversible", "Internal-only — no external exposure", "Cheap to start"],
         ["Limited learning — small sample", "Slow ramp to firm-wide value", "No firm-wide signal of commitment"],
         "—", "Too small to learn from", False),
        ("Option B · Recommended", "Full practice rollout", "Ship to the whole practice; measure and publish.",
         ["Real measurement at meaningful N", "Builds the case for firm-wide scale", "Demonstrates leadership commitment"],
         ["Higher initial investment", "Exposes early failure visibly", "Requires onboarding bandwidth"],
         "PICK", "Best risk-adjusted learning", True),
        ("Option C", "Firm-wide license", "Buy a vendor product; deploy everywhere.",
         ["Vendor support out of the box", "Scale is immediate", "Predictable cost line"],
         ["No internal IP — nothing proprietary", "Vendor lock-in on roadmap & price", "Can't tune to our taste or templates"],
         "—", "Surrenders the IP advantage", False),
    ]

    for ri, (letter, name, desc, pros, cons, rmark, rnote, is_pick) in enumerate(rows):
        n = ri + 1
        ry = rows_top + ri * (row_h + row_gap)

        opt = add_rect(slide, f"row-{n}-opt-bg", g_left, ry, opt_w, row_h, CARD_BG_DARK)
        opt.line.color.rgb = BRAND_ACCENT_SOFT if is_pick else CARD_BORDER_DARK
        opt.line.width = 25400 if is_pick else 9525
        add_rect(slide, f"row-{n}-opt-stripe", g_left, ry, 4,
                 row_h, BRAND_ACCENT_SOFT if is_pick else BRAND_PRIMARY_MID)

        add_text(
            slide, f"compare-row-{n}-letter", letter.upper(),
            x_px=g_left + 14, y_px=ry + 12, w_px=opt_w - 28, h_px=12,
            font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"compare-row-{n}-label", name.upper(),
            x_px=g_left + 14, y_px=ry + 28, w_px=opt_w - 28, h_px=22,
            font_size_px=14, color=WHITE, bold=True, uppercase=True,
        )
        add_text(
            slide, f"compare-row-{n}-desc", desc,
            x_px=g_left + 14, y_px=ry + 54, w_px=opt_w - 28, h_px=row_h - 64,
            font_size_px=11, color=TEXT_ON_DARK_MID,
        )

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

        cx += pc_w + col_gap
        rec_bg_color = BRAND_ACCENT if is_pick else CARD_BG_DARK
        rec = add_rect(slide, f"compare-row-{n}-rec", cx, ry, rec_w, row_h, rec_bg_color)
        if not is_pick:
            rec.line.color.rgb = CARD_BORDER_DARK
            rec.line.width = 9525
        add_text(
            slide, f"compare-row-{n}-rec-mark", rmark,
            x_px=cx, y_px=ry + 12, w_px=rec_w, h_px=28,
            font_size_px=18 if is_pick else 16,
            color=WHITE if is_pick else TEXT_ON_DARK_FAINT,
            bold=True, align="center", uppercase=True,
        )
        add_text(
            slide, f"compare-row-{n}-rec-note", rnote,
            x_px=cx + 8, y_px=ry + 48, w_px=rec_w - 16, h_px=row_h - 60,
            font_size_px=10,
            color=WHITE if is_pick else TEXT_ON_DARK_FAINT,
            italic=not is_pick,
            bold=is_pick,
            align="center",
        )

    cv_y = g_bottom + 4
    cv_h = 38
    add_rect(slide, "convergence-bg", g_left, cv_y, g_w, cv_h, RGBColor(0x1A, 0x05, 0x30))
    add_rect(slide, "convergence-accent", g_left, cv_y, 3, cv_h, BRAND_ACCENT_SOFT)
    add_text(
        slide, "convergence",
        "Pick option B — the cons are addressable; the pros are not replaceable.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_w - 44, h_px=cv_h,
        font_size_px=13, color=WHITE, italic=True, bold=True, anchor="middle",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "61",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "61d_tradeoff-pros-cons.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
