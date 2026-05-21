"""
Dark variant of pattern 42: Q&A discussion.

Source HTML: _pattern-library/42_q-and-a-discussion-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Open for discussion — five questions worth your sixty seconds each.",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "No slides after this one. Pick the question that lands hardest for you and we'll start there.",
        x_px=64, y_px=108, w_px=900, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    q_top = 168
    q_left = 64
    q_right = 1280 - 64
    q_w = q_right - q_left
    q_total_h = 720 - 130 - q_top
    row_h = q_total_h // 5

    questions = [
        ("Q1",
         "Where do YOUR decks degrade most — early structure, mid-review pile-ons, or late-stage rework?",
         "Helps us calibrate the pilot focus area."),
        ("Q2",
         "What would make a four-week pilot land vs. fade — clarity of measurement or visibility to leadership?",
         "Tells us where to invest the program manager hours."),
        ("Q3",
         "Who in the practice would be the best skeptic for this pilot — someone who'd push back fairly?",
         "We need a critic, not a champion, for the week-3 review."),
        ("Q4",
         "What's the smallest measurable win that would convince you to go to wave 2?",
         "Lets us define success up front, not in retrospect."),
        ("Q5",
         "What's the BIGGEST risk we haven't named yet?",
         "Any risk we name today, we can mitigate."),
    ]

    for i, (num, qtext, ctxt) in enumerate(questions):
        n = i + 1
        ry = q_top + i * row_h
        add_text(
            slide, f"question-{n}-num", num,
            x_px=q_left, y_px=ry + (row_h - 36) // 2, w_px=60, h_px=36,
            font_size_px=30, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"question-{n}-text", qtext,
            x_px=q_left + 84, y_px=ry + 14, w_px=q_w - 84, h_px=42,
            font_size_px=17, color=WHITE, bold=True,
        )
        add_text(
            slide, f"question-{n}-context", "→  " + ctxt,
            x_px=q_left + 84, y_px=ry + 56, w_px=q_w - 84, h_px=18,
            font_size_px=12, color=TEXT_ON_DARK_MID, italic=True,
        )
        if i < 4:
            add_rect(slide, f"question-{n}-rule", q_left, ry + row_h - 1, q_w, 1, CARD_BORDER_DARK)

    add_convergence(
        slide,
        "No wrong answers — pick the one that matters most to you and start there.",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(
        slide, "source", "Source: [add source here or delete]",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
    )
    add_text(
        slide, "page-number", "42",
        x_px=1170, y_px=688, w_px=52, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right",
    )
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "42d_q-and-a-discussion.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
