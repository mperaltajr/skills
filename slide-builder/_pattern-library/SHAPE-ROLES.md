# Shape Role Vocabulary

Canonical `data-shape-id` values for the Slide Lab pattern library. Stamped into every approved HTML pattern. Mapped 1:1 with shape names in the corresponding PPTX twin.

This vocabulary was derived by reading the 85 approved patterns (01-100 minus the 7 rejects and 8 deferred tweaks). Names are role-based, not class-based: a "metric value" is `metric-N-value` regardless of whether the source class is `.kpi-value`, `.stat-number`, `.tile-stat`, `.tile-figure`, or `.k-value`.

## Universal invariants (every pattern)

| data-shape-id | Description | Typical content |
|---|---|---|
| `accenture-tag` | top-left chrome | "ACCENTURE INTERNAL" |
| `draft-badge` | top-center yellow pill | "DRAFT" |
| `title` | main action title | 28-32px bold, brand-primary punchword |
| `subtitle` | italic gray sub-headline | 14px italic |
| `brand-rule` | 3-4px tall, 56-80px wide accent rule below subtitle | (no text) |
| `footer-rule` | 1px rule at bottom: 32px | (no text) |
| `footer-left` | bottom-left chrome | "CONFIDENTIAL — ACCENTURE INTERNAL" |
| `footer-right` | bottom-right chrome | "Slide Lab · 2026 · N" |

> Cover pattern (19) is the only invariant outlier: it has no action title / subtitle / brand-rule; instead it carries cover-specific shapes (see "Cover" family below). The chrome roles still apply.

## Optional title-block additions (above title)

| data-shape-id | Description | Where it shows up |
|---|---|---|
| `eyebrow` | kicker label above title — 10-11px uppercase letter-spaced accent text | 03, 05, 10, 22, 23, 38, 40, 41, 46, 47, 48, 49, 52, 57, 59, 62, 63, 75, 86, 87, 88, 89, 91, 95, 96, 97, 98, 100 (very common). Canonical source class: `.section-label`, `.eyebrow`, `.pre-label`, `.tag`. |
| `eyebrow-meta` | secondary meta on title row (date, period, section number) | 06 (`Section · 03`), 88 (`May 2026`), 98 (period label). Rare — keep as canonical because ≥3 patterns. |

## Body-zone roles — by family

### Hero / single statement (pattern 38, 30, 97)

| data-shape-id | Description |
|---|---|
| `hero-statement` | the big quote/statement text (60-72px on dark, italic) |
| `hero-rule` | accent rule under the statement |
| `hero-attribution` | "— Mario Peralta · After 12 pilot decks · May 2026" |
| `hero-context` | optional italic gloss below attribution |

### Hero stat (single giant number — 91, 74, 10's annot panel echo)

| data-shape-id | Description |
|---|---|
| `hero-stat-label` | "OUR NORTH STAR" eyebrow above the number |
| `hero-stat-value` | the giant number (96-160px) |
| `hero-stat-unit` | inline unit suffix ("%", "days", "×") inside the value |
| `hero-stat-caption` | one-sentence italic caption under the number |

### Section divider (pattern 06)

| data-shape-id | Description |
|---|---|
| `divider-numeral` | the huge 200-360px section number (right side) |
| `divider-section-label` | "SECTION · 03" eyebrow |
| `divider-title` | the section title (replaces normal `title`) |
| `divider-subtitle` | replaces normal `subtitle` |
| `divider-rule` | accent rule under divider title |
| `divider-top-rule` | full-width 6px brand-accent bar at top of slide |
| `divider-bottom-rule` | full-width 6px brand-accent bar at bottom of slide |

### Cover (pattern 19)

| data-shape-id | Description |
|---|---|
| `cover-left-panel` | dark brand-primary half-panel (background, no text) |
| `cover-deck-title` | "Slide Lab" |
| `cover-tagline` | "Think. Argue. Build." |
| `cover-pre-label` | "INTERNAL DECK · 2026" |
| `cover-presented-label` | "PRESENTED BY" |
| `cover-presented-name` | "Mario Peralta · Strategy Manager" |
| `cover-brand-mark` | small 18px accent square top-right |
| `cover-meta-rule` | vertical accent rule beside meta block |
| `cover-meta-1-label` …`cover-meta-3-label` | "PREPARED FOR" / "DATE" / "DURATION" |
| `cover-meta-1-value` …`cover-meta-3-value` | the values |

