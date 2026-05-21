"""
Builder for pattern 93: Communication plan matrix.

Title + right-pushed audience-type legend (EX/MG/IC badges).
5-column table: Audience (with colored badge) | Message | Channel | Frequency | Owner.
7 rows of stakeholder cadences. Convergence band below.

Source HTML: _pattern-library/93_communication-plan-matrix.html
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

LEG_BG = RGBColor(0xFB, 0xFA, 0xFD)
BADGE_EX_BG = BRAND_PRIMARY
BADGE_EX_FG = WHITE
BADGE_MG_BG = BRAND_ACCENT
BADGE_MG_FG = WHITE
BADGE_IC_BG = CARD_BG
BADGE_IC_FG = BRAND_PRIMARY


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # --- Title block ---
    add_text(
        slide, "eyebrow", "Stakeholder communication",
        x_px=48, y_px=50, w_px=900, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=2, uppercase=True,
    )
    add_text(
        slide, "title",
        "Communication plan — seven audiences, seven cadences.",
        x_px=48, y_px=70, w_px=900, h_px=40,
        font_size_px=24, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Each audience gets the message that matters to them, on a channel they actually read, at a rhythm that fits their decision cycle. One owner per row, no shared accountability.",
        x_px=48, y_px=114, w_px=900, h_px=44,
        font_size_px=12, color=TEXT_MID,
    )
    add_rect(slide, "brand-rule", x_px=48, y_px=164, w_px=56, h_px=3, fill_color=BRAND_ACCENT)

    # --- Audience-type legend — BELOW subheadline (HARD RULE: top-y >= 230, right-aligned to x ~1240)
    # Compact horizontal layout (title + 3 badges in a row) to fit the band above the table.
    leg_w = 420
    leg_h = 40
    leg_x = 1240 - leg_w  # right edge at 1240 (HARD RULE)
    leg_y = 230
    leg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, LEG_BG)
    leg.line.color.rgb = CARD_BORDER
    leg.line.width = 9525
    add_text(
        slide, "legend-title", "Audience type",
        x_px=leg_x + 12, y_px=leg_y, w_px=84, h_px=leg_h,
        font_size_px=8, color=TEXT_MID, bold=True,
        letter_spacing_px=1.2, uppercase=True, anchor="middle",
    )
    badges = [
        ("EX", "Executive", BADGE_EX_BG, BADGE_EX_FG, False),
        ("MG", "Manager", BADGE_MG_BG, BADGE_MG_FG, False),
        ("IC", "Individual", BADGE_IC_BG, BADGE_IC_FG, True),
    ]
    badge_h = 18
    badge_y = leg_y + (leg_h - badge_h) // 2  # vertical center
    bx = leg_x + 104
    for i, (code, desc, bg, fg, has_border) in enumerate(badges):
        n = i + 1
        # Mini badge
        badge = add_rect(slide, f"legend-badge-{n}", bx, badge_y, 22, badge_h, bg)
        if has_border:
            badge.line.color.rgb = CARD_BORDER
            badge.line.width = 6350
        add_text(
            slide, f"legend-badge-{n}-code", code,
            x_px=bx, y_px=badge_y, w_px=22, h_px=badge_h,
            font_size_px=8, color=fg, bold=True, align="center", anchor="middle",
        )
        add_text(
            slide, f"legend-badge-{n}-desc", desc,
            x_px=bx + 26, y_px=badge_y, w_px=80, h_px=badge_h,
            font_size_px=10, color=TEXT_MID, anchor="middle",
        )
        bx += 108

    # --- Table --- (shifted to clear legend at y=230..274)
    table_top = 286
    table_left = 48
    table_w = 1280 - 96
    col_pct = [0.22, 0.26, 0.18, 0.17, 0.17]
    col_widths = [int(table_w * p) for p in col_pct]
    col_x = [table_left]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)

    # Header
    header_h = 36
    add_rect(slide, "table-header-bg", table_left, table_top, table_w, header_h, BRAND_PRIMARY)
    headers = ["Audience", "Message", "Channel", "Frequency", "Owner"]
    for i, h in enumerate(headers):
        n = i + 1
        add_text(
            slide, f"col-header-{n}", h,
            x_px=col_x[i] + 14, y_px=table_top, w_px=col_widths[i] - 28, h_px=header_h,
            font_size_px=9, color=WHITE, bold=True, anchor="middle",
            letter_spacing_px=1.4, uppercase=True, align="left",
        )

    rows = [
        ("EX", "Program MD",         "Pilot progress & risk escalations",          "1:1 sync",       "Weekly",      "Mario"),
        ("EX", "Practice MDs",       "Q3 rollout decision & investment ask",       "Monthly forum",  "Monthly",     "Maria"),
        ("IC", "Pilot users",        "Tactical updates & quick wins",              "Slack channel",  "Daily",       "Coach"),
        ("IC", "Pilot users",        "Recap & what to try next",                   "Email digest",   "Weekly",      "Coach"),
        ("MG", "Skeptical seniors",  "1:1 coaching — addressing objections",       "In-person",      "Ad-hoc",      "Coach"),
        ("IC", "All consultants",    "Pilot announcement & Wave 2 preview",        "All-hands",      "Pre-Wave 2",  "MD"),
        ("MG", "Wave 2 candidates",  "Onboarding & method walkthrough",            "Workshops",      "Pre-launch",  "PMO"),
    ]
    badge_map = {
        "EX": (BADGE_EX_BG, BADGE_EX_FG, False),
        "MG": (BADGE_MG_BG, BADGE_MG_FG, False),
        "IC": (BADGE_IC_BG, BADGE_IC_FG, True),
    }
    # Row height tightened to give breathing room above the convergence band.
    row_h = 38
    body_top = table_top + header_h
    for ri, (code, aud_name, msg, channel, freq, owner) in enumerate(rows):
        n = ri + 1
        ry = body_top + ri * row_h

        # Audience cell bg
        add_rect(slide, f"row-{n}-aud-bg", col_x[0], ry, col_widths[0], row_h, CARD_BG)
        # 2px right border on audience cell
        add_rect(slide, f"row-{n}-aud-rule", col_x[0] + col_widths[0] - 2, ry, 2, row_h, CARD_BORDER)
        # Badge
        bg, fg, has_border = badge_map[code]
        badge = add_rect(slide, f"row-{n}-badge", col_x[0] + 12, ry + (row_h - 22) // 2, 26, 22, bg)
        if has_border:
            badge.line.color.rgb = CARD_BORDER
            badge.line.width = 6350
        add_text(
            slide, f"row-{n}-badge-code", code,
            x_px=col_x[0] + 12, y_px=ry + (row_h - 22) // 2, w_px=26, h_px=22,
            font_size_px=9, color=fg, bold=True, align="center", anchor="middle",
        )
        # Audience name
        add_text(
            slide, f"row-{n}-aud-name", aud_name,
            x_px=col_x[0] + 48, y_px=ry, w_px=col_widths[0] - 60, h_px=row_h,
            font_size_px=12, color=BRAND_PRIMARY, bold=True, anchor="middle",
        )
        # Top rule
        add_rect(slide, f"row-{n}-rule", table_left, ry, table_w, 1, CARD_BORDER)
        # Other cells
        for ci, (val, color, italic, weight, lspacing) in enumerate([
            (msg,     TEXT_DARK, False, False, 0),
            (channel, TEXT_DARK, False, True,  0),
            (freq,    TEXT_MID,  False, True,  0.2),
            (owner,   BRAND_PRIMARY_MID, False, True, 0),
        ]):
            cn = ci + 2
            cell_align = "left"
            uppercase = (ci == 2)
            add_text(
                slide, f"row-{n}-cell-{cn}", val,
                x_px=col_x[cn - 1] + 14, y_px=ry, w_px=col_widths[cn - 1] - 28, h_px=row_h,
                font_size_px=11, color=color, bold=weight, anchor="middle",
                letter_spacing_px=lspacing, uppercase=uppercase, align=cell_align,
            )
        # Vertical rules between cells (light)
        for ci in range(1, 5):
            add_rect(slide, f"row-{n}-vrule-{ci}", col_x[ci] - 1, ry, 1, row_h, CARD_BORDER)

    # Table outer border
    bottom_rule_y = body_top + len(rows) * row_h
    add_rect(slide, "table-bottom-rule", table_left, bottom_rule_y, table_w, 1, CARD_BORDER)

    # --- Convergence band (with so-what tag pill) ---
    conv_y = 624
    conv_h = 40
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, conv_h, BRAND_PRIMARY)
    # Tag pill
    add_rect(slide, "convergence-tag-bg", 60, conv_y + 10, 62, 20, BRAND_PRIMARY)
    add_text(
        slide, "convergence-tag", "So what",
        x_px=60, y_px=conv_y + 10, w_px=62, h_px=20,
        font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center", anchor="middle",
        letter_spacing_px=1.6, uppercase=True,
    )
    add_text(
        slide, "convergence",
        "Generic “all-hands updates” fail because <strong>no audience hears their message</strong>. Segment by decision rhythm — daily for doers, monthly for deciders — or the change stalls in the middle.",
        x_px=132, y_px=conv_y, w_px=1280 - 96 - 96, h_px=conv_h,
        font_size_px=12, color=WHITE, anchor="middle",
        emphasis_color=BRAND_ACCENT_SOFT,
    )

    add_footer(slide, page_num=93)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "93_communication-plan-matrix.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
