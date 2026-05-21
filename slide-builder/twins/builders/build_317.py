"""
Builder for pattern 317: 3-bucket numbered steps with arrow connectors.

Three numbered step boxes in a row, with arrow connectors between, and an outcome
strip at the bottom.

Source HTML: _pattern-library/317_3bucket-numbered-steps.html
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
from pptx.enum.shapes import MSO_SHAPE
from twins.helpers import px_to_emu


def _circle(slide, name, x, y, size, fill, text=None, text_color=WHITE, font_size=14):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, px_to_emu(x), px_to_emu(y),
        px_to_emu(size), px_to_emu(size),
    )
    shape.name = f"{name}-bg"
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    if text is not None:
        add_text(
            slide, f"{name}-text", text,
            x_px=x, y_px=y, w_px=size, h_px=size,
            font_size_px=font_size, color=text_color, bold=True,
            align="center", anchor="middle",
        )


def _step_box(slide, n, x, y, w, h, *, num, name, desc, outcome):
    box = add_rect(slide, f"step-{n}-box", x, y, w, h, CARD_BG)
    box.line.color.rgb = CARD_BORDER
    box.line.width = 9525
    # Top accent
    add_rect(slide, f"step-{n}-accent", x, y, w, 4, BRAND_ACCENT)
    # Number circle
    csize = 44
    cx = x + (w - csize) // 2
    cy = y + 28
    _circle(slide, f"step-{n}-circle", cx, cy, csize, BRAND_PRIMARY, text=num,
            text_color=WHITE, font_size=18)
    # Name
    add_text(
        slide, f"step-{n}-name", name,
        x_px=x + 16, y_px=cy + csize + 16, w_px=w - 32, h_px=24,
        font_size_px=15, color=BRAND_PRIMARY, bold=True, align="center",
    )
    # Description
    add_text(
        slide, f"step-{n}-desc", desc,
        x_px=x + 22, y_px=cy + csize + 50, w_px=w - 44, h_px=180,
        font_size_px=11, color=TEXT_MID,
    )
    # Outcome pill
    pill_w = 160
    pill_h = 22
    pill_x = x + (w - pill_w) // 2
    pill_y = y + h - pill_h - 18
    pill = add_rect(slide, f"step-{n}-pill", pill_x, pill_y, pill_w, pill_h, BRAND_ACCENT_SOFT)
    pill.line.fill.background()
    add_text(
        slide, f"step-{n}-pill-text", outcome.upper(),
        x_px=pill_x, y_px=pill_y, w_px=pill_w, h_px=pill_h,
        font_size_px=9, color=BRAND_PRIMARY, bold=True, align="center", anchor="middle",
        letter_spacing_px=1.4,
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Three steps to <strong>deliver with confidence</strong>",
        subtitle="A sequential process framework — from alignment to execution to impact",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 60 - body_top  # leave room for outcome strip
    arrow_w = 30
    card_w = (body_w - 2 * arrow_w) // 3

    steps = [
        ("1", "Align & Define",
         "Establish a shared understanding of scope, objectives, and success criteria across all stakeholders before any work begins. Resolve ambiguity early to reduce rework.",
         "Scoping Complete"),
        ("2", "Build & Validate",
         "Develop the solution in focused sprints, validating each increment against defined criteria. Surface risks early and iterate with client feedback loops in place.",
         "Solution Validated"),
        ("3", "Deploy & Sustain",
         "Release to production with a structured hypercare period. Embed knowledge, hand over runbooks, and establish KPIs to measure and sustain value over time.",
         "Value Realized"),
    ]
    positions = []
    for i, (num, name, desc, outcome) in enumerate(steps):
        n = i + 1
        cx = body_left + i * (card_w + arrow_w)
        positions.append((cx, cx + card_w))
        _step_box(slide, n, cx, body_top, card_w, body_h,
                  num=num, name=name, desc=desc, outcome=outcome)
    # Arrows between
    arrow_y = body_top + body_h // 2 - 4
    for i in range(2):
        n = i + 1
        ax = positions[i][1] + 4
        # shaft
        add_rect(slide, f"arrow-{n}-shaft", ax, arrow_y, arrow_w - 12, 3, TEXT_FAINT)
        # head: 3 stepped rectangles approximating a chevron
        add_rect(slide, f"arrow-{n}-head1", ax + arrow_w - 16, arrow_y - 4, 3, 11, TEXT_FAINT)
        add_rect(slide, f"arrow-{n}-head2", ax + arrow_w - 12, arrow_y - 2, 3, 7, TEXT_FAINT)

    # Outcome strip
    os_y = body_top + body_h + 8
    os_h = 32
    strip = add_rect(slide, "outcome-strip", body_left, os_y, body_w, os_h, BRAND_PRIMARY)
    add_text(
        slide, "outcome-label", "OUTCOME",
        x_px=body_left + 16, y_px=os_y, w_px=80, h_px=os_h,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, anchor="middle",
        letter_spacing_px=1.6,
    )
    add_text(
        slide, "outcome-text",
        "End-to-end delivery rhythm that reduces time-to-value by 30%, with clear ownership at every gate and a measurable handover ensuring the client can operate independently post-engagement.",
        x_px=body_left + 100, y_px=os_y, w_px=body_w - 116, h_px=os_h,
        font_size_px=11, color=WHITE, italic=True, anchor="middle",
    )

    add_footer(slide, page_num=317)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "317_3bucket-numbered-steps.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
