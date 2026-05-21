"""
Builder for pattern 17d: Before-after transformation — DARK variant.

Light source: twins/builders/build_17.py
On dark, BEFORE panel is the card-bg-dark; AFTER is a brighter accent panel.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
AFTER_PANEL_BG = RGBColor(0xA1, 0x00, 0xFF)  # brand-accent for AFTER


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "What changed in four weeks of pilot.",
        x_px=64, y_px=32, w_px=1000, h_px=68,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Same teams, same deck volume. Different discipline — and the workflow followed.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    grid_left = 56
    grid_w = 1280 - 112
    arrow_w = int(grid_w * 16 / 100)
    panel_w = (grid_w - arrow_w) // 2
    panel_top = 220
    panel_h = 340
    after_overlap = 10

    # BEFORE panel — card-bg-dark
    before_x = grid_left
    bp = add_rect(slide, "before-panel-bg", before_x, panel_top, panel_w, panel_h, CARD_BG_DARK)
    bp.line.color.rgb = CARD_BORDER_DARK
    bp.line.width = 9525
    add_text(
        slide, "before-panel-label", "BEFORE · WEEK 0",
        x_px=before_x + 24, y_px=panel_top + 18, w_px=panel_w - 48, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_MID, bold=True, uppercase=True,
    )
    add_text(
        slide, "before-panel-heading", "Disconnected deck workflow",
        x_px=before_x + 24, y_px=panel_top + 42, w_px=panel_w - 48, h_px=28,
        font_size_px=20, color=WHITE, bold=True,
    )
    add_text(
        slide, "before-panel-body",
        "• Slide deck assembled bottom-up from workstream findings\n"
        "• Argument lost as bullets compound across review cycles\n"
        "• Three rounds of partner edits per deck typical\n"
        "• 11 days median from kickoff to final",
        x_px=before_x + 24, y_px=panel_top + 86, w_px=panel_w - 48, h_px=panel_h - 100,
        font_size_px=13, color=TEXT_ON_DARK_MID,
    )

    # ARROW
    arrow_x = before_x + panel_w
    add_text(
        slide, "transformation-arrow-label-top", "PILOT",
        x_px=arrow_x, y_px=panel_top + panel_h // 2 - 56, w_px=arrow_w, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True, align="center",
    )
    arrow_shape_w = arrow_w - 16
    arrow_shape_h = 50
    arrow_sx = arrow_x + 8
    arrow_sy = panel_top + panel_h // 2 - 25
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW,
        px_to_emu(arrow_sx), px_to_emu(arrow_sy),
        px_to_emu(arrow_shape_w), px_to_emu(arrow_shape_h),
    )
    arrow.name = "transformation-arrow"
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = BRAND_ACCENT
    arrow.line.fill.background()
    add_text(
        slide, "transformation-arrow-label-bottom", "WEEKS 1–4",
        x_px=arrow_x, y_px=panel_top + panel_h // 2 + 36, w_px=arrow_w, h_px=14,
        font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, uppercase=True, align="center",
    )

    # AFTER — brand-accent fill, white text
    after_x = arrow_x + arrow_w
    after_y = panel_top - after_overlap
    after_h = panel_h + after_overlap
    add_rect(slide, "after-panel-bg", after_x, after_y, panel_w, after_h, AFTER_PANEL_BG)
    add_text(
        slide, "after-panel-label", "AFTER · WEEK 4",
        x_px=after_x + 24, y_px=after_y + 24, w_px=panel_w - 48, h_px=16,
        font_size_px=11, color=WHITE, bold=True, uppercase=True,
    )
    add_text(
        slide, "after-panel-heading", "Structured argument-first workflow",
        x_px=after_x + 24, y_px=after_y + 48, w_px=panel_w - 48, h_px=28,
        font_size_px=20, color=WHITE, bold=True,
    )
    add_text(
        slide, "after-panel-body",
        "• Governing thought drives the deck structure\n"
        "• Each slide carries one argument; reviews sharpen, not pile on\n"
        "• One round of partner edits\n"
        "• 5 days median from kickoff to final",
        x_px=after_x + 24, y_px=after_y + 92, w_px=panel_w - 48, h_px=after_h - 110,
        font_size_px=13, color=WHITE,
    )

    conv_y = 720 - 78 - 42
    add_rect(slide, "convergence-bg",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42, fill_color=BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "The change isn't a tool — it's a discipline. The tool just enforces it.",
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
    add_text(slide, "page-number", "17",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "17d_before-after-transformation.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
