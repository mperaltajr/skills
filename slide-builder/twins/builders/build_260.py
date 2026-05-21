"""
Builder for pattern 260: Small multiples — 6-up bar charts.

Source HTML: _pattern-library/260_small-multiples-6up-bars.html

Layout: title + 3x2 grid of mini bar charts (FY22-FY26), each with CAGR callout.
Consistent scale 0-300 across all panels.

No legend — last bar (FY26) highlighted in darker shade, others uniform accent.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

BAR_LAST = RGBColor(0x6B, 0x00, 0xCC)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Revenue by segment — <strong>consistent scale, 5-year view</strong>",
        subtitle="FY22–FY26 · Revenue $M · Consistent scale 0–$300M across all panels",
    )

    # Body
    body_top = 230
    body_bottom = 632
    body_h = body_bottom - body_top
    left_x = 48
    right_x = 1280 - 48
    body_w = right_x - left_x

    # 3 cols × 2 rows of cards
    cols, rows_n = 3, 2
    col_gap = 16
    row_gap = 14
    card_w = (body_w - (cols - 1) * col_gap) // cols
    card_h = (body_h - (rows_n - 1) * row_gap) // rows_n

    segments = [
        ("Retail", [120, 145, 162, 178, 201], "+14%"),
        ("Healthcare", [85, 98, 110, 129, 158], "+17%"),
        ("Financial Services", [210, 225, 238, 251, 274], "+7%"),
        ("Manufacturing", [95, 88, 92, 105, 119], "+6%"),
        ("Technology", [67, 89, 124, 165, 214], "+34%"),
        ("Government", [180, 184, 179, 188, 195], "+2%"),
    ]
    years = ["FY22", "FY23", "FY24", "FY25", "FY26"]
    max_scale = 300

    for idx, (name, vals, cagr) in enumerate(segments):
        n = idx + 1
        r = idx // cols
        c = idx % cols
        cx = left_x + c * (card_w + col_gap)
        cy = body_top + r * (card_h + row_gap)
        # card bg
        card = add_rect(slide, f"card-{n}", cx, cy, card_w, card_h, WHITE)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # title
        add_text(
            slide, f"card-{n}-title", name,
            x_px=cx + 14, y_px=cy + 10, w_px=card_w - 28, h_px=18,
            font_size_px=12, color=BRAND_PRIMARY, bold=True,
        )
        # chart area
        chart_top = cy + 36
        chart_bottom = cy + card_h - 40
        chart_h = chart_bottom - chart_top
        chart_left = cx + 16
        chart_right = cx + card_w - 16
        chart_w = chart_right - chart_left
        # 5 bars, gap evenly
        bar_count = 5
        bar_slot = chart_w / bar_count
        bar_w = int(bar_slot * 0.55)
        for j, v in enumerate(vals):
            bx = int(chart_left + j * bar_slot + (bar_slot - bar_w) / 2)
            h = int((v / max_scale) * chart_h)
            by = chart_bottom - h
            color = BAR_LAST if j == bar_count - 1 else BRAND_ACCENT
            add_rect(slide, f"card-{n}-bar-{j+1}", bx, by, bar_w, h, color)
            # value label on top
            v_color = BAR_LAST if j == bar_count - 1 else TEXT_MID
            v_bold = (j == bar_count - 1)
            add_text(
                slide, f"card-{n}-val-{j+1}", str(v),
                x_px=bx - 6, y_px=by - 14, w_px=bar_w + 12, h_px=12,
                font_size_px=7, color=v_color, bold=v_bold, align="center",
            )
            # year label
            y_color = BRAND_PRIMARY if j == bar_count - 1 else TEXT_FAINT
            y_bold = (j == bar_count - 1)
            add_text(
                slide, f"card-{n}-year-{j+1}", years[j],
                x_px=bx - 6, y_px=chart_bottom + 2, w_px=bar_w + 12, h_px=12,
                font_size_px=7, color=y_color, bold=y_bold, align="center",
            )
        # callout row at bottom
        callout_y = cy + card_h - 26
        add_text(
            slide, f"card-{n}-cagr", cagr,
            x_px=cx + 14, y_px=callout_y, w_px=80, h_px=18,
            font_size_px=14, color=BRAND_ACCENT, bold=True,
        )
        add_text(
            slide, f"card-{n}-cagr-label", "CAGR FY22–26",
            x_px=cx + 60, y_px=callout_y + 4, w_px=card_w - 80, h_px=14,
            font_size_px=8, color=TEXT_FAINT, bold=True,
            letter_spacing_px=1, uppercase=True,
        )

    add_footer(slide, page_num=260)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "260_small-multiples-6up-bars.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
