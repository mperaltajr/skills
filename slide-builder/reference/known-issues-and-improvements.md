# Known Issues and Improvement Notes — Slide Builder

This document captures issues encountered during real client slide production. Each section describes the problem, root cause, and the fix or skill change needed. Claude should read this before building slides and apply the fixes proactively.

**Status legend:** `Fixed` — resolved and shipped; `Workaround available` — acknowledged, partial mitigation in place; `Deferred` — not yet built.

---

## 1. CSS Pseudo-Elements Are Invisible in PPTX — Never Use `::before` / `::after` for Content

**Status:** Fixed

### Problem
Bullet points styled with `li::before { content:"•"; }` are CSS pseudo-elements. The PPTX builder walks real DOM nodes via `getBoundingClientRect()` — pseudo-elements are not real DOM nodes and are completely invisible to it. The bullet dots simply do not appear in the built slide.

### Fix
**Always use real `<span>` elements for any content that must appear in the PPTX.** Replace pseudo-element bullets with an inline span:

```html
<!-- WRONG — bullet will vanish in PPTX -->
<li><span class="s-b">Topic</span> — description</li>

<!-- CORRECT — bullet is a real DOM node -->
<li><span class="s-bul">•</span><span class="s-b">Topic</span> — description</li>
```

CSS for the bullet span:
```css
.s-bul { color:#7D22C3; flex-shrink:0; font-size:13px; }
.s-ul.out .s-bul { color:#C74755; }
```

**This rule applies to any decorative content** — icons, check marks, arrows, dividers — anything that must appear in the final PPTX must be a real HTML element, not a CSS-generated pseudo-element.

---

## 2. Font Size Issue — px in HTML ≠ pt in PPTX

**Status:** Fixed

### Problem
The skill instructs mockup authors to write CSS font sizes in `px` (e.g., `font-size:12px`). The user expects this to produce 12pt text in the final PPTX. It does not. The builder converts px → pt using the 96dpi → 72dpi ratio:

```
pt = px × (72 / 96)
```

So:
| CSS (px) | PPTX output (pt) |
|----------|-----------------|
| 12px     | 9pt             |
| 13px     | ~9.75pt         |
| 14px     | ~10.5pt         |
| 16px     | 12pt            |
| 18px     | ~13.5pt         |

This caused the user to receive slides with 9pt body text when they expected 12pt. Non-standard fractional pt values (9.4pt, 9.75pt) also appeared, which are not acceptable in a professional deck.

### Fix
**Never use non-standard pt sizes in PPTX output.** The rule is:
- Preferred body text: **12pt** → use **16px** in HTML mockup CSS
- Minimum body text: **10pt** → use **13px** in HTML mockup CSS (rounds to ~9.75pt — acceptable; 14px = ~10.5pt is cleaner)
- Do not go below 10pt for any visible body text
- Round all PPTX pt values to the nearest whole number or 0.5pt

**The skill's mockup authoring instructions should be updated to state the conversion explicitly:**
> "Body text should be 16px in CSS to render as 12pt in PPTX. Minimum is 14px (≈10.5pt). Never use fractional px values that produce sub-10pt output."

**The builder (`build_slide.py`) should also snap font sizes to the nearest whole pt value** before writing to PPTX XML, so fractional sizes like 9.75pt never appear in the output.

---

## 3. Slide Construction Challenges

**Status:** Fixed

### 3a. Label-to-row alignment across columns

**Problem:** The initial design used a flexbox column for row labels and separate flexbox columns for the in-scope and out-of-scope panels. Because each column sized its rows independently based on content, the category labels (MSP, GCC, Shared, Experience) did not vertically align with the corresponding panel rows. The MSP label sat at the top of the label column while the MSP panel row was taller and started lower.

**Fix applied:** Switched to CSS Grid with `grid-template-columns: 148px 1fr 22px 1fr` and `grid-template-rows: 44px 3fr 2fr 2fr 2fr`. All four columns (label, in-panel, gap, out-panel) share identical row heights automatically because they are in the same grid.

