"""
Builder for pattern 261: Waterfall chart with subtotals (dark).

Legend MOVED from chart-top-right to BELOW subheadline at y=230, right-aligned
per mandatory rule (right panel is <30% width / 35% in this design but rule says
default to below subhead).

Source HTML: _pattern-library/261_waterfall-subtotals-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER = RGBColor(0x55, 0x36, 0x77)

GROWTH = RGBColor(0x38, 0xA1, 0x69)
GROWTH_LIGHT = RGBColor(0x68, 0xD3, 0x91)
HEADWIND = RGBColor(0xE5, 0x3E, 0x3E)
HEADWIND_LIGHT = RGBColor(0xFC, 0x81, 0x81)
SUBTOTAL = RGBColor(0xC0, 0xB0, 0xD8)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Title block — canonical chrome
    add_text(slide, "title",
             "FY25→FY26 Revenue Bridge: <strong>$90M Net Growth</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Waterfall decomposition of drivers — volume & price gains offset FX and churn headwinds",
             x_px=48, y_px=108, w_px=900, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 80, 3, BRAND_ACCENT_SOFT)

    # Legend BELOW subhead, right-aligned (right edge x≈1232, y≥230)
    leg_y = 230
    leg_items = [
        ("Growth driver", GROWTH),
        ("Headwind", HEADWIND),
        ("Subtotal", SUBTOTAL),
        ("Total / Actual", BRAND_ACCENT),
    ]
    leg_item_w = [110, 90, 90, 120]
    leg_total = sum(leg_item_w) + 30
    leg_x_start = 1232 - leg_total
    cx = leg_x_start
    for i, (lbl, col) in enumerate(leg_items):
        add_rect(slide, f"legend-{i+1}-swatch", cx, leg_y + 4, 10, 10, col)
        add_text(slide, f"legend-{i+1}-label", lbl,
                 x_px=cx + 14, y_px=leg_y, w_px=leg_item_w[i] - 14, h_px=18,
                 font_size_px=10, color=TEXT_ON_DARK_MID)
        cx += leg_item_w[i]

    # Body below legend: chart left, cards right
    body_top = 260
    body_bot = 670
    chart_x = 48
    chart_w = 760
    cards_x = chart_x + chart_w + 24
    cards_w = 1232 - cards_x

    # ---- CHART (waterfall) - scale to body ----
    # Original SVG was viewBox 760x530. Map to chart area.
    # plotLeft=70, plotRight=740, plotTop=20, plotBottom=460 in svg coords.
    # We render directly using shape rects scaled into chart region.
    cy0 = body_top + 16
    ch = body_bot - body_top - 60  # leave room for x-labels
    sx = chart_w / 760.0
    sy = ch / 480.0

    def cx_(x):
        return chart_x + int(x * sx)

    def cy_(y):
        return cy0 + int(y * sy)

    # Gridline at baseline
    add_rect(slide, "axis-baseline", cx_(70), cy_(460), cx_(740) - cx_(70), 1,
             RGBColor(0x6E, 0x4F, 0x8C))

    # Bars
    bars = [
        # x_svg, y_svg, w_svg, h_svg, fill, label, label_y, label_color, grounded
        (80, 158, 56, 302, BRAND_PRIMARY_MID, "$480M", 138, WHITE),
        (154, 105, 56, 53, GROWTH, "+$85M", 85, GROWTH_LIGHT),
        (228, 79, 56, 26, GROWTH, "+$42M", 59, GROWTH_LIGHT),
        (302, 61, 56, 18, GROWTH, "+$28M", 41, GROWTH_LIGHT),
        (376, 61, 56, 399, SUBTOTAL, "$635M", 41, WHITE),
        (450, 61, 56, 21, HEADWIND, "-$34M", 86, HEADWIND_LIGHT),
        (524, 82, 56, 12, HEADWIND, "-$19M", 98, HEADWIND_LIGHT),
        (598, 94, 56, 8, HEADWIND, "-$12M", 106, HEADWIND_LIGHT),
        (672, 102, 56, 358, BRAND_ACCENT, "$570M", 82, BRAND_ACCENT_SOFT),
    ]
    x_labels = ["FY25", "Volume", "Price", "New Mkt", "H1 Sub", "FX", "Cost", "Churn", "FY26"]

    for i, (x, y, w, h, fill, val, lbly, lblc) in enumerate(bars):
        n = i + 1
        bx = cx_(x)
        by = cy_(y)
        bw = max(1, int(w * sx))
        bh = max(1, int(h * sy))
        add_rect(slide, f"bar-{n}", bx, by, bw, bh, fill)
        # Value label centered above
        add_text(slide, f"bar-{n}-label", val,
                 x_px=bx - 20, y_px=cy_(lbly) - 4, w_px=bw + 40, h_px=14,
                 font_size_px=9, color=lblc, bold=True, align="center")
        # X-axis label (centered under bar)
        add_text(slide, f"bar-{n}-xlabel", x_labels[i],
                 x_px=bx - 16, y_px=cy_(465), w_px=bw + 32, h_px=18,
                 font_size_px=9, color=TEXT_ON_DARK_MID, align="center")

    # Chart title strip (left)
    add_text(slide, "chart-y-label", "Revenue ($M)",
             x_px=chart_x, y_px=cy0 - 4, w_px=120, h_px=14,
             font_size_px=9, color=TEXT_ON_DARK_FAINT)

    # ---- RIGHT: 1 callout + 3 insight cards ----
    n_cards = 4
    card_h = (body_bot - body_top - (n_cards - 1) * 10) // n_cards
    cy = body_top

    # Net callout
    add_rect(slide, "net-callout-bg", cards_x, cy, cards_w, card_h,
             RGBColor(0x52, 0x1E, 0x7A))
    add_text(slide, "net-callout-label", "NET REVENUE CHANGE",
             x_px=cards_x + 14, y_px=cy + 10, w_px=cards_w - 28, h_px=14,
             font_size_px=8, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1.5)
    add_text(slide, "net-callout-value", "+$90M",
             x_px=cards_x + 14, y_px=cy + 26, w_px=cards_w - 28, h_px=30,
             font_size_px=22, color=BRAND_ACCENT_SOFT, bold=True)
    add_text(slide, "net-callout-desc",
             "$155M tailwinds (volume, price, new markets) offset $65M headwinds (FX, cost, churn) = net +$90M.",
             x_px=cards_x + 14, y_px=cy + 58, w_px=cards_w - 28, h_px=card_h - 64,
             font_size_px=10, color=TEXT_ON_DARK_MID)
    cy += card_h + 10

    insights = [
        ("GROWTH DRIVERS", "Volume & price = 82% of tailwinds",
         "Volume ($85M) and price ($42M) are the primary levers. New Markets +$28M tracking ahead of plan."),
        ("HEADWIND EXPOSURE", "FX = 52% of downside risk",
         "$34M FX headwind is the largest drag. Cost pass-through ($19M) and churn ($12M) manageable."),
        ("FY26 OUTLOOK", "$570M actual; momentum sustained",
         "H1 Subtotal $635M exceeded target ~3%. Upside scenario reaches $590-600M with FX normalisation."),
    ]
    for i, (lbl, ttl, body) in enumerate(insights):
        add_rect(slide, f"insight-{i+1}-bg", cards_x, cy, cards_w, card_h, CARD_BG)
        add_text(slide, f"insight-{i+1}-label", lbl,
                 x_px=cards_x + 14, y_px=cy + 10, w_px=cards_w - 28, h_px=14,
                 font_size_px=8, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1.2)
        add_text(slide, f"insight-{i+1}-title", ttl,
                 x_px=cards_x + 14, y_px=cy + 28, w_px=cards_w - 28, h_px=20,
                 font_size_px=11, color=WHITE, bold=True)
        add_text(slide, f"insight-{i+1}-body", body,
                 x_px=cards_x + 14, y_px=cy + 50, w_px=cards_w - 28, h_px=card_h - 56,
                 font_size_px=10, color=TEXT_ON_DARK_MID)
        cy += card_h + 10

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "261",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "261_waterfall-subtotals-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
