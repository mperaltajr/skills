"""
Builder for pattern 16d: Process phases rich — 4 sequential cards — DARK variant.

Light source: twins/builders/build_16.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
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
        "Four phases — each with a clear exit criterion before moving on.",
        x_px=64, y_px=32, w_px=1000, h_px=68,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Sequential by design. No phase advances on optimism; each gate is a discrete sign-off.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

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
    for i, (num, eyebrow, name, body2, exit_text, meta_l, meta_r) in enumerate(phase_data):
        n = i + 1
        cx = grid_left + i * (card_w + gap)
        cy = cards_top
        card = add_rect(slide, f"step-{n}-bg", cx, cy, card_w, card_h, CARD_BG_DARK)
        card.line.color.rgb = CARD_BORDER_DARK
        card.line.width = 9525
        add_rect(slide, f"step-{n}-accent", cx, cy, card_w, 3, BRAND_ACCENT_SOFT)

        add_text(
            slide, f"step-{n}-num", num,
            x_px=cx + 18, y_px=cy + 14, w_px=60, h_px=44,
            font_size_px=40, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"step-{n}-eyebrow", eyebrow.upper(),
            x_px=cx + 90, y_px=cy + 16, w_px=card_w - 106, h_px=12,
            font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"step-{n}-name", name,
            x_px=cx + 90, y_px=cy + 30, w_px=card_w - 106, h_px=22,
            font_size_px=17, color=WHITE, bold=True,
        )

        add_text(
            slide, f"step-{n}-body", body2,
            x_px=cx + 18, y_px=cy + 78, w_px=card_w - 36, h_px=130,
            font_size_px=12, color=WHITE,
        )

        exit_y = cy + 220
        add_rect(slide, f"step-{n}-exit-sep", x_px=cx + 18, y_px=exit_y - 4, w_px=card_w - 36, h_px=1,
                 fill_color=CARD_BORDER_DARK)
        add_text(
            slide, f"step-{n}-exit-label", "EXIT CRITERION",
            x_px=cx + 18, y_px=exit_y, w_px=card_w - 36, h_px=12,
            font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"step-{n}-exit-text", exit_text,
            x_px=cx + 18, y_px=exit_y + 14, w_px=card_w - 36, h_px=36,
            font_size_px=11, color=WHITE, bold=True,
        )

        meta_y = cy + card_h - 22
        add_text(
            slide, f"step-{n}-meta-left", meta_l,
            x_px=cx + 18, y_px=meta_y, w_px=(card_w - 36) // 2, h_px=14,
            font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
        )
        add_text(
            slide, f"step-{n}-meta-right", meta_r,
            x_px=cx + card_w // 2, y_px=meta_y, w_px=card_w // 2 - 18, h_px=14,
            font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True, align="right",
        )

    conv_y = 720 - 78 - 42
    add_rect(slide, "convergence-bg",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42, fill_color=BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "No phase advances without its exit criterion. That's the discipline.",
        x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42,
        font_size_px=14, color=WHITE, italic=True,
        anchor="middle", padding_px=(0, 22, 0, 22),
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "16",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "16d_process-phases-rich.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
