"""
Builder for pattern 92: Three-step approach — argue, build, QC.

Three chevron-headed steps across the body, each with activities list and
deliverable pill at the bottom. Headers graduate from brand-primary (step 1)
to brand-primary-mid (step 2) to brand-accent (step 3).
Convergence: gradient line + centered italic text.

Source HTML: _pattern-library/92_three-step-approach.html
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
from pptx.enum.shapes import MSO_SHAPE
from twins.helpers import px_to_emu


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # --- Title block ---
    add_text(
        slide, "title",
        "Three steps — <strong>argue, build, QC. Nothing else.</strong>",
        x_px=56, y_px=56, w_px=1168, h_px=44,
        font_size_px=26, color=TEXT_DARK, bold=True,
        emphasis_color=BRAND_PRIMARY,
    )
    add_text(
        slide, "subtitle",
        "A deliberately simple approach — each step ends in a tangible artefact the next step builds on.",
        x_px=56, y_px=108, w_px=1168, h_px=22,
        font_size_px=12, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=56, y_px=144, w_px=56, h_px=3, fill_color=BRAND_ACCENT)

    # --- Three steps ---
    body_top = 200
    body_bottom = 590
    body_h = body_bottom - body_top
    body_left = 56
    body_right = 1280 - 56
    body_w = body_right - body_left
    gap = 18
    step_w = (body_w - 2 * gap) // 3
    head_h = 68
    chevron_pt = 22  # depth of chevron arrow

    head_colors = [BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT]
    steps = [
        (
            "Step 01", "ARGUE",
            ["Lock the governing thought", "Sharpen MECE structure", "Test against counterexamples"],
            "Argued storyline",
        ),
        (
            "Step 02", "BUILD",
            ["Match patterns", "Fill content", "Apply brand theme"],
            "Real PPTX deck",
        ),
        (
            "Step 03", "QC",
            ["Run hygiene checklist", "Render and inspect", "Refine and deliver"],
            "Partner-ready deck",
        ),
    ]
    for i, (snum, sname, activities, deliverable) in enumerate(steps):
        n = i + 1
        sx = body_left + i * (step_w + gap)
        head_color = head_colors[i]

        # Chevron head — use PENTAGON shape (right-pointing) which gives a flat-left,
        # pointed-right look matching the HTML clip-path.
        chev = slide.shapes.add_shape(
            MSO_SHAPE.PENTAGON,
            px_to_emu(sx), px_to_emu(body_top),
            px_to_emu(step_w), px_to_emu(head_h),
        )
        chev.name = f"step-{n}-head"
        chev.fill.solid()
        chev.fill.fore_color.rgb = head_color
        chev.line.fill.background()

        # Head text
        add_text(
            slide, f"step-{n}-num", snum,
            x_px=sx + 22, y_px=body_top + 10, w_px=step_w - chevron_pt - 22, h_px=16,
            font_size_px=9, color=WHITE, bold=True,
            letter_spacing_px=2.5, uppercase=True,
        )
        add_text(
            slide, f"step-{n}-name", sname,
            x_px=sx + 22, y_px=body_top + 28, w_px=step_w - chevron_pt - 22, h_px=32,
            font_size_px=22, color=WHITE, bold=True,
            letter_spacing_px=1,
        )

        # Body box (below head)
        body_y = body_top + head_h
        body_h_real = body_h - head_h
        body_box = add_rect(slide, f"step-{n}-body", sx, body_y, step_w, body_h_real, CARD_BG)
        body_box.line.color.rgb = CARD_BORDER
        body_box.line.width = 9525

        # Activity bullets
        list_top = body_y + 20
        for ai, act in enumerate(activities):
            an = ai + 1
            ay = list_top + ai * 32
            # Bullet
            add_rect(slide, f"step-{n}-bullet-{an}-dot", sx + 18, ay + 7, 6, 6, head_color)
            add_text(
                slide, f"step-{n}-bullet-{an}", act,
                x_px=sx + 32, y_px=ay, w_px=step_w - 50, h_px=24,
                font_size_px=12, color=TEXT_DARK,
            )

        # Deliverable pill
        pill_w = step_w - 40
        pill_h = 42
        pill_x = sx + (step_w - pill_w) // 2
        pill_y = body_y + body_h_real - pill_h - 18
        pill_box = add_rect(slide, f"step-{n}-pill", pill_x, pill_y, pill_w, pill_h, WHITE)
        pill_box.line.color.rgb = head_color
        pill_box.line.width = 19050
        add_text(
            slide, f"step-{n}-pill-label", "Deliverable",
            x_px=pill_x, y_px=pill_y + 6, w_px=pill_w, h_px=12,
            font_size_px=8, color=head_color, bold=True,
            letter_spacing_px=1.8, uppercase=True, align="center",
        )
        add_text(
            slide, f"step-{n}-pill-text", deliverable,
            x_px=pill_x, y_px=pill_y + 18, w_px=pill_w, h_px=20,
            font_size_px=12, color=BRAND_PRIMARY, bold=True, align="center",
        )

    # --- Convergence: gradient line + centered italic ---
    conv_y = 620
    # Three colored segments to approximate gradient
    seg_w = 380
    line_y = conv_y + 12
    add_rect(slide, "conv-line-1", body_left, line_y, seg_w, 2, BRAND_PRIMARY)
    add_rect(slide, "conv-line-2", body_left + seg_w, line_y, seg_w, 2, BRAND_PRIMARY_MID)
    add_rect(slide, "conv-line-3", body_right - seg_w, line_y, seg_w, 2, BRAND_ACCENT)
    # White text-clear behind centered text
    add_rect(slide, "conv-text-bg", 290, conv_y, 700, 30, WHITE)
    add_text(
        slide, "convergence",
        "Argument earns the build · Build earns the QC · QC earns the delivery",
        x_px=290, y_px=conv_y, w_px=700, h_px=30,
        font_size_px=12, color=BRAND_PRIMARY, italic=True, bold=True, align="center", anchor="middle",
    )

    add_footer(slide, page_num=92)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "92_three-step-approach.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
