# Ontology Challenge — Agent 2

## Verdict: SHIP IT WITH FIXES

The 10 splits + 2 objects ontology is directionally correct and a clear improvement over a 19-chassis vocabulary that just clocked a 23% curator acceptance rate. But split #10 ("Diagram canvas") is a hand-wave that absorbs roughly a third of real consulting slides and will become the new failure mode if you ship without tightening it. There are also two real holes (RACI, KPI dashboards with charts inline) and a rule-3 over-trigger that needs an escape valve. Fix those four things and ship.

## What I tried to break it with

I ran the existing exemplar library — which I take as the empirical universe of "slides this skill actually produces" — through the proposed ontology, focusing on the j-* (diagram), f-* (2x2 matrix), g-* (timeline/Gantt/swimlane), i-* (table), l-* (KPI), and h-* (chart) families. Specifically I force-fit: org chart (2-level), fishbone, customer journey (5-stage), swimlane process, Gantt, RACI, Porter's 5 forces, value chain, BCG matrix, Kano model, decision tree, KPI dashboard with sparkline, and a heatmap. I also looked for slides where natural rendering produces two adjacent slides of the same split (rule 3 trigger).

## What broke

### Break 1: "Diagram canvas" is a single bucket holding incompatible diagrams

**Case.** Org chart (j-org-chart), fishbone (j-fishbone), customer journey (j-customer-journey), value chain (j-value-chain), pyramid (j-pyramid), venn (j-venn-two/three), hub-spoke (j-hub-spoke), cycle (j-cycle), funnel (j-funnel), iceberg (j-iceberg), service blueprint (j-service-blueprint). These all collapse to "split 10". That's roughly 25+ exemplars hidden behind one helper.

**Gap.** The helper for split 10 cannot pre-position zones — every one of these diagrams has a different topology (tree, spine+branches, horizontal stages, nested rings, hub-with-spokes, vertical stack). "Pre-positioned zones" is exactly what makes the other 9 splits cheap; split 10 has none. You've replaced 19 chassis with 9 splits + a wildcard, and the wildcard is where the build-quality variance will concentrate. This is the same convergence-risk that killed the chassis vocabulary's acceptance rate, just relocated.

**Fix.** Either (a) sub-type split 10 into 3-4 topology helpers — `diagram_tree`, `diagram_spine`, `diagram_radial`, `diagram_stages` — each with real pre-positioned anchors, or (b) admit split 10 is escape-hatch territory and require it to import a topology primitive from a small named set. Don't pretend it's one split with one helper.

### Break 2: RACI / responsibility matrix doesn't fit cleanly

**Case.** RACI is structurally a table with row=task, col=role, cell=R/A/C/I letter. The existing exemplar is i-responsibility-matrix and it lives in the table family.

**Gap.** The proposed ontology says "Table" is a special object for "banded rows with header." RACI is a table by geometry but the cells are semantic glyphs (R/A/C/I or filled circles), not text. If the Table helper assumes "banded rows with header -> text cells" it will produce an unreadable RACI. If you instead force RACI into "Dense grid (2x3 or 3x3)" you've cheated — RACI is routinely 8x5 or 12x6.

**Fix.** Either expand the Table object spec to cover "matrix-style tables with glyph or color cells" (RACI, heatmap i-heatmap, skills matrix i-skills-matrix, traffic-light tracker l-kpi-traffic-light), or add a third special object: **Matrix table** (rows x cols x cell-token). Don't fold this into Dense Grid.

### Break 3: KPI dashboards with inline sparklines / trends

**Case.** l-kpi-with-trend, l-kpi-sparkline, l-kpi-with-bar, l-exec-scorecard. These are "N-column row" or "Dense grid" by geometry but each tile contains a tiny chart.