**Skill improvement:** The `visual-treatment-library.md` entry for Comparison layouts should call out this pattern explicitly: when a label column must align with multi-column content rows, use CSS Grid spanning all columns, not independent flexbox columns.

### 3b. Canvas fill / white space at the bottom

**Problem:** Initial mockups used `auto` row heights, which meant rows sized to their content and left large empty white space below the last row. This violated the canvas fill rule (Rule 1 in `phase-a-rules.md`) but the violation wasn't caught because the rule is stated in principle, not in implementation terms for grid/flex layouts.

**Fix applied:** Changed grid rows to `fr` units (`3fr 2fr 2fr 2fr`) so they always fill the available height. Combined with `flex:1; min-height:0` on the grid container to ensure it fills the remaining slide height after the header and footer.

**Skill improvement:** `phase-a-rules.md` should add a concrete implementation note:
> "If your content area uses CSS Grid or flexbox rows, always use `fr` units for row heights, not `auto`. `auto` rows collapse to content size and leave dead space at the bottom. The grid container should have `flex:1; min-height:0` to fill the remaining canvas after fixed header/footer zones."

### 3c. Content length vs. font size tradeoff

**Problem:** Bullets were written at natural prose length without considering the column width at the target font size. At 13px in a ~470px wide column, a bullet of 80+ characters wraps to two lines, breaking the "one line per bullet" rule and causing content to overflow the row.

**Fix applied:** Manually trimmed each bullet to fit one line at the target font size. Rough guideline: at 13px FedEx Sans in a 470px column, max ~65–70 characters per bullet.

**Skill improvement:** When authoring bullet content for narrow columns, apply a character budget per line:
- Column width ÷ ~6.5px per character (FedEx Sans Regular at 13px) = max chars per line
- For 470px columns: ~72 chars max. Trim bullets to stay within this before finalizing the mockup.

---

## 4. Stylistic Preferences That Weren't Captured in the Skill

**Status:** Fixed

These are preferences the user had to ask for explicitly, round after round. The skill should bake them in as defaults so they're delivered correctly on the first pass.

### 4a. Light tint panels, not heavy brand color fills

**What happened:** The initial options used saturated brand colors (dark purple fills, bold orange accents) for panel backgrounds. The user wanted a much lighter treatment matching the client's existing slide 6 — light purple tint (`#F3EEF9`) for in-scope, light pink tint (`#FFF3F3`) for out-of-scope, with thin colored borders and accent-colored top rules instead of full fills.

**Preference stated by user:** "not as color heavy" — the slide should feel airy and readable, not branded-heavy.

**Skill improvement:** The `visual-treatment-library.md` Comparison layout entry should add:
> "When the client deck is already color-heavy in the master header and footer, body content panels should use light tints (primary tint 5–10%, not full accent fills) to avoid visual fatigue. Reserve full accent fills for column headers only (top 3–5px accent rule or header background). Check the client template's existing slides before defaulting to dark fills."

### 4b. Bullet format: **Bold topic** — description

**What happened:** The initial bullets were written as plain prose or with generic bold formatting. The user had to explicitly ask for the format: `**Bold topic** — plain description` on one line. This is a clean, scannable format common in consulting deliverables.

**Skill improvement:** Add to the structured text and comparison layout entries in `visual-treatment-library.md`:
> "Default bullet format for scope/comparison/structured slides: `**Topic** — one-line description`. Bold the topic label; follow with an em-dash and a concise descriptor. One line per bullet. No sub-bullets."

### 4c. Category label alignment with panel rows

**What happened:** The user had to point out that labels weren't aligning with rows before the CSS Grid fix was applied. This is a fundamental readability issue for any labeled multi-row layout.

**Skill improvement:** Any layout with row labels on the left and content panels on the right must use shared-grid rows. This should be a hard rule in the layout authoring section, not something discovered during iteration.

### 4d. Structural variation between options

**What happened:** Early options (before the CSS Grid version) were decoratively varied rather than structurally varied — different colors, different header styles, but the same underlying list layout. The user flagged this explicitly ("these all look the same").

**Skill improvement:** This is already in `phase-a-rules.md` Rule 3 but it wasn't applied. The self-check should enforce naming the structural approach in a comment before writing HTML, and the pre-show check should explicitly compare options visually. If removing color and text would make options look identical, regenerate.

