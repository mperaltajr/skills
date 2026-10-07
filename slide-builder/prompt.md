# Per-slide build prompt — slide-builder

This file is the **template** loaded by `scripts/build_deck.py`. At prep time, the build script renders one copy per slide with brief content and slide metadata interpolated into `{{PLACEHOLDER}}` tokens. The rendered output lands at `<out>/slide_NN/_prompt.md` and becomes the dispatched agent's task.

Placeholders rendered by `build_deck.py`:

| Token | Meaning |
|---|---|
| `{{SLIDE_N}}` | Slide number (1-indexed) |
| `{{SLIDE_TOTAL}}` | Total slides in this deck |
| `{{SLIDE_TITLE}}` | Slide title from the brief |
| `{{GOVERNING_THOUGHT}}` | The slide's claim (verbatim from brief) |
| `{{SO_WHAT}}` | The takeaway (verbatim from brief) |
| `{{EDITORIAL_EMPHASIS}}` | Editorial direction from the brief |
| `{{EVIDENCE_CONTENT}}` | Supporting content / evidence block |
| `{{CHART_TYPE}}` | Chart type from brief (`none` or scatter/line/bar/waterfall/donut/quadrant) |
| `{{CHART_DATA}}` | Chart data block from brief (inline table, CSV/Excel path, or `TBD — placeholder`). Build the chart from this when `{{CHART_TYPE}}` is not `none`. |
| `{{NOT_THIS_SLIDE}}` | "What this slide is NOT" block (may be empty) |
| `{{VISUAL_RHYTHM}}` | Optional steering: the dominance pattern the brief wants (e.g. `conclusion-dominant`, `contrast-dominant`). Honor it when set; else use your judgment. |
| `{{PINNED_SOURCE_PAGE}}` | A page the user supplied to be reproduced on this slide, or `(none)`. When set, option A must reproduce it. |
| `{{MANDATORY_SHAPE}}` | Optional steering: a layout shape the brief requires (e.g. `two-column`, `three-column`). When set, the picked pattern MUST satisfy it. |
| `{{FORBIDDEN_PATTERNS}}` | Optional steering: pattern stems the brief excludes. Do NOT pick any pattern named here. |
| `{{ACCENT_PLACEMENT}}` | Optional steering: where the accent color should land on this slide. Honor it when set. |
| `{{DECK_LEVEL_DESIGN_NOTES}}` | Deck-level constraints from the brief (binding on every slide) |
| `{{CLIENT_TEMPLATE_PATH}}` | Absolute path to client PPTX template |
| `{{OUTPUT_DIR}}` | Absolute path where option scripts must be written |
| `{{CONTENT_HASH}}` | md5 hex digest of `governing_thought + so_what + evidence_content` — locked at prep time by `build_deck.py`; used by the seeds below |
| `{{PATTERN_PICK_SEED}}` | md5 hex digest of `content_hash + slide_n` — your tiebreaker when multiple patterns score equally |
| `{{VARIANT_SEED_A}}` | md5 hex digest of `content_hash + slide_n + "A"` — variant tiebreaker for option A |
| `{{VARIANT_SEED_B}}` | md5 hex digest of `content_hash + slide_n + "B"` — variant tiebreaker for option B |
| `{{VARIANT_SEED_C}}` | md5 hex digest of `content_hash + slide_n + "C"` — variant tiebreaker for option C |
| `{{LAYOUTS_MD_PATH}}` | Absolute path to `reference/layouts.md` |
| `{{ANTI_PATTERNS_MD_PATH}}` | Absolute path to `reference/anti-patterns.md` |
| `{{SKILL_MD_PATH}}` | Absolute path to `SKILL.md` |
| `{{HELPERS_MODULE_PATH}}` | Absolute path to `slide-builder/` — the parent directory of `twins/helpers.py`. Goes on `sys.path` so `from twins.helpers import ...` resolves. |
| `{{PATTERN}}` | Build-path routing for this slide: `sketch` = HTML output (worker writes `option_X.html`; translator converts to native python-pptx at Stage 3.5), `direct` = python-pptx direct. Defaults to `direct` for unrouted builds. |

