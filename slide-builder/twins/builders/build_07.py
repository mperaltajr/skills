"""
Builder for pattern 07: Honest-expectations two-panel.

Source HTML: _pattern-library/07_honest-expectations-two-panel.html
Two side-by-side panels (green/good, amber/growing) + convergence band.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, TEXT_DARK,
)
from pptx.dml.color import RGBColor

GOOD_BG = RGBColor(0xF0, 0xFD, 0xF4)
GOOD_BORDER = RGBColor(0xBB, 0xF7, 0xD0)
GOOD_ACCENT = RGBColor(0x16, 0xA3, 0x4A)
GROW_BG = RGBColor(0xFE, 0xF3, 0xC7)
GROW_BORDER = RGBColor(0xFD, 0xE6, 0x8A)
GROW_ACCENT = RGBColor(0xCA, 0x8A, 0x04)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Honest about what works today — and what's still growing.",
        subtitle="No demo magic. Production reality on one side; in-development on the other.",
        title_h=68,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Two-panel grid: 28px gap, equal width
    panels_top = 240
    panel_h = 320
    gap = 28
    panel_w = (1280 - 128 - gap) // 2
    left_x = 64

    # PANEL 1 - Good
    add_rect(slide, "panel-1-bg", left_x, panels_top, panel_w, panel_h, GOOD_BG)
    # 4px left border
    add_rect(slide, "panel-1-accent", left_x, panels_top, 4, panel_h, GOOD_ACCENT)
    add_text(
        slide, "panel-1-label", "WORKS WELL TODAY",
        x_px=left_x + 24, y_px=panels_top + 18, w_px=panel_w - 40, h_px=16,
        font_size_px=11, color=GOOD_ACCENT, bold=True, uppercase=True,
    )
    add_text(
        slide, "panel-1-heading", "Production-grade now",
        x_px=left_x + 24, y_px=panels_top + 42, w_px=panel_w - 40, h_px=30,
        font_size_px=22, color=BRAND_PRIMARY, bold=True,
    )
    add_text(
        slide, "panel-1-body",
        "• Builds a real PPTX in your brand template — not a screenshot export\n"
        "• Forces a governing thought before drafting any slide\n"
        "• Pushes back on weak claims and bullet-padded structure\n"
        "• Renders chart + commentary slides with structurally valid layouts\n"
        "• Survives review cycles without losing the through-line",
        x_px=left_x + 24, y_px=panels_top + 84, w_px=panel_w - 48, h_px=panel_h - 100,
        font_size_px=13, color=TEXT_DARK,
    )

    # PANEL 2 - Growing
    p2_x = left_x + panel_w + gap
    add_rect(slide, "panel-2-bg", p2_x, panels_top, panel_w, panel_h, GROW_BG)
    add_rect(slide, "panel-2-accent", p2_x, panels_top, 4, panel_h, GROW_ACCENT)
    add_text(
        slide, "panel-2-label", "STILL GROWING",
        x_px=p2_x + 24, y_px=panels_top + 18, w_px=panel_w - 40, h_px=16,
        font_size_px=11, color=GROW_ACCENT, bold=True, uppercase=True,
    )
    add_text(
        slide, "panel-2-heading", "In-development",
        x_px=p2_x + 24, y_px=panels_top + 42, w_px=panel_w - 40, h_px=30,
        font_size_px=22, color=BRAND_PRIMARY, bold=True,
    )
    add_text(
        slide, "panel-2-body",
        "• Visual model templates (fishbone, value chain, wheel)\n"
        "• Hand-drawn-style diagrams from a quick description\n"
        "• Multi-deck consistency checks (cross-slide narrative QC)\n"
        "• Cost-per-deck telemetry for partner-level review",
        x_px=p2_x + 24, y_px=panels_top + 84, w_px=panel_w - 48, h_px=panel_h - 100,
        font_size_px=13, color=TEXT_DARK,
    )

    add_convergence(
        slide,
        "We're being honest because we'd rather you trust the parts that work than discover gaps mid-pitch.",
    )

    add_footer(slide, page_num=9)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "07_honest-expectations-two-panel.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
