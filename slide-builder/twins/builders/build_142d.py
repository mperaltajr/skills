"""
Builder for pattern 142d: Win themes (proposal) — 2x2 card grid (dark).

Source HTML: _pattern-library/142_win-themes-proposal-dark.html
Dark variant of build_142.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
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

    # Canonical chrome
    add_text(slide, "title",
             "<strong>Four win themes</strong> tied to evaluation criteria — each substantiated by verifiable proof points",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Mapped to RFP evaluation criteria · Substantiated with verifiable client outcomes",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # 2x2 card grid: top:220 left:48 right:48 bottom:60; gap:16
    grid_x = 48
    grid_y = 220
    grid_w = 1280 - 96
    grid_h = 720 - 60 - 60 - grid_y  # leave room for footer + breathing
    # Actually constrain to invariant zone (672): grid_h = 672 - 220 - some_gap
    grid_h = 672 - grid_y - 8
    gap = 14
    card_w = (grid_w - gap) // 2
    card_h = (grid_h - gap) // 2

    cards = [
        ("Deep Industry Expertise", "20+ years in financial services transformation",
         ["Sector-specific accelerators pre-built for FS operating models",
          "Regulatory knowledge embedded across all workstreams",
          "Active reference client network in this segment"],
         "Delivered 3 of the last 5 comparable programs in this sector"),
        ("Proven AI-at-Scale", "From POC to production in < 90 days",
         ["Pre-built ML pipelines reduce integration time by design",
          "Dedicated MLOps practice with continuous monitoring",
          "200+ models currently in production across clients"],
         "47% faster deployment than industry average"),
        ("People-First Change", "Change management is core, not a workstream",
         ["PROSCI-certified practitioners on every engagement",
          "Embedded OCM from day one alongside technical delivery",
          "95% end-user adoption rates measured at 90-day mark"],
         "0 rollbacks in last 12 implementations"),
        ("Commercial Flexibility", "Risk-sharing model aligned to your outcomes",
         ["Outcome-based fees tied to agreed success metrics",
          "Phased payment structure matching delivery milestones",
          "Gain-share provisions when targets are exceeded"],
         "Average client saves 18% vs. fixed-fee model"),
    ]

    for i, (heading, eyebrow, bullets, footer_text) in enumerate(cards):
        n = i + 1
        col = i % 2
        row = i // 2
        cx = grid_x + col * (card_w + gap)
        cy = grid_y + row * (card_h + gap)

        # Card background + top accent
        card = add_rect(slide, f"card-{n}-bg", cx, cy, card_w, card_h, CARD_BG_DARK)
        card.line.color.rgb = CARD_BORDER_DARK
        card.line.width = 9525
        add_rect(slide, f"card-{n}-accent", cx, cy, card_w, 4, BRAND_ACCENT)

        # Heading
        add_text(slide, f"card-{n}-heading", heading,
                 x_px=cx + 18, y_px=cy + 14, w_px=card_w - 36, h_px=22,
                 font_size_px=15, color=BRAND_ACCENT_SOFT, bold=True)
        # Eyebrow/tagline
        add_text(slide, f"card-{n}-eyebrow", eyebrow,
                 x_px=cx + 18, y_px=cy + 36, w_px=card_w - 36, h_px=18,
                 font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)

        # Body
        body_text = "\n".join("• " + b for b in bullets)
        add_text(slide, f"card-{n}-body", body_text,
                 x_px=cx + 18, y_px=cy + 58, w_px=card_w - 36, h_px=card_h - 110,
                 font_size_px=11, color=WHITE)

        # Proof footer (callout with left accent)
        add_rect(slide, f"card-{n}-footer-accent", cx + 18, cy + card_h - 38, 3, 28, BRAND_ACCENT)
        add_text(slide, f"card-{n}-footer", footer_text,
                 x_px=cx + 30, y_px=cy + card_h - 38, w_px=card_w - 50, h_px=28,
                 font_size_px=11, color=WHITE, italic=True, anchor="middle")

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "142",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "142d_win-themes-proposal.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
