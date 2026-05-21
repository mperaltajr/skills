"""
Builder for pattern 196d: Pilot Results Summary — DARK variant.

Light source: twins/builders/build_196.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

GREEN = RGBColor(0x4A, 0xDE, 0x80)
GREEN_BG = RGBColor(0x06, 0x5F, 0x46)
GREEN_TXT = RGBColor(0xD7, 0xF1, 0xDA)
WORKED_BG = RGBColor(0x0F, 0x3F, 0x2A)
WORKED_BORDER = RGBColor(0x1F, 0x5F, 0x45)
WORKED_BADGE = RGBColor(0x4A, 0xDE, 0x80)
WORKED_BADGE_TXT = RGBColor(0x0F, 0x3F, 0x2A)
IMPROVE_BG = RGBColor(0x44, 0x33, 0x10)
IMPROVE_BORDER = RGBColor(0x78, 0x55, 0x1F)
IMPROVE_BADGE = RGBColor(0xFB, 0xBF, 0x24)
IMPROVE_BADGE_TXT = RGBColor(0x44, 0x33, 0x10)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Pilot <strong>Results</strong> Summary",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Performance outcomes, qualitative findings, and lessons learned from the field pilot",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    strip_top = 220
    add_text(slide, "pilot-strip-label", "PILOT OVERVIEW",
             x_px=64, y_px=strip_top + 4, w_px=110, h_px=16,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True)
    meta = [
        ("Location", "Northeast Region — 4 Sites"),
        ("Duration", "8 Weeks (Mar – May 2026)"),
        ("Participants", "142 End Users · 6 Admins"),
    ]
    chip_x = 184
    for i, (label, val) in enumerate(meta):
        chip_w = 320
        cx = chip_x + i * (chip_w + 8)
        chip = add_rect(slide, f"pilot-meta-{i+1}-chip", cx, strip_top, chip_w, 24, CARD_BG_DARK)
        chip.line.color.rgb = CARD_BORDER_DARK
        chip.line.width = 9525
        add_text(slide, f"pilot-meta-{i+1}-label", label,
                 x_px=cx + 12, y_px=strip_top + 5, w_px=70, h_px=14,
                 font_size_px=10, color=TEXT_ON_DARK_FAINT)
        add_text(slide, f"pilot-meta-{i+1}-value", val,
                 x_px=cx + 84, y_px=strip_top + 5, w_px=chip_w - 96, h_px=14,
                 font_size_px=10, color=WHITE, bold=True)

    body_top = 260
    body_bot = 600
    col_w = (1280 - 128 - 32) // 3
    col_gap = 16

    cx1 = 64
    add_text(slide, "col-1-header", "QUANTITATIVE RESULTS",
             x_px=cx1, y_px=body_top, w_px=col_w, h_px=18,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_rect(slide, "col-1-rule", cx1, body_top + 20, col_w, 2, CARD_BORDER_DARK)
    metrics = [
        ("Process Cycle Time", "14.2 days", "8.7 days", "▲ 39%"),
        ("Error Rate (per 1,000 transactions)", "23.1", "9.4", "▲ 59%"),
        ("User Satisfaction Score (NPS)", "+18", "+54", "▲ 200%"),
    ]
    mt = body_top + 36
    row_h = 64
    for i, (label, before, after, delta) in enumerate(metrics):
        ry = mt + i * row_h
        row = add_rect(slide, f"metric-{i+1}-bg", cx1, ry, col_w, row_h - 8, CARD_BG_DARK)
        row.line.color.rgb = CARD_BORDER_DARK
        row.line.width = 9525
        add_text(slide, f"metric-{i+1}-label", label,
                 x_px=cx1 + 10, y_px=ry + 10, w_px=col_w - 160, h_px=36,
                 font_size_px=10, color=WHITE, bold=True)
        add_text(slide, f"metric-{i+1}-before", before,
                 x_px=cx1 + col_w - 150, y_px=ry + 8, w_px=80, h_px=14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, align="right")
        add_text(slide, f"metric-{i+1}-value", after,
                 x_px=cx1 + col_w - 150, y_px=ry + 22, w_px=80, h_px=16,
                 font_size_px=13, color=BRAND_ACCENT_SOFT, bold=True, align="right")
        add_text(slide, f"metric-{i+1}-delta", delta,
                 x_px=cx1 + col_w - 60, y_px=ry + 18, w_px=52, h_px=16,
                 font_size_px=9, color=GREEN_TXT, bold=True, align="center",
                 bg_fill=GREEN_BG, padding_px=(2, 4, 2, 4))

    cx2 = cx1 + col_w + col_gap
    add_text(slide, "col-2-header", "QUALITATIVE FINDINGS",
             x_px=cx2, y_px=body_top, w_px=col_w, h_px=18,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_rect(slide, "col-2-rule", cx2, body_top + 20, col_w, 2, CARD_BORDER_DARK)
    quals = [
        ("✓", "Frontline staff found the redesigned workflow significantly easier to navigate — onboarding time dropped by half in observed sessions."),
        ("✓", "Integration with existing ERP required minimal rework; IT teams rated the deployment complexity as \"lower than expected\" in exit interviews."),
        ("△", "Exception-handling for edge cases (legacy vendor codes) required manual intervention in ~7% of transactions — volume is manageable but warrants automation."),
    ]
    for i, (icon, txt) in enumerate(quals):
        ry = mt + i * row_h
        row = add_rect(slide, f"qual-{i+1}-bg", cx2, ry, col_w, row_h - 8, CARD_BG_DARK)
        row.line.color.rgb = CARD_BORDER_DARK
        row.line.width = 9525
        add_text(slide, f"qual-{i+1}-icon", icon,
                 x_px=cx2 + 8, y_px=ry + 8, w_px=20, h_px=20,
                 font_size_px=13, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"qual-{i+1}-text", txt,
                 x_px=cx2 + 32, y_px=ry + 6, w_px=col_w - 40, h_px=48,
                 font_size_px=10, color=TEXT_ON_DARK_MID)

    cx3 = cx2 + col_w + col_gap
    add_text(slide, "col-3-header", "LESSONS LEARNED",
             x_px=cx3, y_px=body_top, w_px=col_w, h_px=18,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_rect(slide, "col-3-rule", cx3, body_top + 20, col_w, 2, CARD_BORDER_DARK)
    lessons = [
        ("worked", "What worked", "Dedicated change-champion network accelerated adoption in sites 2 and 3 by mobilising peer-to-peer coaching."),
        ("worked", "What worked", "Phased data migration reduced go-live risk; zero critical data-loss incidents recorded across all four sites."),
        ("improve", "To improve", "Expand exception-rule library before full rollout to reduce manual overrides; assign a dedicated triage owner per region."),
    ]
    for i, (kind, badge, txt) in enumerate(lessons):
        ry = mt + i * row_h
        if kind == "worked":
            bgc = WORKED_BG; border = WORKED_BORDER; badge_bg = WORKED_BADGE; badge_txt = WORKED_BADGE_TXT
        else:
            bgc = IMPROVE_BG; border = IMPROVE_BORDER; badge_bg = IMPROVE_BADGE; badge_txt = IMPROVE_BADGE_TXT
        row = add_rect(slide, f"lesson-{i+1}-bg", cx3, ry, col_w, row_h - 8, bgc)
        row.line.color.rgb = border
        row.line.width = 9525
        add_text(slide, f"lesson-{i+1}-badge", badge,
                 x_px=cx3 + 10, y_px=ry + 8, w_px=86, h_px=14,
                 font_size_px=8, color=badge_txt, bold=True, align="center", uppercase=True,
                 bg_fill=badge_bg, padding_px=(2, 4, 2, 4))
        add_text(slide, f"lesson-{i+1}-text", txt,
                 x_px=cx3 + 10, y_px=ry + 28, w_px=col_w - 20, h_px=28,
                 font_size_px=11, color=WHITE)

    rec_y = 612
    add_rect(slide, "convergence-bg", 64, rec_y, 1280 - 128, 38, CARD_BG_DARK)
    add_rect(slide, "convergence-accent", 64, rec_y, 4, 38, BRAND_ACCENT_SOFT)
    add_text(slide, "convergence-mark", "RECOMMENDATION",
             x_px=78, y_px=rec_y + 4, w_px=120, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "convergence",
             "Proceed to full rollout — pilot results meet all success thresholds. Incorporate 2 modifications before scale-up.",
             x_px=200, y_px=rec_y + 4, w_px=1280 - 64 - 200, h_px=16,
             font_size_px=12, color=WHITE, bold=True)
    add_text(slide, "rec-mod-1",
             "• Automate legacy vendor-code exception handling prior to Wave 2 launch",
             x_px=200, y_px=rec_y + 20, w_px=540, h_px=14,
             font_size_px=10, color=TEXT_ON_DARK_MID)
    add_text(slide, "rec-mod-2",
             "• Replicate change-champion model across all remaining regions",
             x_px=750, y_px=rec_y + 20, w_px=440, h_px=14,
             font_size_px=10, color=TEXT_ON_DARK_MID)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "196",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "196d_pilot-results-summary-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
