"""
Builder for pattern 148d: Workshop summary — 3-panel — dark.

Source HTML: _pattern-library/148_workshop-summary-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
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

    # Canonical chrome
    add_text(slide, "title",
             "<strong>Five decisions made, zero deferred</strong> — fastest design sprint in the program; Phase 2 scope now locked.",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Phase 2 Design Sprint · May 15, 2026 · 14 attendees · 6 hours",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Layout area
    la_x = 48
    la_y = 220
    la_w = 1280 - 96
    la_h = 664 - la_y

    # Workshop bar
    ws_h = 32
    add_rect(slide, "workshop-bar", la_x, la_y, la_w, ws_h, BRAND_PRIMARY_MID)
    add_text(slide, "workshop-date", "May 15, 2026",
             x_px=la_x + 16, y_px=la_y + 8, w_px=140, h_px=16,
             font_size_px=12, color=WHITE, bold=True)
    add_text(slide, "workshop-name", "Phase 2 Design Sprint",
             x_px=la_x + 178, y_px=la_y + 8, w_px=400, h_px=16,
             font_size_px=12, color=WHITE, bold=True)

    # 3 panels
    panels_y = la_y + ws_h + 12
    panels_h = la_h - ws_h - 12 - 60
    pgap = 14
    pw = (la_w - 2 * pgap) // 3

    panel_data = [
        ("What we did", [
            "Aligned on data architecture principles",
            "Reviewed 3 integration options",
            "Completed stakeholder impact mapping",
            "Ran friction log review (47 items)",
            "Prioritized backlog top-20",
        ]),
        ("What we decided", [
            "Adopt API-first integration pattern",
            "Defer mobile app to Phase 3",
            "Appoint Change Lead (Maya Chen)",
            "Extend sprint by 2 weeks for QA",
            "Approve $320K contingency draw",
        ]),
        ("What's next", [
            "Architecture design review (May 22)",
            "Vendor kickoff — DataCo (May 24)",
            "User story grooming (May 28)",
            "Steering committee update (June 2)",
            "Phase 3 planning begins (June 15)",
        ]),
    ]

    for i, (heading, items) in enumerate(panel_data):
        n = i + 1
        px = la_x + i * (pw + pgap)
        panel = add_rect(slide, f"panel-{n}-bg", px, panels_y, pw, panels_h, CARD_BG_DARK)
        panel.line.color.rgb = CARD_BORDER_DARK
        panel.line.width = 9525
        add_rect(slide, f"panel-{n}-accent", px, panels_y, 4, panels_h, BRAND_ACCENT)
        add_text(slide, f"panel-{n}-heading", heading,
                 x_px=px + 14, y_px=panels_y + 12, w_px=pw - 28, h_px=18,
                 font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
        body_text = "\n".join(f"{j+1}. {it}" for j, it in enumerate(items))
        add_text(slide, f"panel-{n}-body", body_text,
                 x_px=px + 14, y_px=panels_y + 38, w_px=pw - 28, h_px=panels_h - 52,
                 font_size_px=11, color=WHITE)

    # Convergence
    conv_y = panels_y + panels_h + 6
    add_rect(slide, "convergence-bg", la_x, conv_y, la_w, 32, BRAND_ACCENT)
    add_rect(slide, "convergence-accent", la_x, conv_y, 4, 32, BRAND_ACCENT_SOFT)
    add_text(slide, "convergence",
             "Phase 2 scope locked. Five decisions taken in one session — no deferrals, no escalations. "
             "Next hard gate: architecture review May 22.",
             x_px=la_x + 14, y_px=conv_y, w_px=la_w - 28, h_px=32,
             font_size_px=11, color=WHITE, anchor="middle")

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "148",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "148d_workshop-summary.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
