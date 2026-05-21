"""
Builder for pattern 35: Funnel conversion.

Decompose treatment (per SHAPE-ROLES table): 5 stacked trapezoid stages as
native shapes, plus right-side callouts.

Pattern-local IDs: funnel-stage-N-shape, funnel-stage-N-name, funnel-stage-N-count,
funnel-stage-N-tag, funnel-stage-N-body, funnel-stage-N-drop.

Source HTML: _pattern-library/35_funnel-conversion.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

# Funnel tier fills (top lightest → bottom darkest)
FUNNEL_FILLS = [
    RGBColor(0xE5, 0xD5, 0xF0),
    RGBColor(0xC3, 0x9B, 0xDB),
    RGBColor(0x8B, 0x5F, 0xB8),
    RGBColor(0x5C, 0x2D, 0x87),
    RGBColor(0x2D, 0x0A, 0x4E),
]


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Where decks die — 1,000 initiated, 28 reach the client clean.",
        subtitle="Annual deck-quality funnel across the practice. The leak isn't the pitch — it's the early structure.",
        title_h=64,
        subtitle_h=22,
    )

    # Funnel area at left, callouts at right
    # Funnel widths (px): 720 / 560 / 410 / 280 / 180; we'll scale to fit
    # Stage area: left=124 (64 + 60 offset), funnel max width 600
    funnel_left = 124
    funnel_center = funnel_left + 300
    tier_h = 60
    tier_gap = 6
    tier_top = 200
    # Bottom tier widened from 150→210 so the "CLIENT-READY" / "28" labels
    # sit inside the shape with comfortable padding.
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

        # Stage shape (rectangle approximation of trapezoid; the actual SVG
        # uses polygons but here we keep it simple).
        stage = add_rect(slide, f"funnel-stage-{n}-shape", x, y, w, tier_h, fill)
        if i == 0:
            # Focal stage gets accent ring
            stage.line.color.rgb = BRAND_ACCENT
            stage.line.width = 31750  # ~2.5pt

        # Stage name + count (centered, color depends on tier brightness)
        text_color = WHITE if i >= 2 else BRAND_PRIMARY
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

        # Callout (right side)
        cy = y
        ch = tier_h
        # Focal callout (stage 1) gets background + accent border
        if i == 0:
            cobj = add_rect(slide, f"funnel-stage-{n}-callout-bg",
                            callout_left, cy, callout_w, ch, CARD_BG)
            add_rect(slide, f"funnel-stage-{n}-callout-border",
                     callout_left, cy, 3, ch, BRAND_ACCENT)

        add_text(
            slide, f"funnel-stage-{n}-tag", tags[i],
            x_px=callout_left + 14, y_px=cy + 4, w_px=callout_w - 20, h_px=12,
            font_size_px=8, color=BRAND_ACCENT if i == 0 else TEXT_FAINT,
            bold=True, letter_spacing_px=1.5, uppercase=True,
        )
        add_text(
            slide, f"funnel-stage-{n}-body", bodies[i],
            x_px=callout_left + 14, y_px=cy + 18, w_px=callout_w - 20, h_px=18,
            font_size_px=11, color=BRAND_PRIMARY if i == 0 else TEXT_DARK,
        )
        add_text(
            slide, f"funnel-stage-{n}-drop", drops[i],
            x_px=callout_left + 14, y_px=cy + 38, w_px=callout_w - 20, h_px=18,
            font_size_px=10, color=BRAND_PRIMARY_MID if i == 0 else TEXT_FAINT,
            italic=(i != 0),
        )

    add_convergence(
        slide,
        "From 1,000 decks initiated to 28 client-ready — the leak isn't the pitch, it's the early structure.",
    )

    add_footer(slide, page_num=35)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "35_funnel-conversion.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
