# Ontology Challenge — Agent 5

## Verdict: SHIP IT WITH FIXES

The simpler ontology is directionally correct — 19 chassis + adjacency + content tags + list schema + Layer 5 was over-engineered and the 23% acceptance proves it. Ten splits plus two objects covers most consulting slide work. But there are three concrete holes that will resurface as the same agent confusion the v1 architecture was supposed to solve, and one piece of vocabulary (Diagram canvas) that is doing the work of a garbage bag. Fix them before shipping or you will be writing a v3 ontology in four weeks.

## What I tried

I ran fourteen consulting slide concepts through the splits and objects and tried to place each one without cheating:

- Org chart, RACI, Gantt, swimlane, Porter 5 Forces, value chain, customer journey, KPI tile row, BCG 2x2, Kano curve, decision tree, tornado/sensitivity, waterfall bridge, multi-currency dashboard.

For each, I asked: which split? Which object? Is the placement honest, or am I shoving it into Diagram canvas because nothing else fits?

I also stress-tested rule 3 (no adjacent same-split) against three realistic brief patterns: an executive summary deck with 5 KPI-row slides in a row, a "current state vs future state" pair, and a four-page findings section where every page is naturally Top-band-plus-body.

## What broke

**1. Diagram canvas is a dumping ground.** Org chart, swimlane, Porter, value chain, customer journey, decision tree all land here. Six of fourteen concepts collapse into one bucket with zero structural guidance. The whole point of having vocabulary is so the agent can pre-position zones from a helper function. "Diagram canvas (free-form)" has no zones — it is the absence of a split. You have not simplified those six slide types; you have deferred them to agent autonomy, which is exactly where v1 burned. Expect drift, expect overlap bugs, expect SKELETON_REJECTED loops on every diagram slide.

**2. Multi-object slides have no home.** A multi-currency dashboard is six small charts plus a KPI strip plus a takeaway. The rule "charts/tables only in object layouts" implies one object per slide. There is no composable rule "dense grid of charts" or "N-column row of objects." Same problem with a competitor-comparison page that wants three mini-tables side by side, or a portfolio review with 4 KPI cards + 1 chart + 1 callout. You either need (a) objects to nest inside splits, or (b) a "dashboard" split with N tiles each typed as chart/KPI/text. The current ontology forces these slides into Diagram canvas, which means free-form, which means the same coordinate-math failures.

**3. Gantt and swimlane are mis-routed.** Gantt is declared absorbed by Chart, but Chart is "axes + items + takeaway." Gantt is a time-axis table where rows are tasks and the data is positioned bars — semantically closer to Table-with-bar-fills than to bar chart. If your Chart helper assumes value bars at Y=task, fine — say so explicitly. If not, the agent will either build a custom diagram or produce a deformed bar chart. Swimlane is the same problem: it is semantically a Table with labeled rows AND labeled columns, but Table is "banded rows + header" (single axis of labeling). The two-axis labeled grid is a missing primitive.

**4. Rule 3 over-fires on legitimate cadence.** An executive summary commonly opens with five KPI-row slides — same split is the *point*, it creates visual rhythm and signals "scan these together." Same with three sequential Top-band-plus-body findings pages. Rule 3 will reject these and the agent will start varying split just to satisfy the rule, producing layout chop where the brief asked for cadence. Rule 3 needs an escape hatch: either "rule 3 fires only across section boundaries" or "rule 3 fires only when content density differs."

**5. Asymmetric vertical (75/25) is suspiciously narrow.** Why 75/25 and not 60/40 or 70/30? Real briefs hand you content ratios all over the map. Either you allow a parameter (e.g., split ratio in {60/40, 70/30, 75/25, 80/20}) and the agent picks, or you will see "75/25" abused for any unequal split and the rendering will be wrong half the time. Same scrutiny applies to N-column row (3-6) — fine — and Dense grid (2x3 or 3x3) — why no 2x2 or 2x4 or 3x2? 2x2 is one of the most common consulting layouts.

**6. Autonomy convergence.** Variants = agent autonomy on typography, accent, icon, numeral, eyebrow. With five agents fanned out in parallel and no shared variant token, you will see four agents pick the same "obvious" choice (e.g., navy accent, sans-serif numeral) because the brief steers them there. Then the user sees four near-identical options. v1 had this same problem; deleting the variant vocabulary does not fix it, it just removes the lever for forcing diversity. Either seed each agent with a forced variant axis or accept that variants are decorative noise.

## What held

The core ten splits cover roughly 60% of real consulting slides cleanly: KPI rows, two-column compare, anchor-plus-cards, findings with sub-points, dense data grids. The Chart object absorbing Matrix is defensible *for true plotted matrices* (BCG, Kano, risk heatmap). The deletion of adjacency graph + content tags + list[1..2] is the right call — those were academic. SKELETON_REJECTED as a hard gate is correct. Pre-positioned zones in helpers.py is the right architectural shape, assuming you actually have a zone definition for every split (Diagram canvas does not — see above).

Migration-wise, most of the 19 chassis map cleanly: 2panel-convergence -> 50/50; 3pillar-icon-circles -> N-column row (3); anchor-with-cards -> Left rail + body or Top band + body; cover-fullbleed-dark -> Full canvas; dark-hero-foil -> Full canvas (variant=dark). The chassis that do NOT map cleanly are the diagram-flavored ones — anything that was depending on chassis-specific geometry (delta-spine, convergence arrows) now lives in Diagram canvas with no guidance.

## Matrix-as-chart position

Honest for BCG, Kano, risk heatmap, GE-McKinsey nine-box. Paper-over for RACI and any "matrix" that is actually a labeled grid of text cells. The test is: does the position of an item encode a value on two numeric or ordinal axes? If yes, Chart. If the cells just contain text labeled by row/column, it is a two-axis Table, not a Chart, and you do not have a primitive for that. Either add "Grid-table (row-header + column-header + cells)" as a third object, or admit RACI/swimlane/competitor-comparison go to Diagram canvas and accept the quality cost.

## Biggest concern

Diagram canvas. Six of fourteen consulting slide concepts land there, including org chart, swimlane, Porter, value chain, journey, decision tree — all high-frequency executive-deck content. "Free-form" with no zone helper means each one is built from scratch every time by an agent doing coordinate math. That is the exact failure mode the chassis vocabulary was invented to prevent. If you ship without at least four named diagram patterns (tree, swimlane-grid, process-flow, hub-and-spoke), each with a helper that pre-positions zones, you will get the same 23% acceptance rate on diagrams that you got on chassis overall — and diagrams are the slides where the cost of failure is highest, because users cannot eyeball-fix a broken Porter diagram the way they can nudge a misaligned KPI tile.

Add those four diagram primitives, add a "dashboard" or composite-object rule, parameterize the asymmetric split, soften rule 3, and this ships.
