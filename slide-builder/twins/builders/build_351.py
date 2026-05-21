"""
Builder for pattern 351: Dark Closing CTA.

Source HTML: _pattern-library/351_dark-closing-cta.html
Standalone — closest light reference: 40_closing-cta-revival;
closest dark sibling: 294_where-we-go-from-here-dark.

Layout: editorial closing slide.
  - Eyebrow "NEXT STEPS"
  - Hero statement "We recommend moving forward"
  - Brand-rule
  - 3 step cards (numbered, with timeframe chip + action text)
  - "Ready to begin?" headline
  - Contact strip (email + Mario profile pill)

Treated as standalone — title block omitted intentionally because the
editorial design uses an eyebrow + hero pattern rather than the standard
title/subtitle/rule layout. (LinkedIn glyph approximated with text "in".)
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def add_oval(slide, name, x, y, size, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                 px_to_emu(x), px_to_emu(y),
                                 px_to_emu(size), px_to_emu(size))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Editorial title block: eyebrow + hero statement + brand rule
    # (Title shape kept for canonical anchor at y bottom=100)
    add_text(slide, "title-eyebrow", "NEXT STEPS",
             x_px=64, y_px=68, w_px=600, h_px=20,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=3)
    add_text(slide, "title",
             "We recommend <strong>moving forward</strong>",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=36, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    # Hide actual title position with eyebrow above
    # Brand rule
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)
    # Subtitle slot kept empty for canonical compliance
    add_text(slide, "subtitle", "",
             x_px=64, y_px=108, w_px=600, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)

    # Step cards
    cards_y = 240
    cards_h = 240
    gap = 20
    card_w = (1152 - 2 * gap) // 3
    steps = [
        ("1", "Align Stakeholders", "This Week",
         "Schedule executive sponsor review and confirm decision authority for program go-ahead."),
        ("2", "Finalize Scope & Team", "Next Sprint",
         "Lock MVP scope, confirm resourcing, and issue statements of work for Wave 1 delivery."),
        ("3", "Launch & Measure", "Q3",
         "Begin Sprint 1, establish baseline KPIs, and set cadence for bi-weekly steering updates."),
    ]
    for i, (n, title, when, action) in enumerate(steps):
        x = 64 + i * (card_w + gap)
        c = add_rect(slide, f"step-{n}-bg", x, cards_y, card_w, cards_h, CARD_BG_DARK)
        c.line.color.rgb = CARD_BORDER_DARK
        c.line.width = 9525
        # Number circle
        add_oval(slide, f"step-{n}-num-bg", x + 22, cards_y + 22, 44, BRAND_ACCENT)
        add_text(slide, f"step-{n}-num", n,
                 x_px=x + 22, y_px=cards_y + 22, w_px=44, h_px=44,
                 font_size_px=22, color=WHITE, bold=True,
                 align="center", anchor="middle")
        add_text(slide, f"step-{n}-title", title,
                 x_px=x + 22, y_px=cards_y + 76, w_px=card_w - 44, h_px=28,
                 font_size_px=18, color=WHITE, bold=True)
        # Timeframe chip
        pill = add_rect(slide, f"step-{n}-when-bg", x + 22, cards_y + 110, 100, 22,
                        BRAND_PRIMARY_MID)
        pill.line.color.rgb = BRAND_ACCENT_SOFT
        pill.line.width = 6350
        add_text(slide, f"step-{n}-when", when,
                 x_px=x + 22, y_px=cards_y + 110, w_px=100, h_px=22,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", anchor="middle", uppercase=True,
                 letter_spacing_px=1)
        add_text(slide, f"step-{n}-action", action,
                 x_px=x + 22, y_px=cards_y + 144, w_px=card_w - 44, h_px=cards_h - 156,
                 font_size_px=12, color=TEXT_ON_DARK_MID)

    # Ready headline
    add_text(slide, "ready", "Ready to begin?",
             x_px=64, y_px=502, w_px=1152, h_px=46,
             font_size_px=28, color=BRAND_ACCENT_SOFT, bold=True, italic=True,
             align="center")

    # Contact strip
    strip_y = 564
    strip_h = 88
    strip = add_rect(slide, "contact-bg", 160, strip_y, 960, strip_h, CARD_BG_DARK)
    strip.line.color.rgb = BRAND_ACCENT_SOFT
    strip.line.width = 9525
    # Email
    add_text(slide, "contact-email", "presenter@example.com",
             x_px=180, y_px=strip_y, w_px=380, h_px=strip_h,
             font_size_px=14, color=WHITE, bold=True, anchor="middle")
    # Divider
    add_rect(slide, "contact-divider", 560, strip_y + 24, 1, strip_h - 48,
             CARD_BORDER_DARK)
    # Profile pill
    add_oval(slide, "profile-avatar", 580, strip_y + 22, 44, BRAND_ACCENT)
    add_text(slide, "profile-init", "MP",
             x_px=580, y_px=strip_y + 22, w_px=44, h_px=44,
             font_size_px=14, color=WHITE, bold=True,
             align="center", anchor="middle")
    add_text(slide, "profile-name", "Mario Peralta",
             x_px=636, y_px=strip_y + 20, w_px=380, h_px=22,
             font_size_px=14, color=WHITE, bold=True)
    add_text(slide, "profile-role", "Managing Director · Strategy & Consulting",
             x_px=636, y_px=strip_y + 42, w_px=380, h_px=18,
             font_size_px=11, color=TEXT_ON_DARK_MID, italic=True)
    # LinkedIn glyph (approximated)
    add_rect(slide, "linkedin-bg", 1060, strip_y + 30, 28, 28,
             RGBColor(0x0A, 0x66, 0xC2))
    add_text(slide, "linkedin-glyph", "in",
             x_px=1060, y_px=strip_y + 30, w_px=28, h_px=28,
             font_size_px=14, color=WHITE, bold=True, italic=True,
             align="center", anchor="middle")

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "351",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "351_dark-closing-cta.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
