"""
Builder for pattern 167: Press / Coverage Compilation — 3x2 press card grid.

Source HTML: _pattern-library/167_press-coverage-compilation.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT,
)
from pptx.dml.color import RGBColor

LOGO_BG = RGBColor(0xD9, 0xD9, 0xD9)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Media Coverage &amp; <strong>Press Highlights</strong>",
        subtitle="Curated press mentions, analyst coverage, and earned media — reporting period [Month YYYY]",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

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
    grid_top = 156
    grid_w = 1280 - 96
    gap = 16
    card_w = (grid_w - 2 * gap) // 3
    card_h = (720 - 64 - grid_top - gap) // 2

    for i, (outlet, head, quote, date) in enumerate(cards_data):
        n = i + 1
        col = i % 3
        row = i // 3
        cx = grid_left + col * (card_w + gap)
        cy = grid_top + row * (card_h + gap)

        # Card body
        card = add_rect(slide, f"card-{n}-bg", cx, cy, card_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Left accent stripe
        add_rect(slide, f"card-{n}-accent", cx, cy, 3, card_h, BRAND_ACCENT)

        # Outlet name
        add_text(slide, f"card-{n}-outlet", outlet,
                 cx + 14, cy + 14, card_w - 80, 14,
                 font_size_px=11, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
        # Logo placeholder
        add_rect(slide, f"card-{n}-logo",
                 cx + card_w - 62, cy + 12, 48, 20, LOGO_BG)
        # Headline
        add_text(slide, f"card-{n}-heading", head,
                 cx + 14, cy + 36, card_w - 28, 40,
                 font_size_px=13, color=TEXT_DARK, bold=True)
        # Pull-quote
        add_text(slide, f"card-{n}-body", quote,
                 cx + 14, cy + 80, card_w - 28, card_h - 110,
                 font_size_px=11, color=TEXT_MID, italic=True)
        # Date
        add_text(slide, f"card-{n}-footer", date,
                 cx + 14, cy + card_h - 22, card_w - 28, 14,
                 font_size_px=9, color=TEXT_FAINT, align="right", uppercase=True)

    add_footer(slide, page_num=167)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "167_press-coverage-compilation.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
