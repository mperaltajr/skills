"""
Builder for pattern 18: Methodology overview — five steps with activities and deliverables.

Source HTML: _pattern-library/18_methodology-overview.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.enum.shapes import MSO_SHAPE


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Our approach — five steps, each with activities and a deliverable.",
        subtitle="Each step ends with an artefact a stakeholder can react to — never an internal-only milestone.",
        title_h=68,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # 5 step cards
    grid_left = 56
    gap = 14
    n_cards = 5
    card_w = (1280 - 112 - (n_cards - 1) * gap) // n_cards
    cards_top = 220
    card_h = 360
    head_h = 130
    activities_h = 110
    deliv_h = card_h - head_h - activities_h

    step_data = [
        ("01", "DISCOVER", "Frame the problem and align stakeholders",
         "• Stakeholder interviews\n• Problem framing\n• Pain point inventory",
         ["Stakeholder map", "Problem statement"]),
        ("02", "DIAGNOSE", "Surface root causes from evidence",
         "• Root cause analysis\n• Data analysis\n• Pattern identification",
         ["Diagnostic memo"]),
        ("03", "DESIGN", "Develop options, trade-offs, recommendation",
         "• Options framing\n• Trade-off analysis\n• Recommendation drafting",
         ["Options memo", "Recommendation deck"]),
        ("04", "PILOT", "Run a measured pilot before scaling",
         "• Pilot scoping\n• Implementation\n• Measurement",
         ["Pilot plan", "Measurement framework"]),
        ("05", "SCALE", "Roll out the validated approach",
         "• Rollout planning\n• Wave 2 prep\n• Governance handoff",
         ["Scorecard", "Governance handoff"]),
    ]
    for i, (num, name, desc, activities, deliverables) in enumerate(step_data):
        n = i + 1
        cx = grid_left + i * (card_w + gap)
        cy = cards_top
        # Card body
        card = add_rect(slide, f"step-{n}-bg", cx, cy, card_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # 3px accent top
        add_rect(slide, f"step-{n}-accent", cx, cy, card_w, 3, BRAND_ACCENT)

        # Step circle (42x42 centered)
        circle_x = cx + card_w // 2 - 21
        circle_y = cy + 16
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            px_to_emu(circle_x), px_to_emu(circle_y),
            px_to_emu(42), px_to_emu(42),
        )
        circle.name = f"step-{n}-num-bg"
        circle.fill.solid()
        circle.fill.fore_color.rgb = BRAND_ACCENT
        circle.line.fill.background()
        add_text(
            slide, f"step-{n}-num", num,
            x_px=circle_x, y_px=circle_y, w_px=42, h_px=42,
            font_size_px=14, color=WHITE, bold=True,
            align="center", anchor="middle",
        )

        # Name
        add_text(
            slide, f"step-{n}-name", name,
            x_px=cx, y_px=cy + 64, w_px=card_w, h_px=20,
            font_size_px=14, color=BRAND_PRIMARY, bold=True,
            align="center", uppercase=True,
        )

        # Desc
        add_text(
            slide, f"step-{n}-desc", desc,
            x_px=cx + 8, y_px=cy + 86, w_px=card_w - 16, h_px=38,
            font_size_px=11, color=TEXT_MID, italic=True, align="center",
        )

        # Activities zone label
        activities_y = cy + head_h
        add_text(
            slide, f"step-{n}-activities-label", "ACTIVITIES",
            x_px=cx + 14, y_px=activities_y + 8, w_px=card_w - 28, h_px=12,
            font_size_px=9, color=BRAND_ACCENT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"step-{n}-body", activities,
            x_px=cx + 14, y_px=activities_y + 22, w_px=card_w - 28, h_px=activities_h - 30,
            font_size_px=11, color=TEXT_DARK,
        )

        # Deliverables zone
        deliv_y = activities_y + activities_h
        add_rect(slide, f"step-{n}-deliv-bg", cx, deliv_y, card_w, deliv_h, WHITE)
        add_text(
            slide, f"step-{n}-deliverables-label", "DELIVERABLES",
            x_px=cx + 14, y_px=deliv_y + 8, w_px=card_w - 28, h_px=12,
            font_size_px=9, color=BRAND_ACCENT, bold=True, uppercase=True,
        )
        for j, dname in enumerate(deliverables):
            dn = j + 1
            dy = deliv_y + 26 + j * 26
            # Icon placeholder (20x20)
            add_rect(slide, f"step-{n}-deliverable-{dn}-icon", cx + 14, dy, 20, 20, CARD_BG)
            # Name
            add_text(
                slide, f"step-{n}-deliverable-{dn}-name", dname,
                x_px=cx + 40, y_px=dy + 2, w_px=card_w - 54, h_px=18,
                font_size_px=11, color=BRAND_PRIMARY, bold=True,
            )

    add_convergence(
        slide,
        "Every step produces something a stakeholder can react to — nothing is internal-only.",
    )

    add_footer(slide, page_num=18)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "18_methodology-overview.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
