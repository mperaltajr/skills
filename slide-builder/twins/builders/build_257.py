"""
Builder for pattern 257: Lollipop chart — channel engagement.

Source HTML: _pattern-library/257_lollipop-chart.html

Layout: title block + chart (10 rows, accent dots top-3 + grey rest) on left,
key-findings annotation panel on right.

LEGEND PLACEMENT: Right-aligned below subheadline (top-y ≥ 230, right edge ≈ 1240).
Body shifted down to clear the legend.
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

GREY_DOT = RGBColor(0x64, 0x74, 0x8B)
GREY_LINE = RGBColor(0x94, 0xA3, 0xB8)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Channel engagement scores — <strong>digital leads by a wide margin.</strong>",
        subtitle="Composite engagement index by channel, current period · ranked descending · top 3 highlighted",
    )

    # === LEGEND — below subheadline, right-aligned to x≈1240 ===
    leg_y = 230
    leg_h = 22
    leg_w = 280
    leg_x = 1240 - leg_w
    # swatch+label item 1
    add_rect(slide, "legend-1-swatch", leg_x, leg_y + 7, 10, 10, BRAND_ACCENT)
    add_text(
        slide, "legend-1-label", "Top 3 channels",
        x_px=leg_x + 16, y_px=leg_y + 2, w_px=120, h_px=18,
        font_size_px=11, color=TEXT_MID, bold=True,
    )
    add_rect(slide, "legend-2-swatch", leg_x + 140, leg_y + 7, 10, 10, GREY_DOT)
    add_text(
        slide, "legend-2-label", "All other channels",
        x_px=leg_x + 156, y_px=leg_y + 2, w_px=130, h_px=18,
        font_size_px=11, color=TEXT_MID, bold=True,
    )

    # === Body — shifted down to clear legend (legend bottom ≈ 252) ===
    body_top = 268
    body_bottom = 632
    body_h = body_bottom - body_top
    left_x = 48
    right_x = 1280 - 48
    body_w = right_x - left_x

    # Split: chart 70%, annotation 30%
    chart_w = int(body_w * 0.66)
    ann_gap = 18
    ann_w = body_w - chart_w - ann_gap

    # Chart panel background
    chart_x = left_x
    chart_y = body_top
    chart_bg = add_rect(slide, "chart-zone", chart_x, chart_y, chart_w, body_h, CARD_BG)
    chart_bg.line.color.rgb = CARD_BORDER
    chart_bg.line.width = 9525

    # Plot area inside chart
    # 10 rows, label zone left ≈ 150px, plot zone right
    plot_left = chart_x + 150
    plot_right = chart_x + chart_w - 60  # leave room for value labels
    plot_w = plot_right - plot_left
    plot_top = chart_y + 16
    plot_bottom = chart_y + body_h - 30
    plot_h = plot_bottom - plot_top
    row_n = 10
    row_step = plot_h // row_n

    # X-axis grid lines (25/50/75/100%)
    for pct in (25, 50, 75, 100):
        gx = plot_left + int(plot_w * pct / 100)
        # dashed-ish: use thin grey line
        add_rect(slide, f"gridline-{pct}", gx, plot_top, 1, plot_h, CARD_BORDER)
    # X-axis labels
    for pct in (0, 25, 50, 75, 100):
        gx = plot_left + int(plot_w * pct / 100)
        add_text(
            slide, f"tick-{pct}", f"{pct}%",
            x_px=gx - 20, y_px=plot_bottom + 4, w_px=40, h_px=14,
            font_size_px=9, color=TEXT_FAINT, align="center",
        )

    rows = [
        ("Digital Channels", 87, True),
        ("Mobile App", 79, True),
        ("Self-Service", 71, True),
        ("Email", 64, False),
        ("Branch", 58, False),
        ("Call Center", 52, False),
        ("Chat Bot", 44, False),
        ("Partner Network", 38, False),
        ("Postal", 24, False),
        ("Fax", 8, False),
    ]
    for i, (name, value, top3) in enumerate(rows):
        n = i + 1
        cy = plot_top + i * row_step + row_step // 2
        col_line = BRAND_ACCENT if top3 else GREY_LINE
        col_dot = BRAND_ACCENT if top3 else GREY_DOT
        # label
        add_text(
            slide, f"row-{n}-label", name,
            x_px=chart_x + 10, y_px=cy - 8, w_px=130, h_px=16,
            font_size_px=10, color=TEXT_DARK,
            bold=top3, align="right",
        )
        # line from axis to value
        end_x = plot_left + int(plot_w * value / 100)
        add_rect(slide, f"row-{n}-line", plot_left, cy - 1, end_x - plot_left, 2, col_line)
        # dot
        add_rect(slide, f"row-{n}-dot", end_x - 5, cy - 5, 10, 10, col_dot)
        # value
        add_text(
            slide, f"row-{n}-val", f"{value}%",
            x_px=end_x + 8, y_px=cy - 8, w_px=50, h_px=16,
            font_size_px=10, color=TEXT_MID, bold=True,
        )

    # Annotation panel (right)
    ann_x = chart_x + chart_w + ann_gap
    ann_bg = add_rect(slide, "annotation", ann_x, body_top, ann_w, body_h, BRAND_PRIMARY)

    add_text(
        slide, "annotation-tag", "KEY FINDINGS",
        x_px=ann_x + 18, y_px=body_top + 16, w_px=ann_w - 36, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        letter_spacing_px=1.4, uppercase=True,
    )
    bullets = [
        ("Digital channels dominate:", " the top 3 ranked channels are all digital — signalling a decisive shift in customer preference away from human-staffed touchpoints."),
        ("Legacy channels trail sharply:", " Postal (24%) and Fax (8%) score below a quarter of the leading channel, indicating residual edge-case use only."),
        ("Mid-tier gap is actionable:", " Call Center and Chat Bot cluster between 44–52% — targeted investment in conversational AI could close the gap in one cycle."),
    ]
    bul_top = body_top + 48
    bul_area_h = body_h - 100
    item_h = bul_area_h // len(bullets)
    for i, (head, tail) in enumerate(bullets):
        n = i + 1
        iy = bul_top + i * item_h
        add_text(
            slide, f"ann-bullet-{n}-marker", "■",
            x_px=ann_x + 18, y_px=iy, w_px=12, h_px=18,
            font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"ann-bullet-{n}", f"<strong>{head}</strong>{tail}",
            x_px=ann_x + 36, y_px=iy - 2, w_px=ann_w - 54, h_px=item_h - 6,
            font_size_px=11, color=WHITE, emphasis_color=WHITE,
        )

    add_text(
        slide, "annotation-source",
        "Source: Customer Engagement Survey, Q1 2026 · n = 4,200 · composite (reach × depth × satisfaction)",
        x_px=ann_x + 18, y_px=body_top + body_h - 36, w_px=ann_w - 36, h_px=30,
        font_size_px=8, color=BRAND_ACCENT_SOFT, italic=True,
    )

    add_footer(slide, page_num=257)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "257_lollipop-chart.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
