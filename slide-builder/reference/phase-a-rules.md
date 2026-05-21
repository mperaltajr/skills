# Phase A Rules — How to Generate MBB-Quality Mockups

This file is the operational checklist for Phase A (mockup authoring). Read it before generating any HTML mockups, and apply it to every slide × every option.

**Why this file exists:** earlier versions of Slide Lab produced mockups that looked weak — empty white space, takeaways buried in tiny pills, three "options" that were the same idea with different decoration. The chassis spec defined what good slides look like, but the model wasn't applying it. This file makes the rules operational.

**Parent skill:** `slide-builder/SKILL.md` — the full pipeline (Phase A → Phase B → reviewer pass → delivery). This file covers Phase A authoring rules only.

**Canvas spec — non-negotiable:** every slide div must be exactly `width:1280px; height:720px` (16:9 widescreen). This is the standard modern PowerPoint dimension. 1024×768 is the obsolete 4:3 "Standard" format — never use it.

**Companion file:** `visual-treatment-library.md` is the per-layout *recipe* book — which composition variant (tinted cards, dark headers, full-bleed, etc.) to pick for each layout family, with explicit "when to use" criteria. This file gives the *principles*; that file gives the *moves*. Read this one first; consult that one once you know the layout family for each slide.

---

## The four hard rules — every slide, every option

### Rule 1 — Canvas Fill

**A 1280×720 slide is a canvas, not a document.** Documents flow top-down and stop when content runs out. Slides compose across the entire frame.

**"Intentionally used" does not mean "filled to the footer line."** White space is allowed — even below the 30% mark — when it is symmetric, balanced, and the layout reads as complete. The failure mode Rule 1 targets is *dead* white space: content that stopped because the designer ran out of things to say, not because the design was finished.

**Rule 1 passes when ANY of these is true:**
- The bottom zone has content (a strip, callout, stat, or panel that anchors it)
- The white space is **symmetric** — both columns or all panels end at the same height, creating equal bottom margins that read as deliberate breathing room. A two-column comparison where both sides end at 60% height is a design choice, not a canvas fill failure.
- The slide type genuinely calls for minimal content (divider, big-number, quote) and the main visual is dominant enough that the white space reads as "designed"

**Rule 1 fails when:**
- One column is full and another is sparse, leaving asymmetric dead space
- Content fills only the top 35–40% and the bottom half is obviously incomplete
- The slide was never designed around the bottom zone at all — it just ran out

**Dead space levers — try in this order (micro before structural):**

Work through the list from top to bottom. Most dead space problems are solved by levers 1–4 without adding any new structural elements. Structural additions (levers 5–7) are the last resort, not the first move.

**Typographic levers (change nothing structural — just adjust sizing and spacing):**
1. **Increase font size.** Body text at 14px → 16px → 18px → 22px. Three bullets at 16px occupy ~120px; at 12px they occupy ~70px. Going from 14px to 18px on a 4-bullet column recovers ~80px immediately.
2. **Increase line-height / padding between elements.** Add `line-height:1.6` or increase `padding` between sections. This spreads existing content over more vertical space without changing any words.
3. **Increase element size.** If the slide has an icon, chart, image, or visual model — make it bigger. A chart at 300px tall vs. 220px tall fills the canvas without adding content.

**Content levers (change what is on the slide):**
4. **Add or expand bullet points.** If the brief has more supporting detail that was cut, put it back. If bullets are terse, expand each to a full thought (one line of ~60–70 characters). Adding two bullets to a 3-bullet column fills roughly 80–100px.
5. **Make content more concise, then reuse the space differently.** If the existing text is wordy, trim it — then use the freed vertical space to increase font size or add a callout. This is the "tighten the writing, then breathe it out" move.
6. **Reposition elements vertically.** If all content is clustered in the top 50%, spread it. Move a callout or label lower, add top-padding to push content toward the vertical center, or use `justify-content:space-between` to distribute items across the full column height.
7. **Reposition elements horizontally.** Widen a narrow column to give text more room (wider columns → shorter line-wraps → more vertical height). Narrow an oversized column if one side is overflowing into the other's space.

