"""
Builder for pattern 05d: Screenshot hero with caption + step strip — DARK variant.

Light source: twins/builders/build_05.py
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
IMAGE_PH_BG = RGBColor(0x3C, 0x1F, 0x5C)
IMAGE_PH_BORDER = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Eyebrow
    add_text(
        slide, "eyebrow", "Demo · Think & Argue in action",
        x_px=64, y_px=64, w_px=600, h_px=16,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )

    # Title (editorial 26px, on dark → white)
    add_text(
        slide, "title",
        "A 30-second sequence — from governing thought to argued structure.",
        x_px=64, y_px=84, w_px=1050, h_px=64,
        font_size_px=26, color=WHITE, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Captured from a recent build session. Real input, real output, no scripted demo.",
        x_px=64, y_px=152, w_px=880, h_px=20,
        font_size_px=13, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=180, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    photo_top = 200
    photo_h = 280
    photo_w = 1280 - 128
    zone = add_rect(slide, "photo-zone", 64, photo_top, photo_w, photo_h, IMAGE_PH_BG)
    zone.line.color.rgb = IMAGE_PH_BORDER
    zone.line.width = 19050

    add_text(
        slide, "photo-corner-tag", "SCREENSHOT",
        x_px=78, y_px=photo_top + 12, w_px=110, h_px=18,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        bg_fill=RGBColor(0x14, 0x05, 0x28), padding_px=(2, 8, 2, 8), uppercase=True,
    )
    add_text(
        slide, "photo-label", "[ Demo capture — Slide Lab Think & Argue panel ]",
        x_px=64, y_px=photo_top, w_px=photo_w, h_px=photo_h,
        font_size_px=13, color=TEXT_ON_DARK_FAINT, bold=True,
        align="center", anchor="middle",
    )

    strip_top = photo_top + photo_h + 22
    step_w = (photo_w - 56) // 3
    step_gap = 28
    step_data = [
        ("1", "Governing thought entered",
         "The user states the one sentence the whole deck has to prove."),
        ("2", "Structure proposed",
         "Slide Lab returns a 6-slide outline with a so-what per slide."),
        ("3", "Argument tested",
         "The model surfaces three counterexamples and asks how to respond."),
    ]
    for i, (num, head, body) in enumerate(step_data):
        n = i + 1
        sx = 64 + i * (step_w + step_gap)
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            px_to_emu(sx), px_to_emu(strip_top),
            px_to_emu(30), px_to_emu(30),
        )
        circle.name = f"step-{n}-num-bg"
        circle.fill.solid()
        circle.fill.fore_color.rgb = BRAND_ACCENT
        circle.line.fill.background()
        add_text(
            slide, f"step-{n}-num", num,
            x_px=sx, y_px=strip_top, w_px=30, h_px=30,
            font_size_px=13, color=WHITE, bold=True,
            align="center", anchor="middle",
        )
        add_text(
            slide, f"step-{n}-heading", head,
            x_px=sx + 42, y_px=strip_top, w_px=step_w - 42, h_px=18,
            font_size_px=13, color=WHITE, bold=True,
        )
        add_text(
            slide, f"step-{n}-body", body,
            x_px=sx + 42, y_px=strip_top + 20, w_px=step_w - 42, h_px=44,
            font_size_px=12, color=TEXT_ON_DARK_MID,
        )

    # Takeaway convergence band — brand-accent
    conv_y = 720 - 70 - 44
    add_rect(slide, "convergence-bg",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=44, fill_color=BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "Twelve minutes from problem statement to a defensible structure — start of the deck, not the end.",
        x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=44,
        font_size_px=14, color=WHITE, italic=True,
        anchor="middle", padding_px=(0, 22, 0, 22),
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "7",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "05d_screenshot-hero-caption.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
