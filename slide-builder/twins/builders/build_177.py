"""
Builder for pattern 177: Cover — Logo + Tagline + Meta. Left dark / right light split.

Source HTML: _pattern-library/177_cover-logo-tagline-meta.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BORDER, WHITE,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()

    # Left panel — 40% width, brand-primary fill
    left_w = int(1280 * 0.40)
    add_rect(slide, "cover-left-panel", 0, 0, left_w, 720, BRAND_PRIMARY)


    # Brand name & tagline (vertical center of left panel)
    brand_y = 280
    add_text(slide, "cover-brand-name", "ACCENTURE",
             x_px=48, y_px=brand_y, w_px=left_w - 96, h_px=32,
             font_size_px=24, color=WHITE, bold=True, uppercase=True)
    add_text(slide, "cover-tagline", "Let there be change.",
             x_px=48, y_px=brand_y + 40, w_px=left_w - 96, h_px=28,
             font_size_px=16, color=BRAND_ACCENT_SOFT, italic=True)
    add_rect(slide, "cover-left-rule", 48, brand_y + 80, left_w - 96, 1, RGBColor(0x60, 0x40, 0x80))

    # Right panel content
    right_x = left_w + 56
    right_w = 1280 - right_x - 48
    # Logo placeholder top-right
    add_rect(slide, "cover-logo", 1280 - 48 - 80, 32, 80, 30, RGBColor(0xD1, 0xD5, 0xDB))
    add_text(slide, "cover-logo-text", "LOGO",
             x_px=1280 - 48 - 80, y_px=32, w_px=80, h_px=30,
             font_size_px=8, color=RGBColor(0x6B, 0x72, 0x80), bold=True, align="center", anchor="middle", uppercase=True)

    # Title
    title_y = 220
    add_text(slide, "cover-deck-title",
             "Unlocking <strong>Growth</strong>\nThrough Digital Reinvention",
             x_px=right_x, y_px=title_y, w_px=480, h_px=120,
             font_size_px=32, color=BRAND_PRIMARY, bold=True,
             emphasis_color=BRAND_ACCENT)

    # Subtitle
    add_text(slide, "cover-subtitle",
             "A strategic roadmap for accelerating value creation and building resilience in an AI-powered economy.",
             x_px=right_x, y_px=title_y + 130, w_px=480, h_px=44,
             font_size_px=14, color=TEXT_MID)

    # Accent rule
    add_rect(slide, "cover-rule", right_x, title_y + 188, 64, 3, BRAND_ACCENT)

    # Meta block
    meta_y = title_y + 210
    metas = [
        ("Prepared for:", "[Client Name]"),
        ("Date:", "May 2026"),
        ("Classification:", "Confidential"),
    ]
    for i, (lbl, val) in enumerate(metas):
        add_text(slide, f"cover-meta-{i+1}",
                 f"<strong>{lbl}</strong>  {val}",
                 x_px=right_x, y_px=meta_y + i * 22, w_px=480, h_px=18,
                 font_size_px=12, color=TEXT_MID, emphasis_color=TEXT_DARK)

    # Footer
    add_text(slide, "page-number", "177",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "177_cover-logo-tagline-meta.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
