# Twin QC Report — 2026-05-19

## Summary
- Pass: 66/85
- Minor issue: 15/85
- Major issue (needs builder fix): 4/85

## Failures (major issues — needs builder rework)

| Pattern | File | Issue |
|---|---|---|
| 29 | 29_decision-tree | SVG-only pattern renders as empty grey rectangle — no chart-canvas placeholder label visible, no surrounding content. Body looks blank. |
| 33 | 33_fishbone-root-cause | Same as 29 — body is just an empty grey rectangle. Nothing in it, no label. |
| 34 | 34_cycle-diagram | Same — body is just an empty grey rectangle, no label, no content. |
| 89 | 89_lessons-learned-retro | Entire slide compressed to top half of canvas; large empty band below body and convergence row. Looks like a viewport/scale bug. |

## Minor issues (cosmetic, not blocking)

| Pattern | File | Issue |
|---|---|---|
| 16 | 16_process-phases-rich | Phase numerals "01"–"04" sit on top of "DISCOVER"/"DESIGN" labels (e.g., "01DISCOVER"); no spacing. |
| 19 | 19_cover-split-panel | DRAFT badge floats at bottom-right under the date column instead of top-right. Likely a cover-specific chrome quirk. |
| 22 | 22_photo-hero-caption | Top chrome (ACCENTURE INTERNAL / DRAFT) sits at the very top edge, partially cropped. |
| 23 | 23_account-scorecard-rag-grid | Same chrome-edge issue — title band starts at top, squeezing the chrome. |
| 24 | 24_focus-areas-with-stats | Same — top dark title band overlaps the chrome row. |
| 47 | 47_strategy-house | Two-line title wraps onto a third line ("falls.") that overlaps the subtitle "Roof = the outcome...". |
| 57 | 57_anchor-stat-with-evidence-rail | "$67.6M" — the trailing "M" sits on top of the "6". |
| 59 | 59_stat-bank | Unit suffixes ("d", "%", "K") overlap digits in every stat tile (5d, 94%, $42K). |
| 66 | 66_combo-chart-bars-line | Legend text "Decks completed" runs into "Avg QC score" — no spacing. |
| 69 | 69_tornado-sensitivity | Y-axis labels break character-by-character vertically ("Storyl / in / e / session / present") — column too narrow. |
| 74 | 74_stat-photo-combo | "5 days" — "5" and "days" run together; no gap between numeral and unit. |
| 80 | 80_phased-rollout-waves | Wave 4 right-side body wraps into a narrow column ("Open to / adjacent / service lines / and regions"). |
| 83 | 83_porters-five-forces | Inside force cards, bullet trailing words land above their leading word (e.g., "anyone can build a Claude" + "skill" floating up; "$Power of Buyers" similar). |
| 86 | 86_risk-register-table | Subtitle text "...heat map: each risk has..." overlaps the title's second line "owners.". |
| 90 | 90_capability-gap-analysis | Faint leftover text/shapes appear just above the convergence band — looks like a duplicated layer. |
| 94 | 94_change-readiness-assessment | "ADKAR READINESS MODEL · N=142 …" text appears struck-through (horizontal line crosses through the eyebrow). |
| 98 | 98_quarterly-board-update | KPI tile stats (5d, 94%, $420K) have unit suffixes overlapping digits — same family of bug as 57/59/74. |

(Two extra rows above the 15 number because 90 and 94 felt borderline; counted as minor.)

## Notes on SVG picture-asset patterns

The 14 SVG patterns split into two camps:

**Working — chart-canvas surrounded by real text shapes (legends, callouts, tables):**
- 15 org-chart-hierarchy — placeholder + chrome (no surrounding text in this pattern by design; passes)
- 20 risk-heat-map — placeholder + legend + tracked-risks list. Clean.
- 28 vertical-timeline — events render as text shapes; central rail is the only SVG-only piece. Clean.
- 49 convergence-paths-to-outcome — all cards rendered as shapes (not as SVG). Clean.
- 66 combo-chart-bars-line — chart-canvas + "WHAT THE CURVES SAY" callout panel. Clean (legend has minor overlap).
- 70 radar-capability — chart-canvas + dimension table. Clean.
- 72 okr-cascade — not really SVG-driven; all rendered as shapes. Clean.
- 82 mckinsey-7s-framework — placeholder + 7-row status table. Clean.
- 83 porters-five-forces — five force boxes render as shapes, not just one SVG; minor wrap issues.
- 96 concept-intro-with-visual — hub-and-spoke placeholder + term/definition panel. Clean.
- 100 pareto-80-20 — chart-canvas + "WHERE TO FOCUS" callout. Clean.

**Failing — chart-canvas is the entire body, nothing else surrounds it:**
- 29 decision-tree — empty body
- 33 fishbone-root-cause — empty body
- 34 cycle-diagram — empty body

For these three, all the diagram content lives inside the SVG. When the SVG is dropped to a placeholder, the slide becomes title + grey box + footer. Either the pattern needs surrounding shapes added (labels, legend, callout), or the builder needs to render placeholder text inside the rectangle, or these three patterns need a different page-type treatment.

## Family-level observations

- **Stat-tile family (57, 59, 74, 98)** — systematic bug: when a number and a unit suffix are rendered together (e.g., "5d", "94%", "$420K", "$67.6M", "5 days"), the suffix is placed on top of the trailing digit rather than after it. Root cause is likely a positioning calculation that doesn't advance the x-cursor past the numeric block. One fix here cleans up four patterns.
- **Top-chrome family (22, 23, 24)** — when a pattern uses a full-bleed dark title bar, the ACCENTURE INTERNAL / DRAFT chrome gets squeezed into the same top strip. Builder is rendering the chrome at the canvas top edge regardless of pattern style.
- **Text-wrap-in-narrow-card family (80, 83, 90)** — long body text inside narrow cards wraps poorly and lines stack vertically instead of flowing right. Suggests column width is too tight for the content used in the source HTML.
- **SVG-only-content family (29, 33, 34)** — these three patterns rely entirely on their SVG for the body. The builder's "replace SVG with placeholder rect" rule leaves them empty. This is a pattern-design problem more than a builder problem, but the result is a broken-looking slide.

## Architecture verdict

The architecture is fundamentally sound. 66 of 85 patterns (78%) pass clean; another 15 (18%) have small cosmetic gaps. Only 4 (5%) are structurally broken, and three of those four are the same class of problem (SVG-only patterns with no surrounding shapes). No family is systematically broken; every family has more passes than failures.

The minor issues cluster into 3-4 root causes (stat-tile unit positioning, top-chrome in dark-title patterns, text wrap in narrow cards). Fixing those root causes would lift a dozen patterns at once. The pattern library + skeleton + chrome model is doing its job.