**Structural additions (add new elements — only when levers 1–7 don't solve it):**
8. **Add a bottom strip** with the takeaway/page-context/next-step (full-bleed, color-blocked, ~80–120px, `position:absolute; bottom:52px`).
9. **Add a stat or callout** — a metric, a short punchy phrase, or an action item pinned to the bottom of a column using `margin-top:auto`.
10. **Pull supporting context into a side panel** (right column, ~30–40% width, takes full canvas height).
11. **Promote a timeline / status / checklist** that shows the progression this slide is part of.

**Do NOT add decorative boxes or containers purely to fill space.** A colored rectangle with no content purpose makes the white space more visible, not less. If the layout is balanced and symmetric, leave the breathing room — it is correct.

### Rule 2 — Takeaway Dominance

**The slide's so-what must be the visually dominant element.** A reader scanning at arm's length should know what the slide says before reading any body text.

The takeaway is dominant when at least two of these are true:
- It's the largest type on the slide (typically 48–96pt for a number; 22–28pt for a phrase)
- It uses an accent color that nothing else uses
- It sits in a color-blocked panel (purple/dark band, or a colored card)
- It's centered or has the strongest position on the page (top-left for English readers, or hero-strip)

Anti-patterns that bury the takeaway (and what to do instead):
- ❌ Takeaway as a small "pill" floating in a header band → ✓ Make it a hero number/phrase in its own dedicated zone
- ❌ Takeaway in body text inside a paragraph → ✓ Pull it out as an isolated callout
- ❌ Takeaway only stated in the slide title → ✓ Repeat it visually (the title is for the eye-track entry, the visual is for the actual brain)
- ❌ Multiple competing "takeaways" on one slide → ✓ Pick one. The others are supporting evidence

### Rule 3 — Structural Variation Between Options

**Three options for one slide must vary on the layout family axis, not just the structural or decorative axis.**

Layout family variation (required):
- Each option must belong to a **different layout family** — branching-tree, split-panel, hero-number, waterfall, Q&A-grid, timeline, kanban, comparison-matrix, etc.
- "Three different card arrangements" is NOT variation. Left-aligned cards, three-column cards, and grouped-row cards are all the same layout family (grid). They must look like completely different slide types.

Decorative variation (NOT acceptable):
- Option A: list with circles · Option B: list with cards · Option C: list with dividers
- Option A: blue header · Option B: orange header · Option C: purple header
- Option A: 4 columns · Option B: 4 columns wider · Option C: 4 columns with icons

Within-family variation (NOT acceptable — same failure mode as decorative):
- Option A: left-aligned cards · Option B: three-column cards · Option C: grouped-row cards → all grid family
- Option A: horizontal tree · Option B: vertical tree · Option C: indented tree → all tree family
- Option A: bar chart · Option B: bar chart with annotations · Option C: horizontal bar chart → all chart family

Cross-family variation (acceptable):
- Option A: branching-tree (nodes + connectors) · Option B: split-panel (two zones, contrast) · Option C: hero-number (large stat dominant)
- Option A: data-as-chart (SVG bar/waterfall) · Option B: data-as-comparison-matrix (rows × columns) · Option C: data-as-Q&A-grid (three questions answered)
- Option A: chronological timeline · Option B: kanban (Ready / In-progress / At-risk) · Option C: two-panel with decision callout

**Before writing any HTML, name the layout family for each option:**
```
Option A layout family: [e.g., branching-tree]
Option B layout family: [e.g., split-panel]
Option C layout family: [e.g., hero-number-with-evidence]
```
If all three families are not different, stop. Pick three genuinely different families before writing a single line of HTML.

A useful heuristic: if you swapped the colors and removed all text, would the three options still look like completely different slide types? If no, the families are not different enough. Try again.

### Rule 4 — Story-First Structure

**Every slide answers: what does this slide want the audience to know, decide, or do?** The structure of the slide should serve the story, not the other way around.

**Consult `page-types.md` first to identify the page type. Then consult `visual-treatment-library.md` for the composition recipe for that page type.**

Before writing any HTML for a slide:
1. State the **governing thought** in one sentence (the so-what)
2. Identify the **page-type** from `page-types.md` (executive summary, data-with-takeaway, comparison, decision, divider, etc.)
3. Pick the **dominance hierarchy**: what's primary visual? secondary? tertiary?
4. Allocate the canvas to those three levels of dominance — primary gets the most space and strongest position, etc.
5. *Then* write CSS

Without this sequencing, the model defaults to filling-content-then-decorating, which is exactly how you get the bad mockups.

---

## Rule 4A — Audience Reading Path and Skeleton Adaptation

**A slide layout must create a logical reading sequence for an audience member who knows nothing about this deck.** Skeletons are starting points, not rigid templates. When a skeleton's default arrangement would force the audience to read evidence before context, or supporting information before primary content, adapt the skeleton. A skeleton that was followed faithfully but communicates badly is a failure.

### The reading path test — run this before finalising any layout

Trace the eye path a cold reader takes, top-to-bottom, left-to-right:

1. **Does the audience encounter framing before detail?** They need to know *what phase*, *what category*, *what dimension* before they read the specific items that belong to it. If a label or header that frames a group appears *after* or *below* the group it frames, the layout is backwards.

2. **Does the audience encounter primary content before supporting infrastructure?** Legends, keys, source labels, and footnotes are supporting infrastructure — they exist to help decode the main content, not to be read first. If supporting infrastructure occupies a full row at the same visual weight as the primary content, it is mis-ranked.

3. **Can the audience read the slide top-to-bottom without having to scan backwards to resolve what something means?** If following the natural reading path requires the reader to jump backwards to an earlier zone to make sense of what they just read, the layout fails.

### Common violations and how to fix them

| Violation | Root cause | Fix |
|---|---|---|
| Phase/category labels appear below or inside the group they frame | Skeleton placed labels inside the flow element for aesthetic symmetry | Move labels above the element; they frame what follows, so they must precede it |
| "What we need" band above the chevron, "what you'll see" band below | Content split above and below a middle element forces two backwards eye-jumps | Move both bands below the chevron: first the phases (context), then asks, then deliverables — linear top-to-bottom |
| RAG/status legend taking a full-width row | Legend treated as a content section when it is supporting infrastructure | Compact corner position (top-right, subordinate size, no background panel); never a full-width row |
| Recommendation or conclusion at the top of the slide | Skeleton placed "key message" at top without considering the evidence hasn't been seen yet | Conclusion/recommendation anchors at the bottom; audience reads the evidence first, then arrives at the resolution |
| Milestone labels inside the chevron, below the phase name | Skeleton stacked two items inside the shape | Milestone labels live *above* the chevron strip as column headers; inside the chevron, only the phase name remains, vertically centered |

### The adaptation rule

When the content and a skeleton's default layout conflict, **adapt the skeleton to fit the content** — do not force the content into the skeleton's default. Specifically:

- **Move framing elements above what they frame.** Column headers, phase labels, category names, milestone markers: if they describe a group, they must visually precede the group.
- **Move both related bands to the same side of a flow element.** If two content bands relate to phases (e.g., asks and deliverables), place both below the phase strip — not one above and one below.
- **Reduce the visual weight of supporting elements.** Legends, keys, source lines: compact, small, right-aligned or footnote-zone. They should not compete with the table header or section heading for visual prominence.
- **Switch from single-text to bullet lists when content is inherently multi-item.** If the brief has two or more distinct items per cell, render them as bullets. Forcing three items into a single unwrapped string creates a run-on that the audience has to parse — bullet structure does that work for them.
- **The skeleton is a library of proven patterns, not a set of rules.** Shift vertical positions, reorder bands, change label placement whenever the default arrangement would force a reader to scan backwards.

---

## Rule 5 — Editorial Emphasis Is a Layout Mandate

**When the narrative brief names a specific visual format in the editorial emphasis field, that format IS the layout — not one option among many.**

Editorial emphasis is not a theme or a content description. It is a direct instruction about what the dominant visual must be. If the brief says "value tree dominant," the mockup must show a branching diagram with node boxes and connector lines. Cards, columns, and tables that convey the same hierarchy implicitly do NOT qualify.

### Editorial emphasis → layout family mapping

Read this table before writing any HTML. If the brief's editorial emphasis matches a keyword below, the mockup must use the named layout family. No exceptions.

| If the brief says... | The mockup MUST use... | What does NOT qualify |
|---|---|---|
| "value tree" / "issue tree" / "driver tree" / "logic tree" | Branching diagram — node boxes connected by lines/arrows, reading left-to-right or top-to-bottom. SVG or div-based connectors. | Cards in columns, grouped rows, indented lists |
| "waterfall" / "bridge" / "from→to" / "walk from X to Y" | Waterfall bridge — sequential bars showing additions/subtractions from a starting value to an ending value | Simple bar charts, two-column before/after |
| "contrast" / "before and after" / "old vs new" | Split-screen — two clearly demarcated zones (left/right or top/bottom) with a visual pivot or divider between them | Side-by-side bullets, two-column table |
| "numbers dominant" / "hero stat" / "the number is the story" | One or two large numerals at 48pt+, with supporting detail clearly subordinate in size and position | Stats in a card grid at equal size |
| "the evidence" / "show the data" / "chart tells the story" | Chart or data visualization (SVG bar, line, scatter, stacked bar) as the primary canvas element, ≥50% of slide area | Tables, bullet lists with numbers |
| "the ask" / "decision needed" / "CTA" | Decision prompt or call-to-action as the largest, most prominent visual element — often dark-panel dominant | Decision buried at slide bottom or in a footnote |
| "org chart" / "hierarchy" / "governance" | Top-down hierarchy diagram with boxes and connecting lines. Levels visually distinct by fill or size. | Nested bullets, numbered list |
| "roadmap" / "timeline" / "phases" | Horizontal phase bars with gate markers, milestone annotations, and date anchors | Vertical list of phases, text-only sequence |
| "2x2" / "quadrant" / "matrix" / "framework" | Four-quadrant grid with labeled axes. Target quadrant highlighted. Items placed within quadrants. | Comparison table, four cards in a row |

### What to do when the brief names a format you're unsure how to build

1. Look up the format in `visual-treatment-library.md` — it has composition recipes for every layout family above.
2. Build all three options within that layout family, varying on depth/framing/emphasis — not by switching to a different family for one option.
3. If genuinely unsure how to render a specific format (e.g., SVG connector lines for a tree), default to the simplest working version (div boxes with a CSS border-right connector) rather than substituting a different layout.

---

## Rule 6 — Position Audit Before Any Absolute-Positioned Edit

CSS `top`/`left`/`height` values on a 1280×720px canvas are geometry, not style preferences. Guessing them produces loops. Before editing any `position:absolute` coordinate, compute the position explicitly and output this block:

```
POSITION AUDIT:
Canvas: 1280×720px
Panel bounds: top=[N]px, bottom=[N]px, height=[N]px
Element rendered size: ~[W]×[H]px  (font-size × line-count, or known element type)
Proposed placement: top=[N]px → element bottom lands at y=[N]px
Clearance to footer: [N]px (must be ≥52px)
Intent match: YES / NO — [reason if NO]
```

Do not write the edit until "Intent match: YES." If NO, recalculate. The loop cost of skipping this is always higher than the 30 seconds it takes.

---

## Rule 7 — Bottom-Anchor Elements Must Use `position:absolute`

**Never rely on flex flow to position the last content element above the footer.**

The footer bar (`position:absolute; bottom:0; height:44px; z-index:10`) paints over anything that gets too close. Flex container height is browser-dependent — in one rendering the impact strip clears the footer by 8px; in another it overlaps by 2px. This inconsistency is invisible in the HTML preview (the CSS gives the footer a high z-index) but surfaces in both preview and PPTX as overlap.

**Any full-width bottom-anchor element (strip, callout bar, summary row) must be absolutely positioned:**

```html
<div style="position:absolute; bottom:52px; left:48px; right:48px;
            background:#333333; padding:12px 24px; border-radius:3px; text-align:center;">
  <!-- content -->
</div>
```

`bottom:52px` = footer height (44px) + 8px minimum clearance. Set the content zone's `bottom` to `strip_height + 52px` so panels above stop well clear of the strip.

---

## Rule 8 — CSS Features Not Supported by the Builder

The builder's DOM walker reads bounding boxes and computed styles but does not simulate the full browser rendering pipeline. The following CSS features produce correct HTML previews but **broken PPTX output**:

| CSS used in mockup | What breaks in PPTX | Correct alternative |
|---|---|---|
| `border-radius: 50%` | Shape renders as a rectangle — border-radius is CSS-only | Use `<svg><circle ...></svg>` for any circle that must appear in the PPTX |
| `transform: translateY(-50%)` / `translateX(...)` | Element position is computed from untransformed bbox — text lands at wrong coordinates | Use explicit `position:absolute; top:Xpx; left:Ypx` instead |
| `z-index` | PPTX layer order follows DOM insertion order, not z-index — higher z-index does NOT render on top | Place elements in DOM order: background elements first, foreground elements last |
| `::before` / `::after` pseudo-elements | Not real DOM nodes — completely invisible to the walker | Replace with `<span>` elements inline |
| `display:grid` with fractional rows | Grid row heights are not computed at walk time | Use explicit `height:Npx` on each row or convert to flex |
| `background-image: url(...)` | Background images are not captured as picture shapes | Use `<img>` elements with explicit width/height inside the container |

**Pre-build check**: `build_slide.py` scans for `border-radius:50%` and `transform:translate` before running Playwright and warns if found. Fix before building — do not rely on the post-build QA to catch these.

---

## Rule 9 — DOM Order Is PPTX Layer Order

**CSS `z-index` has no effect in the built PPTX.** The builder emits shapes in the order the DOM walker visits them (roughly document order). PowerPoint renders shapes in insertion order — the last shape inserted is visually on top.

**Consequence:** an element that appears visually on top in the HTML preview (via high `z-index`) will appear BEHIND earlier DOM elements in the PPTX if it comes first in the DOM.

**Rule:** The DOM order of your elements must match the intended visual stacking order:
1. Background fills and panel shapes → first in DOM
2. Chart images or large visual elements → next
3. Text boxes and labels → after their containers
4. Overlay callouts, badges, takeaway strips → last in DOM

**Check:** For any element that must appear visually above another, verify it also comes later in the HTML source. If a takeaway banner must cover a chart, the banner `<div>` must appear after the chart `<div>` in the markup.

---

## Rule 10 — No Sibling `<span>` Elements as Direct Flex Children

**The builder creates a separate PPTX text box for each leaf text-bearing element.** When two `<span>` elements sit as direct children of a `display:flex` container, the builder measures their bounding boxes independently and places them as separate text boxes. Flex's `justify-content:center` or `gap` pushes them to approximately the same x-coordinate — the result in PPTX is two text boxes painted on top of each other.

**Collapse label+value pairs into a single container:**

```html
<!-- WRONG — sibling spans as flex children → overlapping text boxes in PPTX -->
<div style="display:flex; justify-content:center; gap:20px;">
  <span style="color:#ccc;">Combined value at risk</span>
  <span style="color:#FF6600;">~$24.3M</span>
</div>

<!-- CORRECT — single div, inline spans, no flex gap -->
<div style="text-align:center;">
  <span style="color:#ccc;">Combined value at risk&nbsp;&nbsp;</span><span style="color:#FF6600;">~$24.3M</span>
</div>
```

Reserve flex containers for structural layout (panels, columns, rows between slides). Do not use flex to position text runs within a single visual unit.

---

## Rule 11 — Vertical Rhythm

**Gate behavior: Rule 8 is blocking.** An option with more than 40% empty space must be regenerated, not shown. See the per-option checklist — "If NO: do not save this option" is a hard instruction.

The hero element (the dominant content block — a chart, a large stat, a key visual model) should occupy **40–60% of the canvas height** (288–432px of the 720px canvas).

- Supporting content cascades below the hero, filling to the footer clearance line (bottom:52px)
- Deliberate whitespace above the hero is acceptable (breathing room between title and content)
- Empty space below the supporting content is not acceptable — it reads as an unfinished slide

**Recovery patterns when content is thin:** Apply the dead space levers from Rule 1 in order — typographic first (font size, line-height, element size), content second (expand bullets, reposition, rebalance columns), structural additions last (bottom strip, stat callout, side panel, timeline). The full ordered list is in Rule 1. Key patterns specific to hero layouts:
- Increase the hero element size — a chart or stat that fills 35% of canvas height should fill 50%
- Promote a supporting stat to a large hero number positioned below the main content
- Add a takeaway strip (`position:absolute; bottom:52px`) with a pull-quote or key callout
- Extend a side panel to full canvas height to fill the right zone

### Sparse-content trigger — multi-column layouts

When a multi-column layout (2–5 columns) has **fewer than 5 bullet points per column at body font size (14–16px)**, the column content will not fill the canvas. This is a known failure mode — sparse column content reliably produces a blank bottom half regardless of card background color.

**Critical:** Using `align-items:stretch` to give cards a full-height background is NOT a fix on its own. A card with a background that fills 500px but text that only fills 150px still looks broken — the background color makes the empty space MORE visible, not less. A stretched card requires a bottom anchor.

**Required — do ALL of the following when this trigger fires:**

1. **Increase body font size** to 16–18px. Three lines at 16px occupy ~120px; at 12px they occupy ~70px. Larger font recovers 50px per column immediately.

2. **Add a bottom anchor per column** — a stat, metric, short callout, or action phrase pinned to the bottom of each card using `margin-top:auto`. This is mandatory whenever `align-items:stretch` is used. Without it, the stretched card just shows more empty space.
   ```html
   <!-- Inside each stretched card div -->
   <div style="margin-top:auto; padding-top:12px; border-top:1px solid #C8B8E8;
               font-size:20px; font-weight:700; color:#4D148C; text-align:center;">
     $12M saved
   </div>
   ```
   If real data isn't available, use a short punchy phrase that reinforces the column header ("Cuts 40% of noise", "Needs structure first", "One message wins").

3. **Use full-height card boundaries WITH the bottom anchor above** — set `align-items:stretch; height:520px` on the column container, give each column a background. The card edge + bottom anchor together fill the canvas intentionally.
   ```html
   <div style="display:flex; gap:12px; align-items:stretch; height:520px;">
     <div style="flex:1; background:#F8F4FF; border-radius:6px; padding:20px;
                 display:flex; flex-direction:column;">
       <div class="number">01</div>
       <div class="title">Too much to say</div>
       <div class="body">Body text here...</div>
       <div style="margin-top:auto; padding-top:12px; border-top:1px solid #C8B8E8;
                   font-size:18px; font-weight:700; color:#4D148C;">Knowing what to cut</div>
     </div>
   </div>
   ```

**The gate test for sparse-content recovery:** After applying recovery patterns, the text+bottom-anchor content should occupy at least **50% of each card's height**. If the bottom anchor pushes above 50% of height and the top content fills 30%+, the card reads as intentional. If the middle 40% of the card is still empty, the recovery did not work — increase font size further or lengthen the body text.

A mockup that triggers this rule and shows more than 40% empty space in any column must not be saved — regenerate with the patterns above applied.

---

## Rule 12 — Horizontal Distribution

- **Centered single element:** must span at least **60% of canvas width** (768px of 1280px). Elements narrower than this appear stranded — increase font size, padding, or width.
- **Two-column layouts:** use 50/50, 60/40, or 40/60 splits only. Do not use 70/30 — the narrow column becomes a caption column, not a peer column, and the layout reads as unbalanced.
- **Side panels:** must extend to **full canvas height** (720px). A side panel that stops short leaves a bottom gap that draws the eye to empty space.
- **Multi-column bucket layouts (3–5 columns):** columns should be equal width. If one column has notably more content, consider splitting it into its own slide.

---

## Rule 13 — Reading Path

Before finalizing any mockup option, identify the intended reading order and confirm the layout supports it:

- **Top-to-bottom:** title → hero content → supporting detail → takeaway/footer. Default for most insight slides.
- **Left-to-right:** used in process flows, timelines, and comparison layouts. The eye must move naturally from left to right without backtracking.
- **Hub-and-spoke:** a central element with radiating detail. The hub must be visually dominant; spokes should be equidistant and equal-weight.

**Check:** If a viewer's eye would naturally land in an empty area and find nothing, the reading path is broken. Fix by repositioning content or applying a Rule 8 recovery pattern.

---

## Rule 14 — Process Icons

Process icons (see `reference/icon-vocabulary.md`) may be included **only in multi-column bucket layouts** with 2–5 structural columns, where each column represents a distinct conceptual theme (phase, workstream, pillar, capability).

**Do not use icons:**
- In tables, lists, or data-heavy layouts
- In single-column slides
- When the bucket header already has strong visual differentiation (color bands, numbering)

**Implementation:** Use `<div class="process-icon" data-icon="[name]">` and leave the div body empty — Phase B replaces it with the bundled PNG from `slide-builder/icons/<name>.png`. Optionally add a simple placeholder shape in the HTML for visual preview only; it will not appear in the PPTX. See `reference/icon-vocabulary.md` for the full HTML pattern and icon vocabulary.

---

## Phase A Gate — mandatory before showing mockups to the user

**This is a hard gate, not a guideline.** Mockups do not get shown to the user until every slide × every option passes every item below. A silent internal check is not sufficient — the gate result must be written out visibly (see "Gate output format" at the bottom of this section) so the user can see that it ran.

**Why visible output matters:** A silent checklist is self-policed and gets skipped under time pressure. Writing the gate result out loud forces the model to actually evaluate each item, and gives the user evidence that the check happened. If the gate output is missing, the check did not run.

**Layout-aware exemption:** Rules 1 and 2 are mostly enforced by the corporate layout itself — check them, but a layout-aware slide that fills its template placeholders correctly usually passes automatically. Rules 3 and 4 always apply regardless of mode.

### Per-option checklist

```
SLIDE [N] OPTION [X]:

——— Canvas fill & visual dominance ————————————————————————
□ Bottom 30% of canvas is intentionally used (Rule 1)
  — "intentionally used" includes symmetric white space: if both columns / all panels end at
     the same height and the equal bottom margin reads as deliberate breathing room, this passes.
     Do NOT add decorative boxes just to fill the zone — that fails Rule 1 worse than leaving it.
  — layout-aware: verify the template's own layout fills the frame
  — authoring gate: a <!-- CANVAS FILL CHECK --> comment must appear before the closing </div>
     and must answer "yes" (including "yes — symmetric layout, balanced white space") before the
     next slide is written. "No" = asymmetric dead space or content that stops at 35-40% with no
     layout rationale. This is not optional — the pre-check alone does not enforce Rule 1 across
     multi-pass Edit calls.
□ Takeaway is the visually dominant element (Rule 2)
  — layout-aware: verify the dominant placeholder carries the so-what

——— Structural variation & story ————————————————————————
□ Layout family differs from the other two options — named above (Rule 3)
  — "three card arrangements" is NOT variation; must be different family types
□ If editorial emphasis names a specific format, this option uses that format (Rule 5)
  — "value tree" = branching diagram; "waterfall" = bridge bars; etc.
□ Page-type is named in a comment and matches the story (Rule 4)
□ Layout family + recipe variant named in a comment, matching a prescription
  in visual-treatment-library.md

——— Brand fidelity ———————————————————————————————————
□ Every brand color hex in the mockup CSS exactly matches a hex from
  --print-theme output (not a close approximation — an exact match)
□ Theme fonts declared in CSS using the template's font family name
  from --print-theme (with a system fallback stack)
□ No CSS pseudo-elements (::before / ::after) used for any visible content
  — pseudo-elements are invisible to the DOM walker and will silently
  disappear from the PPTX output
□ Minimum font size in CSS is 14px (= 10.5pt in PPTX). No visible text below this.

——— Vertical rhythm & canvas fill depth ————————————————
□ Hero element occupies 40–60% of canvas height (Rule 8)
  — If NO: do not save this option. Apply Rule 8 recovery patterns and re-check.
□ For multi-column layouts: does each column/panel fill to within 60px of the footer clearance line?
  — PASS requires: text+bottom-anchor content occupies ≥50% of card height AND no column
    has more than 40% empty space in the middle zone.
  — align-items:stretch alone does NOT pass this check. A stretched card with content
    only in the top 30% and no bottom anchor FAILS — the background makes the empty
    space more visible, not less. Each stretched card must have a bottom-anchored element
    (stat, callout, or short phrase) using margin-top:auto inside a flex-direction:column card.
  — If NO: a recovery pattern is REQUIRED before saving. State which pattern was applied.
  — "The content is sparse" is not an exemption — it is the trigger condition for a recovery pattern.

——— Composition & reading path ——————————————————————
□ Horizontal distribution follows Rule 9 splits; side panels extend to full height
□ Reading path identified and confirmed — no empty zones on the intended path (Rule 10)
  — Reading path must have a visual anchor in the bottom 30% of the canvas. If it does not,
    apply a bottom-zone recovery pattern (takeaway strip, stat callout, or timeline strip).
  — If NO anchor after applying a recovery pattern: do not save this option. Regenerate.
□ Process icons (if present) are in multi-column bucket layouts only, using div.process-icon[data-icon] (Rule 11)

——— Conclusion / recommendation position ————————————————
□ If this slide contains a recommendation, conclusion, resolution, or so-what:
  it is anchored at the BOTTOM or RIGHT of the content zone — never at the top.
  Rationale: audience reads evidence first and arrives at the resolution last.
  A recommendation at the top pre-empts the supporting structure that justifies it.
  — PASS: recommendation is a bottom-anchored strip, a right-column panel, or the
    final row of a structured layout
  — FAIL: recommendation is the first visible element below the title, appears in
    a top panel, or is placed above any supporting evidence
  — If FAIL: move the recommendation element to the bottom anchor position and
    reorganise supporting content above it. Do not show this option until fixed.
```

### Per-slide checklist

```
SLIDE [N]:
□ Three layout families named BEFORE any HTML was written — all three are different
□ If brief editorial emphasis names a specific format, all options use that format
  (options vary in framing/depth/emphasis, not by switching to a different format)
□ All three options pass the per-option checklist above
□ Story (governing thought) is consistent across all three options
  — they tell the same story differently, not different stories

——— Action title gate (check ONCE per slide, before writing any option HTML) ———
□ Governing thought / action title fits on ONE line at the template's heading font and size.
  Estimate: title font size × ~0.55 avg char width × char count ≤ usable title width.
  Rough caps by template class:
    — 24pt serif bold (e.g. Georgia): ~85 chars on a standard 12" title zone
    — 24pt sans (e.g. FedEx Sans):    ~80 chars
    — 22pt condensed sans:            ~78 chars
  If the title EXCEEDS the cap: FLAG and rewrite before writing any HTML.
  Do NOT shrink the font. Do NOT allow the title to wrap to two lines.
  A wrapped title is a failed slide — it signals the governing thought was not
  sharpened to one idea. Rewrite, don't accommodate.
```

### Pre-save file checklist — run before writing mockups.html to disk

```
FILE:
□ All options are in ONE file: _session/mockups.html
  — do NOT create separate files (option-a.html, option-b.html, etc.)
□ Each option is a <div class="slide"> with BOTH:
    data-slide-index="N"   (integer, 1-based)
    data-option="A"        (single letter: A, B, or C)
□ File is saved to <session-folder>/_session/mockups.html
  — NOT AppData\Temp, NOT the project root, NOT a system path
□ Every slide div contains a `<!-- CANVAS FILL CHECK: yes/no — [reason] -->` comment before its closing `</div>`. This is separate from the gate block at the top of the file — both are required.
□ After saving, output the full absolute Windows path in the reply:
    C:\Users\...\sessions\YYYY-MM-DD Topic\_session\mockups.html

IMAGE PATHS:
□ <img> tags OUTSIDE data-chart containers: use base64 data URIs (preferred) or
  just the filename. Never use "_session/" as a path segment — mockups.html lives
  inside _session/, so src="_session/x.png" resolves to _session/_session/x.png
  (broken). Scan for src="_session/" before saving; if found, fix immediately.

□ <img> tags INSIDE data-chart="true" containers: use relative filename ONLY —
  never base64. Base64 prevents Playwright from computing the element's bounding
  box (flex container collapses to zero height), producing a blank screenshot and
  an empty white rectangle in the PPTX. The HTML preview will show a broken image
  icon for these — that is expected and acceptable. The PPTX output will be correct.

  Summary:
    Outside data-chart  →  base64 data URI            (preview ✓, build ✓)
    Inside  data-chart  →  relative filename only      (preview ✗ icon, build ✓)

WHITE BODY FILL:
□ Every slide contains an explicit white rectangle covering the body zone,
  placed immediately after <div class="hdr"></div>:

    <div style="position:absolute; top:50px; left:0; right:0;
                bottom:44px; background:#ffffff;"></div>

  Without this, any client template with a dark slide master (e.g. purple) bleeds
  its background color through all areas not covered by a named shape. This is
  invisible in HTML preview (the .slide CSS rule hides it) but surfaces in every
  PPTX build. The white fill is a structural default — not optional.
```

LAYOUT-AWARE WIRING (required for templates with 20+ named layouts):
□ Every slide div carries data-layout-master and data-layout-index attributes.
  Identify the correct layout by running --catalog-layouts and finding the layout
  with a TITLE (1) placeholder at y ≈ 40px and a light background.
  Example: data-layout-master="2" data-layout-index="4"
□ The governing thought element carries data-placeholder="title":
  <div class="tz-title" data-placeholder="title">...</div>
  Without this, the title is a floating overlay shape — it will NOT follow layout
  changes when the user switches layouts in PowerPoint. All other elements
  (header, content zone, footer) remain as overlays; only the title needs wiring.

NO NATIVE TABLE ELEMENTS:
□ No <table>, <thead>, <tbody>, <tr>, <td>, or <th> elements appear anywhere in
  slide content divs. Native tables return h=0 in Playwright's layout engine inside
  positioned containers — place_table() silently skips them, producing a blank slide
  with no error. All tabular data must use div-based rows (display:flex per row).
  Scan for "<table" before saving; if found, convert to div rows before continuing.

HEIGHT BUDGET VERIFIED:
□ For every slide option, confirm the height arithmetic before saving:
    [section]: top Npx + height Npx = bottom Npx
    [section]: top Npx + height Npx = bottom Npx
    Last section bottom ≤ 668px  (content area = 50px–668px; footer = 668px–720px)
  If any section exceeds 668px, fix before saving. A canvas fill comment that says
  "fills canvas" without this arithmetic is not a valid check.

CHART DATA ATTRIBUTE:
□ Every <div data-chart="true"> that contains real (non-placeholder) chart data
  must have a data-chart-data attribute with valid JSON. Without it, build_slide.py
  silently skips xlsx generation — the user receives a PPTX with no companion file.

  Required JSON shape (single series):
    {
      "title": "Sheet name in xlsx",
      "categories": ["Cat A", "Cat B", "Cat C"],
      "series": [{"name": "Series 1", "values": [1.0, 2.0, 3.0]}],
      "notes": "Optional: context, reference lines, caveats"
    }

  Multi-series (clustered bar, grouped line, etc.):
    {
      "title": "Sheet name in xlsx",
      "categories": ["Q1", "Q2", "Q3", "Q4"],
      "series": [
        {"name": "Actual",   "values": [4.2, 5.1, 4.8, 6.0]},
        {"name": "Forecast", "values": [4.0, 5.3, 5.0, 6.2]}
      ],
      "notes": "Both series appear as separate columns/lines in the companion xlsx."
    }

  Each object in "series" produces one series row in the xlsx. The chart PNG is
  generated from data you already have — the JSON is for the xlsx handoff only.

  Copy the source data from the brief's "Chart data:" field at chart generation time.
  Do not leave this step for Phase B — if the attribute is absent during the build,
  no recovery is possible without a full rebuild.

FOOTER CLEARANCE:
□ Any bottom-anchor element (impact strip, callout bar, summary row) must use
  position:absolute with an explicit bottom value, NOT flex flow:

    <div style="position:absolute; bottom:52px; left:48px; right:48px; ...">

  The footer occupies bottom:0 to bottom:44px. An explicit bottom:52px gives 8px
  guaranteed clearance regardless of content height above. Flex layout cannot
  reliably produce this clearance — the flex container's total height is
  browser-dependent and may land the last item only 4–6px above the footer,
  which causes the footer (z-index:10) to paint over it in both preview and PPTX.

□ If the slide has an absolute bottom-anchor strip (impact bar, summary bar, etc.):
  Set the content zone's bottom to strip_height + 52px — not just 52px.

    <!-- Strip is 80px tall → content zone bottom = 80 + 52 = 132px -->
    <div class="cz" style="position:absolute; top:50px; left:48px; right:48px; bottom:132px;">

  Without this co-adjustment, flex panels flow into the strip's z-index shadow.
  Failing to set the co-adjusted bottom value is the same failure class as
  bottom:0 on the strip itself — it just happens higher up the stack.

SIBLING SPAN CHECK:
□ Scan each slide for <span> elements that are direct children of a display:flex
  container. If found, collapse them into a single inline run:

    <!-- WRONG — two sibling spans as flex children -->
    <div style="display:flex; justify-content:center; gap:20px;">
      <span>Label</span>
      <span>Value</span>
    </div>

    <!-- CORRECT — single div with inline spans -->
    <div style="text-align:center;">
      <span style="...">Label&nbsp;&nbsp;</span><span style="...">Value</span>
    </div>

  The builder creates a separate PPTX shape per element. Flex-positioned sibling
  spans get independent bounding boxes that overlap in the output. Reserve flex
  containers for structural layout (panels, columns, rows) — not for positioning
  text runs within a single visual unit.
```

If any item fails: fix before presenting the file to the user. Do not present separate files as the deliverable.

### What to do when an item fails

Do not show the user a known-failing option. Regenerate it.

| Failing item | Fix |
|---|---|
| Bottom 30% empty | Add a bottom strip (takeaway/decision/context, ~80–120px) OR extend a side panel to full height OR promote a timeline/status bar |
| Takeaway not dominant | Promote to hero panel — largest type, accent color, dedicated zone. Read Rule 2 again. |
| Options too similar | Name three genuinely different structural approaches. Use the "remove colors and text — would they still look different?" test. |
| Page-type unclear | Assign one from `page-types.md`. If no page-type fits, the slide is doing too many things — narrow the story. |
| Color hex mismatch | Re-run `--print-theme` and copy exact hex values. No approximations. |
| Pseudo-element found | Replace with a real `<span>` element or switch to direct python-pptx pipeline. |
| Font below 14px | Increase to 14px minimum. Prefer 16px for body text. |
| Footer clearance violation | Convert bottom-anchor element to `position:absolute; bottom:52px`. Set `.cz { bottom: [strip_h + 52]px }`. |
| Sibling spans in flex | Collapse into a single `<div style="text-align:center">` with inline spans and `&nbsp;` separation. |

### Gate output format — required before saving mockups.html

Write this block as an HTML comment at the top of `_session/mockups.html` before saving for user review. The block must be present — its absence means the gate did not run.

```html
<!--
PHASE A GATE — [Deck name] — [Date]
========================================
Slide 1 "[Slide title]"
  Structural approaches named first: YES — A=hero-number | B=waterfall-bridge | C=Q&A-grid
  Option A: canvas fill ✓ | takeaway dominant ✓ | structurally distinct ✓ | page-type: data-with-takeaway ✓ | colors ✓ | fonts ✓ | no pseudo-elements ✓ | font floor ✓
  Option B: canvas fill ✓ | takeaway dominant ✓ | structurally distinct ✓ | page-type: data-with-takeaway ✓ | colors ✓ | fonts ✓ | no pseudo-elements ✓ | font floor ✓
  Option C: canvas fill ✗ → REGENERATED (bottom 40% empty, added decision strip) → ✓
  SLIDE 1: PASS

Slide 2 "[Slide title]"
  Structural approaches named first: YES — A=split-screen | B=three-columns | C=comparison-matrix
  Option A: all ✓
  Option B: all ✓
  Option C: structural variation ✗ → REGENERATED (too similar to B, replaced with timeline) → ✓
  SLIDE 2: PASS

GATE RESULT: ALL SLIDES PASS — proceeding to user review
========================================
-->
```

Any slide that shows "FAIL" in the gate output must be fixed before the file is saved. The user sees the gate output when they open mockups.html — this is the evidence that quality control ran.

---

## Post-build checklist — run after build_slide.py completes

```
BUILD OUTPUT:
□ PPTX file exists at the expected path and is non-zero bytes
□ Open the PPTX in PowerPoint (or inspect via python-pptx) — verify slide count matches
  the number of slides built

XLSX COMPANION (charts only):
□ If any slide had a <div data-chart="true"> with a data-chart-data attribute,
  verify that <deck>-chart-data.xlsx exists in the session folder alongside the PPTX.

  If the xlsx is MISSING:
    (a) data-chart-data was absent from chart elements → add it and rebuild, OR
    (b) The PPTX save failed before the xlsx was written → run gen_chart_xlsx.py
        directly from the brief's chart data as a recovery step.

  Do not deliver the PPTX without the xlsx if charts are present — the user needs
  the companion file to hand off chart data to their think-cell operator.

VISUAL SPOT-CHECK (open in PowerPoint):
□ No purple/dark background bleeding through the body zone
  (confirms white body fill rectangle was present in mockup)
□ Header gradient and footer bar present on every slide
□ Governing thought title text is correct — no truncation, correct font size
□ Chart images render correctly — no blank white rectangles
  (blank chart = base64 was used inside a data-chart container; fix: use relative filename)
□ No text below 10pt (visible body text minimum)
□ Bottom 30% of each slide is intentionally used — no dead white space
```

---

## Patterns that work — quick reference

These are not the only patterns; they're starting points when you're stuck.

### When you have a clear single number/answer (e.g., "$11.7M exceeds commitment"):
- **Hero-with-supporting-evidence**: hero number takes top 25%, bridge/explanation fills middle 50%, side panel takes right 30% with the question being answered
- **Contrast hero**: two numbers side-by-side (committed vs forecast), full-width hero strip, supporting tables below
- **Q&A grid**: three vertical columns, each is a question + answer + evidence

### When you have a comparison (e.g., "60 assumed vs ~30 confirmed"):
- **Direct contrast**: two large numbers side-by-side with ratio/delta in the middle, dollar implication as full-width band below
- **Scenario table dominant**: full-width table on left, decision/risk panel on right takes full height
- **Closure visualization**: stacked bar showing the cohorts, action checklist below

### When you have a list of items (e.g., agenda, scope, initiatives):
- **Horizontal-cards-grid**: 3–4 cards across, full-canvas, each card is a self-contained unit
- **Numbered-stack-with-page-refs**: vertical list left (60% width), framing/why panel right (40% width)
- **Hierarchical tree**: root at top, branches into categories below

### When you have a status/readiness picture:
- **Kanban**: Ready / In-progress / At-risk columns, each item is a card
- **Countdown-anchored**: large date/timer left, readiness bars right
- **Timeline matrix**: rows = items, columns = time periods (now → milestone → after)

### When you have a divider or section-opener:
- **Big-number-with-eyebrow**: one giant number/word, supporting eyebrow caption, full-bleed accent color
- **Question-as-header**: the section's central question in 36–44pt, one-line answer below

---

## Anti-patterns — fix these on sight

| Anti-pattern | What it looks like | Fix |
|---|---|---|
| **The Document** | Top-aligned content, empty bottom 40% | Add bottom strip OR side context OR promote a timeline |
| **The Tiny Pill** | Takeaway as "+$0.8M" in 11pt header | Hero number, 60pt, dedicated panel |
| **Three Decorations** | Three options that are the same idea with different colors/icons | Name three structural approaches first; if you can't, you have one option not three |
| **The Stranded Sidebar** | Right panel ends at 60% height, leaves 40% gap | Extend the panel to full height; absorb the empty zone |
| **Caption-as-Body** | Slide title is the takeaway, body just elaborates | Pull the takeaway into a visual hero; let the title do the eye-track |
| **The Wall of Text** | Right panel is 6 paragraphs of dense prose | Break into eyebrow + 2-sentence statements; use bullet structure |
| **The Buried Decision** | Slide ends with "decision needed" in 10pt at the bottom | Decision goes in a dedicated dark-color panel, headlined |

---

## When to use blank-mode vs. layout-aware

(Recap from main slide-builder/SKILL.md, applied to Phase A rule selection.)

**Blank mode** (most slides): the mockup IS the design. All four rules above apply directly to the HTML you write.

**Layout-aware mode** (when client template has good corporate layouts): the mockup supplies content; the layout supplies position/font/dominance.
- Rules 1 (canvas-fill) and 2 (takeaway-dominance) are mostly handled by the layout itself
- Rules 3 (structural variation) and 4 (story-first) still apply — choose three different *layouts* (e.g. "Title + 3 Stats" vs "Title + Comparison" vs "Section Divider"), not three sets of content for the same layout

---

## A worked example: applying the rules to "FY26 forecast exceeds commitment"

**Story**: $11.7M forecast exceeds $10.9M commitment by $0.8M, even after a $2.3M correction.

**Bad approach** (the failure mode this file is designed to prevent):
> "I'll make a table of the bridge, then put a side panel with the explanation, then add a small pill that says +$0.8M."
>
> Result: takeaway buried as pill, table+panel-only-fill-50%-of-canvas, three options that all look like table+panel.

**Good approach** (chassis-enforced):
> 1. Page-type: data-with-takeaway. Takeaway: "$11.7M, beats $10.9M committed by $0.8M."
> 2. Three structural approaches:
>    - **Option A — hero-number-dominant**: $11.7M is the visual hero in a wide top band; bridge table is supporting evidence below; the awkward $2.3M-correction question gets its own side panel
>    - **Option B — bridge-as-story**: actual SVG waterfall is the dominant element (showing the journey from $10.9M → $11.7M); three explanation cards below as a row
>    - **Option C — Q&A grid**: three column panels, each a question Micah will ask + the answer; the third question is "why the $2.3M correction" with reassurance
> 3. For each option, allocate canvas: hero band (25%), main evidence (50%), supporting context (25%). No empty zones. Takeaway is the largest, brightest thing on every slide.
>
> Result: each option is structurally different from the others, each one fills the canvas, each one makes the takeaway dominant.

When in doubt, ask: **"Could a reader walk past my slide at 6 feet and know the answer?"** If yes, it's working. If no, the takeaway isn't dominant enough.
