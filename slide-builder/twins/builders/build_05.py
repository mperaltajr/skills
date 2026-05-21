"""
Builder for pattern 05: Screenshot hero with caption + step strip + takeaway.

Source HTML: _pattern-library/05_screenshot-hero-caption.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

IMAGE_PH_BG = RGBColor(0xF1, 0xF5, 0xF9)
IMAGE_PH_BORDER = RGBColor(0xCB, 0xD5, 0xE1)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Eyebrow
    add_text(
        slide, "eyebrow", "Demo · Think & Argue in action",
        x_px=64, y_px=64, w_px=600, h_px=16,
        font_size_px=11, color=BRAND_ACCENT, bold=True, uppercase=True,
    )

    # Title (26px)
    add_text(
        slide, "title",
        "A 30-second sequence — from governing thought to argued structure.",
        x_px=64, y_px=84, w_px=1050, h_px=64,
        font_size_px=26, color=TEXT_DARK, bold=True,
    )

    # Subtitle
    add_text(
        slide, "subtitle",
        "Captured from a recent build session. Real input, real output, no scripted demo.",
        x_px=64, y_px=152, w_px=880, h_px=20,
        font_size_px=13, color=TEXT_MID, italic=True,
    )

    # Brand-rule
    add_rect(slide, "brand-rule", x_px=64, y_px=180, w_px=64, h_px=3, fill_color=BRAND_ACCENT)

    # Screenshot zone (height 300px, dashed border, centered text)
    photo_top = 200
    photo_h = 280
    photo_w = 1280 - 128
    zone = add_rect(slide, "photo-zone", 64, photo_top, photo_w, photo_h, IMAGE_PH_BG)
    zone.line.color.rgb = IMAGE_PH_BORDER
    zone.line.width = 19050  # ~2px

    # Photo corner tag
    add_text(
        slide, "photo-corner-tag", "SCREENSHOT",
        x_px=78, y_px=photo_top + 12, w_px=110, h_px=18,
        font_size_px=10, color=BRAND_ACCENT, bold=True,
        bg_fill=WHITE, padding_px=(2, 8, 2, 8), uppercase=True,
    )

    # Photo label centered
    add_text(
        slide, "photo-label", "[ Demo capture — Slide Lab Think & Argue panel ]",
        x_px=64, y_px=photo_top, w_px=photo_w, h_px=photo_h,
        font_size_px=13, color=TEXT_FAINT, bold=True,
        align="center", anchor="middle",
    )

    # Step strip (3 numbered steps)
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
        # Numbered circle (30x30 brand-accent)
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            px_to_emu(sx), px_to_emu(strip_top),
            px_to_emu(30), px_to_emu(30),
        )
        circle.name = f"step-{n}-num-bg"
        circle.fill.solid()
        circle.fill.fore_color.rgb = BRAND_ACCENT
        circle.line.fill.background()
        # Number text on top of circle
        add_text(
            slide, f"step-{n}-num", num,
            x_px=sx, y_px=strip_top, w_px=30, h_px=30,
            font_size_px=13, color=WHITE, bold=True,
            align="center", anchor="middle",
        )
        # Step heading
        add_text(
            slide, f"step-{n}-heading", head,
            x_px=sx + 42, y_px=strip_top, w_px=step_w - 42, h_px=18,
            font_size_px=13, color=BRAND_PRIMARY, bold=True,
        )
        # Step body
        add_text(
            slide, f"step-{n}-body", body,
            x_px=sx + 42, y_px=strip_top + 20, w_px=step_w - 42, h_px=44,
            font_size_px=12, color=TEXT_DARK,
        )

    # Takeaway convergence band — at bottom: 70 from bottom
    add_convergence(
        slide,
        "Twelve minutes from problem statement to a defensible structure — start of the deck, not the end.",
        bottom_px=70, height_px=44,
    )

    add_footer(slide, page_num=7)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "05_screenshot-hero-caption.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
