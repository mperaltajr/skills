"""
Builder for pattern 274: SOAR Framework (2×2 quadrant).

Source HTML: _pattern-library/274_soar-framework.html

Four quadrants: Strengths, Opportunities, Aspirations, Results.
Each has a colored header band with letter+name+prompt, bulleted body, and
key-outcome strip at bottom.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

RESULTS_GREEN = RGBColor(0x1A, 0x6B, 0x3C)


def draw_quadrant(slide, q_id, x, y, w, h, letter, name, prompt, bullets, outcome, head_color):
    # Body card
    body = add_rect(slide, f"quadrant-{q_id}", x, y, w, h, CARD_BG)
    body.line.color.rgb = CARD_BORDER
    body.line.width = 9525

    # Header band
    head_h = 50
    add_rect(slide, f"quadrant-{q_id}-head", x, y, w, head_h, head_color)
    # Letter (big)
    add_text(
        slide, f"quadrant-{q_id}-letter", letter,
        x_px=x + 14, y_px=y + 6, w_px=24, h_px=14,
        font_size_px=10, color=WHITE, bold=True,
        uppercase=True, letter_spacing_px=2,
    )
    # Name (uppercase)
    add_text(
        slide, f"quadrant-{q_id}-name", name,
        x_px=x + 14, y_px=y + 20, w_px=w - 28, h_px=18,
        font_size_px=13, color=WHITE, bold=True,
        uppercase=True, letter_spacing_px=0.5,
    )
    # Prompt (italic)
    add_text(
        slide, f"quadrant-{q_id}-prompt", prompt,
        x_px=x + 14, y_px=y + 36, w_px=w - 28, h_px=12,
        font_size_px=10, color=RGBColor(0xFF, 0xFF, 0xFF), italic=True,
    )

    # Bullets
    bul_y = y + head_h + 10
    bul_step = 22
    for i, b in enumerate(bullets):
        # dot
        add_rect(slide, f"quadrant-{q_id}-bullet-{i+1}-dot",
                 x + 16, bul_y + i * bul_step + 7, 5, 5, head_color)
        add_text(
            slide, f"quadrant-{q_id}-bullet-{i+1}", b,
            x_px=x + 28, y_px=bul_y + i * bul_step, w_px=w - 40, h_px=20,
            font_size_px=12, color=TEXT_DARK,
        )

    # Outcome strip at bottom
    out_h = 44
    out_y = y + h - out_h
    out_bg = add_rect(slide, f"quadrant-{q_id}-outcome-bg", x, out_y, w, 1, CARD_BORDER)
    add_text(
        slide, f"quadrant-{q_id}-outcome", "Key outcome: " + outcome,
        x_px=x + 14, y_px=out_y + 1, w_px=w - 28, h_px=out_h - 4,
        font_size_px=11, color=head_color, bold=True, italic=True, anchor="middle",
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="SOAR Framework — <strong>forward-looking strategy on a single page.</strong>",
        subtitle="Strengths to build on · Opportunities to capture · Aspirations to aim for · Results to measure",
    )

    # Grid: 2x2 in zone y=240..640, x=56..1224 (1168 wide)
    grid_x = 56
    grid_y = 240
    grid_w = 1168
    grid_h = 400
    gap = 10
    cell_w = (grid_w - gap) // 2
    cell_h = (grid_h - gap) // 2

    # S — top-left
    draw_quadrant(
        slide, "tl", grid_x, grid_y, cell_w, cell_h,
        "S", "Strengths", "What do we do best?",
        [
            "Market-leading NPS score of 76",
            "3,200 specialist consultants",
            "94% client retention",
            "ISO-certified delivery model",
        ],
        "Leverage certified talent base and high retention to deepen client relationships.",
        BRAND_PRIMARY,
    )
    # O — top-right
    draw_quadrant(
        slide, "tr", grid_x + cell_w + gap, grid_y, cell_w, cell_h,
        "O", "Opportunities", "What are our best opportunities?",
        [
            "GenAI advisory practice: $2B market",
            "Uncontested mid-market segment",
            "ESG compliance wave",
            "Partner ecosystem expansion",
        ],
        "Capture GenAI advisory market leadership before incumbents mobilise at scale.",
        BRAND_ACCENT,
    )
    # A — bottom-left
    draw_quadrant(
        slide, "bl", grid_x, grid_y + cell_h + gap, cell_w, cell_h,
        "A", "Aspirations", "What do we aspire to be?",
        [
            "#1 transformation partner by 2028",
            "$5B revenue milestone",
            "Net zero operations by 2027",
            "50% diverse leadership",
        ],
        "Be recognised as the defining transformation partner of the late 2020s decade.",
        BRAND_PRIMARY_MID,
    )
    # R — bottom-right
    draw_quadrant(
        slide, "br", grid_x + cell_w + gap, grid_y + cell_h + gap, cell_w, cell_h,
        "R", "Results", "How will we know we've succeeded?",
        [
            "Revenue: $5B by FY28",
            "NPS: 80+",
            "Market share: 18%",
            "Employee engagement: top quartile",
        ],
        "Four hard metrics tracked quarterly confirm the strategy is landing as designed.",
        RESULTS_GREEN,
    )

    add_footer(slide, page_num=274)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "274_soar-framework.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
