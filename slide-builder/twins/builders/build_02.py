"""
Builder for pattern 02: Three pillars with icons + outputs strip.

Source HTML: _pattern-library/02_three-pillars-icons-outputs.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_FAINT, WHITE,
)

PILLAR_GLYPHS = ["◇", "⊕", "⊞"]  # Think / Argue / Build


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Pattern 02 uses 28px title; standard title block handles it.
    add_title_block(
        slide,
        title="Three skill domains — connected, not stacked.",
        subtitle="Strategy work requires all three. Weakness in one cascades to the others — and the deck pays the price.",
        title_h=68,
        subtitle_h=20,
        brand_rule_w=56,
    )

    # Body region: left:56, right:56. 3 pillars in equal columns w/ 22px gap.
    # pillar header 52h (brand-primary), pillar body height=260
    # Then 22px gap, then outputs strip ~64h
    grid_left = 56
    pillar_w = (1280 - 112 - 44) // 3  # = 372
    gap = 22
    pillar_header_h = 52
    pillar_body_h = 200  # tightened for vertical fit
    pillar_top = 232

    pillar_data = [
        ("Think",
         "Frame the problem before reaching for the slide\nGovern the argument with a single thought\nApply MECE structure — not just bullet points\nTest the so what before drafting\nIdentify decisions vs context"),
        ("Argue",
         "Build the logic chain before the visuals\nPressure-test claims against counterexamples\nSharpen the headline until it stands alone\nAnticipate the senior partner's first question\nDistinguish evidence from assertion"),
        ("Build",
         "Match the right page type to the argument\nKeep the action title doing the work\nUse chart only when chart adds signal\nRespect the invariant footer zone\nRender in PowerPoint, not Word"),
    ]

    for i, (name, body) in enumerate(pillar_data):
        n = i + 1
        cx = grid_left + i * (pillar_w + gap)

        # Header (brand-primary fill)
        add_rect(slide, f"pillar-{n}-header", cx, pillar_top, pillar_w, pillar_header_h, BRAND_PRIMARY)
        # Icon glyph in header
        add_icon(slide, f"pillar-{n}-icon", cx + 20, pillar_top + 8, 32,
                 PILLAR_GLYPHS[i], color=WHITE)
        # Pillar name (white, 18px bold)
        add_text(
            slide, f"pillar-{n}-name", name,
            x_px=cx + 60, y_px=pillar_top + 14, w_px=pillar_w - 80, h_px=28,
            font_size_px=18, color=WHITE, bold=True,
        )

        # Body (card-bg, bordered)
        body_y = pillar_top + pillar_header_h
        body_rect = add_rect(slide, f"pillar-{n}-body-bg", cx, body_y, pillar_w, pillar_body_h, CARD_BG)
        body_rect.line.color.rgb = CARD_BORDER
        body_rect.line.width = 9525

        # Body text
        add_text(
            slide, f"pillar-{n}-body", body,
            x_px=cx + 20, y_px=body_y + 16, w_px=pillar_w - 36, h_px=pillar_body_h - 24,
            font_size_px=12, color=TEXT_DARK,
        )

    # Outputs strip: same 3-column grid, below pillars
    strip_top = pillar_top + pillar_header_h + pillar_body_h + 22
    strip_h = 60

    outputs = [
        "A governing thought + structured argument",
        "A defensible logic chain, claim by claim",
        "A real PPTX, not a wall of text in a box",
    ]
    for i, txt in enumerate(outputs):
        n = i + 1
        cx = grid_left + i * (pillar_w + gap)
        # Background cell
        cell = add_rect(slide, f"output-{n}-bg", cx, strip_top, pillar_w, strip_h, WHITE)
        cell.line.color.rgb = CARD_BORDER
        cell.line.width = 9525
        # 2px brand-accent top
        add_rect(slide, f"output-{n}-accent", cx, strip_top, pillar_w, 2, BRAND_ACCENT)
        # Label
        add_text(
            slide, f"output-{n}-label", "PRODUCES",
            x_px=cx + 18, y_px=strip_top + 10, w_px=pillar_w - 36, h_px=14,
            font_size_px=10, color=TEXT_FAINT, bold=True, uppercase=True,
        )
        # Text
        add_text(
            slide, f"output-{n}-text", txt,
            x_px=cx + 18, y_px=strip_top + 26, w_px=pillar_w - 36, h_px=28,
            font_size_px=12, color=BRAND_PRIMARY, bold=True,
        )

    add_footer(slide, page_num=5)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "02_three-pillars-icons-outputs.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
