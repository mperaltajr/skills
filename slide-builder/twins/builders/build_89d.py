"""
Builder for pattern 89d: Lessons learned / retro — dark variant.

Source HTML: _pattern-library/89_lessons-learned-retro-dark.html
Light template: twins/builders/build_89.py
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

WORKED_BAND = RGBColor(0x05, 0x96, 0x69)
WORKED_BG = RGBColor(0x14, 0x4D, 0x2E)
WORKED_MARK = RGBColor(0x05, 0x96, 0x69)
WORKED_BORDER = RGBColor(0x14, 0x68, 0x40)

DIDNT_BAND = RGBColor(0xD9, 0x77, 0x06)
DIDNT_BG = RGBColor(0x57, 0x36, 0x09)
DIDNT_MARK = RGBColor(0xD9, 0x77, 0x06)
DIDNT_BORDER = RGBColor(0x7E, 0x4F, 0x10)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(slide, "eyebrow", "Lessons learned",
             x_px=48, y_px=20, w_px=400, h_px=16,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "title",
             "Four weeks of Slide Lab pilot — what worked, what didn't, what's next.",
             x_px=48, y_px=42, w_px=1180, h_px=60,
             font_size_px=26, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Wins and challenges came out roughly even. The \"try next time\" list is where half the value of this retro lives — carry it into Wave 2.",
             x_px=48, y_px=108, w_px=1100, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 134, 56, 3, BRAND_ACCENT_SOFT)

    # 3 columns
    col_left = 48
    col_top = 220
    col_bot = 720 - 132
    col_h = col_bot - col_top
    col_w_total = 1280 - 96
    gap = 16
    col_w = (col_w_total - gap * 2) // 3
    band_h = 38

    columns = [
        ("compare-col-1", "What worked", "4 wins",
         WORKED_BAND, WORKED_BG, WORKED_MARK, WORKED_BORDER,
         [("✓", "Pre-deck storyline session as default — consultants showed up with a sharper governing thought."),
          ("✓", "Brand-template integration was clean — no rework needed on slides handed to PMO."),
          ("✓", "Pattern library accelerated build — first-draft slides in ~8 min vs. 35 baseline."),
          ("✓", "Coach-driven feedback loop kept quality high without slowing the team down.")]),
        ("compare-col-2", "What didn't", "4 gaps",
         DIDNT_BAND, DIDNT_BG, DIDNT_MARK, DIDNT_BORDER,
         [("✗", "Wave 2 IT provisioning was late — users sat idle for the first three days of the wave."),
          ("✗", "Junior team couldn't self-serve patterns — the picker assumes prior storyline fluency."),
          ("✗", "Two senior managers resisted change — defaulted to their own templates and stalled adoption on their pods."),
          ("✗", "HTML preview broke on Edge — only Chrome rendered reliably, blocking non-default users.")]),
        ("compare-col-3", "Try next time", "4 moves",
         BRAND_PRIMARY_MID, CARD_BG_DARK, BRAND_ACCENT_SOFT, CARD_BORDER_DARK,
         [("→", "Pre-provision IT 2 weeks ahead of each wave — treat it as a hard gate, not a parallel track."),
          ("→", "Build a junior-friendly pattern picker UI — intent-first prompts, not pattern names."),
          ("→", "Skeptic-as-coach assignment — turn the loudest resistors into the rollout's peer reviewers."),
          ("→", "QC checklist printed on every preview — make hygiene checks visible at the point of build.")]),
    ]

    for i, (cid, header, meta, band_color, body_bg, mark_color, border_color, items) in enumerate(columns):
        n = i + 1
        cx = col_left + i * (col_w + gap)

        body = add_rect(slide, cid, cx, col_top, col_w, col_h, body_bg)
        body.line.color.rgb = border_color
        body.line.width = 9525

        add_rect(slide, f"compare-col-{n}-band", cx, col_top, col_w, band_h, band_color)
        add_text(slide, f"compare-col-{n}-header", header,
                 x_px=cx + 16, y_px=col_top + 10, w_px=col_w - 100, h_px=18,
                 font_size_px=12, color=WHITE, bold=True, uppercase=True)
        add_text(slide, f"compare-col-{n}-meta", meta,
                 x_px=cx + col_w - 90, y_px=col_top + 12, w_px=80, h_px=16,
                 font_size_px=9, color=WHITE, bold=True, align="right", uppercase=True)

        item_top = col_top + band_h + 18
        items_area_h = col_h - band_h - 28
        item_row_h = items_area_h // len(items)
        for j, (mark, text) in enumerate(items):
            iy = item_top + j * item_row_h
            add_rect(slide, f"compare-col-{n}-item-{j+1}-mark",
                     cx + 14, iy + 2, 22, 22, mark_color)
            add_text(slide, f"compare-col-{n}-item-{j+1}-mark-text", mark,
                     x_px=cx + 14, y_px=iy + 2, w_px=22, h_px=22,
                     font_size_px=12, color=WHITE, bold=True,
                     align="center", anchor="middle")
            add_text(slide, f"compare-col-{n}-item-{j+1}", text,
                     x_px=cx + 44, y_px=iy, w_px=col_w - 58, h_px=item_row_h - 8,
                     font_size_px=13, color=WHITE)

    # Convergence
    conv_y = 720 - 56 - 56
    conv_h = 52
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, conv_h, BRAND_PRIMARY_MID)
    add_text(slide, "convergence-mark", "SO WHAT",
             x_px=48 + 14, y_px=conv_y + 16, w_px=80, h_px=20,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center",
             bg_fill=BRAND_PRIMARY, padding_px=(3, 6, 3, 6))
    add_text(slide, "convergence",
             "Wins and challenges came out roughly even — that's honest, not a failure. The \"try next time\" list is half the value of this retro; the four moves carry directly into the Wave 2 plan.",
             x_px=48 + 110, y_px=conv_y, w_px=1280 - 96 - 130, h_px=conv_h,
             font_size_px=12, color=WHITE, anchor="middle")

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "89",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "89d_lessons-learned-retro-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
