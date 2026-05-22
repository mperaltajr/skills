"""
ANTI-EXEMPLAR — six-panel-no-hierarchy

Family: Insight / Finding (attempted) — really a Value-Case Summary slide
Variant: 3-column top half + 3-column bottom half = 6 dense panels on a single
         slide. Every supporting text element collapses to ~10pt to fit.

This is the "everything is 10pt" failure. The author had six things to say
(benchmarks, value levers, business impact, current challenges, key assumptions,
support required) and forced all of them onto ONE slide. To make it fit, every
piece of supporting text — labels, axis captions, body copy, bullet content,
benchmark values, footnotes — shrinks to the same uniform ~10pt size.

The slide title is 28pt. Below the title there is NO visual hierarchy: bullets,
section headings, body copy, axis labels, and footnotes all share the same
~10pt size. The reader has no anchor for "what is the headline number on this
panel" vs. "what is supporting detail." Everything has equal weight, so nothing
has weight.

Other failures that ride along with the six-panel cram:
- Six panel headers ("Current State Benchmarks", "Value Levers", "Business
  Impact", "Current Challenges", "Key Assumptions", "Fedex Support Required")
  compete with the title for first-fixation.
- Body bullets in the bottom row are 10pt, the same size as the panel headers
  and the same size as the value-lever subheaders. The eye has nowhere to land.
- The two big "$X.XM/yr" callouts in the Business Impact panel ARE sized up to
  ~22pt — but they're surrounded by so much 10pt noise that they read as just
  another label.

Rule violated (designer-brief / rules.md): body-font floor (14px / ~10.5pt
PPTX) is the absolute minimum for any readable body text on a 1280x720 slide
projected at meeting-room scale. This deck uses 10pt as the DEFAULT size for
every non-title, non-jumbo-callout element. There is no hierarchy because
there is no size variation.

Rule violated: one slide, one idea. Six independent content blocks on one
slide is a section, not a slide.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()

    # Title — sized correctly. Everything BELOW is the failure.
    add_title_block(
        slide,
        title="[Lever headline: the one-line claim with the number — $X.XM/yr]",
        subtitle="[Sub-headline: what was measured, scope, and time period]",
    )

    # Eyebrow + top-right run-rate badge (mimics source slide)
    add_text(
        slide, "eyebrow",
        "[CATEGORY] · [LEVER N]",
        x_px=64, y_px=4, w_px=300, h_px=14,
        font_size_pt=8, color=TEXT_FAINT, uppercase=True,
    )
    add_text(
        slide, "badge-label",
        "[METRIC LABEL]",
        x_px=1080, y_px=20, w_px=160, h_px=14,
        font_size_pt=8, color=TEXT_FAINT, align="right", uppercase=True,
    )
    add_text(
        slide, "badge-value",
        "[$X.XM · $XXM]",
        x_px=1080, y_px=36, w_px=160, h_px=22,
        font_size_pt=11, color=TEXT_DARK, align="right", bold=True,
    )

    # ── Top half: 3 columns of cards ──
    # Each column: 392px wide. Gutter 16px. Starts at x=64.
    col_w = 392
    col_h = 320
    top_y = 110
    col_xs = [64, 64 + col_w + 16, 64 + 2 * (col_w + 16)]

    # Panel headers + bodies for top half
    top_panels = [
        ("Current State Benchmarks",
         "Cost per Invoice (loaded)        APQC D&T Jan 2026\n"
         "[Org]            ~$X.XX\n"
         "Median           $X.XX\n"
         "[$X.XX gap × X.XM touchable invoices = $X.XM cost reduction]\n"
         "\n"
         "[Metric Two]                     APQC n=XX · ↑ better\n"
         "[Org]            XX%\n"
         "Best-in-class   100%\n"
         "[Supporting note about the gap and what it implies]\n"
         "\n"
         "[Metric Three]                   APQC n=XX · ↑ better\n"
         "[Org]            est. low\n"
         "Median           XX%\n"
         "[Supporting note about manual exception rework]"),
        ("Value Levers — by Process",
         "[Workstream A]                   XX% target · XX% wt.\n"
         "AI-assisted processing, duplicate detection, and straight-through.\n"
         "Largest lever by weight.\n"
         "\n"
         "[Workstream B]                   XX% target · XX% wt.\n"
         "GenAI [function] on [platform]; self-service portal reduces volume.\n"
         "\n"
         "[Workstream C]                   XX% target · XX% wt.\n"
         "Automated detection and run processing; advanced matching in high case.\n"
         "\n"
         "[Workstream D]                   XX% target · XX% wt.\n"
         "Master data automation; optimizes [control] audit step.\n"
         "\n"
         "[Workstream E]                   XX% target · XX% wt.\n"
         "GenAI verification (~XX% accuracy) and real-time policy engine."),
        ("Business Impact",
         "",  # body for impact handled separately so we can size the headline up
        ),
    ]

    for i, (header, body) in enumerate(top_panels):
        x = col_xs[i]
        # Panel header strip
        add_rect(
            slide, f"top-{i}-header-bg",
            x_px=x, y_px=top_y, w_px=col_w, h_px=22,
            fill_color=CARD_BG,
        )
        add_text(
            slide, f"top-{i}-header", header,
            x_px=x + 8, y_px=top_y + 4, w_px=col_w - 16, h_px=18,
            font_size_pt=8, color=TEXT_DARK, bold=True, uppercase=True,
        )
        # Panel body box (border only via fill swatch behind)
        add_rect(
            slide, f"top-{i}-body-bg",
            x_px=x, y_px=top_y + 22, w_px=col_w, h_px=col_h - 22,
            fill_color=WHITE,
        )
        # The failure: body text at 10pt (~13px) — every line same size.
        if body:
            add_text(
                slide, f"top-{i}-body", body,
                x_px=x + 8, y_px=top_y + 28, w_px=col_w - 16, h_px=col_h - 36,
                font_size_pt=7.5, color=TEXT_DARK,
            )

    # Business Impact column gets the jumbo callouts that the author DID size up
    # — but they're isolated by a sea of 10pt noise so they don't carry hierarchy.
    impact_x = col_xs[2]
    add_text(
        slide, "impact-big-1", "[$X.XM/yr]",
        x_px=impact_x + 16, y_px=top_y + 60, w_px=col_w - 32, h_px=36,
        font_size_pt=22, color=BRAND_PRIMARY, bold=True,
    )
    add_text(
        slide, "impact-big-1-label",
        "Steady-state annual P&L (FYXX+)",
        x_px=impact_x + 16, y_px=top_y + 98, w_px=col_w - 32, h_px=14,
        font_size_pt=7.5, color=TEXT_DARK,
    )
    add_text(
        slide, "impact-big-2", "[$XX.XM]",
        x_px=impact_x + 16, y_px=top_y + 180, w_px=col_w - 32, h_px=36,
        font_size_pt=22, color=BRAND_PRIMARY, bold=True,
    )
    add_text(
        slide, "impact-big-2-label",
        "5-year cumulative P&L (FYXX–FYXX)",
        x_px=impact_x + 16, y_px=top_y + 218, w_px=col_w - 32, h_px=14,
        font_size_pt=7.5, color=TEXT_DARK,
    )

    # ── Bottom half: 3 columns of bullet panels ──
    bot_y = top_y + col_h + 12
    bot_h = 198
    bottom_panels = [
        ("CURRENT CHALLENGES",
         "• [Challenge 1: scope and the gap to benchmark or target]\n"
         "• [Challenge 2: process or control weakness in current state]\n"
         "• [Challenge 3: tooling or coverage gap that drives leakage]\n"
         "• [Challenge 4: governance or accountability gap]"),
        ("KEY ASSUMPTIONS",
         "• [Assumption 1: addressable population and source]\n"
         "• [Assumption 2: unit economic — rate, cost, or success factor]\n"
         "• [Assumption 3: ramp schedule and steady-state year]\n"
         "• [Assumption 4: model parameter or benchmark anchor]"),
        ("[CLIENT] SUPPORT REQUIRED",
         "• [Data or system access required by kick-off]\n"
         "• [SME time commitment by workstream]\n"
         "• [Project owner and decision authority]\n"
         "• [Stakeholder alignment or contract dependency]"),
    ]

    for i, (header, body) in enumerate(bottom_panels):
        x = col_xs[i]
        add_rect(
            slide, f"bot-{i}-bg",
            x_px=x, y_px=bot_y, w_px=col_w, h_px=bot_h,
            fill_color=CARD_BG,
        )
        # Panel header — same 10pt as the body underneath. No hierarchy.
        add_text(
            slide, f"bot-{i}-header", header,
            x_px=x + 12, y_px=bot_y + 12, w_px=col_w - 24, h_px=14,
            font_size_pt=8, color=TEXT_DARK, bold=True,
        )
        # The failure: bullet body at the SAME size as the panel header above
        # and the SAME size as the benchmark labels in the top half. Uniform 10pt.
        add_text(
            slide, f"bot-{i}-body", body,
            x_px=x + 12, y_px=bot_y + 32, w_px=col_w - 24, h_px=bot_h - 44,
            font_size_pt=7.5, color=TEXT_DARK,
        )

    add_footer(slide, page_num=1, source="[Source citation if needed]")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
