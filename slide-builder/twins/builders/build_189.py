"""
Builder for pattern 189: Porter's Value Chain Analysis.

Picture-asset chart-canvas placeholder + native text overlays for support bars,
primary arrow segments, and Margin box (pattern-local vc-* IDs).

Source HTML: _pattern-library/189_value-chain-analysis.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Porter's Value Chain reveals where you <strong>create</strong> and where you <strong>erode</strong> margin",
        subtitle="Map primary and support activities to identify competitive advantage and cost drivers",
        title_h=60, subtitle_h=20, brand_rule_w=64,
    )

    # Framework area: top:170, bottom:600
    fw_top = 170
    fw_bot = 600
    fw_left = 64
    fw_right = 1280 - 64
    fw_w = fw_right - fw_left

    # Chart canvas placeholder for the whole framework
    canvas = add_rect(slide, "chart-canvas", fw_left, fw_top, fw_w, fw_bot - fw_top, CARD_BG)
    canvas.line.color.rgb = CARD_BORDER
    canvas.line.width = 9525

    # Rotated label on left
    add_text(slide, "vc-framework-label", "Porter's Value Chain",
             x_px=fw_left + 8, y_px=fw_top + 80, w_px=150, h_px=20,
             font_size_px=9, color=BRAND_PRIMARY, bold=True, uppercase=True)

    # Support Activities section (top half)
    grid_left = fw_left + 40
    grid_w = fw_w - 40 - 80  # leave room for margin box

    add_text(slide, "vc-support-label", "SUPPORT ACTIVITIES",
             x_px=grid_left, y_px=fw_top + 10, w_px=200, h_px=14,
             font_size_px=8, color=TEXT_FAINT, bold=True, uppercase=True)

    support_data = [
        ("Firm Infrastructure", "Finance & accounting · Legal, compliance & governance"),
        ("Human Resource Mgmt", "Talent acquisition & retention · Training & performance systems"),
        ("Technology Development", "R&D and process automation · IT infrastructure & data platforms"),
        ("Procurement", "Supplier selection & negotiation · Strategic vendor partnerships"),
    ]
    support_colors = [
        RGBColor(0x2D, 0x0A, 0x4E),
        RGBColor(0x3D, 0x12, 0x66),
        RGBColor(0x5C, 0x2D, 0x87),
        RGBColor(0x7A, 0x46, 0xA8),
    ]
    sup_top = fw_top + 30
    sup_h = 38
    for i, ((name, items), bg) in enumerate(zip(support_data, support_colors)):
        n = i + 1
        by = sup_top + i * (sup_h + 3)
        add_rect(slide, f"vc-support-{n}-bar", grid_left, by, grid_w, sup_h, bg)
        add_text(slide, f"vc-support-{n}-name", name,
                 x_px=grid_left + 12, y_px=by + 8, w_px=200, h_px=22,
                 font_size_px=10, color=WHITE, bold=True)
        add_text(slide, f"vc-support-{n}-items", items,
                 x_px=grid_left + 220, y_px=by + 8, w_px=grid_w - 240, h_px=22,
                 font_size_px=9, color=RGBColor(0xD8, 0xC0, 0xE0))

    # Divider line
    div_y = sup_top + 4 * (sup_h + 3) + 6
    add_rect(slide, "vc-divider", grid_left, div_y, grid_w, 1, CARD_BORDER)

    # Primary activities
    pri_top = div_y + 8
    pri_h = fw_bot - pri_top - 8
    add_text(slide, "vc-primary-label", "PRIMARY ACTIVITIES",
             x_px=grid_left, y_px=pri_top, w_px=200, h_px=14,
             font_size_px=8, color=TEXT_FAINT, bold=True, uppercase=True)
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
        RGBColor(0x2D, 0x0A, 0x4E),
        RGBColor(0x3D, 0x12, 0x66),
        RGBColor(0x4A, 0x1D, 0x78),
        RGBColor(0x5C, 0x2D, 0x87),
        RGBColor(0x6E, 0x3D, 0x9A),
    ]
    for i, ((name, bullets), bg) in enumerate(zip(primary_data, primary_colors)):
        n = i + 1
        sx = grid_left + i * seg_w
        add_rect(slide, f"vc-primary-{n}-seg", sx, pri_seg_top, seg_w - 2, pri_seg_h, bg)
        add_text(slide, f"vc-primary-{n}-name", name,
                 x_px=sx + 14, y_px=pri_seg_top + 12, w_px=seg_w - 28, h_px=20,
                 font_size_px=11, color=WHITE, bold=True)
        for j, b in enumerate(bullets):
            add_text(slide, f"vc-primary-{n}-bullets" if j == 0 else f"vc-primary-{n}-bullet-{j+1}",
                     "· " + b,
                     x_px=sx + 14, y_px=pri_seg_top + 38 + j * 16,
                     w_px=seg_w - 28, h_px=16,
                     font_size_px=9, color=RGBColor(0xCF, 0xBC, 0xE3))

    # Margin box (right side, full height of primary section)
    mg_x = grid_left + grid_w + 6
    add_rect(slide, "vc-margin-box", mg_x, pri_seg_top, 70, pri_seg_h, BRAND_ACCENT)
    add_text(slide, "vc-margin", "MARGIN",
             x_px=mg_x, y_px=pri_seg_top, w_px=70, h_px=pri_seg_h,
             font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle",
             uppercase=True)

    add_footer(slide, page_num=189)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "189_value-chain-analysis.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
