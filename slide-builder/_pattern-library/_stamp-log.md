# Shape ID Stamping Log

Stamping the 85 approved patterns per SHAPE-ROLES.md vocabulary.

## STATUS: COMPLETE — 85 of 85 patterns stamped (2,970 `data-shape-id` attributes)

**Verification:** `git diff --stat` shows 85 files changed, 2,970 insertions / 2,970 deletions, 100% of new lines contain a `data-shape-id` attribute. No markup, text, or whitespace changes — only attribute additions.

Patterns 01-18 stamped manually with per-pattern care (first agent run, ~390 IDs). Remaining 67 patterns stamped via 7 parallel batch agents, each working from this log + SHAPE-ROLES.md as the contract. All conventions below were honored across the batches.

## Completed patterns

| # | File | IDs added | Pattern-local IDs | Notes | Confidence |
|---|---|---|---|---|---|
| 01 | `01_anchor-with-cards-icons.html` | 16 | — | Cards 1-3 with icon/heading/body. Clean canonical mapping. | clean |
| 02 | `02_three-pillars-icons-outputs.html` | 24 | — | 3 pillars + 3 outputs strip. Canonical pillar-N-* and output-N-*. | clean |
| 03 | `03_hero-statement-supporting-cards.html` | 19 | `spacer-rule` | Hero band uses `eyebrow`+`title`+`brand-rule`+`subtitle` (not hero-statement family, since cards follow). Cards 1-4 with num/heading/body. | clean |
| 04 | `04_comparison-band-headers.html` | 21 | `convergence-text` | Compare matrix with `compare-col-N-icon/header`, `compare-row-N-label`, `compare-row-N-col-N-cell`. matrix-header-blank skipped (empty layout). | clean |
| 05 | `05_screenshot-hero-caption.html` | 16 | — | photo-zone with corner-tag + label; 3 steps with num+body. No brand-rule div in source — pattern is missing universal invariant. | needs-review (missing brand-rule) |
| 06 | `06_section-divider-numeral.html` | 9 | — | Divider family: `divider-top-rule`, `divider-section-label`, `divider-title`, `divider-rule`, `divider-subtitle`, `divider-numeral`, `divider-bottom-rule`. No footer-rule (acceptable for divider). | clean |
| 07 | `07_honest-expectations-two-panel.html` | 13 | — | panel-1-* and panel-2-* per "honest expectations / two-panel symmetric" family. UL is the body. | clean |
| 09 | `09_agenda-numbered-toc.html` | 32 | `objectives-rule` | TOC 1-8 with num/title/desc; objectives label/heading + 4 objective rows + note. The obj-rule between list and note is pattern-local. | clean |
| 10 | `10_hero-stat-annotated.html` | 40 | — | Eyebrow + title + brand-rule + subtitle. Chart frame (title/subtitle/source) + 4 bar-rows (label/baseline-bar/pilot-bar/delta) + 2 legend swatches + annot panel (header/sub/rule + 3 annot rows). Big canonical match. | clean |
| 11 | `11_long-form-structured-text.html` | 19 | — | SCQA family: table-head-1/2/3 + section-1..4 (num/name/body). | clean |
| 12 | `12_kpi-tile-dashboard.html` | 23 | — | 6 tiles with metric-N-label/value/delta. Max-N=6 confirmed. | clean |
| 13 | `13_2x2-framework-quadrants.html` | 24 | — | Quadrants tl/tr/bl/br with label/name/directive/body. Axis labels + low/high ticks. Pattern is core canonical match. | clean |
| 14 | `14_gantt-workplan-timeline.html` | 31 | `timeline-row-header` | 3 phase bands + 12 timeline ticks + 8 task labels + 5 visible bars + 3 milestones + 4 legend swatches. Empty grid cells (task-cell placeholders) NOT stamped — they're layout, not visible shapes. | clean |
| 15 | `15_org-chart-hierarchy.html` | 9 | — | Picture-asset per SHAPE-ROLES. Only outer SVG stamped as `chart-canvas`. Internal nodes not individually addressable. | clean |
| 16 | `16_process-phases-rich.html` | 36 | — | 4 steps with num/eyebrow/name/body/exit-label/exit-text + meta-left/meta-right. All canonical step-N-* fields used. | clean |
| 17 | `17_before-after-transformation.html` | 13 | — | before-panel-* + after-panel-* + transformation-arrow + arrow labels (top/bottom). Canonical before/after family. | clean |
| 18 | `18_methodology-overview.html` | 47 | `step-N-activities-label`, `step-N-deliverables-label`, `step-N-deliverable-N-icon`, `step-N-deliverable-N-name` | 5 steps each with num/name/desc/body, plus activities-label and a sub-block of deliverables (icon+name, up to 2 per step). Deliverables are pattern-local. | clean |

