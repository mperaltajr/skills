# Slide Lab Exemplar Library

This is the production exemplar library for Slide Lab deck builds. Each exemplar is a python-pptx slide that the user has hand-validated as a canonical example of its page-type. Per-slide agents reference these files when generating new slides so the output inherits the design discipline already encoded in the example.

## How agents use this

`scripts/build_deck.py` classifies each slide in the brief to a coarse `page-type` (the `classify_page_type()` heuristic). At prompt-render time, the script looks up the page-type in `PAGE_TYPE_TO_EXEMPLAR` and inlines 1-2 paths from `exemplars/do/<slug>/exemplar.py` into the agent prompt under the heading **"Reference exemplars (study these closely before writing)"**. The agent is expected to:

1. Read the exemplar's `exemplar.py` source.
2. Read the exemplar's `WHY.md` for the rationale.
3. Look at the rendered `exemplar.png` if vision is available.
4. Produce three structurally distinct options that honor the same disciplines (one accent moment, bold ≤ 5, body floor 14px, title bottom-anchored, etc.).

Exemplars are deliberately small (1-2 per slide) to avoid prompt bloat. Chart slides get BOTH chart exemplars because the two layouts are siblings — the agent benefits from seeing the bottom-band variant and the right-card variant together.

## `do/` — the approved set

| Page-type | One-line description | Path |
|---|---|---|
| `cover-fullbleed-dark` | Full-bleed BRAND_PRIMARY cover; typography is the visual; one accent rule | `exemplars/do/cover-fullbleed-dark/exemplar.py` |
| `dark-hero-foil` | Asymmetric cover: 35% dark left block + 65% white right panel with meta | `exemplars/do/dark-hero-foil/exemplar.py` |
| `anchor-with-cards` | Left BRAND_PRIMARY anchor panel + right column of numbered evidence rows | `exemplars/do/anchor-with-cards/exemplar.py` |
| `2panel-convergence` | Symmetric two-column comparison + BRAND_PRIMARY convergence band punchline | `exemplars/do/2panel-convergence/exemplar.py` |
| `3pillar-icon-circles` | Three parallel cards led by BRAND_PRIMARY circle icon containers with WHITE glyphs | `exemplars/do/3pillar-icon-circles/exemplar.py` |
| `single-finding` | Hero takeaway (36px bold) + 3 subordinate bullets + one BRAND_ACCENT rule | `exemplars/do/single-finding/exemplar.py` |
| `hero-kpi-tile` | 96px BRAND_PRIMARY hero number anchors the top; compact bar strip proves it | `exemplars/do/hero-kpi-tile/exemplar.py` |
| `recommendation-cta` | Top hero ASK band + 3 sub-ask cards with shared accent left-strip | `exemplars/do/recommendation-cta/exemplar.py` |
| `chart-bottom-takeaway` | Grouped multi-series bar chart + full-width BRAND_PRIMARY takeaway band below | `exemplars/do/chart-bottom-takeaway/exemplar.py` |
| `chart-right-takeaway` | Same chart, right-hand takeaway card variant; sibling-box 2-column layout | `exemplars/do/chart-right-takeaway/exemplar.py` |

Each folder contains exactly three files:
- `exemplar.py` — the python-pptx source the agent should study
- `exemplar.png` — the rendered output (themed against the client template where applicable)
- `WHY.md` — 100-200 word rationale: what makes the exemplar strong, when to reach for it, specific patterns to copy

## `dont/` — anti-exemplars

Anti-exemplars are curated separately — see `exemplars/dont/`. Each will pair a failed slide with a sharp note on the specific rule it violated (lorem in production, two accent moments, eyebrow bold, raw hex literals, etc.). Mario is curating these in parallel; the `dont/` directory is not populated by this commit.

## Adding a new exemplar

1. Hand-build the slide (or harvest from a validated session run).
2. Create `exemplars/do/<page-type-slug>/`.
3. Copy `exemplar.py` and `exemplar.png` into the folder.
4. Write `WHY.md` following the existing template (what / strong moves / when / patterns).
5. Add the page-type to `PAGE_TYPE_TO_EXEMPLAR` in `scripts/build_deck.py` so agents start receiving the reference.
