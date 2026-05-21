"""
Builder for pattern 253: Executive narrative — labeled rows.

Source HTML: _pattern-library/253_exec-narrative-labeled-rows.html

Layout: title block + 5 horizontal row bands, each with a coloured pill label
(Context / Challenge / Insight / Recommendation / Next Steps) and body text.
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

PILL_GREEN = RGBColor(0x1A, 0x6B, 0x3C)
PILL_ORANGE = RGBColor(0xC2, 0x55, 0x0F)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Procurement Transformation — <strong>Strategic Narrative</strong>",
        subtitle="Executive summary across context, challenge, insight, recommendation and next steps",
    )

    # Rows area
    top = 230
    bottom = 640
    rows_h = bottom - top
    gap = 8
    n_rows = 5
    row_h = (rows_h - (n_rows - 1) * gap) // n_rows
    left_x = 48
    right_x = 1280 - 48
    row_w = right_x - left_x
    pill_w = 140

    rows = [
        ("Context", BRAND_PRIMARY,
         "Global procurement costs have risen 23% since 2023, driven by supply chain volatility and inflationary pressure on key input categories."),
        ("Challenge", PILL_ORANGE,
         "Current category management practices are fragmented across 14 business units with no unified sourcing strategy or shared vendor panel."),
        ("Insight", BRAND_PRIMARY_MID,
         "Analysis of $2.4B in annual spend reveals 60% concentration in 8 categories where consolidation alone could yield $180M in savings."),
        ("Recommendation", BRAND_ACCENT,
         "Establish a Centre-Led Procurement model with category ownership, shared supplier contracts, and analytics capability by Q3 2026."),
        ("Next Steps", PILL_GREEN,
         "Approve business case (week 1), appoint Category Leads (week 3), launch supplier renegotiation pilots in top 3 categories (week 8)."),
    ]

    for i, (label, color, body) in enumerate(rows):
        n = i + 1
        ry = top + i * (row_h + gap)
        # Row body card
        card = add_rect(slide, f"row-{n}-bg", left_x, ry, row_w, row_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Pill label (left)
        pill_y = ry + (row_h - 26) // 2
        add_rect(slide, f"row-{n}-pill", left_x + 16, pill_y, pill_w, 26, color)
        add_text(
            slide, f"row-{n}-pill-text", label.upper(),
            x_px=left_x + 16, y_px=pill_y, w_px=pill_w, h_px=26,
            font_size_px=10, color=WHITE, bold=True, align="center", anchor="middle",
            letter_spacing_px=1.2,
        )
        # Body text
        add_text(
            slide, f"row-{n}-text", body,
            x_px=left_x + 16 + pill_w + 18, y_px=ry,
            w_px=row_w - pill_w - 50, h_px=row_h,
            font_size_px=13, color=TEXT_DARK, anchor="middle",
        )

    add_footer(slide, page_num=253)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "253_exec-narrative-labeled-rows.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
