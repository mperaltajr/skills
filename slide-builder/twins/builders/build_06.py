"""
Builder for pattern 06: Section divider with hero numeral + brand accents.

Source HTML: _pattern-library/06_section-divider-numeral.html
Dark-mode divider — brand-primary background, no standard title block,
no draft badge per the divider chrome convention (kept here matching HTML which DOES include it).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()

    # Dark background (brand-primary)
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Top accent rule (6px full-width brand-accent)
    add_rect(slide, "divider-top-rule", x_px=0, y_px=0, w_px=1280, h_px=6, fill_color=BRAND_ACCENT)

    # Project label (light variant)

    # Two-column layout: left text, right giant numeral
    # Padding 0 80, centered vertically
    left_x = 80
    left_w = 540

    # Section meta (eyebrow): "SECTION · 03"
    add_text(
        slide, "divider-section-label", "SECTION · 03",
        x_px=left_x, y_px=220, w_px=left_w, h_px=18,
        font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )

    # Divider title (56px, white, bold)
    add_text(
        slide, "divider-title", "What Slide Lab actually is",
        x_px=left_x, y_px=246, w_px=left_w, h_px=140,
        font_size_px=56, color=WHITE, bold=True,
    )

    # Divider rule (80x4 brand-accent)
    add_rect(slide, "divider-rule", x_px=left_x, y_px=400, w_px=80, h_px=4, fill_color=BRAND_ACCENT)

    # Divider subtitle (16px, brand-accent-soft)
    add_text(
        slide, "divider-subtitle",
        "The mechanics behind the thought partner — how it sharpens the thesis before it builds anything.",
        x_px=left_x, y_px=428, w_px=480, h_px=72,
        font_size_px=16, color=BRAND_ACCENT_SOFT,
    )

    # Right column: huge numeral
    # The CSS uses font-size 360px right-aligned. Place it center-right.
    add_text(
        slide, "divider-numeral", "03",
        x_px=640, y_px=140, w_px=560, h_px=420,
        font_size_px=360, color=BRAND_ACCENT, bold=True,
        align="right",
    )

    # Bottom accent rule
    add_rect(slide, "divider-bottom-rule", x_px=0, y_px=714, w_px=1280, h_px=6, fill_color=BRAND_ACCENT)

    # Footer (light variant on dark)
    text_on_dark_faint = RGBColor(0xB8, 0xA5, 0xD9)
    add_text(slide, "page-number", "6",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=text_on_dark_faint, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "06_section-divider-numeral.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
