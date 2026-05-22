# Designer Brief — Inline Rulebook for Per-Slide Agents

This is the load-bearing rulebook. Every rule below is enforced. Read it once at the top of the prompt; refer back to specific sections when uncertain. The source files (`phase-a-rules.md`, `slot-design-rules.md`, `visual-treatment-library.md`, `page-types.md`, `rules.md`, `glossary.md`, `known-issues-and-improvements.md`) are deeper-reading only.

---

## 1. Hard constraints (never violate)

- **Canvas: 1280×720.** `new_slide()` already sets this. Do not change.
- **Title bottom-anchored at y≈100.** ALWAYS use `add_title_block(slide, title=..., subtitle=...)` from `twins.helpers`. Never place a raw title shape at y=40. Title grows UPWARD for 2-line titles; subtitle never moves.
- **Footer = `add_footer(slide, page_num=N)`.** This emits page number + footnote placeholder + source placeholder at y≈672–700. Nothing else belongs there.
- **Body font floor = 14px** (= 10.5pt PPTX). Eyebrows can be 11px, meta italic lines 12px, but body claims and bullets must be ≥14px. No exceptions.
- **Brand palette only.** Use the named constants imported from `twins.helpers`: `BRAND_PRIMARY`, `BRAND_PRIMARY_MID`, `BRAND_ACCENT`, `BRAND_ACCENT_SOFT`, `TEXT_DARK`, `TEXT_MID`, `TEXT_FAINT`, `CARD_BG`, `CARD_BORDER`, `WHITE`. Never raw `RGBColor(...)` literals.
- **One accent moment per slide.** `BRAND_ACCENT` (purple-magenta) appears on exactly ONE element — the load-bearing thing the takeaway hinges on. Everything else uses `BRAND_PRIMARY` or neutral tones. Two accents = the accent does no work.
- **No external assets.** No PIL, no PNG embedding, no chart image generation. Bars, waterfalls, KPI tiles — all drawn with `add_rect` + `add_text`. Icons are unicode glyphs via `add_icon` or omitted.
- **No CSS, no HTML.** Pure python-pptx via the helpers. No `border-radius:50%`, no `transform`, no pseudo-elements — those are HTML-pipeline concerns and don't apply here.
- **Insertion order = paint order.** Background fills first, foreground/text last. If you want a label to sit on top of a card, add the card rect first, then the label.

## 2. Privacy + content rules (recurring failures — read carefully)

- **NEVER include personal contact info** (email, phone, mailing address) unless the brief EXPLICITLY contains it as part of the slide's content. The presenter's *name* is fine. Their *email* is NOT. If you see `name@company.com` or any other email anywhere except the brief's literal slide content — DO NOT put it on the slide. This is a recurring privacy leak.
- **NEVER add chrome to invariant zones.** No "ACCENTURE", no "DRAFT", no "CONFIDENTIAL", no "PRIVILEGED & CONFIDENTIAL", no client name tags, no copyright lines, no signature lines, no AC logo. The top zone (y < 19) and bottom zone (y > 670) are reserved for `add_footer`'s output only.
- **NEVER invent footnote text with real-looking numbers.** Use `add_footer`'s placeholder ("[add source here or delete]"). If the brief gives you a real source, pass it as `source=...`.
- **If the brief mentions a person's name/title but no email — do NOT add an email.** Don't fill in plausible-looking details. Leave them off.
- **No lorem ipsum, no "TODO", no "[Insert X]", no "Subtitle goes here".** Every visible string is real content from the brief or a documented placeholder from a helper.
- **Examples in this rulebook are showing you HOW to call functions, not WHAT to write on the slide.** Any specific phrase that appears inside a code example — icon-mapping keywords, shape ID strings, placeholder taglines, comment annotations — is illustrative wiring, not content. NEVER copy a phrase from a rulebook example onto a slide. If the per-slide brief gives you no title or tagline, derive it from the **deck-level governing thought** at the top of the brief; if there's nothing there either, use a generic placeholder like `[Cover title — fill from brief]` so the gap is visible. Do not invent content from the rulebook itself.

## 3. Chart-honoring rule (the slide 6 failure — read carefully)

### 3a. Explicit chart requests

If the brief says `**Chart type:** <X>` and X is anything other than "none":

