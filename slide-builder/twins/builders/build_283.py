"""
Builder for pattern 283: Sprint plan (2-week, 6 workstreams × 10 days).

Source HTML: _pattern-library/283_sprint-plan-2week.html

Goal strip + week/day grid + Gantt bars + bottom panels (blockers + velocity).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

BLOCKER_BG = RGBColor(0xFE, 0xF2, 0xF2)
BLOCKER_BAR = RGBColor(0xEF, 0x44, 0x44)
BLOCKER_RED = RGBColor(0xB9, 0x1C, 0x1C)
QA_GRAY = RGBColor(0xCB, 0xD5, 0xE1)
ALT_BG = RGBColor(0xFB, 0xF8, 0xFE)
GREEN_OK = RGBColor(0x16, 0xA3, 0x4A)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Sprint 14 · <strong>Two-week delivery plan</strong>",
        subtitle="Day-by-day task allocation across workstreams — 19 May to 30 May 2026",
    )

    # Goal strip
    gs_y = 232
    gs_h = 36
    gs = add_rect(slide, "goal-strip", 56, gs_y, 1280 - 112, gs_h, CARD_BG)
    gs.line.color.rgb = CARD_BORDER
    gs.line.width = 9525
    add_text(
        slide, "goal-label", "SPRINT 14 GOAL:",
        x_px=68, y_px=gs_y, w_px=130, h_px=gs_h,
        font_size_px=10, color=BRAND_ACCENT, bold=True, anchor="middle",
        uppercase=True, letter_spacing_px=1.4,
    )
    add_text(
        slide, "goal-text",
        "Complete API integration layer and user acceptance testing for module 3.",
        x_px=200, y_px=gs_y, w_px=720, h_px=gs_h,
        font_size_px=12, color=TEXT_DARK, anchor="middle",
    )
    add_text(
        slide, "sprint-dates", "19 May – 30 May 2026",
        x_px=1280 - 56 - 200, y_px=gs_y, w_px=190, h_px=gs_h,
        font_size_px=11, color=TEXT_MID, bold=True, anchor="middle", align="right",
    )

    # Grid layout
    g_x = 56
    g_y = 280
    g_w = 1280 - 112
    g_h = 270
    label_w = 130
    day_w = (g_w - label_w) // 10

    # Week header
    wh_y = g_y
    wh_h = 22
    # corner label
    add_rect(slide, "wh-corner-bg", g_x, wh_y, label_w, wh_h, CARD_BG)
    add_text(
        slide, "wh-corner", "WORKSTREAM",
        x_px=g_x + 12, y_px=wh_y, w_px=label_w - 12, h_px=wh_h,
        font_size_px=9, color=TEXT_FAINT, bold=True, anchor="middle",
        uppercase=True, letter_spacing_px=1.2,
    )
    # week 1
    w1_x = g_x + label_w
    w1_w = day_w * 5
    add_rect(slide, "week-1-bg", w1_x, wh_y, w1_w, wh_h, BRAND_PRIMARY_MID)
    add_text(
        slide, "week-1-label", "Week 1 · Mon 19 – Fri 23 May",
        x_px=w1_x, y_px=wh_y, w_px=w1_w, h_px=wh_h,
        font_size_px=10, color=WHITE, bold=True, align="center", anchor="middle",
    )
    # week 2
    w2_x = w1_x + w1_w
    add_rect(slide, "week-2-bg", w2_x, wh_y, day_w * 5, wh_h, BRAND_PRIMARY)
    add_text(
        slide, "week-2-label", "Week 2 · Mon 26 – Fri 30 May",
        x_px=w2_x, y_px=wh_y, w_px=day_w * 5, h_px=wh_h,
        font_size_px=10, color=WHITE, bold=True, align="center", anchor="middle",
    )

    # Day headers
    dh_y = wh_y + wh_h
    dh_h = 20
    days = ["Mon 19", "Tue 20", "Wed 21", "Thu 22", "Fri 23",
            "Mon 26", "Tue 27", "Wed 28", "Thu 29", "Fri 30"]
    add_rect(slide, "dh-bg", g_x, dh_y, g_w, dh_h, CARD_BG)
    add_text(
        slide, "dh-corner", "DAY",
        x_px=g_x + 12, y_px=dh_y, w_px=label_w - 12, h_px=dh_h,
        font_size_px=9, color=TEXT_FAINT, anchor="middle",
        uppercase=True, letter_spacing_px=1.2,
    )
    for i, d in enumerate(days):
        dx = g_x + label_w + i * day_w
        color = BRAND_ACCENT if i == 0 else TEXT_MID
        bold = (i == 0)
        add_text(
            slide, f"day-{i+1}", d,
            x_px=dx, y_px=dh_y, w_px=day_w, h_px=dh_h,
            font_size_px=9, color=color, bold=bold, anchor="middle", align="center",
        )

    # Task grid rows
    rows_top = dh_y + dh_h
    rows_h = g_h - wh_h - dh_h
    workstreams = [
        ("UX Design",          [(1, 3, BRAND_ACCENT_SOFT, "Wireframes & flows"),
                                (6, 3, BRAND_ACCENT_SOFT, "UAT screens")]),
        ("Frontend Dev",       [(1, 8, BRAND_ACCENT, "API integration UI")]),
        ("Backend Dev",        [(1, 10, BRAND_PRIMARY_MID, "API layer build · full sprint")]),
        ("QA Testing",         [(4, 7, QA_GRAY, "Test cases · regression · UAT sign-off")]),
        ("Data Engineering",   [(1, 5, BRAND_ACCENT_SOFT, "Pipeline & schema setup")]),
        ("Stakeholder Review", [(10, 1, BRAND_PRIMARY, "Review")]),
    ]
    row_h = rows_h // len(workstreams)
    for ri, (ws_name, bars) in enumerate(workstreams):
        ry = rows_top + ri * row_h
        # Label cell
        label_bg = add_rect(slide, f"row-{ri+1}-label-bg", g_x, ry, label_w, row_h, WHITE)
        label_bg.line.color.rgb = CARD_BORDER
        label_bg.line.width = 9525
        add_text(
            slide, f"row-{ri+1}-label", ws_name,
            x_px=g_x + 12, y_px=ry, w_px=label_w - 12, h_px=row_h,
            font_size_px=11, color=TEXT_DARK, bold=True, anchor="middle",
        )
        # Cell backgrounds (alternating)
        for ci in range(10):
            cx = g_x + label_w + ci * day_w
            bg = ALT_BG if ci % 2 == 1 else WHITE
            cell = add_rect(slide, f"row-{ri+1}-cell-{ci+1}", cx, ry, day_w, row_h, bg)
            # Light right border
            if ci < 9:
                add_rect(slide, f"row-{ri+1}-cell-{ci+1}-rule",
                         cx + day_w - 1, ry, 1, row_h, CARD_BORDER)
        # Row bottom border
        add_rect(slide, f"row-{ri+1}-bottom-rule", g_x, ry + row_h - 1, g_w, 1, CARD_BORDER)

        # Gantt bars
        bar_h = 18
        bar_y = ry + (row_h - bar_h) // 2
        for bi, (start_day, span, color, label) in enumerate(bars):
            bx = g_x + label_w + (start_day - 1) * day_w + 3
            bw = span * day_w - 6
            text_color = BRAND_PRIMARY if color == BRAND_ACCENT_SOFT or color == QA_GRAY else WHITE
            add_rect(slide, f"row-{ri+1}-bar-{bi+1}", bx, bar_y, bw, bar_h, color)
            add_text(
                slide, f"row-{ri+1}-bar-{bi+1}-label", label,
                x_px=bx, y_px=bar_y, w_px=bw, h_px=bar_h,
                font_size_px=9, color=text_color, bold=True, anchor="middle", align="center",
            )

    # TODAY vertical line at day 1 center
    today_x = g_x + label_w + day_w // 2
    add_rect(slide, "today-line", today_x, dh_y, 2, rows_h + dh_h, BRAND_ACCENT)

    # Bottom panels
    bp_y = 568
    bp_h = 86
    # Blockers panel
    bl_w = 400
    add_text(
        slide, "blockers-title", "BLOCKERS",
        x_px=56, y_px=bp_y, w_px=bl_w, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True,
        uppercase=True, letter_spacing_px=1.4,
    )
    blocker_top = bp_y + 18
    # Blocker 1
    add_rect(slide, "blocker-1-bar", 56, blocker_top, 3, 28, BLOCKER_BAR)
    add_rect(slide, "blocker-1-bg", 59, blocker_top, bl_w - 3, 28, BLOCKER_BG)
    add_text(
        slide, "blocker-1",
        "<strong>AUTH SERVICE:</strong> OAuth token refresh intermittent failure in staging — DevOps investigating.",
        x_px=66, y_px=blocker_top, w_px=bl_w - 16, h_px=28,
        font_size_px=10, color=TEXT_DARK, anchor="middle",
        emphasis_color=BLOCKER_RED,
    )
    # Blocker 2
    add_rect(slide, "blocker-2-bar", 56, blocker_top + 32, 3, 28, BLOCKER_BAR)
    add_rect(slide, "blocker-2-bg", 59, blocker_top + 32, bl_w - 3, 28, BLOCKER_BG)
    add_text(
        slide, "blocker-2",
        "<strong>MODULE 3 SPEC:</strong> Final acceptance criteria not signed off — Product Owner review requested by Wed 21.",
        x_px=66, y_px=blocker_top + 32, w_px=bl_w - 16, h_px=28,
        font_size_px=10, color=TEXT_DARK, anchor="middle",
        emphasis_color=BLOCKER_RED,
    )

    # Velocity stats panel
    vs_x = 56 + bl_w + 16
    vs_w = 1280 - 56 - vs_x
    vs = add_rect(slide, "stats-panel", vs_x, bp_y, vs_w, bp_h, CARD_BG)
    vs.line.color.rgb = CARD_BORDER
    vs.line.width = 9525
    add_text(
        slide, "stats-title", "SPRINT VELOCITY",
        x_px=vs_x + 16, y_px=bp_y + 10, w_px=vs_w - 32, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY_MID, bold=True,
        uppercase=True, letter_spacing_px=1.4,
    )
    add_text(
        slide, "stat-committed", "42",
        x_px=vs_x + 16, y_px=bp_y + 28, w_px=44, h_px=28,
        font_size_px=22, color=BRAND_PRIMARY, bold=True,
    )
    add_text(
        slide, "stat-committed-label", "pts committed",
        x_px=vs_x + 64, y_px=bp_y + 38, w_px=140, h_px=14,
        font_size_px=11, color=TEXT_MID,
    )
    # Separator
    add_rect(slide, "stat-sep", vs_x + 210, bp_y + 30, 1, 28, CARD_BORDER)
    add_text(
        slide, "stat-completed", "38",
        x_px=vs_x + 224, y_px=bp_y + 28, w_px=44, h_px=28,
        font_size_px=22, color=BRAND_PRIMARY, bold=True,
    )
    add_text(
        slide, "stat-completed-label", "pts completed last sprint",
        x_px=vs_x + 272, y_px=bp_y + 38, w_px=220, h_px=14,
        font_size_px=11, color=TEXT_MID,
    )
    add_text(
        slide, "velocity-row",
        "Velocity trend: <strong>↑ improving</strong> — team capacity stable across both weeks",
        x_px=vs_x + 16, y_px=bp_y + 64, w_px=vs_w - 32, h_px=18,
        font_size_px=11, color=TEXT_MID, emphasis_color=GREEN_OK,
    )

    add_footer(slide, page_num=283)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "283_sprint-plan-2week.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
