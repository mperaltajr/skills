# Slide Lab Glossary
## Chassis spec for MBB-quality slides

This is the platform spec. Every slide built with Slide Lab inherits the anchor grid, zone vocabulary, spacing rules, and terminology defined here. Use these exact terms in instructions, mockups, QA checks, and user-facing notes — consistent vocabulary prevents drift between agents and across runs.

Pairs with `rules.md` (universal slide rules) and `page-types.md` (per-page-type structure). This document defines *what we call things and where they go*; the others define *what must be true about them*.

**Visual companion:** `references/slide_section_glossary.svg` is an annotated diagram of a consulting slide showing every zone defined below — action title, sub-headline band, body, chart sub-zones, annotation zone, takeaway panel, hero stat, and invariant zone — with pixel positions labelled. Read this alongside the zone vocabulary in section 3 to ground the terminology visually before building any mockup.

Precedence: glossary > layout/page-type files > prior conventions.

---

## 1. Canvas

Slide: **1280 × 720 pixels** (16:9 widescreen).

Equivalents: 13.33 × 7.5 inches; 960 × 540 points; 12,192,000 × 6,858,000 EMU.
Conversion: 1 inch = 96 px = 72 pt = 914,400 EMU.

All coordinates here are in **pixels at 1280 × 720** unless stated. Font sizes are in **points** (inherited from the master template).

---

## 2. Anchor grid

Fixed scaffolding every slide inherits.

- Left margin: **x = 58**
- Right margin: **x = 1222** (58 px from right edge)
- Content width: **1164 px**
- Top of title band: **y = 19**
- Bottom of title band: **y = 100** (compact) or **y = 121** (expanded)
- Top of sub-headline band: **y = 108** (compact only)
- Bottom of sub-headline band: **y = 134**
- Top of body: **y = 151**
- Bottom of body: **y = 662** (full) or **y = 606** (with bottom takeaway strip)
- Top of invariant zone: **y = 672**
- Bottom of invariant zone: **y = 698**
- Gutter between adjacent zones: **24 px** (chassis-controlled zones only — see exception below)

**Master-defined exception:** when a slide layout master defines the body/takeaway-panel split (the `1/4` and `1/3` master layouts), the master's panel region boundary determines body width and panel position. The visual gutter between body and panel is master-defined and wider than 24 px. This applies to the four `chart-with-takeaway-*` layouts. See section 3 (body) and section 4 (layout patterns).

---

## 3. Zone vocabulary

Every named zone the platform recognizes. Use these terms verbatim.

### title band

