# MBB Slide Rules — Universal

This document contains the universal rules that apply to every slide, regardless of page type. Page-type-specific rules (Insight, Recommendation, Status Update, etc.) live in `page-types.md`. Zone terminology and anatomy diagrams live in `glossary.md`. The three documents work together — rules.md defines *what's always true*, page-types.md defines *what's true for each type*, glossary.md defines *what we call things*.

---

## What Makes a Slide "MBB Quality"

Before the rules themselves — the *why*. A slide passes the MBB quality bar when:

1. **The action title alone tells the story** — a senior leader who only reads the title walks away with the right conclusion
2. **The deck passes the title-only test** — reading only the action titles in sequence tells the full story without needing the body content
3. **Every element earns its place** — remove anything that doesn't directly support the action title
4. **The structure is airtight** — supporting points are MECE, non-overlapping, and together prove the action title
5. **The visual does work** — it doesn't decorate, it proves
6. **Data is always cited and labeled** — every chart has axis titles, every data point has a source
7. **It respects the audience's time** — scannable in under 30 seconds for a senior reader
8. **It holds up as a PDF** — formatting, alignment, and spacing are verified in PDF view before sharing

The rules below exist to produce these outcomes. When a rule feels arbitrary, look back to this list — every rule is traceable to one of these eight principles.

---

## Action Title

- The action title is the **"so what"** — it must state the insight, recommendation, or conclusion, not describe what the slide contains
- Bad: *"Revenue by Region Q3"* → Good: *"APAC is the only region driving growth; NA and EU are flat or declining"*
- Must be a **declarative sentence** — verb-driven, conclusive, not a label or topic description
- Maximum **two lines**; one line strongly preferred — if the full slide cannot be explained in two lines, split into two slides
- A reader should be able to read only the action titles across the full deck and understand the complete story — every title must hold up to this test
- Font size: inherits from the template title placeholder (~28pt, bold) — do not hardcode

**Exception — PMO and recurring reports:** descriptive titles are acceptable when the audience is pattern-matching against prior versions of the same report. See PMO Mode at the end of this document.

**Exception — Executive Summary:** a label title ("Executive Summary") is acceptable because the body of the slide carries the argument directly. See `page-types.md` Executive Summary for details.

**Exception — Conceptual pages (dividers, quotes, full-bleed statements):** action title not required; a short phrase, single word, or no title at all is acceptable. See `page-types.md` Conceptual for details.

---

## Sub-Headline

- **Stylistic option, not a hard rule.** Use when there is no explicit takeaway or insight callout section on the slide
- Purpose: **bridge the action title conclusion to the supporting evidence** — adds one layer of context the audience may need
- **Only use a sub-headline when the action title fits on one line.** If the title wraps to two lines, the sub-headline is removed — a two-line title plus sub-headline crowds the top and competes with the content zone
- Sits directly below the action title, visually subordinate (smaller font, lighter weight or muted color)
- Maximum one line; if it runs longer, the title may not be sharp enough
- Do not use if body content already opens with a clear bridging statement — it will be redundant
- Font: inherits from template subtitle placeholder (16pt / ~21px) — do not hardcode

---

## Structure

- **One governing thought per slide.** If a slide is trying to say two things, it should be two slides
- Supporting content must directly prove or illustrate the action title — nothing on the slide exists unless it earns its place
- Maximum **2-5 supporting points or buckets** — more than 5 signals the thinking hasn't been tightened
- Supporting points must be **MECE** (Mutually Exclusive, Collectively Exhaustive) where possible — no overlaps, no gaps

---

## Visual

- Every slide must have at least one visual element — chart, icon, diagram, table, callout stat, or shape-based model
- No text-only slides
- Visuals must directly support the action title — decorative visuals are not acceptable
- Every chart must have **axis titles** — unlabeled axes are not acceptable
- Every data point must have a **source** — uncited data loses credibility

---

## Chart Positioning and Alignment

