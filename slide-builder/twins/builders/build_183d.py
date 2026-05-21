"""
Builder for pattern 183d: Annotated Screenshot — DARK variant.

Light source: twins/builders/build_183.py
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

PHOTO_BG = RGBColor(0x2A, 0x14, 0x44)
PHOTO_BORDER = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Key findings <strong>annotated</strong> on the source screenshot",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Four callout markers highlight critical observations directly on the captured image",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    body_left = 48
    body_top = 220
    body_w = 1280 - 96
    body_h = 720 - body_top - 56

    ss_w = 700
    ss_h = 340
    ss_x = body_left + (body_w - ss_w) // 2
    ss_y = body_top + (body_h - ss_h) // 2

    ss = add_rect(slide, "photo-zone", ss_x, ss_y, ss_w, ss_h, PHOTO_BG)
    ss.line.color.rgb = PHOTO_BORDER
    ss.line.width = 19050
    add_text(slide, "photo-label", "Screenshot / Image",
             ss_x, ss_y, ss_w, ss_h,
             font_size_px=13, color=TEXT_ON_DARK_FAINT, bold=True,
             align="center", anchor="middle")

    pins = [
        (1, 0.22, 0.28),
        (2, 0.74, 0.24),
        (3, 0.26, 0.70),
        (4, 0.72, 0.72),
    ]
    pin_size = 24
    for n, fx, fy in pins:
        cx = ss_x + int(ss_w * fx)
        cy = ss_y + int(ss_h * fy)
        pin = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                      px_to_emu(cx - pin_size // 2),
                                      px_to_emu(cy - pin_size // 2),
                                      px_to_emu(pin_size), px_to_emu(pin_size))
        pin.name = f"pin-{n}-bg"
        pin.fill.solid()
        pin.fill.fore_color.rgb = BRAND_ACCENT_SOFT
        pin.line.fill.background()
        add_text(slide, f"pin-{n}", str(n),
                 cx - pin_size // 2, cy - pin_size // 2, pin_size, pin_size,
                 font_size_px=11, color=BRAND_PRIMARY, bold=True, align="center", anchor="middle")

    callout_w = 148
    callout_h = 50
    callouts = [
        (1, body_left + 0, body_top + 4, "① Navigation bar",
         "Primary menu collapses on mobile viewports below 768 px"),
        (2, body_left + body_w - callout_w, body_top + 4, "② Hero banner",
         "CTA button contrast ratio fails WCAG AA at current opacity"),
        (3, body_left + 0, body_top + body_h - callout_h - 6, "③ Data table",
         "Horizontal scroll triggers on columns exceeding viewport width"),
        (4, body_left + body_w - callout_w, body_top + body_h - callout_h - 6, "④ Footer links",
         "Legal disclaimer text renders at 9 px — below minimum legibility"),
    ]
    for n, x, y, head, body_txt in callouts:
        c = add_rect(slide, f"callout-{n}-bg", x, y, callout_w, callout_h, CARD_BG_DARK)
        c.line.color.rgb = CARD_BORDER_DARK
        c.line.width = 9525
        add_text(slide, f"callout-{n}-num", head,
                 x + 8, y + 4, callout_w - 16, 14,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"callout-{n}-text", body_txt,
                 x + 8, y + 20, callout_w - 16, callout_h - 24,
                 font_size_px=10, color=TEXT_ON_DARK_MID)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "183",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "183d_annotated-screenshot-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
