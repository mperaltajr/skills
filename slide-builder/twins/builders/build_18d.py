"""
Builder for pattern 18d: Methodology overview — DARK variant.

Light source: twins/builders/build_18.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
DELIV_BG_DARK = RGBColor(0x14, 0x05, 0x28)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Our approach — five steps, each with activities and a deliverable.",
        x_px=64, y_px=32, w_px=1000, h_px=68,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Each step ends with an artefact a stakeholder can react to — never an internal-only milestone.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

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
        card = add_rect(slide, f"step-{n}-bg", cx, cy, card_w, card_h, CARD_BG_DARK)
        card.line.color.rgb = CARD_BORDER_DARK
        card.line.width = 9525
        add_rect(slide, f"step-{n}-accent", cx, cy, card_w, 3, BRAND_ACCENT_SOFT)

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

        add_text(
            slide, f"step-{n}-name", name,
            x_px=cx, y_px=cy + 64, w_px=card_w, h_px=20,
            font_size_px=14, color=WHITE, bold=True,
            align="center", uppercase=True,
        )

        add_text(
            slide, f"step-{n}-desc", desc,
            x_px=cx + 8, y_px=cy + 86, w_px=card_w - 16, h_px=38,
            font_size_px=11, color=TEXT_ON_DARK_MID, italic=True, align="center",
        )

        activities_y = cy + head_h
        add_text(
            slide, f"step-{n}-activities-label", "ACTIVITIES",
            x_px=cx + 14, y_px=activities_y + 8, w_px=card_w - 28, h_px=12,
            font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"step-{n}-body", activities,
            x_px=cx + 14, y_px=activities_y + 22, w_px=card_w - 28, h_px=activities_h - 30,
            font_size_px=11, color=WHITE,
        )

        deliv_y = activities_y + activities_h
        add_rect(slide, f"step-{n}-deliv-bg", cx, deliv_y, card_w, deliv_h, DELIV_BG_DARK)
        add_text(
            slide, f"step-{n}-deliverables-label", "DELIVERABLES",
            x_px=cx + 14, y_px=deliv_y + 8, w_px=card_w - 28, h_px=12,
            font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
        )
        for j, dname in enumerate(deliverables):
            dn = j + 1
            dy = deliv_y + 26 + j * 26
            add_rect(slide, f"step-{n}-deliverable-{dn}-icon", cx + 14, dy, 20, 20, CARD_BG_DARK)
            add_text(
                slide, f"step-{n}-deliverable-{dn}-name", dname,
                x_px=cx + 40, y_px=dy + 2, w_px=card_w - 54, h_px=18,
                font_size_px=11, color=WHITE, bold=True,
            )

    conv_y = 720 - 78 - 42
    add_rect(slide, "convergence-bg",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42, fill_color=BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "Every step produces something a stakeholder can react to — nothing is internal-only.",
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
    add_text(slide, "page-number", "18",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "18d_methodology-overview.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
