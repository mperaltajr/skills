"""
Builder for pattern 62d: Theory of change (dark variant).

Source HTML: _pattern-library/62_theory-of-change-dark.html
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

COL2_BODY = RGBColor(0x42, 0x22, 0x66)
COL3_BODY = RGBColor(0x4F, 0x2A, 0x78)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Theory of change — from four weeks of inputs to a Q3 decision.",
        x_px=64, y_px=20, w_px=1100, h_px=80,
        font_size_px=28, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Inputs power activities, activities produce outputs, outputs drive the outcomes that close the case.",
        x_px=64, y_px=108, w_px=1100, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    g_top = 220
    g_left = 56
    g_right = 1280 - 56
    g_bottom = 720 - 80 - 60
    g_w = g_right - g_left
    g_h = g_bottom - g_top
    gap = 18
    col_w = (g_w - 3 * gap) // 4
    head_h = 62

    cols = [
        ("Stage 1", "INPUTS", "What we put in", RGBColor(0x55, 0x36, 0x77), CARD_BG_DARK,
         ["4 pilot users committed",
          "Existing decks as baseline",
          "Coaching time, 2 hrs / wk",
          "Slide Lab tool access",
          "4-week pilot window"], WHITE),
        ("Stage 2", "ACTIVITIES", "What we do", BRAND_PRIMARY_MID, COL2_BODY,
         ["Storyline coaching sessions",
          "Deck rebuilds against patterns",
          "Pattern-library application",
          "Weekly retro and review"], WHITE),
        ("Stage 3", "OUTPUTS", "What comes out", RGBColor(0x7E, 0x3F, 0xB0), COL3_BODY,
         ["12 decks measured end-to-end",
          "Reusable pattern library",
          "Coaching playbook v1",
          "Pilot scorecard published"], WHITE),
        ("Stage 4", "OUTCOMES & IMPACT", "What changes", BRAND_ACCENT, RGBColor(0x1A, 0x05, 0x30),
         ["-64% cycle time per deck",
          "+34pp sign-off rate at first review",
          "Replicable practice across teams",
          "Q3 rollout decision unlocked"], WHITE),
    ]

    for ci, (eyebrow, name, desc, head_bg, body_bg, items, item_color) in enumerate(cols):
        n = ci + 1
        cx = g_left + ci * (col_w + gap)

        add_rect(slide, f"step-{n}-header", cx, g_top, col_w, head_h, head_bg)
        add_text(
            slide, f"step-{n}-eyebrow", eyebrow.upper(),
            x_px=cx + 16, y_px=g_top + 8, w_px=col_w - 32, h_px=12,
            font_size_px=9, color=WHITE, bold=True, uppercase=True,
        )
        add_text(
            slide, f"step-{n}-name", name,
            x_px=cx + 16, y_px=g_top + 22, w_px=col_w - 32, h_px=24,
            font_size_px=18, color=WHITE, bold=True,
        )
        add_text(
            slide, f"step-{n}-desc", desc,
            x_px=cx + 16, y_px=g_top + 46, w_px=col_w - 32, h_px=14,
            font_size_px=11, color=WHITE, italic=True,
        )

        body_top = g_top + head_h
        body_h = g_h - head_h
        body = add_rect(slide, f"step-{n}-body", cx, body_top, col_w, body_h, body_bg)
        body.line.color.rgb = CARD_BORDER_DARK
        body.line.width = 9525

        item_h = (body_h - 28) // max(len(items), 1)
        for ii, txt in enumerate(items):
            inum = ii + 1
            iy = body_top + 14 + ii * item_h
            add_text(
                slide, f"step-{n}-item-{inum}", "·  " + txt,
                x_px=cx + 16, y_px=iy, w_px=col_w - 32, h_px=item_h - 4,
                font_size_px=12, color=item_color,
            )

        if ci < 3:
            chev_x = cx + col_w + gap // 2 - 6
            chev_y = g_top + head_h // 2 - 8
            add_text(
                slide, f"step-{n}-arrow", "▶",
                x_px=chev_x, y_px=chev_y, w_px=20, h_px=20,
                font_size_px=14, color=BRAND_ACCENT_SOFT, bold=True, align="center",
            )

    cv_y = g_bottom + 8
    cv_h = 44
    add_rect(slide, "convergence-bg", g_left, cv_y, g_w, cv_h, RGBColor(0x1A, 0x05, 0x30))
    add_text(
        slide, "convergence",
        "If inputs hold and activities run on cadence, the Q3 decision lands on evidence — not opinion.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_w - 100, h_px=cv_h,
        font_size_px=14, color=WHITE, italic=True, anchor="middle",
    )
    add_text(
        slide, "convergence-mark", "›››",
        x_px=g_left + g_w - 80, y_px=cv_y, w_px=60, h_px=cv_h,
        font_size_px=16, color=BRAND_ACCENT_SOFT, bold=True, anchor="middle", align="right",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "62",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "62d_theory-of-change.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