### Cards (N = 1..6) — 01, 03, 23, 24, 27, 37, 41, 64, 75, 77, ...

| data-shape-id | Description |
|---|---|
| `card-N-num` | optional 01/02/… numeral in card (max N=6 seen in 03, 52) |
| `card-N-icon` | optional icon (no text) |
| `card-N-eyebrow` | optional eyebrow above heading |
| `card-N-heading` | card title (16-18px bold brand-primary) |
| `card-N-body` | card body copy (12-14px) |
| `card-N-footer` | optional footer text inside card (badge, source, "Lead: PM" etc.) |
| `card-N-badge` | optional "RECOMMENDED" / "FEATURED" pill |

Max N observed: 6 (logo wall and other 2x3 grids). Most patterns use 3 or 4.

### Tiles / KPI metrics (N = 1..6) — 12, 24, 27, 44, 59, 91, 98, 88

| data-shape-id | Description |
|---|---|
| `metric-N-label` | tile eyebrow / KPI name (10-12px uppercase) |
| `metric-N-value` | the big number (32-52px) |
| `metric-N-unit` | inline unit ("%", "days", "×", "/10") |
| `metric-N-delta` | optional secondary delta line ("−62% vs baseline · 14d → 5d") |
| `metric-N-sublabel` | optional second label line under value |

Max N observed: 6 (pattern 12). Stat-bank pattern 59 also runs N=6.

### Pillars / columns / vertical bands (N = 1..5) — 02, 47, 60, 71, 81, 87

| data-shape-id | Description |
|---|---|
| `pillar-N-header` | dark header band |
| `pillar-N-icon` | icon in header |
| `pillar-N-name` | pillar name in header |
| `pillar-N-body` | light body with bullets |
| `pillar-N-tag` | optional small tag/sub label |

Max N observed: 5 (47 strategy house, 71 ref-architecture layers, 52 tile rail). Pillars 1-5.

### Process / phases / steps (N = 1..5) — 16, 18, 28, 45, 46, 51, 80, 92

| data-shape-id | Description |
|---|---|
| `step-N-num` | the circled / large numeral |
| `step-N-eyebrow` | "PHASE 1" etc. |
| `step-N-name` | "DISCOVER" — bold cap (14-18px) |
| `step-N-desc` | one-line descriptor under name |
| `step-N-body` | bullet list / rich content |
| `step-N-exit-label` | "EXIT CRITERION" eyebrow |
| `step-N-exit-text` | the exit-criterion text |
| `step-N-meta-left` | optional "Lead: PM" |
| `step-N-meta-right` | optional "W1–W2" |

Max N observed: 5 (pattern 18, 52). Chevron variants reuse the same vocabulary.

### 2x2 / quadrant frameworks — 13, 21, 32, 88, 99

Quadrant positions use **`tl`, `tr`, `bl`, `br`** suffixes (top-left, top-right, bottom-left, bottom-right).

| data-shape-id | Description |
|---|---|
| `quadrant-tl-label` … `quadrant-br-label` | small eyebrow per quadrant ("START HERE", "PLAN DELIBERATELY") |
| `quadrant-tl-name` … `quadrant-br-name` | quadrant name ("Quick wins", "Strategic bets") |
| `quadrant-tl-directive` … `quadrant-br-directive` | italic one-liner directive |
| `quadrant-tl-body` … `quadrant-br-body` | bullet list of items inside quadrant |
| `quadrant-x-axis-label` | "EFFORT" axis title |
| `quadrant-x-low` / `quadrant-x-high` | "LOW" / "HIGH" tick labels |
| `quadrant-y-axis-label` | "IMPACT" axis title |
| `quadrant-y-low` / `quadrant-y-high` | tick labels |

### SWOT (special-case quadrant, pattern 32) — reuses `quadrant-*` with `tl`/`tr`/`bl`/`br`.

### Cards-in-quadrant items (stakeholder chips, 21)

| data-shape-id | Description |
|---|---|
| `quadrant-tl-chip-N` | individual chip inside the quadrant body (N=1..6) |

