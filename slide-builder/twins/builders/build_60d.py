"""
Builder for pattern 60d: Strategic roadmap 3-horizon (dark variant).

Source HTML: _pattern-library/60_strategic-roadmap-3-horizon-dark.html
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

NOW_INIT_BG = RGBColor(0x4A, 0x28, 0x6C)
LATER_INIT_BG = RGBColor(0x2A, 0x10, 0x48)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title", "Three horizons — now, next, later.",
        x_px=64, y_px=20, w_px=1050, h_px=80,
        font_size_px=28, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle", "Today's bets fund tomorrow's options. Each horizon earns the next.",
        x_px=64, y_px=108, w_px=1050, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    g_top = 220
    g_left = 56
    g_right = 1280 - 56
    g_bottom = 720 - 80 - 60
    g_h = g_bottom - g_top
    gap = 18
    col_w = (g_right - g_left - 2 * gap) // 3

    cols = [
        ("now", "Horizon 1", "NOW", "Next 3 months", BRAND_ACCENT, WHITE, [
            ("Pilot Slide Lab in 1 workstream",
             "Prove the value loop end-to-end with a single team before scaling.",
             "Mario · Q2"),
            ("Hire 1 designer-engineer",
             "Embed design judgment into the build, not bolted on after.",
             "PMO · Q2"),
            ("Build pattern library to 100",
             "Cover the long tail of consulting slide types — coverage = adoption.",
             "Mario · Q3"),
        ], BRAND_ACCENT, NOW_INIT_BG),
        ("next", "Horizon 2", "NEXT", "3 to 9 months", BRAND_PRIMARY_MID, WHITE, [
            ("Roll out to 3 practice areas",
             "Take the proven loop horizontal — Strategy, Tech, Industry X.",
             "Maria · Q3 to Q4"),
            ("Add brand-template variants",
             "Client-specific themes so the output ships ready, not 'almost there'.",
             "Designer · Q4"),
            ("Train 12 senior coaches",
             "Multiply by training the coaches who train the teams.",
             "PMO · Q4"),
        ], BRAND_PRIMARY_MID, CARD_BG_DARK),
        ("later", "Horizon 3", "LATER", "9 to 18 months", CARD_BG_DARK, WHITE, [
            ("License to peer firms",
             "Turn internal capability into external revenue once the IP is stable.",
             "Partner · 2027"),
            ("Publish IP as method",
             "Codify the playbook publicly to set the category standard.",
             "R&D · 2027"),
            ("Build standalone product",
             "Spin out a productized version once the market is validated.",
             "TBD · 2028"),
        ], TEXT_ON_DARK_FAINT, LATER_INIT_BG),
    ]

    head_h = 60
    init_h = (g_h - head_h - 20) // 3
    init_gap = 6

    for ci, (key, label, name, tf, head_bg, head_color, inits, init_border, init_bg) in enumerate(cols):
        n = ci + 1
        cx = g_left + ci * (col_w + gap)

        col_frame = add_rect(slide, f"pillar-{n}-frame", cx, g_top, col_w, g_h, CARD_BG_DARK)
        col_frame.line.color.rgb = head_bg if key == "now" else CARD_BORDER_DARK
        col_frame.line.width = 9525

        add_rect(slide, f"pillar-{n}-header", cx, g_top, col_w, head_h, head_bg)
        add_text(
            slide, f"pillar-{n}-tag", label.upper(),
            x_px=cx + 16, y_px=g_top + 8, w_px=col_w - 32, h_px=14,
            font_size_px=10, color=head_color, bold=True, uppercase=True,
        )
        add_text(
            slide, f"pillar-{n}-name", name,
            x_px=cx + 16, y_px=g_top + 22, w_px=col_w - 32, h_px=26,
            font_size_px=20, color=head_color, bold=True,
        )
        add_text(
            slide, f"pillar-{n}-timeframe", tf,
            x_px=cx + 16, y_px=g_top + 46, w_px=col_w - 32, h_px=14,
            font_size_px=11, color=head_color, bold=True,
        )

        body_top = g_top + head_h + 10
        for ii, (ititle, idesc, imeta) in enumerate(inits):
            in_ = ii + 1
            iy = body_top + ii * (init_h + init_gap)
            add_rect(slide, f"pillar-{n}-initiative-{in_}",
                     cx + 10, iy, col_w - 20, init_h, init_bg)
            add_rect(slide, f"pillar-{n}-initiative-{in_}-stripe",
                     cx + 10, iy, 3, init_h, init_border)
            add_text(
                slide, f"pillar-{n}-initiative-{in_}-title", ititle,
                x_px=cx + 22, y_px=iy + 9, w_px=col_w - 42, h_px=20,
                font_size_px=13, color=WHITE, bold=True,
            )
            add_text(
                slide, f"pillar-{n}-initiative-{in_}-desc", idesc,
                x_px=cx + 22, y_px=iy + 30, w_px=col_w - 42, h_px=init_h - 56,
                font_size_px=11, color=TEXT_ON_DARK_MID,
            )
            meta_color = BRAND_ACCENT_SOFT if key == "now" else TEXT_ON_DARK_FAINT
            add_text(
                slide, f"pillar-{n}-initiative-{in_}-meta", imeta.upper(),
                x_px=cx + 22, y_px=iy + init_h - 20, w_px=col_w - 42, h_px=14,
                font_size_px=10, color=meta_color, bold=True, uppercase=True,
            )

    cv_y = g_bottom + 8
    cv_h = 44
    add_rect(slide, "convergence-bg", g_left, cv_y, g_right - g_left, cv_h, RGBColor(0x1A, 0x05, 0x30))
    add_text(
        slide, "convergence",
        "Today's bets are tomorrow's foundations.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_right - g_left - 44, h_px=cv_h,
        font_size_px=14, color=WHITE, italic=True, anchor="middle",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "60",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "60d_strategic-roadmap-3-horizon.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
