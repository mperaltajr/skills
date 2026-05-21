"""
Builder for pattern 49d: Convergence paths to outcome (dark variant).

Source HTML: _pattern-library/49_convergence-paths-to-outcome-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

# Dark color tokens
TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
CHART_PLACEHOLDER_FILL = RGBColor(0x3C, 0x1F, 0x5C)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # --- Canonical chrome ---
    add_text(
        slide, "title",
        "Two parallel paths feed one outcome — together they produce influence plus credibility.",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Each lane runs independently from source to result. Both lines converge at the right-edge outcome.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    # River canvas
    river_left = 56
    river_top = 220
    river_w = 1280 - 112
    river_h = 340

    add_rect(slide, "chart-canvas", river_left, river_top, river_w, river_h, CHART_PLACEHOLDER_FILL)

    lane_right = river_left + river_w - 240
    tag_w = 110
    nodes_left = river_left + tag_w + 12
    node_count = 3
    chev_w = 14
    node_total_w = lane_right - nodes_left - 2 * chev_w
    node_w = (node_total_w - 2 * 12) // 3

    lane_h = 140
    lane_top_y = river_top + 10
    lane_bot_y = river_top + river_h - lane_h - 10

    lane_data = [
        ("lane-1", lane_top_y, "Prong 1", "Mindset shift", BRAND_ACCENT_SOFT, [
            ("Mindset shift", "How we think and operate.", True),
            ("Trusted relationships", "Teams frame problems and engage at the right level.", False),
            ("Influence", "We shape decisions before they are made.", False),
        ]),
        ("lane-2", lane_bot_y, "Prong 2", "Ops engine", BRAND_ACCENT, [
            ("Ops intelligence engine", "What we know and deliver.", True),
            ("Insights", "Grounded in how the business actually makes money.", False),
            ("Credibility", "Teams identify, quantify, and capture value.", False),
        ]),
    ]

    for lane_id, ly, tag_main, tag_sub, accent, nodes in lane_data:
        lane_idx = int(lane_id.split("-")[1])

        add_text(
            slide, f"lane-{lane_idx}-tag", tag_main.upper(),
            x_px=river_left, y_px=ly + 50, w_px=tag_w, h_px=14,
            font_size_px=11, color=accent, bold=True, uppercase=True,
        )
        add_text(
            slide, f"lane-{lane_idx}-tag-sub", tag_sub,
            x_px=river_left, y_px=ly + 66, w_px=tag_w, h_px=14,
            font_size_px=11, color=WHITE, bold=True,
        )

        for ni, (n_name, n_desc, is_start) in enumerate(nodes):
            n = ni + 1
            nx = nodes_left + ni * (node_w + 12 + chev_w)
            ny = ly + 22
            nh = 96

            if is_start:
                node = add_rect(slide, f"lane-{lane_idx}-node-{n}", nx, ny, node_w, nh, accent)
                name_color = BRAND_PRIMARY
                desc_color = BRAND_PRIMARY
            else:
                node = add_rect(slide, f"lane-{lane_idx}-node-{n}", nx, ny, node_w, nh, CARD_BG_DARK)
                node.line.color.rgb = CARD_BORDER_DARK
                node.line.width = 9525
                name_color = accent
                desc_color = TEXT_ON_DARK_MID

            add_text(
                slide, f"lane-{lane_idx}-node-{n}-name", n_name,
                x_px=nx + 12, y_px=ny + 18, w_px=node_w - 24, h_px=18,
                font_size_px=12, color=name_color, bold=True,
            )
            add_text(
                slide, f"lane-{lane_idx}-node-{n}-desc", n_desc,
                x_px=nx + 12, y_px=ny + 38, w_px=node_w - 24, h_px=52,
                font_size_px=10, color=desc_color,
            )

            if ni < node_count - 1:
                add_text(
                    slide, f"lane-{lane_idx}-chev-{n}", "›",
                    x_px=nx + node_w + 4, y_px=ny + nh // 2 - 12, w_px=chev_w + 4, h_px=24,
                    font_size_px=22, color=accent, bold=True, align="center",
                )

    out_x = river_left + river_w - 220
    out_y = river_top
    out_w = 220
    out_h = river_h
    add_rect(slide, "outcome", out_x, out_y, out_w, out_h, CARD_BG_DARK)
    add_rect(slide, "outcome-accent", out_x, out_y, 4, out_h, BRAND_ACCENT_SOFT)

    # Convergence arrows: each lane's last node tip → outcome card left edge.
    last_node_right = nodes_left + 3 * (node_w + 12 + chev_w) - chev_w - 12
    for lane_id, ly, *_ in lane_data:
        lane_idx = int(lane_id.split("-")[1])
        arrow_y = ly + 22 + 96 // 2  # center of last node vertically
        head_color = BRAND_ACCENT_SOFT if lane_idx == 1 else BRAND_ACCENT
        add_rect(slide, f"lane-{lane_idx}-converge-line",
                 last_node_right, arrow_y, out_x - last_node_right - 6, 2,
                 head_color)
        add_rect(slide, f"lane-{lane_idx}-converge-head",
                 out_x - 8, arrow_y - 3, 6, 8, head_color)
    add_text(
        slide, "outcome-label", "TOGETHER",
        x_px=out_x + 20, y_px=out_y + 110, w_px=out_w - 40, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "outcome-name", "New and expanded opportunities",
        x_px=out_x + 20, y_px=out_y + 130, w_px=out_w - 40, h_px=64,
        font_size_px=18, color=WHITE, bold=True,
    )
    add_text(
        slide, "outcome-body",
        "Influence + credibility drive new work won and expansion of existing engagements — durable, structural success.",
        x_px=out_x + 20, y_px=out_y + 198, w_px=out_w - 40, h_px=100,
        font_size_px=11, color=WHITE,
    )

    # Convergence (text on dark)
    add_text(
        slide, "convergence",
        "Without both prongs we leave value on the table — where we are today.",
        x_px=64, y_px=720 - 78 - 30, w_px=1280 - 128, h_px=30,
        font_size_px=13, color=TEXT_ON_DARK_MID, italic=True,
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "49",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "49d_convergence-paths-to-outcome.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