### Legends (top-right per the standing rule, or bottom) — 10, 14, 20, 23, 44, 66, 69, 70, 86, 87, 88, 90, 95, 99, 100

| data-shape-id | Description |
|---|---|
| `legend-title` | optional legend title |
| `legend-N-swatch` | colored swatch / dot / line marker (N=1..5; up to 5 seen) |
| `legend-N-label` | swatch label ("Baseline", "Pilot · wk 4", "On track") |
| `legend-N-meta` | optional secondary meta on the legend row |

### Bar rows (horizontal bar chart bodies, pattern 10)

| data-shape-id | Description |
|---|---|
| `bar-N-label` | row label ("Cycle time") |
| `bar-N-unit` | unit ("days") below label |
| `bar-N-baseline-bar` | the baseline bar (no text — shape only) |
| `bar-N-pilot-bar` | the pilot bar |
| `bar-N-baseline-val` | inline value on baseline bar ("14") |
| `bar-N-pilot-val` | inline value on pilot bar ("5") |
| `bar-N-delta` | delta callout ("−64%") |
| `bar-N-delta-cap` | small caption under delta ("faster") |

Max N seen: 4 (pattern 10). Tornado (69) uses the same naming with positive/negative variant.

### Chart annotation panel (right-side panel beside chart) — 10, 66, 69, 100

| data-shape-id | Description |
|---|---|
| `annot-header` | "WHAT THIS MEANS" eyebrow |
| `annot-sub` | sub-headline |
| `annot-rule` | small accent rule |
| `annot-N-marker` | arrow/bullet marker per row (no text) |
| `annot-N-label` | row label / heading |
| `annot-N-body` | row body |

Max N: 3 in patterns observed.

### Chart frame (containers for SVG charts) — 10, 14, 28, 33, 34, 66, 68, 69, 70, 72, 100

| data-shape-id | Description |
|---|---|
| `chart-title` | chart title above the SVG |
| `chart-subtitle` | optional chart subtitle / sample size |
| `chart-source` | small italic source line under chart |
| `chart-canvas` | the SVG when treated as a single picture-shape in PPTX twin |

### SVG handling — mixed approach (per user decision 2026-05-18)

Each SVG-driven pattern is classified at twin-generation time as either **decompose** (each SVG primitive becomes a native python-pptx shape with its own `data-shape-id`) or **picture-asset** (the whole SVG is rendered to PNG and inserted as one picture with `data-shape-id="chart-canvas"`).

Classification policy:
- **Decompose** when: SVG is geometric/regular (stacked rectangles, concentric circles, radial slices), node count ≤ ~12, and per-node text edits are plausible
- **Picture-asset** when: SVG has irregular geometry (trees, fishbones, cascades, river flows), node count > ~12, or per-node editing is unlikely in deck-build

| Pattern | Diagram | Treatment | Reason |
|---|---|---|---|
| 15 | Org chart | **picture-asset** | Hierarchical tree, many nodes, irregular spacing |
| 28 | Vertical timeline | **picture-asset** | Variable event count, irregular spacing |
| 29 | Decision tree | **picture-asset** | Branching, irregular |
| 31 | Pyramid | **decompose** | 4-5 stacked trapezoids — clean primitives |
| 33 | Fishbone | **picture-asset** | Radial bones, irregular geometry |
| 34 | Cycle | **picture-asset** | Circular arrows around N nodes — arc geometry hard to decompose cleanly |
| 35 | Funnel | **decompose** | N stacked trapezoids — clean primitives |
| 48 | Venn | **decompose** | 2 circles + overlap text — trivial |
| 49 | Convergence river | **picture-asset** | Flowing lanes, complex curves |
| 68 | Donut | **decompose** | Concentric ring with N segments — uses python-pptx pie/donut chart |
| 70 | Radar | **picture-asset** | Polar grid + polygon — complex geometry |
| 71 | Architecture layers | **decompose** | Stacked panels (not really SVG-native) |
| 72 | OKR cascade | **picture-asset** | Multi-level cascade with connectors |
| 82 | 7S framework | **picture-asset** | 7 interconnected circles with curves |
| 83 | Porter's five forces | **picture-asset** | Center + 4 outer with arrows |
| 96 | Concept visual | **picture-asset** | (review at twin-gen time — likely picture) |
| 100 | Pareto | **decompose** | Bar+line chart → python-pptx native chart |

