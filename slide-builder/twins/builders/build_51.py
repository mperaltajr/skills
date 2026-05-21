"""
Builder for pattern 51: Phased plan timeline-table.

NOTE: Pattern 51 uses a non-standard top title-band (full-width 64px brand
band) instead of the universal chrome. The title sits inside the dark band.
We render that variant rather than calling add_chrome / add_title_block.

Manual table placement (5 cols x 3 rows). Phase stripe color per row.

Source HTML: _pattern-library/51_phased-plan-timeline-table.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

PHASE_1 = RGBColor(0x2D, 0x0A, 0x4E)
PHASE_2 = RGBColor(0x5C, 0x2D, 0x87)
PHASE_3 = RGBColor(0xA1, 0x00, 0xFF)
ZEBRA_BG = RGBColor(0xF6, 0xF2, 0xFB)


def build():
    prs, slide = new_slide()

    # ---- Top title-band variant (replaces standard chrome) ----
    # Brand-primary band 1280 x 64
    add_rect(slide, "title-band", 0, 0, 1280, 64, BRAND_PRIMARY)
    # Accent rule under band (3px)
    add_rect(slide, "brand-rule", 0, 64, 1280, 3, BRAND_ACCENT)

    # Title text inside band
    add_text(
        slide, "title",
        "90-day plan — three phases, one runway from foundation to scale.",
        x_px=40, y_px=28, w_px=1200, h_px=32,
        font_size_px=22, color=WHITE,
    )

    # ---- Timeline header ----
    tl_left = 88
    tl_right = 1280 - 88
    tl_w = tl_right - tl_left
    tl_y = 96

    # Timeline bar (3 segments)
    add_rect(slide, "timeline-axis", tl_left, tl_y + 18, tl_w // 3, 5, PHASE_1)
    add_rect(slide, "timeline-seg-2", tl_left + tl_w // 3, tl_y + 18, tl_w // 3, 5, PHASE_2)
    add_rect(slide, "timeline-seg-3", tl_left + 2 * tl_w // 3, tl_y + 18, tl_w - 2 * (tl_w // 3), 5, PHASE_3)

    # Tick labels (under bar)
    seg_w = tl_w / 3
    add_text(
        slide, "timeline-tick-1-label", "Days 1–30  ·  “Roll down the runway”",
        x_px=tl_left, y_px=tl_y + 36, w_px=int(seg_w), h_px=14,
        font_size_px=10, color=PHASE_1, bold=True,
    )
    add_text(
        slide, "timeline-tick-2-label", "Days 31–60  ·  “Liftoff”",
        x_px=tl_left + int(seg_w), y_px=tl_y + 36, w_px=int(seg_w), h_px=14,
        font_size_px=10, color=PHASE_2, bold=True, align="center",
    )
    add_text(
        slide, "timeline-tick-3-label", "Days 61–90  ·  “Initial climb”",
        x_px=tl_left + int(2 * seg_w), y_px=tl_y + 36, w_px=int(seg_w), h_px=14,
        font_size_px=10, color=PHASE_3, bold=True, align="right",
    )

    # ---- Table ----
    t_left = 40
    t_right = 1280 - 40
    t_top = 174
    t_bottom = 720 - 96  # 624
    t_w = t_right - t_left
    t_h = t_bottom - t_top  # 450

    # Outer border
    outer = add_rect(slide, "table-frame", t_left, t_top, t_w, t_h, WHITE)
    outer.line.color.rgb = CARD_BORDER
    outer.line.width = 9525

    # Header row (36px)
    head_h = 36
    add_rect(slide, "table-head-bg", t_left, t_top, t_w, head_h, BRAND_PRIMARY)

    col_phase_w = 180
    col_obj_w = 200
    col_output_w = 220
    col_actions_w = t_w - col_phase_w - col_obj_w - col_output_w

    cx = t_left
    add_text(
        slide, "table-col-1-header", "PHASE",
        x_px=cx + 14, y_px=t_top, w_px=col_phase_w - 14, h_px=head_h,
        font_size_px=10, color=WHITE, bold=True, anchor="middle", uppercase=True,
    )
    cx += col_phase_w
    add_text(
        slide, "table-col-2-header", "OBJECTIVE",
        x_px=cx + 14, y_px=t_top, w_px=col_obj_w - 14, h_px=head_h,
        font_size_px=10, color=WHITE, bold=True, anchor="middle", uppercase=True,
    )
    cx += col_obj_w
    add_text(
        slide, "table-col-3-header", "KEY ACTIONS",
        x_px=cx + 14, y_px=t_top, w_px=col_actions_w - 14, h_px=head_h,
        font_size_px=10, color=WHITE, bold=True, anchor="middle", uppercase=True,
    )
    cx += col_actions_w
    add_text(
        slide, "table-col-4-header", "OUTPUT · PROOF OF PROGRESS",
        x_px=cx + 14, y_px=t_top, w_px=col_output_w - 14, h_px=head_h,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, anchor="middle", uppercase=True,
    )

    # Rows
    row_h = (t_h - head_h) // 3
    rows = [
        (PHASE_1, "Days 1–30", "“Access & foundation”",
         "Establish trusted access at senior levels and align on business priorities.",
         ["Align on priority domains; conduct executive listening sessions.",
          "Focus discussions on outcome gaps, value leakage, and partner blind spots.",
          "Establish a monthly executive touch-point cadence."],
         ["Shared view of executive priorities & pain points",
          "1–2 senior sponsors aligned to approach"], False),
        (PHASE_2, "Days 31–60", "“Credibility & proof”",
         "Demonstrate value and shift perception from delivery vendor to trusted advisor.",
         ["Deliver targeted, domain-specific insights via lightweight POVs.",
          "Facilitate decision-focused working sessions with leaders.",
          "Embed insights directly into active programs and live discussions."],
         ["Leaders begin pulling us into discussions",
          "Evidence of improved decisions and value clarity"], True),
        (PHASE_3, "Days 61–90", "“Scale & positioning”",
         "Institutionalize the role in the operating rhythm and decision-making cycle.",
         ["Launch quarterly operational value reviews — jointly owned with the client.",
          "Position as connector across operations, transformation, and value.",
          "Embed capability into account governance and investment cycles."],
         ["Consistently present in decision-making forums",
          "Role embedded in operating model — expected, not optional"], False),
    ]

    for ri, (stripe_color, days, name, obj, actions, outputs, zebra) in enumerate(rows):
        n = ri + 1
        ry = t_top + head_h + ri * row_h

        # Row background (zebra)
        if zebra:
            add_rect(slide, f"row-{n}-bg", t_left, ry, t_w, row_h, ZEBRA_BG)

        # Row divider (top border)
        if ri > 0:
            add_rect(slide, f"row-{n}-rule", t_left, ry, t_w, 1, CARD_BORDER)

        # Stripe (5px wide on left)
        add_rect(slide, f"phase-{n}-stripe", t_left, ry, 5, row_h, stripe_color)

        cx = t_left + 5
        # Phase cell
        add_text(
            slide, f"phase-{n}-days", days,
            x_px=cx + 14, y_px=ry + 14, w_px=col_phase_w - 19, h_px=18,
            font_size_px=12, color=TEXT_DARK, bold=True,
        )
        add_text(
            slide, f"phase-{n}-name", name,
            x_px=cx + 14, y_px=ry + 36, w_px=col_phase_w - 19, h_px=22,
            font_size_px=11, color=stripe_color, bold=True, italic=True,
        )
        cx = t_left + col_phase_w
        # Objective cell
        add_text(
            slide, f"phase-{n}-objective", obj,
            x_px=cx + 14, y_px=ry + 14, w_px=col_obj_w - 28, h_px=row_h - 28,
            font_size_px=11, color=TEXT_MID,
        )
        cx += col_obj_w
        # Actions cell — 3 bullets stacked
        for ai, a in enumerate(actions):
            an = ai + 1
            ay = ry + 14 + ai * 36
            add_text(
                slide, f"phase-{n}-action-{an}", "• " + a,
                x_px=cx + 14, y_px=ay, w_px=col_actions_w - 28, h_px=32,
                font_size_px=11, color=TEXT_DARK,
            )
        cx += col_actions_w
        # Output cell — 2 bullets
        for oi, o in enumerate(outputs):
            on = oi + 1
            oy = ry + 14 + oi * 52
            add_text(
                slide, f"phase-{n}-output-{on}", "• " + o,
                x_px=cx + 14, y_px=oy, w_px=col_output_w - 28, h_px=48,
                font_size_px=11, color=TEXT_DARK, bold=True,
            )

    # Footer (standard)
    add_text(slide, "page-number", "51",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "51_phased-plan-timeline-table.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