Holds the **action title** (the slide's so-what — see `rules.md`). Two states:

- **`title-band-compact`** — 1-line title (≤120 chars). x=58, y=19, w=1164, h=77. Paired with a sub-headline band below.
- **`title-band-expanded`** — 2-line title (≤240 chars). x=58, y=19, w=1164, h=102. The sub-headline band is deleted from the slide in this state.

3+ lines forbidden. Font size: template-driven; fallback 28 pt. Title placeholder inherits its width from the slide layout master — do not override per-slide.

### sub-headline band

Scope, unit, period, or qualifying condition. Used only when the action title fits on one line.

- x=58, y=95, w=1164, h=26 (compact state only).
- 1 line max (≤120 chars).
- Font: template-driven; fallback 16 pt.
- In `title-band-expanded`, this band is deleted (not hidden — removed from the slide).

### body

The primary content area. Named `body` (not "content area" or "primary region"). Holds any visual: chart, table, matrix, pyramid, cycle, funnel, framework, process flow, diagram, image. **What fills the body is a content decision, not a layout decision.** The takeaway panel is not part of the body.

Body coordinates depend on the layout pattern (see section 4):

- **Full-width**: x=58, y=151, w=1164, h=511. Or h=456 with a bottom takeaway strip.
- **With `takeaway-quarter`**: x=58, y=151, w=832, h=511. Master `1/4` defines the panel region from x=922; body must end at or before x=922. Visual gutter to the takeaway panel is master-defined (~65 px).
- **With `takeaway-third`**: x=58, y=151, w=731, h=511. Master `1/3` defines the panel region from x=822. Visual gutter to the panel is master-defined (~59 px).
- **Dual-section (left)**: x=58, y=151, w=570, h=511. Chassis-controlled — 24 px gutter.
- **Dual-section (right)**: x=652, y=151, w=570, h=511.

### chart sub-zones

Exist only when the body contains a chart. Positioned 16 px in from the body's edges.

- **chart title** — body top-left, 16 px in from top and left. 14 pt bold default. Describes what the chart shows (data + unit + scope), not the insight (the action title carries the insight).
- **legend** — body top-right, 16 px in from top and right. Required when colors or icons encode meaning.
- **x-axis** and **y-axis** — inside body's chart area.
- **axis label** — adjacent to each axis. Required on every chart.

Never put the legend at the bottom of the chart (the PowerPoint default — always override).

When the body holds a table, matrix, diagram, or other non-chart visual, these sub-zones don't apply; the content defines its own internal structure.

### annotation zone

A floating overlay inside the body, positioned at the data point or element being annotated.

- No fixed coordinates; placement follows the annotated element.
- ≤10 words.
- Max 1 per slide.
- Dashed border preferred for visual distinction from chart elements.
- Color: accent or red for negative/warning callouts.

### takeaway panel

Side or bottom panel with the slide's so-what — concise takeaway text, optionally with hero stat and bullets. Three variants:

- **`takeaway-quarter`** — x=955, y=151, w=267, h=511. Sits inside the `1/4` master's panel region. Use when takeaway has ≤3 bullets.
- **`takeaway-third`** — x=848, y=151, w=374, h=511. Sits inside the `1/3` master's panel region. Use when takeaway has ≥4 bullets or longer content.
- **`takeaway-bottom-strip`** — x=58, y=614, w=1164, h=48. Use with a full-width body when a side panel would waste real estate.

For quarter and third variants, panel coordinates and gutter to body are master-defined, not the chassis 24 px rule.

The takeaway panel is not part of the body.

### hero stat

Optional sub-zone inside the takeaway panel. One prominent number summarizing the slide.

- Centered horizontally in the panel, 16–24 px below panel top.
- Hero descriptor (small text under the number, e.g., "in Q3 savings") sits directly below, centered, standard line-height.
- Hero stat + descriptor together form the top block of the panel.
- Below the hero block: 24 px gap, then takeaway body text (left-aligned at 16 px panel padding), 24 px gap, then bullets (left-aligned).
- Font size: template-driven; typically 2–3× takeaway body size. Range 28–48 pt.
- Max 1 hero stat per slide.

When absent, the takeaway panel begins with a header label (e.g., "Takeaway / Insight Panel") instead.

### bucket header / body / footer

Sub-zones inside each bucket in the `multi-bucket` layout (see section 4).

- **bucket header** — optional process icon (circular, centered horizontally, top of bucket) + bucket headline (14 pt bold default, centered) + divider line 16 px below the headline.
- **bucket body** — bullets or supporting text, left-aligned at 16 px padding, 12 pt body default.
- **bucket footer** — per-bucket takeaway, separated by divider 16 px above the footer text.

### footnote zone

Part of the invariant zone. Bottom-left of every slide.

- x=58, y=672, w=1164, h=13.
- Starts with a numeric reference (e.g., `1.`) matching a body superscript.
- **8 pt, fixed.** Never flexes.
- Placeholder: `[Insert Footnote]` until user replaces.

### source line

Part of the invariant zone. Directly below the footnote.

- x=58, y=685, w=1164, h=13.
- Attribution for data shown on the slide.
- **8 pt, fixed.**
- Placeholder: `[Insert Source]` until user replaces.
- Multiple sources: comma-separated on one line; stack on two lines if needed.

### page number

Part of the invariant zone. Bottom-right.

- x=1172, y=685, w=50, h=13.
- 8 pt.
- Auto-generated by the builder. Never moves between slides.

### draft watermark

**Prohibited.** Do not add DRAFT, CONFIDENTIAL, or any review-gate chrome to any slide. The invariant zone holds only sources, footnotes, and the page number. Review status is tracked outside the slide, not stamped on it.

---

## 4. Layout patterns

Eight canonical patterns. The chassis layouts. Models may compose new patterns using the anchor grid, section 3 zones, and section 6 rules — but every new pattern must respect the chassis.

| Pattern ID | When to use | Source slide |
|---|---|---|
| `chart-with-takeaway-quarter-hero` | Chart + short takeaway (≤3 bullets) + hero stat | Slide 1 of `0__Layouts.pptx` |
| `chart-with-takeaway-quarter` | Chart + short takeaway, no hero stat | Slide 2 |
| `chart-with-takeaway-third-hero` | Chart + longer takeaway (≥4 bullets) + hero stat | Slide 3 |
| `chart-with-takeaway-third` | Chart + longer takeaway, no hero stat | Slide 4 |
| `dual-section` | Two parallel items side-by-side; sub-headline carries the takeaway | Slide 5 |
| `chart-with-bottom-takeaway` | Full-width body + bottom takeaway strip | Slide 6 |
| `multi-bucket` | 2–5 (or more, with two-row splits) parallel items: phases, pillars, options | Slide 7 |
| `full-section` | Full-width body, no takeaway. Matrices, frameworks, diagrams, structured text. | Slide 8 |

For `multi-bucket`: 2–5 buckets in one row, ≥180 px each. 6+ split into two rows (6→3+3, 7→3+4, 8→4+4). Buckets within a row are symmetrical; partial rows are centered. Row 2 starts at row-1-bottom + 24 px.

---

## 5. Palette roles

Slide design output never contains literal hex codes, font names, or font sizes. Only role names. The client's master template fills the variables at render time.

### Background
- `--bg-default`, `--bg-zone-tint`, `--tint-10`, `--tint-60`

### Text
- `--text-primary`, `--text-on-dark`, `--text-muted`

### Accent
- `--hero-color` (primary accent — action title, hero stat, primary chart series)
- `--accent2` (secondary accent)

### Rule
- `--rule-color`, `--rule-style` (solid or dashed)

### Chart series
- `--chart-series-primary`, `--chart-series-secondary`, `--chart-series-muted`

### Draft
- `--draft-color` (red)

### Font
- `--font-title`, `--font-body`, `--font-display`

### Size
- `--size-title` (28 pt default), `--size-hero` (template-driven), `--size-header` (14 pt bold), `--size-body` (12 pt), `--size-caption` (10.5 pt), `--size-footer` (8 pt fixed)

### Weight
- `--weight-bold`, `--weight-regular`

---

## 6. Density and spacing rules

### Font size ladder

Step through pairs (header / body) until content fits:

1. **Default**: 14 pt bold / 12 pt
2. **Tight**: 12 pt / 10 pt
3. **Floor**: 11 pt / 9 pt

Never below the floor. If content doesn't fit at the floor, reduce content.

Source and footnote: always 8 pt, fixed. Only text below 9 pt.

### Font size budget

Max 2 font sizes per slide. 3 acceptable in rare cases. 4 never. Source/footnote at 8 pt is invariant and doesn't count against the budget.

### Bullet rules

- **Count**: as few as possible while MECE. No fixed maximum. Collapse bullets that don't carry distinct ideas.
- **Words**: aim for ≤7. Longer allowed when truncation would lose meaning.

### Action title rules

- 1 line: ≤120 chars. Sub-headline allowed (1 line max).
- 2 lines: ≤240 chars. Sub-headline removed.
- 3 lines: never. Rewrite until it fits.

### Padding inside a zone

**Minimum 16 px** on all four sides of any filled zone (takeaway panel, bucket, body when tinted). Content never closer than 16 px to a zone edge.

### Gutter between zones

**24 px** between any two adjacent zones — when the chassis controls both zones. Applies to: multi-bucket column gutters, multi-bucket row gutters, dual-section gutter.

**Exception — master-defined splits**: when a slide layout master defines the body/panel split (`1/4`, `1/3`), the master controls gutter. Do not override with the 24 px rule.

Padding + gutter stack: total distance from bucket 1 content to bucket 2 content = 16 + 24 + 16 = 56 px.

### Minimum column width

**180 px**. Caps multi-bucket at 5 per row. Below 180 px, content (headers, bullets, icons) loses semantic readability.

### No empty bottom

Bottom edge of content (body, panel, or strip — whichever extends furthest) must end within **40 px** of invariant zone top (y=672). If the gap exceeds 40 px, fix in this order:

1. Grow content (extend height, add a bottom takeaway strip).
2. Increase text size (step up the ladder).
3. Center vertically within the zone — distribute whitespace symmetrically above and below content.

Prefer symmetrical vertical whitespace over asymmetrical. Content pinned to the top with empty space below reads as unfinished.

### Dividers

A divider line may separate sections within any zone when whitespace alone isn't enough. Runs full inner width (zone-left + 16 px to zone-right − 16 px), sits 16 px from adjacent content on both sides, uses `--rule-color` / `--rule-style`.

### Visual element roles

Every visual element on a slide plays exactly one role:

1. **Structural** — sequence/phase. Process icons + step labels. Connector arrows between process steps.
2. **Status** — value vs. benchmark. RAG, Harvey balls, directional arrows (↑↓) with color. Pair with a legend when meaning isn't obvious from context.
3. **Layout** — separation between zones. Whitespace, tinted backgrounds, color blocks, dividers. Weight matches intent — bold only when the audience's eye should stop there.

Constraints:

- Each visual element must do unique work. If two elements encode the same status for the same data point, delete one.
- Icon style consistent within a slide (all filled, all outline, or all duotone — never mixed).
- Connector arrows (structural) and directional arrows (status) are different jobs; never interchangeable.
- Layout-style separators: weight matches what the audience should do. Whitespace = "these are distinct"; light divider = "these are parallel"; tint = "these are grouped"; bold = "stop here, this is different."

---

## 7. Invariant zone rules

The invariant zone spans the bottom 26 px (y=672 to y=698). Every slide. No exceptions.

- **Builder-enforced.** The builder inserts and positions invariant elements automatically.
- The designer never places design content in the invariant zone.
- The designer never removes, moves, or resizes invariant elements.
- The user replaces `[Insert Footnote]` and `[Insert Source]` placeholders with real content before handoff.


Coordinates in section 3.

This zone is the platform's trust boundary — it guarantees every shipped slide has citation, pagination, and a review gate regardless of what happens in design.

---

## 8. Terminology lock

Use these exact terms. Synonyms are forbidden.

- **action title** — not "headline", "slide title", "title", "key message".
  > In the narrative brief (storyline-helper), the slide's assertion is called "governing thought." In the built PPTX and in Phase A mockups, the same concept is the "action title." These are the same thing at different pipeline stages — the term changes at the Phase A → Phase B boundary.
- **sub-headline** — not "subtitle", "tagline", "subheader", "deck".
- **body** — not "content area", "primary region", "chart zone", "visual area".
- **takeaway panel** — not "callout box", "sidebar", "insight box", "right rail".
- **hero stat** — not "big number", "headline number".
- **bucket** — not "column", "section", "card", "panel", "pillar", "phase", "step" (when referring to grouped items in `multi-bucket`).
- **annotation zone** — not "callout", "overlay", "flag".
- **invariant zone** — not "footer area", "bottom area", "page furniture".
- **draft watermark** — not "DRAFT flag", "watermark", "review marker".
- **footnote zone** — not "footnote area", "note".
- **source line** — not "attribution", "source note".
- **page number** — not "pagination", "page marker".
- **legend** — not "chart legend", "key" (when inside a chart).
- State IDs: **`title-band-compact`**, **`title-band-expanded`**.
- Takeaway variants: **`takeaway-quarter`**, **`takeaway-third`**, **`takeaway-bottom-strip`**.
- Layout pattern IDs: **`chart-with-takeaway-quarter-hero`**, **`chart-with-takeaway-quarter`**, **`chart-with-takeaway-third-hero`**, **`chart-with-takeaway-third`**, **`dual-section`**, **`chart-with-bottom-takeaway`**, **`multi-bucket`**, **`full-section`**.
- Visual element roles: **structural**, **status**, **layout**.

---

## What changed from prior glossary (zone names retired)

These terms appeared in the previous glossary but are no longer used. They map to current terms below; do not introduce new uses.

- **section label** — removed. Section identification is handled by the master template if needed; not a chassis zone.
- **content zone** / **primary region** / **secondary region** / **tertiary region** — replaced by `body`, `takeaway panel` (with three variants), and `multi-bucket` layout. The old vocabulary conflated "where content goes" with "which layout pattern" — the new vocabulary keeps these separate.
- **Visual Model layout** — removed as a layout pattern. Pyramids, cycles, 2×2s, hub-and-spoke, etc. are body content, not their own layout. Use `full-section` (or `chart-with-bottom-takeaway` for an insight strip) with the visual inside the body. The reference deck `11_Visual Models.pptx` provides body-content templates that inherit a chassis layout.
