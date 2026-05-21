"""
Builder for pattern 63: RACI matrix (5 activities x 5 roles + legend).

Manual table placement. Uses table-row-N-cell-M + table-col-N-header IDs.

Source HTML: _pattern-library/63_raci-matrix.html
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


def RGBColor_from_hex(r, g, b):
    return RGBColor(r, g, b)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title block (with eyebrow)
    add_text(
        slide, "eyebrow", "ROLES & RESPONSIBILITIES",
        x_px=48, y_px=48, w_px=600, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True,
    )
    add_text(
        slide, "title",
        "Pilot RACI — who decides, who does, who's in the loop.",
        x_px=48, y_px=66, w_px=900, h_px=40,
        font_size_px=26, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Five activities across the pilot lifecycle, mapped to five roles. "
        "One accountable per row keeps decisions unambiguous.",
        x_px=48, y_px=112, w_px=900, h_px=22,
        font_size_px=13, color=TEXT_MID,
    )
    add_rect(slide, "brand-rule", 48, 144, 56, 3, BRAND_ACCENT)

    # RACI legend — BELOW subtitle/brand-rule, right-aligned (right edge ≈ 1216).
    # Widened to fit Responsible/Accountable/Consulted/Informed on one line.
    leg_w = 520
    leg_h = 36
    leg_x = 1216 - leg_w
    leg_y = 160
    leg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, RGBColor_from_hex(0xFB, 0xFA, 0xFD))
    leg.line.color.rgb = CARD_BORDER
    leg.line.width = 9525

    add_text(
        slide, "legend-title", "RACI KEY",
        x_px=leg_x + 10, y_px=leg_y, w_px=70, h_px=leg_h,
        font_size_px=9, color=TEXT_MID, bold=True, anchor="middle", uppercase=True,
    )

    raci_items = [
        ("R", "Responsible", BRAND_ACCENT, WHITE),
        ("A", "Accountable", BRAND_PRIMARY, WHITE),
        ("C", "Consulted", BRAND_PRIMARY_MID, WHITE),
        ("I", "Informed", CARD_BG, BRAND_PRIMARY),
    ]
    item_x = leg_x + 90
    item_step = 105  # swatch (18) + gap (4) + label (~70) + gap before next item
    label_w = 78
    for i, (letter, label, swatch_bg, swatch_fg) in enumerate(raci_items):
        n = i + 1
        sx = item_x + i * item_step
        add_text(
            slide, f"legend-{n}-swatch", letter,
            x_px=sx, y_px=leg_y + 9, w_px=18, h_px=18,
            font_size_px=10, color=swatch_fg, bold=True, align="center",
            bg_fill=swatch_bg, padding_px=(0, 0, 0, 0),
        )
        add_text(
            slide, f"legend-{n}-label", label,
            x_px=sx + 22, y_px=leg_y + 11, w_px=label_w, h_px=14,
            font_size_px=9, color=TEXT_DARK, bold=True,
        )

    # Table
    t_left = 48
    t_right = 1280 - 48
    t_top = 230
    t_bottom = 720 - 32 - 70  # leave room for convergence + thin footer
    t_w = t_right - t_left
    t_h = t_bottom - t_top

    # Columns: activity (32%) + 5 role cols (13.6% each)
    act_w = int(t_w * 0.32)
    role_w = (t_w - act_w) // 5

    head_h = 44
    add_rect(slide, "table-head-bg", t_left, t_top, t_w, head_h, BRAND_PRIMARY)

    add_text(
        slide, "table-col-1-header", "ACTIVITY",
        x_px=t_left + 14, y_px=t_top, w_px=act_w - 14, h_px=head_h,
        font_size_px=10, color=WHITE, bold=True, anchor="middle", uppercase=True,
    )
    roles = [
        ("Program MD", "Sponsor"),
        ("Workstream Lead", "Delivery"),
        ("Slide Lab Coach", "Method"),
        ("Analyst", "Build"),
        ("Practice PM", "Ops"),
    ]
    for i, (role, sub) in enumerate(roles):
        n = i + 2
        cx = t_left + act_w + i * role_w
        add_text(
            slide, f"table-col-{n}-header", role,
            x_px=cx, y_px=t_top + 6, w_px=role_w, h_px=18,
            font_size_px=10, color=WHITE, bold=True, align="center", uppercase=True,
        )
        add_text(
            slide, f"table-col-{n}-sub", sub.upper(),
            x_px=cx, y_px=t_top + 24, w_px=role_w, h_px=14,
            font_size_px=8, color=BRAND_ACCENT_SOFT, align="center", uppercase=True,
        )

    # Body rows
    activities = [
        ("Activity 1", "Approve pilot scope", ["A", "C", "I", "I", "R"]),
        ("Activity 2", "Run storyline sessions", ["I", "C", "AR", "C", "I"]),
        ("Activity 3", "Build decks", ["I", "A", "C", "R", "I"]),
        ("Activity 4", "Weekly review", ["A", "R", "C", "I", "I"]),
        ("Activity 5", "Decide on rollout", ["A", "C", "I", "I", "C"]),
    ]
    row_h = (t_h - head_h) // 5

    chip_colors = {
        "R": (BRAND_ACCENT, WHITE),
        "A": (BRAND_PRIMARY, WHITE),
        "C": (BRAND_PRIMARY_MID, WHITE),
        "I": (CARD_BG, BRAND_PRIMARY),
    }

    for ri, (act_num, act_name, cells) in enumerate(activities):
        n = ri + 1
        ry = t_top + head_h + ri * row_h

        # Activity cell
        add_rect(slide, f"row-{n}-act-bg", t_left, ry, act_w, row_h, CARD_BG)
        add_text(
            slide, f"table-row-{n}-num", act_num.upper(),
            x_px=t_left + 14, y_px=ry + 12, w_px=act_w - 28, h_px=12,
            font_size_px=9, color=BRAND_ACCENT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"table-row-{n}-label", act_name,
            x_px=t_left + 14, y_px=ry + 28, w_px=act_w - 28, h_px=row_h - 36,
            font_size_px=12, color=BRAND_PRIMARY, bold=True,
        )

        # Role cells (5)
        for ci, cell_val in enumerate(cells):
            cn = ci + 2  # cell M starts at 2 because col 1 is the activity label
            cx = t_left + act_w + ci * role_w
            # Row separator (top)
            if ri > 0:
                add_rect(slide, f"row-{n}-rule-{ci}", cx, ry, role_w, 1, CARD_BORDER)
            # Cell - stack chips if multi-letter (e.g. "AR")
            chip_w = 30
            letters = list(cell_val)
            total_w = len(letters) * chip_w + (len(letters) - 1) * 5 if len(letters) > 1 else chip_w
            chip_x = cx + (role_w - total_w) // 2
            chip_y = ry + (row_h - chip_w) // 2

            cell_id = f"table-row-{n}-cell-{cn}"
            # Render first chip with the cell id
            for li, letter in enumerate(letters):
                bg, fg = chip_colors[letter]
                shape_id = cell_id if li == 0 else f"{cell_id}-extra-{li}"
                add_text(
                    slide, shape_id, letter,
                    x_px=chip_x + li * (chip_w + 5), y_px=chip_y,
                    w_px=chip_w, h_px=chip_w,
                    font_size_px=14, color=fg, bold=True, align="center", anchor="middle",
                    bg_fill=bg, padding_px=(0, 0, 0, 0),
                )

    # Convergence (gradient band approximated as solid primary)
    cv_y = 720 - 32 - 56
    cv_h = 50
    add_rect(slide, "convergence-bg", 48, cv_y, 1280 - 96, cv_h, BRAND_PRIMARY)
    add_text(
        slide, "convergence-mark", "SO WHAT",
        x_px=66, y_px=cv_y + 14, w_px=70, h_px=22,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True,
        bg_fill=None, padding_px=(0, 0, 0, 0),
    )
    # Border around tag
    tag_frame = add_rect(slide, "convergence-tag-frame", 60, cv_y + 12, 80, 24, BRAND_PRIMARY)
    tag_frame.line.color.rgb = BRAND_ACCENT_SOFT
    tag_frame.line.width = 9525
    add_text(
        slide, "convergence", "Two A's on any row means no one's accountable. Watch the A column — exactly one per activity, no exceptions.",
        x_px=160, y_px=cv_y, w_px=1280 - 96 - 120, h_px=cv_h,
        font_size_px=13, color=WHITE, anchor="middle",
    )

    # Footer
    add_footer(slide, page_num=63)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "63_raci-matrix.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