**Left alignment — the most important rule:**
- The chart's left edge (y-axis line) must be flush with the slide's left content margin — the same x-position as the action title, chart title, and any table below it
- Everything on the slide shares one vertical alignment axis down the left side
- A chart that floats centered while a table starts at the left margin is a hard error — fix it

**Chart title:**
- Position: directly above the chart, left-aligned flush with the slide's left content margin
- Font: bold, 14pt (or the larger of the two body sizes) — smaller than the action title, larger than body text
- Distinct from the action title — chart title labels *what the chart shows*; action title states *what it means*
- Gap between chart title and chart body: 4-6pt — title should feel attached to the chart, not floating above
- Always left-aligned — never centered

**Legend (internal to the chart):**
- Default position: top right, horizontally inline with the chart title — title anchors the left, legend anchors the right
- Compact, small font (10-11pt), icon/swatch + label, horizontal row
- Never place at the bottom of the chart — bottom legends are the PowerPoint default and must always be overridden
- If the title is long, move the legend below the chart title or directly above the chart area

**Chart width:**
- The chart spans the full available content width — no large empty margins on the right side
- When a chart shares the slide with a callout box (insight panel right), the chart takes the remaining left-side width; its left edge still aligns with the slide margin

**When chart and table appear on the same slide:**
- Both share the same left edge — the table's first column left edge aligns with the chart's y-axis
- Column widths in the table should approximately mirror the bar or data point spacing in the chart above it

---

## Source / Footnote

- A source/footnote line must be included on **every slide by default** — permanent structural element, not optional
- Placeholder text: *"Source: [insert source]"*
- Position: bottom left, above the page number if present
- Font: 9-10pt, muted color (visually subordinate to all body content)
- Consultant may populate, modify, or delete — but it must always be placed and visible in the initial output so it is not forgotten
- Multiple sources: comma-separated on the same line; if too long, stack on two lines at the same font size

---

## Legend

- **Required** whenever colors or icons encode meaning — never leave the audience to guess
- **Default format (Format A — Key Table):** compact bordered box in the **top-right corner** containing icon/swatch + label rows; include a "Legend" header label in 9pt uppercase
- **Exception format (Format B — Inline Pills):** use when icons or colors are scattered across a diagram, map, or chart and a top-right box would feel detached — float pill-style labels near the data they describe
- **Minimal format (Format C — Footer Dot Row):** use only when the legend has 2-4 color-only items and is secondary to the content — sits just above the footnote line as a single horizontal row
- Legend items must use the **exact same icon, color, or symbol** as they appear in the content — never approximate
- Must be present even if the meaning feels "obvious" — assume the audience is seeing the slide cold

---

## Language

- **Active voice** and **concrete language** — avoid hedging words like "may," "could," "seems"
- Numbers must have units and context — *"$4.2B"* not *"4.2"*; *"↑23% YoY"* not just *"up"*
- Avoid jargon unless the audience is confirmed to use it

---

## Tables

**When to use:**
- When the audience needs to reference or interrogate specific numbers — a chart would obscure precision
- When comparing multiple attributes across multiple options simultaneously (comparison matrix)
- When there is no single dominant trend — the data tells many small stories, not one big one

**Header row:**
- Default style: dark filled header row (navy or dark gray background, white text, bold) — adapts to template if one is provided
- Header text: concise column labels, not sentences

**Row highlighting:**
- Only two rows receive special formatting by default: the **header row** and the **total/summary row**
- Any other highlighted cell or row must have a specific insight reason — never highlight for aesthetics
- Preferred treatments: bold text, accent background color, or a subtle border callout — pick one and apply consistently

**Row styling:**
- Default: clean white rows with light border lines — no alternating row colors unless the template specifies
- Row height: generous enough to avoid cramped text — minimum 0.3" row height

**Font size:**
- **Comparison tables** must stay within the two-font-size rule
- **Data tables** may use a third, smaller font size when density requires it — minimum 9pt, never smaller
- The third size is a last resort — first try reducing columns, abbreviating labels, or splitting across two slides

