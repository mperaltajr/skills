# Layouts reference — 14 patterns + 1 fallback

The authoritative catalog for `slide-builder`. Every per-slide agent reads this file at prompt time and picks **exactly one** pattern per slide.

The pattern is the spec. Within a chosen pattern, the agent has variant autonomy (typography weight, accent placement, icon vs. no-icon, eyebrow vs. no-eyebrow, light vs. dark canvas where applicable). Two seeds drive determinism, both stamped per slide by `build_deck.py`:

- `pattern_pick_seed = md5(content_hash + slide_n)` — breaks ties when multiple patterns score equally for a slide.
- `variant_seed_{A,B,C} = md5(content_hash + slide_n + option_letter)` — drives variant choices within the picked pattern, distinct per A/B/C option.

`content_hash = md5(governing_thought + so_what + evidence_content)` so re-running the same brief reproduces the same picks.

**14 patterns + 1 fallback path:**
- **Splits (9):** pure geometric layouts. The most common shape — most slides land here.
- **Diagram primitives (3):** native python-pptx, rectangles + explicit (x, y) connectors only.
- **Special objects (2):** first-class helpers with their own plumbing (chart, table).
- **Fallback path (1):** HTML→PNG screenshot for curved-container diagrams python-pptx cannot render cleanly.

---

## How to pick

For each slide, score the candidate patterns. Take the highest-scoring pattern. If two or more tie, use the rotation seed to break the tie.

**Signals to look for in the brief:**

| Signal type | Examples |
|---|---|
| **Item count** | "2 paths" / "3 pillars" / "4 phases" / "6 findings" / "single hero stat" |
| **Comparison shape** | "today vs. tomorrow" / "option A vs. B" / "before/after" |
| **Data shape** | "items in 2D" / "KPI scorecard" / "comparison table" / "process with hand-offs" |
| **Visual weight** | "headline finding + evidence" / "dominant statement" / "navigation chrome" |
| **Diagram type** | "hierarchy" / "swimlane" / "decision tree" / "hub-spoke" / "fishbone" |
| **Directive verb** | "recommend X" / "warn against Y" / "diagnose root cause" / "show urgency" / "show progress" / "compare neutrally" / "summarize" — see § "Directive verb vocabulary" below. The verb shapes the variant tilt, not the pattern; but a verb mismatch with the brief means the slide loses its argument. |

If brief and pattern fundamentally disagree (brief enumerates 2 items, slot calls for 4), emit `# SKELETON_REJECTED: <reason>` as the first line of the option script and stop. Do not fabricate to fit. See SKILL.md § "Hardline rules" #5.

> **Load-bearing for the architecture.** This signals table is what agents use to pick patterns. If A/B testing shows agents diverging widely (4+ different patterns picked across 5 parallel agents on the same brief) → revise this section first. Convergence on the same brief (5/5 same pattern) means the signals table is sharp.

---

## Directive verb vocabulary — pick exactly one per slide

A pattern doesn't fully specify a slide. The same pattern can ship two different decks — one that argues a position, one that reads neutral. The agent must identify the **editorial intent** of the slide from the brief, mapped to a **closed 7-verb vocabulary**, and tilt at least one of the three option variants to honor it.

The vocabulary is intentionally bounded. the chassis-vocab regrew uncontrollably when it added "named intents" alongside named chassis; v2 caps the list at 7 verbs and forbids invention. A brief that doesn't map to one of the 7 → `SKELETON_REJECTED: ambiguous editorial intent`. Defaulting to neutral is the failure mode this list exists to prevent.

