"""
Builder for pattern 194d: Key Messages per Audience — DARK variant.

No light template (rejected). Authored from dark HTML:
_pattern-library/194_key-messages-per-audience-dark.html
Structural reference: build_93 (audience-tier table).
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


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Tailored <strong>key messages</strong> for every audience",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Right message, right person, right channel — driving aligned action across the organisation",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    # 4 columns
    body_top = 220
    body_bot = 660
    body_h = body_bot - body_top
    cont_left = 48
    cont_w = 1280 - 96
    col_gap = 16
    col_w = (cont_w - 3 * col_gap) // 4

    columns = [
        ("Board",
         BRAND_ACCENT_SOFT,
         "Governance, risk & fiduciary duty",
         "This initiative protects enterprise value and strengthens our strategic position",
         ["Reduces regulatory exposure by an estimated 40%",
          "Aligns with approved 3-year strategy",
          "ROI positive within 18 months"],
         "Approve programme charter at next board meeting",
         "Town Hall  /  Board Pack"),
        ("C-Suite",
         BRAND_ACCENT,
         "P&L impact, cross-function alignment",
         "We gain competitive advantage while meeting our cost and growth targets",
         ["$12M efficiency target in Year 1",
          "Removes the top 3 cross-unit bottlenecks",
          "Enables new revenue stream by Q3"],
         "Champion the change within your function by Week 2",
         "Leadership Offsite  /  Email"),
        ("Operations",
         BRAND_ACCENT,
         "Process reliability, KPIs & workload",
         "The new process reduces manual steps and makes hitting your SLAs easier",
         ["Cuts average handling time by 25%",
          "Single system of record — no dual entry",
          "Dedicated support desk during go-live"],
         "Complete training module and certify by [date]",
         "Manager Briefing  /  Intranet"),
        ("Front-Line",
         BRAND_ACCENT_SOFT,
         "Day-to-day ease, job security & clarity",
         "This change makes your daily work simpler — and your team will be fully supported",
         ["New tool trained in under 2 hours",
          "No role eliminations in scope",
          "Peer champions on every team"],
         "Attend your team's kick-off session this week",
         "Team Huddle  /  SMS Alert"),
    ]

    for i, (name, accent, care, msg, bullets, cta, channel) in enumerate(columns):
        n = i + 1
        cx = cont_left + i * (col_w + col_gap)
        col = add_rect(slide, f"pillar-{n}-bg", cx, body_top, col_w, body_h, CARD_BG_DARK)
        col.line.color.rgb = CARD_BORDER_DARK
        col.line.width = 9525
        # Left accent bar
        add_rect(slide, f"pillar-{n}-accent-bar", cx, body_top, 4, body_h, accent)
        # Header
        add_text(slide, f"pillar-{n}-name", name,
                 x_px=cx + 14, y_px=body_top + 14, w_px=col_w - 28, h_px=24,
                 font_size_px=16, color=WHITE, bold=True)
        # What they care about (small uppercase label)
        add_text(slide, f"pillar-{n}-tag", care,
                 x_px=cx + 14, y_px=body_top + 44, w_px=col_w - 28, h_px=32,
                 font_size_px=10, color=TEXT_ON_DARK_MID, italic=True)
        # Key message
        add_text(slide, f"pillar-{n}-message", msg,
                 x_px=cx + 14, y_px=body_top + 82, w_px=col_w - 28, h_px=72,
                 font_size_px=13, color=WHITE, bold=True)
        # Proof points
        proof_y = body_top + 162
        for j, b in enumerate(bullets):
            by = proof_y + j * 36
            add_rect(slide, f"pillar-{n}-bullet-{j+1}-dot", cx + 14, by + 6, 4, 4, accent)
            add_text(slide, f"pillar-{n}-body-{j+1}" if j > 0 else f"pillar-{n}-body", b,
                     x_px=cx + 24, y_px=by, w_px=col_w - 38, h_px=34,
                     font_size_px=11, color=TEXT_ON_DARK_MID)
        # CTA
        cta_y = proof_y + 3 * 36 + 8
        add_text(slide, f"pillar-{n}-cta", cta,
                 x_px=cx + 14, y_px=cta_y, w_px=col_w - 28, h_px=44,
                 font_size_px=10, color=accent, italic=True, bold=True)
        # Channel footer
        ch_y = body_top + body_h - 32
        add_rect(slide, f"pillar-{n}-channel-rule", cx + 14, ch_y - 6, col_w - 28, 1, CARD_BORDER_DARK)
        add_text(slide, f"pillar-{n}-channel", channel,
                 x_px=cx + 14, y_px=ch_y, w_px=col_w - 28, h_px=20,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, uppercase=True, bold=True)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "194",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "194d_key-messages-per-audience-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