### 4e. White space management (top/bottom breathing room)

**What happened:** The user wanted the slide to feel "full" but not cramped — similar to slide 6 which has deliberate top padding above the title and a footer bar at the bottom that grounds the slide. The initial mockups lacked this framing and felt like floating content.

**Skill improvement:** All slides should have:
- A fixed header zone (gradient master bar or solid brand color, ~50px) at the top
- A fixed footer bar (~45–50px, solid brand color) at the bottom with page number and confidentiality notice
- Title zone with deliberate top padding (~16–20px above title text)

These three elements create the "grounded" look of a properly framed slide. They should be part of the default blank-mode slide template in the skill, not optional add-ons.

---

## 5. Chart Image Paths — Broken Preview When Using `_session/` Prefix in `<img src>`

**Status:** Fixed

### Problem
`generate_chart.py` saves PNGs to `_session/`. `mockups.html` also lives in `_session/`. When the mockup referenced charts as `src="_session/chart-slide-N.png"`, the browser resolved the path relative to the HTML file's location — producing `_session/_session/chart-slide-N.png`, which does not exist. The chart rendered as a broken image icon, blocking human review.

The build (Phase B / Playwright) was unaffected if PNGs were embedded before it ran, so the bug only surfaced during the preview step — exactly where design decisions are made.

### Fix
**Always embed chart PNGs as base64 data URIs** after generating them. This makes the mockup self-contained and removes any path dependency:

```python
import base64, pathlib
uri = "data:image/png;base64," + base64.b64encode(pathlib.Path(png_path).read_bytes()).decode()
img_tag = f'<img src="{uri}" style="width:560px;height:320px;object-fit:contain;">'
```

Never use `src="_session/..."` — the `_session/` prefix is only valid from one directory above the file. The pre-save checklist in `phase-a-rules.md` now includes a scan for this pattern.

---

## 5b. Base64 Data URI Inside `data-chart` Container — Blank Chart in PPTX

**Status:** Fixed

### Problem
To fix the broken preview (Issue 5), chart `<img>` tags were converted to base64 data URIs. This fixed the HTML preview but broke the PPTX build. `build_slide.py` screenshots any `<div data-chart="true">` element via Playwright. When that div contains an `<img src="data:image/png;base64,...">` inside a `flex:1; min-height:0` container, Playwright returns a zero-height bounding box — the flex height collapses without a concrete parent height at screenshot time. The screenshot is blank; the PPTX shows an empty white rectangle.

### Fix
**Two-rule system based on context:**

| Context | Required src | Why |
|---|---|---|
| `<img>` outside `data-chart` | `data:image/png;base64,...` | Self-contained, renders everywhere |
| `<img>` inside `data-chart="true"` | Relative filename: `chart-slide-N.png` | Playwright needs a real file path to resolve the bounding box correctly |

The HTML preview will show a broken image icon for `data-chart` containers — this is expected. The PPTX output is correct. Never use `_session/` as a path prefix in either context.

---

## 5c. Dark Template Background Bleeds Into Body Zone

**Status:** Fixed

### Problem
The FedEx Org Design template (and other templates with a dark slide master) uses a dark purple fill (`#4D148C`) as the master background. When `build_slide.py` picks the "cleanest blank" layout, the slide inherits this background. The HTML mockup's `.slide { background: #fff }` CSS rule is not translated to PPTX — the builder renders HTML elements as overlay shapes, not the slide container. Any area of the slide not explicitly covered by a named shape shows the template's dark background bleeding through. Result: all text and content floats on purple with no visible card backgrounds.

### Fix
Add an explicit white fill rectangle to every slide in `mockups.html`, placed immediately after `<div class="hdr"></div>`:

```html
<div class="hdr"></div>
<!-- White body fill — required for templates with dark slide master backgrounds -->
<div style="position:absolute; top:50px; left:0; right:0; bottom:44px; background:#ffffff;"></div>
```

