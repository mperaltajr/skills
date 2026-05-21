# Visual Treatment Library — Per-Layout Composition Recipes

This file is the visual companion to `phase-a-rules.md`. Where phase-a-rules.md gives the four hard *principles* (canvas fill, takeaway dominance, structural variation, story-first), this file gives the per-layout *moves* — concrete composition recipes for each layout family in the deck.

**Why this file exists:** the chassis spec tells you where things go. The phase-a-rules tell you what makes a slide good. Neither tells you that a three-column parallel slide should default to tinted card backgrounds with a thin accent1 top border, or that a quadrant framework should fill the "target" quadrant in accent1 to make the composition do the persuading. That layer of guidance is what separates a slide that passes the chassis spec from a slide that looks MBB.

**How to use this file:** consult during Phase A mockup authoring once you know the layout family. Each entry lists 1–4 sub-variants with explicit "when to use" criteria — the criteria matter more than the recipes themselves. Picking the right variant is what makes the slide feel deliberate.

**Not a decision tree — a vocabulary.** Read the insight, feel the content, then pick the variant that serves. Active decisions — background fill, tint application, where hero typography sits, where contrast accents land — are not optional polish. They are the design.

---

## Palette roles — ACN Graphik template defaults

Run `build_slide.py --print-theme <template.pptx>` to get the exact hex values for the current deck. The slot names below are stable; the hex values differ per client template.

| Slot name | ACN Graphik default role | Typical hex |
|-----------|--------------------------|-------------|
| `accent1` | Brand purple — primary fill for headers, card backgrounds, dominant shapes | `#4D148C` |
| `accent2` | Hero contrast accent — milestone markers, the single "active" element, CTA highlight | `#FF6600` |
| `dk1` | Near-black body text | `#1A1A2E` |
| `dk2` | Secondary dark — borders, muted lines, supporting rules | `#333366` |
| `lt1` | Slide background white | `#FFFFFF` |
| `lt2` | Light tint wash — panel backgrounds, alternating row fills | `#F3EEF9` |

**In CSS:** always use exact hex values from `--print-theme` output — never approximations. **In python-pptx:** use `<a:schemeClr val="accent1"/>` to inherit the correct value at render time rather than hardcoding hex.

---

## Cover / Divider

