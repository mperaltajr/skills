"""
Builder for pattern 231: Input → Transform → Output (3-column process model).

Source HTML: _pattern-library/231_input-transform-output.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="How we turn raw inputs into <strong>measurable outcomes</strong>",
        subtitle="A structured transformation model — from data and constraints to value delivery",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Content: top:138, left:48, right:48 (w=1184), bottom 64
    body_top = 138
    body_h = 518
    # Layout: inputs(258) + arrow(52) + transform(flex) + arrow(52) + outputs(258)
    inp_w = 258
    arrow_w = 52
    out_w = 258
    transform_w = 1184 - inp_w - out_w - 2 * arrow_w
    inputs_x = 48
    arrow1_x = inputs_x + inp_w
    transform_x = arrow1_x + arrow_w
    arrow2_x = transform_x + transform_w
    outputs_x = arrow2_x + arrow_w

    # Column labels
    add_text(slide, "inputs-header", "INPUTS",
             x_px=inputs_x, y_px=body_top, w_px=inp_w, h_px=16,
             font_size_px=10, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_text(slide, "outputs-header", "OUTCOMES",
             x_px=outputs_x, y_px=body_top, w_px=out_w, h_px=16,
             font_size_px=10, color=BRAND_PRIMARY, bold=True, uppercase=True)
    # Transform label inside dark panel — drawn after panel

    inputs_data = [
        ("Business Requirements", "Stakeholder priorities & strategic goals"),
        ("Raw Data & Systems", "Existing platforms, data sources, APIs"),
        ("Constraints & Risks", "Budget, timeline, regulatory requirements"),
        ("Team Capabilities", "Skills inventory & resource availability"),
        ("Market Signals", "Customer feedback, competitive intel, demand data"),
    ]
    outputs_data = [
        ("30%+ Cost Reduction", "Operational savings within 12 months"),
        ("Accelerated Time-to-Value", "First results delivered within 8 weeks"),
        ("Scalable Platform", "Architecture ready to grow with demand"),
        ("Empowered Teams", "Self-sufficient capabilities post-engagement"),
        ("Measurable ROI", "Quantified benefits tracked against baseline KPIs"),
    ]
    card_top = body_top + 26
    card_area_h = body_h - 26
    n_cards = len(inputs_data)
    card_h = (card_area_h - (n_cards - 1) * 6) // n_cards

    for i, (label, sub) in enumerate(inputs_data):
        n = i + 1
        cy = card_top + i * (card_h + 6)
        card = add_rect(slide, f"input-{n}-card", inputs_x, cy, inp_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Dot y-center aligned with label first-line center (label at cy+12, h=18 → center at cy+21)
        dot_y = cy + 12 + (18 - 8) // 2  # = cy + 17
        add_rect(slide, f"input-{n}-dot", inputs_x + 14, dot_y, 8, 8, BRAND_ACCENT)
        add_text(slide, f"input-{n}-label", label,
                 x_px=inputs_x + 30, y_px=cy + 12, w_px=inp_w - 40, h_px=18,
                 font_size_px=12, color=TEXT_DARK, bold=True)
        add_text(slide, f"input-{n}-sub", sub,
                 x_px=inputs_x + 30, y_px=cy + 30, w_px=inp_w - 40, h_px=card_h - 36,
                 font_size_px=10, color=TEXT_MID)

    for i, (label, sub) in enumerate(outputs_data):
        n = i + 1
        cy = card_top + i * (card_h + 6)
        card = add_rect(slide, f"output-{n}-card", outputs_x, cy, out_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Dot y-center aligned with label first-line center (label at cy+12, h=18 → center at cy+21)
        dot_y = cy + 12 + (18 - 8) // 2  # = cy + 17
        add_rect(slide, f"output-{n}-dot", outputs_x + 14, dot_y, 8, 8, BRAND_PRIMARY_MID)
        add_text(slide, f"output-{n}-label", label,
                 x_px=outputs_x + 30, y_px=cy + 12, w_px=out_w - 40, h_px=18,
                 font_size_px=12, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"output-{n}-sub", sub,
                 x_px=outputs_x + 30, y_px=cy + 30, w_px=out_w - 40, h_px=card_h - 36,
                 font_size_px=10, color=TEXT_MID)

    # Transform dark panel
    panel_top = body_top
    add_rect(slide, "transform-panel", transform_x, panel_top, transform_w, body_h, BRAND_PRIMARY)
    add_text(slide, "transform-label", "OUR PROCESS",
             x_px=transform_x + 20, y_px=panel_top + 16, w_px=transform_w - 40, h_px=16,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "transform-headline",
             "We apply a proven three-phase methodology to translate inputs into reliable, scalable outcomes — on time and on budget.",
             x_px=transform_x + 20, y_px=panel_top + 36, w_px=transform_w - 40, h_px=60,
             font_size_px=14, color=WHITE, bold=True)
    # Separator
    add_rect(slide, "transform-rule",
             transform_x + 20, panel_top + 104, transform_w - 40, 1, BRAND_ACCENT_SOFT)

    steps = [
        ("Diagnose & Align",
         "Rapid discovery to validate assumptions and surface hidden blockers before work begins"),
        ("Design & Build",
         "Agile delivery sprints with continuous stakeholder checkpoints and risk-adjusted scope"),
        ("Test & Iterate",
         "Pilot rollouts with measurement loops to refine the solution before broad deployment"),
        ("Embed & Scale",
         "Capability transfer, change management, and tooling to sustain gains independently"),
    ]
    step_top = panel_top + 124
    step_area_h = body_h - 124 - 12
    step_h = step_area_h // len(steps)
    for i, (name, desc) in enumerate(steps):
        n = i + 1
        sy = step_top + i * step_h
        add_rect(slide, f"step-{n}-num-bg", transform_x + 20, sy + 4, 22, 22, BRAND_ACCENT)
        add_text(slide, f"step-{n}-num", str(n),
                 x_px=transform_x + 20, y_px=sy + 4, w_px=22, h_px=22,
                 font_size_px=10, color=WHITE, bold=True, align="center", anchor="middle")
        add_text(slide, f"step-{n}-name", name,
                 x_px=transform_x + 50, y_px=sy + 4, w_px=transform_w - 70, h_px=18,
                 font_size_px=12, color=WHITE, bold=True)
        add_text(slide, f"step-{n}-desc", desc,
                 x_px=transform_x + 50, y_px=sy + 22, w_px=transform_w - 70, h_px=60,
                 font_size_px=10, color=BRAND_ACCENT_SOFT)

    # Arrows (large purple → in middle of arrow_w)
    arrow_y = body_top + body_h // 2 - 18
    add_icon(slide, "arrow-1", arrow1_x + arrow_w // 2 - 18, arrow_y, 36, "→", color=BRAND_ACCENT)
    add_icon(slide, "arrow-2", arrow2_x + arrow_w // 2 - 18, arrow_y, 36, "→", color=BRAND_ACCENT)

    add_footer(slide, page_num=231)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "231_input-transform-output.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
