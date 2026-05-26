# Ontology Challenge - Agent 3

## Verdict

**SHIP IT WITH FIXES.**

The 10-split chassis collapse is directionally correct - 19 chassis + adjacency graph + content tags + list[1..2] + Layer 5 + 7-tag matrix was a curator-comprehensibility disaster at 23% acceptance, and most of that machinery was paying rent in agent-time, not slide quality. But the proposed 10 splits as written have at least three real holes (process/flow, swimlane/Gantt, and decision-tree/org-chart) that "Diagram canvas" alone cannot absorb without becoming the same Layer-5 dumping ground we just deleted. The Matrix-as-Chart collapse is honest IF the Chart object has axes-as-first-class - but the proposal as written doesn't say it does. Fix those three things and ship.

---

## What I tried

I ran 13 consulting slide concepts through the 10-split + 2-object grid: org chart, RACI, Gantt, swimlane, Porter's 5 forces, value chain, customer journey, KPI dashboard, BCG matrix, Kano, decision tree, SWOT, McKinsey 7S. I also pulled the actual current `exemplars/do/` directory (490 leaves) and bucketed each one against a split to find the dead-zones. I stress-tested rule 3 (no adjacent same-split) against three realistic 12-slide consulting decks - diagnostic, strategy, transformation roadmap - to see where it over-fires.

---

## What broke

### 1. Process / flow / arrow chain (Gantt, swimlane, value chain, journey)

**Case:** "Order-to-cash value stream - five steps left to right with handoff arrows between steps, each step has 2 sub-bullets and an owner pill underneath."

**Gap:** None of the 10 splits hold this. "N-column row (3-6)" is the closest, but columns are *parallel*, not *sequential* - there are no arrows, no handoff semantics, no temporal axis. "Diagram canvas (open-zone)" technically holds it, but that's where the proposal puts everything it doesn't want to think about, which is the Layer-5 trap we just escaped. The current `G-family` has 30+ variants for a reason: process flow / Gantt / swimlane / roadmap each have distinct geometric constraints (Gantt has a time axis at top, swimlane has horizontal lanes, process flow has connectors).

**Fix:** Add an **11th split: Sequence canvas** - a horizontal- or vertical-axis open zone with a time/order axis primitive and a pre-positioned connector layer. Or: promote "Stacked horizontal rows" to take an optional `axis: time` parameter and turn it into the swimlane host. Without one of these, Gantt and swimlane fall into "Diagram canvas" and the agent has to fabricate the entire connector geometry every time - that's exactly what failed in the chassis vocab.

### 2. Org chart / decision tree / hierarchy

**Case:** "Org chart of post-merger leadership: 1 CEO box -> 4 direct reports -> 11 leaf nodes, color-coded by legacy entity."

**Gap:** "Diagram canvas (open-zone)" again. The proposal treats hierarchy as "the agent figures it out" - but the agent has nothing to anchor on. Current `J-family` has `j-dark-org-chart`, `j-portfolio-tree`, `j-hub-spoke`, `j-target-diagram`, `j-bow-tie`, `j-cycle` - these are not stylistic variants, they are different topologies. Collapsing all of them into one open canvas means the agent autonomy variants (typography, accent, icon, numeral, eyebrow) can't make any of them, because none of them are *typographic* variants - they're *graph topology* variants.

**Fix:** Either (a) keep a thin **Diagram primitives library** as a third special object alongside Chart and Table - `tree`, `cycle`, `hub-spoke`, `flow` - each with pre-built layout helpers in `helpers.py`, or (b) bite the bullet and accept that any slide whose meaning is a graph topology needs a named helper and exit the "10 splits cover everything" framing. Hand-waving "Diagram canvas" at a 14-node org chart is just relocating the problem.

### 3. Rule 3 (no adjacent same-split) over-fires on diagnostic decks

