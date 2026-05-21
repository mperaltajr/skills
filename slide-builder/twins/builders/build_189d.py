"""
Builder for pattern 189d: Porter's Value Chain Analysis — DARK variant.

Light source: twins/builders/build_189.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Porter's Value Chain reveals where you <strong>create</strong> and where you <strong>erode</strong> margin",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=28, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Map primary and support activities to identify competitive advantage and cost drivers",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    fw_top = 220
    fw_bot = 620
    fw_left = 64
    fw_right = 1280 - 64
    fw_w = fw_right - fw_left

    canvas = add_rect(slide, "chart-canvas", fw_left, fw_top, fw_w, fw_bot - fw_top, CARD_BG_DARK)
    canvas.line.color.rgb = CARD_BORDER_DARK
    canvas.line.width = 9525

    add_text(slide, "vc-framework-label", "Porter's Value Chain",
             x_px=fw_left + 8, y_px=fw_top + 8, w_px=200, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)

    grid_left = fw_left + 40
    grid_w = fw_w - 40 - 80

    add_text(slide, "vc-support-label", "SUPPORT ACTIVITIES",
             x_px=grid_left, y_px=fw_top + 24, w_px=200, h_px=14,
             font_size_px=8, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True)

    support_data = [
        ("Firm Infrastructure", "Finance & accounting · Legal, compliance & governance"),
        ("Human Resource Mgmt", "Talent acquisition & retention · Training & performance systems"),
        ("Technology Development", "R&D and process automation · IT infrastructure & data platforms"),
        ("Procurement", "Supplier selection & negotiation · Strategic vendor partnerships"),
    ]
    # In dark mode, ramp from lighter to darker accent bands for visibility
    support_colors = [
        RGBColor(0x55, 0x36, 0x77),
        RGBColor(0x6E, 0x3D, 0x9A),
        RGBColor(0x8B, 0x5C, 0xC4),
        RGBColor(0xA8, 0x76, 0xD8),
    ]
    sup_top = fw_top + 44
    sup_h = 32
    for i, ((name, items), band) in enumerate(zip(support_data, support_colors)):
        n = i + 1
        by = sup_top + i * (sup_h + 3)
        add_rect(slide, f"vc-support-{n}-bar", grid_left, by, grid_w, sup_h, band)
        add_text(slide, f"vc-support-{n}-name", name,
                 x_px=grid_left + 12, y_px=by + 6, w_px=200, h_px=22,
                 font_size_px=10, color=WHITE, bold=True)
        add_text(slide, f"vc-support-{n}-items", items,
                 x_px=grid_left + 220, y_px=by + 6, w_px=grid_w - 240, h_px=22,
                 font_size_px=9, color=RGBColor(0xE6, 0xDC, 0xFF))

    div_y = sup_top + 4 * (sup_h + 3) + 6
    add_rect(slide, "vc-divider", grid_left, div_y, grid_w, 1, CARD_BORDER_DARK)

    pri_top = div_y + 8
    pri_h = fw_bot - pri_top - 8
    add_text(slide, "vc-primary-label", "PRIMARY ACTIVITIES",
             x_px=grid_left, y_px=pri_top, w_px=200, h_px=14,
             font_size_px=8, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True)
    pri_seg_top = pri_top + 20
    pri_seg_h = pri_h - 20
    seg_w = grid_w // 5
    primary_data = [
        ("Inbound Logistics", ["Receiving & warehousing", "Inventory control"]),
        ("Operations", ["Manufacturing & assembly", "Quality management"]),
        ("Outbound Logistics", ["Order fulfillment", "Distribution & delivery"]),
        ("Marketing & Sales", ["Pricing & promotion", "Channel management"]),
        ("Service", ["After-sales support", "Repair & warranty"]),
    ]
    primary_colors = [
        RGBColor(0x55, 0x36, 0x77),
        RGBColor(0x6E, 0x3D, 0x9A),
        RGBColor(0x8B, 0x5C, 0xC4),
        RGBColor(0xA8, 0x76, 0xD8),
        RGBColor(0xC7, 0x80, 0xFF),
    ]
    for i, ((name, bullets), band) in enumerate(zip(primary_data, primary_colors)):
        n = i + 1
        sx = grid_left + i * seg_w
        add_rect(slide, f"vc-primary-{n}-seg", sx, pri_seg_top, seg_w - 2, pri_seg_h, band)
        add_text(slide, f"vc-primary-{n}-name", name,
                 x_px=sx + 14, y_px=pri_seg_top + 12, w_px=seg_w - 28, h_px=20,
                 font_size_px=11, color=WHITE, bold=True)
        for j, b in enumerate(bullets):
            add_text(slide, f"vc-primary-{n}-bullets" if j == 0 else f"vc-primary-{n}-bullet-{j+1}",
                     "· " + b,
                     x_px=sx + 14, y_px=pri_seg_top + 38 + j * 16,
                     w_px=seg_w - 28, h_px=16,
                     font_size_px=9, color=RGBColor(0xE6, 0xDC, 0xFF))

    mg_x = grid_left + grid_w + 6
    add_rect(slide, "vc-margin-box", mg_x, pri_seg_top, 70, pri_seg_h, BRAND_ACCENT)
    add_text(slide, "vc-margin", "MARGIN",
             x_px=mg_x, y_px=pri_seg_top, w_px=70, h_px=pri_seg_h,
             font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle",
             uppercase=True)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "189",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "189d_value-chain-analysis-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
