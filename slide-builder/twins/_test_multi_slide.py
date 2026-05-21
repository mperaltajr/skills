"""
Smoke test for multi-slide deck composition.

Builds a 4-slide deck pulling from 4 different patterns to verify:
- The slide-clone XML copy works
- Each slide gets its own substitutions applied
- The output is a valid PPTX that opens cleanly
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from twins.composer import compose_deck


def main():
    out = Path(__file__).resolve().parent.parent / "_renders" / "twins" / "_test_multi_slide_deck.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)

    compose_deck(
        out_path=str(out),
        slides=[
            # Slide 1: cover
            {
                "pattern": "19_cover-split-panel",
                "overrides": {
                    "cover-deck-title": "Pilot Recap",
                    "cover-tagline": "Four weeks, six metrics.",
                    "cover-pre-label": "INTERNAL · 2026 Q2",
                    "cover-presented-name": "Mario Peralta · Strategy Manager",
                    "cover-meta-1-value": "Pilot Team",
                    "cover-meta-2-value": "May 19, 2026",
                    "cover-meta-3-value": "20 minutes",
                },
            },
            # Slide 2: hero statement
            {
                "pattern": "38_statement-hero-text",
                "overrides": {
                    "eyebrow": "The single takeaway",
                    "hero-statement": "Four weeks in, every metric is moving in the right direction.",
                    "hero-attribution": "Mario Peralta · After 12 pilot decks · May 2026",
                    "hero-context": "We have enough signal to commit to Q3 rollout.",
                },
            },
            # Slide 3: KPI tiles
            {
                "pattern": "12_kpi-tile-dashboard",
                "overrides": {
                    "title": "Six metrics, all moving the right way.",
                    "subtitle": "Pilot scorecard, weeks 1-4 against Q1 baseline.",
                    "metric-1-label": "Cycle time",
                    "metric-1-value": "-62%",
                    "metric-1-delta": "▼ 14d → 5d",
                    "metric-2-label": "Partner edits",
                    "metric-2-value": "1.4×",
                    "metric-2-delta": "▼ 3.2 → 1.4 rounds",
                    "metric-3-label": "Sign-off",
                    "metric-3-value": "94%",
                    "metric-3-delta": "▲ 60% → 94%",
                    "metric-4-label": "Deck length",
                    "metric-4-value": "11",
                    "metric-4-delta": "▼ 19 → 11 slides",
                    "metric-5-label": "Gate pass rate",
                    "metric-5-value": "8/10",
                    "metric-5-delta": "▲ 4/10 → 8/10",
                    "metric-6-label": "Build errors",
                    "metric-6-value": "0",
                    "metric-6-delta": "● 4 clean weeks",
                    "convergence": "Two more weeks of pilot, then commit to Q3 rollout.",
                },
            },
            # Slide 4: cards (closing)
            {
                "pattern": "01_anchor-with-cards-icons",
                "overrides": {
                    "title": "Three reasons we're recommending Q3 rollout.",
                    "subtitle": "Each one is structurally repeatable across the next four pilots.",
                    "card-1-heading": "Cycle time",
                    "card-1-body": "62% reduction holds across two distinct workstreams. Not a one-off.",
                    "card-2-heading": "Edit rounds",
                    "card-2-body": "Partner-edit rounds dropped 56% — every decade dropped is one less stakeholder meeting.",
                    "card-3-heading": "Gate pass rate",
                    "card-3-body": "8/10 storylines pass first-time. Twice the baseline. Faster handoffs, fewer rebuilds.",
                    "convergence": "Greenlight Q3 rollout. Decision needed by Friday.",
                    "footer-right": "Slide Lab · 2026 · 4",
                },
            },
        ],
    )
    print(f"Built 4-slide deck: {out}")


if __name__ == "__main__":
    main()