**Structure:**
- Column widths should reflect content priority — the most important column gets the most space
- Numbers right-aligned, text left-aligned, headers centered or left-aligned to match content
- Units in column header, not repeated in every cell (*"Revenue ($M)"* not *"$4.2M, $3.1M..."*)
- Totals and subtotals clearly separated — bold border or heavier line weight, not just bold text

**Red flags:**
- Table has no insight highlighted → audience will skim and miss the point
- Too many columns to fit legibly → reduce scope or split into two tables
- Numbers have no units → always label
- Header row indistinguishable from body rows → fix contrast

---

## Font Size Rules

**Titles and subtitles are excluded from the body font size rules.** They inherit from the template:
- **Action title:** ~28pt, bold — inherits from template title placeholder
- **Sub-headline:** 16pt (~21px) — inherits from template subtitle placeholder

**Body font size rules (applies to all content inside the content zone):**

Default body font is **12pt**. Use 12pt unless there is too much information (go smaller) or too much empty space (go larger).

Two font sizes are used in the content body — one for section headers, one for detail text:
- **Section headers / chart titles / main takeaway lines:** bold, 14pt (or the larger of the two sizes)
- **Context and detail text / supporting bullets:** regular, 12pt (or the smaller of the two sizes)
- The two sizes should be exactly 2pt apart (14/12, 12/10, 11/9)
- If space is tight → scale both down together, maintaining 2pt gap
- If space is generous → scale both up together to fill the page

**Emphasis items — allowed to break the 2-size rule:**
- Significant callout numbers (hero stats like "$198M") may be displayed at a much larger display size to stand alone visually
- Treat these as display elements, not body text — used sparingly, one or two per slide maximum

**Chart and table exceptions:**
- Axis labels, data annotations, and chart legends may use a third smaller size when data density requires it
- Legends should generally be at the smallest font size on the slide
- Data table cells may use a third smaller size (floor: 9pt) when rows are too dense — comparison tables should not break the 2-size rule

**Hard floor:** chart axis labels, data annotations, legends, and dense table cells: 9pt minimum. All other user-read text (body, bullets, captions, takeaways, sub-headlines): 10.5pt (14px CSS) minimum.

---

## Icons

- Large icons emphasize MECE structure and provide visual breaks between sections
- Icons must be relevant to the content — never decorative
  - Gear wheel → process, work in progress, operations
  - Person/people → stakeholders, team, headcount
  - Chart/graph → data, analysis, metrics
  - Clock → timeline, urgency, deadline
  - Checkmark → complete, approved, confirmed
  - Warning triangle → risk, caution, at-risk item
  - Arrow → direction, change, transition
- **Style-locked per slide.** All icons on a single slide share one style — filled, outline, or duotone. Never mix styles on the same slide
- If one section has an icon, all parallel sections must have icons — never mix icon and no-icon sections
- Size: proportional to the section header, large enough to be immediately recognizable
- Every icon maps to a named concept — icons are structural, not decorative

---

## Formatting Hierarchy

| Element | Spec |
|---|---|
| Action title | ~28pt, bold — inherits from template title placeholder |
| Sub-headline | 16pt (~21px) — inherits from template subtitle placeholder |
| Section headers / chart titles | 14pt, bold (or larger of the two body sizes) |
| Body / detail text | 12pt, regular (default; scale up or down with space) |
| Emphasis callouts (hero stats) | Display size — stands alone, used sparingly |
| Chart axis / data labels | Smallest size needed — minimum 9pt |
| Legends | Smallest font on the slide — minimum 9pt |
| Footnotes / sources | 9-10pt, muted color, bottom left |
| Margins | 0.5" minimum all sides |
| Content block spacing | 0.3" minimum between blocks |

**Font rules:**
- One font family consistently throughout — never mix typefaces across slides in the same deck
- Titles and subtitles follow the template master
- Body content uses exactly two font sizes — 2pt apart
- Font sizes consistent across all slides of the same type — no ad hoc sizing