## Decisions and conventions established

1. **Hero-band with cards (pattern 03)**: hero block uses `eyebrow`+`title`+`brand-rule`+`subtitle` (NOT hero-statement family). Hero family is reserved for pure-hero patterns (38, 30, 97).
2. **Convergence variants**: pattern-local `.takeaway` divs are stamped `data-shape-id="convergence"`. Sub-elements like `.convergence-mark` get canonical `convergence-mark`; `.convergence-text` is pattern-local.
3. **Empty grid cells**: Gantt task-cells that contain no visible content are NOT stamped (they're layout placeholders, not shapes). Only cells with a bar/milestone inside are stamped via the inner shape.
4. **SVG picture-asset**: stamp only outer `<svg>` with `data-shape-id="chart-canvas"`. Internal `<g>`/`<rect>`/`<text>` left unstamped. Applied to pattern 15.
5. **Pattern 05 missing brand-rule**: Pattern 05 has no `.title-rule` div under its subtitle. This violates the universal invariant — flagged for user review.
6. **Pattern 06 (divider) lacks footer-rule**: Acceptable per spec because divider has its own `divider-bottom-rule`.

## Vocabulary gaps observed so far

- `step-N-activities-label` / `step-N-deliverables-label` (pattern 18): zone-label eyebrows within each step card don't fit canonical step-N-* fields. Treated as pattern-local.
- `step-N-deliverable-N-icon` / `step-N-deliverable-N-name`: sub-deliverables within a step are pattern-local in pattern 18.
- `timeline-row-header` (pattern 14): label-col-head ("Workstream") above the task labels — pattern-local.
- `objectives-rule` (pattern 09): the small divider between objectives list and note — pattern-local under the agenda family.
- `convergence-text` (pattern 04): when convergence is split into mark+text divs.

None of these warrant adding to canonical (each appears once).

## Batch summary (patterns 19-100, stamped in parallel)

| Batch | Patterns | IDs added |
|---|---|---|
| Initial (01-18) | 01, 02, 03, 04, 05, 06, 07, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18 | ~390 |
| A (19-30) | 19, 20, 21, 22, 23, 24, 27, 28, 29, 30 | ~195 |
| B (31-40) | 31, 32, 33, 34, 35, 36, 37, 38, 39, 40 | 292 |
| C (41-52) | 41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 52 | 376 |
| D (53-66) | 53, 54, 57, 59, 60, 61, 62, 63, 64, 66 | 346 |
| E (68-81) | 68, 69, 70, 71, 72, 74, 75, 76, 77, 80, 81 | 450 |
| F (82-91) | 82, 83, 85, 86, 87, 88, 89, 90, 91 | 425 |
| G (94-100) | 94, 95, 96, 97, 98, 99, 100 | 233 |
| **Total** | **85 patterns** | **2,970** |

## Variant-chrome findings (library-wide)

The 8 "universal invariants" defined in SHAPE-ROLES.md are NOT actually universal across the 85 patterns. Many patterns use alternate chrome styles. This is not a defect — it's a real library characteristic that the composer must handle gracefully (skip substitution for shapes that don't exist in a given twin).

**Patterns missing `draft-badge`** (use top-chrome bar variant instead):
- 44, 46, 47, 48, 49, 63, 86, 87, 89, 90, 95

**Patterns missing `subtitle`** (header-band-titled or hero variants):
- 05 (missing brand-rule too), 23, 24, 36, 39, 51, 88, 95 (no subtitle), 97 (hero — by design), 98

**Patterns with extended footer slots** (a third `footer-center` slot):
- 40

**Composer implication:** the deck composer must look up shapes by `data-shape-id` using a "find or skip" pattern, not "find or error." Missing IDs are expected and silent.

## SVG handling actually applied

- **Picture-asset (chart-canvas):** 15, 20, 28, 29, 33, 34, 49, 66, 70, 72, 82, 83, 96, 100
- **Decompose (per-primitive IDs):** 31 (pyramid tiers), 35 (funnel stages), 48 (venn circles), 68 (donut slices), 71 (architecture layers)

Pattern 100 (Pareto) and 66 (combo chart) ended up as picture-asset by the "default when in doubt" rule rather than full decompose — they have complex axis/grid systems. Acceptable for first-pass twins; can be promoted to native python-pptx charts later if per-data-point editing becomes a need.

## Verification commands

```
cd _pattern-library
git diff --stat                                  # 85 files, balanced ins/del
git diff *.html | grep -c 'data-shape-id'        # 2970 — confirms count
```