For **decompose** patterns: each primitive gets a canonical or pattern-local `data-shape-id` (e.g., `tier-1-shape`, `tier-2-shape`, `venn-circle-left`, `donut-slice-1`).
For **picture-asset** patterns: only the outer `<svg>` is stamped with `data-shape-id="chart-canvas"`. Per-node SVG text is NOT individually addressable. Text **next to** the SVG (legends, callouts, captions) is stamped normally with canonical IDs.

**One-way sync caveat:** for picture-asset patterns, editing the SVG content requires regenerating the picture. The PPTX twin's `chart-canvas` is a regenerated artifact, not directly editable in PowerPoint without re-rendering from HTML.

### Convergence / takeaway band (single brand-primary strip at bottom of body) — extremely common

| data-shape-id | Description |
|---|---|
| `convergence` | the body convergence/takeaway/so-what band |
| `convergence-mark` | optional icon/arrow/quote-mark prefix |

Appears in: 01, 04, 05, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 27, 29, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 47, 48, 49, 53, 54, 57, 59, 60, 61, 62, 63, 64, 66, 68, 69, 70, 71, 72, 74, 75, 76, 77, 80, 81, 82, 83, 85, 86, 87, 88, 89, 90, 91, 94, 95, 96, 97, 99, 100. (Near-universal — but not chrome-invariant because cover/divider lack it.)

### Comparison band / matrix headers — 04, 17, 37, 54, 61

| data-shape-id | Description |
|---|---|
| `compare-col-1-header` … `compare-col-N-header` | column header text (max N=3 observed) |
| `compare-col-1-icon` … `compare-col-N-icon` | optional column icon |
| `compare-row-N-label` | row label ("Root cause", "What it produces") |
| `compare-row-N-col-N-cell` | the cell text — addressable as `compare-row-1-col-1-cell` |

### Before / After two-panel — 17

| data-shape-id | Description |
|---|---|
| `before-panel-label` | "BEFORE · WEEK 0" |
| `before-panel-heading` | panel title |
| `before-panel-body` | bullet list / body |
| `after-panel-label` / `after-panel-heading` / `after-panel-body` | same for After |
| `transformation-arrow-label-top` / `transformation-arrow-label-bottom` | small captions above/below arrow |
| `transformation-arrow` | arrow shape (no text) |

### Honest-expectations / two-panel symmetric — 07

Uses generic `panel-1-*` / `panel-2-*`, same fields as before/after.

### Agenda / TOC (numbered list, pattern 09)

| data-shape-id | Description |
|---|---|
| `toc-N-num` | "01", "02" … (max N=8 seen) |
| `toc-N-title` | section title |
| `toc-N-desc` | one-line description |
| `objectives-label` | "SESSION OBJECTIVES" eyebrow |
| `objectives-heading` | "By the end of 30 minutes…" |
| `objective-N-marker` | bullet marker (no text) |
| `objective-N-text` | objective text (max N=4) |
| `objectives-note` | trailing italic note |

### Long-form structured text / SCQA — 11, 43, 89, 96

| data-shape-id | Description |
|---|---|
| `section-N-num` | "01" (max N=4 in SCQA) |
| `section-N-name` | stage name ("SITUATION") |
| `section-N-body` | the paragraph |
| `table-head-N` | column headers when rendered as table |

### Definitions / glossary — 43, 96

| data-shape-id | Description |
|---|---|
| `term-N-label` | the term being defined |
| `term-N-def` | the definition body |
| `term-N-example` | example italic |
| `term-N-prov` | provenance / source attribution |
| `term-N-rule` | divider rule between term rows |

### Tables (RACI 63, risk register 86, action register 95, scorecard 44, RAG-grid 23, 7S legend 82, comm plan, capability gap 90, scenarios 54)

| data-shape-id | Description |
|---|---|
| `table-col-1-header` … `table-col-N-header` | column headers |
| `table-row-N-cell-M` | data cell at row N, col M |
| `table-row-N-num` | row number when shown |
| `table-row-N-rag-dot` | RAG status dot (no text) |
| `table-row-N-status-pill` | status pill ("On track" / "At risk") |
| `table-row-N-status-pill-text` | pill text |

