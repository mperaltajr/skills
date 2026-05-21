"""
Builder for pattern 166: Operating Rhythm — 4-col cadence grid with meeting cards.

Source HTML: _pattern-library/166_operating-rhythm.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

LEAD_BG = RGBColor(0xED, 0xE7, 0xF6)
LEAD_BORDER = RGBColor(0x9C, 0x6F, 0xD6)
OPS_BG = RGBColor(0xE8, 0xF5, 0xE9)
OPS_BORDER = RGBColor(0x4C, 0xAF, 0x50)
PLAN_BG = RGBColor(0xFF, 0xF3, 0xE0)
PLAN_BORDER = RGBColor(0xFF, 0x98, 0x00)

TYPE_MAP = {
    "leadership": (LEAD_BG, LEAD_BORDER),
    "ops": (OPS_BG, OPS_BORDER),
    "planning": (PLAN_BG, PLAN_BORDER),
}


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Cadence of <strong>Operating Rhythm</strong>",
        subtitle="Structured meetings and rituals that keep teams aligned and accountable across every horizon.",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

    # Legend — below subheadline, top-y ≥ 230, right-aligned to x≈1240
    legend_data = [
        (1, "Leadership", LEAD_BORDER),
        (2, "Operations", OPS_BORDER),
        (3, "Planning", PLAN_BORDER),
    ]
    lg_y = 230
    # Each item: swatch(8) + gap(6) + label(70) + item_gap(16) = 100
    item_span = 100
    total_leg_w = len(legend_data) * item_span - 16  # subtract trailing gap
    lg_x = 1240 - total_leg_w
    for i, (n, label, color) in enumerate(legend_data):
        x = lg_x + i * item_span
        add_rect(slide, f"legend-{n}-swatch", x, lg_y + 3, 8, 8, color)
        add_text(slide, f"legend-{n}-label", label,
                 x + 14, lg_y, 80, 14, font_size_px=9, color=TEXT_MID, bold=True, uppercase=True)

    # 4-column cadence grid — pushed down to clear legend (legend bottom ≈ 244)
    grid_top = 252
    grid_left = 48
    grid_w = 1280 - 96
    col_gap = 12
    col_w = (grid_w - col_gap * 3) // 4

    col_data = [
        ("Daily", "Every business day", BRAND_ACCENT,
         [("ops", "Stand-up Sync", "15 min", "Delivery team · Scrum Master"),
          ("ops", "Blocker Triage", "10 min", "Tech Lead · PM"),
          ("leadership", "Exec Pulse Check", "5 min", "Engagement Lead · Client Sponsor"),
          ("ops", "EOD Handoff", "10 min", "Delivery team · Offshore Lead"),
          ("planning", "Tomorrow's Priorities", "5 min", "PM · Workstream Leads")]),
        ("Weekly", "Every Monday & Friday", LEAD_BORDER,
         [("leadership", "Steering Committee", "60 min", "Sponsors · Program Lead · Workstream Leads"),
          ("ops", "Status & Risk Review", "30 min", "PM · Tech Lead · QA Lead"),
          ("planning", "Sprint Planning", "45 min", "Delivery team · Product Owner"),
          ("ops", "Retrospective", "30 min", "Delivery team"),
          ("leadership", "Client Check-in", "30 min", "Engagement Lead · Client Sponsor")]),
        ("Monthly", "1st week of each month", OPS_BORDER,
         [("leadership", "Program Board Review", "90 min", "All workstream leads · Exec sponsor"),
          ("planning", "Milestone & Roadmap Check", "60 min", "PM · Client PMO · Architects"),
          ("ops", "Budget & Resource Review", "45 min", "Engagement Lead · Finance Lead"),
          ("ops", "Quality & Defect Trends", "45 min", "QA Lead · Tech Lead"),
          ("planning", "Capacity Forecast", "30 min", "PMO · Resource Manager")]),
        ("Quarterly", "End of each quarter", PLAN_BORDER,
         [("planning", "Quarterly Business Review", "Half-day", "C-suite · Engagement Lead · PMO"),
          ("leadership", "Strategic Alignment Session", "3 hrs", "Program Sponsor · Architecture Board"),
          ("planning", "OKR & Goal Reset", "2 hrs", "All leads · Strategy team"),
          ("ops", "Vendor & Partner Review", "90 min", "Procurement · Engagement Lead"),
          ("leadership", "Talent & Succession", "2 hrs", "HR Lead · Program Sponsor")]),
    ]

    meeting_idx = 0
    for col_i, (col_name, col_desc, accent, cards) in enumerate(col_data):
        cx = grid_left + col_i * (col_w + col_gap)
        # Header
        header_h = 38
        add_rect(slide, f"col-{col_i+1}-header-bg", cx, grid_top, col_w, header_h, BRAND_PRIMARY)
        add_rect(slide, f"col-{col_i+1}-accent", cx, grid_top, col_w, 3, accent)
        add_text(slide, f"col-{col_i+1}-name", col_name,
                 cx + 10, grid_top + 6, col_w - 20, 16,
                 font_size_px=11, color=WHITE, bold=True, uppercase=True)
        add_text(slide, f"col-{col_i+1}-desc", col_desc,
                 cx + 10, grid_top + 22, col_w - 20, 14,
                 font_size_px=9, color=RGBColor(0xCC, 0xCC, 0xDD))

        # Cards
        card_y = grid_top + header_h + 6
        card_h = 50
        card_gap = 6
        for card in cards:
            meeting_idx += 1
            kind, name, dur, parts = card
            bg, border = TYPE_MAP[kind]
            add_rect(slide, f"meeting-{meeting_idx}-bg", cx, card_y, col_w, card_h, bg)
            add_rect(slide, f"meeting-{meeting_idx}-border", cx, card_y, 3, card_h, border)
            # Name
            add_text(slide, f"meeting-{meeting_idx}-name", name,
                     cx + 10, card_y + 6, col_w - 60, 14,
                     font_size_px=11, color=TEXT_DARK, bold=True)
            # Pill
            pill_w = 48
            pill_h = 14
            add_rect(slide, f"meeting-{meeting_idx}-pill-bg",
                     cx + col_w - pill_w - 6, card_y + 6, pill_w, pill_h, border)
            add_text(slide, f"meeting-{meeting_idx}-duration", dur,
                     cx + col_w - pill_w - 6, card_y + 6, pill_w, pill_h,
                     font_size_px=8, color=WHITE, bold=True, align="center", anchor="middle")
            # Participants
            add_text(slide, f"meeting-{meeting_idx}-participants", parts,
                     cx + 10, card_y + 24, col_w - 16, 22,
                     font_size_px=9, color=TEXT_MID)
            card_y += card_h + card_gap

    # Convergence bar
    conv_y = 720 - 56 - 44 - 4
    add_rect(slide, "convergence-bg", grid_left, conv_y, grid_w, 38, BRAND_PRIMARY)
    add_text(slide, "convergence",
             "Rhythm drives ACCOUNTABILITY — every cadence ties to a decision, an action, or a commitment.",
             grid_left, conv_y, grid_w, 38,
             font_size_px=11, color=WHITE, bold=True, uppercase=True,
             align="center", anchor="middle")

    add_footer(slide, page_num=166)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "166_operating-rhythm.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
