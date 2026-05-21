"""
Builder for pattern 263: Slope chart — before/after capability maturity.

Source HTML: _pattern-library/263_slope-chart-before-after.html

Layout: title + slope chart (FY2024 → FY2026, 8 capabilities, 5 increasing accent /
3 decreasing red dashed) on left, key insights panel on right.

LEGEND PLACEMENT: Right-aligned below subheadline (top-y ≥ 230, right edge ≈ 1240).
Increase legend = solid violet line. Decrease = dashed red line.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

RED_DEC = RGBColor(0xE5, 0x3E, 0x3E)


def _connector(slide, x1, y1, x2, y2, color, width_emu, dashed=False):
    line = slide.shapes.add_connector(1, 0, 0, 0, 0)
    line.begin_x = px_to_emu(x1)
    line.begin_y = px_to_emu(y1)
    line.end_x = px_to_emu(x2)
    line.end_y = px_to_emu(y2)
    line.line.color.rgb = color
    line.line.width = width_emu
    if dashed:
        from pptx.enum.dml import MSO_LINE_DASH_STYLE
        line.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return line


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Digital capabilities surged — <strong>legacy operations fell sharply.</strong>",
        subtitle="Maturity scores by capability area, FY2024 vs FY2026 (0–100 scale). Increases in violet, decreases in red dashed.",
    )

    # === LEGEND — below subheadline, right-aligned ===
    leg_y = 230
    leg_w = 380
    leg_x = 1240 - leg_w
    add_rect(slide, "legend-up-swatch", leg_x, leg_y + 8, 22, 3, BRAND_ACCENT)
    add_text(slide, "legend-up", "Increase (solid violet)",
             x_px=leg_x + 28, y_px=leg_y + 2, w_px=170, h_px=18,
             font_size_px=11, color=TEXT_DARK, bold=True)
    add_rect(slide, "legend-down-swatch", leg_x + 200, leg_y + 8, 22, 3, RED_DEC)
    add_text(slide, "legend-down", "Decrease (dashed red)",
             x_px=leg_x + 228, y_px=leg_y + 2, w_px=160, h_px=18,
             font_size_px=11, color=TEXT_DARK, bold=True)

    # === Body ===
    body_top = 268
    body_bottom = 635
    body_h = body_bottom - body_top
    left_x = 48
    right_x = 1280 - 48
    body_w = right_x - left_x

    chart_w = int(body_w * 0.66)
    gap = 18
    panel_w = body_w - chart_w - gap

    chart_x = left_x
    chart_y = body_top
    chart_bg = add_rect(slide, "chart-area", chart_x, chart_y, chart_w, body_h, CARD_BG)
    chart_bg.line.color.rgb = CARD_BORDER
    chart_bg.line.width = 9525

    # Plot area: leave 80px each side for name labels
    plot_left = chart_x + 100
    plot_right = chart_x + chart_w - 110
    plot_top = chart_y + 40
    plot_bottom = chart_y + body_h - 30
    plot_h = plot_bottom - plot_top

    def y_for(v):
        return plot_bottom - int((v / 100) * plot_h)

    # Y gridlines (0,25,50,75,100)
    for v in (0, 25, 50, 75, 100):
        gy = y_for(v)
        add_rect(slide, f"grid-{v}", plot_left, gy, plot_right - plot_left, 1, CARD_BORDER)
        add_text(slide, f"y-tick-{v}", str(v),
                 x_px=plot_left - 36, y_px=gy - 7, w_px=30, h_px=14,
                 font_size_px=9, color=TEXT_FAINT, align="right")

    # Column headers
    add_text(slide, "col-head-before", "FY2024",
             x_px=plot_left - 40, y_px=plot_top - 24, w_px=80, h_px=16,
             font_size_px=11, color=BRAND_PRIMARY, bold=True, align="center",
             letter_spacing_px=0.5)
    add_text(slide, "col-head-after", "FY2026",
             x_px=plot_right - 40, y_px=plot_top - 24, w_px=80, h_px=16,
             font_size_px=11, color=BRAND_PRIMARY, bold=True, align="center",
             letter_spacing_px=0.5)

    # Vertical axes
    add_rect(slide, "left-axis", plot_left, plot_top, 1, plot_h, BRAND_PRIMARY)
    add_rect(slide, "right-axis", plot_right, plot_top, 1, plot_h, BRAND_PRIMARY)

    data = [
        ("Digital", 38, 74, "inc"),
        ("Mobile", 29, 61, "inc"),
        ("Analytics", 45, 67, "inc"),
        ("Cloud", 52, 71, "inc"),
        ("Process Auto", 18, 42, "inc"),
        ("Legacy Systems", 78, 65, "dec"),
        ("Manual Ops", 82, 58, "dec"),
        ("Paper-based", 71, 31, "dec"),
    ]

    for i, (name, before, after, kind) in enumerate(data):
        n = i + 1
        y1 = y_for(before)
        y2 = y_for(after)
        color = BRAND_ACCENT if kind == "inc" else RED_DEC
        _connector(slide, plot_left, y1, plot_right, y2, color, 22225, dashed=(kind == "dec"))
        # dots
        add_rect(slide, f"dot-{n}-L", plot_left - 5, y1 - 5, 10, 10, color)
        add_rect(slide, f"dot-{n}-R", plot_right - 5, y2 - 5, 10, 10, color)
        # left name
        add_text(slide, f"name-L-{n}", name,
                 x_px=chart_x + 6, y_px=y1 - 8, w_px=80, h_px=14,
                 font_size_px=9, color=BRAND_PRIMARY, bold=True, align="right")
        add_text(slide, f"val-L-{n}", str(before),
                 x_px=plot_left + 8, y_px=y1 - 8, w_px=24, h_px=14,
                 font_size_px=9, color=color, bold=True)
        # right
        add_text(slide, f"val-R-{n}", str(after),
                 x_px=plot_right - 32, y_px=y2 - 8, w_px=24, h_px=14,
                 font_size_px=9, color=color, bold=True, align="right")
        add_text(slide, f"name-R-{n}", name,
                 x_px=plot_right + 8, y_px=y2 - 8, w_px=90, h_px=14,
                 font_size_px=9, color=BRAND_PRIMARY, bold=True)

    # Right insight panel
    pn_x = chart_x + chart_w + gap
    pn_y = body_top
    add_rect(slide, "right-panel", pn_x, pn_y, panel_w, body_h, BRAND_PRIMARY)
    add_text(slide, "panel-label", "KEY INSIGHTS",
             x_px=pn_x + 18, y_px=pn_y + 18, w_px=panel_w - 36, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             letter_spacing_px=1.4, uppercase=True)
    add_text(slide, "panel-headline",
             "Digital adoption accelerated while legacy dependencies contracted.",
             x_px=pn_x + 18, y_px=pn_y + 40, w_px=panel_w - 36, h_px=60,
             font_size_px=14, color=WHITE, bold=True)

    bullets = [
        ("Five capabilities gained 24–36 pts", " in two years — led by Digital (+36) and Cloud (+19). Concentrated investment in targeted sprints is paying off at scale."),
        ("Three legacy areas declined by 13–40 pts", " — Paper-based processes fell most sharply (−40). Decommission runway must be accelerated before capability gaps widen."),
    ]
    bul_top = pn_y + 116
    bul_area_h = body_h - 150
    item_h = bul_area_h // len(bullets)
    for i, (head, tail) in enumerate(bullets):
        iy = bul_top + i * item_h
        add_text(slide, f"bullet-{i+1}-marker", "■",
                 x_px=pn_x + 18, y_px=iy, w_px=12, h_px=14,
                 font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"bullet-{i+1}", f"<strong>{head}</strong>{tail}",
                 x_px=pn_x + 34, y_px=iy - 2, w_px=panel_w - 52, h_px=item_h - 6,
                 font_size_px=11, color=WHITE, emphasis_color=WHITE)

    add_footer(slide, page_num=263)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "263_slope-chart-before-after.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
