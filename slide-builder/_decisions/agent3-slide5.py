"""Agent 3 -- Slide 5 (simpler-arch test).

Layout: Hero / hero-statement / light canvas.
Brief: "Narrative is the spec -- no brief, no build."
- Hero phrase carries the slide.
- Three supporting artefacts: governing thought, editorial emphasis, evidence.
"""
from pathlib import Path
import sys
sys.path.insert(0, r"C:\Users\m.a.peralta\.claude\skills\slide-builder")
from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT, CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()

    # Standard title block (action title) -- the brief headline.
    add_title_block(
        slide,
        title="Narrative is the spec -- <strong>no brief, no build</strong>",
        subtitle="The consultant focuses on the argument; the tool handles the layout.",
    )

    # Hero phrase -- single load-bearing statement, centered, ~110px tall band.
    # y starts at 220 (clear of title/subtitle), full width minus margins.
    hero_y = 220
    add_text(
        slide, "hero-phrase", "“Narrative is the spec.”",
        x_px=64, y_px=hero_y, w_px=1280 - 128, h_px=130,
        font_size_pt=54, color=BRAND_PRIMARY, bold=True,
        anchor="middle", align="center",
    )

    # Single-accent moment: thin horizontal rule under the hero phrase.
    add_rect(
        slide, "accent-rule",
        x_px=(1280 // 2) - 40, y_px=hero_y + 140, w_px=80, h_px=4,
        fill_color=BRAND_ACCENT,
    )

    # Three supporting artefacts -- equal columns, label + body.
    # Body region: y=400-590, three columns inside body margin.
    artefacts = [
        ("Governing thought",
         "One-sentence answer to so-what: what does this slide prove?"),
        ("Editorial emphasis",
         "The visual move that makes the claim land -- hero stat, compare, flow."),
        ("Evidence",
         "The data or claim that proves the thought -- traceable, not invented."),
    ]
    body_x = 64
    body_w = 1280 - 128
    gutter = 24
    col_w = (body_w - 2 * gutter) // 3
    col_y = 410

    for i, (label, body) in enumerate(artefacts):
        x = body_x + i * (col_w + gutter)
        # Top hairline rule per column for editorial structure
        add_rect(
            slide, f"art-rule-{i+1}",
            x_px=x, y_px=col_y - 12, w_px=col_w, h_px=1,
            fill_color=CARD_BORDER,
        )
        # Label
        add_text(
            slide, f"art-label-{i+1}", label,
            x_px=x, y_px=col_y, w_px=col_w, h_px=28,
            font_size_px=16, color=BRAND_PRIMARY, bold=True,
        )
        # Body
        add_text(
            slide, f"art-body-{i+1}", body,
            x_px=x, y_px=col_y + 36, w_px=col_w, h_px=140,
            font_size_px=14, color=TEXT_MID, anchor="top",
        )

    # Footer
    add_footer(slide, page_num=5)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "agent3-slide5.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