**Case:** A 12-slide diagnostic deck I sketched against this rule: cover, agenda divider, then 6 finding slides each with the same skeleton (anchor finding statement + 3 supporting columns) = same split each time (Asymmetric vertical 75/25 or Left rail + body, depending on read). Then a 2x2 SWOT, then a roadmap, then recommendations, then back cover.

**Gap:** Rule 3 fires 5 times in the finding section. The agent will start *manufacturing* split changes to satisfy the rule - alternating Left rail + body with Asymmetric vertical 75/25 for slides that should all be the same skeleton because **consistency is the point** in a finding section. This is the same failure mode as the old "deadlock audit": a global rule punishing a locally-correct choice.

**Fix:** Scope rule 3 to **transitions between deck sections** (cover->body, body->divider, body->close), not slide-to-slide. Or: make it a *soft* lint (warn the curator) not a *hard* rule. Or: explicit override - if the brief carries a `section: parallel-findings` tag, suppress rule 3 within that run.

### 4. Special objects: Chart absorbs Matrix - but only honestly if axes are first-class

**Case:** BCG 2x2 (market growth x relative share, 6 business units placed as bubbles). Then Kano (satisfaction x functionality, items placed as labeled points). Then SWOT (no axes - just 4 named quadrants).

**Gap:** BCG and Kano *are* charts (continuous axes, plotted items) and the collapse works. **SWOT is not** - its quadrants are categorical labels, not axis intervals. Same for risk/likelihood heatmaps when they're labeled "Low/Med/High" rather than plotted on a continuous scale. If Chart-object assumes `x-axis + y-axis + items`, SWOT breaks the schema. If Chart-object allows "categorical axes," it has just re-invented the Matrix chassis under a new name.

**Fix:** Either (a) admit Chart has two modes - `continuous-axes` and `categorical-quadrants` - and document both, or (b) keep a Matrix special object after all and accept 3 specials not 2. Don't paper over this by saying "categorical is a sub-mode of axis" without writing it down - that's how we ended up with 489 chassis slugs.

### 5. Migration: chassis that don't map cleanly

I pulled the current 490 do/ exemplars and tried to bucket each. Cleanly mapping (>=85%): the cover/divider/back-cover (60+ leaves -> "Full canvas"), b-* singles (50+ -> "Full canvas" with text-only variant), c-* lists (40+ -> "Stacked horizontal rows" or "Vertical N-row stack"), d* columns (40+ -> "N-column row 3-6" or "Asymmetric vertical 75/25" for anchor), e* rows (40+ -> "Stacked horizontal rows"), h* charts (25+ -> Chart object), l* KPI (40+ -> "Dense grid 2x3 or 3x3"), i* tables (40+ -> Table object). **That is ~85% clean.**

**The other ~15% does not map cleanly:**
- **g* sequence/timeline/Gantt (30+ leaves)** - covered in break #1
- **j* diagrams (25+ leaves)** - covered in break #2
- **f* matrix (40+ leaves)** - partial; BCG-style cleanly to Chart, SWOT-style needs break #4 resolution
- **2panel-convergence, 2panel-delta-spine, hero-numeral-divider, dark-hero-foil** - special compositional flourishes that aren't really splits, they're decorative variants. These are fine; absorb into autonomy variants.

So ~110-150 exemplars require either a new split, a new helper, or a documented "Diagram canvas with X primitive" mapping.

---

## What held

### Cover / divider / back-cover -> Full canvas
60+ leaves, all collapse cleanly. Autonomy variants (typography, accent, numeral, eyebrow) cover the styling axis. The proposal genuinely deletes a lot of redundant chassis here with no information loss.

### Single-focus statement (B-family) -> Full canvas
50+ "one big number / one quote / one claim" exemplars all reduce to Full canvas + autonomy. Killing `b-bold-claim`, `b-hero-finding`, `b-key-number`, `b-pull-quote`, `b-tldr` as separate chassis is correct - they were typographic variants of the same skeleton.

