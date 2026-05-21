"""
Builder for pattern 01d: Anchor with cards + icons — DARK variant.

Light source: twins/builders/build_01.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
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

    # Title (bottom-anchored at y=20, h=80 -> bottom-y=100)
    add_text(
        slide, "title",
        "Consultants rarely lack ideas — they struggle to <strong>cut through them</strong>.",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    # Subtitle y=108, h=22
    add_text(
        slide, "subtitle",
        "Not a knowledge gap. Not a skill deficit. A structural one — and structural problems have structural solutions.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    # Brand-rule y=132, w=64, h=3
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    card_glyphs = ["☰", "✦", "→"]
    card_y = 290
    card_w = 368
    card_h = 200
    gap = 24

    for i in range(3):
        cx = 64 + i * (card_w + gap)
        n = i + 1

        body = add_rect(slide, f"card-{n}-body-bg", cx, card_y, card_w, card_h, CARD_BG_DARK)
        body.line.color.rgb = CARD_BORDER_DARK
        body.line.width = 9525

        add_rect(slide, f"card-{n}-accent", cx, card_y, card_w, 2, BRAND_ACCENT_SOFT)

        add_icon(slide, f"card-{n}-icon", cx + 22, card_y + 22, 30, card_glyphs[i],
                 color=BRAND_ACCENT_SOFT)

        add_text(
            slide, f"card-{n}-heading",
            ["Too much to say", "Too many cooks", "The audience needs what's next"][i],
            x_px=cx + 22, y_px=card_y + 22 + 30 + 14,
            w_px=card_w - 44, h_px=22,
            font_size_px=16, color=WHITE, bold=True,
        )

        add_text(
            slide, f"card-{n}-body",
            [
                "Knowing what to cut is harder than knowing what to include. Every workstream produces legitimate findings, and not all of them belong on the page.",
                "Every collaborator has a view on what belongs on the page. More opinions mean harder choices, not a richer argument.",
                "They don't need to understand all the work. They need to understand the next step — and most decks bury it.",
            ][i],
            x_px=cx + 22, y_px=card_y + 22 + 30 + 14 + 22 + 8,
            w_px=card_w - 44, h_px=card_h - (22 + 30 + 14 + 22 + 8) - 22,
            font_size_px=13, color=TEXT_ON_DARK_MID,
        )

    # Convergence band — brand-accent (visibility on dark)
    conv_y = 720 - 78 - 42
    add_rect(slide, "convergence-bg",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42, fill_color=BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "The fix is a structured way to think, argue, and build — not another tool that produces slides faster.",
        x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42,
        font_size_px=14, color=WHITE, italic=True, bold=False,
        anchor="middle", padding_px=(0, 22, 0, 22),
    )

    # Source + page number (invariant footer)
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "2",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "01d_anchor-with-cards-icons.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
