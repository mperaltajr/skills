"""
Builder for pattern 42: Q&A discussion — 5 open questions.

Each row: 60px Q-prefix + question text + context line. 1px dividers between
rows. Convergence band at bottom.

Pattern-local IDs: question-N-num, question-N-text, question-N-context.

Source HTML: _pattern-library/42_q-and-a-discussion.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_ACCENT,
    CARD_BORDER, TEXT_DARK, TEXT_MID,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Open for discussion — five questions worth your sixty seconds each.",
        subtitle="No slides after this one. Pick the question that lands hardest for you and we'll start there.",
        title_h=64,
        subtitle_h=22,
    )

    # Questions grid: top=168, bottom=130, left=64, right=64
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
        # Q prefix (60px wide accent)
        add_text(
            slide, f"question-{n}-num", num,
            x_px=q_left, y_px=ry + (row_h - 36) // 2, w_px=60, h_px=36,
            font_size_px=30, color=BRAND_ACCENT, bold=True,
        )
        # Question text (single line, multi-row wrap)
        add_text(
            slide, f"question-{n}-text", qtext,
            x_px=q_left + 84, y_px=ry + 14, w_px=q_w - 84, h_px=42,
            font_size_px=17, color=TEXT_DARK, bold=True,
        )
        # Context line below
        add_text(
            slide, f"question-{n}-context", "→  " + ctxt,
            x_px=q_left + 84, y_px=ry + 56, w_px=q_w - 84, h_px=18,
            font_size_px=12, color=TEXT_MID, italic=True,
        )
        # Bottom divider (except last)
        if i < 4:
            add_rect(slide, f"question-{n}-rule", q_left, ry + row_h - 1, q_w, 1, CARD_BORDER)

    add_convergence(
        slide,
        "No wrong answers — pick the one that matters most to you and start there.",
    )

    add_footer(slide, page_num=42)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "42_q-and-a-discussion.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
