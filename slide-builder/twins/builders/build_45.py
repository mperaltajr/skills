"""
Builder for pattern 45: Swimlane with chevron handoff.

Two horizontal lanes (storyline-helper at top, slide-builder at bottom),
each with a vertical lane label and 5 (or 4) chevron-step blocks. A handoff
pill sits between them.

Pattern-local IDs: lane-N-label, lane-N-eyebrow,
lane-N-step-M-num/name/body, handoff-pill.

Source HTML: _pattern-library/45_swimlane-chevron-handoff.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

LANE1_TINT = RGBColor(0xF6, 0xEC, 0xFF)
LANE2_TINT = RGBColor(0xF1, 0xE8, 0xFB)
LANE1_STEP_TINT = RGBColor(0xEC, 0xDC, 0xFF)
LANE2_STEP_TINT = RGBColor(0xE4, 0xD2, 0xF4)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title block (subtitle is uppercase brand-mid in this pattern, not italic)
    add_text(
        slide, "title",
        "Two skills, one workflow — the thinking is locked before a single slide is designed.",
        x_px=56, y_px=64, w_px=1100, h_px=68,
        font_size_px=26, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "HOW STORYLINE-HELPER AND SLIDE-BUILDER WORK IN SEQUENCE",
        x_px=56, y_px=132, w_px=900, h_px=18,
        font_size_px=12, color=BRAND_PRIMARY_MID, bold=True,
        letter_spacing_px=1.2, uppercase=True,
    )
    add_rect(slide, "brand-rule", x_px=56, y_px=158, w_px=56, h_px=3, fill_color=BRAND_ACCENT)

    # Content area: top=180, bottom=56, left=56, right=56 (1168 × 484)
    c_top = 180
    c_left = 56
    c_w = 1168
    c_h = 484

    # 3 zones vertically: lane 1 (top), handoff (middle, 32h), lane 2 (bottom)
    handoff_h = 32
    lane_h = (c_h - handoff_h) // 2

    # ---- Lane 1 ----
    lane1_top = c_top
    # Lane label band (96px wide, brand-accent)
    add_rect(slide, "lane-1-label-bg", c_left, lane1_top, 96, lane_h, BRAND_ACCENT)
    add_text(
        slide, "lane-1-label", "STORYLINE-HELPER",
        x_px=c_left, y_px=lane1_top + (lane_h - 220) // 2, w_px=96, h_px=220,
        font_size_px=12, color=WHITE, bold=True, align="center", anchor="middle",
        letter_spacing_px=2,
    )
    # Lane body
    lane1_body_x = c_left + 96
    lane1_body_w = c_w - 96
    lane1_body = add_rect(slide, "lane-1-body-bg", lane1_body_x, lane1_top, lane1_body_w, lane_h, LANE1_TINT)
    lane1_body.line.color.rgb = BRAND_ACCENT
    lane1_body.line.width = 19050

    add_text(
        slide, "lane-1-eyebrow", "Structures the thinking",
        x_px=lane1_body_x + 18, y_px=lane1_top + 12, w_px=lane1_body_w - 36, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=0.8, uppercase=True,
    )

    # 5 steps in lane 1
    steps_top = lane1_top + 36
    steps_h = lane_h - 48
    step_w = (lane1_body_w - 30 - 16) // 5  # 5 steps, ~4 gaps
    lane1_steps = [
        ("1", "Template intake", "Reads fonts, colors & layouts from your .pptx automatically"),
        ("2", "Opening question", "What are you trying to communicate? — starts the structured conversation"),
        ("3", "Audience + context", "Who sees this, what they already know, what they need to believe"),
        ("4", "Infer & confirm", "Page type, mode and governing thought reflected back — confirmed before deeper"),
        ("5", "Sharpen structure → Brief", "2-4 supporting buckets, evidence, risks — structured brief produced"),
    ]
    for i, (num, name, body) in enumerate(lane1_steps):
        n = i + 1
        sx = lane1_body_x + 14 + i * (step_w + 4)
        # Step head (brand-accent chevron approximation = rectangle)
        head_h = 44
        add_rect(slide, f"lane-1-step-{n}-head", sx, steps_top, step_w, head_h, BRAND_ACCENT)
        add_text(
            slide, f"lane-1-step-{n}-num", num,
            x_px=sx + 8, y_px=steps_top + 4, w_px=18, h_px=18,
            font_size_px=10, color=BRAND_ACCENT, bold=True, align="center", anchor="middle",
            bg_fill=WHITE,
        )
        add_text(
            slide, f"lane-1-step-{n}-name", name,
            x_px=sx + 8, y_px=steps_top + 22, w_px=step_w - 16, h_px=20,
            font_size_px=10, color=WHITE, bold=True,
        )
        # Step body
        body_y = steps_top + head_h
        body_h = steps_h - head_h
        add_rect(slide, f"lane-1-step-{n}-body-bg", sx, body_y, step_w, body_h, LANE1_STEP_TINT)
        add_text(
            slide, f"lane-1-step-{n}-body", body,
            x_px=sx + 10, y_px=body_y + 8, w_px=step_w - 20, h_px=body_h - 16,
            font_size_px=10, color=TEXT_DARK,
        )

    # ---- Handoff bar ----
    handoff_top = lane1_top + lane_h
    add_rect(slide, "handoff-bg", c_left, handoff_top, c_w, handoff_h, WHITE)
    # Handoff pill (centered)
    pill_w = 760
    pill_h = 22
    pill_x = c_left + (c_w - pill_w) // 2
    pill_y = handoff_top + (handoff_h - pill_h) // 2
    add_rect(slide, "handoff-pill", pill_x, pill_y, pill_w, pill_h, BRAND_PRIMARY)
    add_text(
        slide, "handoff-pill-text",
        "▼  STRUCTURED BRIEF HANDOFF — GOVERNING THOUGHT · AUDIENCE · STRUCTURE · EVIDENCE · RISKS CONFIRMED  ▼",
        x_px=pill_x, y_px=pill_y, w_px=pill_w, h_px=pill_h,
        font_size_px=9, color=WHITE, bold=True, align="center", anchor="middle",
        letter_spacing_px=1,
    )

    # ---- Lane 2 ----
    lane2_top = handoff_top + handoff_h
    add_rect(slide, "lane-2-label-bg", c_left, lane2_top, 96, lane_h, BRAND_PRIMARY_MID)
    add_text(
        slide, "lane-2-label", "SLIDE-BUILDER",
        x_px=c_left, y_px=lane2_top + (lane_h - 220) // 2, w_px=96, h_px=220,
        font_size_px=12, color=WHITE, bold=True, align="center", anchor="middle",
        letter_spacing_px=2,
    )
    lane2_body_x = c_left + 96
    lane2_body = add_rect(slide, "lane-2-body-bg", lane2_body_x, lane2_top, c_w - 96, lane_h, LANE2_TINT)
    lane2_body.line.color.rgb = BRAND_PRIMARY_MID
    lane2_body.line.width = 19050
    add_text(
        slide, "lane-2-eyebrow", "Designs and builds the slide",
        x_px=lane2_body_x + 18, y_px=lane2_top + 12, w_px=c_w - 132, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY_MID, bold=True,
        letter_spacing_px=0.8, uppercase=True,
    )

    # 4 steps in lane 2 — placed on the SAME column grid as lane 1 (step_w + 4),
    # using columns 0, 1, 2, 4. This leaves column 3 empty so step #9
    # (Build + QA) sits directly under step #5 in lane 1 (the rightmost
    # chevron), which is the alignment the prior version got wrong.
    steps2_top = lane2_top + 36
    step2_w = step_w  # match lane 1's step width
    lane2_steps = [
        ("6", "Read brief + rules", "Applies MBB slide rules and page-type conventions to the brief", 0),
        ("7", "Generate mockups", "3-4 structurally distinct HTML/SVG variations — each a different layout bet", 1),
        ("8", "Select + refine", "React, combine options or request changes — nothing locked until approved", 2),
        ("9", "Build + QA → .pptx ✓", "Built on client template, QA'd as PDF, delivered as clickable file link", 4),
    ]
    for i, (num, name, body, col) in enumerate(lane2_steps):
        n = i + 1
        sx = lane2_body_x + 14 + col * (step2_w + 4)
        is_final = (n == 4)
        head_fill = BRAND_PRIMARY if is_final else BRAND_PRIMARY_MID
        body_fill = RGBColor(0xE0, 0xD0, 0xF0) if is_final else LANE2_STEP_TINT
        head_h = 44
        add_rect(slide, f"lane-2-step-{n}-head", sx, steps2_top, step2_w, head_h, head_fill)
        add_text(
            slide, f"lane-2-step-{n}-num", num,
            x_px=sx + 8, y_px=steps2_top + 4, w_px=18, h_px=18,
            font_size_px=10, color=head_fill, bold=True, align="center", anchor="middle",
            bg_fill=WHITE,
        )
        add_text(
            slide, f"lane-2-step-{n}-name", name,
            x_px=sx + 8, y_px=steps2_top + 22, w_px=step2_w - 16, h_px=20,
            font_size_px=10, color=WHITE, bold=True,
        )
        body_y = steps2_top + head_h
        body_h = lane_h - 36 - head_h
        add_rect(slide, f"lane-2-step-{n}-body-bg", sx, body_y, step2_w, body_h, body_fill)
        add_text(
            slide, f"lane-2-step-{n}-body", body,
            x_px=sx + 10, y_px=body_y + 8, w_px=step2_w - 20, h_px=body_h - 16,
            font_size_px=10, color=TEXT_DARK,
        )

    add_footer(slide, page_num=45)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "45_swimlane-chevron-handoff.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
