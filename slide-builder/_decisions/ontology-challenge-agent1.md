## Verdict

**SHIP IT WITH FIXES** — the ontology survives most of the real consulting slide types I threw at it, and the matrix-as-chart collapse is more honest than I expected. But it has four concrete structural holes that, left unfixed, will reproduce the same divergence bug that killed the 19-chassis approach. Fix list at the bottom of this section; details below.

The four fixes:
1. **Make split #10 (Diagram canvas) a real primitive, not an escape hatch** — declare 3-4 named diagram subtypes (tree, hub-spoke, fishbone, linear-flow) with explicit geometry, or split #10 IS the agent-autonomy black hole that re-creates the convergence bug.
2. **Allow nested splits inside zones** (or explicitly disallow and add an 11th split for banded N-column, i.e. value-chain geometry).
3. **Soften rule 3 (no adjacent same-split) to "no 3+ consecutive same-split"** — the hardline version is incompatible with the dominant executive-deck pattern of multiple sequential findings.
4. **Carve a "compound-object" exemption to rule 1 (charts/tables only in own layouts)** — dashboards with sparklines and before/after dual-chart slides are real and the current rule forbids them.

## What I tried to break it with

I ran 14 real consulting slide types through the 10+2 splits: org chart, RACI, swimlane (cross-functional process), Gantt, Porter's 5 forces, value chain, customer journey, Stacey/Eisenhower/BCG 2x2, Kano, MoSCoW, KPI dashboard, decision tree, P&L summary, sensitivity (tornado).

I also attacked the architecture itself on four axes: (a) does diagram canvas re-introduce the convergence bug under a new name, (b) does rule 3 over-trigger on the standard executive-deck shape, (c) does rule 1 forbid legitimate compound slides, (d) is "variant autonomy" actually constrained enough to prevent the 23% acceptance failure.

## What broke

**Case 1: Diagram canvas is "free-form" — same agent-autonomy hole that killed the 19-chassis approach.**
Org chart, Porter's 5 forces, fishbone, decision tree, hub-spoke, and any process-with-branching all land in split #10. The brief just says "open-zone for free-form node-networks." That is not a layout — it is "agent decides." Two agents handed the same Porter's 5 Forces brief will produce two visually divergent slides — exactly the failure mode that just blew up at 23% acceptance. The 10-split ontology cannot claim convergence wins from collapsing chassis vocabulary if it then concentrates all node-graph slides into one undefined split.
**Fix:** Either declare 3-4 named diagram subtypes with hardcoded geometry (`helpers.diagram_tree`, `helpers.diagram_hub_spoke`, `helpers.diagram_fishbone`, `helpers.diagram_linear_flow`), or accept that split #10 has no convergence guarantee and exclude that family from convergence-rate KPIs.

**Case 2: Value chain (Porter) — banded N-column geometry not in the 10.**
Value chain is one band of 4 "support activities" stacked on top of a band of 5 "primary activities," all wrapped in an arrow shape. That is a #6 (N-row stack) where each row is itself a #5 (N-column). The 10 splits do not declare whether zones can nest other splits. If they can, value chain works (and so does customer journey, which is a similar nested grid). If they cannot, value chain has no home and you have genuinely lost a primitive.
**Fix:** Either explicitly state "any split's zone may host another split, recursively" in the rulebook (preferred — opens nested-grid space cheaply), or add split #11 "banded N-column" as a first-class primitive.

**Case 3: Rule 3 (no adjacent same-split) breaks the standard 3-finding executive pattern.**
The most common consulting deck shape is: cover -> context -> Finding 1 -> Finding 2 -> Finding 3 -> synthesis -> recommendation. Findings 1/2/3 almost always want the same split (top-band-plus-body or asymmetric-vertical) because they are parallel content. Rule 3 forbids that. You either break the rule (in which case it is not a rule), or you contort findings 2 and 3 into geometries that do not match their content. This is a real defect, not a corner case.
**Fix:** Soften to "no 3+ consecutive same-split" OR exempt the finding-series pattern explicitly. Visual variety across 8 slides is good; visual variety FORCED across 3 parallel findings is bad.

