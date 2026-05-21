"""
Builder for pattern 49: Convergence paths to outcome — two lanes feeding outcome.

SVG-driven (picture-asset per SHAPE-ROLES) — single chart-canvas placeholder
for the joiner SVG; lane nodes + outcome are rendered as native shapes since
text is addressable.

Source HTML: _pattern-library/49_convergence-paths-to-outcome.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

CHART_PLACEHOLDER_FILL = RGBColor(0xFB, 0xF8, 0xFE)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Two parallel paths feed one outcome — together they produce influence plus credibility.",
        subtitle="Each lane runs independently from source to result. Both lines converge at the right-edge outcome — either alone gets you halfway.",
        title_h=64,
        subtitle_h=22,
        brand_rule_w=48,
    )

    # River canvas: top=190, left=56, right=56, height=360
    river_left = 56
    river_top = 190
    river_w = 1280 - 112  # 1168
    river_h = 360

    # Chart-canvas placeholder for SVG joiner lines
    add_rect(slide, "chart-canvas", river_left, river_top, river_w, river_h, CHART_PLACEHOLDER_FILL)

    # Lane geometry: lane stops 240px short of right edge for outcome column
    lane_right = river_left + river_w - 240
    tag_w = 110
    nodes_left = river_left + tag_w + 12
    node_count = 3
    chev_w = 14
    node_total_w = lane_right - nodes_left - 2 * chev_w
    node_w = (node_total_w - 2 * 12) // 3  # 2 inner gaps of 12

    lane_h = 150
    lane_top_y = river_top
    lane_bot_y = river_top + river_h - lane_h  # 210

    lane_data = [
        ("lane-1", lane_top_y, "Prong 1", "Mindset shift", BRAND_PRIMARY, [
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

        # Tag block on left
        add_text(
            slide, f"lane-{lane_idx}-tag", tag_main.upper(),
            x_px=river_left, y_px=ly + 50, w_px=tag_w, h_px=14,
            font_size_px=11, color=accent, bold=True, uppercase=True,
        )
        add_text(
            slide, f"lane-{lane_idx}-tag-sub", tag_sub,
            x_px=river_left, y_px=ly + 66, w_px=tag_w, h_px=14,
            font_size_px=11, color=TEXT_DARK, bold=True,
        )

        for ni, (n_name, n_desc, is_start) in enumerate(nodes):
            n = ni + 1
            nx = nodes_left + ni * (node_w + 12 + chev_w)
            ny = ly + 27  # center node ~96 tall in 150 lane
            nh = 96

            if is_start:
                node = add_rect(slide, f"lane-{lane_idx}-node-{n}", nx, ny, node_w, nh, accent)
                name_color = WHITE
                desc_color = WHITE
            else:
                node = add_rect(slide, f"lane-{lane_idx}-node-{n}", nx, ny, node_w, nh, CARD_BG)
                node.line.color.rgb = CARD_BORDER
                node.line.width = 9525
                name_color = accent
                desc_color = TEXT_MID

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

            # Chevron between nodes
            if ni < node_count - 1:
                add_text(
                    slide, f"lane-{lane_idx}-chev-{n}", "›",
                    x_px=nx + node_w + 4, y_px=ny + nh // 2 - 12, w_px=chev_w + 4, h_px=24,
                    font_size_px=22, color=accent, bold=True, align="center",
                )

    # Outcome column on right
    out_x = river_left + river_w - 220
    out_y = river_top
    out_w = 220
    out_h = river_h
    add_rect(slide, "outcome", out_x, out_y, out_w, out_h, BRAND_PRIMARY)
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

    add_convergence(
        slide,
        "Without both prongs we leave value on the table — where we are today.",
    )

    add_footer(slide, page_num=49)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "49_convergence-paths-to-outcome.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