Cells are addressable. For tables with N≥8 rows (RAG grid 23, action register 95, risk register 86), the pattern-specific table is still canonical — just keep N tied to the pattern's max.

### Status / RAG signals — 23, 44, 86, 88, 90, 94, 95

| data-shape-id | Description |
|---|---|
| `rag-dot` | small colored dot (no text) — when standalone |
| `rag-pill` | status pill with text |
| `rag-pill-text` | the pill label |
| `status-dot` | alias used in some patterns |

### Timeline / Gantt — 14, 28, 51, 53, 60, 80

| data-shape-id | Description |
|---|---|
| `timeline-axis` | the horizontal/vertical baseline |
| `timeline-tick-N-label` | "W1", "Q3 2025" etc. |
| `phase-band-N-label` | phase header band ("PHASE 1 · SETUP") — N=1..3 |
| `task-N-label` | row label ("Stakeholder alignment") |
| `task-N-bar` | the Gantt bar shape |
| `task-N-bar-text` | text inside bar ("W1–W2 · in flight") |
| `milestone-N` | diamond shape (no text) |
| `milestone-N-label` | small label above milestone |

### Persona card — 41

| data-shape-id | Description |
|---|---|
| `persona-photo` | photo placeholder |
| `persona-name` | name |
| `persona-role` | role |
| `persona-name-rule` | accent rule |
| `persona-zone-goals-label` / `persona-zone-goals-body` | "GOALS" zone |
| `persona-zone-pains-label` / `persona-zone-pains-body` | "PAIN POINTS" zone |
| `persona-skill-N-name` | skill name |
| `persona-skill-N-dots` | dot meter (no text) |
| `persona-quote` | pull-quote inside persona card |
| `persona-quote-attr` | attribution |

### Photo / image placeholders — 05, 22, 41, 74, 76, 77

| data-shape-id | Description |
|---|---|
| `photo-zone` | the placeholder rectangle (no text — PPTX picture insertion target) |
| `photo-corner-tag` | "SCREENSHOT" / "PHOTO" corner badge |
| `photo-label` | "[ Demo capture — Slide Lab Think & Argue panel ]" placeholder text |
| `photo-caption` | caption beside / below photo |
| `photo-meta` | meta line (filename, attribution, source) |

For multi-image grids (77), use `photo-N-zone`, `photo-N-caption`, etc. Max N=6.

### Logo wall — 76

| data-shape-id | Description |
|---|---|
| `logo-N-tile` | logo placeholder tile (max N=12) |

### Quotes (single — 30, stack of 3 — 75)

| data-shape-id | Description |
|---|---|
| `quote-mark` | big leading quote glyph |
| `quote-text` | quote body |
| `quote-attribution-name` | name of speaker |
| `quote-attribution-role` | role / context |
| `quote-rule` | accent rule under the quote |

For stacked quotes (75), use `quote-N-text`, `quote-N-attribution-name`, etc. N=1..3.

### Closing CTA / Ask — 40

| data-shape-id | Description |
|---|---|
| `primary-ask-label` | "PRIMARY ASK" eyebrow |
| `primary-ask-text` | the main ask sentence |
| `ask-caption` | italic caption |
| `conditions-label` | "CONDITIONS" eyebrow |
| `conditions-hint` | small hint line |
| `sub-ask-N-num` / `sub-ask-N-label` / `sub-ask-N-body` / `sub-ask-N-meta` | three sub-asks |

### Decision frame (revival CTA 40, decisions needed 88)

Re-uses `sub-ask-*` and `decision-*` shapes — kept under the CTA family above.

### Exec status quad (88) — re-uses `quadrant-*` (tl/tr/bl/br) plus optional `quad-N-meta` ("3 open") and `quad-N-icon`.

### Mission / Vision / Values tiered pyramid (85)

| data-shape-id | Description |
|---|---|
| `tier-vision-label` / `tier-vision-statement` | top tier (dark) |
| `tier-mission-label` / `tier-mission-statement` | middle tier |
| `tier-values-label` | base tier label |
| `value-chip-N-icon` / `value-chip-N-name` / `value-chip-N-desc` | values across the base (N=1..5) |

