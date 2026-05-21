"""
Builder for pattern 88d: Status report — executive summary — dark variant.

Source HTML: _pattern-library/88_status-report-exec-summary-dark.html
Light template: twins/builders/build_88.py

Variant: brand-primary slide bg + brand-primary-mid header band so the band
remains visible against the dark slide. Light text throughout.
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

RAG_GREEN = RGBColor(0x2E, 0xCC, 0x71)
RAG_GREEN_SOFT = RGBColor(0x14, 0x4D, 0x2E)
RAG_AMBER = RGBColor(0xF3, 0x9C, 0x12)
RAG_RED = RGBColor(0xDC, 0x26, 0x26)
RAG_RED_BG = RGBColor(0x4A, 0x1B, 0x2A)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Header bar — use primary-mid so it reads as a band on dark bg
    add_rect(slide, "header-bar", 0, 36, 1280, 68, BRAND_PRIMARY_MID)
    add_text(slide, "title",
             "Pilot status · Week 3 · Green overall, three decisions needed.",
             x_px=40, y_px=42, w_px=1200, h_px=58,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_rect(slide, "brand-rule", 0, 104, 1280, 4, BRAND_ACCENT)

    # Eyebrow + meta
    add_text(slide, "eyebrow", "Executive Summary",
             x_px=40, y_px=120, w_px=400, h_px=14,
             font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "eyebrow-meta", "Week 3 of 4 · Steering Committee",
             x_px=880, y_px=120, w_px=360, h_px=14,
             font_size_px=12, color=TEXT_ON_DARK_MID, bold=True, align="right", uppercase=True)

    quads = {
        "tl": (40, 148, 590, 220, "Overall Status", "Week 3 of 4", BRAND_PRIMARY_MID, BRAND_ACCENT_SOFT),
        "tr": (650, 148, 590, 220, "Key Wins This Period", "4 wins", BRAND_PRIMARY_MID, BRAND_ACCENT_SOFT),
        "bl": (40, 384, 590, 232, "Key Risks", "3 open", RAG_RED, RGBColor(0xFF, 0xC8, 0xC8)),
        "br": (650, 384, 590, 232, "Decisions Needed", "3 asks", BRAND_ACCENT, BRAND_ACCENT_SOFT),
    }

    for pos, (x, y, w, h, name, meta, head_color, meta_color) in quads.items():
        body_color = RAG_RED_BG if pos == "bl" else CARD_BG_DARK
        outer = add_rect(slide, f"quadrant-{pos}", x, y, w, h, body_color)
        outer.line.color.rgb = CARD_BORDER_DARK
        outer.line.width = 9525
        add_rect(slide, f"quad-{pos}-head", x, y, w, 40, head_color)
        add_text(slide, f"quadrant-{pos}-name", name,
                 x_px=x + 36, y_px=y + 12, w_px=w - 120, h_px=18,
                 font_size_px=13, color=WHITE, bold=True, uppercase=True)
        add_rect(slide, f"quad-{pos}-icon", x + 14, y + 14, 14, 14, meta_color)
        add_text(slide, f"quad-{pos}-meta", meta,
                 x_px=x + w - 130, y_px=y + 12, w_px=120, h_px=18,
                 font_size_px=11, color=meta_color, bold=True, align="right", uppercase=True)

    # TL body
    tl_x, tl_y, tl_w, tl_h = 40, 148, 590, 220
    body_top = tl_y + 40
    add_rect(slide, "quadrant-tl-rag-dot", tl_x + 24, body_top + 24, 56, 56, RAG_GREEN)
    add_text(slide, "quadrant-tl-rag-label", "GREEN",
             x_px=tl_x + 96, y_px=body_top + 22, w_px=200, h_px=30,
             font_size_px=22, color=RAG_GREEN, bold=True, uppercase=True)
    add_text(slide, "quadrant-tl-rag-status", "On Track",
             x_px=tl_x + 96, y_px=body_top + 54, w_px=200, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_MID, bold=True, uppercase=True)
    add_text(slide, "quadrant-tl-body",
             "Pilot on track for all 4 success metrics. No escalations this week. Wave 2 scope ready for steering approval.",
             x_px=tl_x + 24, y_px=body_top + 100, w_px=tl_w - 48, h_px=80,
             font_size_px=13, color=WHITE)

    # TR body
    tr_x, tr_y, tr_w, tr_h = 650, 148, 590, 220
    wins = [
        "Cycle time −64% vs baseline — exceeded 50% target",
        "94% first-review sign-off — target was 85%",
        "All 4 pilot users actively engaged, no drop-offs",
        "Pattern library at 80 patterns; on track for 100 by EOM",
    ]
    win_top = tr_y + 50
    for i, w in enumerate(wins):
        wy = win_top + i * 36
        add_text(slide, f"quadrant-tr-bullet-{i+1}-glyph", "✓",
                 x_px=tr_x + 14, y_px=wy + 2, w_px=18, h_px=18,
                 font_size_px=14, color=RAG_GREEN, bold=True, align="center")
        add_text(slide, f"quadrant-tr-bullet-{i+1}", w,
                 x_px=tr_x + 36, y_px=wy, w_px=tr_w - 50, h_px=32,
                 font_size_px=12, color=WHITE)
    add_text(slide, "quadrant-tr-body", "",
             x_px=tr_x + 12, y_px=win_top, w_px=tr_w - 24, h_px=tr_h - 48)

    # BL body
    bl_x, bl_y, bl_w, bl_h = 40, 384, 590, 232
    risks = [
        ("Amber: 2 senior managers still ramping — coaching scheduled this week", RAG_AMBER),
        ("Amber: CFO transition mid-pilot — stakeholder re-alignment underway", RAG_AMBER),
        ("Red: IT provisioning for Wave 2 not started — blocks 6/1 kickoff", RAG_RED),
        ("Amber: Vendor SOW renewal lagging — legal review still pending", RAG_AMBER),
    ]
    risk_top = bl_y + 50
    for i, (rtext, color) in enumerate(risks):
        ry = risk_top + i * 40
        add_text(slide, f"quadrant-bl-bullet-{i+1}-glyph", "⚑",
                 x_px=bl_x + 14, y_px=ry + 2, w_px=18, h_px=18,
                 font_size_px=14, color=color, bold=True, align="center")
        add_text(slide, f"quadrant-bl-bullet-{i+1}", rtext,
                 x_px=bl_x + 36, y_px=ry, w_px=bl_w - 50, h_px=36,
                 font_size_px=12, color=WHITE)
    add_text(slide, "quadrant-bl-body", "",
             x_px=bl_x + 12, y_px=risk_top, w_px=bl_w - 24, h_px=bl_h - 48)

    # BR body
    br_x, br_y, br_w, br_h = 650, 384, 590, 232
    asks = [
        ("Approve Wave 2 scope (+12 users, 3 new use cases)", "Mario · by Fri"),
        ("Greenlight pattern library investment to 100 patterns", "MD · by Fri"),
        ("Hire 1 designer-engineer to sustain pattern velocity", "HR · by next week"),
    ]
    ask_top = br_y + 50
    card_h = 42
    stride = 48
    for i, (ask, owner) in enumerate(asks):
        n = i + 1
        ay = ask_top + i * stride
        dcard = add_rect(slide, f"sub-ask-{n}", br_x + 14, ay, br_w - 28, card_h, BRAND_PRIMARY)
        dcard.line.color.rgb = CARD_BORDER_DARK
        dcard.line.width = 9525
        add_rect(slide, f"sub-ask-{n}-accent", br_x + 14, ay, 3, card_h, BRAND_ACCENT)
        add_rect(slide, f"sub-ask-{n}-num-bg", br_x + 26, ay + 10, 22, 22, BRAND_ACCENT)
        add_text(slide, f"sub-ask-{n}-num", str(n),
                 x_px=br_x + 26, y_px=ay + 10, w_px=22, h_px=22,
                 font_size_px=12, color=WHITE, bold=True, align="center", anchor="middle")
        add_text(slide, f"sub-ask-{n}-body", ask,
                 x_px=br_x + 56, y_px=ay + 4, w_px=br_w - 80, h_px=20,
                 font_size_px=12, color=WHITE, bold=True)
        add_text(slide, f"sub-ask-{n}-meta", owner,
                 x_px=br_x + 56, y_px=ay + 22, w_px=br_w - 80, h_px=16,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)

    # Convergence
    conv_y = 720 - 56 - 40
    conv_h = 40
    add_rect(slide, "convergence-bg", 40, conv_y, 1280 - 80, conv_h, BRAND_PRIMARY_MID)
    add_rect(slide, "convergence-accent", 40, conv_y, 3, conv_h, BRAND_ACCENT)
    add_text(slide, "convergence",
             "Three items need MD decision by Friday — without them, Wave 2 slips two weeks.",
             x_px=40 + 18, y_px=conv_y, w_px=1280 - 80 - 36, h_px=conv_h,
             font_size_px=13, color=WHITE, italic=True, bold=True, anchor="middle")

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "88",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "88d_status-report-exec-summary-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