| Directive verb | Brief signals | Variant tilt direction |
|---|---|---|
| **recommend** | "recommend X", "we propose", "preferred option", "the right answer is", "advise" | Asymmetric weight toward the recommended item — dominant fill, larger type, accent stripe on the recommended option. Not equal weight. Patterns: 50/50 with one side dominant, 75/25 with the recommendation in the anchor, Table with recommended-row indicator. |
| **warn** | "watch out for", "risk of", "danger", "if we don't act", "threat" | High-contrast accent on the threat element. Dark-canvas variant for the threat side. Brand-accent on the consequence, not on the entity being warned about. Patterns: Full canvas (dark), Horizontal bands (light/dark), Top band + body with dark band carrying the warning. |
| **diagnose** | "root cause", "why X is broken", "what's failing", "the issue is", "diagnose" | Analytical breakdown with explicit category labels. No accent winner; categories carry equal weight. Patterns: Vertical N-row stack with category labels, N-column row with diagnostic dimensions, Org chart for hierarchical breakdowns. |
| **show urgency** | "now", "before Q3", "deadline", "must act by", "running out of time" | Bold typography for the timing element. Brand-accent on the date/deadline, not on the body text. Dark-canvas-hero variant for full-canvas slides. Patterns: Full canvas (with hero date/deadline), Top band + body with dark urgency band. |
| **show progress** | "Phase 2 of 4", "next step is", "completed X, now Y", "trajectory", "roadmap" | Directional visual — arrows, accent track between columns, chevron. Brand-accent on the current or next milestone, not on completed/future. Patterns: N-column row with phases, Swimlane with sequential steps, Horizontal bands (past/future). |
| **compare neutrally** | "compare", "evaluate options", "trade-offs", "pros and cons of each", "options" | Equal weight across compared items. No accent winner. Same fill, same typography, parallel structure. Patterns: 50/50, N-column row, Table without recommended-row indicator. The signal that this verb is right is "neutral" appearing explicitly or trade-off framing without a directive lean. |
| **summarize** | "in summary", "the headline finding", "key takeaway", "in one sentence" | Hero claim + supporting brevity. Sparse type as the figure. Patterns: Full canvas (hero claim), Asymmetric 75/25 with hero metric on the anchor side. Body content if present is subordinate to the claim. |

**Rule of one.** Exactly one verb per slide. If two seem to apply (e.g., "recommend" + "show urgency"), pick the dominant one — the one the brief leads with. If you cannot decide between two verbs, that's a brief problem; surface it as a clarification rather than picking both.

**No invention.** If the brief signal doesn't clearly map to one of the 7, do not invent an 8th. Emit `SKELETON_REJECTED: ambiguous editorial intent — brief does not map to {recommend, warn, diagnose, show urgency, show progress, compare neutrally, summarize}`. The closed vocabulary is what prevents v1's chassis-vocab regrowth pattern from coming back here.

**The directive verb shapes the variant tilt, not the pattern.** "Recommend" can ship via 50/50 or 75/25 or Table — what makes it a "recommend" slide is asymmetric weight + accent on the recommended side, regardless of the pattern. The verb is a separate axis from pattern picking. Pick the pattern first (per the signals table above); then identify the verb; then tilt at least one of your three variants to honor the verb.

---

# Splits (9)

## 1 — Full canvas

![Full canvas](../_decisions/gallery/gallery1-full-canvas.png)

A single dominant zone. The slide is one composition — hero claim, statement, divider, or quote — typeset against an unbroken canvas. Asymmetric left-aligned typography breathes against the whitespace and lets the claim land without competing elements. Light canvas is the default; dark canvas (brand-primary fill) is the variant for cover slides, section dividers, and high-emphasis statements.

**Use when:** the brief is one sentence carrying the slide alone · the slide is a section divider or cover · a single dominant quote or claim · a sparse "so what" statement after an evidence-heavy slide.

**Variants:** light vs. dark canvas · counter-line (brand-primary horizontal rule) yes/no · supporting tagline below the claim yes/no · type alignment (left, center).

**Do not use for:** enumerated content (≥2 items) · charts, tables, or diagrams · cases where the brief has supporting evidence that needs to land.

---

## 2 — 50/50 vertical

![50/50 vertical](../_decisions/gallery/gallery2-50-50-vertical.png)