`top:50px` = header height. `bottom:44px` = footer height. This creates a white canvas in the body zone while leaving the header gradient and footer intact. **This is a structural default — include it in every slide, not just slides where a dark template is known to be in use.** It is invisible in HTML preview and harmless on light templates.

---

## 6. Chart Formatting Standards

**Status:** Fixed

These apply to all charts generated by `generate_chart.py`. They match consulting deck conventions and are enforced in the script.

### 6a. Chart title — bold title, regular units, top left

The chart title block has two lines, both left-aligned with the plot area's left edge:
- **Line 1:** Bold, 11pt — the chart name. Example: `CY29 Net Run-Rate Benefit`
- **Line 2:** Regular weight, 9pt, gray — the unit or qualifier. Example: `$M` or `(# FTEs)`

This matches the convention in the screenshot: title left-aligns with the start of the Action Title above it. Pass `--title` and `--units` separately to `generate_chart.py`.

Do NOT use `ax.set_title()` — it centres the text and cannot produce a two-line title with mixed weight.

### 6b. Legend — always top right

All chart legends are positioned `upper right`. No exceptions. This applies to line, clustered bar, stacked bar, waterfall, and any multi-series chart.

---

## 7. Title Built as Overlay Shape — Does Not Follow Layout Changes in PowerPoint

**Status:** Fixed

### Problem
All slides built in blank mode render the governing thought title as a free-floating overlay shape. When the user opens the PPTX and changes a slide's layout via PowerPoint's Layout menu, the template's native placeholders reposition — but the overlay title stays fixed. The title is not wired to the template's TITLE placeholder, so it cannot follow any layout change. This makes the deck harder to edit and breaks a fundamental expectation of PowerPoint.

### Root cause
Without `data-layout-master` / `data-layout-index` on the slide div and `data-placeholder="title"` on the governing thought element, the builder treats everything as an overlay. Blank mode is the default and requires no upfront layout research — but it produces disconnected title shapes.

### Fix
After running `--catalog-layouts`, identify the default content layout: the layout with a `TITLE (1)` placeholder at `y ≈ 40px`, full width, and a light background. Record its `master_index` and `layout_index`.

Add to every slide div:
```html
<div class="slide" data-layout-master="2" data-layout-index="4" data-slide-index="1" data-option="A">
```

Add to the governing thought element:
```html
<div class="tz-title" data-placeholder="title">Governing thought text</div>
```

The builder pumps the element's text into the layout's TITLE placeholder. All other elements remain as overlays — no other changes required. This applies to any template with 20+ named layouts. The pre-save checklist in `phase-a-rules.md` now enforces this check.

---

## 7b. Pipeline Decision Made Silently — User Received a Built Deck Instead of Design Options

**Status:** Fixed

### Problem
When slides were identified as structured (tables, bullet grids), the skill skipped Phase A entirely and built and delivered the slides immediately. The user expected to see three design options and pick one — the same experience as visual slides. There was no review step.

### Root cause
The old architecture treated "direct python-pptx" as a separate path that bypassed Phase A. This created an asymmetry: visual slides got a design review, structured slides did not — even though tables and card grids have meaningful layout variation.

### Fix
Phase A now runs for every slide regardless of type. HTML mockups are generated for tables and structured layouts the same as visual slides — three options, user picks one. Phase B then uses the appropriate build engine (Playwright for visual, python-pptx for structured) based on the selected option. The build engine choice is entirely internal and never shown to the user. The user experience is identical for every slide type.

---

## 7c. xlsx Companion Not Generated — `data-chart-data` Attribute Missing

**Status:** Fixed

### Problem
The xlsx companion (`<deck>-chart-data.xlsx`) was never produced despite charts being present in the deck. The user received the PPTX with charts but no companion file, and had to ask for it explicitly.

`build_slide.py` generates the xlsx **only** when chart elements in the mockup carry a `data-chart-data` JSON attribute. The chart generation workflow produces PNG images but never writes the source data back into the attribute on the `<div data-chart="true">` element. Without that attribute, `build_slide.py` finds no exportable data and silently skips the xlsx entirely — no warning, no indication it was skipped.

