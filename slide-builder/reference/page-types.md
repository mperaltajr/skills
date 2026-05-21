# Page Types Catalog

This document catalogs every page type the pipeline supports. Each entry uses a consistent schema so the model can reliably select the right type:

- **Purpose** — what this page type is for
- **When to use** — signals that indicate this type fits the content
- **Headline rule** — what the action title must do for this type (including any exceptions)
- **Structure** — the required argumentative structure
- **Visual** — what visual treatment is standard
- **Layout variants** — the 2-7 common layouts used for this type
- **Reference** — which reference PDF holds reference examples
- **Red flags** — common failure patterns to avoid

Pairs with `rules.md` (universal rules) and `glossary.md` (zone terminology). Universal rules apply to every page type except where this document notes an explicit exception.

---

## Page Type Index

1. [Insight / Finding](#1-insight--finding)
2. [Recommendation](#2-recommendation)
3. [Status Update](#3-status-update)
4. [Process / How](#4-process--how)
5. [Data Deep-Dive](#5-data-deep-dive)
6. [Comparison](#6-comparison)
7. [Executive Summary](#7-executive-summary)
8. [Visual Model](#8-visual-model)
9. [Conceptual — Divider / Transition](#9-conceptual--divider--transition)
10. [Conceptual — Quote](#10-conceptual--quote)
11. [Conceptual — Analytical Framework](#11-conceptual--analytical-framework)
12. [Conceptual — Full-Bleed Image / Statement](#12-conceptual--full-bleed-image--statement)
13. [Text, Trends & Insight](#13-text-trends--insight)
14. [Competitive & Market Analysis](#14-competitive--market-analysis)
15. [Roadmap & Timeline](#15-roadmap--timeline)
16. [Org Chart, Team & Governance](#16-org-chart-team--governance)

**Not handled as insight-generation page types** — see [PMO — Handled as Template Fill-In, Not Insight Generation](#pmo--handled-as-template-fill-in-not-insight-generation) at the end of this document.

---

## Reference Group Index

Every page-type entry below names one or more reference groups. The groups live as PDFs in `~/.claude/skills/references/`:

| Group | Name | Teaches |
|---|---|---|
| reference group 01 | Executive Summary and Storyline | Single-slide deck summaries |
| reference group 02 | Bar and Column Charts | Ranked comparisons, grouped bars, waterfalls |
| reference group 03 | Line, Scatter and Bubble Charts | Trends, scenarios, correlations |
| reference group 04 | Competitive and Market Analysis | Competitor tables, positioning scatters |
| reference group 05 | Strategic Frameworks | Established analytical frameworks (SWOT, Porter's, etc.) |
| reference group 06 | Process and Journey Maps | Directional flows, sequential steps |
| reference group 07 | Roadmaps and Timelines | Time-based phases, Gantt charts |
| reference group 08 | Structured Text Layouts | Text with icon anchors, parallel items |
| reference group 09 | Cover, Divider and Navigation | Conceptual pages |
| reference group 10 | Org Charts, Teams and Governance | People and structure patterns |
| reference group 11 | Visual Models and Narrative Shapes | Pyramids, cycles, 2x2s, hub-and-spoke |
| reference group 12 | KPI Tiles and Dashboards | At-a-glance metrics, tile layouts, dashboard-style summaries |

---

## 1. Insight / Finding

**Purpose:** Communicate a single, evidence-backed finding that changes how the audience understands the situation.

**When to use:**
- Presenting an analysis result that reframes the audience's understanding
- Surfacing a non-obvious pattern in data
- Landing a fact that drives a subsequent recommendation

**Headline rule:** State the insight as a conclusion, not a topic.
- Bad: *"Customer churn analysis"*
- Good: *"Churn is concentrated in the 0-90 day cohort — retention efforts after 90 days have negligible ROI"*

**Structure:**
- Lead with the chart or visual — insight pages are evidence-first
- Supporting bullets (max 3) explain *why* the insight holds, not *what* the chart shows
- Caveats or limitations go in a footnote, not in body copy

**Visual:**
- One primary chart — bar, line, scatter, or waterfall depending on the story
- Annotate the chart directly to call out the key data point that proves the headline
- Avoid pie charts — they obscure magnitude and rank

**Layout variants:**
- A: Chart-dominant, right takeaway panel (65/35 split)
- B: Full-width chart, inline callout annotation
- C: Hero stat + supporting chart
- D: Data table with highlighted rows (when precision matters more than pattern)

**Reference:** `02_Bar Charts.pdf`, `03_Line Scatter Charts.pdf`

**Red flags:**
- Action title describes the chart instead of drawing a conclusion → rewrite
- More than one chart on the page → split or pick the stronger one
- Supporting bullets repeat what the chart already shows → cut them

---

## 2. Recommendation

**Purpose:** Drive a decision. The audience leaves knowing exactly what is being recommended and why.

**When to use:**
- Closing out an analysis with a proposed action
- Asking for a go/no-go decision
- Proposing a choice between options

**Headline rule:** State the recommended action directly.
- Bad: *"Options for go-to-market strategy"*
- Good: *"We recommend a direct sales model in Tier 1 cities before expanding channel partnerships"*

**Structure:**
- **Recommendation** (the what) — clearly stated, unambiguous
- **Rationale** (the why) — 2-3 reasons, each one sentence
- **Risks / mitigations** (the so what if wrong) — 1-2 key risks with a mitigation for each
- Optionally: alternatives considered and why rejected

**Visual:**
- Decision matrix, pros/cons comparison, or a simple 3-box structure (Recommend / Rationale / Risks)
- Avoid complex charts — this page is about clarity of argument, not data density

**Layout variants:**
- A: Findings + Recommendations two-panel
- B: Recommendation + Rationale + Risks three-box
- C: Challenges + Solutions rows
- D: Decision matrix with highlighted winner

**Reference:** `08_Structured Text.pdf`

**Red flags:**
- Recommendation is hedged (*"we suggest considering..."*) → make it direct or flag it as a hypothesis
- No risks acknowledged → audience will distrust the recommendation
- More than one recommendation on the page → split

---

## 3. Status Update

**Purpose:** Give a clear, honest picture of where things stand against plan.

**When to use:**
- Periodic project reporting
- Checkpoint reviews with sponsors
- Escalating issues to steering

**Headline rule:** State the overall status as a conclusion.
- Bad: *"Project status as of Q3"*
- Good: *"Project is on track overall; procurement delay is the only risk to the timeline"*

**Structure:**
- RAG (Red / Amber / Green) status indicators for each workstream — never omit reds
- Progress vs. plan for each workstream (% complete, milestone hit/missed)
- Next steps or actions required, with owner and due date
- Escalation items clearly flagged — if something needs a decision, say so explicitly

**Visual:**
- Timeline or Gantt for schedule-heavy updates
- RAG table for multi-workstream projects
- Scannable — a senior leader should absorb status in under 30 seconds

**Layout variants:**
- A: RAG table by workstream
- B: Gantt tracker with RAG overlay
- C: Milestone summary with dates
- D: Immediate next steps list

**Reference:** `07_Roadmaps.pdf`

**Red flags:**
- All RAG indicators are green → credibility problem; push for honest assessment
- No owners or dates on next steps → actions won't happen
- Milestone descriptions are vague (*"work in progress"*) → be specific

---

## 4. Process / How

**Purpose:** Show how something works, how to do something, or how a system or workflow is structured.

**When to use:**
- Explaining a workflow or methodology
- Showing a phased approach
- Describing a customer journey or operational sequence

**Headline rule:** State what the process achieves or why it matters.
- Bad: *"Onboarding process overview"*
- Good: *"A streamlined 4-step onboarding cuts time-to-productivity from 6 weeks to 3"*

**Structure:**
- Sequential steps with clear, action-oriented labels (verb-first: *"Assess," "Design," "Deploy"*)
- Maximum 6-7 steps — if more, group into phases
- Each step should include: what happens, who owns it, and how long (if relevant)
- Decision points or branches clearly marked

**Visual:**
- Left-to-right flow diagram or numbered step layout
- Swimlanes when multiple teams are involved
- Icons help orient but must be consistent and purposeful (style-locked per slide)

**Layout variants:**
- A: Linear arrow flow
- B: Chevron phase blocks
- C: Customer journey swimlane
- D: Before / now / future three-state

**Reference:** `06_Process Journey.pdf`

**Red flags:**
- Steps are passive or noun-based (*"Assessment phase"*) → rewrite as actions
- More than 7 steps without grouping → collapse into phases
- Missing owners on a process that involves multiple teams → add swimlanes

---

## 5. Data Deep-Dive

**Purpose:** Present detailed data for an analytically sophisticated audience that needs to interrogate the numbers.

**When to use:**
- Audience is analyst-level and wants to see the data, not just a summary
- Multiple segments or cuts need to be shown simultaneously
- The data itself will be referenced in discussion

**Headline rule:** Even data-heavy slides need a governing thought.
- Bad: *"Revenue breakdown by segment, channel, and geography"*
- Good: *"Direct channel in APAC is the highest-margin segment across all geographies — 3x the company average"*

**Structure:**
- Primary chart or table carries the data
- Annotations on the chart call out the 2-3 most important data points
- Brief methodology note if the data source or calculation is non-obvious
- Footnotes for definitions, exclusions, or caveats

**Visual:**
- Chart type must match the story: waterfall for composition/change, line for trend, bar for comparison, scatter for correlation
- Tables acceptable if the audience needs specific numbers — but highlight the key cells
- Never 3D charts — they distort magnitude

**Layout variants:**
- A: Comparison bars, dominant
- B: Trend line, dominant
- C: Data table with highlighted rows
- D: Chart + accompanying table

**Reference:** `02_Bar Charts.pdf`, `03_Line Scatter Charts.pdf`, `12_KPIs and Dashboards.pdf`

**Red flags:**
- No action title insight → audience draws its own (possibly wrong) conclusion
- Chart type doesn't match the story → change it
- Too many data series on one chart → split or simplify
- No source citation → data loses credibility

---

## 6. Comparison

**Purpose:** Help the audience evaluate two or more options, approaches, or scenarios against each other.

**When to use:**
- Presenting alternatives for a decision
- Benchmarking against competitors
- Showing trade-offs between strategies

**Headline rule:** State the conclusion of the comparison, not just that a comparison exists.
- Bad: *"Option A vs. Option B"*
- Good: *"Option B delivers 2x the margin at comparable risk — it is the stronger path forward"*

**Structure:**
- Consistent criteria applied to all options — never compare on criteria that only favor one side
- Highlight the winner or preferred option visually (bold border, accent color, checkmark)
- Include a "basis of comparison" note if criteria weighting is non-obvious

**Visual:**
- Side-by-side columns or a structured comparison matrix
- Icons or RAG indicators for quick orientation
- Avoid prose paragraphs for each option — keep it scannable

**Layout variants:**
- A: Competitor table with Harvey Ball indicators
- B: Competitor table with inline bar charts
- C: Positioning scatter with quadrants
- D: Value-prop dot-line chart

**Reference:** `04_Competitive Analysis.pdf`

**Red flags:**
- Criteria cherry-picked to favor one option → add balanced criteria or flag the bias
- No clear winner identified → force a conclusion or explicitly state *"this is a decision for the client"*
- Too many options (4+) → narrow to the 2-3 most credible

---

## 7. Executive Summary

**Purpose:** Frame the full narrative of a deck in a single slide. Used at the opening of every engagement. The audience should understand the full story — context, findings, recommendation — without reading any other slide.

**When to use:**
- First slide of a deck
- When a deck needs to stand alone if only one slide is read
- Senior audiences who may only read page 1

**Headline rule:** **Exception to universal rules** — a descriptive label (*"Executive summary"*) is acceptable because the content itself carries the argument.

**Structure:**
- All columns and panels must stretch to equal height — never leave one column short while another is full
- The body itself must pass the title-only test for the deck — if you read only the bolded takeaways, the argument must hold

**Visual:**
- Text-led with structured visual framework
- Bold headers for each takeaway or section

**Layout variants:**
- A: Paragraph — 3-4 short paragraphs, each opening with the key point in bold (best when the narrative is sequential)
- B: Bold headline + 3-bullet supporting structure per takeaway (best when takeaways are independent and MECE)
- C: 4-column dark card takeaway headers with supporting bullets below (best for high-level strategic summaries with 4 themes)
- D: 3-column Background / Findings / Recommendation (best for project kickoff or situation framing)
- E: Findings table left, contents index right (best when the deck needs both summary and navigation)

**Reference:** `01_Executive Summary.pdf`

**Red flags:**
- Executive summary is just a list of slide titles → it's not doing work
- One panel is empty while another is full → redistribute content
- No recommendation visible → the audience will miss the "ask"

---

## 8. Visual Model

**Inherits chassis layout:** `full-section`. The model shape lives inside the body. Visual Model is a **page-type** (a content recipe), not a chassis layout. See `glossary.md` section 4 for the eight chassis layouts.

**Purpose:** Communicate an argument through a visual shape rather than through structured data or text alone. The shape *is* the argument — a pyramid says "these are stages that build on each other," a cycle says "these repeat and reinforce," a 2x2 says "these are trade-off quadrants." Slide Designer treats Visual Model as a first-class peer of other page types, not a sub-type of Conceptual.

**When to use — the three-signal trigger:**

The model detects Visual Model based on three signals in the structured brief. If **all three fire**, one of the 3 design options must be a Visual Model variant. If **two fire**, Visual Model is optional. If **zero or one fires**, do not include Visual Model.

1. **Shape-words in the governing thought or supporting structure** — stages, levels, phases, horizons, loops, cycles, pillars, forces, tiers, steps (when parallel), layers, spectrum
2. **Supporting structure is parallel and countable** — the 2-5 buckets are equally weighted, the consultant thinks of them as "the five things" rather than "one main thing plus four caveats"
3. **No data / no chart needed** — if data is secondary context, this signal fires; if the slide is chart-dominant, it does not

**Headline rule:** Standard action title applies. The model is the body of the slide — it must still be anchored by a title that tells the audience what the model means or why it matters.
- Acceptable: *"Our value creation model operates across three interdependent horizons"*
- Not acceptable: *"Value creation model"* (label only — too passive)

**Structure:**
- The model shape lives inside the body of a `full-section` chassis layout (full-width body, no takeaway panel)
- The shape dominates the body (60-75% of body real estate)
- Labels within the model are minimal — names and short descriptors only, not full sentences
- Optional: a brief explanatory note per element if the concept needs unpacking for this audience
- If the slide needs a "so what" strip, use `chart-with-bottom-takeaway` chassis instead — the takeaway-bottom-strip carries the implication, the body holds the model

**Visual:**
- Shape must be purposeful — the shape itself reinforces the concept
- Consistent icon, color, and size treatment across all elements
- Minimal decorative complexity — the model should be immediately interpretable

**Shape sub-taxonomy:**

| Relationship in content | Shape | Reference |
|---|---|---|
| Sequential, parallel-weighted | 5-circle horizontal, numbered columns, chevron steps | `11_Visual Models.pdf` |
| Hierarchical, ascending | Pyramid, stacked layers, maturity model | `11_Visual Models.pdf` |
| Cyclical, self-reinforcing | Circular flow, flywheel, closed loop | `11_Visual Models.pdf` |
| Branching, decision-driven | Tree, decision flow, cascade | `05_Frameworks.pdf`, `reference group 11` |
| Opposing, trade-off | 2x2, spectrum, polarity map | `reference group 05`, `reference group 11` |
| Central with satellites | Hub-and-spoke, wheel, orbit | `10_Org Charts Team Governance.pdf`, `reference group 11` |

**Shape rationale is mandatory.** Every Visual Model option in the design spec must include a one-sentence rationale: *why does this specific shape match the relationship in the content?* If the rationale is weak, pick a different shape.

**Design lies to avoid:**
- A pyramid for non-ascending content is a lie
- A cycle for a one-way process is a lie
- A 2x2 for content without a trade-off is a lie
- A hub-and-spoke when the "spokes" aren't actually related to the hub is a lie

Every shape carries meaning. The consultant should walk away from the slide understanding *why this shape fits this content*, which is also the key teaching moment in the Coaching Note.

**Rules relaxations:**
- Two-font-size rule relaxed — model labels, element descriptors, and title are naturally three sizes; 9pt floor still applies
- Legend required only if colors encode distinct meaning across elements; not required for purely structural color (alternating shades)
- Source/footnote: include if the model is sourced from a third party; omit if original

**Reference:** `11_Visual Models.pdf` primarily; specific shapes also in `reference group 05`, `reference group 06`, `reference group 10`.

**Red flags:**
- Shape doesn't match the relationship in the content → pick a different shape
- Too many elements in the model (>7) → simplify or split across two slides
- Text inside model elements too small to read → reduce elements or scale up (floor: 9pt)
- Title is a label rather than a statement of meaning → rewrite

---

## 9. Conceptual — Divider / Transition

**Purpose:** Create a moment of pause or emphasis in a deck — a tonal shift before or after dense content, or a transition between major sections.

**When to use:**
- Between major sections of a deck
- Before a high-stakes recommendation
- To signal a shift in subject matter

**Headline rule:** **Exception to universal rules** — no action title required. A single bold word, short phrase, or section label is the only text needed. The visual carries the moment.

**Structure:**
- One dominant visual element — full colored background, gradient, or large abstract image
- Single centered word or short phrase (*"Opportunity," "The Challenge," "What's Next"*)
- No body content, no bullets, no supporting structure

**Visual:**
- Full-bleed background — solid color, gradient, or abstract image
- High contrast between text and background
- Typography as design element — oversized, bold, centered

**Rules relaxations:**
- No action title required
- No source/footnote required
- No page number required (optional — follow deck convention)
- Two-font-size rule suspended — typography is the visual
- No legend required

**Layout variants:**
- A: Full-bleed solid color with centered word
- B: Full-bleed gradient with centered phrase
- C: Large typographic numeral with section name
- D: Abstract image with overlaid phrase

**Reference:** `09_Cover Divider.pdf`

**Usage guidance:** one divider per major section transition — no more.

---

## 10. Conceptual — Quote

**Purpose:** Feature a quote that sets context or reinforces the narrative. Carries emotional or authoritative weight that the consultant's own words cannot.

**When to use:**
- Opening a section with an authoritative voice
- Reinforcing a finding with customer or expert testimony
- Providing a moment of pause in a dense deck

**Headline rule:** **Exception to universal rules** — no action title. The quote itself is the content. Attribution replaces the source/footnote.

**Structure:**
- The quote — large, prominent, typographically treated
- Attribution — speaker name and context (*"— Satya Nadella, CEO, Microsoft"*) in smaller muted text below or beside the quote
- Optional: a one-line framing sentence above or below if the quote needs context (*"Our clients are telling us the same thing:"*)

**Visual:**
- Typography-led — the quote treatment IS the visual
- Optional: background image reinforcing the quote's tone (used sparingly — must not compete with readability)
- Quotation marks as visual device acceptable if purposeful

**Rules relaxations:**
- No action title
- Attribution replaces source/footnote
- No data, no charts, no legend required
- Two-font-size rule suspended

**Layout variants:**
- A: Large quote, centered, attribution below
- B: Quote left, photo of speaker right
- C: Full-bleed background image with overlaid quote
- D: Pull-quote style with accent color bar

**Reference:** `09_Cover Divider.pdf`

**Red flags:**
- Quote too long to be impactful → trim or pull excerpt
- Attribution missing → always credit
- Background image makes quote hard to read → increase contrast or remove image

**Usage guidance:** 1-2 quote slides per deck maximum.

---

## 11. Conceptual — Analytical Framework

**Purpose:** Present an established analytical framework (Porter's Five Forces, SWOT, Strategy House, BCG Matrix) with the consultant's content mapped to it. Different from Visual Model (Section 8) — analytical frameworks have external conventions the audience already knows; visual models are narrative shapes invented for this specific content.

**When to use:**
- The audience is familiar with the framework and expects to see it
- The framework's established structure does the work of explaining the analysis
- You want to demonstrate analytical rigor through recognized methodology

**Headline rule:** Standard action title applies. The framework is the body — it must be anchored by a title that tells the audience what the framework reveals about their specific situation.
- Acceptable: *"Porter's analysis shows supplier power is the dominant threat to margins"*
- Not acceptable: *"Porter's Five Forces for [Client]"* (label only)
- **Sub-exception:** if the framework is used as a reference tool (not to reach a conclusion), a descriptive title is acceptable — but this is rare

**Structure:**
- Framework structure dominates (established form — don't reinvent)
- Content maps to framework slots
- Brief insight note per slot where relevant

**Visual:**
- Use the framework's canonical visual representation
- Don't stylize heavily — audiences recognize the framework by its shape
- Highlight the most relevant slot visually (color or border)

**Layout variants:**
- A: SWOT 2x2 quadrants
- B: Porter's Five Forces diagram
- C: Strategy House with pillars
- D: BCG Matrix (growth/share)

**Reference:** `05_Frameworks.pdf`

**Rules relaxations:**
- Two-font-size rule relaxed — framework labels, element descriptors, and title are naturally three sizes; 9pt floor still applies
- Source/footnote: include if framework is sourced from a third party; omit if original

**Red flags:**
- Consultant invents a "new framework" that looks analytical but isn't → this is Visual Model (Section 8), not Analytical Framework
- Framework used as a label with no conclusion drawn → the title needs to state what the framework reveals
- Content forced into framework slots where it doesn't fit → pick a different framework or use a Visual Model

---

## 12. Conceptual — Full-Bleed Image / Statement

**Purpose:** Land a single emotional or aspirational message using a dominant image and a bold statement. Used at opening, closing, or a pivot moment.

**When to use:**
- Deck opening (cover)
- Deck closing (call to action)
- A single pivot moment where tone must shift dramatically

**Headline rule:** **Exception to universal rules** — a single bold statement is acceptable; it does not need to follow the action title format. The statement and image work together to land one emotional message.
- Acceptable: *"Innovative," "The future is already here," "We need to move differently"*
- Not acceptable: a structured action title reading like an insight headline — that belongs on a structured content slide

**Structure:**
- Large background image (full-bleed or dominant portion of slide)
- Single bold word or short statement overlaid on or beside the image
- Optional: 1-2 lines of supporting text — brief, not analytical

**Visual:**
- Image must be high quality and directly relevant — no generic stock photography
- Text overlay must have sufficient contrast — use a color overlay, dark tint, or position text on a clear area of the image
- Typography as design element — weight, size, placement intentional

**Rules relaxations:**
- No action title required
- No source/footnote required unless image is licensed
- No legend required
- Two-font-size rule suspended
- One-message-per-slide rule applies strictly — this type has the least content; it must say exactly one thing

**Layout variants:**
- A: Full-bleed image with overlaid statement
- B: Split layout — image left, statement right
- C: Image with dark overlay and centered statement
- D: Image at top, statement below with accent bar

**Reference:** `09_Cover Divider.pdf`

**Red flags:**
- Image is generic or disconnected from the message → replace
- Text is hard to read against the image → add contrast treatment
- More than one idea on the slide → remove one

**Usage guidance:** use at opening, closing, or a single pivot moment — not as filler.

---

## 13. Text, Trends & Insight

**Purpose:** Communicate structured analysis without charts. Used for trend overviews, findings summaries, hypothesis maps, and challenge/solution pairs.

**When to use:**
- The argument is qualitative, not data-driven
- The content has 3-5 parallel items with descriptive detail per item
- Icons or typography anchors can carry visual weight where a chart would be

**Relationship to Visual Model:** Text/Trends variants A, D, E overlap with Visual Model sub-types (trends-to-takeaway, numbered columns, numbered rows). Rule of thumb: if the *shape* is the argument (a pyramid means "ascending," a cycle means "repeating"), it's Visual Model. If the layout is a structured text container with icons as anchors, it's Text/Trends. When in doubt, Slide Designer chooses based on the three-signal Visual Model trigger — if signals fire, use Visual Model; otherwise use Text/Trends.

**Headline rule:** Action title required.

**Structure:**
- 3-5 parallel items
- Each item has a bold header and 2-4 supporting bullets or a short descriptor
- Takeaway bar or summary sometimes added at the bottom

**Visual:**
- Icons as section anchors (style-locked per slide)
- Clean grid or row layout
- Accent color used sparingly for emphasis

**Layout variants:**
- A: 3 trends, icon stems converging to takeaway bar
- B: 3 trends, icon left + bold header + bullets right (rows)
- C: Deep-dive: text+bullets left, full-height photo right
- D: 5 key areas, numbered columns
- E: 5 key areas, numbered half-circle rows
- F: Findings + Recommendations two-panel
- G: Challenges + Solutions rows with connecting arrows

**Reference:** `08_Structured Text.pdf`

**Red flags:**
- Items are uneven in depth (one has 4 bullets, another has 1) → rebalance or cut
- Icons are decorative, not structural → make them relevant or remove
- No takeaway at the bottom → consider adding a summary bar if the items together imply a conclusion

---

## 14. Competitive & Market Analysis

**Purpose:** Present landscape data on competitors, market positioning, or value proposition comparison.

**When to use:**
- Benchmarking the client against competitors
- Mapping the competitive landscape
- Showing where the client plays in the market

**Headline rule:** Action title required — state what the landscape means, not just what it shows.

**Structure:**
- Consistent criteria across all players
- Client highlighted visually (distinct color, border, or callout)
- Source and methodology noted

**Visual:**
- Competitor tables with indicators (Harvey Balls, inline bars)
- Positioning scatter plots with quadrant shading
- Value proposition dot-line charts

**Layout variants:**
- A: Competitor table with Harvey Ball indicators
- B: Competitor table with inline bar charts
- C: Positioning scatter with quadrants
- D: Value proposition dot-line chart

**Reference:** `04_Competitive Analysis.pdf`

**Red flags:**
- Criteria biased toward client → use balanced criteria or flag the bias
- Competitors not clearly identified → label each player
- Positioning map with no axes labeled → always label axes

---

## 15. Roadmap & Timeline

**Purpose:** Show project phases, milestones, and time-based sequencing.

**When to use:**
- Presenting a multi-phase plan
- Showing progress against a timeline
- Sequencing initiatives over time

**This page type vs. three-column parallel:** If the user calls the content a "timeline," use this page type — not a multi-bucket layout. Three-column parallel (page type 4) suits parallel workstreams with no date anchors. This page type suits any content the user associates with calendar time, phases, or sequence. When in doubt: did the user say "timeline"? Then it's a timeline.

**Headline rule:** Action title required — state what the timeline achieves, not just that a timeline exists.

**Structure:**
- Phases or time periods clearly demarcated
- Activities, deliverables, and milestones mapped to phases
- Owner per phase if multiple teams are involved

**Visual:**
- Chevron or arrow phases
- Gantt-style bars for concurrent activities
- Milestone diamonds or pentagons

**Layout variants:**
- A: 3-phase project plan with chevron arrows
- B: 3 or 4-phase roadmap with deliverable icons
- C: Gantt tracker (workstream + weekly bars)
- D: Immediate next steps list

**Reference:** `07_Roadmaps.pdf`

**Red flags:**
- Phases don't have clear start/end dates → add dates
- Activities span too many phases → break up or escalate as risk
- No owners per phase → status without accountability is not actionable

**Phase A HTML build pattern (Gantt-style CSS Grid):**

Limits: max 5 workstreams, max 8 time periods. For longer timelines, split into two slides (first half / second half) and note the split in the page title.

```html
<!-- Gantt roadmap: 4 workstreams × 6 quarters -->
<div style="
  display: grid;
  grid-template-columns: 130px repeat(6, 1fr);
  grid-template-rows: 36px repeat(4, 1fr);
  gap: 2px;
  width: 1100px; height: 400px;
  position: absolute; top: 110px; left: 60px;
">

  <!-- Header row: empty corner + time period labels -->
  <div style="grid-column:1; grid-row:1;"></div>
  <div style="grid-column:2; grid-row:1; font-size:11px; font-weight:700; color:#555; text-align:center;">Q1 2025</div>
  <div style="grid-column:3; grid-row:1; font-size:11px; font-weight:700; color:#555; text-align:center;">Q2 2025</div>
  <div style="grid-column:4; grid-row:1; font-size:11px; font-weight:700; color:#555; text-align:center;">Q3 2025</div>
  <div style="grid-column:5; grid-row:1; font-size:11px; font-weight:700; color:#555; text-align:center;">Q4 2025</div>
  <div style="grid-column:6; grid-row:1; font-size:11px; font-weight:700; color:#555; text-align:center;">Q1 2026</div>
  <div style="grid-column:7; grid-row:1; font-size:11px; font-weight:700; color:#555; text-align:center;">Q2 2026</div>

  <!-- Workstream row 1: label + activity bar spanning columns 2–4 -->
  <div style="grid-column:1; grid-row:2; font-size:12px; font-weight:600; color:#222; display:flex; align-items:center; padding-right:8px;">Data Foundation</div>
  <div style="grid-column:2/5; grid-row:2; background:#4D148C; border-radius:4px; margin:6px 2px; display:flex; align-items:center; padding-left:8px;">
    <span style="font-size:10px; color:#fff; font-weight:600;">Assessment → Architecture → Pilot</span>
  </div>
  <!-- milestone marker: appears at end of bar -->
  <div style="grid-column:5; grid-row:2; display:flex; align-items:center; justify-content:flex-start; padding-left:4px;">
    <div style="width:12px; height:12px; background:#4D148C; transform:rotate(45deg); border-radius:1px;"></div>
  </div>

  <!-- Workstream row 2: label + two separate bars -->
  <div style="grid-column:1; grid-row:3; font-size:12px; font-weight:600; color:#222; display:flex; align-items:center; padding-right:8px;">Analytics Platform</div>
  <div style="grid-column:3/6; grid-row:3; background:#7B3FAD; border-radius:4px; margin:6px 2px; display:flex; align-items:center; padding-left:8px;">
    <span style="font-size:10px; color:#fff; font-weight:600;">Build → Deploy → Stabilize</span>
  </div>

  <!-- Workstream row 3 -->
  <div style="grid-column:1; grid-row:4; font-size:12px; font-weight:600; color:#222; display:flex; align-items:center; padding-right:8px;">Change & Training</div>
  <div style="grid-column:4/7; grid-row:4; background:#2C5F8A; border-radius:4px; margin:6px 2px; display:flex; align-items:center; padding-left:8px;">
    <span style="font-size:10px; color:#fff; font-weight:600;">Comms → Training → Adoption</span>
  </div>

  <!-- Workstream row 4 -->
  <div style="grid-column:1; grid-row:5; font-size:12px; font-weight:600; color:#222; display:flex; align-items:center; padding-right:8px;">Governance</div>
  <div style="grid-column:2/8; grid-row:5; background:#E8E8E8; border-radius:4px; margin:6px 2px; display:flex; align-items:center; padding-left:8px;">
    <span style="font-size:10px; color:#444; font-weight:600;">Ongoing — steering cadence throughout</span>
  </div>

</div>
```

**Rules:**
- Label column is always `grid-column:1`; time period columns start at `grid-column:2`
- Activity bars use `grid-column:start/end` shorthand — end is exclusive (col 2–4 inclusive = `2/5`)
- Milestone markers are `div` elements with `transform:rotate(45deg)` — no SVG diamonds
- No cross-workstream connector lines — Phase B cannot render diagonal paths
- Row heights use `1fr` (not fixed px) so bars fill the row without dead space
- Phase background color bands (to group time periods) use a background div in row 1 spanning the target columns

---

## 16. Org Chart, Team & Governance

**Purpose:** Show people, reporting structures, decision flows, or governance tiers.

**When to use:**
- Presenting an engagement team
- Showing governance structure
- Mapping decision authority

**Headline rule:** Action title required.

**Structure:**
- Hierarchy or flow clearly indicated (solid lines for direct reporting, dashed for advisory or matrix)
- Named individuals where relevant (with roles)
- Decision or approval flows marked

**Visual:**
- Boxes connected by lines for hierarchy
- Chevron flows for decision sequences
- Central hub for function or governance maps

**Layout variants:**
- A: Governance structure (steering / working / advisory tiers)
- B: Traditional org chart
- C: Project team with workstream tracks
- D: Function map (central hub + satellites)
- E: Decision flow (inputs → working team → steering → executive)

**Reference:** `10_Org Charts Team Governance.pdf`

**Red flags:**
- Reporting lines ambiguous → use solid/dashed distinction
- Missing owner names → add them
- Decision authority unclear → mark it explicitly
- More than 3 hierarchy levels → split into two slides (tiers 1–2 / tiers 3+). Beyond 3 levels, node text becomes unreadably small at slide canvas dimensions (1280×720px). State the split in the page title, e.g. "Governance — steering and programme tiers."

**Phase A HTML build pattern (nested flex tree):**

Limits: max 3 levels deep, max 5 nodes per level. If the org chart exceeds these limits, split across two slides (top half / bottom half) and note the split in the page title (e.g., "Governance structure — tiers 1 & 2").

Connector lines are CSS borders on wrapper divs — no SVG, no pseudo-elements (Phase B cannot render either).

```html
<!-- Org chart: 3 levels, root → 3 reports → 2 reports each -->
<div style="
  display: flex; flex-direction: column; align-items: center;
  width: 1100px; gap: 0;
  position: absolute; top: 110px; left: 60px;
">

  <!-- LEVEL 1: Root node -->
  <div style="display:flex; flex-direction:column; align-items:center;">
    <div style="
      background:#4D148C; color:#fff; font-size:12px; font-weight:700;
      padding:10px 20px; border-radius:4px; text-align:center; min-width:160px;
    ">
      Programme Director<br>
      <span style="font-size:10px; font-weight:400;">Jane Smith</span>
    </div>
    <!-- Connector stem down -->
    <div style="width:2px; height:24px; background:#CCCCCC;"></div>
  </div>

  <!-- Horizontal connector bar spanning all children -->
  <div style="display:flex; flex-direction:row; align-items:flex-start; gap:0;">

    <!-- Left branch -->
    <div style="display:flex; flex-direction:column; align-items:center; margin:0 16px;">
      <!-- Top border draws the horizontal bar + left turn -->
      <div style="width:2px; height:20px; background:#CCCCCC;"></div>
      <!-- LEVEL 2: Node -->
      <div style="
        background:#7B3FAD; color:#fff; font-size:12px; font-weight:600;
        padding:8px 16px; border-radius:4px; text-align:center; min-width:140px;
      ">
        Workstream Lead A<br>
        <span style="font-size:10px; font-weight:400;">Alex Johnson</span>
      </div>
      <div style="width:2px; height:20px; background:#CCCCCC;"></div>
      <!-- LEVEL 3: Reports -->
      <div style="display:flex; flex-direction:row; gap:8px;">
        <div style="
          background:#EDE7F6; color:#222; font-size:11px; font-weight:600;
          padding:6px 12px; border-radius:4px; text-align:center; min-width:110px;
        ">
          Analyst<br><span style="font-size:10px; font-weight:400;">M. Lee</span>
        </div>
        <div style="
          background:#EDE7F6; color:#222; font-size:11px; font-weight:600;
          padding:6px 12px; border-radius:4px; text-align:center; min-width:110px;
        ">
          Consultant<br><span style="font-size:10px; font-weight:400;">K. Patel</span>
        </div>
      </div>
    </div>

    <!-- Vertical divider between branches (draws the cross-bar) -->
    <div style="width:2px; height:20px; background:#CCCCCC; margin-top:0; align-self:flex-start;"></div>

    <!-- Center branch -->
    <div style="display:flex; flex-direction:column; align-items:center; margin:0 16px;">
      <div style="width:2px; height:20px; background:#CCCCCC;"></div>
      <div style="
        background:#7B3FAD; color:#fff; font-size:12px; font-weight:600;
        padding:8px 16px; border-radius:4px; text-align:center; min-width:140px;
      ">
        Workstream Lead B<br>
        <span style="font-size:10px; font-weight:400;">Sam Rivera</span>
      </div>
      <div style="width:2px; height:20px; background:#CCCCCC;"></div>
      <div style="display:flex; flex-direction:row; gap:8px;">
        <div style="
          background:#EDE7F6; color:#222; font-size:11px; font-weight:600;
          padding:6px 12px; border-radius:4px; text-align:center; min-width:110px;
        ">
          Analyst<br><span style="font-size:10px; font-weight:400;">T. Chen</span>
        </div>
        <div style="
          background:#EDE7F6; color:#222; font-size:11px; font-weight:600;
          padding:6px 12px; border-radius:4px; text-align:center; min-width:110px;
        ">
          Consultant<br><span style="font-size:10px; font-weight:400;">B. Osei</span>
        </div>
      </div>
    </div>

    <!-- Right branch -->
    <div style="display:flex; flex-direction:column; align-items:center; margin:0 16px;">
      <div style="width:2px; height:20px; background:#CCCCCC;"></div>
      <div style="
        background:#7B3FAD; color:#fff; font-size:12px; font-weight:600;
        padding:8px 16px; border-radius:4px; text-align:center; min-width:140px;
      ">
        PMO Lead<br>
        <span style="font-size:10px; font-weight:400;">C. Adeyemi</span>
      </div>
    </div>

  </div>
</div>
```

**Rules:**
- Level 1 node uses the darkest accent color; Level 2 uses mid-accent; Level 3 uses a tinted background with dark text
- Connector stems are `<div style="width:2px; height:Npx; background:#CCCCCC;">` — plain divs, no SVG or pseudo-elements
- The horizontal crossbar between siblings is achieved by the gap between flex children + the vertical connector divs — no absolute positioning
- Advisory or matrix relationships (dashed lines): use `border:2px dashed #CCCCCC` on the connector div instead of a solid background
- Role label + person name in a single node: use a `<br>` and a `<span>` with lighter weight
- Do not exceed 3 levels. For deeper hierarchies, show levels 1–2 on slide 1, collapse level 3 into counts (e.g., "4 analysts")

---

## 17. Swim Lane

**Purpose:** Show a multi-team or multi-role process where each row represents one actor and columns represent time or stages.

**When to use:**
- Explaining a handoff-heavy workflow involving 2–4 teams
- Showing who does what at each stage of a process
- Mapping a customer journey with internal back-stage steps

**Headline rule:** State the outcome the process delivers, or the friction it resolves.
- Bad: *"Order-to-cash process"*
- Good: *"Streamlined order-to-cash cuts fulfillment time from 14 days to 8"*

**Structure:**
- Rows = lanes (one per actor/team); max 4 lanes
- Columns = stages or time periods; max 6 columns
- Each cell contains the activity owned by that actor in that stage
- Handoff arrows implied by adjacency — no cross-lane SVG connectors

**Visual:**
- Alternating lane row background colors for readability
- Lane header column at left (fixed width ~120px)
- Activity blocks as filled `<div>` elements within each cell

**Layout variants:**
- A: Stage-based (columns = process steps)
- B: Time-based (columns = weeks/months)
- C: Simplified 2-lane (us vs. client)

**Red flags:**
- More than 4 lanes → consolidate or split into two slides
- Activities that span multiple lanes → model as a separate "shared step" row instead
- Cross-lane arrows → remove; use sequencing within a lane or a handoff label

**Phase A HTML build pattern (CSS Grid swim lane):**

Limits: max 4 lanes, max 6 time periods, max 2-column span per activity block. No cross-lane connector lines.

```html
<!-- Swim lane: 3 lanes × 5 stages -->
<div style="
  display: grid;
  grid-template-columns: 120px repeat(5, 1fr);
  grid-template-rows: 36px repeat(3, 1fr);
  gap: 2px;
  width: 1100px; height: 380px;
  position: absolute; top: 110px; left: 60px;
">

  <!-- Header row: corner + stage labels -->
  <div style="grid-column:1; grid-row:1; background:#F0F0F0; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#555;"></div>
  <div style="grid-column:2; grid-row:1; background:#F0F0F0; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#555;">Initiate</div>
  <div style="grid-column:3; grid-row:1; background:#F0F0F0; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#555;">Assess</div>
  <div style="grid-column:4; grid-row:1; background:#F0F0F0; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#555;">Design</div>
  <div style="grid-column:5; grid-row:1; background:#F0F0F0; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#555;">Build</div>
  <div style="grid-column:6; grid-row:1; background:#F0F0F0; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#555;">Deploy</div>

  <!-- Lane 1: Client -->
  <div style="grid-column:1; grid-row:2; background:#EDE7F6; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; color:#4D148C; border-right:2px solid #CCCCCC;">Client</div>
  <div style="grid-column:2; grid-row:2; background:#F8F4FF; padding:8px; font-size:11px; color:#333;">Define scope<br>Approve charter</div>
  <div style="grid-column:3; grid-row:2; background:#F8F4FF; padding:8px; font-size:11px; color:#333;">Review findings<br>Validate priorities</div>
  <!-- Spans 2 stages: Design + Build -->
  <div style="grid-column:4/6; grid-row:2; background:#D9C9F0; padding:8px; font-size:11px; color:#333; border-radius:2px;">Review & approve designs in sprint cycles</div>
  <div style="grid-column:6; grid-row:2; background:#F8F4FF; padding:8px; font-size:11px; color:#333;">Sign-off<br>Go-live approval</div>

  <!-- Lane 2: Accenture Delivery -->
  <div style="grid-column:1; grid-row:3; background:#E3EEF7; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; color:#2C5F8A; border-right:2px solid #CCCCCC; text-align:center; padding:4px;">Delivery Team</div>
  <div style="grid-column:2; grid-row:3; background:#F4F9FF; padding:8px; font-size:11px; color:#333;">Kick-off<br>Mobilise team</div>
  <div style="grid-column:3; grid-row:3; background:#F4F9FF; padding:8px; font-size:11px; color:#333;">Current-state analysis<br>Gap assessment</div>
  <div style="grid-column:4; grid-row:3; background:#F4F9FF; padding:8px; font-size:11px; color:#333;">Solution design<br>Prototyping</div>
  <div style="grid-column:5; grid-row:3; background:#F4F9FF; padding:8px; font-size:11px; color:#333;">Build & test<br>UAT support</div>
  <div style="grid-column:6; grid-row:3; background:#F4F9FF; padding:8px; font-size:11px; color:#333;">Deployment<br>Hypercare</div>

  <!-- Lane 3: Technology -->
  <div style="grid-column:1; grid-row:4; background:#FFF3E0; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; color:#BF5700; border-right:2px solid #CCCCCC;">Technology</div>
  <div style="grid-column:2/4; grid-row:4; background:#FFFAF0; padding:8px; font-size:11px; color:#333; border-radius:2px;">Environment setup & access provisioning</div>
  <div style="grid-column:4; grid-row:4; background:#FFFAF0; padding:8px; font-size:11px; color:#333;">Infra design<br>Sign-off</div>
  <div style="grid-column:5/7; grid-row:4; background:#FFE0B2; padding:8px; font-size:11px; color:#333; border-radius:2px;">CI/CD pipeline → production deployment</div>

</div>
```

**Rules:**
- Lane header cells use a distinct background and a `border-right:2px solid #CCCCCC` to separate the label column from content
- Activity spans use `grid-column:start/end` (exclusive end) — max span of 2 columns
- No `position:absolute` inside grid cells — Phase B reads DOM-computed bboxes from the grid layout
- No cross-lane arrows; handoff is implied by adjacent cells in different rows reaching the same column
- Lane background colors should come from the template's accent palette (light tints, not full saturation)

---

## 18. Flowchart / Process Decision Flow

**Purpose:** Show a branching or decision-driven process where steps connect with arrows, including YES/NO decision branches, loops, and cross-lane handoffs.

**When to use:**
- Explaining a process that has decision points (gates, approvals, branches)
- Showing a pipeline with conditional paths (e.g. pass/fail, approve/reject)
- Mapping a multi-actor workflow where arrows cross lane boundaries

**Distinction from Swim Lane (Section 17):** Swim lanes show parallel activities across actors where handoffs are implied by adjacency. Flowcharts have explicit arrows — including L-shaped elbow connectors that cross lanes — and decision diamonds. If the slide needs visible arrows between steps, use the flowchart pattern.

**Headline rule:** State what the process produces or decides, not that a process exists.
- Bad: *"Slide Lab pipeline overview"*
- Good: *"A three-phase pipeline converts a brief into a reviewed PPTX in one session"*

**Limits:** Max 4 lanes, max 8 process steps, max 3 decision points. For more complex flows, split into two slides (Phase 1 / Phase 2).

**Phase A mandatory warning — connector arrows do not survive Phase B:**

> **Tell the user this before building the mockup:** "Connector arrows in this flowchart mockup will NOT appear in the built PPTX. The Phase B DOM walker excludes SVG overlays. After delivery, open the PPTX in PowerPoint and add the connectors manually using Insert → Shape → Lines → Elbow Connector. If you need the arrows baked into the file (e.g. for a read-only PDF), this slide must be built as a static PNG (set `data-chart="true"` on the entire canvas div) instead."

**Phase A HTML build pattern — SVG overlay for connectors:**

Flowcharts MUST use a single SVG overlay for ALL connectors and arrowheads. Do NOT use two separate div segments for L-shaped connectors — CSS div segments cannot produce clean miter-joined corners and create visual artifacts at joints.

```html
<!-- Flowchart: 4-lane process with decision diamond and elbow connectors -->
<div style="position:relative; width:1280px; height:720px; background:#fff;">

  <!-- LANE HEADER COLUMN (left side) -->
  <div style="position:absolute; left:0; top:80px; width:110px; height:600px;">
    <div style="height:150px; background:#EDE7F6; display:flex; align-items:center;
                justify-content:center; font-size:11px; font-weight:700; color:#4D148C;
                border-bottom:1px solid #D0C0E8; text-align:center; padding:4px;">
      Consultant
    </div>
    <div style="height:150px; background:#E3EEF7; display:flex; align-items:center;
                justify-content:center; font-size:11px; font-weight:700; color:#2C5F8A;
                border-bottom:1px solid #C0D8E8; text-align:center; padding:4px;">
      storyline-helper
    </div>
    <div style="height:150px; background:#FFF3E0; display:flex; align-items:center;
                justify-content:center; font-size:11px; font-weight:700; color:#BF5700;
                border-bottom:1px solid #E0D0B0; text-align:center; padding:4px;">
      slide-builder
    </div>
    <div style="height:150px; background:#F1F8E9; display:flex; align-items:center;
                justify-content:center; font-size:11px; font-weight:700; color:#558B2F;
                text-align:center; padding:4px;">
      Session Output
    </div>
  </div>

  <!-- STEP BOXES (absolutely positioned) -->
  <!-- Lane 1, Step 1 -->
  <div style="position:absolute; left:160px; top:105px; width:140px; height:60px;
              background:#4D148C; border-radius:6px; display:flex; align-items:center;
              justify-content:center; text-align:center; padding:6px;">
    <span style="font-size:11px; font-weight:700; color:#fff;">Provide brief &amp; template</span>
  </div>

  <!-- Decision diamond (lane 2) -->
  <div style="position:absolute; left:460px; top:215px; width:80px; height:80px;
              background:#fff; border:2px solid #2C5F8A; transform:rotate(45deg);">
  </div>
  <div style="position:absolute; left:460px; top:215px; width:80px; height:80px;
              display:flex; align-items:center; justify-content:center; text-align:center;">
    <span style="font-size:10px; font-weight:700; color:#2C5F8A; line-height:1.2;">Gate<br>pass?</span>
  </div>

  <!-- YES label on diamond branch -->
  <div style="position:absolute; left:556px; top:245px; font-size:10px;
              font-weight:700; color:#558B2F;">YES</div>
  <!-- NO label on diamond branch -->
  <div style="position:absolute; left:490px; top:300px; font-size:10px;
              font-weight:700; color:#C62828;">NO</div>

  <!-- SVG OVERLAY — all connectors and arrowheads -->
  <!--
    Rules:
    - One <marker> per stroke color. orient="auto" rotates arrowhead correctly for all directions.
    - refX="0" places the marker base at the path end; tip extends 8px beyond in path direction.
    - Stop all paths 8px before the target box edge so arrowhead tip lands flush on the box.
    - Elbow right-then-down: M x1 y1 L xc y1 L xc y2_minus8
    - Elbow down-then-right: M x1 y1 L x1 yc L x2_minus8 yc
    - Three-segment return: M x1 y1 L x2 y1 L x2 y3 L x4_minus8 y3
  -->
  <svg style="position:absolute; top:0; left:0; width:1280px; height:720px;
              pointer-events:none; overflow:visible;">
    <defs>
      <!-- Purple arrowhead -->
      <marker id="arr-purple" markerWidth="8" markerHeight="7"
              refX="0" refY="3.5" orient="auto" markerUnits="userSpaceOnUse">
        <polygon points="0,0 8,3.5 0,7" fill="#4D148C"/>
      </marker>
      <!-- Blue arrowhead -->
      <marker id="arr-blue" markerWidth="8" markerHeight="7"
              refX="0" refY="3.5" orient="auto" markerUnits="userSpaceOnUse">
        <polygon points="0,0 8,3.5 0,7" fill="#2C5F8A"/>
      </marker>
      <!-- Green arrowhead -->
      <marker id="arr-green" markerWidth="8" markerHeight="7"
              refX="0" refY="3.5" orient="auto" markerUnits="userSpaceOnUse">
        <polygon points="0,0 8,3.5 0,7" fill="#558B2F"/>
      </marker>
      <!-- Red arrowhead (NO branch) -->
      <marker id="arr-red" markerWidth="8" markerHeight="7"
              refX="0" refY="3.5" orient="auto" markerUnits="userSpaceOnUse">
        <polygon points="0,0 8,3.5 0,7" fill="#C62828"/>
      </marker>
    </defs>

    <!-- Step 1 → Step 2: straight horizontal -->
    <path d="M 300 135 L 348" stroke="#4D148C" stroke-width="2" fill="none"
          marker-end="url(#arr-purple)"/>

    <!-- Step 2 → Decision diamond: elbow down-then-right -->
    <path d="M 390 165 L 390 254 L 452" stroke="#2C5F8A" stroke-width="2" fill="none"
          marker-end="url(#arr-blue)"/>

    <!-- YES branch: diamond → Step 3 (straight right) -->
    <path d="M 548 255 L 618" stroke="#558B2F" stroke-width="2" fill="none"
          marker-end="url(#arr-green)"/>

    <!-- NO branch: diamond → return to Step 1 (elbow down-then-left-then-up) -->
    <path d="M 500 303 L 500 380 L 140 380 L 140 172" stroke="#C62828"
          stroke-width="2" fill="none" stroke-dasharray="6 3"
          marker-end="url(#arr-red)"/>

  </svg>

</div>
```

**SVG connector rules (enforced — not optional):**
- All connectors must use a single SVG overlay element (`position:absolute; top:0; left:0; width:1280px; height:720px`), not separate div segments
- One `<marker>` per stroke color; `orient="auto"` handles all arrowhead directions automatically — no manual per-direction arrowhead divs
- `refX="0"` places the marker base at the path endpoint; the tip extends 8px beyond in the path direction
- Stop all paths 8px before the target box edge: `x2_minus8 = target_left - 8` so the arrowhead tip lands flush
- Elbow paths use L-commands: `M x1 y1 L xc y1 L xc y2` (right-then-down) or `M x1 y1 L x1 yc L x2 yc` (down-then-right)
- Dashed lines for return/rejected paths: `stroke-dasharray="6 3"`

**Phase B rendering:** The DOM walker excludes full-slide SVG overlays from the screenshot path — flowchart connector arrows do NOT appear in the built PPTX and must be added manually in PowerPoint after the build. The boxes and labels render correctly as overlay shapes. Do not attempt to walk SVG path elements individually — they are not renderable by python-pptx. (Known limitation — see Issue 12 in `reference/known-issues-and-improvements.md`.)

**Red flags:**
- Using two separate `<div>` segments for an L-shaped connector → replace with SVG path
- Per-direction arrowhead divs (separate elements for left/right/up/down arrows) → replace with `orient="auto"` marker
- More than 3 decision points on a single slide → split into two slides

---

## PMO — Handled as Template Fill-In, Not Insight Generation

**PMO slides are not a first-class page type in this system.** The pipeline — Storyline Helper, the Foundation Check, mentor coaching, governing-thought-first structuring, Visual Model detection — is designed to help consultants generate *insightful, thoughtful* slides. PMO slides (status updates, risk registers, decision logs, action item trackers, milestone summaries) are recurring operational reports where the work is filling in a known template consistently, not generating new insight. Forcing the insight-generation pipeline onto PMO work is a category error — it adds cost without adding value.

### How the pipeline handles PMO slides

**Detection.** storyline-helper detects PMO intent either from the consultant's opening answer (mentions of status, recurring report, RAG indicators, workstreams, risk register) or by asking directly when the slide's purpose sounds operational rather than argumentative.

**Conversation.** When PMO intent is confirmed, storyline-helper does NOT run the full insight-generation flow. Instead, it says something like:

> *"PMO slides are recurring and template-driven — they don't need the insight-generation work this system is designed to do. Do you have an existing format you want me to fill in? If so, drop it in this folder and I'll replicate the structure with your new content. If you don't have a template yet, I'd recommend either (a) building your first version manually in PowerPoint, then coming back next cycle so I can replicate it going forward, or (b) telling me what data you want on the slide and I'll do my best to lay it out cleanly — but this isn't where the system shines."*

**Template-fill mode (if the consultant has a template):**
- Consultant drops the existing PMO template PPTX in the project folder
- storyline-helper reads the template to understand its structure (RAG columns, workstream rows, whatever the client's format is)
- Skips Storyline Helper, the Foundation Check, and Visual Model detection
- Hands Builder a minimal brief: *"Replicate this template's structure. Fill with the following content: [consultant's data]."*
- Builder produces one slide (not 4 variations — a PMO report doesn't need design options)
- Output delivers as normal

**No-template fallback (if the consultant doesn't have one):**
- storyline-helper suggests the consultant build it manually first
- If they insist on proceeding, storyline-helper produces a minimal brief using the closest available layout from reference group 07 (Roadmaps and Timelines)
- Builder produces one slide with a clear flag that this is a first-pass PMO layout that the consultant will likely want to refine manually

**What carries over from the insight pipeline:**
- Universal rules in `rules.md` still apply (9pt floor, source/footnote presence, alignment, page numbers)
- Glossary terminology still applies
- Everything else is bypassed

### Why we made this choice

Early versions of this system included PMO as 5 first-class page types (Status Update, Risk Register, Decision Log, Action Item Tracker, Milestone Summary). We removed them because PMO isn't a *visual pattern* worth teaching through references — it's a *content type* that reuses existing patterns (tables, timelines, RAG indicators) from other groups. Including PMO as its own page type created the wrong incentive: it made Designer generate 4 variations of a status slide when a consultant just wants one replicated-format slide per week.

If your primary use case is PMO reporting, this system will do it — but it's not the product this system is designed to be. A PowerPoint template with locked formatting is a better tool for that work.

---

## How the Model Uses This Catalog

When the model receives a structured brief:

1. Infers the page type from the slide's editorial emphasis and content description in the brief (the narrative brief has no explicit "Page Type" field — the model derives it from context)
2. Looks up the corresponding entry in this catalog
3. Uses the entry's layout variants as the starting set for the 3 design options
4. Consults the named Reference PDF for proportional layout examples
5. Applies universal rules from `rules.md` (which always apply) and the entry's Rules Relaxations (which override universals for this type only)
6. Uses zone terminology from `glossary.md` consistently

For Visual Model (Section 8), Designer additionally runs the three-signal trigger check to decide whether to include Visual Model as one of the 4 options when the page type is something other than Visual Model.

**For PMO briefs:** the model routes PMO requests to template-fill mode and does not run the full insight-generation flow. Only insight-generation page types (1-16) receive the full Phase A mockup treatment.

If a brief's page type does not match any entry in this catalog, halt and ask the user to re-classify.
