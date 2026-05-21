"""
Builder for pattern 170: News Timeline — horizontal timeline with above/below cards.

Source HTML: _pattern-library/170_news-timeline.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_FAINT, WHITE,
)
from pptx.enum.shapes import MSO_SHAPE


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Five Years of <strong>Market-Shifting</strong> Events",
        subtitle="A chronological view of the developments that redefined the competitive landscape, 2020-2025",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

    # Timeline area: top=168, bottom=64, left=48, right=48
    area_top = 168
    area_bottom = 720 - 64
    area_left = 48
    area_w = 1280 - 96
    axis_y = (area_top + area_bottom) // 2

    # Axis
    add_rect(slide, "timeline-axis", area_left, axis_y - 1, area_w, 2, BRAND_PRIMARY_MID)

    events = [
        ("Mar 2020", "Global Lockdowns Accelerate Digital Adoption",
         "McKinsey Global Institute · Mar 2020", "above", False),
        ("Jun 2021", "Supply Chain Disruptions Reshape Global Trade",
         "World Economic Forum · Jun 2021", "below", False),
        ("Nov 2022", "Generative AI Goes Mainstream — ChatGPT Launches",
         "OpenAI · Nov 2022 — Key Moment", "above", True),
        ("Apr 2023", "Regulators Move on AI — EU AI Act Advances",
         "European Parliament · Apr 2023", "below", False),
        ("Jan 2025", "Agentic AI Deployments Enter Enterprise at Scale",
         "Gartner Hype Cycle · Jan 2025", "above", False),
    ]
    n_events = len(events)
    col_w = area_w // n_events
    card_w = 186
    card_h = 88

    for i, (date, head, src, side, is_key) in enumerate(events):
        n = i + 1
        cx_center = area_left + col_w * i + col_w // 2
        # Dot
        dot_size = 15 if is_key else 12
        dot_x = cx_center - dot_size // 2
        dot_y = axis_y - dot_size // 2
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                      px_to_emu(dot_x), px_to_emu(dot_y),
                                      px_to_emu(dot_size), px_to_emu(dot_size))
        dot.name = f"event-{n}-dot"
        dot.fill.solid()
        dot.fill.fore_color.rgb = BRAND_ACCENT if is_key else BRAND_PRIMARY_MID
        dot.line.color.rgb = WHITE
        dot.line.width = 19050

        # Connector
        conn_h = 28
        if side == "above":
            conn_y = axis_y - dot_size // 2 - conn_h
            card_y = conn_y - card_h - 4
        else:
            conn_y = axis_y + dot_size // 2
            card_y = axis_y + dot_size // 2 + conn_h + 4
        add_rect(slide, f"event-{n}-connector", cx_center - 1, conn_y, 2, conn_h, BRAND_PRIMARY_MID)

        # Card
        card_x = cx_center - card_w // 2
        card = add_rect(slide, f"event-{n}-card", card_x, card_y, card_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        if is_key:
            add_rect(slide, f"event-{n}-accent", card_x, card_y, 3, card_h, BRAND_ACCENT)

        # Date chip
        chip_w = 60
        chip_h = 16
        add_rect(slide, f"event-{n}-date-chip-bg", card_x + 10, card_y + 8, chip_w, chip_h, BRAND_ACCENT)
        add_text(slide, f"event-{n}-date", date,
                 card_x + 10, card_y + 8, chip_w, chip_h,
                 font_size_px=8, color=WHITE, bold=True, align="center", anchor="middle", uppercase=True)
        # Headline
        add_text(slide, f"event-{n}-title", head,
                 card_x + 10, card_y + 28, card_w - 20, 38,
                 font_size_px=11, color=TEXT_DARK, bold=True)
        # Source
        add_text(slide, f"event-{n}-desc", src,
                 card_x + 10, card_y + card_h - 16, card_w - 20, 14,
                 font_size_px=9, color=TEXT_FAINT)

    add_footer(slide, page_num=170)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "170_news-timeline.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