There is a second failure mode: even if `data-chart-data` is present, the xlsx is written **after** `pres.save()`. If the PPTX save fails (e.g., file is open in PowerPoint), the xlsx is also lost.

### Fix
**At chart generation time:** immediately add the `data-chart-data` JSON attribute to the `<div data-chart="true">` element in the mockup. Copy the source data from the brief's `Chart data:` field:

```json
{
  "title": "Sheet name in xlsx",
  "categories": ["Cat A", "Cat B"],
  "series": [{"name": "Series 1", "values": [1.0, 2.0]}],
  "notes": "Optional: chart context, reference lines, caveats"
}
```

**If the xlsx is missing after a build:** either (a) `data-chart-data` was not present — add it and rebuild, or (b) the PPTX save failed before the xlsx was written — generate it directly from the brief's chart data using a standalone script (`gen_chart_xlsx.py`).

**Post-build check:** verify `<deck>-chart-data.xlsx` exists alongside the PPTX before delivering. The xlsx is required — the user needs it to hand chart data off to their think-cell operator.

---

## 8. Content Overflows Into Footer — Flex Layout Clearance Unpredictable

**Status:** Fixed

### Problem
A bottom-anchor impact strip on slide 2A visually overlapped the purple footer bar in both HTML preview and built PPTX. The pre-show checklist ran but did not catch the overflow because there was no explicit step for verifying footer clearance.

The footer is `position:absolute; bottom:0; height:44px; z-index:10`. With a flex-column layout, the last flex item lands at the bottom of the flex container — but flex container height is browser-dependent. A strip computed to end at 670px from slide top (with the footer starting at 676px) looks like a 6px gap in one browser and actual overlap in another. The footer's `z-index:10` paints over anything that gets too close.

### Fix
**Always position bottom-anchor elements with `position:absolute` and an explicit `bottom` value — never rely on flex flow:**

```html
<div style="position:absolute; bottom:52px; left:48px; right:48px;
            background:#333333; padding:12px 24px; border-radius:3px;">
  <!-- strip content -->
</div>
```

`bottom:52px` = footer height (44px) + 8px minimum clearance. Set the content zone's `bottom` to `strip_height + 52px` so panels above stop well clear of the strip.

Added as Rule 6 in `phase-a-rules.md` and as a FOOTER CLEARANCE check in the pre-save file checklist.

---

## 9. Sibling `<span>` in Flex Container — Text Boxes Overlap in PPTX

**Status:** Fixed

### Problem
An impact strip containing two `<span>` elements inside a `display:flex; justify-content:center; gap:20px` parent rendered correctly in HTML but produced overlapping text boxes in the PPTX. The builder (`build_slide.py`) creates a separate PPTX text box for each leaf text-bearing element. When two inline spans sit as direct flex children, the builder measures each span's bounding box independently and places both at approximately the same x-coordinate — one painted on top of the other.

### Fix
**Collapse sibling label+value spans into a single container:**

```html
<!-- WRONG — two sibling spans as flex children → overlapping shapes in PPTX -->
<div style="display:flex; justify-content:center; gap:20px;">
  <span style="color:#ccc;">Combined value at risk</span>
  <span style="color:#FF6600;">~$24.3M</span>
</div>

<!-- CORRECT — single div, inline spans, no flex gap -->
<div style="text-align:center;">
  <span style="color:#ccc;">Combined value at risk&nbsp;&nbsp;</span><span style="color:#FF6600;">~$24.3M</span>
</div>
```

Reserve flex containers for structural layout (panels, columns, rows). Never use flex to position text runs within a single visual unit — these always collapse to sibling span overlap in the PPTX output.

Added as Rule 7 in `phase-a-rules.md` and as a SIBLING SPAN CHECK in the pre-save file checklist.

---

## 10. Sparse Column Content — Bottom Half Empty in Multi-Column Layouts

**Status:** Fixed

**Session:** 2026-05-14 Phase Test

### Problem

Four-column icon layout (Option A) rendered with icons and bullets filling only the top ~38% of the canvas. The bottom ~280px was empty white space. Rule 8 (hero element 40–60% canvas height) and Rule 10 (reading path anchored in bottom 30%) both describe this failure, but neither was enforced as a blocking gate before the mockup was saved.

