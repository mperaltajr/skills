"""
Builder for pattern 153d: Sprint review summary — kanban board — dark.

Source HTML: _pattern-library/153_sprint-review-summary-dark.html
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

DONE_BG = RGBColor(0x16, 0xA3, 0x4A)
IP_BG = RGBColor(0xD9, 0x77, 0x06)
BLOCKED_BG = RGBColor(0xDC, 0x26, 0x26)
COL_BG_DARK = RGBColor(0x35, 0x1A, 0x52)
BLOCKED_SOFT = RGBColor(0x5C, 0x1F, 0x1F)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title",
             "<strong>Sprint 14 closes at 93% velocity</strong> — single blocker is external dependency, escalated to vendor",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Agile delivery · Sprint review · May 5-18, 2026",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Sprint meta bar
    sm_y = 220
    sm_h = 28
    add_rect(slide, "sprint-meta", 48, sm_y, 1280 - 96, sm_h, BRAND_PRIMARY_MID)
    add_text(slide, "sprint-meta-text",
             "Sprint 14  ·  May 5-18, 2026  ·  Velocity: 42 points  ·  Target: 45 points (93%)",
             x_px=64, y_px=sm_y, w_px=1280 - 128, h_px=sm_h,
             font_size_px=11, color=WHITE, bold=True, anchor="middle")

    # Kanban columns
    kb_y = sm_y + sm_h + 8
    kb_x = 48
    kb_w = 1280 - 96
    kb_h = 604 - kb_y
    gap = 12
    cw = (kb_w - 2 * gap) // 3
    head_h = 32

    columns = [
        ("Done", "6 stories · 32 pts", DONE_BG, [
            ("US-142", "User login with SSO integration", "8 pts", "JM"),
            ("US-143", "Dashboard data refresh (live polling)", "5 pts", "RP"),
            ("US-145", "Export report to PDF & CSV", "5 pts", "KL"),
            ("US-147", "Role-based access control setup", "8 pts", "JM"),
            ("US-149", "Notification email templates", "3 pts", "AL"),
            ("US-151", "Accessibility audit — WCAG 2.1 AA", "3 pts", "RP"),
        ]),
        ("In Progress", "3 stories · 10 pts", IP_BG, [
            ("US-153", "Bulk user import via CSV upload", "5 pts", "KL"),
            ("US-155", "Audit log viewer — admin panel", "3 pts", "AL"),
            ("US-157", "Dark mode theme toggle", "2 pts", "RP"),
        ]),
        ("Blocked", "1 story · 5 pts", BLOCKED_BG, [
            ("US-189", "Third-party payment API integration", "5 pts", "JM"),
        ]),
    ]

    for ci, (label, count_text, head_color, cards) in enumerate(columns):
        n = ci + 1
        cx = kb_x + ci * (cw + gap)
        col_bg = add_rect(slide, f"col-{n}-bg", cx, kb_y, cw, kb_h, COL_BG_DARK)
        col_bg.line.color.rgb = CARD_BORDER_DARK
        col_bg.line.width = 9525
        add_rect(slide, f"col-{n}-header", cx, kb_y, cw, head_h, head_color)
        add_text(slide, f"col-{n}-label", label,
                 x_px=cx + 12, y_px=kb_y + 8, w_px=cw - 100, h_px=18,
                 font_size_px=11, color=WHITE, bold=True, uppercase=True)
        add_text(slide, f"col-{n}-count", count_text,
                 x_px=cx + cw - 130, y_px=kb_y + 10, w_px=120, h_px=14,
                 font_size_px=8, color=WHITE, bold=True, align="right", uppercase=True)

        card_y_start = kb_y + head_h + 8
        card_h = 52
        card_gap = 6
        for i, (story_id, story_title, pts, avatar) in enumerate(cards):
            cy = card_y_start + i * (card_h + card_gap)
            if cy + card_h > kb_y + kb_h - 8:
                break
            is_blocked = ci == 2
            card_bg_color = BLOCKED_SOFT if is_blocked else CARD_BG_DARK
            card = add_rect(slide, f"card-{n}-{i+1}-bg", cx + 8, cy, cw - 16, card_h, card_bg_color)
            card.line.color.rgb = CARD_BORDER_DARK
            card.line.width = 9525
            add_rect(slide, f"card-{n}-{i+1}-accent", cx + 8, cy, 3, card_h, head_color)
            add_text(slide, f"card-{n}-{i+1}-id", story_id,
                     x_px=cx + 16, y_px=cy + 4, w_px=44, h_px=14,
                     font_size_px=8, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True,
                     bg_fill=BRAND_PRIMARY, padding_px=(2, 4, 2, 4))
            add_text(slide, f"card-{n}-{i+1}-title", story_title,
                     x_px=cx + 64, y_px=cy + 4, w_px=cw - 80, h_px=28,
                     font_size_px=10, color=WHITE, bold=True)
            add_text(slide, f"card-{n}-{i+1}-pts", pts,
                     x_px=cx + 16, y_px=cy + card_h - 18, w_px=40, h_px=14,
                     font_size_px=8, color=TEXT_ON_DARK_MID, bold=True, align="center",
                     bg_fill=BRAND_PRIMARY, padding_px=(2, 4, 2, 4))
            add_text(slide, f"card-{n}-{i+1}-avatar", avatar,
                     x_px=cx + cw - 36, y_px=cy + card_h - 22, w_px=20, h_px=18,
                     font_size_px=8, color=WHITE, bold=True, align="center", anchor="middle",
                     bg_fill=head_color, padding_px=(0, 0, 0, 0))

        if ci == 2:
            br_y = card_y_start + len(cards) * (card_h + card_gap)
            br_h = 56
            br_bg = add_rect(slide, "blocker-bg", cx + 8, br_y, cw - 16, br_h, BLOCKED_SOFT)
            br_bg.line.color.rgb = BLOCKED_BG
            br_bg.line.width = 9525
            add_rect(slide, "blocker-accent", cx + 8, br_y, 3, br_h, BLOCKED_BG)
            add_text(slide, "blocker-label", "BLOCKER",
                     x_px=cx + 16, y_px=br_y + 6, w_px=60, h_px=14,
                     font_size_px=8, color=RGBColor(0xF8, 0x71, 0x71), bold=True, uppercase=True)
            add_text(slide, "blocker-text",
                     "API contract not finalized — ETA unknown. Escalated to vendor. Carrying to Sprint 15.",
                     x_px=cx + 16, y_px=br_y + 22, w_px=cw - 32, h_px=30,
                     font_size_px=9, color=WHITE, bold=True)

    # Summary strip
    conv_y = kb_y + kb_h + 6
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, 36, BRAND_ACCENT)
    add_text(slide, "convergence",
             "42/45 pts completed  ·  1 blocker  ·  Carryover: US-189 (5 pts) to Sprint 15",
             x_px=48, y_px=conv_y, w_px=1280 - 96, h_px=36,
             font_size_px=11, color=WHITE, anchor="middle", align="center")

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "153",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "153d_sprint-review-summary.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
