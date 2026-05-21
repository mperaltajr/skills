"""
Dark variant of pattern 35: Funnel conversion.

Source HTML: _pattern-library/35_funnel-conversion-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

# Funnel tier fills inverted for dark mode (lightest at top, darkest at bottom would clash).
# Use a graduated lighter-to-mid-brand stack so each stage stays legible against the dark bg.
FUNNEL_FILLS = [
    RGBColor(0xC7, 0x80, 0xFF),  # tier 1 (focal) — brand-accent-soft
    RGBColor(0xA8, 0x7C, 0xD4),
    RGBColor(0x8B, 0x5F, 0xB8),
    RGBColor(0x6F, 0x44, 0x95),
    RGBColor(0x55, 0x36, 0x77),
]


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Where decks die — 1,000 initiated, 28 reach the client clean.",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Annual deck-quality funnel across the practice. The leak isn't the pitch — it's the early structure.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    funnel_left = 124
    funnel_center = funnel_left + 300
    tier_h = 60
    tier_gap = 6
    tier_top = 200
    tier_widths = [600, 470, 340, 230, 210]

    callout_left = funnel_left + 700
    callout_w = 340

    names = ["AWARENESS", "DRAFTS", "REVIEWED", "PARTNER-READY", "CLIENT-READY"]
    counts = ["1,000", "600", "270", "80", "28"]
    tags = [
        "BIGGEST LEAK · SLIDE LAB PLAYS HERE",
        "STAGE 2 · STRUCTURE FAILS",
        "STAGE 3 · REVIEW SLOG",
        "STAGE 4 · FINAL POLISH",
        "STAGE 5 · OUTCOME",
    ]
    bodies = [
        "Decks created in the practice over a year.",
        "Got past the workstream-findings dump into a storyline.",
        "Made it to partner review without being fully mangled.",
        "Partner signed off without major rework.",
        "Survived the final review. Sent to client clean.",
    ]
    drops = [
        "60% lost to blank-page paralysis & workstream dumps.",
        "55% lost — story doesn't hold under partner review.",
        "70% lost — heavy edits, redo cycles.",
        "65% lost — late-stage edits before client send.",
        "Just 2.8% end-to-end — 28 of 1,000.",
    ]

    for i in range(5):
        n = i + 1
        y = tier_top + i * (tier_h + tier_gap)
        w = tier_widths[i]
        x = funnel_center - w // 2
        fill = FUNNEL_FILLS[i]

        stage = add_rect(slide, f"funnel-stage-{n}-shape", x, y, w, tier_h, fill)
        if i == 0:
            stage.line.color.rgb = BRAND_ACCENT_SOFT
            stage.line.width = 31750

        # Text color: dark on light tiers, white on darker tiers
        text_color = BRAND_PRIMARY if i <= 1 else WHITE
        add_text(
            slide, f"funnel-stage-{n}-name", names[i],
            x_px=x + 12, y_px=y + 12, w_px=w - 24, h_px=18,
            font_size_px=11, color=text_color, bold=True, align="center",
            letter_spacing_px=1.8, uppercase=True,
        )
        add_text(
            slide, f"funnel-stage-{n}-count", counts[i],
            x_px=x + 12, y_px=y + 28, w_px=w - 24, h_px=28,
            font_size_px=22, color=text_color, bold=True, align="center",
        )

        cy = y
        ch = tier_h
        if i == 0:
            cobj = add_rect(slide, f"funnel-stage-{n}-callout-bg",
                            callout_left, cy, callout_w, ch, CARD_BG_DARK)
            add_rect(slide, f"funnel-stage-{n}-callout-border",
                     callout_left, cy, 3, ch, BRAND_ACCENT_SOFT)

        add_text(
            slide, f"funnel-stage-{n}-tag", tags[i],
            x_px=callout_left + 14, y_px=cy + 4, w_px=callout_w - 20, h_px=12,
            font_size_px=8, color=BRAND_ACCENT_SOFT if i == 0 else TEXT_ON_DARK_FAINT,
            bold=True, letter_spacing_px=1.5, uppercase=True,
        )
        add_text(
            slide, f"funnel-stage-{n}-body", bodies[i],
            x_px=callout_left + 14, y_px=cy + 18, w_px=callout_w - 20, h_px=18,
            font_size_px=11, color=WHITE,
        )
        add_text(
            slide, f"funnel-stage-{n}-drop", drops[i],
            x_px=callout_left + 14, y_px=cy + 38, w_px=callout_w - 20, h_px=18,
            font_size_px=10, color=TEXT_ON_DARK_MID,
            italic=(i != 0),
        )

    add_convergence(
        slide,
        "From 1,000 decks initiated to 28 client-ready — the leak isn't the pitch, it's the early structure.",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(
        slide, "source", "Source: [add source here or delete]",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
    )
    add_text(
        slide, "page-number", "35",
        x_px=1170, y_px=688, w_px=52, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right",
    )
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "35d_funnel-conversion.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
