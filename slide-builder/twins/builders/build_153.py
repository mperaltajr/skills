"""
Builder for pattern 153: Sprint review summary — kanban board (Done/In Progress/Blocked).

Source HTML: _pattern-library/153_sprint-review-summary.html
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
from pptx.dml.color import RGBColor

DONE_BG = RGBColor(0x16, 0x65, 0x34)
IP_BG = RGBColor(0x92, 0x40, 0x0E)
BLOCKED_BG = RGBColor(0x99, 0x1B, 0x1B)
BLOCKED_SOFT = RGBColor(0xFE, 0xE2, 0xE2)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Eyebrow + title
    add_text(slide, "eyebrow", "Agile Delivery · Sprint Review",
             x_px=48, y_px=58, w_px=400, h_px=14,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "title",
             "<strong>Sprint 14 closes at 93% velocity</strong> — single blocker is external dependency, escalated to vendor",
             x_px=48, y_px=78, w_px=1100, h_px=46,
             font_size_px=22, color=TEXT_DARK, bold=True,
             emphasis_color=BRAND_PRIMARY)
    add_rect(slide, "brand-rule", 48, 130, 56, 3, BRAND_ACCENT)

    # Sprint meta bar
    sm_y = 148
    sm_h = 28
    add_rect(slide, "sprint-meta", 48, sm_y, 1280 - 96, sm_h, BRAND_PRIMARY_MID)
    add_text(slide, "sprint-meta-text",
             "Sprint 14  ·  May 5-18, 2026  ·  Velocity: 42 points  ·  Target: 45 points (93%)",
             x_px=64, y_px=sm_y, w_px=1280 - 128, h_px=sm_h,
             font_size_px=11, color=WHITE, bold=True, anchor="middle")

    # Kanban columns: top:188 left:48 right:48 bottom:100
    kb_y = 188
    kb_x = 48
    kb_w = 1280 - 96
    kb_h = 720 - 100 - kb_y
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
        # Column body bg
        col_bg = add_rect(slide, f"col-{n}-bg", cx, kb_y, cw, kb_h, RGBColor(0xFA, 0xFA, 0xFA))
        col_bg.line.color.rgb = CARD_BORDER
        col_bg.line.width = 9525
        # Header
        add_rect(slide, f"col-{n}-header", cx, kb_y, cw, head_h, head_color)
        add_text(slide, f"col-{n}-label", label,
                 x_px=cx + 12, y_px=kb_y + 8, w_px=cw - 100, h_px=18,
                 font_size_px=11, color=WHITE, bold=True, uppercase=True)
        add_text(slide, f"col-{n}-count", count_text,
                 x_px=cx + cw - 130, y_px=kb_y + 10, w_px=120, h_px=14,
                 font_size_px=8, color=WHITE, bold=True, align="right", uppercase=True)

        # Cards
        card_y_start = kb_y + head_h + 8
        card_h = 52
        card_gap = 6
        for i, (story_id, story_title, pts, avatar) in enumerate(cards):
            cy = card_y_start + i * (card_h + card_gap)
            if cy + card_h > kb_y + kb_h - 8:
                break
            is_blocked = ci == 2
            card_bg_color = BLOCKED_SOFT if is_blocked else WHITE
            card = add_rect(slide, f"card-{n}-{i+1}-bg", cx + 8, cy, cw - 16, card_h, card_bg_color)
            card.line.color.rgb = CARD_BORDER
            card.line.width = 9525
            # Left accent
            add_rect(slide, f"card-{n}-{i+1}-accent", cx + 8, cy, 3, card_h, head_color)
            # Story ID pill
            add_text(slide, f"card-{n}-{i+1}-id", story_id,
                     x_px=cx + 16, y_px=cy + 4, w_px=44, h_px=14,
                     font_size_px=8, color=BRAND_ACCENT, bold=True, align="center", uppercase=True,
                     bg_fill=CARD_BG, padding_px=(2, 4, 2, 4))
            # Title
            add_text(slide, f"card-{n}-{i+1}-title", story_title,
                     x_px=cx + 64, y_px=cy + 4, w_px=cw - 80, h_px=28,
                     font_size_px=10, color=TEXT_DARK, bold=True)
            # Points + avatar
            add_text(slide, f"card-{n}-{i+1}-pts", pts,
                     x_px=cx + 16, y_px=cy + card_h - 18, w_px=40, h_px=14,
                     font_size_px=8, color=TEXT_MID, bold=True, align="center",
                     bg_fill=RGBColor(0xF1, 0xF5, 0xF9), padding_px=(2, 4, 2, 4))
            add_text(slide, f"card-{n}-{i+1}-avatar", avatar,
                     x_px=cx + cw - 36, y_px=cy + card_h - 22, w_px=20, h_px=18,
                     font_size_px=8, color=WHITE, bold=True, align="center", anchor="middle",
                     bg_fill=head_color, padding_px=(0, 0, 0, 0))

        # Blocker reason for blocked column
        if ci == 2:
            br_y = card_y_start + len(cards) * (card_h + card_gap)
            br_h = 56
            br_bg = add_rect(slide, "blocker-bg", cx + 8, br_y, cw - 16, br_h, RGBColor(0xFE, 0xF2, 0xF2))
            br_bg.line.color.rgb = RGBColor(0xFC, 0xA5, 0xA5)
            br_bg.line.width = 9525
            add_rect(slide, "blocker-accent", cx + 8, br_y, 3, br_h, BLOCKED_BG)
            add_text(slide, "blocker-label", "BLOCKER",
                     x_px=cx + 16, y_px=br_y + 6, w_px=60, h_px=14,
                     font_size_px=8, color=BLOCKED_BG, bold=True, uppercase=True)
            add_text(slide, "blocker-text",
                     "API contract not finalized — ETA unknown. Escalated to vendor. Carrying to Sprint 15.",
                     x_px=cx + 16, y_px=br_y + 22, w_px=cw - 32, h_px=30,
                     font_size_px=9, color=RGBColor(0x7F, 0x1D, 0x1D), bold=True)

    # Summary strip (convergence)
    conv_y = 720 - 76
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, 38, BRAND_PRIMARY)
    add_text(slide, "convergence",
             "42/45 pts completed  ·  1 blocker  ·  Carryover: US-189 (5 pts) to Sprint 15",
             x_px=48, y_px=conv_y, w_px=1280 - 96, h_px=38,
             font_size_px=11, color=WHITE, anchor="middle", align="center")

    add_footer(slide, page_num=153)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "153_sprint-review-summary.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
