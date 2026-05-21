"""
Builder for pattern 07d: Honest-expectations two-panel — DARK variant.

Light source: twins/builders/build_07.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)

# Tinted dark equivalents — keep semantic green/amber meaning but on dark
GOOD_BG = RGBColor(0x1A, 0x3D, 0x2A)
GOOD_ACCENT = RGBColor(0x4A, 0xD4, 0x80)
GROW_BG = RGBColor(0x3D, 0x30, 0x10)
GROW_ACCENT = RGBColor(0xF5, 0xC4, 0x4A)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Honest about what works today — and what's still growing.",
        x_px=64, y_px=32, w_px=1000, h_px=68,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "No demo magic. Production reality on one side; in-development on the other.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    panels_top = 240
    panel_h = 320
    gap = 28
    panel_w = (1280 - 128 - gap) // 2
    left_x = 64

    # PANEL 1 - Good
    add_rect(slide, "panel-1-bg", left_x, panels_top, panel_w, panel_h, GOOD_BG)
    add_rect(slide, "panel-1-accent", left_x, panels_top, 4, panel_h, GOOD_ACCENT)
    add_text(
        slide, "panel-1-label", "WORKS WELL TODAY",
        x_px=left_x + 24, y_px=panels_top + 18, w_px=panel_w - 40, h_px=16,
        font_size_px=11, color=GOOD_ACCENT, bold=True, uppercase=True,
    )
    add_text(
        slide, "panel-1-heading", "Production-grade now",
        x_px=left_x + 24, y_px=panels_top + 42, w_px=panel_w - 40, h_px=30,
        font_size_px=22, color=WHITE, bold=True,
    )
    add_text(
        slide, "panel-1-body",
        "• Builds a real PPTX in your brand template — not a screenshot export\n"
        "• Forces a governing thought before drafting any slide\n"
        "• Pushes back on weak claims and bullet-padded structure\n"
        "• Renders chart + commentary slides with structurally valid layouts\n"
        "• Survives review cycles without losing the through-line",
        x_px=left_x + 24, y_px=panels_top + 84, w_px=panel_w - 48, h_px=panel_h - 100,
        font_size_px=13, color=WHITE,
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
        font_size_px=22, color=WHITE, bold=True,
    )
    add_text(
        slide, "panel-2-body",
        "• Visual model templates (fishbone, value chain, wheel)\n"
        "• Hand-drawn-style diagrams from a quick description\n"
        "• Multi-deck consistency checks (cross-slide narrative QC)\n"
        "• Cost-per-deck telemetry for partner-level review",
        x_px=p2_x + 24, y_px=panels_top + 84, w_px=panel_w - 48, h_px=panel_h - 100,
        font_size_px=13, color=WHITE,
    )

    # Convergence band — brand-accent
    conv_y = 720 - 78 - 42
    add_rect(slide, "convergence-bg",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42, fill_color=BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "We're being honest because we'd rather you trust the parts that work than discover gaps mid-pitch.",
        x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42,
        font_size_px=14, color=WHITE, italic=True,
        anchor="middle", padding_px=(0, 22, 0, 22),
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "9",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "07d_honest-expectations-two-panel.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
