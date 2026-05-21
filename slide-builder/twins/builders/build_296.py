"""
Builder for pattern 296: Thank You / Q&A.

Source HTML: _pattern-library/296_thank-you-qa.html

Centered "Thank You & Questions" closing slide. Decorative faint background "?",
large headline, accent rule, two contact cards, appendix strip.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Decorative background "?" (very faint primary)
    add_text(
        slide, "deco-question", "?",
        x_px=900, y_px=60, w_px=320, h_px=240,
        font_size_px=200, color=RGBColor(0xF0, 0xE8, 0xF5), bold=True,
        anchor="top", align="center",
    )

    # Headline: "Thank You &" (& in brand-accent)
    # Center the two-line composite
    add_text(
        slide, "headline-thankyou", "Thank You <strong>&</strong>",
        x_px=240, y_px=170, w_px=800, h_px=80,
        font_size_px=58, color=BRAND_PRIMARY, bold=True,
        align="center", emphasis_color=BRAND_ACCENT,
    )
    add_text(
        slide, "headline-sub", "Questions & Discussion",
        x_px=240, y_px=258, w_px=800, h_px=40,
        font_size_px=24, color=TEXT_MID, italic=True, align="center",
    )

    # Accent rule
    add_rect(slide, "accent-rule", x_px=600, y_px=320, w_px=80, h_px=4,
             fill_color=BRAND_ACCENT)

    # Contacts row — two cards centered with divider
    contacts_y = 380
    # Left contact (right-aligned text)
    add_text(
        slide, "contact-1-name", "Sarah Mitchell",
        x_px=320, y_px=contacts_y, w_px=270, h_px=20,
        font_size_px=15, color=TEXT_DARK, bold=True, align="right",
    )
    add_text(
        slide, "contact-1-role", "Lead Partner, Strategy & Consulting",
        x_px=320, y_px=contacts_y + 22, w_px=270, h_px=18,
        font_size_px=12, color=TEXT_MID, align="right",
    )
    add_text(
        slide, "contact-1-email", "sarah.mitchell@accenture.com",
        x_px=320, y_px=contacts_y + 44, w_px=270, h_px=18,
        font_size_px=12, color=TEXT_MID, align="right",
    )
    add_text(
        slide, "contact-1-phone", "+1 (212) 555 0142",
        x_px=320, y_px=contacts_y + 64, w_px=270, h_px=18,
        font_size_px=12, color=TEXT_MID, align="right",
    )

    # Vertical divider
    add_rect(slide, "contact-divider", 638, contacts_y + 4, 1, 80, CARD_BORDER)

    # Right contact (left-aligned text)
    add_text(
        slide, "contact-2-name", "David Okafor",
        x_px=688, y_px=contacts_y, w_px=270, h_px=20,
        font_size_px=15, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "contact-2-role", "Managing Director, Technology",
        x_px=688, y_px=contacts_y + 22, w_px=270, h_px=18,
        font_size_px=12, color=TEXT_MID,
    )
    add_text(
        slide, "contact-2-email", "david.okafor@accenture.com",
        x_px=688, y_px=contacts_y + 44, w_px=270, h_px=18,
        font_size_px=12, color=TEXT_MID,
    )
    add_text(
        slide, "contact-2-phone", "+1 (312) 555 0387",
        x_px=688, y_px=contacts_y + 64, w_px=270, h_px=18,
        font_size_px=12, color=TEXT_MID,
    )

    # Appendix strip — centered
    strip_w = 360
    strip_x = (1280 - strip_w) // 2
    strip_y = 540
    strip = add_rect(slide, "appendix-strip", strip_x, strip_y, strip_w, 42, CARD_BG)
    strip.line.color.rgb = CARD_BORDER
    strip.line.width = 9525
    # arrow + text
    add_text(
        slide, "appendix-arrow", "→",
        x_px=strip_x + 16, y_px=strip_y, w_px=22, h_px=42,
        font_size_px=18, color=BRAND_ACCENT, bold=True, anchor="middle",
    )
    add_text(
        slide, "appendix-text", "APPENDIX AVAILABLE UPON REQUEST",
        x_px=strip_x + 44, y_px=strip_y, w_px=strip_w - 56, h_px=42,
        font_size_px=12, color=TEXT_MID, bold=True, anchor="middle",
        uppercase=True, letter_spacing_px=1,
    )

    add_footer(slide, page_num=296)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "296_thank-you-qa.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