Two equal vertical zones separated by a thin rule. Both sides carry parallel structure — eyebrow + headline + 3–4 bullets each — so the eye reads left-to-right and the comparison emerges from the shape itself. The two side-heads can differ in color (e.g., gray for "current," brand-primary for "after") to telegraph which side is the recommended state without extra graphics.

**Use when:** symmetric compare (today vs. tomorrow, option A vs. option B, current vs. future state) · two parallel concepts with equal editorial weight · brief uses "vs.", "compare", "before/after."

**Variants:** vertical rule yes/no · side-head color contrast (gray/brand-primary, gray/accent, both gray) · bullet style (numerals, dashes, plain) · evidence vs. recommendation framing.

**Do not use for:** asymmetric content (one side dominant) · ≥3 items · single-statement claims · data-heavy comparisons (use Table instead).

---

## 3 — Asymmetric vertical (75/25)

![Asymmetric 75/25](../_decisions/gallery/gallery3-asymmetric-75-25.png)

A dominant content panel and an anchor panel in roughly 75/25 proportion. The anchor panel typically carries a dark brand-primary fill with eyebrow, takeaway, and a hero metric; the content panel sits in light fill with the supporting evidence laid out as cards. The metric on the anchor pairs with the evidence on the body to telegraph the takeaway before the reader processes the supporting detail.

**Use when:** "headline finding + supporting evidence" structure · a hero metric anchoring multiple supporting cards · the brief has one dominant takeaway and 2–4 pieces of evidence.

**Variants:** anchor panel side (left, right) · anchor fill (dark brand-primary, dark gray, light with brand-accent rule) · hero metric size · evidence layout (cards, bullets, mini-table).

**Do not use for:** symmetric comparison (use 50/50 instead) · enumerated lists without a clear anchor takeaway · slides with no quantitative or qualitative hero element.

---

## 4 — Top band + body

![Top band + body](../_decisions/gallery/gallery4-top-band-body.png)

A dark brand-primary band across the top carries the headline finding; the body beneath carries parallel evidence cards. The band is the figure, the cards are the ground. Each card typically has a brand-accent numeral, an evidence statement, and an italic implication.

**Use when:** the brief has one headline + N parallel evidence items (most commonly 3) · executive-summary slides · "we found X. here's why" structure with parallel supporting cards.

**Variants:** band height (full headline weight, compact) · card count (2–4) · numeral style (filled circle, large outline, plain) · italic-implication line yes/no · accent rule above implication yes/no.

**Do not use for:** asymmetric evidence (one piece dominant) · ≥5 evidence items (use Vertical N-row stack or Dense grid) · cases where the headline is the entire slide (use Full canvas).

---

## 5 — N-column row (3–9)

![N-column row](../_decisions/gallery/gallery5-n-column-row.png)

A horizontal row of N columns, each anchored by a number, icon, or label, connected optionally by a brand-accent track. Each column carries: anchor + name + short qualifier (month range, owner, status) + summary + bullets. The shape is parallel: every column has the same elements in the same place.

**Use when:** parallel principles, options, phases, journey stages, or workstreams (3–9 items) · roadmap with sequential phases · multi-option comparison with equal editorial weight · capability inventory.

**Variants:** anchor type (numeral, icon, label-only) · accent track between columns yes/no · column count (3–9; visually 3–6 is the sweet spot) · bullet style · per-column status indicator yes/no.

**Do not use for:** ≤2 items (use 50/50 instead) · items with different shapes (one rich, others sparse) · sequential items that need hand-off arrows between them (use Swimlane instead).

---

## 6 — Vertical N-row stack

![Vertical N-row stack](../_decisions/gallery/gallery6-vertical-n-row-stack.png)

A vertical stack of N anchored rows, each row laid out as: big numeral (or icon) + vertical accent line + heading + body. The card-bg tint keeps rows readable without heavy borders. The shape implies a list with editorial weight rather than a parallel grid.

**Use when:** anchored lists (numerals, icons, labels) · principles, capabilities, or commitments in vertical order · lists where each item needs more body text than fits in an N-column row · 3–6 items.

