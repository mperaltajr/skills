"""
Builder for pattern 73: Workshop agenda with timings.

Title + right-pushed legend (Intro/Working/Break/Decision tag colors).
Header row → 7 agenda rows, each: time, tag-swatch, item title+desc, owner.
Decision rows get a soft accent wash + DECISION pill.
Bottom: total duration + convergence band.

Source HTML: _pattern-library/73_workshop-agenda-timings.html
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

TAG_INTRO = BRAND_PRIMARY_MID
TAG_WORKING = BRAND_PRIMARY
TAG_BREAK = TEXT_FAINT
TAG_DECISION = BRAND_ACCENT
ACCENT_WASH = RGBColor(0xF7, 0xEC, 0xFE)
BREAK_WASH = RGBColor(0xF4, 0xF6, 0xF9)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # --- Title block (canonical bottom-anchored) ---
    add_text(
        slide, "title",
        "Workshop agenda — <strong>three hours, three decisions</strong>.",
        x_px=56, y_px=20, w_px=1168, h_px=80,
        font_size_px=26, color=TEXT_DARK, bold=True,
        emphasis_color=BRAND_PRIMARY, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Pilot kickoff · run-of-show with owners and decision moments flagged.",
        x_px=56, y_px=104, w_px=820, h_px=22,
        font_size_px=13, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=56, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT)

    # Legend — BELOW subheadline (HARD RULE: top-y >= 230, right-aligned to x=1240)
    leg_w = 360
    leg_h = 28
    leg_x = 1240 - leg_w
    leg_y = 230
    leg_bg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, CARD_BG)
    leg_bg.line.color.rgb = CARD_BORDER
    leg_bg.line.width = 9525
    legend_items = [
        ("Intro", TAG_INTRO),
        ("Working", TAG_WORKING),
        ("Break", TAG_BREAK),
        ("Decision", TAG_DECISION),
    ]
    # Single-row horizontal layout — all swatches share one midline.
    item_step = (leg_w - 24) // len(legend_items)
    sw_size = 10
    sw_y = leg_y + (leg_h - sw_size) // 2
    for i, (lbl, color) in enumerate(legend_items):
        n = i + 1
        sx = leg_x + 12 + i * item_step
        add_rect(slide, f"legend-sw-{n}", sx, sw_y, sw_size, sw_size, color)
        add_text(
            slide, f"legend-lbl-{n}", lbl,
            x_px=sx + sw_size + 4, y_px=leg_y, w_px=item_step - sw_size - 8, h_px=leg_h,
            font_size_px=9, color=TEXT_MID, bold=True,
            letter_spacing_px=0.6, uppercase=True, anchor="middle",
        )

    # --- Column header (shifted down to clear legend at y=230+28=258) ---
    col_top = 268
    time_w = 112
    tag_w = 24
    owner_w = 160
    body_left = 56
    body_right = 1280 - 56
    body_w = body_right - body_left
    item_x = body_left + time_w + 18 + tag_w + 18
    item_w = body_w - time_w - 18 - tag_w - 18 - owner_w - 18

    headers = [
        ("Time", body_left, time_w, "left", BRAND_PRIMARY),
        ("Item", item_x, item_w, "left", TEXT_FAINT),
        ("Owner", body_right - owner_w, owner_w, "right", TEXT_FAINT),
    ]
    for i, (h, hx, hw, halign, hc) in enumerate(headers):
        n = i + 1
        add_text(
            slide, f"col-header-{n}", h,
            x_px=hx, y_px=col_top, w_px=hw, h_px=16,
            font_size_px=9, color=hc, bold=True,
            letter_spacing_px=2, uppercase=True, align=halign,
        )
    # Header bottom rule (brand-primary thick)
    add_rect(slide, "col-header-rule", body_left, col_top + 24, body_w, 2, BRAND_PRIMARY)

    # --- Agenda rows ---
    rows = [
        ("9:00 – 9:15",   "intro",    "Welcome + objectives",    "Why we're here, what we'll decide, ground rules.", "Mario", "Facilitator", False),
        ("9:15 – 9:45",   "intro",    "Why we're here — context","Walk through the pre-read; surface questions before demo.", "Sarah", "Pre-read review", False),
        ("9:45 – 10:30",  "working",  "Live demo",               "Think → Argue → Build, end-to-end on a real brief.", "Mario", "Driver", False),
        ("10:30 – 10:45", "break",    "Break",                   "", "—", "", False),
        ("10:45 – 11:15", "working",  "Q&A",                     "Open floor — concerns, edge cases, objections.", "All", "Group", False),
        ("11:15 – 11:45", "working",  "Pilot scoping working session", "Team, use cases, success metrics — draft on the wall.", "Maria", "Lead", False),
        ("11:45 – 12:00", "decision", "Decision: scope + go/no-go", "Lock the pilot scope, confirm sponsor, set kickoff date.", "MD", "Decision owner", True),
    ]
    tag_color_map = {"intro": TAG_INTRO, "working": TAG_WORKING, "break": TAG_BREAK, "decision": TAG_DECISION}
    row_top = col_top + 28
    row_h = 42

    for i, (time, kind, name, desc, owner, role, is_decision) in enumerate(rows):
        n = i + 1
        ry = row_top + i * row_h

        # Background wash
        if kind == "break":
            add_rect(slide, f"row-{n}-bg", body_left, ry, body_w, row_h, BREAK_WASH)
        elif is_decision:
            add_rect(slide, f"row-{n}-bg", body_left, ry, body_w, row_h, ACCENT_WASH)

        # Bottom rule
        add_rect(slide, f"row-{n}-rule", body_left, ry + row_h, body_w, 1, CARD_BORDER)

        # Time
        add_text(
            slide, f"row-{n}-time", time,
            x_px=body_left, y_px=ry, w_px=time_w, h_px=row_h,
            font_size_px=12, color=BRAND_PRIMARY, bold=True, anchor="middle",
            font_name="Consolas",
        )
        # Tag swatch
        tx = body_left + time_w + 18
        add_rect(slide, f"row-{n}-tag", tx, ry + (row_h - 10) // 2, 10, 10, tag_color_map[kind])
        # Item title + desc
        if kind == "break":
            add_text(
                slide, f"row-{n}-name", name,
                x_px=item_x, y_px=ry, w_px=item_w, h_px=row_h,
                font_size_px=11, color=TEXT_MID, bold=True,
                letter_spacing_px=1.5, uppercase=True, anchor="middle",
            )
        else:
            add_text(
                slide, f"row-{n}-name", name,
                x_px=item_x, y_px=ry + 4, w_px=item_w, h_px=18,
                font_size_px=12, color=BRAND_PRIMARY, bold=True,
            )
            # Decision pill
            if is_decision:
                pill_x = item_x + 270
                add_rect(slide, f"row-{n}-decision-pill", pill_x, ry + 6, 70, 14, ACCENT_WASH)
                add_text(
                    slide, f"row-{n}-decision-pill-text", "DECISION",
                    x_px=pill_x, y_px=ry + 6, w_px=70, h_px=14,
                    font_size_px=7, color=BRAND_ACCENT, bold=True,
                    align="center", anchor="middle", letter_spacing_px=1.5,
                )
            if desc:
                add_text(
                    slide, f"row-{n}-desc", desc,
                    x_px=item_x, y_px=ry + 22, w_px=item_w, h_px=18,
                    font_size_px=10, color=TEXT_MID, italic=True,
                )
        # Owner
        ox = body_right - owner_w
        add_text(
            slide, f"row-{n}-owner", owner,
            x_px=ox, y_px=ry + 4, w_px=owner_w, h_px=18,
            font_size_px=11, color=TEXT_DARK, bold=True, align="right",
        )
        if role:
            add_text(
                slide, f"row-{n}-role", role,
                x_px=ox, y_px=ry + 22, w_px=owner_w, h_px=14,
                font_size_px=8, color=TEXT_FAINT, align="right",
                letter_spacing_px=1, uppercase=True,
            )

    # --- Bottom band: total duration ---
    band_y = row_top + len(rows) * row_h + 6
    add_rect(slide, "band-rule", body_left, band_y, body_w, 1, CARD_BORDER)
    add_text(
        slide, "total-label", "Total duration",
        x_px=body_left, y_px=band_y + 6, w_px=body_w - 80, h_px=18,
        font_size_px=10, color=TEXT_FAINT, bold=True,
        letter_spacing_px=1.5, uppercase=True, align="right",
    )
    add_text(
        slide, "total-value", "3h 00m",
        x_px=body_right - 70, y_px=band_y + 6, w_px=70, h_px=18,
        font_size_px=12, color=BRAND_PRIMARY, bold=True, align="right",
    )

    # --- Convergence band ---
    conv_y = band_y + 32
    add_rect(slide, "convergence-bg", body_left, conv_y, body_w, 30, CARD_BG)
    add_rect(slide, "convergence-accent", body_left, conv_y, 3, 30, BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "<strong>Three decision moments — flagged.</strong> Everything else is groundwork.",
        x_px=body_left + 14, y_px=conv_y, w_px=body_w - 24, h_px=30,
        font_size_px=12, color=BRAND_PRIMARY, anchor="middle",
        emphasis_color=BRAND_PRIMARY,
    )

    add_footer(slide, page_num=73)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "73_workshop-agenda-timings.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
