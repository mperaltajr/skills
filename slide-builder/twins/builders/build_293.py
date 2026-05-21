"""
Builder for pattern 293: Key question (dark) — text-hero style.

Centered hero treatment: label, big question, accent rule, context paragraph,
3 sub-question pills row.

Source HTML: _pattern-library/293_key-question-dark.html
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

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
PILL_BG = RGBColor(0x4A, 0x29, 0x76)
PILL_BORDER = RGBColor(0x6E, 0x4F, 0x9E)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Canonical chrome — title/subtitle/brand-rule per spec.
    # NOTE: This is a centered-hero pattern; the canonical chrome layout
    # doesn't fit its original intent. Flagged for redesign.
    add_text(slide, "title",
             "Key Question",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Framing the central strategic tension for this session",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 80, 3, BRAND_ACCENT_SOFT)

    # Main question (shifted into body zone)
    add_text(slide, "kq-question",
             "How do we accelerate growth while managing risk across an increasingly fragmented market?",
             x_px=210, y_px=230, w_px=860, h_px=120,
             font_size_px=26, color=WHITE, bold=True, align="center")

    # Accent rule (centered, 80px wide, 4px tall)
    add_rect(slide, "kq-rule", (1280 - 80) // 2, 370, 80, 4, BRAND_ACCENT)

    # Context paragraph
    add_text(slide, "kq-context",
             "As competitive pressure intensifies and customer expectations shift, leadership must align on a clear strategic direction. This session examines the core tensions shaping our path forward and frames the choices that will define the next chapter.",
             x_px=300, y_px=400, w_px=680, h_px=92,
             font_size_px=13, color=TEXT_ON_DARK_MID, align="center")

    # 3 sub-question pills row, centered
    pills = [
        ("1.", "Where are we winning today, and why does it matter?"),
        ("2.", "What capabilities do we need to build or acquire?"),
        ("3.", "Which trade-offs are we prepared to make to move fast?"),
    ]
    pill_w = 260
    pill_h = 76
    pill_gap = 14
    total = 3 * pill_w + 2 * pill_gap
    px_start = (1280 - total) // 2
    py = 530
    for i, (prefix, txt) in enumerate(pills):
        px = px_start + i * (pill_w + pill_gap)
        add_rect(slide, f"pill-{i+1}-bg", px, py, pill_w, pill_h, PILL_BG)
        add_text(slide, f"pill-{i+1}-prefix", prefix,
                 x_px=px + 16, y_px=py + 14, w_px=24, h_px=20,
                 font_size_px=13, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"pill-{i+1}-text", txt,
                 x_px=px + 40, y_px=py + 14, w_px=pill_w - 56, h_px=pill_h - 24,
                 font_size_px=12, color=WHITE)

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "293",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "293_key-question-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
