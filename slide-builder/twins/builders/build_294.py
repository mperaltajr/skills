"""
Builder for pattern 294: Where we go from here (dark).

Left panel: section label + headline + 3 numbered action items.
Right panel: phased roadmap with arrow + 3 milestones.

Source HTML: _pattern-library/294_where-we-go-from-here-dark.html
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
NUMBER_BG = RGBColor(0x4A, 0x29, 0x76)
DIVIDER = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Canonical chrome
    add_text(slide, "title",
             "Where We Go From <strong>Here</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Three near-term actions and the phased roadmap behind them",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 80, 3, BRAND_ACCENT_SOFT)

    # Two-panel body
    body_top = 220
    body_bot = 680
    left_x = 48
    left_w = 660
    right_x = 740
    right_w = 1232 - right_x
    divider_x = 720

    # Divider
    add_rect(slide, "panel-divider", divider_x, body_top, 1, body_bot - body_top - 30, DIVIDER)

    # LEFT
    add_text(slide, "section-label", "WHERE WE GO FROM HERE",
             x_px=left_x, y_px=body_top, w_px=left_w, h_px=18,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=3)

    add_text(slide, "headline",
             "Three actions to <strong>unlock value</strong>",
             x_px=left_x, y_px=body_top + 24, w_px=left_w, h_px=70,
             font_size_px=24, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT)

    # 3 action items
    actions = [
        ("Align on a single operating model",
         "Consolidate fragmented processes into one authoritative framework owned by a cross-functional steering group."),
        ("Instrument the data pipeline end-to-end",
         "Deploy lightweight telemetry at each handoff point so latency and quality gaps become immediately visible."),
        ("Scale the pilot to two additional regions",
         "Apply learnings from the EMEA pilot to APAC and NAM with adapted change management and local governance."),
    ]
    actions_top = body_top + 120
    actions_bot = body_bot - 20
    a_h = (actions_bot - actions_top) // 3

    # Dotted vertical connector
    for i in range(0, a_h * 3, 8):
        add_rect(slide, f"connector-{i}", left_x + 17, actions_top + 30 + i, 2, 4,
                 RGBColor(0x6B, 0x2B, 0xA8))

    for i, (ttl, desc) in enumerate(actions):
        ay = actions_top + i * a_h
        # Number circle
        num_y = ay + 14
        add_rect(slide, f"action-{i+1}-dot", left_x + 12, num_y + 8, 14, 14, BRAND_ACCENT)
        # Large faded number background
        add_text(slide, f"action-{i+1}-number-bg", str(i + 1),
                 x_px=left_x, y_px=ay, w_px=46, h_px=60,
                 font_size_px=44, color=RGBColor(0x55, 0x36, 0x77), bold=True, align="center")
        # Content
        add_text(slide, f"action-{i+1}-title", ttl,
                 x_px=left_x + 56, y_px=ay + 8, w_px=left_w - 60, h_px=24,
                 font_size_px=14, color=WHITE, bold=True)
        add_text(slide, f"action-{i+1}-desc", desc,
                 x_px=left_x + 56, y_px=ay + 32, w_px=left_w - 60, h_px=a_h - 36,
                 font_size_px=11, color=TEXT_ON_DARK_MID)

    # RIGHT — phased roadmap
    add_text(slide, "timeline-label", "PHASED ROADMAP",
             x_px=right_x + 60, y_px=body_top + 60, w_px=right_w - 60, h_px=16,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, letter_spacing_px=2.5)

    arrow_x = right_x + 24
    arrow_top = body_top + 100
    arrow_bot = body_bot - 30
    # Arrow head (triangle approximated as text)
    add_text(slide, "arrow-head", "▼",
             x_px=arrow_x - 10, y_px=arrow_bot - 16, w_px=24, h_px=18,
             font_size_px=18, color=BRAND_ACCENT, align="center")
    # Arrow shaft
    add_rect(slide, "arrow-shaft", arrow_x + 1, arrow_top, 3, arrow_bot - arrow_top - 14, BRAND_ACCENT)

    # 3 milestones — order: Now (top), 30 Days (mid), 90 Days (bottom)
    milestones = [
        ("NOW", "Steering group chartered; operating model draft circulated for sign-off."),
        ("30 DAYS", "Telemetry deployed; first data-quality dashboard published to stakeholders."),
        ("90 DAYS", "Scaled model live in two regions; KPIs reported to executive board."),
    ]
    m_top = arrow_top
    m_bot = arrow_bot - 20
    m_h = (m_bot - m_top) // 3
    for i, (period, outcome) in enumerate(milestones):
        my = m_top + i * m_h
        # Node on arrow
        add_rect(slide, f"milestone-{i+1}-node", arrow_x - 6, my + 4, 14, 14, BRAND_ACCENT)
        # Pip
        add_rect(slide, f"milestone-{i+1}-pip", right_x + 56, my + 4, 6, 6, BRAND_ACCENT)
        add_text(slide, f"milestone-{i+1}-period", period,
                 x_px=right_x + 70, y_px=my, w_px=200, h_px=18,
                 font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1.5)
        add_text(slide, f"milestone-{i+1}-outcome", outcome,
                 x_px=right_x + 70, y_px=my + 22, w_px=right_w - 80, h_px=m_h - 28,
                 font_size_px=12, color=TEXT_ON_DARK_MID)

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "294",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "294_where-we-go-from-here-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
