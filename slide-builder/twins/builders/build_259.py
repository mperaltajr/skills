"""
Builder for pattern 259: Bar + sparkline rows — Regional Revenue Performance.

Source HTML: _pattern-library/259_bar-sparkline-rows.html

Layout: title + 8-row table (Category | Bar+Value | Sparkline | ΔYoY) on left,
key insights panel on right.

No legend in source pattern; categorical bars + sparklines are self-labeling.
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

POS = RGBColor(0x16, 0xA3, 0x4A)
NEG = RGBColor(0xDC, 0x26, 0x26)
NEUTRAL = RGBColor(0x94, 0xA3, 0xB8)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Regional Revenue Performance <strong>FY2026</strong>",
        subtitle="Ranked by absolute value with six-year trend and year-on-year delta · All figures in USD millions",
    )

    # Body
    body_top = 230
    body_bottom = 632
    body_h = body_bottom - body_top
    left_x = 48
    right_x = 1280 - 48
    body_w = right_x - left_x

    # Split: table 70%, panel 30%
    table_w = int(body_w * 0.70)
    gap = 16
    panel_w = body_w - table_w - gap

    # Column layout for table
    table_x = left_x
    cat_w = 130
    bar_w = 360  # area for bar+value
    spark_w = 110
    delta_w = table_w - cat_w - bar_w - spark_w
    col_x = [table_x, table_x + cat_w, table_x + cat_w + bar_w,
             table_x + cat_w + bar_w + spark_w]
    col_widths = [cat_w, bar_w, spark_w, delta_w]

    # Header row
    header_h = 24
    add_rect(slide, "col-header-bg", table_x, body_top, table_w, header_h, CARD_BG)
    headers = ["Category", "Value (FY26)", "Trend (FY21–26)", "ΔYoY"]
    aligns = ["left", "left", "center", "right"]
    for ci, (h, a) in enumerate(zip(headers, aligns)):
        add_text(
            slide, f"col-header-{ci+1}", h.upper(),
            x_px=col_x[ci] + 10, y_px=body_top, w_px=col_widths[ci] - 20, h_px=header_h,
            font_size_px=9, color=TEXT_MID, bold=True, anchor="middle",
            letter_spacing_px=1.2, align=a,
        )

    # 8 rows
    rows = [
        ("North America", 847, "$847M", 18, "pos"),
        ("EMEA", 612, "$612M", 7, "pos"),
        ("Asia Pacific", 441, "$441M", 31, "pos"),
        ("Latin America", 198, "$198M", 3, "pos-mild"),
        ("Middle East", 124, "$124M", 22, "pos"),
        ("Africa", 89, "$89M", -4, "neg"),
        ("Central Asia", 54, "$54M", 1, "pos-mild"),
        ("ANZ", 47, "$47M", -11, "neg"),
    ]
    row_h = (body_h - header_h) // len(rows)
    bar_max_value = 1000
    bar_track_w = bar_w - 80  # leave room for value label
    bar_height_px = 12

    # sparkline polyline data (FY21-FY26 trend shape)
    spark_data = [
        [480, 510, 560, 620, 700, 847],
        [490, 500, 510, 540, 570, 612],
        [210, 240, 280, 320, 380, 441],
        [220, 200, 185, 175, 192, 198],
        [55, 65, 75, 88, 102, 124],
        [105, 100, 98, 95, 93, 89],
        [50, 51, 52, 53, 53, 54],
        [70, 65, 60, 55, 53, 47],
    ]

    for i, (cat, value, val_text, delta, kind) in enumerate(rows):
        n = i + 1
        ry = body_top + header_h + i * row_h
        # alternating row backgrounds
        if i % 2 == 1:
            add_rect(slide, f"row-{n}-bg", table_x, ry, table_w, row_h, CARD_BG)
        # category
        add_text(
            slide, f"row-{n}-cat", cat,
            x_px=col_x[0] + 10, y_px=ry, w_px=cat_w - 20, h_px=row_h,
            font_size_px=12, color=TEXT_DARK, bold=True, anchor="middle",
        )
        # bar
        bar_pct = value / bar_max_value
        b_w = int(bar_track_w * bar_pct)
        b_y = ry + (row_h - bar_height_px) // 2
        add_rect(slide, f"row-{n}-bar-track", col_x[1] + 10, b_y, bar_track_w, bar_height_px,
                 RGBColor(0xEE, 0xE8, 0xF5))
        add_rect(slide, f"row-{n}-bar-fill", col_x[1] + 10, b_y, b_w, bar_height_px, BRAND_ACCENT)
        # value label
        add_text(
            slide, f"row-{n}-val", val_text,
            x_px=col_x[1] + 10 + bar_track_w + 6, y_px=ry, w_px=70, h_px=row_h,
            font_size_px=11, color=TEXT_DARK, bold=True, anchor="middle",
        )
        # sparkline — draw polyline as multiple small rects (approximation of line segments)
        spark = spark_data[i]
        sx = col_x[2] + 10
        sw = spark_w - 20
        sh = row_h - 16
        sy = ry + 8
        smin, smax = min(spark), max(spark)
        if smax == smin:
            smax = smin + 1
        pts = []
        for j, v in enumerate(spark):
            px = sx + int(j * sw / (len(spark) - 1))
            py = sy + sh - int((v - smin) * sh / (smax - smin))
            pts.append((px, py))
        # draw line segments via thin rects
        for j in range(len(pts) - 1):
            x1, y1 = pts[j]
            x2, y2 = pts[j + 1]
            # we approximate with a thin rotated-looking segment: just a thin connector rectangle
            # PowerPoint doesn't easily rotate; draw a short diagonal as a freeform line shape
            from pptx.enum.shapes import MSO_SHAPE_TYPE
            line = slide.shapes.add_connector(1, 0, 0, 0, 0)  # straight connector
            from twins.helpers import px_to_emu
            line.begin_x = px_to_emu(x1)
            line.begin_y = px_to_emu(y1)
            line.end_x = px_to_emu(x2)
            line.end_y = px_to_emu(y2)
            line.line.color.rgb = BRAND_ACCENT_SOFT
            line.line.width = 19050  # ~2pt
        # delta
        if kind == "pos":
            d_color = POS
            d_text = f"+{delta}% ↑"
        elif kind == "pos-mild":
            d_color = POS
            d_text = f"+{delta}% ↑"
        else:
            d_color = NEG
            d_text = f"{delta}% ↓"
        add_text(
            slide, f"row-{n}-delta", d_text,
            x_px=col_x[3], y_px=ry, w_px=delta_w - 10, h_px=row_h,
            font_size_px=12, color=d_color, bold=True, align="right", anchor="middle",
        )

    # Right insight panel
    pn_x = table_x + table_w + gap
    add_text(
        slide, "panel-heading", "KEY INSIGHTS",
        x_px=pn_x, y_px=body_top, w_px=panel_w, h_px=14,
        font_size_px=9, color=TEXT_FAINT, bold=True,
        letter_spacing_px=1.4, uppercase=True,
    )
    # card 1
    c1_y = body_top + 22
    c1_h = 150
    card1 = add_rect(slide, "insight-card-1", pn_x, c1_y, panel_w, c1_h, CARD_BG)
    card1.line.color.rgb = CARD_BORDER
    card1.line.width = 9525
    add_rect(slide, "insight-card-1-accent", pn_x, c1_y, 3, c1_h, BRAND_ACCENT)
    add_text(
        slide, "insight-card-1-label", "GROWTH LEADER",
        x_px=pn_x + 14, y_px=c1_y + 12, w_px=panel_w - 28, h_px=12,
        font_size_px=9, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=1.2, uppercase=True,
    )
    add_text(
        slide, "insight-card-1-body",
        "Asia Pacific posted the strongest YoY growth at <strong>+31%</strong>, driven by accelerated digital transformation investment across SEA markets. Momentum is steepening — FY27 could surpass Latin America in absolute scale.",
        x_px=pn_x + 14, y_px=c1_y + 28, w_px=panel_w - 28, h_px=c1_h - 36,
        font_size_px=10, color=TEXT_DARK, emphasis_color=BRAND_PRIMARY,
    )
    # card 2
    c2_y = c1_y + c1_h + 12
    c2_h = 150
    card2 = add_rect(slide, "insight-card-2", pn_x, c2_y, panel_w, c2_h, CARD_BG)
    card2.line.color.rgb = CARD_BORDER
    card2.line.width = 9525
    add_rect(slide, "insight-card-2-accent", pn_x, c2_y, 3, c2_h, BRAND_ACCENT)
    add_text(
        slide, "insight-card-2-label", "WATCH LIST",
        x_px=pn_x + 14, y_px=c2_y + 12, w_px=panel_w - 28, h_px=12,
        font_size_px=9, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=1.2, uppercase=True,
    )
    add_text(
        slide, "insight-card-2-body",
        "Africa and ANZ are in structural decline. Combined revenue contraction of <strong>−$14M</strong> YoY warrants portfolio review. Flat trend in Central Asia signals limited near-term upside.",
        x_px=pn_x + 14, y_px=c2_y + 28, w_px=panel_w - 28, h_px=c2_h - 36,
        font_size_px=10, color=TEXT_DARK, emphasis_color=BRAND_PRIMARY,
    )
    # source
    add_text(
        slide, "source-note",
        "Source: Global Revenue Operations Dashboard, FY26 Q4 Close · Figures rounded to nearest $1M.",
        x_px=pn_x, y_px=body_bottom - 28, w_px=panel_w, h_px=24,
        font_size_px=8, color=TEXT_FAINT, italic=True,
    )

    add_footer(slide, page_num=259)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "259_bar-sparkline-rows.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
