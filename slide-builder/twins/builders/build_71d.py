"""
Builder for pattern 71d: Reference architecture layers (dark variant).

Source HTML: _pattern-library/71_reference-architecture-layers-dark.html
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

LAYER_1 = RGBColor(0x55, 0x36, 0x77)
LAYER_2 = BRAND_PRIMARY_MID
LAYER_3 = RGBColor(0x7E, 0x3F, 0xB0)
LAYER_4 = BRAND_ACCENT
LAYER_5 = BRAND_ACCENT_SOFT


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Slide Lab architecture — five layers, two cross-cutting concerns.",
        x_px=64, y_px=20, w_px=1100, h_px=80,
        font_size_px=28, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Layered reference architecture, top to bottom. Brand theming and QC engine apply at every layer.",
        x_px=64, y_px=108, w_px=1100, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    g_top = 220
    g_left = 64
    g_right = 1280 - 64
    g_bottom = 720 - 60 - 32
    g_w = g_right - g_left
    g_h = g_bottom - g_top
    cc_w = 220
    gap = 14
    stack_w = g_w - cc_w - gap

    layers = [
        ("LAYER 1", "PRESENTATION", LAYER_1, WHITE,
         [("Claude Code UI", "Primary surface"),
          ("VS Code", "Author IDE"),
          ("Web preview", "HTML render")]),
        ("LAYER 2", "SKILLS", LAYER_2, WHITE,
         [("storyline-helper", "Narrative"),
          ("slide-builder", "Build"),
          ("slide-helper", "Assist"),
          ("slide-qc", "Review")]),
        ("LAYER 3", "PATTERN LIBRARY", LAYER_3, WHITE,
         [("100+ HTML patterns", "Mockups"),
          ("Theme variables", "CSS tokens"),
          ("QC rules", "Standards")]),
        ("LAYER 4", "BUILD ENGINE", LAYER_4, WHITE,
         [("HTML to PPTX", "Translator"),
          ("python-pptx", "Core lib"),
          ("Template integration", "Layouts")]),
        ("LAYER 5", "TEMPLATES", LAYER_5, BRAND_PRIMARY,
         [("Accenture", "Brand deck"),
          ("FedEx", "Client deck"),
          ("Generic", "Fallback")]),
    ]

    layer_gap = 8
    layer_h = (g_h - 4 * layer_gap) // 5
    head_w = 140

    for li, (num, name, head_bg, head_color, components) in enumerate(layers):
        n = li + 1
        ly = g_top + li * (layer_h + layer_gap)

        layer = add_rect(slide, f"tier-{n}-shape", g_left, ly, stack_w, layer_h, CARD_BG_DARK)
        layer.line.color.rgb = CARD_BORDER_DARK
        layer.line.width = 9525

        add_rect(slide, f"tier-{n}-header", g_left, ly, head_w, layer_h, head_bg)
        add_text(
            slide, f"tier-{n}-label", num,
            x_px=g_left + 12, y_px=ly + 12, w_px=head_w - 24, h_px=14,
            font_size_px=9, color=head_color, bold=True, uppercase=True,
        )
        add_text(
            slide, f"tier-{n}-name", name,
            x_px=g_left + 12, y_px=ly + 28, w_px=head_w - 24, h_px=22,
            font_size_px=13, color=head_color, bold=True, uppercase=True,
        )

        body_left = g_left + head_w
        body_w = stack_w - head_w
        ncomp = len(components)
        comp_gap = 8
        comp_w = (body_w - 28 - (ncomp - 1) * comp_gap) // ncomp

        for ci, (cname, cmeta) in enumerate(components):
            cn = ci + 1
            cx = body_left + 14 + ci * (comp_w + comp_gap)
            comp = add_rect(slide, f"tier-{n}-component-{cn}",
                            cx, ly + 10, comp_w, layer_h - 20, RGBColor(0x42, 0x22, 0x66))
            comp.line.color.rgb = BRAND_ACCENT_SOFT
            comp.line.width = 9525
            add_text(
                slide, f"tier-{n}-component-{cn}-name", cname,
                x_px=cx + 4, y_px=ly + 18, w_px=comp_w - 8, h_px=18,
                font_size_px=11, color=WHITE, bold=True, align="center",
            )
            add_text(
                slide, f"tier-{n}-component-{cn}-meta", cmeta.upper(),
                x_px=cx + 4, y_px=ly + 38, w_px=comp_w - 8, h_px=14,
                font_size_px=9, color=TEXT_ON_DARK_MID, uppercase=True, align="center",
            )

    cc_x = g_left + stack_w + gap
    cc_gap = 10
    cc_bar_w = (cc_w - cc_gap) // 2

    cc_bars = [
        ("BRAND THEMING", "SPANS ALL LAYERS", RGBColor(0x1A, 0x05, 0x30), WHITE),
        ("QC ENGINE", "SPANS ALL LAYERS", BRAND_ACCENT, WHITE),
    ]
    for bi, (label, tag, bg_c, fg) in enumerate(cc_bars):
        n = bi + 1
        cx = cc_x + bi * (cc_bar_w + cc_gap)
        add_rect(slide, f"cross-cutting-{n}-shape", cx, g_top, cc_bar_w, g_h, bg_c)
        add_text(
            slide, f"cross-cutting-{n}-tag", tag,
            x_px=cx, y_px=g_top + 10, w_px=cc_bar_w, h_px=14,
            font_size_px=9, color=fg, bold=True, align="center", uppercase=True,
        )
        add_text(
            slide, f"cross-cutting-{n}-label", label,
            x_px=cx, y_px=g_top + g_h // 2 - 12, w_px=cc_bar_w, h_px=24,
            font_size_px=13, color=fg, bold=True, align="center", uppercase=True,
        )

    cv_y = 720 - 32 - 50
    cv_h = 44
    add_rect(slide, "convergence-bg", g_left, cv_y, g_w, cv_h, RGBColor(0x1A, 0x05, 0x30))
    add_text(
        slide, "convergence",
        "Five layers stacked top-to-bottom; brand theming and QC engine cut across every layer, end to end.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_w - 44, h_px=cv_h,
        font_size_px=14, color=WHITE, italic=True, anchor="middle",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "71",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "71d_reference-architecture-layers.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
