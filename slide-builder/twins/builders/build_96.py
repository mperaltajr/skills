"""
Builder for pattern 96: Concept intro with visual (term/def left, hub-spoke SVG right).

Source HTML: _pattern-library/96_concept-intro-with-visual.html

SVG hub-and-spoke is picture-asset (chart-canvas placeholder).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="What is a governing thought — and why every deck needs one.",
        subtitle="One sentence the deck has to prove — everything else either supports it or doesn't belong.",
        title_x=64, title_w=1100, title_h=70,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Two columns. body-region starts ~y=200
    body_top = 198
    body_left = 64
    body_right = 1280 - 64
    body_w = body_right - body_left
    gap = 56
    col_w = (body_w - gap) // 2

    # LEFT — term + definition + example
    left_x = body_left

    add_text(slide, "term-1-label", "TERM",
             x_px=left_x, y_px=body_top, w_px=col_w, h_px=16,
             font_size_px=11, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
    add_text(slide, "term-1-word", "Governing\nthought",
             x_px=left_x, y_px=body_top + 24, w_px=col_w, h_px=110,
             font_size_px=44, color=BRAND_PRIMARY, bold=True)
    add_rect(slide, "term-1-rule", left_x, body_top + 140, 72, 4, BRAND_ACCENT)
    add_text(
        slide, "term-1-def",
        "The single sentence the entire deck has to prove. If the deck were one sentence, it's this one. Every slide either supports it — or it doesn't belong.",
        x_px=left_x, y_px=body_top + 162, w_px=col_w, h_px=90,
        font_size_px=17, color=TEXT_DARK,
    )

    # Example block (card with left accent)
    ex_y = body_top + 268
    ex_h = 90
    ex = add_rect(slide, "term-1-example", left_x, ex_y, col_w, ex_h, CARD_BG)
    ex.line.fill.background()
    add_rect(slide, "term-1-example-accent", left_x, ex_y, 3, ex_h, BRAND_ACCENT_SOFT)
    add_text(slide, "term-1-example-label", "EXAMPLE",
             x_px=left_x + 16, y_px=ex_y + 12, w_px=col_w - 32, h_px=14,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
    add_text(slide, "term-1-example-text",
             "\"Our strategy practice will lead Q3 sign-off rates by 30 points.\"",
             x_px=left_x + 16, y_px=ex_y + 32, w_px=col_w - 32, h_px=48,
             font_size_px=13, color=TEXT_DARK, italic=True)

    # RIGHT — visual column
    right_x = left_x + col_w + gap
    # Top caption
    add_text(slide, "visual-caption-top", "HOW IT HOLDS THE DECK TOGETHER",
             x_px=right_x, y_px=body_top, w_px=col_w, h_px=16,
             font_size_px=11, color=BRAND_PRIMARY_MID, bold=True,
             align="center", uppercase=True)

    # Chart canvas placeholder (hub-and-spoke)
    canvas_y = body_top + 28
    canvas_h = 340
    canvas = add_rect(slide, "chart-canvas", right_x, canvas_y, col_w, canvas_h, CARD_BG)
    canvas.line.color.rgb = CARD_BORDER
    canvas.line.width = 9525
    add_text(slide, "chart-canvas-placeholder",
             "[ HUB-AND-SPOKE DIAGRAM — Governing Thought hub + 4 slide nodes ]",
             x_px=right_x, y_px=canvas_y, w_px=col_w, h_px=canvas_h,
             font_size_px=12, color=TEXT_FAINT, italic=True,
             align="center", anchor="middle")

    # Bottom caption
    add_text(slide, "visual-caption-bottom",
             "Hub-and-spoke — one thought at the center, every supporting slide pointed back at it.",
             x_px=right_x + 20, y_px=canvas_y + canvas_h + 8, w_px=col_w - 40, h_px=36,
             font_size_px=12, color=TEXT_MID, italic=True, align="center")

    # Convergence
    add_convergence(
        slide,
        "If a slide doesn't trace back to the hub, it doesn't belong in the deck.",
        bottom_px=56, height_px=46,
    )
    add_rect(slide, "convergence-accent", 64, 720 - 56 - 46, 4, 46, BRAND_ACCENT)

    add_footer(slide, page_num=96)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "96_concept-intro-with-visual.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