**Case 4: Rule 1 (charts/tables only in own layouts) forbids dashboards and before/after.**
KPI dashboards with embedded sparklines, and before/after slides showing two charts side-by-side, are both standard. Rule 1 says charts only live in split #11. So a KPI dashboard in split #7 (dense grid) cannot contain a sparkline tile. A before/after slide in split #2 (50/50 vertical) cannot put a chart on each side. This is not a rare case — it is everywhere in operational reporting.
**Fix:** Reword rule 1 to "Chart slides (whose primary purpose is plotting data) use split #11. Charts embedded as supporting elements inside cells of other splits are permitted." Same for tables.

## What held

**Org chart (with fix 1):** named tree subtype in diagram canvas — works.
**RACI:** pure Table (#12). Clean fit.
**Gantt:** Chart (#11) with horizontal-bar variant on time axis. Clean.
**Customer journey:** dense grid (#7) of stages x layers; emotion curve becomes a chart overlay (needs fix 4 to allow embedded chart).
**Stacey / Eisenhower / BCG 2x2:** Chart (#11) with the "quadrant labels" mode. Works — see honest take below.
**Kano model:** pure Chart (#11). Clean.
**MoSCoW:** N-column row (#5) with 4 columns, or dense grid 2x2. Both work.
**P&L summary:** pure Table (#12). Clean.
**Sensitivity (tornado):** Chart (#11) horizontal bar. Clean.
**Cover / single finding / recommendation / agenda:** all fit cleanly into full-canvas, top-band-plus-body, or asymmetric vertical. No issues.

The 10 splits genuinely cover the long tail of cover/content/finding/recommendation slides plus the two structured objects. The collapse is real for ~80% of slide types I tested.

## Honest take on the matrix-as-chart collapse

**Mostly honest, defensible — but it does conflate two cases the rulebook should name.**

A plotted Stacey matrix (specific risks plotted on the agreement/certainty plane) is structurally identical to a scatter chart: 2D axes, items positioned by attribute values, takeaway. Calling that Chart is correct.

An empty Stacey/Eisenhower template with just the four quadrant labels and no plotted items is NOT a chart — it is a 2x2 dense grid with axis labels. There is no plotting, no positional encoding of attributes, no items. It is the same primitive as a 2x2 feature grid that happens to have axis labels.

The collapse forces both into Chart for ontology economy, and I think that is the right call — but the helper needs to accept both modes (`chart.scatter_plotted` vs `chart.quadrant_labeled`) and the rulebook should explicitly say "an axes-with-quadrant-labels-no-items rendering is a Chart in 'template mode,' rendered identically to a 2x2 grid." Without that note, agents will see "Chart" and look for data to plot, and a blank Stacey will get the wrong scaffolding.

So: collapse is honest, but needs a one-sentence note in the Chart helper docstring naming the no-items mode explicitly. Otherwise the ontology economy comes at the cost of agent confusion.

Swimlane is the one I am least sure about. It has axes (actor on Y, time on X) but no plotted numerical values — just step-blocks positioned in 2D. By the same logic as Stacey-with-quadrant-labels, it is a Chart in template mode. But swimlanes also have cross-lane arrows, which is a node-graph behavior (diagram canvas). I think swimlane is genuinely split between Chart and Diagram and the ontology does not cleanly resolve it. Minor concern, not a ship-blocker.

## My one biggest concern (since I am voting SHIP IT WITH FIXES)

**Variant autonomy is the same convergence bug, renamed.**

The 19-chassis approach failed at 23% acceptance because chassis names did not constrain enough — agents diverged. The proposal moves variant choices (typography weight, accent placement, icon-or-not, numeral-or-not, eyebrow-or-not) from named axes into "agent autonomy within split." That is strictly LESS constrained than the 19-chassis approach. If 19 named chassis could not pin agents down, 10 splits x unbounded variant freedom will not either.

The only way this is actually a simplification rather than a rebrand is if the helpers in code enforce hard defaults for variant choices, and "agent autonomy" really means "agent picks 1 of 3 documented variants per split" — not "agent picks freely." If it is truly free, you will get 23% acceptance again on the new ontology in 6 weeks, and the post-mortem will read identically to this one.

Lock the variants per split (e.g. split #4 top-band-plus-body has exactly 3 documented variants: dark-band-light-body, light-band-with-accent-rule, oversized-numeral-band) before shipping. Otherwise this is a vocabulary rename, not an architectural improvement.
