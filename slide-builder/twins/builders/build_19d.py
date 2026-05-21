"""
Builder for pattern 19d: Cover slide — split-panel — DARK variant (fully dark).

Light source: twins/builders/build_19.py
19 itself has a dark left + light right. 19d goes fully dark, with the right
meta panel inverted to dark surface + light text.

Cover-only chrome — no standard title block, no convergence.
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
LEFT_PANEL_DARKER = RGBColor(0x14, 0x05, 0x28)  # darker than slide bg for contrast


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Left panel — darker shade for separation
    add_rect(slide, "cover-left-panel", x_px=0, y_px=0, w_px=640, h_px=720, fill_color=LEFT_PANEL_DARKER)

    # Right edge accent strip
    add_rect(slide, "cover-left-accent", x_px=636, y_px=64, w_px=4, h_px=600, fill_color=BRAND_ACCENT)

    # Pre-label
    add_text(
        slide, "cover-pre-label", "INTERNAL DECK · 2026",
        x_px=64, y_px=64, w_px=400, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )

    # Deck title (60px white bold)
    add_text(
        slide, "cover-deck-title", "Slide Lab",
        x_px=64, y_px=260, w_px=540, h_px=76,
        font_size_px=60, color=WHITE, bold=True,
    )

    # Tagline
    add_text(
        slide, "cover-tagline", "Think. Argue. Build.",
        x_px=64, y_px=348, w_px=540, h_px=28,
        font_size_px=19, color=BRAND_ACCENT_SOFT, italic=True,
    )

    # Presented-by — bottom-left
    pby_y = 580
    presented_border = RGBColor(0x4A, 0x2B, 0x6E)
    add_rect(slide, "cover-presented-rule", x_px=64, y_px=pby_y, w_px=360, h_px=1, fill_color=presented_border)
    add_text(
        slide, "cover-presented-label", "PRESENTED BY",
        x_px=64, y_px=pby_y + 14, w_px=360, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "cover-presented-name", "Mario Peralta · Strategy Manager",
        x_px=64, y_px=pby_y + 32, w_px=360, h_px=22,
        font_size_px=15, color=WHITE, bold=True,
    )

    # RIGHT panel — meta block on dark
    meta_left = 704
    meta_top = 270

    add_rect(slide, "cover-meta-rule", x_px=meta_left, y_px=meta_top, w_px=4, h_px=180, fill_color=BRAND_ACCENT)

    meta_x = meta_left + 32
    meta_rows = [
        ("PREPARED FOR", "Internal · Accenture Strategy", True),
        ("DATE", "May 2026", False),
        ("DURATION", "30 minutes", False),
    ]
    row_y = meta_top
    for i, (label, value, is_lead) in enumerate(meta_rows):
        n = i + 1
        add_text(
            slide, f"cover-meta-{n}-label", label,
            x_px=meta_x, y_px=row_y, w_px=400, h_px=14,
            font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"cover-meta-{n}-value", value,
            x_px=meta_x, y_px=row_y + 16, w_px=440, h_px=28 if is_lead else 22,
            font_size_px=22 if is_lead else 17,
            color=BRAND_ACCENT_SOFT if is_lead else WHITE,
            bold=is_lead,
        )
        row_y += 64

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "19d_cover-split-panel.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
