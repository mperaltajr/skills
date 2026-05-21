"""
Builder for pattern 16: Process phases rich — 4 sequential cards with exit criteria.

Source HTML: _pattern-library/16_process-phases-rich.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_FAINT,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Four phases — each with a clear exit criterion before moving on.",
        subtitle="Sequential by design. No phase advances on optimism; each gate is a discrete sign-off.",
        title_h=68,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # 4 phase cards, gap 14, height 320
    grid_left = 56
    gap = 14
    card_w = (1280 - 112 - 3 * gap) // 4
    cards_top = 230
    card_h = 320

    phase_data = [
        ("01", "Phase 1", "DISCOVER",
         "• Stakeholder interviews across business units\n"
         "• Current-state process mapping\n"
         "• Pain point inventory and root-cause clustering",
         "Alignment doc signed by all sponsors",
         "Lead: PM", "W1–W2"),
        ("02", "Phase 2", "DESIGN",
         "• Solution options framing (3–4 candidates)\n"
         "• Trade-off analysis on cost, risk, speed\n"
         "• Recommendation memo with rationale",
         "Option selected by steering committee",
         "Lead: Strategy", "W3–W5"),
        ("03", "Phase 3", "BUILD",
         "• Pilot implementation in scoped wave-1 unit\n"
         "• Training rollout and change comms\n"
         "• Measurement framework instrumented",
         "Pilot live with baseline metrics flowing",
         "Lead: Eng + Strategy", "W6–W9"),
        ("04", "Phase 4", "SCALE",
         "• Rollout to wave-2 units on staged cadence\n"
         "• Sustained measurement against targets\n"
         "• Governance handoff to line operations",
         "BAU operations with owner accountable",
         "Lead: PMO", "W10–W12"),
    ]
    for i, (num, eyebrow, name, body, exit_text, meta_l, meta_r) in enumerate(phase_data):
        n = i + 1
        cx = grid_left + i * (card_w + gap)
        cy = cards_top
        # Card body
        card = add_rect(slide, f"step-{n}-bg", cx, cy, card_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # 3px accent top
        add_rect(slide, f"step-{n}-accent", cx, cy, card_w, 3, BRAND_ACCENT)

        # Head
        add_text(
            slide, f"step-{n}-num", num,
            x_px=cx + 18, y_px=cy + 14, w_px=60, h_px=44,
            font_size_px=40, color=BRAND_ACCENT, bold=True,
        )
        add_text(
            slide, f"step-{n}-eyebrow", eyebrow.upper(),
            x_px=cx + 90, y_px=cy + 16, w_px=card_w - 106, h_px=12,
            font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"step-{n}-name", name,
            x_px=cx + 90, y_px=cy + 30, w_px=card_w - 106, h_px=22,
            font_size_px=17, color=BRAND_PRIMARY, bold=True,
        )

        # Body bullets
        add_text(
            slide, f"step-{n}-body", body,
            x_px=cx + 18, y_px=cy + 78, w_px=card_w - 36, h_px=130,
            font_size_px=12, color=TEXT_DARK,
        )

        # Exit criterion section (dashed separator above)
        exit_y = cy + 220
        add_rect(slide, f"step-{n}-exit-sep", x_px=cx + 18, y_px=exit_y - 4, w_px=card_w - 36, h_px=1,
                 fill_color=CARD_BORDER)
        add_text(
            slide, f"step-{n}-exit-label", "EXIT CRITERION",
            x_px=cx + 18, y_px=exit_y, w_px=card_w - 36, h_px=12,
            font_size_px=9, color=BRAND_ACCENT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"step-{n}-exit-text", exit_text,
            x_px=cx + 18, y_px=exit_y + 14, w_px=card_w - 36, h_px=36,
            font_size_px=11, color=BRAND_PRIMARY, bold=True,
        )

        # Meta footer
        meta_y = cy + card_h - 22
        add_text(
            slide, f"step-{n}-meta-left", meta_l,
            x_px=cx + 18, y_px=meta_y, w_px=(card_w - 36) // 2, h_px=14,
            font_size_px=10, color=TEXT_FAINT, italic=True,
        )
        add_text(
            slide, f"step-{n}-meta-right", meta_r,
            x_px=cx + card_w // 2, y_px=meta_y, w_px=card_w // 2 - 18, h_px=14,
            font_size_px=10, color=TEXT_FAINT, italic=True, align="right",
        )

    add_convergence(
        slide,
        "No phase advances without its exit criterion. That's the discipline.",
    )

    add_footer(slide, page_num=16)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "16_process-phases-rich.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