Root cause: column container set to `height:580px` via flexbox, but column content (icon + header + 3 bullets at 12px) filled only ~230px. Flexbox top-aligns by default. No recovery pattern applied.

**User description:** *"These slides continuously make a lot of white space that is not acceptable. You could have brought the icons lower, increase the font size, and improve it more visually so that the audience can focus on the message."*

### Fix

**Rule 8 sparse-content trigger added** (`phase-a-rules.md`): When a multi-column layout has fewer than 5 bullets per column at body font size, three automatic actions are required: (1) increase font to 15–16px, (2) add a stat/KPI callout per column at the bottom, (3) use `align-items:stretch` with full-height card boundaries. At least one must be applied before saving.

**Per-option checklist hardened** (`phase-a-rules.md`): Rule 8 checklist item now blocks saving when the answer is NO — it requires naming which recovery pattern was applied. A new checklist item asks explicitly whether each column/panel fills to within 60px of the footer clearance line.

---

## 11. L-Shaped Connector Artifacts in Flowchart Slides

**Status:** Fixed (page type 18 added; see also Issue 13 for Phase B limitation)

**Session:** 2026-05-14 Phase Test

### Problem

Flowchart connectors built from two separate absolutely-positioned `<div>` segments (one horizontal + one vertical) produced visual artifacts at elbow corners: overlapping pixels, inconsistent line weight at the joint, and no smooth miter. Arrowheads were CSS border-triangles placed manually for each direction separately — no automatic rotation.

**User description:** *"Is there a reason why the arrows aren't using ones that can flex/bend for corners? I see these as straight lines and they overlap. Is this an issue with the slide builder skill? When I use PPT they connect cleanly."*

### Fix

**Page type 18 (Flowchart) added** (`page-types.md`): Flowchart slides now use a single SVG overlay for all connectors. `<path>` with L-commands produces clean miter-joined elbow corners. `orient="auto"` on `<marker>` handles arrowhead rotation for all directions automatically. One `<marker>` per stroke color. Paths stop 8px before target box edge so arrowhead tips land flush.

**Phase B limitation (see Issue 13):** The SVG overlay approach was initially documented with a `data-chart="true"` wrapper to screenshot the full slide. However Issue 13 revealed the DOM walker excludes full-slide SVG overlays from the screenshot path — flowchart connector arrows do not appear in the built PPTX and must be added manually in PowerPoint.

---

## 12. Orphaned HTML After `</html>` From Short Edit Anchor

**Status:** Fixed

**Session:** 2026-05-14 Phase Test

### Problem

When replacing a slide option block in `mockups.html`, the `old_string` anchor matched only the opening `<div>` of the old slide. The replacement inserted the new content but left hundreds of lines of old slide content in place — after `</html>`. The browser rendered the orphaned block, overlaying the old grid layout on top of the new flowchart.

**User description:** *"Also, the HTML now overlaps and is breaking."*

### Fix

**Edit safety rule added** (`SKILL.md`): `old_string` for any block >~10 lines must span from a unique opening tag/comment to a unique closing tag/comment. Closing comments (`</div><!-- end slide NX ... -->`) are now required on every slide div in `mockups.html`. If orphaned HTML is discovered after `</html>`, truncate the file at the last valid `</html>` line.

---

## 13. SVG Full-Slide Overlay Screenshots Entire Slide as Raster (Phase B)

**Status:** Workaround available (connector arrows must be added manually in PowerPoint)

**Session:** 2026-05-14 Phase Test

### Problem

`build_slide.py` DOM walker JS treated every `<svg>` element as a chart screenshot target (`isChart: el.tagName.toLowerCase() === 'svg'`). A full-slide SVG connector overlay (1280×720px, `pointer-events:none`) caused the entire rendered slide to be screenshotted as a flat PNG placed on top of all PPTX shapes — producing a double-layer effect where the raster image covered editable text boxes.

### Fix

DOM walker now excludes full-slide overlay SVGs from the screenshot path. Detection: `pointer-events === 'none'` AND width/height ≥ 90% of slide dimensions. These overlays are skipped entirely in Phase B — flowchart arrows do not appear in the built PPTX and must be added manually in PowerPoint.

