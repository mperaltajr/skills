"""
Builder for pattern 148: Workshop summary — 3-panel (What we did / decided / next).

Chrome-normalized to Style A (was top-chrome variant).
Source HTML: _pattern-library/148_workshop-summary.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title (Style A normalized, no subtitle)
    add_text(slide, "title",
             "<strong>Five decisions made, zero deferred</strong> — fastest design sprint in the program; Phase 2 scope now locked.",
             x_px=48, y_px=58, w_px=1080, h_px=64,
             font_size_px=22, color=TEXT_DARK, bold=True,
             emphasis_color=BRAND_PRIMARY)
    add_rect(slide, "brand-rule", 48, 130, 56, 3, BRAND_ACCENT)

    # Layout area: top:148 left:48 right:48 bottom:100
    la_x = 48
    la_y = 148
    la_w = 1280 - 96
    la_h = 720 - 100 - la_y

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
    panels_h = la_h - ws_h - 12 - 60  # leave room for convergence + footnote
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
        panel = add_rect(slide, f"panel-{n}-bg", px, panels_y, pw, panels_h, CARD_BG)
        panel.line.color.rgb = CARD_BORDER
        panel.line.width = 9525
        # Left accent
        add_rect(slide, f"panel-{n}-accent", px, panels_y, 4, panels_h, BRAND_ACCENT)
        # Heading
        add_text(slide, f"panel-{n}-heading", heading,
                 x_px=px + 14, y_px=panels_y + 12, w_px=pw - 28, h_px=18,
                 font_size_px=12, color=BRAND_PRIMARY, bold=True, uppercase=True)
        # Body (numbered list)
        body_text = "\n".join(f"{j+1}. {it}" for j, it in enumerate(items))
        add_text(slide, f"panel-{n}-body", body_text,
                 x_px=px + 14, y_px=panels_y + 38, w_px=pw - 28, h_px=panels_h - 52,
                 font_size_px=11, color=TEXT_DARK)

    # Convergence
    conv_y = panels_y + panels_h + 6
    add_rect(slide, "convergence-bg", la_x, conv_y, la_w, 32, BRAND_PRIMARY)
    add_rect(slide, "convergence-accent", la_x, conv_y, 4, 32, BRAND_ACCENT)
    add_text(slide, "convergence",
             "Phase 2 scope locked. Five decisions taken in one session — no deferrals, no escalations. "
             "Next hard gate: architecture review May 22.",
             x_px=la_x + 14, y_px=conv_y, w_px=la_w - 28, h_px=32,
             font_size_px=11, color=WHITE, anchor="middle")

    # Attendees footnote
    add_text(slide, "attendees-note",
             "Attendees: 14 · Duration: 6 hours · Facilitator: [Name]",
             x_px=la_x, y_px=conv_y + 38, w_px=la_w, h_px=14,
             font_size_px=10, color=TEXT_FAINT, align="right", uppercase=True, bold=True)

    add_footer(slide, page_num=148)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "148_workshop-summary.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
