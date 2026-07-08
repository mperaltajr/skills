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
| `{{LIKELY_PRIOR_PATTERNS}}` | Forecasted patterns for slides N-1 and N-2 from the prep-time pattern-hint pass — **context, not constraint**. The agent can override if its brief read differs from the forecast. |
| `{{LAYOUTS_MD_PATH}}` | Absolute path to `reference/layouts.md` |
| `{{ANTI_PATTERNS_MD_PATH}}` | Absolute path to `reference/anti-patterns.md` |
| `{{SKILL_MD_PATH}}` | Absolute path to `SKILL.md` |
| `{{HELPERS_MODULE_PATH}}` | Absolute path to `slide-builder/` — the parent directory of `twins/helpers.py`. Goes on `sys.path` so `from twins.helpers import ...` resolves. |
| `{{PATTERN}}` | Build-path routing for this slide: `sketch` = HTML output (worker writes `option_X.html`; translator converts to native python-pptx at Stage 3.5), `direct` = python-pptx direct. Defaults to `direct` for unrouted builds. |

---

# Slide {{SLIDE_N}} build prompt — `{{SLIDE_TITLE}}`

You are building **slide {{SLIDE_N}} of {{SLIDE_TOTAL}}** of a deck using `slide-builder`. Produce **three structurally distinct options** for this single slide.

**This slide's build path is `{{PATTERN}}`** — and that determines your output format:
- **`direct`** → write three standalone python-pptx scripts: `option_A.py`, `option_B.py`, `option_C.py`. Each is executed by `finalize_deck.py` at finalize time.
- **`sketch`** → write three HTML files instead: `option_A.html`, `option_B.html`, `option_C.html`. A translator converts the picked one to native python-pptx downstream. Do NOT write `.py` files on a `sketch` slide.

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

   If the brief signal does not clearly map to one of these 7, **stop and emit SKELETON_REJECTED**:

   ```
   # SKELETON_REJECTED: ambiguous editorial intent — brief does not map to {recommend, warn, diagnose, show urgency, show progress, compare neutrally, summarize}
   ```

   Do **not** invent an 8th verb. Do **not** default to "compare neutrally" when the brief is actually arguing a position — that's the failure mode this step exists to prevent. The closed vocabulary is deliberately small so it never regrows into an open-ended, hard-to-maintain set of named intents.

   **Rule of one.** Exactly one verb per slide. If two seem to apply, pick the one the brief leads with. If you cannot decide between two, that's a brief problem — emit SKELETON_REJECTED rather than picking both.

   State your verb in the PATTERN PICK output block (added below) AND in the SLIDE BUILD REPORT (§ 10).

2. **Take the highest-scoring pattern.** If two or more tie, use the rotation seed.

   - Your pattern-pick seed: `{{PATTERN_PICK_SEED}}`
   - Tiebreak rule: interpret the first hex character of the seed as a number (0–15). Modulo the number of tied patterns. Pick that index from the sorted-alphabetical list of tied pattern names.
   - Example: if "50/50 vertical" and "Top band + body" tie and the seed starts with `7`, then `7 mod 2 = 1`, sorted alphabetically: `["50/50 vertical", "Top band + body"]`, index 1 = "Top band + body."

