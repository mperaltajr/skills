"""
Builder for pattern 183: Annotated Screenshot — photo placeholder + 4 pins + callouts.

Source HTML: _pattern-library/183_annotated-screenshot.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer, add_title_block,
    BRAND_ACCENT, CARD_BG, CARD_BORDER, TEXT_DARK,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

PHOTO_BG = RGBColor(0xD1, 0xD5, 0xDB)
PHOTO_BORDER = RGBColor(0xB0, 0xB7, 0xC3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Key findings <strong>annotated</strong> on the source screenshot",
        subtitle="Four callout markers highlight critical observations directly on the captured image",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

    # Body area
    body_left = 48
    body_top = 156
    body_w = 1280 - 96
    body_h = 720 - body_top - 56

    # Screenshot centered
    ss_w = 700
    ss_h = 380
    ss_x = body_left + (body_w - ss_w) // 2
    ss_y = body_top + (body_h - ss_h) // 2

    ss = add_rect(slide, "photo-zone", ss_x, ss_y, ss_w, ss_h, PHOTO_BG)
    ss.line.color.rgb = PHOTO_BORDER
    ss.line.width = 19050
    add_text(slide, "photo-label", "Screenshot / Image",
             ss_x, ss_y, ss_w, ss_h,
             font_size_px=13, color=RGBColor(0x6B, 0x72, 0x80), bold=True,
             align="center", anchor="middle")

    # Pin positions (relative to screenshot)
    pins = [
        (1, 0.22, 0.28),
        (2, 0.74, 0.24),
        (3, 0.26, 0.70),
        (4, 0.72, 0.72),
    ]
    pin_size = 24
    pin_coords = {}
    for n, fx, fy in pins:
        cx = ss_x + int(ss_w * fx)
        cy = ss_y + int(ss_h * fy)
        pin = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                      px_to_emu(cx - pin_size // 2),
                                      px_to_emu(cy - pin_size // 2),
                                      px_to_emu(pin_size), px_to_emu(pin_size))
        pin.name = f"pin-{n}-bg"
        pin.fill.solid()
        pin.fill.fore_color.rgb = BRAND_ACCENT
        pin.line.fill.background()
        add_text(slide, f"pin-{n}", str(n),
                 cx - pin_size // 2, cy - pin_size // 2, pin_size, pin_size,
                 font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle")
        pin_coords[n] = (cx, cy)

    # Callouts (relative to body area outer corners)
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
    callout_anchors = {}
    for n, x, y, head, body_txt in callouts:
        c = add_rect(slide, f"callout-{n}-bg", x, y, callout_w, callout_h, CARD_BG)
        c.line.color.rgb = CARD_BORDER
        c.line.width = 9525
        add_text(slide, f"callout-{n}-num", head,
                 x + 8, y + 4, callout_w - 16, 14,
                 font_size_px=10, color=BRAND_ACCENT, bold=True)
        add_text(slide, f"callout-{n}-text", body_txt,
                 x + 8, y + 20, callout_w - 16, callout_h - 24,
                 font_size_px=10, color=TEXT_DARK)
        # Anchor: side toward pin
        if x == body_left + 0:
            ax = x + callout_w
        else:
            ax = x
        ay = y + callout_h // 2
        callout_anchors[n] = (ax, ay)

    # Connector lines (rectangles approximating thin lines from anchor to pin)
    # Use thin rects since we cannot easily draw diagonal lines without connector helper.
    # Skip diagonal — keep as documentation; lines are decorative.

    add_footer(slide, page_num=183)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "183_annotated-screenshot.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