- **You MUST build a visual chart.** Even a simple one. The chart IS the argument; the brief specified it for a reason.
- **Allowed (built with `add_rect` + `add_text`):**
  - Bar chart: stacked rectangles, label per bar, one bar in `BRAND_ACCENT` if the brief points at a specific value.
  - Waterfall / bridge: sequential rects on a baseline, showing start → +driver1 → +driver2 → end. Annotate each delta. One `BRAND_ACCENT` bar = the load-bearing value.
  - KPI tile: large numeral (96px+, `BRAND_PRIMARY`) + label + unit.
  - Comparison bar: two bars side-by-side, delta annotation between.
- **NOT allowed:** replacing the chart with bullet points. If the brief says waterfall and you ship 3 bullets, that's a failed slide — even if the bullets are well-written. The chart's job is to make the magnitude visible.
- **If you genuinely cannot draw it** (rare): add a comment in the `.py` noting which chart type was requested, what blocked you, and what you fell back to. Don't silently substitute.

### 3b. Implicit tables and numeric content (the Micah slide 4 + 6 failure)

`Chart type: none` does NOT mean "ship a wall of text." If the brief's `Evidence / content` contains structured tabular or numeric data, you MUST render it visually — even when no chart type is named. This is the most common failure mode after explicit chart-ducking.

Trigger conditions (any ONE means render as a visual, not as bullets):
- A markdown table in the evidence (lines starting with `|`)
- 3+ structured numeric items (FTE counts, $-ranges, percentages, dates) that share a column shape
- A list of named items each carrying a value (e.g., "Initiative A — $5M; Initiative B — $1–3M")
- A capability/initiative/option roster with status or owner per row

Render patterns:
- **Markdown table** → grid of `CARD_BG` rectangles with a `BRAND_PRIMARY`-filled header row, white header text, `TEXT_DARK` body rows. Keep column widths balanced. Cap at ~6 rows visible; if more, show top-5 + footnote "(N rows total — full list in appendix)".
- **"Item: value" list** → labeled horizontal bars sized to value (e.g., FTE counts as bars). One bar in `BRAND_ACCENT` if the brief highlights a specific item.
- **3+ $-ranges or percentages** → compact metric tiles (3-4 across) with `BRAND_PRIMARY` numeral + small label + `TEXT_MID` context line.
- **Status-per-row roster** → table with a "status" column rendered as colored pill (green = on track, amber = at risk, etc.) using only brand palette neutrals + `BRAND_ACCENT` for the one row that matters.

**Hard rule:** if the slide has 3+ rows of structured data, the structure IS the argument. A bullet list collapses the structure and ducks the argument. Even an ugly visual table beats a beautiful paragraph here.

**Self-check:** before saving, scan your `.py`. If the brief had a markdown table and your output is `add_text(... body)` with `\n• ...` separators, STOP. Replace it with a rect-grid table.

## 4. Page types — pick the right structural family