- **Use for:** slide 1 of a deck, section transitions, major pivots
- **Structure:** large title left-aligned or centered at 35–55% slide height; supporting line or context at 55–65%; minimal other content
- **Visual treatment — reach confidently:** full-bleed dark-background mode is the default, not the exception. Fill the slide with accent1 (or primary tint 90%). Title in white. Use the hero contrast accent (accent2) for a sub-label, section marker, or single word that acts as the eye-anchor. A thin horizontal rule in the contrast accent separating title zone from supporting zone is a common and effective move.
- **Typography:** title 28–36pt (hero numeral slot), subtitle 16pt, footer 9pt
- **Variants:**
  - Full-bleed dark with hero contrast accent (most common)
  - Split layout — dark panel on one side, light tinted panel on the other (effective when the cover needs to hold both a context statement and an ask)
  - Centered white-background with large typographic number + section name (use when the deck's visual rhythm needs a breather)

## Insight / Finding

- **Use for:** one clean insight as the slide's job
- **Structure:** action title + supporting evidence (chart, data table, or structured text) + optional so-what callout
- **Visual treatment:** this layout is the workhorse and usually sits on white. The composition move is the callout — if a "so what" panel is present, give it a tinted background (primary tint 10% wash, or primary tint 90% dark mode if the so-what is the climax of the slide) so it reads as conclusion, not just more text.
- **Typography:** palette standard; callout lead line may use the callout emphasis slot (14–16pt)
- **Variants:**
  - Title + chart dominating (when chart IS the argument — keep background white, let the chart breathe)
  - Title + 2-column evidence (comparative insights)
  - Title + hero stat + supporting context (hero stat uses hero numeral slot 28–48pt, optional tint 10% wash behind it)

## Three-column parallel (and 4-column — same logic)

- **Use for:** parallel findings, patterns, pillars, options (n=3 or 4, and genuinely MECE)
- **Structure:** title + N equal columns (width = (100 − 2 × gutters × N) / N, ~2% gutters) + optional synthesis bar at bottom
- **Visual treatment — this is where decks most often go flat:** do not default to plain columns on white. Choose one of these treatments based on the argument:
  - **Tinted card backgrounds** — each column is a primary tint 10% wash rectangle extending the full column height, 13pt body inside, optional accent1 top border. **Use when the content is evidence supporting a higher claim, not the claim itself.** *This is the most common variant — pick this one unless another fits better.*
  - **Dark card headers + light body** — top 25–35% of each column is a filled accent1 rectangle with white column-header text and a hero numeral (01, 02, 03 in hero numeral slot); bottom is white with 13pt body. **Use when the slide is a MECE *declaration* — the visual weight of the dark headers says "these three things, parallel, exhaustive."**
  - **Rule + label + body (no filled card)** — thin accent1 rule on top of each column, label in 14–17pt bold (section header slot), body 13pt. **Use when the deck already has heavy dark-mode slides and this one needs to lighten the rhythm.**
  - **Two-tier cards** — top tier is "what we're building" (dark or tinted header + short description), bottom tier is "why it matters" (thin accent1 rule + bold claim + supporting line). **This is the move that fills the full slide height without padding** — each column has real content top-to-bottom, not content-then-whitespace.
- **Critical structural rule:** column headers and numeral badges in SEPARATE side-by-side sub-zones within each column, OR stacked with numeral *above* header with deliberate spacing. Numeral overlapping header is a bug.
- **Typography:** column headers 14–17pt bold (section header slot), body 13pt, numeral badges 28–48pt (hero numeral slot)

## Two-column with insight panel (60/40 or 55/45)

- **Use for:** finding + implication, evidence + recommendation, detail + synthesis, context + ask
- **Structure:** title + left column (60%, evidence) + right panel (40%, the so-what)
- **Visual treatment:** right panel defaults to dark-background mode — full accent1 fill, white title, white body, hero contrast accent (accent2) for a "today's ask" or "the bet" mini-header. The visual contrast IS the point: left side is the reasoning, right side is the conclusion that matters. Left side stays white (or primary tint 10% wash if the evidence is a grouped set).
- **Typography:** palette standard; right-panel lead line may use callout emphasis slot (14–16pt); right-panel hero accent (if present — e.g., "Today's Ask" label) uses hero contrast accent color in section header slot

## Headline + chart

- **Use for:** quantitative insights where the chart IS the argument
- **Structure:** action title stating the insight declaratively + large chart (60–75% height) + 1–2 line takeaway
- **Visual treatment:** this layout works on white. The chart itself carries the visual weight. Use accent1 for the primary series, primary tint 60% for secondary, muted gray for reference lines. If the chart has a single "the point" data point, mark it with accent2 (the hero contrast accent) — a single orange dot on a purple line is more eloquent than any annotation.
- **Chart:** static PNG generated from a Python script (matplotlib, plotly, or similar) or inline `<svg>` in the mockup. Always rendered as an image in PPTX, never a native chart object.
- **Typography:** title 20pt, chart labels 11pt, takeaway 13pt (or 14–16pt callout emphasis if the takeaway is the "so what"), source 9pt
- **Companion Excel:** generate a .xlsx with the chart data so the consultant can remake the chart in ThinkCell for client delivery

## Visual Model

Visual Model is a **page-type**, not a chassis layout. Pyramids, cycles, 2x2s, hub-and-spoke, etc. are body content that lives inside a `full-section` chassis layout (or `chart-with-bottom-takeaway` if a so-what strip is needed). See `page-types.md` Section 8 for the three-signal trigger, shape sub-taxonomy, shape rationale rule, and design lies to avoid.

- **Visual treatment — the biggest composition lever in the deck:** Visual Model body content benefits more from composition than any other content type because the shape IS the argument, and a flat shape reads as a diagram; a composed shape reads as a model. **Reach for dark-background mode when the model is the centerpiece of the deck** (the "here's how it fits together" slide). Use tinted backgrounds for the element boxes so they read as distinct but related. Use the hero contrast accent (accent2) for the connecting arrows or the one element that's "active" now vs. the ones that are "future." Element labels in section header slot (14–17pt bold), descriptions in 11pt.
- **Typography:** action title 20pt (chassis title band), element labels 14–17pt bold (section header slot), element descriptions 11pt, optional caption 13pt
- **Build with python-pptx shape primitives:** rectangles, ovals, connectors (auto-arrows), etc., placed inside the body zone of `full-section`

## Comparison (2xN or NxN matrix)

- **Use for:** head-to-head evaluation against criteria
- **Structure:** row headers (criteria) × column headers (things being compared); cells contain evaluation marks, text, or ratings
- **Visual treatment:** header row in dark accent1 fill with white text (section header slot, 14–17pt bold). Alternate row fill: white / primary tint 10% for readability on wide tables. The "winning" column or row may be highlighted with a thin accent2 left-border and bold body text.
- **Build with python-pptx table APIs** — do NOT hand-build tables with textboxes (the v3.4.1 walker already enforces this for `<table>` elements in mockups)

## Framework (2×2, 3×3, quadrant)

- **Use for:** analytical classification with 2 dimensions
- **Structure:** axes with labels, quadrants with titles, items placed within
- **Visual treatment:** the "target" quadrant (the one the argument wants the audience to land in) gets an accent1 fill with white content; other quadrants get primary tint 10% wash or white. This turns the framework from a neutral 2×2 into an argued 2×2 — the composition is doing the persuading.
- **Consult reference:** open `05_Frameworks.pdf` — placement of labels matters a lot in these

## Roadmap / Timeline

- **Use for:** sequence of phases, gates, milestones
- **Structure:** horizontal bar(s) with phase segments, gate markers, milestone annotations
- **Visual treatment:** phase bars in accent1 (or graduated: tint 60% → tint 90% → accent1 to show progression). Gate markers in accent2 (the hero contrast accent) so they read as distinct checkpoints, not just dividers. Current/completed phases vs future phases distinguished by fill (solid) vs outline (stroked only). Phase labels in section header slot (14–17pt bold).
- **Typography:** phase labels 14–17pt bold, annotations 11pt, dates 9pt
- **Consult reference:** `07_Roadmaps.pdf`

## Swim Lane

- **Use for:** multi-actor parallel processes where the story is who does what, and when handoffs occur between roles or teams
- **When to use vs. Flowchart:** Use Swim Lane when actor tracks and sequence are the story, and handoffs are implied by adjacency. Use Flowchart when decision points and connector arrows are the story.
- **Variants:**
  - **A — Horizontal lanes (default):** actors stacked vertically as rows, time flows left to right. Use when the sequence has a clear left-to-right narrative (phases, timeline).
  - **B — Vertical lanes:** actors arranged as columns, flow moves top to bottom. Use when there are 2–3 actors and you want a taller, more compressed layout (fits short processes).
  - **C — Two-actor compressed:** no lane background, actor position (top vs. bottom half) implies ownership. Use when lane headers would consume too much real estate.
- **Visual treatment:** Lane header cells in a solid brand-color column (accent1 dark or light tint depending on template weight). Lane body backgrounds in alternating tints (accent1 tint 5–10% / white). Step boxes: dark fill (accent1) with white text for the primary actor's steps; lighter tint fill for supporting actors. Lane boundaries: 1px rule in the brand color.
- **Typography:** lane header 11–14px bold (white text on dark fill, or accent1 on white), step label 11–12px bold, subtext 9–10px
- **Phase B note:** SVG connector arrows for cross-lane handoffs do not survive Phase B. Warn the user per the Phase A mandatory warning in page-types.md Section 17.
- **HTML pattern:** See `page-types.md` Section 17. No reference PDF — use the HTML build pattern directly.

## Flowchart

- **Use for:** decision-driven processes, branching logic, conditional paths, and multi-step pipelines with explicit arrows
- **When to use vs. Swim Lane:** Use Flowchart when decisions and visible arrows between steps are the story. Use Swim Lane when parallel actor tracks and adjacency handoffs are the story.
- **Variants:**
  - **A — Linear flow with one decision:** left-to-right sequential steps, single YES/NO gate in the middle. Use for approval workflows, pass/fail gates.
  - **B — Multi-branch decision tree:** a diamond with three or more branches (YES/NO/ESCALATE). Use for complex conditional logic (risk triage, routing logic).
  - **C — Loop-back process:** arrows that return to an earlier step (rework cycle, iteration). Use for quality gates, agile sprints, iterative feedback loops.
- **Visual treatment:** Process boxes in accent1 dark fill with white text (primary steps). Decision diamonds in white with accent2 border (so they read as a distinct shape type). Loop-back and branch arrows in muted gray or accent2. Lane backgrounds (if swim-lane hybrid) follow Swim Lane treatment above.
- **Typography:** step label 11–12px bold, decision label 10–11px bold, YES/NO branch label 10px (accent2 for YES, muted red for NO)
- **Phase B limitation — mandatory user warning:** SVG connector arrows do NOT appear in the built PPTX. Before generating the Phase A mockup, tell the user: "Connector arrows will not appear in the built PPTX — you will need to add them manually in PowerPoint after delivery." See page-types.md Section 18 for the full mandatory warning text.
- **HTML pattern:** See `page-types.md` Section 18. No reference PDF — use the HTML build pattern directly.

## Structured text

- **Use for:** dense content that needs to be read, not visualized
- **Do not force a composition treatment** (cards, charts, icons) when the argument lives in the reasoning itself — prose slides exist for a reason.
- **Variants:**
  - **A — Sub-headed prose:** action title + flowing prose body broken by bold sub-headers every 4–6 lines. Use for executive summary narratives, strategy rationale, finding walkthroughs where the full argument needs to breathe.
  - **B — Icon-anchored parallel rows:** 3–5 rows, each with a process icon (36–48px, accent1), a bold heading, and a 2–3 line description. Rows separated by a subtle hairline rule. Use for parallel pillars, capability areas, or workstreams where each item is structurally equal but the audience will read each independently.
  - **C — Two-column text + callout panel:** left column holds the prose/bullets (60% width), right column is a tinted stat callout, pull-quote, or key number (40% width, accent1 tint fill). Use for "finding + implication" or "analysis + so-what" structures where one element needs to dominate visually.
- **Visual treatment:** White background. Sub-headers and row headings in accent1 color (section header slot: 14–17pt bold). Body text in dark muted (not pure black). Callout panel (Variant C) in accent1 tint 10–15% with a 4px left accent bar in full accent1. Avoid walls of 13pt body with no scanning hierarchy.
- **Typography:** title 20–22pt, sub-headers / row headings 14–17pt bold (accent1), body 13pt, callout stat 28–36pt bold
- **When to use this:** executive summary narratives, finding walkthroughs, content where the argument is the reasoning itself

## Org chart / Team / Governance

- **Use for:** hierarchies, reporting structures, governance models
- **Visual treatment:** the topmost level (C-suite, steerco) in accent1 dark fill with white text; middle tiers in primary tint 60%; leaf-level boxes in primary tint 10% or white with accent1 outline. This makes hierarchy readable at a glance without depending on position alone.
- **Consult reference:** `10_Org Charts Team Governance.pdf`
- **Use python-pptx grouped shapes** for the boxes and connectors

## Quote / Pull-quote

- **Use for:** customer or stakeholder testimonial, emphasizing a verbatim statement
- **Structure:** large quote text, attribution, optional context/setting
- **Visual treatment:** full-bleed dark-background mode is often the right call here — the quote wants to land with weight. Quote in white italic, attribution in hero contrast accent (accent2) for the name, muted white for the role/company. Alternative: white background with a large colored quote mark (accent1) as the visual anchor.
- **Typography:** quote 18–24pt italic (callout emphasis slot, scaled up), attribution 11pt

---

## Composition defaults — the rhythm of a deck

A good deck has a visual rhythm. Roughly:

- **Slide 1 (cover):** full-bleed dark-background
- **Middle slides (body):** mix of white-background insight slides and composed (tinted cards, dark panels, dark headers) slides — not all one or the other
- **Pivot slides (one-big-idea moments):** dark-background mode
- **Closing slide (ask or next steps):** usually dark-background for weight, or two-column with dark right-panel "ask"

If you find yourself building 6 slides in a row that are all "white background + three columns of 13pt text," stop. The deck has lost its rhythm. Go back to at least one of them and reach for a composition treatment.

The corollary: **dark-background is for moments of weight** — covers, pivots, the closing ask, the occasional Visual Model centerpiece. It is NOT the default for body slides. A deck that goes dark on every slide is exhausting to read. The default for evidence and finding slides is *tinted cards on white* or *white with deliberate accent1 typography*, not dark mode.

---

## Quick reference — picking a variant

**⚠ STOP: This table is a tiebreaker, not an answer.** The criteria in the sections above are authoritative. Use this table only when no specific "when to use" criterion in the body of this file fires for your slide. If your slide content matches a named criterion above (MECE declaration, so-what is the climax, model is the deck centerpiece, etc.), follow the criterion — do not consult the table. A deck that mechanically runs this table on every slide will lose rhythm.

| If the slide is... | Starting point if no criterion fires | Reach for dark when... |
|---|---|---|
| Cover or divider | Dark accent1 full-bleed | Always (this is the default) |
| Three-column evidence/options | Tinted card backgrounds | The three things ARE the claim (MECE declaration) |
| Two-column finding + ask | White left, dark accent1 right panel | Always (the contrast IS the point) |
| Insight + chart | White background | The so-what is the climax → tint or dark the callout |
| Visual Model | Tinted element boxes on white | The model is the deck centerpiece |
| Comparison matrix | Dark header row, alternating tinted rows | Always (header row only) |
| Framework / 2×2 | Tinted quadrants, accent1 target quadrant | The "winning" quadrant (always one quadrant) |
| Roadmap / timeline | Graduated accent1 phase bars | Never full-dark unless it's a section opener |
| Swim Lane | Tinted lane rows, accent1 lane headers | Never full-dark — lanes need to be distinguishable |
| Flowchart | Dark-fill boxes (accent1), white-border diamonds | Never full-dark — decision shapes need contrast against background |
| Structured text | White background, accent1 sub-headers | Never (prose stays light) |
| Org chart | Accent1 top tier, descending tints | Top tier only |
| Quote | Full-bleed dark accent1 | Default — quotes want weight |

---

## Stylistic defaults for client-branded decks

These defaults apply when building slides that sit alongside a client's existing branded deck. Apply them on the first pass to reduce revision rounds.

**Before choosing any treatment, look at the existing slides in the client template.** Note: header treatment (gradient vs solid, height, colors), panel background weight (full fills vs light tints), footer style, and body font sizes in use. Match those patterns — do not impose a heavier or lighter treatment than the client is already using.

**Color weight — default to light tints when the master is already heavy.** When the client template has a strong colored header and footer, body content panels should use light tints (~5–10% of the brand color), not full fills. Full brand-color fills on panel backgrounds combined with a colored header and footer create visual fatigue.

- In-scope / positive panels: light tint of primary brand color (~5%)
- Out-of-scope / risk panels: light tint of accent color (~5%)
- Accent rule on top of panel: full brand color (3–5px bar)
- Use heavy fills only for: a single dark header row in a comparison table, the "winning" quadrant in a 2×2, or a "so-what" panel in a finding slide

**Bullet format default** — for scope, comparison, and structured list slides:
```
• Bold topic — one-line plain description
```
Bold the topic label. Follow with an em dash and a concise descriptor. One line per bullet. No sub-bullets.

**Slide framing — every blank-mode slide should include three elements:**
1. **Header bar** (~50px tall, top): solid brand color or gradient matching the client's slide master
2. **Footer bar** (~44px tall, bottom): contains confidentiality notice and page number
3. **Title zone** (between header and content): eyebrow label in small caps / uppercase, main title, subtitle/context line in muted color

Without these three elements, slides look unfinished relative to the client's existing deck.

---

## Whitespace Judgment

Not all whitespace is a problem. The test is whether it's deliberate or accidental.

**Deliberate whitespace** — used intentionally to frame or emphasize:
- Cover slides and section dividers: the large element IS the content; empty space around it creates impact
- Hero-number slides: a single large stat with generous breathing room is a design choice, not a gap
- Minimalist layouts where restraint is the visual argument

**Accidental whitespace** — occurs when content is sparse and layout defaults leave gaps:
- Bottom third of slide is empty because flex flow didn't fill it
- Side panel stops short, leaving a visible bottom gap
- A centered element is too narrow, leaving wide empty margins on both sides
- Supporting content is thin and doesn't reach the footer clearance line

**The test:** *"If a viewer's eye naturally lands in the empty space and finds nothing, it's accidental. If the empty space frames something, it's deliberate."*

### Recovery patterns for accidental whitespace

When content is genuinely thin, apply one of these patterns rather than leaving the bottom zone empty:

1. **Bottom takeaway strip** — `position:absolute; bottom:52px` — a one-line pull-quote, key number, or action callout in the footer zone
2. **Full-height side panel** — extend the right-column panel to full canvas height (720px), even if it means adding a supporting context block or visual accent
3. **Stat anchor** — promote a supporting number to a large hero-scale display (48–64px) below the main content block
4. **Context timeline strip** — a compact (60px tall) horizontal timeline at the bottom showing where this slide fits in the project or argument sequence
5. **Visual model promotion** — if the slide has a small inline diagram, enlarge it to occupy the empty zone

### Vertical and Horizontal Rhythm (summary)

These rules are defined in full in `phase-a-rules.md` Rules 8–9. Quick reference:

- Hero element: 40–60% of canvas height (288–432px)
- Centered single element: ≥60% of canvas width (≥768px)
- Two-column splits: 50/50, 60/40, or 40/60 only
- Side panels: always full canvas height

### Reading Path

Defined in full in `phase-a-rules.md` Rule 10. The three patterns: top-to-bottom, left-to-right, hub-and-spoke. If the eye lands in empty space, the path is broken.

---

## Cross-references

- `phase-a-rules.md` — the four hard *principles* (canvas fill, takeaway dominance, structural variation, story-first). Read first; this file picks up where it leaves off.
- `glossary.md` — chassis spec, anchor grid, the eight canonical chassis layouts, palette role definitions (`accent1`, `accent2`, primary tints).
- `page-types.md` — page-type catalog. Visual Model in particular (Section 8) is a page-type that *inherits* a chassis layout, not its own layout.
- `rules.md` — universal MBB rules.
- `references/` — the 12 reference PDFs and PPT files referenced inline above (`05_Frameworks.pdf`, `07_Roadmaps.pdf`, `10_Org Charts Team Governance.pdf`, `11_Visual Models.pdf`, etc.).
