"""
Builder for pattern 300: Transformation office structure (dark).

PMO header bar + 4-column workstream grid + governance cadence strip at bottom.

Source HTML: _pattern-library/300_transformation-office-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER = RGBColor(0x55, 0x36, 0x77)
PMO_BAR_BG = RGBColor(0x52, 0x2A, 0x82)
RAG_GREEN = RGBColor(0x4A, 0xDE, 0x80)
RAG_AMBER = RGBColor(0xFC, 0xD3, 0x4D)
RAG_RED = RGBColor(0xFC, 0xA5, 0xA5)
RAG_GREEN_BG = RGBColor(0x1F, 0x4D, 0x33)
RAG_AMBER_BG = RGBColor(0x5C, 0x4A, 0x14)
RAG_RED_BG = RGBColor(0x5C, 0x20, 0x20)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Canonical chrome
    add_text(slide, "title",
             "<strong>Transformation Office</strong> – Program Structure & Governance",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Workstream ownership, leads, and active initiative tracking as of Q2 2026",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 80, 3, BRAND_ACCENT_SOFT)

    # PMO Header Bar (raised to 64px so the 3-line director block fits inside).
    pmo_y = 216
    pmo_h = 64
    add_rect(slide, "pmo-bar-bg", 48, pmo_y, 1184, pmo_h, PMO_BAR_BG)
    # Icon box
    add_rect(slide, "pmo-icon", 60, pmo_y + 12, 36, 36, BRAND_ACCENT)
    add_text(slide, "pmo-icon-glyph", "▦",
             x_px=60, y_px=pmo_y + 12, w_px=36, h_px=36,
             font_size_px=20, color=WHITE, align="center", anchor="middle")
    add_text(slide, "pmo-label", "PMO / TRANSFORMATION OFFICE",
             x_px=110, y_px=pmo_y + 10, w_px=400, h_px=16,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1.5)
    add_text(slide, "pmo-title", "Enterprise Modernisation Programme",
             x_px=110, y_px=pmo_y + 28, w_px=600, h_px=20,
             font_size_px=13, color=WHITE, bold=True)
    # Right side: director
    add_text(slide, "pmo-director-label", "PROGRAM DIRECTOR",
             x_px=900, y_px=pmo_y + 6, w_px=320, h_px=14,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, letter_spacing_px=1, align="right")
    add_text(slide, "pmo-director-name", "Sarah Mitchell",
             x_px=900, y_px=pmo_y + 22, w_px=320, h_px=18,
             font_size_px=12, color=WHITE, bold=True, align="right")
    add_text(slide, "pmo-reporting", "Reports to: Chief Transformation Officer",
             x_px=900, y_px=pmo_y + 42, w_px=320, h_px=14,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, align="right")

    # Workstream Grid (4 cols)
    ws_top = 290
    ws_bot = 600
    ws_h = ws_bot - ws_top
    ws_left = 48
    ws_right = 1232
    gap = 0
    col_w = (ws_right - ws_left) // 4

    workstreams = [
        ("Data & Analytics", "JK", "James Kwon",
         ["Enterprise data lake migration to Azure",
          "Self-serve BI rollout (Power BI)",
          "Data governance framework & catalogue"],
         "ON TRACK", "green"),
        ("Cloud & Infrastructure", "PR", "Priya Rao",
         ["Lift-and-shift of 42 legacy workloads",
          "Landing zone & network segmentation",
          "FinOps tagging & cost optimisation"],
         "AT RISK", "amber"),
        ("Process & Automation", "TL", "Tom Liang",
         ["Order-to-cash RPA deployment",
          "Process mining & baseline mapping",
          "Intelligent document processing pilot"],
         "ON TRACK", "green"),
        ("Change & Adoption", "AB", "Amara Bello",
         ["Change impact & stakeholder assessment",
          "Training needs analysis & delivery",
          "Comms plan & adoption measurement"],
         "OFF TRACK", "red"),
    ]
    rag_map = {
        "green": (RAG_GREEN, RAG_GREEN_BG),
        "amber": (RAG_AMBER, RAG_AMBER_BG),
        "red": (RAG_RED, RAG_RED_BG),
    }

    for i, (name, initials, lead, inits, rag_label, rag_kind) in enumerate(workstreams):
        cx = ws_left + i * col_w
        add_rect(slide, f"ws-{i+1}-bg", cx, ws_top, col_w, ws_h, CARD_BG)
        # Vertical divider line on left edge (except first)
        if i > 0:
            add_rect(slide, f"ws-{i+1}-divider", cx, ws_top + 10, 1, ws_h - 20, CARD_BORDER)
        # Name
        add_text(slide, f"ws-{i+1}-name", name,
                 x_px=cx + 16, y_px=ws_top + 14, w_px=col_w - 32, h_px=22,
                 font_size_px=13, color=WHITE, bold=True)
        # Lead row
        add_rect(slide, f"ws-{i+1}-initials-circle", cx + 16, ws_top + 50, 26, 26, BRAND_PRIMARY_MID)
        add_text(slide, f"ws-{i+1}-initials", initials,
                 x_px=cx + 16, y_px=ws_top + 50, w_px=26, h_px=26,
                 font_size_px=9, color=WHITE, bold=True, align="center", anchor="middle")
        add_text(slide, f"ws-{i+1}-lead-label", "WORKSTREAM LEAD",
                 x_px=cx + 48, y_px=ws_top + 48, w_px=col_w - 64, h_px=12,
                 font_size_px=8, color=TEXT_ON_DARK_FAINT, letter_spacing_px=0.8)
        add_text(slide, f"ws-{i+1}-lead-name", lead,
                 x_px=cx + 48, y_px=ws_top + 60, w_px=col_w - 64, h_px=18,
                 font_size_px=11, color=TEXT_ON_DARK_MID)
        # Divider under lead row
        add_rect(slide, f"ws-{i+1}-rule", cx + 16, ws_top + 90, col_w - 32, 1, CARD_BORDER)
        # Initiatives list
        iy = ws_top + 102
        for j, init in enumerate(inits):
            add_text(slide, f"ws-{i+1}-init-{j+1}-chev", "›",
                     x_px=cx + 16, y_px=iy, w_px=10, h_px=18,
                     font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True)
            add_text(slide, f"ws-{i+1}-init-{j+1}", init,
                     x_px=cx + 28, y_px=iy, w_px=col_w - 44, h_px=48,
                     font_size_px=11, color=TEXT_ON_DARK_MID)
            iy += 44
        # RAG pill
        rag_col, rag_bg = rag_map[rag_kind]
        pill_y = ws_bot - 36
        add_rect(slide, f"ws-{i+1}-rag-pill", cx + 16, pill_y, 96, 22, rag_bg)
        add_rect(slide, f"ws-{i+1}-rag-dot", cx + 24, pill_y + 8, 6, 6, rag_col)
        add_text(slide, f"ws-{i+1}-rag-label", rag_label,
                 x_px=cx + 34, y_px=pill_y, w_px=78, h_px=22,
                 font_size_px=9, color=rag_col, bold=True,
                 anchor="middle", letter_spacing_px=1)

    # Governance Cadence Strip
    gov_y = 612
    gov_h = 36
    add_rect(slide, "governance-bg", 48, gov_y, 1184, gov_h, CARD_BG)
    add_text(slide, "governance-label", "GOVERNANCE CADENCE",
             x_px=64, y_px=gov_y, w_px=160, h_px=gov_h,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True,
             letter_spacing_px=1.2, anchor="middle")
    add_rect(slide, "gov-divider", 224, gov_y + 10, 1, 16, CARD_BORDER)

    pills = [
        ("WEEKLY", "Workstream Leads Sync"),
        ("WEEKLY", "Program Director Stand-up"),
        ("BI-WEEKLY", "Steering Committee"),
        ("BI-WEEKLY", "Risk & Issue Review"),
        ("MONTHLY", "Executive Sponsor Briefing"),
        ("MONTHLY", "Portfolio Board"),
    ]
    pill_x = 244
    for i, (freq, nm) in enumerate(pills):
        # Approximate widths
        fw = len(freq) * 6 + 10
        nw = len(nm) * 5.8 + 10
        total_w = fw + nw + 6
        add_rect(slide, f"gov-pill-{i+1}", pill_x, gov_y + 8, total_w, 20, CARD_BORDER)
        add_text(slide, f"gov-pill-{i+1}-freq", freq,
                 x_px=pill_x + 6, y_px=gov_y + 8, w_px=fw, h_px=20,
                 font_size_px=8, color=BRAND_ACCENT_SOFT, bold=True,
                 anchor="middle", letter_spacing_px=0.6)
        add_text(slide, f"gov-pill-{i+1}-name", nm,
                 x_px=pill_x + 6 + fw, y_px=gov_y + 8, w_px=nw, h_px=20,
                 font_size_px=9, color=TEXT_ON_DARK_MID, anchor="middle")
        pill_x += total_w + 8

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "300",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "300_transformation-office-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