(From `page-types.md`. Match the brief's editorial emphasis to one.)

- **Insight / Finding** — one evidence-backed conclusion. Chart or visual + 1-3 supporting points. Action title states the conclusion, not the topic.
- **Recommendation / CTA** — the ask is the visual hero. Dark panel dominant. Sub-asks clearly subordinate. (See slide 10 reference builder.)
- **Comparison (2-panel or matrix)** — head-to-head. Symmetric or asymmetric. Single convergence band carries the punchline. (See slide 3 reference builder.)
- **Three-column parallel** — MECE pillars, options, or themes. Tinted cards OR dark-header cards OR rule+label. Never flat columns on white.
- **Hero number / Data-with-takeaway** — one giant numeral at 96px+, supporting context subordinate.
- **Visual Model** — pyramid, cycle, 2x2, hub-and-spoke. The shape IS the argument. Match shape to relationship in content (ascending → pyramid; repeating → cycle; trade-off → 2x2).
- **Roadmap / Timeline** — horizontal phase bars, milestone markers in `BRAND_ACCENT`.
- **Cover / Divider** — full-bleed dark with hero title. Tagline below in `BRAND_ACCENT_SOFT`. Single accent rule. **Hero title size cap: 36-48px for multi-word titles.** 60-96px is reserved for single-numeral hero slides (KPI tile), not cover titles. A multi-word cover title at 72px+ renders as chunky/Impact-style regardless of font family — Graphik, FedEx Sans, Inter all suffer at that scale. Stay editorial.
- **Quote** — large quote in white italic on `BRAND_PRIMARY` fill. Attribution in `BRAND_ACCENT_SOFT`.
- **Structured text** — when reasoning IS the argument (no chart, no diagram). Sub-heads in `BRAND_PRIMARY`, body in `TEXT_DARK`. Don't force a visual.

## 5. Visual treatments — the toolbox

(From `visual-treatment-library.md`. Reach for these confidently.)

- **Full-bleed dark** — `BRAND_PRIMARY` fills the canvas. White type. Use for covers, pivots, the closing ask, occasional Visual Model centerpieces. NOT the default for body slides.
- **Tinted cards on white** — `CARD_BG` rectangles with `CARD_BORDER` outline, optional 3px `BRAND_ACCENT` left edge. The default for evidence/three-column slides.
- **Dark card headers + light body** — top 25-35% of column is `BRAND_PRIMARY` filled with white text + hero numeral; bottom is white with body. Use when the slide is a MECE declaration.
- **Two-column with insight panel** — left 60% evidence (white), right 40% dark panel (`BRAND_PRIMARY` fill, white text). The contrast IS the point.
- **Hero stat + supporting** — large numeral (`BRAND_PRIMARY`, 96-144px) anchors, supporting content recedes.
- **Convergence band** — full-width `BRAND_PRIMARY` strip at bottom of body (use `add_convergence(slide, text)`), white italic punchline. Use when two panels need a unifying so-what.
- **Annotation callout** — single `BRAND_ACCENT` element pointing at a data point. Dashed border, ≤10 words, max 1 per slide.
- **Accent rule** — thin (3-6px) `BRAND_ACCENT` strip on the left edge of a hero card OR as a 56-64px horizontal mark under a hero title. This is often the single accent moment.

### 5a. Icons — use the library, not generic glyphs

If a slide calls for an icon (process / data / people / risk / decision / etc.),
USE `add_icon_from_library(slide, shape_id, x, y, size, name="<icon_name>")`.
This inserts a real vector icon from the Slide Lab icon library (1,143 icons
shipped). Do NOT use `add_icon(...glyph="☰")` — generic Unicode glyphs (☰ ✦ → ⚙)
look amateur next to a proper editorial slide.

15 standard icons to reach for first (full catalog: `icons/icon-index.json`):

| name | use for |
|---|---|
| `gear` | process / operations / workflow |
| `wrench` | work in progress / tools |
| `people` | team / workforce / org |
| `chart-bar` | data / analytics / reporting |
| `compass` | strategy / direction / vision |
| `calendar` | timeline / schedule |
| `coins` | cost / budget / value |
| `shield-warning` | risk / controls / escalation |
| `diamond` | decision / approval / governance |
| `lightbulb` | insight / finding / idea |
| `globe` | external / market / scale |
| `clipboard-check` | compliance / audit / sign-off |
| `chip` | technology / systems / AI |
| `speech` | communication / engagement / change |
| `package` | delivery / output / shipping |

Example for a generic three-pillar slide (substitute your own pillar concepts from the brief — never reuse the example's icon names or any made-up wording):
```python
add_icon_from_library(slide, "pillar-1-icon", x_px=180, y_px=240, size_px=72, name="lightbulb")
add_icon_from_library(slide, "pillar-2-icon", x_px=580, y_px=240, size_px=72, name="speech")
add_icon_from_library(slide, "pillar-3-icon", x_px=980, y_px=240, size_px=72, name="package")
```

The icons get tinted with `BRAND_ACCENT` by default (overridable via `color=`).
After theme remap they inherit the client's accent — no per-client work needed.

If the icon you want isn't in the library, the helper inserts a labeled dashed
placeholder (visible "[name]" marker) — the build never breaks. Don't fall back
to `add_icon(glyph=)` just to avoid the placeholder; the dashed placeholder is
a useful "this needs adding" signal.

### 5b. Icon containers — CIRCLE, not square (read carefully)

When you place an icon on a colored background (the "icon chip" pattern,
e.g., three pillar cards each with an icon at the top), the background **MUST
be a circle**, not a square or rectangle. Squared icon backgrounds read as
web-app tiles. Circles read as editorial slide design. This is non-negotiable.

**Construction (3 lines):**
```python
cx, cy, d = 240, 280, 80                                       # center + diameter
add_circle(slide, "pillar-bg", cx - d//2, cy - d//2, d, BRAND_PRIMARY)
add_icon_from_library(slide, "pillar-icon",
                      cx - 24, cy - 24, 48, name="lightbulb", color=WHITE)
```

**Color rules for the circle:**
- Default: `BRAND_PRIMARY` (deep brand color) with WHITE icon on top
- Variant: `BRAND_PRIMARY_MID` (lighter brand) with WHITE or BRAND_PRIMARY icon
- NEVER use `BRAND_ACCENT` or `BRAND_ACCENT_SOFT` for icon circles — that
  burns your one accent moment on a container, not on the load-bearing element
- NEVER make each circle a different bright color when the items are MECE
  (three pillars / four steps / five themes). Same color for all. Sequencing
  circles by hue (red/orange/blue/green) only makes sense when each item has
  a categorical meaning (RAG status, distinct domains, phases of a timeline)

**Size guidance:**
- Circle diameter: 64–96px (smaller = decorative, larger = hero)
- Icon size inside: ~60% of circle diameter (40px icon in 64px circle, 56px icon in 96px circle)
- Icon is centered on the circle (cx - icon_size/2 for x, same for y)

**The slide 5 option C failure:** peach squares (`BRAND_ACCENT_SOFT`) for
icon backgrounds + orange accent rule under the title + bright violet card
headings = three competing "accent" moments. Replace the peach squares with
a single `BRAND_PRIMARY` circle treatment and the slide reads as one
coherent brand statement.

## 6. Slot design rules

(From `slot-design-rules.md`. Density, alignment, hierarchy.)

- **Find the hero number** before writing slot content. There's usually one load-bearing number per slide ($3.4M, 60%, 2 weeks). Elevate it to hero size (40-96px+, `BRAND_PRIMARY`). Do NOT bury it inside a body sentence.
- **Split prose into bullets.** A 3-fact paragraph from the brief becomes 3 bullet lines, not 1 prose run. Use `•` + newlines or three separate `add_text` calls stacked.
- **Pull category labels out of prose.** "Lever 1: field HR ratio" → "LEVER 1" in 11px uppercase label slot, "Field HR ratio" in 22px heading slot.
- **Strip filler clauses.** Pattern typography carries the formality; text doesn't need to.
- **Slot roles + typical sizes:**
  - Eyebrow / label: 11px uppercase, `TEXT_MID` or `BRAND_PRIMARY`, letter-spaced.
  - Card heading / panel heading: 18-22px bold, `BRAND_PRIMARY` or `TEXT_DARK`. ≤6 words.
  - Body / bullets: 14-16px regular, `TEXT_DARK` or `TEXT_MID`. ≤7 words per bullet ideal.
  - Hero numeral: 40-144px bold, `BRAND_PRIMARY`. One per slide.
  - Convergence / punchline: 14-16px white italic in band.
  - Footnote / source / page number: 10-11px `TEXT_FAINT`. Fixed by `add_footer`.
- **Padding:** 16-22px inside any filled card or panel. Never closer than 16px to a zone edge.
- **Hero element occupies 40-60% of canvas height** (288-432px). If it's smaller, you have dead space below.
- **Side panels run to full canvas height** (~720px). A panel that stops at 60% leaves a visible gap.
- **No empty bottom.** Content extends to within 40-60px of the footer line (y≈610-630). If it doesn't, apply a recovery: enlarge the hero, add a convergence band, add a bottom takeaway strip, or extend a side panel.
- **Title length cap.** If the brief's `Governing thought` exceeds 90 characters, do NOT pass it verbatim to `add_title_block`. EITHER (a) shorten to ≤90 chars while preserving the load-bearing claim, OR (b) split into a short title + a longer sub-claim that lives in the so-what / subtitle slot. A 4-line title with the brand-rule sitting under the last word looks like a typo. The title is a headline, not a paragraph.

- **Bold discipline (the slide 1 + 2 readability failure).** Bold is the most expensive piece of typographic real estate on a slide; spending it everywhere collapses hierarchy. Apply these constraints:
  - **Hero title:** bold (one instance, via `add_title_block`).
  - **Card/panel headings:** bold (one per card, 18-22px).
  - **Eyebrow / label:** NEVER bold. Uppercase + letter-spacing already do the work. `bold=True` on an eyebrow makes the label fight the heading next to it.
  - **Body / bullets:** NEVER bold globally. If a specific phrase needs emphasis, use inline `<strong>X</strong>` on that phrase only — `add_text` interprets the tag and tints with `emphasis_color=BRAND_PRIMARY`.
  - **Stat tiles:** the numeric VALUE may be bold; the LABEL is not.
  - **Hard ceiling: 5 bold elements per slide max.** If you've drawn 6+ bold runs, pull bold off the labels and eyebrows first. If still over 5, drop body emphasis next. Only the title + card headings + one or two values should survive as bold.
  - Failure mode this catches: a slide where every text shape uses `bold=True` because each "felt important" reads as noise — nothing emphasizes anything when everything is emphasized.

## 7. Cross-slide consistency (orchestrator-mode rules)

(From `slide-qc` 5c. These matter when 10 parallel agents each build one slide.)

- **Title style is consistent.** Always `add_title_block` — same font size, same y-anchor, same `BRAND_ACCENT` rule width (56-64px). Don't reinvent.
- **Footer style is consistent.** Always `add_footer(slide, page_num=N)`. Same x/y positions on every slide. Page number is right-aligned at x=1170.
- **Color rhythm:** not every slide is dark-mode. Roughly: cover = dark, body slides = white-with-tints, pivot = dark, close/CTA = dark, others = light. If your slide is a generic body slide, default to white background with tinted-card or rule+label treatments.
- **Accent discipline holds across the deck.** Each slide has its own single accent moment; the accent never spreads across multiple elements just because the slide has more content.
- **Body font sizes don't drift.** 14-16px body text on every slide. A slide with 12px body and a peer slide with 18px body looks inconsistent in deck flow.
- **No "Slide N of M" markers, no section labels, no breadcrumbs.** Page number alone in the bottom-right.

## 8. Common failure modes to avoid

(From `known-issues-and-improvements.md` — the top recurring mistakes.)

1. **Ducking a requested chart.** If `**Chart type:** waterfall`, build a waterfall. Don't ship bullets. (Slide 6 failure.)
2. **Leaking personal email/contact info onto the slide.** (Slide 10 failure.) Presenter name OK; email NOT.
3. **Title at y=40 instead of bottom-anchored at y≈100.** Use `add_title_block`.
4. **Two-line title that displaces the subtitle.** `add_title_block` handles this — let it.
5. **Multiple accent moments.** Pick ONE element to wear `BRAND_ACCENT`. Everything else stays `BRAND_PRIMARY` or neutral.
6. **Body text below 14px.** Sub-10pt text in the final PPTX is amateur. 14px CSS = 10.5pt PPTX = the absolute floor.
7. **Hero number buried mid-sentence.** Promote to its own shape at 40-144px.
8. **Sparse-content slide with empty bottom half.** Apply recovery: increase font, add bottom anchor per card, extend hero, add convergence band.
9. **Three "options" that are the same idea recolored.** Each option must be a different layout family (split-panel / hero-number / convergence-band, not three card grids).
10. **Decorative containers added to fill space.** A colored rect with no content purpose makes the empty space MORE visible. Either content goes in it or it doesn't exist.
11. **Top/bottom chrome ("CONFIDENTIAL", client name, AC logo).** Invariant zones hold ONLY page-number + source + footnote.
12. **Inventing footnote data.** Use `add_footer`'s placeholder unless the brief gives you a real source.

## 9. Self-check before saving

Walk this list mentally on each option:

- [ ] Title bottom-anchored at y≈100? (Used `add_title_block`?)
- [ ] Footer = `add_footer(slide, page_num=N)` and nothing else in the bottom zone?
- [ ] One accent moment? (`BRAND_ACCENT` appears exactly once.)
- [ ] All body text ≥14px?
- [ ] No raw hex literals?
- [ ] If brief named a chart type, did I actually build a visual chart?
- [ ] No personal email, no client name, no DRAFT/CONFIDENTIAL anywhere on the slide?
- [ ] Hero element fills 40-60% of canvas height? Bottom 40px of body is not dead space?
- [ ] Three options are structurally distinct (different layout families)?
- [ ] Script runs standalone via `python option_X.py` from any cwd?

If any box is unchecked — fix it before saving.
