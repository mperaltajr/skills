"""
Builder for pattern 22d: Photo hero with editorial caption — DARK variant.

Light source: twins/builders/build_22.py
Light variant has photo (dark left) + light right caption. 22d inverts the
caption side to also be dark.
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
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
PHOTO_BG = RGBColor(0x14, 0x05, 0x28)  # darker, for photo zone contrast


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Top rule (4px brand-accent)
    add_rect(slide, "top-rule", x_px=0, y_px=44, w_px=1280, h_px=4, fill_color=BRAND_ACCENT)

    body_top = 72
    body_bottom = 672
    body_h = body_bottom - body_top
    photo_w = int(1280 * 58 / 100)
    cap_w = 1280 - photo_w

    # LEFT — photo zone (darker than slide bg)
    pz_left = 40
    pz_top = body_top + 16
    pz_w = photo_w - pz_left
    pz_h = body_h - 32
    photo = add_rect(slide, "photo-zone", pz_left, pz_top, pz_w, pz_h, PHOTO_BG)
    photo.line.color.rgb = BRAND_ACCENT_SOFT
    photo.line.width = 19050

    add_text(
        slide, "photo-corner-tag", "PHOTO PLACEHOLDER",
        x_px=pz_left + 16, y_px=pz_top + 16, w_px=180, h_px=22,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
        bg_fill=BRAND_PRIMARY, padding_px=(4, 10, 4, 10),
    )

    add_text(
        slide, "photo-meta", "SCENARIO IMAGE",
        x_px=pz_left + 24, y_px=pz_top + pz_h - 56, w_px=400, h_px=18,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "photo-meta-filename", "replace · scene-01_review-cycle.jpg",
        x_px=pz_left + 24, y_px=pz_top + pz_h - 36, w_px=400, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT, italic=True,
        font_name="Consolas",
    )

    # RIGHT — caption zone on dark bg
    cap_x = photo_w + 44
    cap_top = body_top + 40
    cap_inner_w = cap_w - 100

    add_text(
        slide, "eyebrow", "SCENE 1",
        x_px=cap_x, y_px=cap_top, w_px=cap_inner_w, h_px=14,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "title",
        "The deck got 40% longer in the last review cycle.",
        x_px=cap_x, y_px=cap_top + 34, w_px=cap_inner_w, h_px=120,
        font_size_px=28, color=WHITE, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Every reviewer added something. Nobody removed anything.",
        x_px=cap_x, y_px=cap_top + 164, w_px=cap_inner_w, h_px=44,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=cap_x, y_px=cap_top + 218, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    add_text(
        slide, "caption-list-label", "WHAT THIS LOOKS LIKE",
        x_px=cap_x, y_px=cap_top + 240, w_px=cap_inner_w, h_px=14,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True,
    )
    add_text(
        slide, "photo-caption",
        "• Slide 6 spawned a backup appendix, then the appendix spawned its own backup.\n"
        "• Three logos got bigger; the argument did not.\n"
        "• The exec read the first page and the last page — same as always.",
        x_px=cap_x, y_px=cap_top + 264, w_px=cap_inner_w, h_px=120,
        font_size_px=13, color=WHITE,
    )

    attr_y = cap_top + 400
    add_rect(slide, "attribution-rule", x_px=cap_x, y_px=attr_y, w_px=cap_inner_w, h_px=1, fill_color=CARD_BORDER_DARK)
    add_text(
        slide, "photo-attribution",
        "Composite scenario · based on 12 pilot conversations",
        x_px=cap_x, y_px=attr_y + 14, w_px=cap_inner_w, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, italic=True,
    )

    add_text(slide, "page-number", "22",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "22d_photo-hero-caption.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
