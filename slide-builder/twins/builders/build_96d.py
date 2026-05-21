"""
Builder for pattern 96d: Concept intro with visual — dark variant.

Source HTML: _pattern-library/96_concept-intro-with-visual-dark.html
Light template: twins/builders/build_96.py
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


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(slide, "title",
             "What is a governing thought — and why every deck needs one.",
             x_px=64, y_px=20, w_px=1100, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "One sentence the deck has to prove — everything else either supports it or doesn't belong.",
             x_px=64, y_px=108, w_px=980, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 56, 3, BRAND_ACCENT_SOFT)

    # Two columns
    body_top = 220
    body_left = 64
    body_right = 1280 - 64
    body_w = body_right - body_left
    gap = 56
    col_w = (body_w - gap) // 2

    # LEFT
    left_x = body_left
    add_text(slide, "term-1-label", "TERM",
             x_px=left_x, y_px=body_top, w_px=col_w, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True)
    add_text(slide, "term-1-word", "Governing\nthought",
             x_px=left_x, y_px=body_top + 24, w_px=col_w, h_px=110,
             font_size_px=44, color=BRAND_ACCENT_SOFT, bold=True)
    add_rect(slide, "term-1-rule", left_x, body_top + 140, 72, 4, BRAND_ACCENT)
    add_text(slide, "term-1-def",
             "The single sentence the entire deck has to prove. If the deck were one sentence, it's this one. Every slide either supports it — or it doesn't belong.",
             x_px=left_x, y_px=body_top + 162, w_px=col_w, h_px=90,
             font_size_px=17, color=WHITE)

    ex_y = body_top + 268
    ex_h = 90
    ex = add_rect(slide, "term-1-example", left_x, ex_y, col_w, ex_h, CARD_BG_DARK)
    ex.line.fill.background()
    add_rect(slide, "term-1-example-accent", left_x, ex_y, 3, ex_h, BRAND_ACCENT_SOFT)
    add_text(slide, "term-1-example-label", "EXAMPLE",
             x_px=left_x + 16, y_px=ex_y + 12, w_px=col_w - 32, h_px=14,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True)
    add_text(slide, "term-1-example-text",
             "\"Our strategy practice will lead Q3 sign-off rates by 30 points.\"",
             x_px=left_x + 16, y_px=ex_y + 32, w_px=col_w - 32, h_px=48,
             font_size_px=13, color=WHITE, italic=True)

    # RIGHT
    right_x = left_x + col_w + gap
    add_text(slide, "visual-caption-top", "HOW IT HOLDS THE DECK TOGETHER",
             x_px=right_x, y_px=body_top, w_px=col_w, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, bold=True,
             align="center", uppercase=True)

    canvas_y = body_top + 28
    canvas_h = 300
    canvas = add_rect(slide, "chart-canvas", right_x, canvas_y, col_w, canvas_h, CARD_BG_DARK)
    canvas.line.color.rgb = CARD_BORDER_DARK
    canvas.line.width = 9525
    add_text(slide, "chart-canvas-placeholder",
             "[ HUB-AND-SPOKE DIAGRAM — Governing Thought hub + 4 slide nodes ]",
             x_px=right_x, y_px=canvas_y, w_px=col_w, h_px=canvas_h,
             font_size_px=12, color=TEXT_ON_DARK_FAINT, italic=True,
             align="center", anchor="middle")

    add_text(slide, "visual-caption-bottom",
             "Hub-and-spoke — one thought at the center, every supporting slide pointed back at it.",
             x_px=right_x + 20, y_px=canvas_y + canvas_h + 8, w_px=col_w - 40, h_px=36,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True, align="center")

    # Convergence
    conv_y = 720 - 56 - 46
    conv_h = 46
    add_rect(slide, "convergence-bg", 64, conv_y, 1280 - 128, conv_h, BRAND_PRIMARY_MID)
    add_rect(slide, "convergence-accent", 64, conv_y, 4, conv_h, BRAND_ACCENT)
    add_text(slide, "convergence",
             "If a slide doesn't trace back to the hub, it doesn't belong in the deck.",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=conv_h,
             font_size_px=14, color=WHITE, italic=True, anchor="middle",
             padding_px=(0, 22, 0, 22))

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "96",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "96d_concept-intro-with-visual-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