**Alignment rules:**
- All text boxes, graphs, subtitles, and visual elements must be aligned — nothing should appear placed by eye
- Left-align all body text and supporting content — center only the action title when the template specifies it
- Consistent page numbers in the same position throughout the deck
- Section labels (top-left corner labels identifying deck section) must be correct, consistent, and aligned across all slides

---

## Space Optimization — No Wasted Space

- Every element must earn its place — no empty boxes, no oversized containers
- **Containers stretch to fill available space — this is the most important layout rule.** Content volume does not determine container size; the available slide area determines container size, and content is distributed within it
- Panels and callout boxes stretch to full available height of their zone — never size a container to minimum content and leave the rest empty
- Content must fill the available slide area — visible empty space larger than 0.3" at the bottom of any panel or section is a layout error
- Vertical distribution: when multiple content blocks share a panel or column, distribute evenly across the available height — do not stack at the top and leave the bottom empty
- Internal padding: 0.1-0.15" (approximately 9-14pt) — breathing room but not wasteful
- If content is genuinely sparse: increase font size, increase line spacing, or add a supporting visual element — never leave large empty areas
- Charts use the full available height of their allocated area — bars must be tall enough to read clearly
- Before finalizing: scan each region — if more than 30% empty space with no deliberate whitespace purpose, resize or redistribute

---

## Visual Flow

- The audience's eye should move naturally through the slide — action title first, then primary visual, then supporting detail
- Information hierarchy must be visible at a glance — the most important thing is the biggest, boldest, and highest
- The slide should feel neither too crowded (too much competing for attention) nor too sparse (empty areas create uncertainty about whether content is missing)
- Icons, color, and size contrast are tools for creating visual flow — use them intentionally, not decoratively

---

## PMO Slides — Handled Outside This Rule Set

This rule set is designed for insight-generation slides. PMO slides (recurring status updates, risk registers, decision logs, action item trackers, milestone summaries) are not insight generation — they are recurring operational reports where the consultant fills in a known template week over week.

**PMO slides bypass most of this pipeline.** Slide Helper detects PMO intent from the consultant's opening answer and routes them to template-fill mode: the consultant provides an existing PMO template, Builder replicates the structure with new content, Output delivers. There is no 4-option spread, no Foundation Check, no Visual Model detection — those are insight-generation moves, and they're a category error for PMO work.

**The universal rules here still apply to PMO slides:**
- 9pt floor for chart/data elements; 10.5pt floor for all user-read body text
- Source/footnote placeholder on every slide
- Legend required when colors or icons encode meaning (RAG indicators always need a legend)
- Alignment and font consistency rules
- Every element earns its place — PMO mode does not mean cluttered

**Action title rule relaxes for PMO:** descriptive titles are acceptable (*"Phase 2 is on track; procurement remains the critical path risk"*). A "so what" conclusion title is still preferred when escalating a specific issue. For recurring reports, keep the title structure consistent week over week — the audience is scanning for changes, not being persuaded.

**Everything else PMO-specific** (RAG tables, risk register columns, milestone summary formats, etc.) is *not* codified in rules because those decisions belong to the consultant's existing template. Slide Helper's job for PMO is to replicate what the consultant already has, not impose a format the system decided is correct.

See the "PMO — Handled as Template Fill-In" section at the bottom of `page-types.md` for how Slide Helper handles PMO routing.

---

## Where to Find More

- **Page-type-specific rules** (Insight, Recommendation, Status Update, Process, Data Deep-Dive, Comparison, Executive Summary, Visual Model, Conceptual variants) → `page-types.md`
- **Zone terminology and anatomy** → `glossary.md`
- **Reference layouts** (reference group 01 through reference group 12 PDFs) → `~/.claude/skills/references/`
- **Pipeline architecture** (how Designer, Builder, Output orchestrate) → individual skill SKILL.md files, not this document