### North-star + input metrics (91)

| data-shape-id | Description |
|---|---|
| `hero-stat-label` / `hero-stat-value` / `hero-stat-caption` | (see hero-stat family) |
| `inputs-header` | "INPUT METRICS — what we actually move" |
| `input-N-value` / `input-N-unit` / `input-N-label` | 4 input cards (N=1..4) |

### Outputs strip (02) — three small footer-strip cards under pillars

| data-shape-id | Description |
|---|---|
| `output-N-label` | "PRODUCES" eyebrow |
| `output-N-text` | strip body |

N=1..3.

### Maturity / staircase / ladder (31 pyramid, 47 house, 71 layers)

The visual is SVG → single `chart-canvas` image in PPTX twin. The accompanying text labels NEXT to the SVG are stamped:

| data-shape-id | Description |
|---|---|
| `tier-N-label` | tier label / level number |
| `tier-N-name` | tier name |
| `tier-N-desc` | tier description |
| `tier-current-chip` | "YOU ARE HERE" pill (single, no N) |
| `tier-current-arrow` | small arrow pointing to current tier |

N typically 1..5.

### Anchor stat + evidence rail (57)

| data-shape-id | Description |
|---|---|
| `anchor-pre-label` | eyebrow |
| `anchor-stat` | the big number |
| `anchor-unit` | inline unit |
| `anchor-status-label` / `anchor-status-value` | status meta below the number |
| `anchor-divider` | thin rule |
| `evidence-N-tag` / `evidence-N-icon` / `evidence-N-title` / `evidence-N-body` | stacked evidence cards (N=1..4) |

### Scenario / impact rail (53, 54)

| data-shape-id | Description |
|---|---|
| `scenario-N-name` | scenario name |
| `scenario-N-tag` | scenario tag/label |
| `scenario-N-impact-amount` | the dollar/numeric impact |
| `scenario-N-impact-note` | note on impact |
| `scenario-N-verdict-pill` | pill ("good"/"bad"/"warn") |

N up to 3.

### Investment thesis cards (64)

| data-shape-id | Description |
|---|---|
| `thesis-N-num` | numeral |
| `thesis-N-statement` | thesis sentence |
| `thesis-N-stat` | KPI inside card |
| `thesis-N-unit` | unit |
| `thesis-N-rationale` | rationale body |

N=1..3.

### ADKAR / change readiness (94)

| data-shape-id | Description |
|---|---|
| `stage-N-letter` | "A" / "D" / "K" / "A" / "R" |
| `stage-N-name` | stage name |
| `stage-N-definition` | definition |
| `stage-N-observation` | observation row |
| `stage-N-score` | readiness score |
| `stage-N-meter` | meter (no text) |
| `stage-N-status-pip` | RAG pip |
| `readiness-bar-fill` | overall readiness bar (single) |
| `readiness-label` / `readiness-verdict` | label + verdict text |

N=1..5.

## Stamping rules

1. Every `<div>` or text element that renders a visible shape gets a `data-shape-id`.
2. Pure layout containers (no own background, no own text, no own border) do NOT get an ID. Examples to skip: `.body-grid`, `.content-block`, `.cards`, `.tile-grid`, `.cards-row`, `.matrix-wrap`, `.grid-wrap`, `.steps`, `.tile-rail`, `.phases`, `.body-row`, `.body-region`, `.title-block`.
3. Inline `<strong>` / `<em>` inside a parent text element do NOT get their own ID — they're part of the parent's run text and re-styled by the composer via the `<strong>` semantic.
4. Repeated shapes use 1-indexed positional suffixes: `card-1-heading`, `card-2-heading`, etc.
5. For quadrants/2x2, use positional suffixes `tl` / `tr` / `bl` / `br` instead of `1` / `2` / `3` / `4`.
6. SVG canvases — classification table above determines whether to decompose into native shapes or treat as a single `chart-canvas` picture. Default to picture-asset when in doubt; decompose only when the SVG is clearly geometric (concentric circles, stacked trapezoids, regular polygons) with ≤ 12 nodes. Text **next to** the SVG (legends, callouts, captions) is always stamped with canonical IDs regardless.
7. Photo / image placeholders get `data-shape-id="photo-zone"` (or `photo-N-zone` in grids); the composer uses this as the picture-insertion target.
8. Empty rule / divider elements (`.title-rule`, `.accent-rule`, `.brand-rule`, `.spacer-rule`) get an ID only if they're load-bearing visual structure. The universal `brand-rule` (under subtitle) always gets the ID; ad-hoc rules inside body shapes can use `<parent>-rule` (e.g. `card-1-rule`, `tile-1-rule`, `persona-name-rule`).

