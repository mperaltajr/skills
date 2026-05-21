"""
Builder for pattern 192: Agile Sprint Board (Kanban).

4 columns (Backlog/In Progress/Review/Done) with task cards. Sprint progress bar
at top. Pillar-N-* for columns, kanban-N-card-M-* for cards (pattern-local).

Source HTML: _pattern-library/192_agile-sprint-board.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

COL_BG = RGBColor(0xF1, 0xEB, 0xF8)
GREEN = RGBColor(0x22, 0xC5, 0x5E)
RED = RGBColor(0xEF, 0x44, 0x44)

EPIC_COLORS = {
    "UX":   (RGBColor(0xF0, 0xFD, 0xF4), RGBColor(0x16, 0x65, 0x34)),
    "Auth": (RGBColor(0xED, 0xE9, 0xFE), RGBColor(0x5B, 0x21, 0xB6)),
    "API":  (RGBColor(0xFE, 0xF3, 0xC7), RGBColor(0x92, 0x40, 0x0E)),
    "Infra":(RGBColor(0xD1, 0xFA, 0xE5), RGBColor(0x06, 0x5F, 0x46)),
    "Perf": (RGBColor(0xFF, 0xF7, 0xED), RGBColor(0xC2, 0x41, 0x0C)),
    "UI":   (RGBColor(0xDB, 0xEA, 0xFE), RGBColor(0x1E, 0x40, 0xAF)),
    "Security": (RGBColor(0xFE, 0xE2, 0xE2), RGBColor(0x99, 0x1B, 0x1B)),
    "Data": (RGBColor(0xFC, 0xE7, 0xF3), RGBColor(0x9D, 0x17, 0x4D)),
}


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Agile <strong>Sprint Board</strong>",
        subtitle="Live task status across Backlog, In Progress, Review, and Done — Sprint 14",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    # Sprint progress bar
    spr_top = 158
    add_text(slide, "sprint-label", "SPRINT 14 · DAY 7 OF 10",
             x_px=64, y_px=spr_top, w_px=400, h_px=14,
             font_size_px=10, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_text(slide, "sprint-pct", "68% complete",
             x_px=1280 - 200, y_px=spr_top, w_px=140, h_px=14,
             font_size_px=10, color=BRAND_ACCENT, bold=True, align="right")
    add_rect(slide, "sprint-track", 64, spr_top + 18, 1280 - 128, 6, CARD_BORDER)
    add_rect(slide, "sprint-fill", 64, spr_top + 18, int((1280 - 128) * 0.68), 6, BRAND_ACCENT)

    # Kanban board: 4 columns
    board_top = 196
    board_bot = 600
    board_h = board_bot - board_top
    col_w = (1280 - 128 - 36) // 4
    col_gap = 12

    columns = [
        ("Backlog", 4, [
            ("User onboarding flow redesign", "5 pts", "UX", None),
            ("OAuth 2.0 refresh token support", "8 pts", "Auth", None),
            ("Export to CSV endpoint", "3 pts", "API", None),
            ("Terraform module for staging env", "5 pts", "Infra", None),
        ]),
        ("In Progress", 3, [
            ("Dashboard performance tuning", "8 pts", "Perf", "ip"),
            ("GraphQL schema migration v3", "13 pts", "API", "ip"),
            ("Notification preference centre UI", "5 pts", "UI", "ip"),
        ]),
        ("Review", 3, [
            ("Role-based access control audit", "8 pts", "Security", None),
            ("Payment gateway webhook handler", "13 pts", "API", "blocked"),
            ("Data pipeline unit test coverage", "5 pts", "Data", None),
        ]),
        ("Done", 4, [
            ("Login page accessibility fixes", "3 pts", "UX", "done"),
            ("CI/CD pipeline Helm chart update", "5 pts", "Infra", "done"),
            ("User search API pagination", "5 pts", "API", "done"),
            ("Dark mode token system setup", "8 pts", "UI", "done"),
        ]),
    ]
    for i, (cname, count, cards) in enumerate(columns):
        cx = 64 + i * (col_w + col_gap)
        n = i + 1
        # Column header
        add_rect(slide, f"pillar-{n}-header", cx, board_top, col_w, 28, BRAND_PRIMARY)
        add_text(slide, f"pillar-{n}-name", cname,
                 x_px=cx + 10, y_px=board_top + 6, w_px=col_w - 60, h_px=16,
                 font_size_px=12, color=WHITE, bold=True, uppercase=True)
        add_text(slide, f"pillar-{n}-tag", str(count),
                 x_px=cx + col_w - 40, y_px=board_top + 6, w_px=24, h_px=16,
                 font_size_px=9, color=WHITE, bold=True, align="center",
                 bg_fill=BRAND_ACCENT, padding_px=(1, 4, 1, 4))
        # Column body
        col_body = add_rect(slide, f"pillar-{n}-body", cx, board_top + 28,
                            col_w, board_h - 28, COL_BG)
        col_body.line.color.rgb = CARD_BORDER
        col_body.line.width = 9525
        # Cards
        card_y = board_top + 36
        card_w = col_w - 16
        for j, (title, pts, epic, state) in enumerate(cards):
            card_h = 60 if state == "blocked" else 48
            card_bg = add_rect(slide, f"kanban-{n}-card-{j+1}-bg",
                               cx + 8, card_y, card_w, card_h, CARD_BG)
            card_bg.line.color.rgb = CARD_BORDER
            card_bg.line.width = 9525
            # Left accent bar
            if state == "ip":
                add_rect(slide, f"kanban-{n}-card-{j+1}-accent",
                         cx + 8, card_y, 3, card_h, BRAND_ACCENT_SOFT)
            elif state == "done":
                add_rect(slide, f"kanban-{n}-card-{j+1}-accent",
                         cx + 8, card_y, 3, card_h, GREEN)
            elif state == "blocked":
                add_rect(slide, f"kanban-{n}-card-{j+1}-accent",
                         cx + 8, card_y, 3, card_h, RED)
            # Title
            title_color = TEXT_MID if state == "done" else TEXT_DARK
            add_text(slide, f"kanban-{n}-card-{j+1}-title", title,
                     x_px=cx + 16, y_px=card_y + 4, w_px=card_w - 60, h_px=24,
                     font_size_px=10, color=title_color, bold=True)
            # Points
            add_text(slide, f"kanban-{n}-card-{j+1}-points", pts,
                     x_px=cx + card_w - 50, y_px=card_y + 4, w_px=44, h_px=16,
                     font_size_px=9, color=BRAND_PRIMARY_MID, bold=True, align="center",
                     bg_fill=CARD_BORDER, padding_px=(1, 4, 1, 4))
            # Epic chip
            bg, txt = EPIC_COLORS.get(epic, (CARD_BG, TEXT_MID))
            add_text(slide, f"kanban-{n}-card-{j+1}-epic", epic,
                     x_px=cx + 16, y_px=card_y + card_h - 22, w_px=60, h_px=14,
                     font_size_px=9, color=txt, bold=True, align="center",
                     bg_fill=bg, padding_px=(1, 5, 1, 5))
            if state == "blocked":
                add_text(slide, f"kanban-{n}-card-{j+1}-blocked",
                         "BLOCKED — awaiting vendor key",
                         x_px=cx + 16, y_px=card_y + card_h - 22 + 16, w_px=card_w - 32, h_px=12,
                         font_size_px=8, color=RED, bold=True, uppercase=True)
            card_y += card_h + 6

    add_footer(slide, page_num=192)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "192_agile-sprint-board.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