**Variants:** anchor style (big numeral, icon, label-only, mixed) · accent line yes/no · row tint yes/no · per-row tag/metric yes/no.

**Do not use for:** ≥7 items (becomes a scroll; use Dense grid) · items that compare across attributes (use Table) · items that are sequential with hand-offs (use Swimlane).

---

## 7 — Dense grid (2..5 × 2..5)

![Dense grid](../_decisions/gallery/gallery7-dense-grid.png)

A grid of tiles, 2×2 to 5×5, each tile carrying: label + value + delta with arrow + vs-plan reference + status indicator. Color-coded indicators (green for on-plan, red for watch) are explicit. The densest layout in the catalog and the right shape for any KPI scorecard or dashboard view.

**Use when:** KPI scorecards · dashboard-style summaries · 4+ parallel metrics with the same shape · status-by-domain or status-by-workstream views.

**Variants:** grid dimensions (2×2, 2×3, 2×4, 3×3, etc.) · delta arrow style · status indicator (badge, dot, tile fill) · per-tile sparkline yes/no · tile tint (white, light gray).

**Do not use for:** narrative content (use a split instead) · ≤3 items (use N-column row) · cases where one metric dominates (use Asymmetric 75/25 with hero metric).

---

## 8 — Left rail + body

![Left rail + body](../_decisions/gallery/gallery8-left-rail-body.png)

A narrow dark left rail carries chrome (section letters running vertically, pagination "02 / 05") and the main body carries the slide content — eyebrow, big title, narrative paragraph, vertical metric tiles, optional "so what" band. The rail signals that the slide belongs to a structured section of the deck.

**Use when:** chaptered sections of a longer deck · slides that should signal "this is part 2 of 5" or "DIAGNOSE phase" · structured workstream views where the rail labels the workstream.

**Variants:** rail content (section letters, section name, pagination, mixed) · rail fill (dark brand-primary, dark gray, light with vertical accent) · body tile layout (vertical stack, horizontal row, mixed) · "so what" band at bottom yes/no.