## Pattern-specific shapes (NOT canonical, listed for reference)

These are shapes that appear in only one or two patterns. The PPTX twin for those patterns will carry the names directly; we don't propagate them to the canonical vocabulary.

| Pattern | Shape | Why not canonical |
|---|---|---|
| 20 | `risk-N-name`, `risk-N-badge` (risk list beside heatmap) | Only pattern 20 has the side risk-list — heatmap cells themselves are inside `chart-canvas`. |
| 28 | `event-N-title`, `event-N-desc`, `event-N-date` (vertical timeline labels) | Vertical timeline is SVG; labels can sit inside the canvas image. |
| 33 | per-bone `category-label`, `subcause-text`, `effect-text` (fishbone) | Inside `chart-canvas`. |
| 34 | `cycle-node-N-label`, `cycle-callout-title/line` | Inside `chart-canvas`. |
| 35 | `funnel-tier-N-stage/count/drop/callout` | Inside `chart-canvas`; outer convergence + tier labels rendered alongside use `tier-N-*`. |
| 36 | `journey-phase-N-name/num`, `journey-row-actions/opps/pain` | Customer journey grid — unique enough to keep pattern-local. |
| 48 | `venn-circle-left/right`, `venn-overlap` text | Inside `chart-canvas`. |
| 49 | `convergence-river` lanes + nodes | Inside `chart-canvas`. |
| 65 | `heatmap-cell-row-N-col-M` (capability heatmap) | DEFERRED pattern; if revived, propose adding to canonical. |
| 70 | radar polygon points, dim labels | Inside `chart-canvas`; delta-rows beside use `delta-N-*` pattern-local. |
| 72 | OKR cascade `objective`, `kr-N` | Cascade is SVG; KR list beside uses pattern-local IDs. |
| 82 | 7S `node-N-name/desc`, `legend-N-name/status` | Diagram inside `chart-canvas`; legend uses standard `legend-N-*` plus pattern-local `status-strong/build/gap` text. |
| 83 | Porter's `force-N-head/name/bullets`, `intensity-high/med` | Force diagram inside `chart-canvas`; surrounding intensity badges are pattern-local. |
| 99 | `plot-dot` quick-win matrix dots | Inside the quadrant grid; treat as decorative — keep pattern-local. |

## Patterns flagged for special handling (composer should treat the chart as a single image)

`15` (org chart), `28` (vertical timeline), `29` (decision tree), `31` (pyramid), `33` (fishbone), `34` (cycle), `35` (funnel), `48` (venn), `49` (convergence river), `68` (donut), `70` (radar), `71` (architecture layers), `72` (OKR cascade), `82` (7S), `83` (Porter's), `96` (concept visual), `100` (Pareto). All of these have an SVG canvas as the body's focal shape; the surrounding text/legend/annotation IS stamped with canonical IDs, but the diagram itself flows through `chart-canvas` (single picture).

## Closed vocabulary summary

**Canonical role families (count):** 30 families covering ~40 distinct base roles (most parametrize by N).

Families: invariants (8 fixed), eyebrow/meta, hero-statement, hero-stat, divider, cover, card, metric/tile, pillar, step/phase, quadrant (tl/tr/bl/br), legend, bar-row, annot, chart frame, convergence, compare matrix, before/after, agenda/TOC, section (SCQA), term/definition, table, status/RAG, timeline/Gantt, persona, photo, logo, quote, CTA/ask, tier (mission/values), inputs, anchor-stat-evidence, scenario, thesis, ADKAR.

The Max-N values reflect real maxima observed in the approved 85 patterns: cards 6, metrics 6, pillars 5, steps 5, legend entries 5, bar rows 4, annot rows 3, sub-asks 3, photos in grid 6, logo wall 12, agenda items 8.