---

# Slide {{SLIDE_N}} build prompt — `{{SLIDE_TITLE}}`

You are building **slide {{SLIDE_N}} of {{SLIDE_TOTAL}}** of a deck using `slide-builder`. Produce the **{{OPTIONS_COUNT}} option(s)** ({{OPTION_LETTERS}}) this prompt lists for this single slide — one by default; more only when the count says so. When you produce more than one, make them structurally distinct.

**This slide's build path is `{{PATTERN}}`** — and that determines your output format. Produce **{{OPTIONS_COUNT}} option(s)** ({{OPTION_LETTERS}}) — the exact file list is in §8:
- **`direct`** → write standalone python-pptx script(s) (`.py`, e.g. `option_A.py`). Each is executed by `finalize_deck.py` at finalize time.
- **`sketch`** → write HTML file(s) (`.html`, e.g. `option_A.html`) instead. A translator converts the picked one to native python-pptx downstream. Do NOT write `.py` files on a `sketch` slide.

The full output contract for each path is in §6 below. Read it before writing anything.

You are one of {{SLIDE_TOTAL}} parallel agents dispatched from the same parent session. The other agents are building the other slides at the same time. You see only your slide's brief content. You do not see the other slides' content directly, but you do see the patterns picked for the previous two slides — those constrain you via the adjacency rule (Hardline #3).

---

## 1. Brief content (only this slide)

**Slide title:** {{SLIDE_TITLE}}

**Governing thought (the claim):**
{{GOVERNING_THOUGHT}}

**So-what (the takeaway):**
{{SO_WHAT}}

**Editorial emphasis:**
{{EDITORIAL_EMPHASIS}}

**Evidence / content:**
{{EVIDENCE_CONTENT}}

**What this slide is NOT:**
{{NOT_THIS_SLIDE}}

**Chart type:** {{CHART_TYPE}}

**Chart data:**
{{CHART_DATA}}

### Per-slide steering (honor when set; otherwise use your own judgment)

- **Visual rhythm:** {{VISUAL_RHYTHM}}
- **Mandatory shape:** {{MANDATORY_SHAPE}} — when this names a shape, the pattern you pick MUST satisfy it.
- **Supplied page to reproduce:** {{PINNED_SOURCE_PAGE}} — when this names a page, **option A reproduces that page**: its structure, sections and wording, rebuilt on the client template. Do not summarize it or replace it with your own design; any other options may reinterpret it. Its figures are reconciled against the brief separately (the source ledger), so where the brief gives a number, use the brief's.
- **Forbidden patterns:** {{FORBIDDEN_PATTERNS}} — never pick a pattern named here.
- **Accent placement:** {{ACCENT_PLACEMENT}}

These steering fields come from the brief author. A set value is a constraint, not a suggestion; an unset value (shown as a `(...)` placeholder) leaves the choice to you.

### Content density (binding)

{{DENSITY_DIRECTIVE}}

---

## 2. Deck-level design notes (binding on every slide)

{{DECK_LEVEL_DESIGN_NOTES}}

These constraints override your variant choices wherever they conflict. If the deck-level notes say "no dark canvas," do not pick a dark-canvas variant even when the pattern would otherwise support it.

---

## 3. Before you write any code — read these two files

**You MUST read both files before picking a pattern.** They are the architecture.

1. **Layout catalog** (the 14 patterns + 1 fallback):
   ```
   {{LAYOUTS_MD_PATH}}
   ```
   This is your pattern picker. Read § "How to pick" and the signals table first, then skim each pattern's "Use when" line. You will refer back to the picked pattern's "Variants" list while writing the option scripts.

2. **Anti-pattern library** (the don't-library, scanned once preventively):
   ```
   {{ANTI_PATTERNS_MD_PATH}}
   ```
   Scan all five categories (Aesthetics, Structural, Content, Chrome, Encoding) before writing any code. Re-read the entries relevant to your picked pattern before finalizing each option script (see § 7 below).

Do not skip either file. The patterns in `layouts.md` and the rules in `anti-patterns.md` are the architecture — most failure modes trace to one of them.

---

## 4. Pick a pattern (your job, not the script's)

There is no pre-classifier. You pick the pattern from the 14 in `layouts.md` based on the brief.

**Picking procedure:**

1. **Score each of the 14 patterns** against the signals in `layouts.md § "How to pick"`. The signal types: item count, comparison shape, data shape, visual weight, diagram type, directive verb.

1.5. **Identify editorial intent — the directive verb.** Read the governing thought + editorial_emphasis line. Map to **exactly one** of the closed 7-verb vocabulary at `layouts.md § "Directive verb vocabulary"`:

   ```
   recommend | warn | diagnose | show urgency | show progress | compare neutrally | summarize
   ```

   storyline-helper writes the emphasis as one of six words. Map it, then read the governing thought to settle the verb:

   | Brief says the emphasis is | Verb |
   |---|---|
   | the conclusion | recommend (summarize if the slide restates the deck's answer) |
   | the ask | recommend |
   | the contrast | compare neutrally, or recommend when the brief favors one side |
   | the evidence | diagnose |
   | the data / the numbers | diagnose, or show progress for results against a plan, show urgency for a deadline or a falling metric |

   Do **not** invent an 8th verb. Do **not** default to "compare neutrally" when the brief is actually arguing a position. Never reject a slide over the verb: if the emphasis is missing or unclear, pick the verb the governing thought leads with and say why in the PATTERN PICK block.

   **Rule of one.** Exactly one verb per slide. If two seem to apply, pick the one the brief leads with.

   State your verb in the PATTERN PICK output block (added below) AND in the SLIDE BUILD REPORT (§ 10).

2. **Take the highest-scoring pattern.** If two or more tie, use the rotation seed.

   - Your pattern-pick seed: `{{PATTERN_PICK_SEED}}`
   - Tiebreak rule: interpret the first hex character of the seed as a number (0–15). Modulo the number of tied patterns. Pick that index from the sorted-alphabetical list of tied pattern names.
   - Example: if "50/50 vertical" and "Top band + body" tie and the seed starts with `7`, then `7 mod 2 = 1`, sorted alphabetically: `["50/50 vertical", "Top band + body"]`, index 1 = "Top band + body."

3. **Adjacency (Hardline #3).** You do not know what the designers of the neighboring slides will pick, so do not guess. Pick the best pattern for this slide's brief; the review page flags any run of 3 same-split slides for the user to resolve at pick time. Do not bend brief fidelity (Hardline #4) to avoid a run.

4. **Check the curved-container trigger.** If the slide concept implies a curved-container diagram (hub-spoke, Porter's Five Forces, ecosystem map, fishbone, concentric rings, free-form network), the routing depends on `{{PATTERN}}` from the dispatch:

<!-- only:direct -->
   **Direct path (python-pptx, no native curve primitives):** For each option the prompt lists (§8), write `option_X.py` with line 1 = `# SKELETON_REJECTED: curved-container diagram — not supported in the direct path; re-route through the sketch path for HTML+SVG`. The script body has `import sys; sys.exit(0)`. The rejection surfaces in REVIEW.html and the user re-routes the slide through the sketch path.
<!-- /only -->

<!-- only:sketch -->
   **Sketch path (HTML-first):** Author the curved diagram natively in HTML/SVG within the body zone. Use `data-shape-id` to mark elements the translator should convert to native shapes; use `<img>` or inline `<svg>` for genuinely curve-shaped paths. The sketch path is the modern replacement for the retired Mermaid fallback.
<!-- /only -->

   Do **not** substitute a different pattern just to avoid the trigger. Silent substitution is the failure mode this protocol exists to prevent.

5. **Check the brief/pattern agreement (Hardline #5).** If the brief enumerates 2 items but your picked pattern needs 4 cells (and vice versa), brief and pattern fundamentally disagree. Emit:
   ```
   # SKELETON_REJECTED: <one-line reason — e.g., brief enumerates 2 items, pattern needs 4 cells>
   ```
   as the **first line** of `option_X.py` and stop. Do not fabricate a third or fourth item to fit. Hardline Rule #2 forbids fabrication beyond brief enumeration.

**State your pick before writing any code.** Output this block in your response (the parent session inspects it):

```
PATTERN PICK — Slide {{SLIDE_N}}
  Picked        : <pattern name from layouts.md>
  Top signals   : <which signals matched, 2-3 max>
  Directive verb: <one of: recommend | warn | diagnose | show urgency | show progress | compare neutrally | summarize>
  Variant tilt  : <one-line description of how the verb shapes the option(s) — with one option, how that single option honors the verb; with more, which option carries the strongest tilt, e.g., "asymmetric weight toward the recommended item, accent stripe">
  Seed used?    : <yes/no — yes if you tiebroke with {{PATTERN_PICK_SEED}}>
  Curved-container? : <no | yes-rejected-routed-to-sketch-path | yes-authored-in-sketch-HTML>
```

---

## 5. Your option(s) — autonomy within the pattern

Produce **{{OPTIONS_COUNT}} option(s)** ({{OPTION_LETTERS}}) for the SAME picked pattern.
- **When exactly one** (the default), make it the single strongest execution of the pattern — one that clearly honors the directive verb (§4 step 1.5). Don't hedge toward a neutral default; commit to the best design.
- **When more than one**, the options must be **structurally distinct** executions of that one pattern — differing on typography weight, accent placement, the style of the structure markers (numerals in circles vs. large numerals vs. icon shapes; see "Make the structure visible" below), eyebrow vs. none, light vs. dark canvas where allowed, anchor side. Genuinely different, not near-clones; a reasonable person would pick differently on aesthetic preference. Offer a spread — one safer + the rest bolder (dark canvas, hero metric, oversized type) — so the reviewer has a real choice.

**Variant rules:**

- Read the picked pattern's "Variants" list in `layouts.md`. Those are your degrees of freedom.
- Use the per-option variant seed(s) to vary your starting variant choice (they also stop parallel agents on the same brief from converging on the same variant):
{{VARIANT_SEEDS}}
  - Tiebreak within variants: first hex character mod the number of eligible variants, sorted alphabetically by variant name.
- **Every option MUST use at least one brand token on a load-bearing element** (hero text, accent rule, divider, anchor, fill — NOT placeholders like `[Date]` or `[Presenter]`). A "safe default" is *quieter typography or composition* — not the absence of brand identity. Every option includes `BRAND_PRIMARY`, `BRAND_ACCENT`, `BRAND_PRIMARY_MID`, or `BRAND_ACCENT_SOFT` somewhere visible; a variant rendering only in TEXT_DARK / TEXT_MID / TEXT_FAINT is a brand-fidelity failure. When you produce multiple options, vary which element carries the brand.

**Make the structure visible (default, every option).** When the slide's content is a sequence or a set of parallel items (steps, phases, stages, levers, pillars, options, sources, criteria, workstreams), show that structure, don't just list it:
- **Number only real sequences:** steps, phases, stages, dated plans, or items the deck refers to by number. A set with no order (levers, pillars, options, criteria, sources) gets a marker but no numbers, because a number implies an order that isn't there.
- **Give each item a simple marker** drawn with native shapes: a circle, chevron, small rounded square or a simple icon built from shapes. No emoji, no clip art, no image files.
- **When the items happen in order**, connect them with arrows, chevrons or a line, so the sequence reads at a glance.
- **Arrows stop short of the boxes.** Work out each arrow's start and end from the box EDGES (not the box centers) and leave at least 8 px between an arrowhead and the box it points at; an arrowhead touching or inside a box is flagged (`MAJOR_ARROW_END_AT_BOX` on the review page). On a **cycle or loop** diagram, also leave at least 60 px between neighboring boxes so each arrow has room to show, and keep the boxes off the arrow's path. On 2026-10-06 a loop's arrowheads ran into the boxes in the sketch, and the finished slide copied it.
- **Skip it only when it would be false or noise:** a single claim, a quote, a chart that already carries the structure, or items with no order or grouping.
- **No trailing periods** on headings, labels, callouts or one-sentence text boxes. Multi-sentence paragraphs keep normal punctuation.

Users had to ask for this in words every round ("how come we aren't using process icons/numbers"). Doing it unasked is the default now; the review page's "Add process structure" button exists for the cases you miss.

**All options use the SAME pattern** — only the variants differ. Don't spread options across different patterns.

**At least one option MUST explicitly honor the directive verb from § 4 step 1.5** (with a single option, that one must). Variant tilt translation lives at `layouts.md § "Directive verb vocabulary"`: "recommend" → asymmetric weight toward the recommended item; "warn" → high-contrast accent on the threat; "compare neutrally" → equal weight, no accent winner. State which option honors the directive in the PATTERN PICK output block.

---

## 6. The 5 hardline rules (re-read before writing each option)

These are non-negotiable. Every option script must satisfy all five. The full text lives at `{{SKILL_MD_PATH}}`; inline summary below.

1. **Charts and tables only in their respective object layouts.** No fake chart-looking visuals in card grids. Inline sparklines and micro-charts in other layouts are allowed.
2. **No fabrication beyond brief enumeration.** If the brief says 2 paths, the slide has 2 items. No invented third or fourth.
3. **No 3+ consecutive slides on the same split.** See § 4.3 above — the adjacency check.
4. **Brief fidelity.** Every visible word on the slide traces to brief content or documented chrome (footer, page number, section label). No invented eyebrows, framework names, or section labels. **Structural-count fabrication (e.g., 4 cards when the brief enumerates 2) is the hard non-negotiable.** You self-attest to this in line 3 of each `option_X.py` header (`# Brief fidelity check: ...`); the rule is enforced by that attestation plus human inspection in REVIEW.html.
5. **SKELETON_REJECTED protocol.** If brief and pattern fundamentally disagree, emit the marker as line 1 and stop. No silent substitution.

---

## 7. Don't-library cross-check (mandatory before each option finalizes)

After you have a draft option script but before you call it done, re-read the relevant entries in `anti-patterns.md` for the pattern you picked. Cross-check matrix:

| Picked pattern | Anti-pattern entries to re-check |
|---|---|
| Full canvas, 50/50, 75/25 | Aesthetics #1 (accent overuse), #4–#5 (dark-fill contrast), #6 (font sizes), #7 (single accent moment) |
| Top band + body | Aesthetics #1, #7; Content #1 (no invented evidence cards) |
| N-column row, Vertical N-row stack | Aesthetics #6, #8 (vertical spacing); Content #1 (no invented columns/rows); Structural #5 (Unicode glyphs) |
| Dense grid | Aesthetics #6; Encoding #1 (size-encoding needs scale legend) |
| Left rail + body | Content #3 (no invented page-of-total), #4 (no invented section labels); Chrome #1 (invariant zones) |
| Horizontal bands | Aesthetics #4–#5 (dark band contrast); Aesthetics #7 (single accent) |
| Org chart, Decision tree | Structural #2 (no auto-routed connectors); Structural #4 (text-box overlap) |
| Swimlane | Structural #2, #4; Content #5 (3+ consecutive same-split — though swimlane is rarely consecutive) |
| Chart (incl. quadrant) | Encoding #1 (scale legend), #2 (named-framework convention positions); Chrome #3 (legend placement) |
| Table | Chrome #4 (no stacked RECOMMENDED badges — use accent stripe); Aesthetics #6 (font sizes) |
| Any with curved-container concept | Structural #1 (no text inside curves — route to fallback) |

This list is a heuristic for which entries are most load-bearing per pattern. The full library still applies — entries not listed here can still bite you. Scan the file once before writing code; re-read the pattern-specific entries before finalizing each option.

---

## 8. Output contract

**Pattern routing for this slide:** `{{PATTERN}}`

Produce **{{OPTIONS_COUNT}} option(s)** ({{OPTION_LETTERS}}) — no more, no fewer.

- **Direct path** (default; python-pptx direct): write the option(s) as `.py` script(s) — the exact file(s) listed below.
- **Sketch path** (HTML-first): write the option(s) as `.html` instead (the sketch file list below); do NOT also write `.py`. Conventions in `slide-builder/reference/sketch-html-spec.md`. Chrome text on elements with `data-template-field`; body shapes on elements with `data-shape-id`. Self-check by rendering each HTML via `scripts/render_html.py option_X.html option_X.sketch.png` and reading the resulting 1280×720 PNG before declaring done. Use exactly that output name: the review page shows `option_X.sketch.png`, and `option_X.png` is the name finalize gives the finished slide, so a render saved there is wasted and can be mistaken for a finished slide. The picked HTML is converted to native python-pptx by the translator at Stage 3.5.

<!-- only:direct -->
Direct-path file(s) to write:

```
{{OPTION_FILES_DIRECT}}
```
<!-- /only -->

<!-- only:sketch -->
Sketch-path file(s) to write instead:

```
{{OPTION_FILES_SKETCH}}
```
<!-- /only -->

<!-- only:direct -->
Each `option_X.py` is a **standalone runnable Python script** that:

1. Imports from `slide-builder\twins\helpers.py` — the shared chrome helpers (title block, footer, brand colors, primitives). Add the absolute path to `sys.path` at the top of each script:
   ```python
   import sys
   sys.path.insert(0, r"{{HELPERS_MODULE_PATH}}")
   from twins.helpers import (
       new_slide, add_title_block, add_footer,
       add_rect, add_text, add_circle, add_icon,
       BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
       TEXT_DARK, TEXT_MID, TEXT_FAINT, CARD_BG, CARD_BORDER, WHITE,
   )
   ```
2. Does **NOT** open the client template directly. Build slide content fresh on a 1280×720 canvas using `new_slide()` from `twins.helpers` — this returns `(prs, slide)` with no template. `finalize_deck.py` handles the graft of your slide onto `{{CLIENT_TEMPLATE_PATH}}` after your script saves. The client template path is provided in § 11 as context only; your script does not need to load it.
3. Builds the slide using `twins.helpers` for chrome (title block at the top, footer at y≈672) and raw python-pptx primitives for body geometry.

   **Footer/source content — explicit choice required.** When you call `add_footer(slide, page_num, source=..., footnote=...)`, every slide's `footnote` and `source` arguments must be either **real text from the brief** or **explicit `None`**. `None` draws nothing (since 2026-06-15). **Never write the presenter prompts `[add footnote here or delete]` / `[add source here or delete]` yourself**, on either path: on the sketch path, a slide whose brief gives no source or footnote simply has no source or footnote element. If the brief's deck-level notes set one source line for every slide (for example "Illustrative data, not real"), use it. Do not invent source text just to make the footer look complete — that violates Hardline #2.
4. **Saves the slide as the exact filename `option_<A|B|C>.pptx`** in the same directory as the script. `finalize_deck.py` looks for this exact filename next to the `.py` (`option_A.pptx`, `option_B.pptx`, or `option_C.pptx`). The script is invoked with **NO command-line arguments** — do **NOT** use `sys.argv[1]`. Standard pattern:

   ```python
   if __name__ == "__main__":
       prs = build()
       prs.save(str(Path(__file__).resolve().parent / "option_A.pptx"))
   ```

   Replace `"option_A.pptx"` with `"option_B.pptx"` or `"option_C.pptx"` for those options. `Path(__file__).resolve().parent` is the safe way to write to the script's own directory regardless of CWD. (`finalize_deck.py` does set CWD to the slide directory, so a bare relative `"option_A.pptx"` also works, but absolute is more robust if anyone runs the script manually from a different CWD.)

**Script header convention** (lines 1–8 of every option script, in this order):

```python
# Slide {{SLIDE_N}} option <A|B|C> — pattern: <picked pattern name>
# Variant: <one-line description of the variant chosen, e.g., "dark canvas, oversized typography, left-anchored">
# Brief fidelity check: <one-line statement that every visible word traces to brief or documented chrome>
import sys
from pathlib import Path
sys.path.insert(0, r"{{HELPERS_MODULE_PATH}}")
from twins.helpers import (...)
# ...
```

If the option must be rejected for **brief/pattern disagreement** (Hardline #5):

```python
# SKELETON_REJECTED: <one-line reason — e.g., brief enumerates 2 items, pattern needs 4 cells>
# Slide {{SLIDE_N}} option <A|B|C> — pattern attempted: <pattern name>
import sys
sys.exit(0)
```

If the option must be rejected for **curved-container diagram under the direct path** (per § 4 step 4), write **only** the `.py`:

```python
# SKELETON_REJECTED: curved-container diagram — not supported in the direct path; re-route through the sketch path for HTML+SVG
# Slide {{SLIDE_N}} option <A|B|C> — pattern attempted: <pattern name>
import sys
sys.exit(0)
```

(For the sketch path the worker authors the curved diagram natively in HTML/SVG inside the body zone; no SKELETON_REJECTED is needed.)

finalize_deck.py reads line 1. Token prefix decides routing:
- `# SKELETON_REJECTED:` → rejection surfaces in REVIEW.html for user resolution (brief/pattern disagreement OR unsupported curved-container under the direct path).
<!-- /only -->
<!-- only:sketch -->
**Source and footnote (sketch path).** Put the brief's source line in the element with `data-template-field="footer"`. If the brief's deck-level notes set one source line for every slide (for example "Illustrative data, not real"), use it. If the brief gives no source, leave the footer element out. **Never write `[add source here or delete]` or `[add footnote here or delete]`.** If the brief and the pattern fundamentally disagree (Hardline #5), write no HTML for that option; write `option_X.py` whose line 1 is `# SKELETON_REJECTED: <reason>` and whose body is `import sys; sys.exit(0)`, and stop.
<!-- /only -->

---

## 9. Constraints

- **Never close, kill or restart the user's programs.** No `taskkill`, `Stop-Process`, `pkill` or killing by name or PID for `msedge.exe`, `chrome.exe`, `POWERPNT.EXE` or any other process you did not start yourself in this command. The user is working in those windows (killing a "stuck" Edge closed the owner's browser, 2026-10-06). Render only through `scripts/render_html.py` / `scripts/_browser.py`, which start their own separate browser and close only that one; never launch `msedge.exe` directly. If a render hangs, let it time out and report it.
- **Touch only files in `{{OUTPUT_DIR}}`.** The expected files are the option file(s) listed in §8 (`.py` for the direct path, `.html` for the sketch path when `PATTERN` is `sketch`), plus their generated `.pptx` / `.png` siblings (when the script or renderer runs). Do not write to any other path. Do not modify `_prompt.md` or any file outside this directory.
- **Do not modify `slide-builder\twins\helpers.py`.** It is shared geometry infrastructure; structural changes break every script that depends on it.
- **Do not read or modify other slides' brief content.** You see only this slide's brief.
- **Do not write summaries, plans, or design docs to disk.** Inline reasoning goes in your response, not in side-files.
- **No external assets.** No PIL, no PNG embedding for native patterns, no chart image generation. Bars, waterfalls, KPI tiles — all drawn with `add_rect` + `add_text`. (Curved diagrams that historically used the Mermaid fallback now route to the sketch path's HTML+SVG; see § 4 step 4.)
- **Use the brand palette constants only.** Never raw `RGBColor(...)` literals. The named constants from `twins.helpers` are: `BRAND_PRIMARY`, `BRAND_PRIMARY_MID`, `BRAND_ACCENT`, `BRAND_ACCENT_SOFT`, `TEXT_DARK`, `TEXT_MID`, `TEXT_FAINT`, `CARD_BG`, `CARD_BORDER`, `WHITE`.
- **Type scale (owner's rule; checked on the final check page and in QC as Major).**
  - **Body text is 12 pt by default**: bullets, card text, table cells and headers, labels, eyebrows, step numbers, captions. Design at **12, 14 or 16 pt**, with **at most 3 body sizes on the slide** (e.g. 16 headings, 14 key lines, 12 detail). **Only when the content truly cannot be cut further** (a dense table, many labels) may detail text drop to **11 or 10.5 pt, never lower**; it still counts toward the 3 sizes, and it shows as a note on the final check page. The title and takeaway use the template's own sizes and are not counted. One large hero figure (24 pt or more) is allowed and not counted.
  - **Exceptions, not under 9 pt:** sources, footnotes, and text that is part of a chart (axis titles, tick labels, legend, data labels on bars or lines). Name these shapes so the check recognizes them: `chart-...` for every chart piece (e.g. `chart-ylab-200`, `chart-legend-vn`, `chart-val-2030`), `source-...` and `footnote-...`. Anything else is body text.
  - **If it does not fit at 12 pt, first cut words, drop a column or split the content.** Going down to 10.5 pt is the last resort, never the first fix, and never below 10.5 pt. Never add a fourth size for one line.
  - Every size must be on PowerPoint's default grid (9 and 10 for exceptions only; 10.5 and 11 as the last-resort body sizes; 12, 14, 16, 18, 20, 24, 28, 32 ... for the rest), never off-grid like 7.3 or 8.2. The finalize step snaps stragglers to the grid, but author on it so what you design is what ships.
<!-- only:direct -->
  - **Direct path (.py):** set `font_size_pt=` to a grid value (use `font_size_pt`, not raw `Pt(...)` arithmetic that lands off-grid).
<!-- /only -->
<!-- only:sketch -->
  - **Sketch path (HTML):** CSS uses px; px = pt × 4⁄3. Size text so it maps to the grid — e.g. **8pt→10.67px, 9pt→12px, 10.5pt→14px, 12pt→16px, 14pt→18.67px, 18pt→24px, 24pt→32px, 32pt→42.67px**. Body text (bullets, labels, eyebrows, table cells) is 12pt (16px) by default, 10.5pt (14px) at the very lowest when the content cannot be cut, in at most 3 sizes; only sources, footnotes and chart text may go down to 9pt (12px). See `reference/sketch-html-spec.md` § "Font-size grid".
<!-- /only -->
- **Insertion order = paint order.** Background fills first, foreground/text last.

---

## 10. After writing your option script(s)

Output this block as the **last thing** in your response (the parent session captures it):

```
SLIDE {{SLIDE_N}} BUILD REPORT
  Pattern picked  : <pattern name>
  Directive verb  : <one of the 7 verbs>
  Variant tilt    : <one-line — which option honors the directive, and how>
  Variants        : one line per option you built ({{OPTION_LETTERS}}) —
                    <letter>: <one-line variant description> | <status: built | SKELETON_REJECTED>
  Curved container? : <no | rejected-routed-to-sketch-path | yes-via-sketch-HTML>
  Anti-patterns   : <list any anti-pattern entry numbers you specifically guarded against>
  Brief fidelity  : <one-line statement, e.g., "every word on every option traces to brief or chrome">
```

If any option is SKELETON_REJECTED, state the reason in the variant line. Do not proceed to write the next slide's prompt or comment on other slides — you handle only this slide.

---

## 11. Reference paths (read once at start)

```
Layout catalog          : {{LAYOUTS_MD_PATH}}
Anti-pattern library    : {{ANTI_PATTERNS_MD_PATH}}
SKILL.md                : {{SKILL_MD_PATH}}
Helpers module          : {{HELPERS_MODULE_PATH}}
Client template         : {{CLIENT_TEMPLATE_PATH}}
Output directory        : {{OUTPUT_DIR}}
```

Begin.
