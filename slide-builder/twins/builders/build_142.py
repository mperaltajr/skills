"""
Builder for pattern 142: Win themes (proposal) — 2x2 card grid.

Source HTML: _pattern-library/142_win-themes-proposal.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title (22px, single line; no subtitle in this variant)
    add_text(slide, "title",
             "<strong>Four win themes</strong> tied to evaluation criteria — each substantiated by verifiable proof points",
             x_px=48, y_px=66, w_px=960, h_px=48,
             font_size_px=22, color=TEXT_DARK, bold=True,
             emphasis_color=BRAND_PRIMARY)
    add_rect(slide, "brand-rule", 48, 124, 48, 3, BRAND_ACCENT)

    # 2x2 card grid: top:148 left:48 right:48 bottom:36; gap:16
    grid_x = 48
    grid_y = 148
    grid_w = 1280 - 96
    grid_h = 720 - 36 - 148
    gap = 16
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
        card = add_rect(slide, f"card-{n}-bg", cx, cy, card_w, card_h, WHITE)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        add_rect(slide, f"card-{n}-accent", cx, cy, card_w, 4, BRAND_ACCENT)

        # Heading
        add_text(slide, f"card-{n}-heading", heading,
                 x_px=cx + 18, y_px=cy + 14, w_px=card_w - 36, h_px=22,
                 font_size_px=15, color=BRAND_PRIMARY, bold=True)
        # Eyebrow/tagline
        add_text(slide, f"card-{n}-eyebrow", eyebrow,
                 x_px=cx + 18, y_px=cy + 36, w_px=card_w - 36, h_px=18,
                 font_size_px=12, color=TEXT_MID, italic=True)

        # Body (bulleted list rendered as single text block)
        body_text = "\n".join("• " + b for b in bullets)
        add_text(slide, f"card-{n}-body", body_text,
                 x_px=cx + 18, y_px=cy + 58, w_px=card_w - 36, h_px=card_h - 110,
                 font_size_px=11, color=TEXT_DARK)

        # Proof footer (callout with left accent)
        add_rect(slide, f"card-{n}-footer-accent", cx + 18, cy + card_h - 38, 3, 28, BRAND_ACCENT)
        add_text(slide, f"card-{n}-footer", footer_text,
                 x_px=cx + 30, y_px=cy + card_h - 38, w_px=card_w - 50, h_px=28,
                 font_size_px=11, color=TEXT_DARK, italic=True, anchor="middle")

    add_footer(slide, page_num=142)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "142_win-themes-proposal.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
