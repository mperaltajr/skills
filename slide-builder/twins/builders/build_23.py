"""
Builder for pattern 23: Account scorecard — RAG grid.

Source HTML: _pattern-library/23_account-scorecard-rag-grid.html

Variant chrome — title sits inside a brand-primary header bar at top, no
standard title block. 2x2 grid of program cards, each with a RAG-coloured
status dot and pill.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

RAG_GREEN = RGBColor(0x2E, 0xCC, 0x71)
RAG_AMBER = RGBColor(0xF3, 0x9C, 0x12)
RAG_RED = RGBColor(0xDC, 0x26, 0x26)
AMBER_BG = RGBColor(0xFF, 0xFB, 0xF4)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Brand header bar (replaces standard title block) — sits below chrome
    add_rect(slide, "title-band", x_px=0, y_px=44, w_px=1280, h_px=68, fill_color=BRAND_PRIMARY)
    add_text(
        slide, "title", "Account scorecard — Q3 FY26 program health",
        x_px=40, y_px=58, w_px=1100, h_px=44,
        font_size_px=22, color=WHITE, bold=True, anchor="middle",
    )
    add_rect(slide, "brand-rule", x_px=0, y_px=112, w_px=1280, h_px=4, fill_color=BRAND_ACCENT)

    # Eyebrow under the band
    add_text(
        slide, "eyebrow", "PROGRAM HEALTH",
        x_px=40, y_px=120, w_px=400, h_px=14,
        font_size_px=12, color=BRAND_PRIMARY, bold=True, uppercase=True,
    )

    # 2x2 grid of program cards
    card_w = 590
    grid_left = 40
    grid_x2 = 650
    card_top = 148
    card_h_top = 246
    card_h_bot = 232
    card_top_bot = 410

    card_data = [
        # (positional, name, rag, body_amber, eyebrow, body_lines)
        ("card-1", "Prometheus", "green", False, "Key Highlights", [
            "› 1,000+ automation use cases; 42% deployed across 14 archetypes",
            "› MS 2.0 pre-requisites complete — go-live confirmed 3/16",
            "› 85%+ MS activation; final 15% on track for Q3 close",
            "› GenAI: 3,800+ GitHub Copilot users active",
        ]),
        ("card-2", "Fairway — EU Mod", "amber", True, "Key Highlights", [
            "› SIT complete; UAT3 starting — 3-week slip risk on cutover",
            "› TSA Exit planning initiated; resourcing gap flagged for steering",
            "› Go-live May 5th — contingency plan for May 19th",
            "› 16 weeks to production; cutover events on schedule",
        ]),
        ("card-3", "Journey 2 Cloud", "green", False, "Key Highlights", [
            "› 45 resources mobilized; Phase 1 design approved",
            "› Phase 2 architecture underway — Q4 FY26 migration start",
            "› $7.9M FY26 benefit on track; no material blockers",
        ]),
        ("card-4", "Tech Mod / Hire-to-Retire", "amber", True, "Key Highlights", [
            "› Joint Mod Council established; governance guardrails pending",
            "› AIQ: 10,000+ courses complete; exec 1:1 coaching active",
            "› Portfolio modernization — benefit at risk without Q3 decision",
        ]),
    ]

    rag_colors = {"green": RAG_GREEN, "amber": RAG_AMBER, "red": RAG_RED}
    rag_labels = {"green": "On Track", "amber": "At Risk", "red": "Off Track"}

    for i, (prefix, name, rag, amber_body, sub_label, lines) in enumerate(card_data):
        n = i + 1
        col = i % 2
        row = i // 2
        cx = grid_left if col == 0 else grid_x2
        cy = card_top if row == 0 else card_top_bot
        ch = card_h_top if row == 0 else card_h_bot

        # Card border
        card = add_rect(slide, f"{prefix}-bg", cx, cy, card_w, ch, WHITE)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525

        # Head (brand-primary band, height 42)
        head_h = 42
        add_rect(slide, f"{prefix}-head", cx, cy, card_w, head_h, BRAND_PRIMARY)
        # RAG dot
        dot_color = rag_colors[rag]
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            px_to_emu(cx + 16), px_to_emu(cy + 15),
            px_to_emu(12), px_to_emu(12),
        )
        dot.name = f"{prefix}-rag-dot"
        dot.fill.solid()
        dot.fill.fore_color.rgb = dot_color
        dot.line.fill.background()
        # Program name (white)
        add_text(
            slide, f"{prefix}-heading", name,
            x_px=cx + 40, y_px=cy + 10, w_px=card_w - 160, h_px=24,
            font_size_px=15, color=WHITE, bold=True,
        )
        # RAG label (colored, right-aligned)
        add_text(
            slide, f"{prefix}-rag-pill-text", rag_labels[rag],
            x_px=cx + card_w - 130, y_px=cy + 12, w_px=120, h_px=20,
            font_size_px=13, color=dot_color, bold=True,
            align="right", uppercase=True,
        )

        # Body
        body_bg = AMBER_BG if amber_body else CARD_BG
        add_rect(slide, f"{prefix}-body-bg", cx + 1, cy + head_h, card_w - 2, ch - head_h - 1, body_bg)

        # Sub-label
        add_text(
            slide, f"{prefix}-eyebrow", sub_label.upper(),
            x_px=cx + 16, y_px=cy + head_h + 12, w_px=card_w - 32, h_px=14,
            font_size_px=11, color=BRAND_PRIMARY, bold=True, uppercase=True,
        )

        # Bullets
        body_text = "\n".join(lines)
        add_text(
            slide, f"{prefix}-body", body_text,
            x_px=cx + 16, y_px=cy + head_h + 32, w_px=card_w - 32, h_px=ch - head_h - 42,
            font_size_px=12, color=TEXT_DARK,
        )

    add_footer(slide, page_num=23)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "23_account-scorecard-rag-grid.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