**Option B (not yet built):** Parse `<path d="...">` M/L commands inside full-slide SVG overlays into EMU coordinates and emit as `python-pptx` `FreeformBuilder` or `MSO_CONNECTOR` shapes. This would preserve flowchart arrows as editable PPTX shapes.

---

## 14. Status Badge Pills Word-Wrap in PPTX Despite white-space:nowrap

**Status:** Fixed

**Session:** 2026-05-14 Phase Test

### Problem

`word_wrap` in built PPTX text frames was set by a height-based heuristic (`element_height <= font_size_px * 1.5`) and unconditionally to `True` for background-colored shapes. The builder did not read the element's computed `white-space` CSS property, so `white-space:nowrap` in the mockup had no effect on PPTX output. Badge pill labels ("ON TRACK", "AT RISK") split across two lines.

### Fix

DOM walker JS now captures `whitespace: cs.whiteSpace` for every element. In `place_element()`, `css_nowrap = whitespace in ("nowrap", "pre", "pre-line", "pre-wrap")` is evaluated before the height heuristic and used as the initial value of `is_single_line`. Both the background-shape branch and the plain textbox branch now respect this flag — `tf.word_wrap = not css_nowrap` rather than unconditional `True`.

**Definitive workaround for badge text containing spaces:** Use `&nbsp;` (non-breaking space) instead of a regular space in any badge or status pill label — e.g. `ON&nbsp;TRACK`, `AT&nbsp;RISK`. A non-breaking space cannot be broken by PPTX's text engine regardless of `word_wrap` setting. This works even when the `whitespace` fix does not take effect (e.g. when the span's computed whitespace is overridden by its flex-item context).

**Skill rule added:** Any badge or pill element whose text contains a space MUST use `&nbsp;`. Document in Phase A mockup authoring guidance.

---

## 15. QA Fixes Listed as Options Instead of Applied (Post-Build Reviewer Pass)

**Status:** Fixed

**Session:** 2026-05-14 Phase Test

### Problem

After Phase B QA identified correctness failures (text overflow, orphan lines, undersized font, too-small process boxes, page number placeholder not filled, footer missing width), Claude listed the fixes as choices for the user rather than applying them immediately. The user had to explicitly instruct Claude to apply fixes — adding an unnecessary round trip.

**Root cause:** No explicit rule in SKILL.md requiring auto-application of correctness failures. Claude treated layout fixes as design decisions.

### Fix

**Mandatory auto-fix table added to Post-Build Reviewer Pass Step 4a** (`SKILL.md`):

| Finding | Auto-fix |
|---------|----------|
| Text wraps to orphan lines | Trim content, reduce line-height, or increase textbox width |
| Font size < 14px | Raise to 14px |
| Process box height too small for content | Increase height |
| Page number placeholder still reads "X" or "N" | Replace with actual slide number |
| Footer text element has no explicit width | Add `width:800px` |

These are correctness failures. Claude applies all found, re-delivers, and notes what was auto-fixed in the reviewer summary. The user is never asked which to apply.

---

## 16. Template Master Footer Bleeds Through on Layouts Without a Footer Placeholder

**Status:** Fixed — `PP_PLACEHOLDER.FOOTER` clear added to `build_slide.py` immediately after slide creation. Re-verify on any new client template by checking that master footer text does not appear on built slides.

**Session:** 2026-05-14 Phase Test

### Problem

When a slide's layout does not expose a footer placeholder, the slide master's default footer text remains visible in the built PPTX even when a `data-role="footer"` element is present in the HTML mockup. The invariant placement path looks for a footer placeholder on the slide layout — finding none, it places nothing, and the master footer text is never overwritten.

**Root cause:** `build_slide.py` invariant path: writes `data-role="footer"` content into the layout's footer placeholder by `idx`. If the layout has no footer placeholder, the write is silently skipped. Master-level footer placeholder text is not suppressed independently.

**User description:** Template footer "Slide Lab — Internal Reference" appeared on Slide 3 even though the HTML had a different footer element.

