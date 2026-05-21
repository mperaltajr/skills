"""
Builder for pattern 281: Swimlane milestone timeline (dark).

12-month timeline with 4 swimlanes, milestone diamonds, TODAY marker.
Legend MOVED from chart-top-right to BELOW subheadline per mandatory rule.

Source HTML: _pattern-library/281_swimlane-milestone-dark.html
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
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Emu

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BORDER = RGBColor(0x55, 0x36, 0x77)
LANE_BAR_PURPLE = RGBColor(0x6D, 0x3D, 0xA5)
LANE_BAR_LIGHT = RGBColor(0x52, 0x2A, 0x82)
LANE_BAR_GRAY = RGBColor(0x55, 0x44, 0x6E)
LANE_BAR_GREEN = RGBColor(0x35, 0x80, 0x55)


def px_to_emu(px):
    return Emu(int(px * 9525))


def add_diamond(slide, name, cx, cy, size, color):
    """Add a diamond shape centered at (cx, cy)."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.DIAMOND,
        px_to_emu(cx - size // 2), px_to_emu(cy - size // 2),
        px_to_emu(size), px_to_emu(size),
    )
    shape.name = name
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Title — canonical chrome
    add_text(slide, "title",
             "2026 Program Roadmap — <strong>four workstreams, one delivery timeline</strong>.",
             x_px=40, y_px=20, w_px=1200, h_px=80,
             font_size_px=20, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "12-month delivery view across strategy, build, change, and deployment lanes",
             x_px=40, y_px=108, w_px=1200, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 40, 132, 80, 3, BRAND_ACCENT_SOFT)

    # Legend BELOW subhead, right-aligned
    leg_y = 230
    leg_items = [
        ("Milestone", "diamond", BRAND_ACCENT),
        ("In Progress", "bar", LANE_BAR_PURPLE),
        ("Planned", "bar", LANE_BAR_GRAY),
    ]
    leg_widths = [110, 110, 100]
    leg_total = sum(leg_widths) + 24
    cx = 1240 - leg_total
    for i, (lbl, kind, col) in enumerate(leg_items):
        if kind == "diamond":
            add_diamond(slide, f"legend-{i+1}-swatch", cx + 6, leg_y + 9, 11, col)
        else:
            add_rect(slide, f"legend-{i+1}-swatch", cx, leg_y + 5, 20, 9, col)
        add_text(slide, f"legend-{i+1}-label", lbl,
                 x_px=cx + 26, y_px=leg_y, w_px=leg_widths[i] - 26, h_px=18,
                 font_size_px=10, color=TEXT_ON_DARK_MID)
        cx += leg_widths[i] + 6

    # Timeline body
    body_top = 270
    body_bot = 670
    label_w = 100
    chart_x = 40
    chart_w = 1240 - chart_x
    body_h = body_bot - body_top

    # Header row (month labels)
    hdr_h = 28
    add_rect(slide, "header-bg", chart_x, body_top, chart_w, hdr_h,
             RGBColor(0x4A, 0x2A, 0x6D))
    add_text(slide, "header-workstream-label", "WORKSTREAM",
             x_px=chart_x + 8, y_px=body_top + 6, w_px=label_w - 8, h_px=18,
             font_size_px=8, color=TEXT_ON_DARK_FAINT, bold=True,
             letter_spacing_px=1.5, anchor="middle")

    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    grid_left = chart_x + label_w
    grid_w = chart_w - label_w
    col_w = grid_w / 12.0
    for i, m in enumerate(months):
        mx = grid_left + int(i * col_w)
        is_may = (i == 4)
        col = WHITE if is_may else TEXT_ON_DARK_MID
        # Alternating column shading
        if i % 2 == 1:
            add_rect(slide, f"col-shade-{i}", mx, body_top + hdr_h, int(col_w), body_h - hdr_h,
                     RGBColor(0x33, 0x14, 0x57))
        add_text(slide, f"month-{m.lower()}", m,
                 x_px=mx, y_px=body_top + 6, w_px=int(col_w), h_px=18,
                 font_size_px=9, color=col, bold=True, align="center",
                 anchor="middle", letter_spacing_px=1)

    # Lane rows (4 lanes)
    lanes_top = body_top + hdr_h
    lanes_h = body_h - hdr_h
    lane_h = lanes_h // 4
    lane_labels = [
        ("STRATEGY", "& DESIGN"),
        ("TECHNOLOGY", "BUILD"),
        ("CHANGE", "MGMT"),
        ("DEPLOYMENT", ""),
    ]
    # Lane separators
    for i in range(5):
        sy = lanes_top + i * lane_h
        add_rect(slide, f"sep-{i}", chart_x, sy, chart_w, 1, CARD_BORDER)
    # Vertical separator after label col
    add_rect(slide, "label-col-sep", grid_left, lanes_top, 1, lanes_h, CARD_BORDER)

    for i, (l1, l2) in enumerate(lane_labels):
        ly = lanes_top + i * lane_h
        add_text(slide, f"lane-{i+1}-label-1", l1,
                 x_px=chart_x + 8, y_px=ly + lane_h // 2 - 14, w_px=label_w - 12, h_px=14,
                 font_size_px=9, color=WHITE, bold=True, letter_spacing_px=0.5)
        if l2:
            add_text(slide, f"lane-{i+1}-label-2", l2,
                     x_px=chart_x + 8, y_px=ly + lane_h // 2, w_px=label_w - 12, h_px=14,
                     font_size_px=9, color=WHITE, bold=True, letter_spacing_px=0.5)

    # Helper to convert month index to x
    def mx(month_idx):
        """0=Jan start, 12=Dec end"""
        return grid_left + int(month_idx * col_w)

    bar_h = 22

    # Lane 1: Discovery (Jan-Mar), Design Sprint (Apr-mid May), milestone end of May
    ly = lanes_top + 0 * lane_h + (lane_h - bar_h) // 2
    add_rect(slide, "lane-1-bar-a", mx(0.05), ly, mx(3) - mx(0.05), bar_h, LANE_BAR_LIGHT)
    add_text(slide, "lane-1-bar-a-label", "Discovery",
             x_px=mx(0.05) + 8, y_px=ly, w_px=mx(3) - mx(0.05) - 16, h_px=bar_h,
             font_size_px=9, color=WHITE, bold=True, anchor="middle")
    add_rect(slide, "lane-1-bar-b", mx(3.05), ly, mx(5) - mx(3.05), bar_h, LANE_BAR_PURPLE)
    add_text(slide, "lane-1-bar-b-label", "Design Sprint",
             x_px=mx(3.05) + 8, y_px=ly, w_px=mx(5) - mx(3.05) - 16, h_px=bar_h,
             font_size_px=9, color=WHITE, bold=True, anchor="middle")
    # Milestone end of May
    m1x = mx(5)
    m1y = ly + bar_h // 2
    add_diamond(slide, "milestone-1-diamond", m1x, m1y, 16, BRAND_ACCENT)
    add_text(slide, "milestone-1-label", "Design Approved",
             x_px=m1x - 60, y_px=m1y + 14, w_px=120, h_px=14,
             font_size_px=8, color=WHITE, bold=True, align="center")

    # Lane 2: Platform Development (Mar-Jul), milestone end Jul
    ly = lanes_top + 1 * lane_h + (lane_h - bar_h) // 2
    add_rect(slide, "lane-2-bar", mx(2.05), ly, mx(7) - mx(2.05), bar_h, LANE_BAR_LIGHT)
    add_text(slide, "lane-2-bar-label", "Platform Development",
             x_px=mx(2.05) + 8, y_px=ly, w_px=mx(7) - mx(2.05) - 16, h_px=bar_h,
             font_size_px=9, color=WHITE, bold=True, anchor="middle")
    m2x = mx(7)
    m2y = ly + bar_h // 2
    add_diamond(slide, "milestone-2-diamond", m2x, m2y, 16, BRAND_ACCENT)
    add_text(slide, "milestone-2-label", "MVP Ready",
             x_px=m2x - 60, y_px=m2y + 14, w_px=120, h_px=14,
             font_size_px=8, color=WHITE, bold=True, align="center")

    # Lane 3: Change Mgmt (Feb-Sep), milestone end Sep
    ly = lanes_top + 2 * lane_h + (lane_h - bar_h) // 2
    add_rect(slide, "lane-3-bar", mx(1.05), ly, mx(9) - mx(1.05), bar_h, LANE_BAR_GRAY)
    add_text(slide, "lane-3-bar-label", "Stakeholder Engagement & Training Design",
             x_px=mx(1.05) + 8, y_px=ly, w_px=mx(9) - mx(1.05) - 16, h_px=bar_h,
             font_size_px=9, color=WHITE, bold=True, anchor="middle")
    m3x = mx(9)
    m3y = ly + bar_h // 2
    add_diamond(slide, "milestone-3-diamond", m3x, m3y, 16, BRAND_ACCENT)
    add_text(slide, "milestone-3-label", "Training Complete",
             x_px=m3x - 60, y_px=m3y + 14, w_px=120, h_px=14,
             font_size_px=8, color=WHITE, bold=True, align="center")

    # Lane 4: Deployment (Aug-Nov), milestone end Nov
    ly = lanes_top + 3 * lane_h + (lane_h - bar_h) // 2
    add_rect(slide, "lane-4-bar", mx(7.05), ly, mx(11) - mx(7.05), bar_h, LANE_BAR_GREEN)
    add_text(slide, "lane-4-bar-label", "Phased Rollout",
             x_px=mx(7.05) + 8, y_px=ly, w_px=mx(11) - mx(7.05) - 16, h_px=bar_h,
             font_size_px=9, color=WHITE, bold=True, anchor="middle")
    m4x = mx(11)
    m4y = ly + bar_h // 2
    add_diamond(slide, "milestone-4-diamond", m4x, m4y, 16, BRAND_ACCENT)
    add_text(slide, "milestone-4-label", "Go-Live",
             x_px=m4x - 60, y_px=m4y + 14, w_px=120, h_px=14,
             font_size_px=8, color=WHITE, bold=True, align="center")

    # TODAY marker at mid-May (x = mx(4.5))
    today_x = mx(4.5)
    add_rect(slide, "today-line", today_x, lanes_top, 2, lanes_h,
             RGBColor(0xC7, 0x80, 0xFF))
    add_rect(slide, "today-pill", today_x - 22, body_top + 2, 44, 14, BRAND_ACCENT)
    add_text(slide, "today-label", "TODAY",
             x_px=today_x - 22, y_px=body_top + 2, w_px=44, h_px=14,
             font_size_px=8, color=WHITE, bold=True, align="center",
             anchor="middle", letter_spacing_px=1)

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "281",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "281_swimlane-milestone-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
