"""
Builder for pattern 06d: Section divider with hero numeral — DARK variant.

Light source: twins/builders/build_06.py
Note: 06 is already a dark divider. 06d is the canonical dark-mode variant —
same structure with all canonical chrome rules applied.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_rect(slide, "divider-top-rule", x_px=0, y_px=0, w_px=1280, h_px=6, fill_color=BRAND_ACCENT)

    left_x = 80
    left_w = 540

    add_text(
        slide, "divider-section-label", "SECTION · 03",
        x_px=left_x, y_px=220, w_px=left_w, h_px=18,
        font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )

    add_text(
        slide, "divider-title", "What Slide Lab actually is",
        x_px=left_x, y_px=246, w_px=left_w, h_px=140,
        font_size_px=56, color=WHITE, bold=True,
    )

    add_rect(slide, "divider-rule", x_px=left_x, y_px=400, w_px=80, h_px=4, fill_color=BRAND_ACCENT)

    add_text(
        slide, "divider-subtitle",
        "The mechanics behind the thought partner — how it sharpens the thesis before it builds anything.",
        x_px=left_x, y_px=428, w_px=480, h_px=72,
        font_size_px=16, color=BRAND_ACCENT_SOFT,
    )

    # Right column: huge numeral
    add_text(
        slide, "divider-numeral", "03",
        x_px=640, y_px=140, w_px=560, h_px=420,
        font_size_px=360, color=BRAND_ACCENT, bold=True,
        align="right",
    )

    # Bottom accent rule — moved out of invariant footer zone (>=672 is invariant)
    # The accent rule at y=714 is decorative but in the footer; light variant has it.
    # Keep at very edge to avoid colliding with source/page-number.
    add_rect(slide, "divider-bottom-rule", x_px=0, y_px=714, w_px=1280, h_px=6, fill_color=BRAND_ACCENT)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "6",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "06d_section-divider-numeral.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