3. **Adjacency context (Hardline #3 — soft-enforced here, hard-enforced at the gate-preview + review steps via `build_gate_preview.py` + `build_review.py`).** Likely prior patterns from the prep-time hint pass:
   ```
   {{LIKELY_PRIOR_PATTERNS}}
   ```
   **This is a forecast, not a constraint.** The prep-time pattern-hint pass ran the same signals table you are running now, but it does not know what you will actually pick. Override the hint if your brief signal clearly points at a different pattern.

   **Soft rule:** if your top-scoring pattern would create a third consecutive same-split run **and** your scoring confidence is low (multiple patterns within ~1 signal of each other), prefer the next-best pattern that breaks the run. If your top-scoring pattern is the clear winner, keep it — `build_gate_preview.py` and `build_review.py` run a post-build adjacency scan that surfaces 3+ same-split runs as an advisory in `GATE3-PREVIEW.html` and `REVIEW.html` for the user to resolve at pick time.

   Do not bend brief fidelity (Hardline #4) to satisfy adjacency. Brief fidelity wins; adjacency is the lower-priority concern that gets resolved at the gate-preview + review steps.

4. **Check the curved-container trigger.** If the slide concept implies a curved-container diagram (hub-spoke, Porter's Five Forces, ecosystem map, fishbone, concentric rings, free-form network), the routing depends on `{{PATTERN}}` from the dispatch:

   **Direct path (python-pptx, no native curve primitives):** For each of the three options write `option_X.py` with line 1 = `# SKELETON_REJECTED: curved-container diagram — not supported in the direct path; re-route through the sketch path for HTML+SVG`. The script body has `import sys; sys.exit(0)`. The rejection surfaces in REVIEW.html and the user re-routes the slide through the sketch path.

   **Sketch path (HTML-first):** Author the curved diagram natively in HTML/SVG within the body zone. Use `data-shape-id` to mark elements the translator should convert to native shapes; use `<img>` or inline `<svg>` for genuinely curve-shaped paths. The sketch path is the modern replacement for the retired Mermaid fallback.

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
  Variant tilt  : <one-line description of how the verb will shape at least one of the three variants — e.g., "Option B asymmetric weight toward recommended option, accent stripe">
  Seed used?    : <yes/no — yes if you tiebroke with {{PATTERN_PICK_SEED}}>
  Adjacency     : <one of: matches hint / overrides hint / no prior context / would-be-3-in-a-row, kept anyway because top scorer>
  Curved-container? : <no | yes-rejected-routed-to-Pattern-B | yes-authored-in-Pattern-B-HTML>
```

---

## 5. Pick three variants — your autonomy within the pattern

You produce **three structurally distinct options** for the same picked pattern. The options differ on variant choices — typography weight, accent placement, icon vs. no-icon, numeral vs. no-numeral, eyebrow vs. no-eyebrow, light vs. dark canvas where the pattern allows it, anchor side (left vs. right) for asymmetric splits.

**Variant picking rules:**

- Read the picked pattern's "Variants" list in `layouts.md`. Those are your degrees of freedom.
- The three options must be **genuinely different**, not three near-clones with one tweak each. A reasonable person should pick differently between them based on aesthetic preference.
- Use the per-option variant seeds to vary your starting variant choice — each of the three options has its own seed so the three end up on different variants. The seeds also prevent 5 parallel agents on the same brief from picking the same variant set.
  - Option A variant seed: `{{VARIANT_SEED_A}}`
  - Option B variant seed: `{{VARIANT_SEED_B}}`
  - Option C variant seed: `{{VARIANT_SEED_C}}`
  - Tiebreak rule within variants is the same as the pattern tiebreak: first hex character mod the number of eligible variants, sorted alphabetically by variant name.
- One option SHOULD push the pattern further than the safe-default version (e.g., dark canvas instead of light, hero metric instead of bullets, oversized typography instead of standard). The user picks among the three; offering one safer + two bolder is good.
- **All three variants MUST use at least one brand token on a load-bearing element** (hero text, accent rule, divider, anchor, fill — NOT placeholders like `[Date]` or `[Presenter]`). A "safe default" is *quieter typography or composition* — not the absence of brand identity. Every option must include `BRAND_PRIMARY`, `BRAND_ACCENT`, `BRAND_PRIMARY_MID`, or `BRAND_ACCENT_SOFT` somewhere visible. A variant rendering only in TEXT_DARK / TEXT_MID / TEXT_FAINT is a brand-fidelity failure. **Vary the brand application across the three variants** — don't converge on the same element (e.g., A on accent rule, B on hero fill, C on anchor circle).

**Do not produce three options on three different patterns.** That defeats the point of pattern-picking. All three options use the same pattern; only the variants differ.

**At least one of the three variants MUST explicitly honor the directive verb you identified in § 4 step 1.5.** Variant tilt translation lives at `layouts.md § "Directive verb vocabulary"`. For "recommend": asymmetric weight toward the recommended item. For "warn": high-contrast accent on the threat. For "compare neutrally": equal weight, no accent winner. The honoring variant is not necessarily the safest of the three — bolder tilt is fine. What matters is that the three options are not all cosmetic variations of a neutral default; at least one carries the directive verb visibly. State which variant honors the directive in the PATTERN PICK output block.

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

- **Direct path** (default; python-pptx direct): write the three files listed below as `.py` scripts.
- **Sketch path** (HTML-first): write `option_A.html`, `option_B.html`, `option_C.html` instead of `.py` files. Conventions in `slide-builder/reference/sketch-html-spec.md`. Chrome text on elements with `data-template-field`; body shapes on elements with `data-shape-id`. Self-check by rendering each HTML via `scripts/render_html.py` and reading the resulting 1280×720 PNG before declaring done. Do NOT also write `.py` files — the sketch path's downstream translator agent converts the picked HTML to native python-pptx at Stage 3.5.

For the direct path, write three files to `{{OUTPUT_DIR}}`:

```
{{OUTPUT_DIR}}\option_A.py
{{OUTPUT_DIR}}\option_B.py
{{OUTPUT_DIR}}\option_C.py
```

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

   **Footer/source content — explicit choice required (F3, 2026-05-26).** When you call `add_footer(slide, page_num, source=..., footnote=...)`, every slide's `footnote` and `source` arguments must be either **real text from the brief** or **explicit `None`**. Omitting or passing `None` is not an accident — it renders the slide-builder intentional presenter prompt (`[add footnote here or delete]` / `[add source here or delete]`), which the presenter fills or deletes before showing the deck. slide-qc allowlists these exact strings as Advisory, not Critical. **Decide consciously per slide:** if the brief supplies a source citation or footnote, pass it as text; if not, pass `None` and the placeholder is the expected outcome. Do not stuff in fabricated source text just to make the footer look complete — that violates Hardline #2.
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

---

## 9. Constraints

- **Touch only files in `{{OUTPUT_DIR}}`.** The expected files are `option_A.py`, `option_B.py`, `option_C.py` (direct path) OR `option_A.html`, `option_B.html`, `option_C.html` (sketch path — when the dispatch's `PATTERN` field is `sketch`), plus the generated `.pptx` / `.png` siblings (when the script or renderer runs). Do not write to any other path. Do not modify `_prompt.md` or any file outside this directory.
- **Do not modify `slide-builder\twins\helpers.py`.** It is shared geometry infrastructure; structural changes break every script that depends on it.
- **Do not read or modify other slides' brief content.** You see only this slide's brief.
- **Do not write summaries, plans, or design docs to disk.** Inline reasoning goes in your response, not in side-files.
- **No external assets.** No PIL, no PNG embedding for native patterns, no chart image generation. Bars, waterfalls, KPI tiles — all drawn with `add_rect` + `add_text`. (Curved diagrams that historically used the Mermaid fallback now route to the sketch path's HTML+SVG; see § 4 step 4.)
- **Use the brand palette constants only.** Never raw `RGBColor(...)` literals. The named constants from `twins.helpers` are: `BRAND_PRIMARY`, `BRAND_PRIMARY_MID`, `BRAND_ACCENT`, `BRAND_ACCENT_SOFT`, `TEXT_DARK`, `TEXT_MID`, `TEXT_FAINT`, `CARD_BG`, `CARD_BORDER`, `WHITE`.
- **Font sizes are locked to PowerPoint's default grid (floor 8pt).** Every visible text size must be one of: **8, 9, 10, 10.5, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 44, 48, 54, 60, 66, 72, 80, 88, 96** (pt) — never an off-grid value like 7.3 or 8.2, and never below 8pt. The finalize step snaps any straggler to the nearest grid size, but author on the grid so what you design is what ships.
  - **Direct path (.py):** set `font_size_pt=` to a grid value (use `font_size_pt`, not raw `Pt(...)` arithmetic that lands off-grid).
  - **Sketch path (HTML):** CSS uses px; px = pt × 4⁄3. Size text so it maps to the grid — e.g. **8pt→10.67px, 9pt→12px, 10.5pt→14px, 12pt→16px, 14pt→18.67px, 18pt→24px, 24pt→32px, 32pt→42.67px**. Body claims/bullets ≥ 10.5pt (14px); eyebrows/labels may go down to 8pt (10.67px) but no smaller. See `reference/sketch-html-spec.md` § "Font-size grid".
- **Insertion order = paint order.** Background fills first, foreground/text last.

---

## 10. After writing the three option scripts

Output this block as the **last thing** in your response (the parent session captures it):

```
SLIDE {{SLIDE_N}} BUILD REPORT
  Pattern picked  : <pattern name>
  Directive verb  : <one of the 7 verbs>
  Variant tilt    : <one-line — which option (A/B/C) honors the directive, and how>
  Variant A       : <one-line variant description>  | <status: built | SKELETON_REJECTED>
  Variant B       : <one-line variant description>  | <status>
  Variant C       : <one-line variant description>  | <status>
  Curved container? : <no | rejected-routed-to-Pattern-B | yes-via-Pattern-B-HTML>
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
