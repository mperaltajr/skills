"""
DONT — reading-order-bottom-up: takeaway lives at the BOTTOM of the slide.

Family: Insight / Finding
Failure mode: the slide's hero takeaway / headline claim sits in the BOTTOM
strip of the body zone, while dense supporting evidence (a paragraph of
context plus a chart placeholder) occupies the TOP.

Readers scan top-to-bottom. They hit the evidence first, try to interpret
raw data without the framing claim, give up, and stop reading before they
ever reach the point. The slide buries its own argument.

This is structurally distinct from a clean "chart-with-bottom-takeaway-strip"
layout because here the bottom strip is the WHOLE POINT of the slide
(36px bold hero headline), not a one-line so-what restatement of a claim
already made at the top. The top has NO claim at all — only evidence.

Layout shape (the WRONG way):
- Top zone (y=152–260): dense paragraph of supporting detail (the evidence)
- Mid zone (y=270–500): chart placeholder (more evidence)
- Bottom zone (y=520–640): HERO TAKEAWAY in 36px bold — where it shouldn't be

The fix: invert. Put the hero takeaway at the TOP (y≈152–280) and let the
evidence flow BELOW it. Readers should hit the point first, evidence second.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="[Slide title: topic of the analysis]",
        subtitle="[Sub-headline: what was measured, over what period]",
    )

    # ── TOP zone (y=152–260): dense supporting paragraph ──
    # This is evidence text — context, methodology, caveats. The reader hits
    # this FIRST and has no idea what claim it's supporting.
    add_text(
        slide, "evidence-paragraph",
        ("[Supporting detail 1 — paragraph]: dense context explaining what "
         "was measured, the time window, the methodology, the data sources, "
         "and the assumptions behind the analysis. The reader is forced to "
         "absorb all of this without knowing what point it serves, because "
         "the takeaway claim is buried at the bottom of the slide."),
        x_px=64, y_px=156, w_px=1152, h_px=96,
        font_size_px=14, color=TEXT_DARK, bold=False,
    )

    # ── MID zone (y=270–500): chart placeholder ──
    # More evidence. Still no claim in sight.
    chart_x = 64
    chart_y = 272
    chart_w = 1152
    chart_h = 224

    # Chart frame (light card)
    add_rect(
        slide, "chart-frame",
        x_px=chart_x, y_px=chart_y, w_px=chart_w, h_px=chart_h,
        fill_color=CARD_BG,
    )
    # Chart label
    add_text(
        slide, "chart-label",
        "[CHART PLACEHOLDER — supporting evidence visualization]",
        x_px=chart_x, y_px=chart_y + 8, w_px=chart_w, h_px=16,
        font_size_px=11, color=TEXT_MID, uppercase=True, letter_spacing_px=1,
        align="center",
    )

    # Fake bars inside the chart frame — placeholder visualization.
    baseline_y = chart_y + chart_h - 36
    add_rect(
        slide, "chart-baseline",
        x_px=chart_x + 32, y_px=baseline_y,
        w_px=chart_w - 64, h_px=1,
        fill_color=CARD_BORDER,
    )
    bar_specs = [
        (0.40, BRAND_PRIMARY_MID),
        (0.55, BRAND_PRIMARY_MID),
        (0.70, BRAND_PRIMARY_MID),
        (0.85, BRAND_PRIMARY),
        (1.00, BRAND_PRIMARY),
    ]
    bar_zone_x = chart_x + 64
    bar_zone_w = chart_w - 128
    n_bars = len(bar_specs)
    gap = 24
    bar_w = (bar_zone_w - gap * (n_bars - 1)) // n_bars
    max_bar_h = chart_h - 100
    for i, (proportion, color) in enumerate(bar_specs):
        bh = int(max_bar_h * proportion)
        bx = bar_zone_x + i * (bar_w + gap)
        by = baseline_y - bh
        add_rect(slide, f"chart-bar-{i}", bx, by, bar_w, bh, color)
        add_text(
            slide, f"chart-bar-lbl-{i}",
            f"[P{i+1}]",
            x_px=bx, y_px=baseline_y + 6, w_px=bar_w, h_px=14,
            font_size_px=11, color=TEXT_MID, align="center",
        )

    # ── BOTTOM zone (y=520–640): HERO TAKEAWAY — wrong place ──
    # This is the load-bearing claim of the slide. It should be at the TOP.
    # Placing it at the bottom forces eye-jump and breaks reading order.
    hero_y = 520
    add_text(
        slide, "hero-takeaway",
        "[Hero takeaway: the load-bearing claim this slide is making]",
        x_px=64, y_px=hero_y, w_px=1152, h_px=80,
        font_size_pt=24, color=TEXT_DARK, bold=True,
        emphasis_color=BRAND_PRIMARY,
    )
    # Accent rule UNDER the bottom-hero — reinforcing that this is "the point",
    # but it arrives after the reader has already mentally checked out.
    add_rect(
        slide, "hero-accent-rule",
        x_px=64, y_px=hero_y + 88, w_px=56, h_px=4,
        fill_color=BRAND_ACCENT,
    )
    # A subordinate one-liner under the hero to make the inversion obvious:
    # what should have been the SETUP for the evidence is acting as a closer.
    add_text(
        slide, "hero-subline",
        "[Subordinate framing line — would normally introduce the evidence above]",
        x_px=64, y_px=hero_y + 100, w_px=1152, h_px=20,
        font_size_px=13, color=TEXT_MID, italic=True,
    )

    add_footer(slide, page_num=4)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
