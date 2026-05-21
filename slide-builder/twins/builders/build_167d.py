"""
Builder for pattern 167d: Press / Coverage Compilation — 3x2 press card grid — dark.

Source HTML: _pattern-library/167_press-coverage-compilation-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
LOGO_BG = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title", "Media Coverage &amp; <strong>Press Highlights</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=26, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Curated press mentions, analyst coverage, and earned media — reporting period [Month YYYY]",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    cards_data = [
        ("Publication Name", "Article Headline Goes Here: Major Announcement Drives Sector Attention",
         '"Pull quote from the article that captures the key message or analyst perspective in one or two lines."',
         "DD Mon YYYY"),
        ("Publication Name", "Second Coverage Piece: Industry Recognition and Strategic Partnership",
         '"Supporting quote demonstrating positive sentiment or endorsement from the outlet or cited expert."',
         "DD Mon YYYY"),
        ("Publication Name", "Third Headline: Thought Leadership Feature in Top-Tier Outlet",
         '"Representative excerpt that highlights the editorial framing or independent validation of the narrative."',
         "DD Mon YYYY"),
        ("Publication Name", "Fourth Story: Client Outcome and Market Impact Covered Broadly",
         '"Quote reinforcing credibility or quantified impact as cited in the original coverage piece."',
         "DD Mon YYYY"),
        ("Publication Name", "Fifth Article: Executive Perspective Shapes Industry Conversation",
         '"Notable pull quote reflecting executive positioning or contributed viewpoint referenced by the outlet."',
         "DD Mon YYYY"),
        ("Publication Name", "Sixth Coverage Item: Innovation Story Earns Analyst Spotlight",
         '"Closing quote that underscores differentiated positioning or relevance to the target audience."',
         "DD Mon YYYY"),
    ]

    grid_left = 48
    grid_top = 220
    grid_w = 1280 - 96
    gap = 16
    card_w = (grid_w - 2 * gap) // 3
    card_h = (664 - grid_top - gap) // 2

    for i, (outlet, head, quote, date) in enumerate(cards_data):
        n = i + 1
        col = i % 3
        row = i // 3
        cx = grid_left + col * (card_w + gap)
        cy = grid_top + row * (card_h + gap)

        card = add_rect(slide, f"card-{n}-bg", cx, cy, card_w, card_h, CARD_BG_DARK)
        card.line.color.rgb = CARD_BORDER_DARK
        card.line.width = 9525
        add_rect(slide, f"card-{n}-accent", cx, cy, 3, card_h, BRAND_ACCENT)

        add_text(slide, f"card-{n}-outlet", outlet,
                 cx + 14, cy + 14, card_w - 80, 14,
                 font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
        add_rect(slide, f"card-{n}-logo",
                 cx + card_w - 62, cy + 12, 48, 20, LOGO_BG)
        add_text(slide, f"card-{n}-heading", head,
                 cx + 14, cy + 36, card_w - 28, 40,
                 font_size_px=13, color=WHITE, bold=True)
        add_text(slide, f"card-{n}-body", quote,
                 cx + 14, cy + 80, card_w - 28, card_h - 110,
                 font_size_px=11, color=TEXT_ON_DARK_MID, italic=True)
        add_text(slide, f"card-{n}-footer", date,
                 cx + 14, cy + card_h - 22, card_w - 28, 14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, align="right", uppercase=True)

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "167",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "167d_press-coverage-compilation.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
