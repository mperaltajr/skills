"""
Builder for pattern 51d: Phased plan timeline-table (dark variant).

Source HTML: _pattern-library/51_phased-plan-timeline-table-dark.html
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

# Dark color tokens
TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

PHASE_1 = BRAND_ACCENT_SOFT
PHASE_2 = RGBColor(0xB0, 0x60, 0xE0)
PHASE_3 = BRAND_ACCENT
ZEBRA_BG = RGBColor(0x36, 0x18, 0x55)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # --- Top title band variant (kept from light) ---
    add_rect(slide, "title-band", 0, 0, 1280, 64, RGBColor(0x1A, 0x05, 0x30))
    add_rect(slide, "brand-rule", 0, 64, 1280, 3, BRAND_ACCENT_SOFT)

    add_text(
        slide, "title",
        "90-day plan — three phases, one runway from foundation to scale.",
        x_px=40, y_px=28, w_px=1200, h_px=32,
        font_size_px=22, color=WHITE,
    )

    # Timeline header
    tl_left = 88
    tl_right = 1280 - 88
    tl_w = tl_right - tl_left
    tl_y = 96

    add_rect(slide, "timeline-axis", tl_left, tl_y + 18, tl_w // 3, 5, PHASE_1)
    add_rect(slide, "timeline-seg-2", tl_left + tl_w // 3, tl_y + 18, tl_w // 3, 5, PHASE_2)
    add_rect(slide, "timeline-seg-3", tl_left + 2 * tl_w // 3, tl_y + 18, tl_w - 2 * (tl_w // 3), 5, PHASE_3)

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

    # Table
    t_left = 40
    t_right = 1280 - 40
    t_top = 174
    t_bottom = 720 - 96
    t_w = t_right - t_left
    t_h = t_bottom - t_top

    outer = add_rect(slide, "table-frame", t_left, t_top, t_w, t_h, CARD_BG_DARK)
    outer.line.color.rgb = CARD_BORDER_DARK
    outer.line.width = 9525

    head_h = 36
    add_rect(slide, "table-head-bg", t_left, t_top, t_w, head_h, RGBColor(0x1A, 0x05, 0x30))

    col_phase_w = 180
    col_obj_w = 200
    col_output_w = 220
    col_actions_w = t_w - col_phase_w - col_obj_w - col_output_w

    cx = t_left
    for i, (hdr, color) in enumerate([
        ("PHASE", WHITE), ("OBJECTIVE", WHITE), ("KEY ACTIONS", WHITE),
        ("OUTPUT · PROOF OF PROGRESS", BRAND_ACCENT_SOFT),
    ]):
        w = [col_phase_w, col_obj_w, col_actions_w, col_output_w][i]
        add_text(
            slide, f"table-col-{i+1}-header", hdr,
            x_px=cx + 14, y_px=t_top, w_px=w - 14, h_px=head_h,
            font_size_px=10, color=color, bold=True, anchor="middle", uppercase=True,
        )
        cx += w

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

        if zebra:
            add_rect(slide, f"row-{n}-bg", t_left, ry, t_w, row_h, ZEBRA_BG)

        if ri > 0:
            add_rect(slide, f"row-{n}-rule", t_left, ry, t_w, 1, CARD_BORDER_DARK)

        add_rect(slide, f"phase-{n}-stripe", t_left, ry, 5, row_h, stripe_color)

        cx = t_left + 5
        add_text(
            slide, f"phase-{n}-days", days,
            x_px=cx + 14, y_px=ry + 14, w_px=col_phase_w - 19, h_px=18,
            font_size_px=12, color=WHITE, bold=True,
        )
        add_text(
            slide, f"phase-{n}-name", name,
            x_px=cx + 14, y_px=ry + 36, w_px=col_phase_w - 19, h_px=22,
            font_size_px=11, color=stripe_color, bold=True, italic=True,
        )
        cx = t_left + col_phase_w
        add_text(
            slide, f"phase-{n}-objective", obj,
            x_px=cx + 14, y_px=ry + 14, w_px=col_obj_w - 28, h_px=row_h - 28,
            font_size_px=11, color=TEXT_ON_DARK_MID,
        )
        cx += col_obj_w
        for ai, a in enumerate(actions):
            an = ai + 1
            ay = ry + 14 + ai * 36
            add_text(
                slide, f"phase-{n}-action-{an}", "• " + a,
                x_px=cx + 14, y_px=ay, w_px=col_actions_w - 28, h_px=32,
                font_size_px=11, color=WHITE,
            )
        cx += col_actions_w
        for oi, o in enumerate(outputs):
            on = oi + 1
            oy = ry + 14 + oi * 52
            add_text(
                slide, f"phase-{n}-output-{on}", "• " + o,
                x_px=cx + 14, y_px=oy, w_px=col_output_w - 28, h_px=48,
                font_size_px=11, color=WHITE, bold=True,
            )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "51",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "51d_phased-plan-timeline-table.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
