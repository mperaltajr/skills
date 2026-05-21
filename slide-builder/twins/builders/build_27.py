"""
Builder for pattern 27: Case study — Situation / Action / Result.

Three cards in a row, each with header band + body + mini-stat. Card 3
(Result) gets accent treatment.

Source HTML: _pattern-library/27_case-study-sar.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Case study — a 30-person practice cut deck cycle time from 14 to 5 days (-64%).",
        subtitle="Same pattern we apply everywhere: storyline first, structured measurement, no bespoke heroics.",
        title_h=68,
        subtitle_h=22,
    )

    # Cards row at y=220, 3 columns, gap=22, padding 56
    grid_left = 56
    card_w = (1280 - 112 - 44) // 3   # 374
    card_h = 310
    gap = 22
    card_top = 220

    headers = ["SITUATION", "ACTION", "RESULT"]
    bodies = [
        "A 30-person strategy practice was producing decks in 12–14 days median, with 8 rounds of partner edits per deck. The bottleneck wasn't talent — it was the assembly process.",
        "Ran a four-week pilot with Slide Lab on one priority workstream. Replaced the partner pre-read meeting with a coached storyline session. Measured every deck against the baseline.",
        "Cycle time dropped from 14 to 5 days — a 64% reduction. Partner edits fell from 8 to 3 per deck, and 94% of decks earned stakeholder sign-off on first review.",
    ]
    foot_labels = ["BASELINE", "APPROACH", "AFTER"]
    foot_values = [
        "14 days median · 8 partner edits",
        "4 weeks · 12 decks measured",
        "5 days median · 3 edits · 94% sign-off",
    ]

    for i in range(3):
        n = i + 1
        cx = grid_left + i * (card_w + gap)

        # Header band
        header_h = 50
        is_result = (i == 2)
        header_fill = BRAND_PRIMARY if is_result else BRAND_PRIMARY_MID
        add_rect(slide, f"card-{n}-header-bg", cx, card_top, card_w, header_h, header_fill)
        add_text(
            slide, f"card-{n}-heading", headers[i],
            x_px=cx + 20, y_px=card_top, w_px=card_w - 40, h_px=header_h,
            font_size_px=13, color=WHITE, bold=True,
            anchor="middle", uppercase=True, letter_spacing_px=3,
        )

        # Card body container (white background, border)
        body = add_rect(slide, f"card-{n}-body-bg", cx, card_top + header_h, card_w, card_h - header_h, WHITE)
        if is_result:
            body.line.color.rgb = BRAND_ACCENT
            body.line.width = 25400  # ~2pt
        else:
            body.line.color.rgb = CARD_BORDER
            body.line.width = 9525

        # Body text
        add_text(
            slide, f"card-{n}-body", bodies[i],
            x_px=cx + 22, y_px=card_top + header_h + 22, w_px=card_w - 44, h_px=card_h - header_h - 100,
            font_size_px=13, color=TEXT_DARK,
        )

        # Mini-stat divider rule
        rule_y = card_top + card_h - 70

        # Mini-stat label + value
        add_text(
            slide, f"card-{n}-footer-label", foot_labels[i],
            x_px=cx + 22, y_px=rule_y + 14, w_px=card_w - 44, h_px=14,
            font_size_px=9, color=BRAND_PRIMARY if is_result else TEXT_FAINT,
            bold=True, uppercase=True, letter_spacing_px=1.4,
        )
        add_text(
            slide, f"card-{n}-footer-value", foot_values[i],
            x_px=cx + 22, y_px=rule_y + 32, w_px=card_w - 44, h_px=22,
            font_size_px=14, color=BRAND_PRIMARY_MID, bold=True,
        )

    add_convergence(
        slide,
        "Same pattern, different client. Repeatable, not bespoke.",
    )

    add_footer(slide, page_num=27)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "27_case-study-sar.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