**Gap.** Hardline rule 1 says "Charts/Tables only in their object layouts." Taken literally, this bans dashboards with sparkline tiles — which is one of the most common executive-summary patterns in consulting. The rule is correct in spirit (don't put a free-floating chart into a 50/50 split) but the literal reading kills a legitimate pattern.

**Fix.** Reword rule 1 to: "Full-canvas charts/tables only appear in Chart/Table object layouts. Inline micro-charts (sparkline, mini-bar, trend arrow) are allowed inside any split as variant decoration on a tile." Otherwise an agent will either break the rule silently or fall back to a worse layout.

### Break 4: Rule 3 (no adjacent same-split) over-triggers on legitimate runs

**Case.** A 6-slide findings section: 6 consecutive "Left rail + body" slides, one per finding, each with the finding number in the rail and detail in the body. This is a deliberate run — the consistency is the point. Rule 3 forces splits 2, 4, 8, 2, 4, 8 or similar variation, which fragments the section visually and forces fake variety.

A second case: a 3-slide before/after sequence ("stacked horizontal rows" three times in a row to show three transformations) — rule 3 blocks it.

**Gap.** Rule 3 is enforcing variety as a proxy for quality, but in a structured run, sameness is the quality signal.

**Fix.** Soften rule 3 to: "Two adjacent slides use the same split only if they belong to a declared section run (`section_run: findings_1_of_6`) or the slide brief explicitly invokes a parallel pattern." A section_run flag is cheap and consultants already think in those terms.

### Break 5: Decision tree, fishbone, Porter's 5 forces — all split 10, all topologically different

**Case.** Decision tree (j-decision-tree) is hierarchical with branching probabilities. Fishbone (j-fishbone) is one central effect with labeled spines. Porter's 5 forces is one central node with five named force-arrows pointing at it. These collapse to "split 10" and inherit the Break-1 problem in a more acute form because each is a textbook framework with a near-canonical geometry.

**Gap.** Same as Break 1, but specifically: agent autonomy on "variant choices (typography, accent, icon, eyebrow)" gives no guidance on whether Porter's 5 forces should be drawn with 5 arrow-callouts around a central box (canonical) or 5 cards in a row (split 5, generic). Autonomy here will produce convergence: every framework will get rendered as the same generic card row because that's the easiest fallback.

**Fix.** Folded into the Break-1 fix. If split 10 is sub-typed, Porter's force-diagram = `diagram_radial`, decision tree = `diagram_tree`, fishbone = `diagram_spine`. Without sub-typing, these will degrade.

## What held

### Hold 1: BCG / 2x2 matrix -> Chart object

**Case.** f-bcg-variant, f-effort-impact, f-prioritization, f-swot.

**Mapping.** Chart object (axes + items in 2D space + takeaway). Clean fit. The matrix-as-chart collapse is the strongest move in the proposal. The fact that BCG, Ansoff, nine-box, SWOT, and effort-impact all share the same geometric primitive (two axes + plotted items + quadrant labels) and were previously 15+ named chassis is exactly the kind of consolidation the ontology should be doing.

### Hold 2: Customer journey (5-stage) -> N-column row

**Case.** j-customer-journey, e3-phase-rows.

**Mapping.** Split 5 (N-column row) for horizontal stage layout, or split 6 (vertical N-row stack) for a portrait variant. Both work. Customer journey is just "stages with sub-content" and N-column handles it as long as the helper supports a per-column eyebrow + body + footer band.

### Hold 3: Gantt / roadmap -> Stacked horizontal rows OR Diagram canvas

**Case.** g-gantt-simple, g-program-roadmap, g-quarterly-plan.

**Mapping.** Stacked horizontal rows (split 9) with a time-axis header. The geometry is one row per workstream, time as horizontal position, bars as accent fills. This works in the new ontology and is actually cleaner than the chassis approach because it forces the agent to commit to "rows of equal height" rather than inventing custom Gantt geometry per slide.

### Hold 4: Recommendation / single-finding / hero KPI -> Full canvas or asymmetric vertical

**Case.** single-finding-v2, recommendation-cta, hero-numeral-divider, b-* family broadly.

**Mapping.** Split 1 (full canvas) or split 3 (asymmetric 25/75). The b-* family of 50+ chassis collapses to maybe 2 splits + variant choices (dark/light, eyebrow on/off, accent number left/right). This is where the ontology earns its keep — these chassis were over-specified.

### Hold 5: Swimlane process -> Stacked horizontal rows

**Case.** g-swimlane.

**Mapping.** Split 9 with a left-rail labels column (or split 8 left-rail + body where body is itself split-9 rows). Works. The "three horizontal bands with a label column" geometry is exactly what split 9 + a labels-rail variant gives you.

## Matrix-as-chart position

**For.** A 2x2 matrix is a chart with discrete-quadrant axes. The plot-and-takeaway pattern is identical. The old Matrix grid chassis encoded the same primitive as the BCG chassis encoded as the Ansoff chassis encoded as the effort-impact chassis — five names, one geometry. Collapsing them all into Chart-object with axis-type=quadrant is the right move and probably the single biggest quality win in this proposal.

**Caveat.** 3x3 matrices (nine-box, GE/McKinsey matrix) need to be explicitly covered — they're chart-with-quadrants but with 3 levels per axis instead of 2. Make sure the Chart object spec parameterizes axis resolution; otherwise agents will render nine-box as a Dense grid and lose the axis semantics. Heatmaps (i-heatmap) are arguably chart-with-quadrants at higher resolution — decide explicitly whether they're Chart or the new Matrix-table object.

## Biggest concern (if ship)

Split 10 ("Diagram canvas") is doing too much work and is the place where the ontology will degrade into "agent invents geometry from scratch" — which is exactly the failure mode the 23% acceptance rate revealed in the chassis approach. The other nine splits give the agent strong constraints; split 10 gives it none. If you ship without sub-typing split 10 into at least `tree`, `spine`, `radial`, and `stages` topology helpers, expect curator acceptance on diagram slides (org charts, fishbones, value chains, Porter's, customer journey maps, hub-spoke ecosystems) to be the new bottleneck and the new excuse for the next ontology rewrite in six months. The fix is small and worth doing before launch, not after.