**Do not use for:** unchaptered decks · single-slide standalone content · slides where the rail content would be invented to fit the layout (Hardline Rule #2).

---

## 9 — Horizontal bands

![Horizontal bands](../_decisions/gallery/gallery9-horizontal-bands.png)

Two full-width horizontal rows, typically a light "today" band above and a dark brand-primary "future" band below, separated by a downward arrow or thin rule. Each band carries eyebrow + headline + 3 bullets. The visual contrast between bands carries the before/after argument without needing extra graphics.

**Use when:** before/after structure with editorial weight · evidence/so-what split (evidence on top, so-what beneath) · current-state/future-state contrast · the brief explicitly calls for vertical contrast between two states.

**Variants:** band fill contrast (light/dark, light/light with accent rule, dark/dark with different accents) · arrow vs. rule between bands · band height ratio (equal, top-heavy, bottom-heavy).

**Do not use for:** parallel comparisons without temporal/causal direction (use 50/50 instead) · ≥3 horizontal zones · cases where the two bands carry the same editorial weight in the same direction (use 50/50).

---

# Diagram primitives (3)

Empirically validated as renderable cleanly in native python-pptx. All three use rectangles + explicit (x, y) coordinates for connectors. No curved containers, no auto-routed connectors, no text inside ovals. If the brief calls for any of those, route to the Fallback path instead.

## 10 — Org chart (hierarchical)

![Org chart](../_decisions/diagram-test/diagram1-orgchart.png)

A 3-level hierarchy with rectangles at each level and orthogonal connectors between them. Works for org charts, capability trees, hierarchical breakdowns of a category, taxonomy diagrams. Connectors run vertically from parent to a horizontal trunk, then vertically to each child.

**Use when:** hierarchical structures · org charts · capability/sub-capability trees · taxonomies · breakdown structures.

**Variants:** node fill (white with brand-primary border, brand-primary fill with white text, mixed by level) · root-node emphasis (oversized, accented fill) · per-node metadata (sub-label, owner, count) yes/no.

**Do not use for:** flat networks (use Fallback) · processes (use Swimlane) · branching decisions with conditional logic (use Decision tree).

---

## 11 — Swimlane (cross-functional process)

![Swimlane](../_decisions/diagram-test/diagram2-swimlane.png)

Horizontal lanes representing functions, with sequential steps inside each lane and hand-off arrows between lanes. The shape makes cross-functional process visible — who hands what to whom, in what order. Works for RACI-as-flow, customer journey with handoffs, end-to-end process diagrams.

**Use when:** cross-functional processes · journeys with hand-offs between roles · sequential workflows where the actor matters as much as the step · process diagrams that explicitly call out who does each step.

**Variants:** lane count (2–5) · lane label position (left, top) · step shape (rectangle, rounded rectangle, chevron) · hand-off arrow style (straight, elbow) · per-step duration or status yes/no.

**Do not use for:** sequential processes with a single actor (use N-column row with arrows) · non-sequential content · hierarchies (use Org chart).

---

## 12 — Decision tree (branching)

![Decision tree](../_decisions/diagram-test/diagram4-decisiontree.png)

A root question branches to leaf outcomes through diagonal connectors with edge labels (Yes/No, conditions, criteria). The recommended path can be highlighted via brand-accent fill on the connectors and leaf node. Works for routing rules, qualification logic, eligibility flows.

**Use when:** branching logic with conditions · decision rules · routing/qualification flows · eligibility trees.

**Variants:** branching factor (binary, ternary) · edge label position (on the line, beside the node) · recommended-path highlight yes/no · leaf-node shape (rectangle, rounded, pill).

**Do not use for:** non-branching processes (use Swimlane) · hierarchies without conditions (use Org chart) · networks without a root (use Fallback).

---

# Special objects (2)

First-class helpers with their own plumbing. Hardline Rule #1: charts and tables only appear in these layouts. No fake chart-looking visuals in card grids. Inline sparklines and micro-charts in other layouts are allowed.

## 13 — Chart (with quadrant mode)

![Chart with quadrant mode](../_decisions/gallery/gallery10-chart-quadrant.png)

Axes plus items in 2D space plus a takeaway. The `chart_type` parameter governs the variant: `scatter`, `line`, `bar`, `waterfall`, `donut`, `quadrant`. **Quadrant mode absorbs the old 2×2 matrix** — BCG, Magic Quadrant, Eisenhower, all render here via `quadrants: [name×4]`. The example PNG shows BCG: brand-primary axes, quadrant labels in the four corners, product bubbles at correct fractional coordinates, right-side "Recommended moves" legend.

**Use when:** any 2-axis chart (scatter, line, bar, waterfall, donut) · 2×2 matrix frameworks (BCG, Magic Quadrant, Eisenhower, prioritization matrices) · charts where the data is the slide's center of gravity.

**Variants:** `chart_type` (scatter, line, bar, waterfall, donut, quadrant) · axis labels yes/no · legend position (right, bottom, top-right under sub-headline) · per-item callout pills yes/no · recommended-item emphasis (size, fill, halo).

**Do not use for:** comparison tables (use Table) · pure category lists without 2D positioning · cases where the chart would be invented because the brief has no quantitative data.

**Convention rules:**
- For BCG-style quadrants: STARS top-right, CASH COWS bottom-right, QUESTION MARKS top-left, DOGS bottom-left. Never swap these positions.
- Legends go below the sub-headline (right-aligned) by default; top-right of the chart only when the right side is occupied by a callout.

---

## 14 — Table

![Table](../_decisions/gallery/gallery11-table.png)

Banded rows with a brand-primary header row. Comparison tables, decision matrices, option scoring. The recommended row gets a brand-accent-soft fill plus a left-edge accent stripe. A first column with bold labels anchors the rows; subsequent columns carry the attributes being compared.

For the recommended-row indicator, use an accent stripe — not a stacked badge. See `anti-patterns.md § Chrome / invariants` for the full rule.

**Use when:** comparison tables · decision matrices · option scoring · structured RFP-style comparisons · any content where the cross-product of items × attributes is the story.

**Variants:** column count (3–7) · row count (3–10) · recommended-row indication (accent fill + edge stripe, edge stripe only, no recommendation) · "so what" callout beneath the table yes/no · bold first column yes/no.

**Do not use for:** sparse data better expressed as cards (use N-column row) · 2D positioning (use Chart) · narrative content (use any split).

---

# Fallback path (1) — HTML→PNG screenshot

![Hub-spoke failure example](../_decisions/diagram-test/diagram3-hubspoke.png)

**This is what NOT to build natively.** Text inside circles wraps badly because python-pptx cannot shape-fit text to ovals. For any brief that implies a hub-and-spoke, Porter's Five Forces, fishbone, ecosystem map, or free-form network: the agent emits `SKELETON_REJECTED` for the native path and the build script routes the slide through the HTML→PNG fallback.

**Use when:** hub-and-spoke topologies · Porter's Five Forces · fishbone / cause-and-effect diagrams · ecosystem maps · any free-form network with curved containers and text inside them · concentric ring frameworks.

**Stack (v0):** Mermaid with brand theme overrides. Mermaid covers the entire curved-container failure set with existing syntax and supports CSS-style brand color theming. The agent emits a Mermaid spec; the build script renders it to PNG via headless Mermaid CLI; the PNG is embedded as a full-bleed image on the slide.

**Escalation:** raw HTML + CSS rendered via Playwright, only if Mermaid's brand fidelity is visibly wrong on a real failing brief. Playwright is not on the day-1 ship list.

**Do not use for:** any diagram that one of the three native primitives can carry cleanly (Org chart, Swimlane, Decision tree). The fallback is only for shapes the natives cannot represent.

---

# Picking discipline — the agent's job at prompt time

1. Read the brief content for this slide.
2. Score the 14 patterns against the signals table at the top of this file.
3. Take the highest-scoring pattern. If tied, use the rotation seed.
4. Within the chosen pattern, pick variants from the variant list — the rotation seed picks the variant when multiple are eligible.
5. If brief and pattern fundamentally disagree, emit `# SKELETON_REJECTED: <reason>` and stop. Hardline Rule #5.
6. Build the option script against `slide-builder/twins/helpers.py` for chrome (title block, footer, brand colors) and raw python-pptx + helpers for body geometry.
7. Read `reference/anti-patterns.md` before finalizing the script. The anti-pattern library is the aesthetics layer; the 14 patterns above are the structure layer.

**Adjacency rule:** Hardline Rule #3 forbids 3+ consecutive slides on the same split. Two in a row is allowed. The rotation seed handles this automatically when computed per-slide; agents do not need to track it explicitly, but should flag if their picked pattern matches the previous two slides' patterns (visible from the dispatch plan).

---

# What is not in this file

- **Build mechanics** (how to invoke `twins/helpers.py`, how to write a python-pptx option script): in `prompt.md`.
- **Aesthetics rules** (don't use accent bars on every slide, don't put low-contrast text on dark fill, etc.): in `reference/anti-patterns.md`.
- **The 5 hardline rules:** in `SKILL.md § "Hardline rules (5)"`.
- **The fallback renderer implementation:** in `scripts/build_deck.py` (Mermaid CLI invocation) and the agent prompt template.

---

# Source

This catalog is the locked output of the v2 architecture session. The empirical validation (11 of 11 gallery PNGs shippable, 3 of 4 diagrams shippable natively, 1 fallback case identified) lives at:

```
C:\Users\m.a.peralta\.claude\skills\slide-builder\_decisions\DECISIONS.md
C:\Users\m.a.peralta\.claude\skills\slide-builder\_decisions\GALLERY.html
C:\Users\m.a.peralta\.claude\skills\slide-builder\_decisions\gallery\GALLERY-NOTES.md
```

The PNGs in this file are the gallery PNGs from those sessions. They are referenced relative-path so the file is portable.
