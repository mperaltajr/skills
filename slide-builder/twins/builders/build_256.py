"""
Builder for pattern 256: Project status + decision ask (dark).

Source HTML: _pattern-library/256_project-status-ask-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER = RGBColor(0x55, 0x36, 0x77)
DIVIDER = RGBColor(0x55, 0x36, 0x77)

RAG_GREEN = RGBColor(0x2E, 0xCC, 0x71)
RAG_AMBER = RGBColor(0xF3, 0x9C, 0x12)
RAG_RED = RGBColor(0xDC, 0x26, 0x26)
RED_LIGHT = RGBColor(0xFF, 0x6B, 0x6B)


def build():
    prs, slide = new_slide()

    # Dark background
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Title block — canonical chrome
    add_text(slide, "title",
             "Phoenix Programme · Week 12 of 24 · <strong>Steering Committee decision required.</strong>",
             x_px=40, y_px=20, w_px=1200, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Four workstreams tracked. One is blocked. This slide asks for a go/no-go on the critical path replan.",
             x_px=40, y_px=108, w_px=1200, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 40, 132, 80, 3, BRAND_ACCENT_SOFT)

    # KPI strip - 4 tiles below brand rule (no legend in this pattern, body can start at y=220)
    kpi_y = 220
    kpi_h = 56
    kpi_data = [
        ("12 / 24", "Week", WHITE),
        ("94%", "Budget Utilized", RAG_AMBER),
        ("3", "Issues Open", RAG_AMBER),
        ("2", "Risks Red", RAG_RED),
    ]
    tile_w = (1200 - 3 * 14) // 4
    for i, (num, lbl, col) in enumerate(kpi_data):
        tx = 40 + i * (tile_w + 14)
        add_rect(slide, f"kpi-{i+1}-bg", tx, kpi_y, tile_w, kpi_h, CARD_BG)
        add_text(slide, f"kpi-{i+1}-number", num,
                 x_px=tx, y_px=kpi_y + 8, w_px=tile_w, h_px=24,
                 font_size_px=18, color=col, bold=True, align="center")
        add_text(slide, f"kpi-{i+1}-label", lbl,
                 x_px=tx, y_px=kpi_y + 34, w_px=tile_w, h_px=18,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True,
                 align="center", uppercase=True, letter_spacing_px=1.2)

    # Body: left (workstream status) and right (decision ask)
    body_top = 290
    body_bot = 660
    left_x = 40
    left_w = 720
    right_x = 800
    right_w = 440
    divider_x = 776

    # Divider
    add_rect(slide, "body-divider", divider_x, body_top, 1, body_bot - body_top, DIVIDER)

    # LEFT - workstream status
    add_text(slide, "ws-section-label", "WORKSTREAM STATUS",
             x_px=left_x, y_px=body_top, w_px=left_w, h_px=16,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             letter_spacing_px=2)

    ws_data = [
        ("Data Migration", "ON TRACK", "green",
         "847K records migrated, target 1.2M — velocity on plan, delta-load testing complete"),
        ("Process Design", "ON TRACK", "green",
         "14 of 18 future-state flows signed off — remaining 4 in business review this week"),
        ("Change & Training", "AT RISK", "amber",
         "LMS build delayed 2 weeks — vendor dependency; contingency plan in review, go-live buffer not yet consumed"),
        ("Integration & Testing", "BLOCKED", "red",
         "UAT environment not provisioned — IT access request pending 18 days; blocks full regression cycle by Week 16"),
    ]
    rag_map = {"green": RAG_GREEN, "amber": RAG_AMBER, "red": RED_LIGHT}
    ws_top = body_top + 26
    ws_h = (body_bot - ws_top - 30) // 4
    for i, (name, tag, rag, status) in enumerate(ws_data):
        y = ws_top + i * (ws_h + 8)
        add_rect(slide, f"ws-{i+1}-bg", left_x, y, left_w, ws_h, CARD_BG)
        # Dot
        add_rect(slide, f"ws-{i+1}-dot", left_x + 14, y + 14, 12, 12, rag_map[rag])
        # Name
        add_text(slide, f"ws-{i+1}-name", name,
                 x_px=left_x + 36, y_px=y + 10, w_px=200, h_px=18,
                 font_size_px=12, color=WHITE, bold=True)
        # Tag pill
        add_rect(slide, f"ws-{i+1}-tag-bg", left_x + 240, y + 12, 80, 16, CARD_BORDER)
        add_text(slide, f"ws-{i+1}-tag", tag,
                 x_px=left_x + 240, y_px=y + 12, w_px=80, h_px=16,
                 font_size_px=8, color=rag_map[rag], bold=True,
                 align="center", anchor="middle", letter_spacing_px=1.2)
        # Status
        add_text(slide, f"ws-{i+1}-status", status,
                 x_px=left_x + 36, y_px=y + 32, w_px=left_w - 50, h_px=ws_h - 38,
                 font_size_px=11, color=TEXT_ON_DARK_MID)

    # RIGHT - decision required
    add_text(slide, "decision-section-label", "DECISION REQUIRED",
             x_px=right_x, y_px=body_top, w_px=right_w, h_px=16,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             letter_spacing_px=2)
    add_text(slide, "decision-statement",
             "UAT environment is 18 days overdue. How should the programme proceed on the critical path?",
             x_px=right_x, y_px=body_top + 26, w_px=right_w, h_px=46,
             font_size_px=14, color=WHITE, bold=True)

    opt_data = [
        ("APPROVE", RAG_GREEN, "Escalate IT provisioning to CTO today — maintains Week 16 regression window, no schedule slip"),
        ("DEFER", RAG_AMBER, "Accept 2-week regression compression — increases defect-escape risk, go-live moves to Week 26"),
        ("ESCALATE", RED_LIGHT, "Invoke programme governance board — triggers formal replanning and revised business case approval"),
    ]
    opt_top = body_top + 88
    opt_h = (body_bot - opt_top - 16) // 3
    for i, (name, col, impl) in enumerate(opt_data):
        y = opt_top + i * (opt_h + 8)
        add_rect(slide, f"option-{i+1}-bg", right_x, y, right_w, opt_h, CARD_BG)
        # Accent bar left
        add_rect(slide, f"option-{i+1}-bar", right_x, y, 4, opt_h, col)
        add_text(slide, f"option-{i+1}-name", name,
                 x_px=right_x + 16, y_px=y + 12, w_px=right_w - 24, h_px=18,
                 font_size_px=12, color=col, bold=True, letter_spacing_px=1.2)
        add_text(slide, f"option-{i+1}-impl", impl,
                 x_px=right_x + 16, y_px=y + 34, w_px=right_w - 28, h_px=opt_h - 42,
                 font_size_px=11, color=TEXT_ON_DARK_MID)

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "256",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "256_project-status-ask-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
