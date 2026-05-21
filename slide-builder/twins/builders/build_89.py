"""
Builder for pattern 89: Lessons learned / retrospective (3 columns — worked, didn't, next).

Source HTML: _pattern-library/89_lessons-learned-retro.html
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

WORKED_BAND = RGBColor(0x04, 0x78, 0x57)
WORKED_BG = RGBColor(0xEC, 0xFD, 0xF5)
WORKED_MARK = RGBColor(0x05, 0x96, 0x69)
WORKED_BORDER = RGBColor(0xBB, 0xF0, 0xD6)

DIDNT_BAND = RGBColor(0xB4, 0x53, 0x09)
DIDNT_BG = RGBColor(0xFF, 0xFB, 0xEB)
DIDNT_MARK = RGBColor(0xD9, 0x77, 0x06)
DIDNT_BORDER = RGBColor(0xFC, 0xE3, 0xA8)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Eyebrow + title
    add_text(slide, "eyebrow", "Lessons learned",
             x_px=48, y_px=58, w_px=400, h_px=16,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "title",
             "Four weeks of Slide Lab pilot — what worked, what didn't, what's next.",
             x_px=48, y_px=78, w_px=1180, h_px=36,
             font_size_px=26, color=TEXT_DARK, bold=True)
    add_text(slide, "subtitle",
             "Wins and challenges came out roughly even. The \"try next time\" list is where half the value of this retro lives — carry it into Wave 2.",
             x_px=48, y_px=118, w_px=1100, h_px=44,
             font_size_px=12, color=TEXT_MID)
    add_rect(slide, "brand-rule", 48, 170, 56, 3, BRAND_ACCENT)

    # 3 columns: left:48, right:48, top:196, bottom:132
    col_left = 48
    col_top = 196
    col_bot = 720 - 132
    col_h = col_bot - col_top  # 392
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
         BRAND_PRIMARY, CARD_BG, BRAND_ACCENT, CARD_BORDER,
         [("→", "Pre-provision IT 2 weeks ahead of each wave — treat it as a hard gate, not a parallel track."),
          ("→", "Build a junior-friendly pattern picker UI — intent-first prompts, not pattern names."),
          ("→", "Skeptic-as-coach assignment — turn the loudest resistors into the rollout's peer reviewers."),
          ("→", "QC checklist printed on every preview — make hygiene checks visible at the point of build.")]),
    ]

    for i, (cid, header, meta, band_color, body_bg, mark_color, border_color, items) in enumerate(columns):
        n = i + 1
        cx = col_left + i * (col_w + gap)

        # Column body
        body = add_rect(slide, cid, cx, col_top, col_w, col_h, body_bg)
        body.line.color.rgb = border_color
        body.line.width = 9525

        # Band (top)
        add_rect(slide, f"compare-col-{n}-band", cx, col_top, col_w, band_h, band_color)
        add_text(slide, f"compare-col-{n}-header", header,
                 x_px=cx + 16, y_px=col_top + 10, w_px=col_w - 100, h_px=18,
                 font_size_px=12, color=WHITE, bold=True, uppercase=True)
        add_text(slide, f"compare-col-{n}-meta", meta,
                 x_px=cx + col_w - 90, y_px=col_top + 12, w_px=80, h_px=16,
                 font_size_px=9, color=WHITE, bold=True, align="right", uppercase=True)

        # Items — stretched to fill the full column body so the slide
        # doesn't read as compressed to its top half.
        item_top = col_top + band_h + 18
        items_area_h = col_h - band_h - 28  # leave 10px breathing room at bottom
        item_row_h = items_area_h // len(items)
        for j, (mark, text) in enumerate(items):
            iy = item_top + j * item_row_h
            # Mark badge (circle)
            add_rect(slide, f"compare-col-{n}-item-{j+1}-mark",
                     cx + 14, iy + 2, 22, 22, mark_color)
            add_text(slide, f"compare-col-{n}-item-{j+1}-mark-text", mark,
                     x_px=cx + 14, y_px=iy + 2, w_px=22, h_px=22,
                     font_size_px=12, color=WHITE, bold=True,
                     align="center", anchor="middle")
            # Item text — fills the row so empty space distributes evenly
            add_text(slide, f"compare-col-{n}-item-{j+1}", text,
                     x_px=cx + 44, y_px=iy, w_px=col_w - 58, h_px=item_row_h - 8,
                     font_size_px=13, color=TEXT_DARK)

    # Convergence
    conv_y = 720 - 56 - 56
    conv_h = 52
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, conv_h, BRAND_PRIMARY)
    add_text(slide, "convergence-mark", "SO WHAT",
             x_px=48 + 14, y_px=conv_y + 16, w_px=80, h_px=20,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center",
             bg_fill=BRAND_PRIMARY_MID, padding_px=(3, 6, 3, 6))
    add_text(
        slide, "convergence",
        "Wins and challenges came out roughly even — that's honest, not a failure. The \"try next time\" list is half the value of this retro; the four moves carry directly into the Wave 2 plan.",
        x_px=48 + 110, y_px=conv_y, w_px=1280 - 96 - 130, h_px=conv_h,
        font_size_px=12, color=WHITE, anchor="middle",
    )

    add_footer(slide, page_num=89)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "89_lessons-learned-retro.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