### Workaround applied

Removed `data-role="footer"` from the Slide 3 footer element and raised the font to 14px so Phase B treats it as a regular text box placed by `place_element`, which renders on top of the master footer text.

### Suggested fix (not yet built)

After building each slide in Phase B, iterate the slide's placeholders and clear any with `PP_PLACEHOLDER.FOOTER` type before the invariant path runs:

```python
from pptx.enum.text import PP_PLACEHOLDER
for ph in slide.placeholders:
    if ph.placeholder_format.type == PP_PLACEHOLDER.FOOTER:
        ph.text_frame.clear()
```

This suppresses master footer text on all slides, regardless of whether the layout exposes a footer placeholder. The `data-role="footer"` element then renders on top as a normal overlay shape.

**Alternative:** Remove `data-role="footer"` from the invariant path entirely and always treat footer elements as regular 14px text boxes placed by `place_element`.

---

## 18. Native `<table>` Elements Return h=0 in Playwright — Silent Empty Slide

**Status:** Workaround available

### Problem
Native HTML `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<td>`, and `<th>` elements return `getBoundingClientRect().height = 0` in Playwright's layout engine when placed inside `position:absolute` containers. `place_table()` in `build_slide.py` silently returns when `h <= 0` — no error, no warning, no shape in the PPTX. The slide renders completely blank for the table area.

Confirmed across three separate build passes in the 2026-05-15 PMO session. Explicit `height:468px` and `position:absolute` on the `<table>` did not fix it — CSS `height` on `<table>` is treated as `min-height` by browsers, and Playwright's synchronous layout evaluation returns 0 before reflow completes.

### Fix
**Never use native `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<td>`, or `<th>` elements in slide HTML.** All tabular data must use div-based rows:

```html
<!-- WRONG — table will be silently absent in PPTX -->
<table style="position:absolute; top:200px; left:58px; width:1164px; height:400px;">
  <thead><tr><th>Status</th><th>Workstream</th></tr></thead>
  <tbody><tr><td>On Track</td><td>Finance</td></tr></tbody>
</table>

<!-- CORRECT — div rows render reliably -->
<div style="position:absolute; top:200px; left:58px; width:1164px;">
  <div style="display:flex; background:#260048; color:white; height:32px; align-items:center;">
    <div style="width:120px; padding:0 8px; font-size:12px; font-weight:700;">Status</div>
    <div style="flex:1; padding:0 8px; font-size:12px; font-weight:700;">Workstream</div>
  </div>
  <div style="display:flex; height:40px; align-items:center; border-bottom:1px solid #E0E0E0;">
    <div style="width:120px; padding:0 8px; font-size:12px;">On Track</div>
    <div style="flex:1; padding:0 8px; font-size:12px;">Finance</div>
  </div>
</div>
```

---

## 17. Future Improvements / Deferred Items

### 17a. End-of-session debrief built into the delivery step

**Status:** Fixed — "Session Debrief" section added to `slide-builder/SKILL.md` after the reviewer pass. The four debrief questions are asked automatically at delivery; answers are saved to `_session/debrief-YYYY-MM-DD.md`.

**What it should do:** After the deck file path is output, slide-builder automatically asks the user four short questions before the session closes. Answers are saved to `_session/debrief-YYYY-MM-DD.md`. No separate invocation required — debrief is part of delivery.

**Questions (plain language — no internal terminology):**
1. Did any slides need to be rebuilt? (yes → which ones, what was wrong / no)
2. Did you have to edit anything in PowerPoint manually before sending? (yes → what / no)
3. Did any slide feel like it missed what you were going for? (yes → which one, what was off / no)
4. If the deck had charts — did the drafts show the right story? (yes / no + what was off / no charts)

**Why this matters:** Debriefs accumulate in `_session/` across sessions. Reviewing them periodically surfaces patterns — repeated failures or workarounds — that become candidates for updating this file and the SKILL.md.

**Implementation:** Small addition to the delivery step in SKILL.md. After the output file path block, the skill asks the four questions and saves responses to `_session/debrief-YYYY-MM-DD.md`.
