"""
Builder for pattern 71: Reference architecture — 5 stacked layers + 2 cross-cutting bars.

Decompose pattern: each layer = header band + body row of components.
Cross-cutting bars on right span all 5 layers.

Source HTML: _pattern-library/71_reference-architecture-layers.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

LAYER_1 = RGBColor(0x2D, 0x0A, 0x4E)
LAYER_2 = RGBColor(0x5C, 0x2D, 0x87)
LAYER_3 = RGBColor(0x7E, 0x3F, 0xB0)
LAYER_4 = RGBColor(0xA1, 0x00, 0xFF)
LAYER_5 = RGBColor(0xC7, 0x80, 0xFF)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_text(
        slide, "title",
        "Slide Lab architecture — five layers, two cross-cutting concerns.",
        x_px=64, y_px=50, w_px=1100, h_px=40,
        font_size_px=28, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Layered reference architecture, top to bottom. Brand theming and QC engine apply at every layer.",
        x_px=64, y_px=98, w_px=1100, h_px=22,
        font_size_px=14, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 142, 56, 3, BRAND_ACCENT)

    # Arch canvas
    g_top = 184
    g_left = 64
    g_right = 1280 - 64
    g_bottom = 720 - 60 - 32  # leave room for convergence + footer (32+~50)
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
         [("Firm", "Brand deck"),
          ("Client", "Client deck"),
          ("Generic", "Fallback")]),
    ]

    layer_gap = 8
    layer_h = (g_h - 4 * layer_gap) // 5
    head_w = 140

    for li, (num, name, head_bg, head_color, components) in enumerate(layers):
        n = li + 1
        ly = g_top + li * (layer_h + layer_gap)

        # Layer frame
        layer = add_rect(slide, f"tier-{n}-shape", g_left, ly, stack_w, layer_h, WHITE)
        layer.line.color.rgb = CARD_BORDER
        layer.line.width = 9525

        # Header band
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

        # Body row of components
        body_left = g_left + head_w
        body_w = stack_w - head_w
        ncomp = len(components)
        comp_gap = 8
        comp_w = (body_w - 28 - (ncomp - 1) * comp_gap) // ncomp

        for ci, (cname, cmeta) in enumerate(components):
            cn = ci + 1
            cx = body_left + 14 + ci * (comp_w + comp_gap)
            comp = add_rect(slide, f"tier-{n}-component-{cn}",
                            cx, ly + 10, comp_w, layer_h - 20, CARD_BG)
            comp.line.color.rgb = BRAND_ACCENT_SOFT
            comp.line.width = 9525
            add_text(
                slide, f"tier-{n}-component-{cn}-name", cname,
                x_px=cx + 4, y_px=ly + 18, w_px=comp_w - 8, h_px=18,
                font_size_px=11, color=TEXT_DARK, bold=True, align="center",
            )
            add_text(
                slide, f"tier-{n}-component-{cn}-meta", cmeta.upper(),
                x_px=cx + 4, y_px=ly + 38, w_px=comp_w - 8, h_px=14,
                font_size_px=9, color=TEXT_MID, uppercase=True, align="center",
            )

    # Cross-cutting bars (right)
    cc_x = g_left + stack_w + gap
    cc_gap = 10
    cc_bar_w = (cc_w - cc_gap) // 2

    cc_bars = [
        ("BRAND THEMING", "SPANS ALL LAYERS", BRAND_PRIMARY, WHITE),
        ("QC ENGINE", "SPANS ALL LAYERS", BRAND_ACCENT, WHITE),
    ]
    for bi, (label, tag, bg, fg) in enumerate(cc_bars):
        n = bi + 1
        cx = cc_x + bi * (cc_bar_w + cc_gap)
        add_rect(slide, f"cross-cutting-{n}-shape", cx, g_top, cc_bar_w, g_h, bg)
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

    # Convergence
    cv_y = 720 - 32 - 50
    cv_h = 44
    add_rect(slide, "convergence-bg", g_left, cv_y, g_w, cv_h, BRAND_PRIMARY)
    add_text(
        slide, "convergence",
        "Five layers stacked top-to-bottom; brand theming and QC engine cut across every layer, end to end.",
        x_px=g_left + 22, y_px=cv_y, w_px=g_w - 44, h_px=cv_h,
        font_size_px=14, color=WHITE, italic=True, anchor="middle",
    )

    add_footer(slide, page_num=71)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "71_reference-architecture-layers.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