### Bullet lists / stacked findings -> Vertical N-row stack or Stacked horizontal rows
Clean mapping. The current C-family's 40+ variants are mostly "what's the body content" not "what's the geometry" - collapsing them is correct.

### KPI tiles -> Dense grid (2x3 or 3x3)
40+ L-family exemplars all reduce. Tile-count parameter handles 3 vs 6 vs 9. Clean.

### Anchor + supporting cards -> Asymmetric vertical (75/25) or Left rail + body
The d0-* and anchor-with-cards exemplars collapse cleanly. This was over-cataloged in the current taxonomy.

### Chart slides -> Chart special object
H-family's 25+ variants compress to one Chart object with parameters (chart-type, takeaway-position). The current `takeaway-position` tag becomes a Chart parameter - clean migration.

---

## Matrix-as-Chart position

**Honest IF the Chart object explicitly supports categorical axes; otherwise it is a paper-over.**

The collapse works for BCG, Kano, Ansoff, growth-share, scatter, bubble - anything with continuous (or pseudo-continuous) axes and plotted items. It does not work for SWOT, risk-likelihood-with-named-cells, Pugh, prioritization-matrix-with-labels - these have **named categorical quadrants** and the "items" don't sit at coordinates, they sit *inside named cells* as text lists.

If the proposal's Chart object treats categorical-quadrant matrices as a Chart sub-mode, write that down explicitly: `Chart.mode = {continuous, categorical}`, with `categorical` rendering as labeled quadrant cells holding text-list items. That is honest collapse. If the proposal silently assumes "Chart handles all matrices" without saying how categorical labels render, that is paper-over, and SWOT will fail at the first real engagement deck.

The current F-family's 40+ variants are *not* all distinct skeletons - most are content-tagged 2x2s (`f-effort-impact`, `f-value-complexity`, `f-urgency-importance`, `f-risk-likelihood` are the *same* 2x2 with different axis labels). Collapsing them is correct. But the schema needs to handle both the continuous and categorical modes.

---

## Biggest concern (if ship)

**"Diagram canvas (open-zone)" becomes the new Layer 5.**

Layer 5 in the current chassis system was the dumping ground for everything that didn't fit - the "agent figures it out" escape hatch - and it had the worst curator acceptance. "Diagram canvas (open-zone)" is structurally identical: no pre-positioned zones, no helper geometry, no constraints, the agent fabricates the whole layout. If org-chart, decision-tree, value-chain, swimlane, process-flow, and "anything weird" all route to Diagram canvas, this single split will carry 15-20% of all slide briefs and will fail at the same rate Layer 5 did.

**Mitigation:** ship Diagram canvas with **3-4 named primitives baked into `helpers.py`** - `tree(nodes, edges)`, `flow(steps, connectors)`, `cycle(nodes)`, `hub_spoke(center, spokes)`. The "split" is still Diagram canvas, but the agent picks a primitive at build time, and the primitive owns the geometry. Without that, you are shipping the same trap with fewer ingredients.

**Secondary concern:** the autonomy-variant axis (typography, accent, icon, numeral, eyebrow) is going to **converge** across agent runs. All five autonomy variants will tend toward the prettiest one (whichever the model prefers stylistically), which means after 30 builds you will have 30 slides with the same accent treatment. The chassis vocab at least *named* the variants and forced selection. Mitigation: rotate autonomy variants deterministically per slide index, or pin per-deck.

---

## Bottom line

Ship the 10 splits, ship the Chart and Table objects, kill the chassis vocab and content tags - all correct. But: (a) add a sequence/flow primitive or 11th split, (b) bake 3-4 diagram primitives into `helpers.py` for Diagram canvas, (c) document Chart's categorical mode explicitly, (d) scope rule 3 to section transitions not slide-to-slide, (e) deterministically rotate autonomy variants to prevent stylistic convergence. With those five fixes, curator acceptance moves from 23% to plausibly 60-70%. Without them, you will be back here in two months arguing about whether "Diagram canvas v2" should be split into seven sub-canvases.
