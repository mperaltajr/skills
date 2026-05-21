"""
Builder for pattern 98: Quarterly board update — one-pager.

Source HTML: _pattern-library/98_quarterly-board-update.html

Header-bar variant (like 88) with top-line band, wins column, KPI tiles,
priorities, and ASK strip.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
    DRAFT_BG, DRAFT_TEXT,
)
from pptx.dml.color import RGBColor

RAG_GREEN = RGBColor(0x2E, 0xCC, 0x71)


def build():
    prs, slide = new_slide()


    # Header bar
    add_rect(slide, "header-bar", 0, 36, 1280, 68, BRAND_PRIMARY)
    add_text(slide, "title",
             "Q2 board update — pilot delivered, asking for Q3 expansion.",
             x_px=40, y_px=50, w_px=1200, h_px=44,
             font_size_px=22, color=WHITE, bold=True)
    add_rect(slide, "brand-rule", 0, 104, 1280, 4, BRAND_ACCENT)

    # Eyebrow + meta
    add_text(slide, "eyebrow", "Quarterly Board Update",
             x_px=40, y_px=120, w_px=400, h_px=14,
             font_size_px=12, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_text(slide, "eyebrow-meta", "Q2 2026 · Board Meeting",
             x_px=880, y_px=120, w_px=360, h_px=14,
             font_size_px=12, color=TEXT_MID, bold=True, align="right", uppercase=True)

    # Top-line band
    tl_y = 148
    tl_h = 56
    add_rect(slide, "topline", 40, tl_y, 1280 - 80, tl_h, BRAND_PRIMARY)
    add_rect(slide, "topline-accent", 40, tl_y, 4, tl_h, BRAND_ACCENT)
    add_text(slide, "topline-label", "TOP LINE",
             x_px=58, y_px=tl_y + 8, w_px=120, h_px=16,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "topline-text",
             "Pilot delivered all four success metrics. Asking for Q3 rollout greenlight to 3 practices.",
             x_px=58, y_px=tl_y + 26, w_px=1280 - 80 - 36, h_px=28,
             font_size_px=15, color=WHITE, bold=True)

    # LEFT: This quarter wins (top:230, width 720)
    left_x = 40
    left_y = 230
    left_w = 720
    left_h = 360

    add_text(slide, "wins-zone-icon", "✓",
             x_px=left_x, y_px=left_y, w_px=22, h_px=22,
             font_size_px=14, color=WHITE, bold=True, align="center",
             bg_fill=BRAND_PRIMARY, padding_px=(2, 4, 2, 4))
    add_text(slide, "wins-zone-title", "This Quarter",
             x_px=left_x + 30, y_px=left_y + 4, w_px=300, h_px=16,
             font_size_px=13, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_text(slide, "wins-zone-meta", "4 key wins",
             x_px=left_x + left_w - 120, y_px=left_y + 4, w_px=120, h_px=16,
             font_size_px=11, color=TEXT_MID, bold=True, align="right", uppercase=True)
    add_rect(slide, "wins-zone-divider", left_x, left_y + 28, left_w, 2, BRAND_PRIMARY)

    wins = [
        ("4-week pilot completed with all metrics green — no slippage, no escalations",
         "STATUS · ON TRACK"),
        ("−64% cycle time vs baseline — exceeded our −40% target by 24 points",
         "TARGET −40% · ACTUAL −64%"),
        ("94% first-review sign-off — above the 85% target, partners reviewing less",
         "TARGET 85% · ACTUAL 94%"),
        ("12 partner-ready decks delivered through pilot — all client-facing, zero rework",
         "12 DECKS · 0 REWORKS"),
    ]
    win_top = left_y + 42
    win_h = 70
    win_gap = 10
    for i, (text, metric) in enumerate(wins):
        n = i + 1
        wy = win_top + i * (win_h + win_gap)
        # Win row card
        wr = add_rect(slide, f"win-{n}-row", left_x, wy, left_w, win_h, CARD_BG)
        wr.line.color.rgb = CARD_BORDER
        wr.line.width = 9525
        # Left green accent
        add_rect(slide, f"win-{n}-accent", left_x, wy, 3, win_h, RAG_GREEN)
        # Check badge
        add_rect(slide, f"win-{n}-check", left_x + 14, wy + 14, 22, 22, RAG_GREEN)
        add_text(slide, f"win-{n}-check-glyph", "✓",
                 x_px=left_x + 14, y_px=wy + 14, w_px=22, h_px=22,
                 font_size_px=12, color=WHITE, bold=True,
                 align="center", anchor="middle")
        # Text
        add_text(slide, f"win-{n}-text", text,
                 x_px=left_x + 44, y_px=wy + 12, w_px=left_w - 60, h_px=34,
                 font_size_px=13, color=TEXT_DARK)
        add_text(slide, f"win-{n}-metric", metric,
                 x_px=left_x + 44, y_px=wy + 46, w_px=left_w - 60, h_px=16,
                 font_size_px=10, color=RAG_GREEN, bold=True, uppercase=True)

    # RIGHT-TOP: KPI tiles (top:230, left:780, w:460, h:180)
    rt_x = 780
    rt_y = 230
    rt_w = 460
    rt_h = 180

    add_text(slide, "metrics-zone-icon", "■",
             x_px=rt_x, y_px=rt_y, w_px=22, h_px=22,
             font_size_px=14, color=WHITE, bold=True, align="center",
             bg_fill=BRAND_PRIMARY, padding_px=(2, 4, 2, 4))
    add_text(slide, "metrics-zone-title", "Key Metrics",
             x_px=rt_x + 30, y_px=rt_y + 4, w_px=200, h_px=16,
             font_size_px=13, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_text(slide, "metrics-zone-meta", "Q2 Actuals",
             x_px=rt_x + rt_w - 120, y_px=rt_y + 4, w_px=120, h_px=16,
             font_size_px=11, color=TEXT_MID, bold=True, align="right", uppercase=True)
    add_rect(slide, "metrics-zone-divider", rt_x, rt_y + 28, rt_w, 2, BRAND_PRIMARY)

    # KPI grid 2x2
    kpis = [
        ("5", "d", "Cycle Time"),
        ("94", "%", "First-Review Sign-Off"),
        ("12", "", "Partner-Ready Decks"),
        ("$420", "K", "Annual Savings (Proj.)"),
    ]
    kpi_top = rt_y + 42
    kpi_h = 64
    kpi_gap = 8
    kpi_w = (rt_w - kpi_gap) // 2

    for i, (val, unit, label) in enumerate(kpis):
        n = i + 1
        row = i // 2
        col = i % 2
        kx = rt_x + col * (kpi_w + kpi_gap)
        ky = kpi_top + row * (kpi_h + kpi_gap)
        k = add_rect(slide, f"kpi-{n}", kx, ky, kpi_w, kpi_h, CARD_BG)
        k.line.color.rgb = CARD_BORDER
        k.line.width = 9525
        add_rect(slide, f"metric-{n}-accent", kx, ky, kpi_w, 3, BRAND_ACCENT)
        # Value
        add_text(slide, f"metric-{n}-value", val,
                 x_px=kx + 10, y_px=ky + 12, w_px=120, h_px=30,
                 font_size_px=26, color=BRAND_PRIMARY, bold=True)
        if unit:
            # Offset unit by estimated width of value (chars * font * 0.62) + pad
            unit_offset = int(len(val) * 26 * 0.62) + 4
            add_text(slide, f"metric-{n}-unit", unit,
                     x_px=kx + 10 + unit_offset, y_px=ky + 20,
                     w_px=40, h_px=20,
                     font_size_px=14, color=BRAND_ACCENT, bold=True)
        add_text(slide, f"metric-{n}-label", label,
                 x_px=kx + 10, y_px=ky + 42, w_px=kpi_w - 20, h_px=16,
                 font_size_px=10, color=TEXT_MID, bold=True, uppercase=True)

    # RIGHT-BOTTOM: Q3 priorities (top:430)
    rb_x = 780
    rb_y = 430
    rb_w = 460
    rb_h = 160

    add_text(slide, "priorities-zone-icon", "▶",
             x_px=rb_x, y_px=rb_y, w_px=22, h_px=22,
             font_size_px=14, color=WHITE, bold=True, align="center",
             bg_fill=BRAND_PRIMARY, padding_px=(2, 4, 2, 4))
    add_text(slide, "priorities-zone-title", "Next Quarter",
             x_px=rb_x + 30, y_px=rb_y + 4, w_px=200, h_px=16,
             font_size_px=13, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_text(slide, "priorities-zone-meta", "Q3 Priorities",
             x_px=rb_x + rb_w - 130, y_px=rb_y + 4, w_px=130, h_px=16,
             font_size_px=11, color=TEXT_MID, bold=True, align="right", uppercase=True)
    add_rect(slide, "priorities-zone-divider", rb_x, rb_y + 28, rb_w, 2, BRAND_PRIMARY)

    priorities = [
        "Roll out to 3 additional practices",
        "Build out pattern library to 150",
        "Certify 6 senior coaches",
    ]
    pri_top = rb_y + 42
    pri_h = 32
    pri_gap = 7
    for i, text in enumerate(priorities):
        n = i + 1
        py = pri_top + i * (pri_h + pri_gap)
        p = add_rect(slide, f"priority-{n}", rb_x, py, rb_w, pri_h, WHITE)
        p.line.color.rgb = CARD_BORDER
        p.line.width = 9525
        add_rect(slide, f"priority-{n}-accent", rb_x, py, 3, pri_h, BRAND_ACCENT)
        # Numbered circle
        add_rect(slide, f"priority-{n}-num-bg", rb_x + 12, py + 5, 22, 22, BRAND_ACCENT)
        add_text(slide, f"priority-{n}-num", str(n),
                 x_px=rb_x + 12, y_px=py + 5, w_px=22, h_px=22,
                 font_size_px=12, color=WHITE, bold=True,
                 align="center", anchor="middle")
        add_text(slide, f"priority-{n}-text", text,
                 x_px=rb_x + 42, y_px=py + 7, w_px=rb_w - 56, h_px=20,
                 font_size_px=12, color=TEXT_DARK, bold=True)

    # ASK strip
    ask_rule_y = 720 - 108
    add_rect(slide, "ask-rule", 40, ask_rule_y, 1280 - 80, 2, BRAND_ACCENT)
    ask_y = 720 - 56 - 50
    ask_h = 50
    add_rect(slide, "primary-ask-bg", 40, ask_y, 1280 - 80, ask_h, BRAND_PRIMARY)
    add_rect(slide, "primary-ask-accent", 40, ask_y, 4, ask_h, BRAND_ACCENT)
    add_text(slide, "primary-ask-label", "ASK FROM THE BOARD",
             x_px=58, y_px=ask_y + 16, w_px=180, h_px=18,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(
        slide, "primary-ask-text",
        "Approve Q3 rollout budget of $80K and 3 practice champions.",
        x_px=250, y_px=ask_y, w_px=1280 - 80 - 220, h_px=ask_h,
        font_size_px=14, color=WHITE, italic=True, bold=True, anchor="middle",
    )

    add_footer(slide, page_num=98)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "98_quarterly-board-update.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
