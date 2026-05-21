"""
Builder for pattern 177d: Cover — Logo + Tagline + Meta, DARK variant.

Light source: twins/builders/build_177.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Left panel — even darker than the slide bg for separation
    left_w = int(1280 * 0.40)
    add_rect(slide, "cover-left-panel", 0, 0, left_w, 720, RGBColor(0x1A, 0x05, 0x33))

    brand_y = 280
    add_rect(slide, "cover-left-rule", 48, brand_y + 80, left_w - 96, 1, CARD_BORDER_DARK)
    add_text(slide, "cover-tagline-label", "STRATEGIC ADVISORY",
             x_px=48, y_px=brand_y, w_px=left_w - 96, h_px=32,
             font_size_px=14, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "cover-tagline", "Let there be change.",
             x_px=48, y_px=brand_y + 40, w_px=left_w - 96, h_px=28,
             font_size_px=16, color=WHITE, italic=True)

    # Right panel — on the brand-primary main bg
    right_x = left_w + 56
    right_w = 1280 - right_x - 48

    title_y = 220
    add_text(slide, "cover-deck-title",
             "Unlocking <strong>Growth</strong>\nThrough Digital Reinvention",
             x_px=right_x, y_px=title_y, w_px=480, h_px=120,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT)

    add_text(slide, "cover-subtitle",
             "A strategic roadmap for accelerating value creation and building resilience in an AI-powered economy.",
             x_px=right_x, y_px=title_y + 130, w_px=480, h_px=44,
             font_size_px=14, color=TEXT_ON_DARK_MID)

    add_rect(slide, "cover-rule", right_x, title_y + 188, 64, 3, BRAND_ACCENT_SOFT)

    meta_y = title_y + 210
    metas = [
        ("Prepared for:", "[Client Name]"),
        ("Date:", "May 2026"),
    ]
    for i, (lbl, val) in enumerate(metas):
        add_text(slide, f"cover-meta-{i+1}",
                 f"<strong>{lbl}</strong>  {val}",
                 x_px=right_x, y_px=meta_y + i * 22, w_px=480, h_px=18,
                 font_size_px=12, color=TEXT_ON_DARK_MID, emphasis_color=WHITE)

    add_text(slide, "page-number", "177",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "177d_cover-logo-tagline-meta-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
