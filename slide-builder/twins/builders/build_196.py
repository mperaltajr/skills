"""
Builder for pattern 196: Pilot Results Summary.

3-column body (Quantitative / Qualitative / Lessons Learned) + pilot overview
meta strip + recommendation bar.

Source HTML: _pattern-library/196_pilot-results-summary.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

GREEN_BG = RGBColor(0xDC, 0xFC, 0xE7)
GREEN_TXT = RGBColor(0x16, 0x65, 0x34)
WORKED_BG = RGBColor(0xF0, 0xFD, 0xF4)
WORKED_BORDER = RGBColor(0xBB, 0xF7, 0xD0)
WORKED_BADGE = RGBColor(0xBB, 0xF7, 0xD0)
WORKED_BADGE_TXT = RGBColor(0x14, 0x53, 0x2D)
IMPROVE_BG = RGBColor(0xFF, 0xFB, 0xEB)
IMPROVE_BORDER = RGBColor(0xFD, 0xE6, 0x8A)
IMPROVE_BADGE = RGBColor(0xFD, 0xE6, 0x8A)
IMPROVE_BADGE_TXT = RGBColor(0x78, 0x35, 0x0F)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Pilot <strong>Results</strong> Summary",
        subtitle="Performance outcomes, qualitative findings, and lessons learned from the field pilot",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    # Pilot strip
    strip_top = 160
    add_text(slide, "pilot-strip-label", "PILOT OVERVIEW",
             x_px=64, y_px=strip_top + 4, w_px=110, h_px=16,
             font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True)
    meta = [
        ("Location", "Northeast Region — 4 Sites"),
        ("Duration", "8 Weeks (Mar – May 2026)"),
        ("Participants", "142 End Users · 6 Admins"),
    ]
    chip_x = 184
    for i, (label, val) in enumerate(meta):
        chip_w = 320
        cx = chip_x + i * (chip_w + 8)
        chip = add_rect(slide, f"pilot-meta-{i+1}-chip", cx, strip_top, chip_w, 24, CARD_BG)
        chip.line.color.rgb = CARD_BORDER
        chip.line.width = 9525
        add_text(slide, f"pilot-meta-{i+1}-label", label,
                 x_px=cx + 12, y_px=strip_top + 5, w_px=70, h_px=14,
                 font_size_px=10, color=TEXT_FAINT)
        add_text(slide, f"pilot-meta-{i+1}-value", val,
                 x_px=cx + 84, y_px=strip_top + 5, w_px=chip_w - 96, h_px=14,
                 font_size_px=10, color=TEXT_DARK, bold=True)

    # 3 body columns
    body_top = 200
    body_bot = 540
    body_h = body_bot - body_top
    col_w = (1280 - 128 - 32) // 3
    col_gap = 16

    # Col 1: Quantitative
    cx1 = 64
    add_text(slide, "col-1-header", "QUANTITATIVE RESULTS",
             x_px=cx1, y_px=body_top, w_px=col_w, h_px=18,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
    add_rect(slide, "col-1-rule", cx1, body_top + 20, col_w, 2, CARD_BORDER)
    metrics = [
        ("Process Cycle Time", "14.2 days", "8.7 days", "▲ 39%"),
        ("Error Rate (per 1,000 transactions)", "23.1", "9.4", "▲ 59%"),
        ("User Satisfaction Score (NPS)", "+18", "+54", "▲ 200%"),
    ]
    mt = body_top + 36
    row_h = 64
    for i, (label, before, after, delta) in enumerate(metrics):
        ry = mt + i * row_h
        row = add_rect(slide, f"metric-{i+1}-bg", cx1, ry, col_w, row_h - 8, CARD_BG)
        row.line.color.rgb = CARD_BORDER
        row.line.width = 9525
        add_text(slide, f"metric-{i+1}-label", label,
                 x_px=cx1 + 10, y_px=ry + 10, w_px=col_w - 160, h_px=36,
                 font_size_px=10, color=TEXT_DARK, bold=True)
        add_text(slide, f"metric-{i+1}-before", before,
                 x_px=cx1 + col_w - 150, y_px=ry + 8, w_px=80, h_px=14,
                 font_size_px=9, color=TEXT_FAINT, align="right")
        add_text(slide, f"metric-{i+1}-value", after,
                 x_px=cx1 + col_w - 150, y_px=ry + 22, w_px=80, h_px=16,
                 font_size_px=13, color=BRAND_PRIMARY, bold=True, align="right")
        add_text(slide, f"metric-{i+1}-delta", delta,
                 x_px=cx1 + col_w - 60, y_px=ry + 18, w_px=52, h_px=16,
                 font_size_px=9, color=GREEN_TXT, bold=True, align="center",
                 bg_fill=GREEN_BG, padding_px=(2, 4, 2, 4))

    # Col 2: Qualitative
    cx2 = cx1 + col_w + col_gap
    add_text(slide, "col-2-header", "QUALITATIVE FINDINGS",
             x_px=cx2, y_px=body_top, w_px=col_w, h_px=18,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
    add_rect(slide, "col-2-rule", cx2, body_top + 20, col_w, 2, CARD_BORDER)
    quals = [
        ("✓", "Frontline staff found the redesigned workflow significantly easier to navigate — onboarding time dropped by half in observed sessions."),
        ("✓", "Integration with existing ERP required minimal rework; IT teams rated the deployment complexity as \"lower than expected\" in exit interviews."),
        ("△", "Exception-handling for edge cases (legacy vendor codes) required manual intervention in ~7% of transactions — volume is manageable but warrants automation."),
    ]
    for i, (icon, txt) in enumerate(quals):
        ry = mt + i * row_h
        row = add_rect(slide, f"qual-{i+1}-bg", cx2, ry, col_w, row_h - 8, CARD_BG)
        row.line.color.rgb = CARD_BORDER
        row.line.width = 9525
        add_text(slide, f"qual-{i+1}-icon", icon,
                 x_px=cx2 + 8, y_px=ry + 8, w_px=20, h_px=20,
                 font_size_px=13, color=BRAND_ACCENT, bold=True)
        add_text(slide, f"qual-{i+1}-text", txt,
                 x_px=cx2 + 32, y_px=ry + 6, w_px=col_w - 40, h_px=48,
                 font_size_px=10, color=TEXT_DARK)

    # Col 3: Lessons learned
    cx3 = cx2 + col_w + col_gap
    add_text(slide, "col-3-header", "LESSONS LEARNED",
             x_px=cx3, y_px=body_top, w_px=col_w, h_px=18,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
    add_rect(slide, "col-3-rule", cx3, body_top + 20, col_w, 2, CARD_BORDER)
    lessons = [
        ("worked", "What worked", "Dedicated change-champion network accelerated adoption in sites 2 and 3 by mobilising peer-to-peer coaching."),
        ("worked", "What worked", "Phased data migration reduced go-live risk; zero critical data-loss incidents recorded across all four sites."),
        ("improve", "To improve", "Expand exception-rule library before full rollout to reduce manual overrides; assign a dedicated triage owner per region."),
    ]
    for i, (kind, badge, txt) in enumerate(lessons):
        ry = mt + i * row_h
        if kind == "worked":
            bg = WORKED_BG; border = WORKED_BORDER; badge_bg = WORKED_BADGE; badge_txt = WORKED_BADGE_TXT
        else:
            bg = IMPROVE_BG; border = IMPROVE_BORDER; badge_bg = IMPROVE_BADGE; badge_txt = IMPROVE_BADGE_TXT
        row = add_rect(slide, f"lesson-{i+1}-bg", cx3, ry, col_w, row_h - 8, bg)
        row.line.color.rgb = border
        row.line.width = 9525
        add_text(slide, f"lesson-{i+1}-badge", badge,
                 x_px=cx3 + 10, y_px=ry + 8, w_px=86, h_px=14,
                 font_size_px=8, color=badge_txt, bold=True, align="center", uppercase=True,
                 bg_fill=badge_bg, padding_px=(2, 4, 2, 4))
        add_text(slide, f"lesson-{i+1}-text", txt,
                 x_px=cx3 + 10, y_px=ry + 28, w_px=col_w - 20, h_px=28,
                 font_size_px=11, color=TEXT_DARK)

    # Recommendation bar
    rec_y = 552
    add_rect(slide, "convergence-bg", 64, rec_y, 1280 - 128, 38, CARD_BG)
    add_rect(slide, "convergence-accent", 64, rec_y, 4, 38, BRAND_ACCENT)
    add_text(slide, "convergence-mark", "RECOMMENDATION",
             x_px=78, y_px=rec_y + 4, w_px=120, h_px=14,
             font_size_px=9, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "convergence",
             "Proceed to full rollout — pilot results meet all success thresholds. Incorporate 2 modifications before scale-up.",
             x_px=200, y_px=rec_y + 4, w_px=1280 - 64 - 200, h_px=16,
             font_size_px=12, color=BRAND_PRIMARY, bold=True)
    add_text(slide, "rec-mod-1",
             "• Automate legacy vendor-code exception handling prior to Wave 2 launch",
             x_px=200, y_px=rec_y + 20, w_px=540, h_px=14,
             font_size_px=10, color=TEXT_MID)
    add_text(slide, "rec-mod-2",
             "• Replicate change-champion model across all remaining regions",
             x_px=750, y_px=rec_y + 20, w_px=440, h_px=14,
             font_size_px=10, color=TEXT_MID)

    add_footer(slide, page_num=196)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "196_pilot-results-summary.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
