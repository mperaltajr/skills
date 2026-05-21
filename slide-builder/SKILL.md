---
name: slide-builder
description: "Builds real PowerPoint slides from a narrative brief. The default Slide Lab flow runs parallel agent fanout against the client template and is documented at the top of this skill. A legacy pattern-library fallback (Pattern Library → Skeleton → HTML authoring) remains available for fast internal builds. All paths render PNG options for user review, then build the final PPTX. Invoked by storyline-helper after the narrative gate passes, or directly for 'rebuild slide N'."
---

# Slide Builder

The build layer of Slide Lab. The mockup is the spec.

---

## Skill routing — read before doing anything else

**This skill is invoked AFTER storyline-helper, not instead of it.**

Before any build path begins (pattern library match, skeleton match, or HTML authoring), verify that storyline-helper has run for every slide being built this session.

| Trigger phrase | Correct action |
|---|---|
| "help me build a slide" / "make a deck" / "add a slide" | Invoke **storyline-helper** first. Do not proceed until the narrative gate passes. |
| "rebuild slide N" on an existing deck | Skip storyline-helper. For a client-facing deck, route the rebuild through the **Slide Lab build flow** (single-slide fanout — see section at top of file). For internal / low-stakes rebuilds, run the legacy pattern-library fallback check — Pattern Library, then Skeleton, then HTML authoring. See **What this skill does** below. |
| Brief already exists + user wants to add slides | **Invoke storyline-helper in edit mode**. After gate passes, run the build flow. |
| User says "fill in [template name]" or "use this template" and provides data | Template fill mode — see **Template Fill Mode** section below. |
| User says "promote this slide to my library" + provides PPTX | Run `promote_skeleton.py` — see **Adding Skeletons** section below. |
| User says "add this to the pattern library" + provides HTML | Drop the HTML into `_pattern-library/NN_<slug>.html`, update `_pattern-library/INDEX.md`, append to `REVIEW.html` MOCKUPS array. |

**Hard stop:** If the user's request adds any new slide content and **no narrative brief exists** → stop and invoke storyline-helper from Step 0. If a brief already exists but the new slides haven't been gated → invoke storyline-helper's edit-mode handler (see "Handling edge cases" in storyline-helper/SKILL.md). Either way, do not build new slide content until the narrative gate has passed for those slides.

## Slide Lab build flow — the default path

The Slide Lab build flow is the validated **default build path for client-facing decks**. It produces visibly higher design quality on real client work than the legacy pattern-library fallback below. Use it whenever the deck will be shown to a client. The legacy pattern-library fallback below remains available for fast internal builds and low-stakes work.

### When to use the default flow vs the legacy fallback

| Use the default flow when | Use the legacy fallback when |
|---|---|
| Deck is client-facing, board-facing, or external | Internal status update, working session, brown-bag |
| Visual quality is load-bearing on outcome | Speed > polish; deck will be thrown away |
| Slides need bespoke composition against the client template | Standard editorial patterns (cards, matrices, stats) cover the intent |
| Brief has 3+ distinct narrative slides | One-off rebuild of a single slide |

### Four-stage architecture

```
STAGE 1 · PREP            build_deck.py
                          Reads narrative brief + client template.
                          Writes one self-contained agent prompt per slide,
                          each carrying the FULL design rulebook
                          (phase-a-rules, slot-design-rules,
                          visual-treatment-library, page-types, rules,
                          glossary, known-issues, designer-brief, QC skill).
                          Output: <out>/slide_NN/_prompt.md + dispatch_plan.md

STAGE 2 · PARALLEL FANOUT deck-builder agents
                          Parent session dispatches one agent per slide IN
                          PARALLEL (Task tool, single message with N calls).
                          Each agent reads its _prompt.md and produces three
                          standalone python-pptx scripts:
                          option_A.py / option_B.py / option_C.py
                          Each script builds ONE slide against the client
                          template — full design rulebook in scope per agent.
                          NOTE: dispatched from the parent session, not from
                          inside the agent itself.

STAGE 3 · FINALIZE        finalize_deck.py
                          Executes every option_X.py, grafts each rendered
                          slide onto the client template, and renders PNGs
                          via LibreOffice headless. Produces option_A.pptx /
                          option_B.pptx / option_C.pptx + matching .png per
                          slide.

STAGE 4 · REVIEW          build_review.py
                          Builds REVIEW.html with all 3N options laid out
                          for user picks. User picks per-slide options.
                          compile_picks.py then stitches the chosen
                          option per slide into the final deck.pptx grafted
                          onto the client template.
```

### File paths

- Prep: `%USERPROFILE%\.claude\skills\slide-builder\scripts\build_deck.py`
- Finalize: `%USERPROFILE%\.claude\skills\slide-builder\scripts\finalize_deck.py`
- Review: `%USERPROFILE%\.claude\skills\slide-builder\scripts\build_review.py`
- Compile picks: `%USERPROFILE%\.claude\skills\slide-builder\scripts\compile_picks.py`
- Agent definition: `%USERPROFILE%\.claude\agents\deck-builder.md`
- Designer brief: `%USERPROFILE%\.claude\skills\slide-builder\reference\designer-brief.md`

### One-command sequence (PowerShell)

```powershell
# Stage 1 — Prep prompts
python %USERPROFILE%\.claude\skills\slide-builder\scripts\build_deck.py `
    --brief <BRIEF.md> --template <CLIENT_TEMPLATE.pptx> --out <OUT_DIR>

# Stage 2 — Parallel agent fanout
#   DISPATCHED FROM THE PARENT SESSION, NOT FROM INSIDE THE AGENT.
#   Single message with N Task-tool calls, one per slide, agent =
#   deck-builder, prompt = contents of <OUT_DIR>/slide_NN/_prompt.md.

# Stage 3 — Finalize: execute option scripts, graft, render PNGs
python %USERPROFILE%\.claude\skills\slide-builder\scripts\finalize_deck.py `
    --root <OUT_DIR> --template <CLIENT_TEMPLATE.pptx>

# Stage 4 — Build review UI for picks
python %USERPROFILE%\.claude\skills\slide-builder\scripts\build_review.py `
    --root <OUT_DIR>

# User picks options in REVIEW.html → records picks → then compile:
python %USERPROFILE%\.claude\skills\slide-builder\scripts\compile_picks.py `
    --root <OUT_DIR> --template <CLIENT_TEMPLATE.pptx>
```

### Why this flow wins

1. **Full design rulebook in every prompt.** Each per-slide agent gets the entire reference set (phase-a-rules, slot-design-rules, visual-treatment-library, page-types, designer-brief, QC skill) injected into its prompt. No partial-context drift.
2. **Parallel quality, not parallel speed.** Three independent options per slide, each authored against the same rulebook, give the user genuine compositional choice rather than three variants of the same idea.
3. **Output grafts onto the client template.** Slides are produced directly against the client's PPTX template — no layout drift, no theme reconstruction. The final deck inherits the client's master, fonts, and chrome.

---

## What this skill does

**There is one engine: the Slide Lab build flow. A legacy pattern-library fallback exists for fast internal builds. Pick the path FIRST, based on whether the deck is client-facing.**

### Default — Slide Lab build flow (client-facing decks)

For any deck that will be shown to a client, board, or external audience: use the **Slide Lab build flow** (documented above in **Slide Lab build flow — the default path**). The flow:

1. **Setup.** Confirm the client template path with the user. Read the brief — **explicitly read the `## Deck-level design notes` section and state its contents before proceeding**; those constraints are binding.
2. **Narrative + Content gates.** Verify governing thoughts are specific and assertive; verify enough raw content per slide. Skip if storyline-helper already gated this session.
3. **Stage 1 — Prep.** Run `build_deck.py` to emit one self-contained agent prompt per slide (full design rulebook baked in).
4. **Stage 2 — Parallel fanout.** Dispatch one `deck-builder` agent per slide IN PARALLEL from the parent session. Each agent produces three standalone python-pptx scripts (option_A/B/C).
5. **Stage 3 — Finalize.** Run `finalize_deck.py` to execute every option script, graft onto the client template, and render PNGs via LibreOffice.
6. **Stage 4 — Review + compile.** Run `build_review.py` to build REVIEW.html; user picks per-slide options; `compile_picks.py` stitches the final deck.
7. **QC.** Run slide-qc against the compiled deck.
8. **Deliver.** PPTX. Output full absolute Windows path. No preview links.

Rebuild individual slides with "rebuild slide N" — re-prep the prompt for slide N, dispatch a single agent, finalize, and replace the picked option.

### Legacy fallback — pattern-library hybrid (fast / internal / low-stakes builds only)

For internal status updates, working sessions, brown-bags, throwaway decks, or single-slide one-offs where speed beats polish: use the legacy pattern-library fallback (Pattern Library → Skeleton → HTML authoring). Each slide intent is checked against the three sub-paths in order. On this path, most slides land on the Pattern Library; structural-only slides land on Skeletons; only truly novel slides fall through to HTML authoring from scratch. The flow:

1. **Setup.** Confirm the client template path with the user (Step 0). Read the brief — **explicitly read the `## Deck-level design notes` section and state its contents before proceeding**; if that section has entries, those constraints are binding on every option (not suggestions). Run `--print-theme` to extract brand colors and fonts. Run `--catalog-layouts` if the template has named layouts.
2. **Narrative Gate.** Verify governing thoughts are specific and assertive. Skip if storyline-helper's gate already passed this session.
3. **Content Sufficiency Gate.** Verify enough raw content exists to build a substantive slide.
4. **Pattern Library match (Tier 1, the primary sub-path within the legacy fallback).** For each slide in the brief, check the curated pattern library at `_pattern-library/` against the slide intent. Read `_pattern-library/INDEX.md` for the catalog of ~100 approved patterns (anchored cards, comparison matrices, hero stats, charts, frameworks, etc.). Match by intent + visual structure. If a pattern matches → that HTML is the slide's starting point; fill content placeholders from the brief; this becomes one option in the mockup review. See **Pattern Library Match** section below for the full protocol. On the legacy path, most slides match a pattern.
5. **Skeleton matching (Tier 2).** For slides with no pattern-library match, attempt to match against `skeletons/`. Skeletons are best for: covers (`cover`), dividers (`hero-numeral-divider`), pure structural layouts (`two-panel`, `three-column-pillars`), and chart-with-takeaway variants. If a skeleton matches → use the token-fill + structural-patches pipeline. See **v2 Skeleton Pipeline** below.
6. **HTML mockup authoring (Tier 3, only when no pattern AND no skeleton matches).** For truly novel slides that neither library covers, author HTML mockup options from scratch. Read `reference/phase-a-rules.md` and `reference/visual-treatment-library.md` at this point, not before. See **Phase A — Authoring HTML mockups** below.
7. **Render options + user picks.** Pattern-matched and HTML-authored slides render through Playwright. Skeleton-matched slides render directly to PNG via LibreOffice. All options shown in one review UI. Picks saved to `_session/selections.md`.
8. **Phase B — Build.** Apply selections — skeleton-matched slides receive patches; HTML-authored slides go through the Playwright build engine; pattern-matched slides go through `twins/composer.py` (copy the matching hand-built PPTX twin from `_renders/twins/NN_*.pptx` and substitute text + fill by shape name — no Playwright, no HTML render). User never sees the engine choice. See **Pattern Library Match** section below for the twins pipeline.
9. **Reviewer pass.** Structured QA against the post-build checklist + the 12-category deck-page-quality audit at `_pattern-library/_qc-reference/deck-page-quality-SKILL.md`. Flags surfaced to user before delivery.
10. **Deliver.** PPTX + xlsx companion. Output full absolute Windows path for every file. No preview links — the user's environment has no preview panel.

Rebuild individual slides on the legacy path with "rebuild slide N" — re-run the legacy fallback check for that slide; if pattern matches, use it; if skeleton matches, use it; otherwise regenerate three HTML options.

## Architecture in one diagram

_Note: **The Slide Lab build flow lives ABOVE this diagram (production default for client-facing decks).** The diagram below describes the legacy pattern-library fallback that is kept for fast internal builds, low-stakes work, and one-off rebuilds._

```
For each slide intent in the brief, check the three tiers in order:

┌──────────────────────────────────────────────────────────────────────┐
│   TIER 1 · PATTERN LIBRARY (primary; ~100 curated HTML patterns)     │
│                                                                      │
│   Match intent + visual structure against _pattern-library/*.html    │
│   (use _pattern-library/INDEX.md as the catalog of approved patterns)│
│                                                                      │
│   If match → use that HTML as the slide's starting point             │
│              fill content placeholders from the brief                │
│              render via Playwright → PNG option in the review UI     │
│                                                                      │
│   If no match → drop to Tier 2 for this slide only                   │
└──────────────────────────────────────────────────────────────────────┘
                          ↓  (per-slide, no pattern match)
┌──────────────────────────────────────────────────────────────────────┐
│   TIER 2 · SKELETON LIBRARY (structural matches; covers, dividers)   │
│                                                                      │
│   Match against skeletons/<id>/skeleton.yaml                         │
│   Best for: covers, dividers, pure structural layouts (two-panel,    │
│   three-column-pillars), chart-with-takeaway variants                │
│                                                                      │
│   If match → token fill + structural patches → PPTX directly         │
│              render via LibreOffice → PNG option in review UI        │
│                                                                      │
│   If no match → drop to Tier 3 for this slide only                   │
└──────────────────────────────────────────────────────────────────────┘
                          ↓  (per-slide, no skeleton match)
┌──────────────────────────────────────────────────────────────────────┐
│   TIER 3 · HTML AUTHORING FROM SCRATCH (truly novel slides only)     │
│                                                                      │
│   Read reference/phase-a-rules.md + visual-treatment-library.md      │
│   Theme colors + fonts from --print-theme; layouts from --catalog    │
│                                                                      │
│   Author 3 HTML mockup options                                       │
│      ↓                                                               │
│   Render via Playwright → PNG options in review UI                   │
│                                                                      │
│   On build:                                                          │
│     Visual / freeform  →  build_slide.py (Playwright → PPTX)         │
│     Table / structured →  python-pptx direct                         │
└──────────────────────────────────────────────────────────────────────┘

After all slides are matched + options rendered:
  → review.html shows all options together (regardless of tier)
  → User picks → _session/selections.md
  → Phase B builds the final deck.pptx
  → slide-qc runs the 12-category audit
```

The Pattern Library protocol is described in **Pattern Library Match** immediately below. Do not read `reference/phase-a-rules.md` until you have first checked the pattern library AND the skeleton library for every slide and identified which (if any) actually need the Tier 3 fallback.

## Pattern Library Match — primary sub-path within the legacy fallback (NOT for client-facing decks)

> **Legacy fallback (pattern library) only.** This section and everything below it through the end of the legacy fallback documentation describes the Pattern Library / Skeleton / HTML-mockup path. For client-facing decks use the Slide Lab build flow instead (see top of file).

The **first** path checked for every slide intent. The pattern library at `_pattern-library/` is a curated collection of ~100 approved HTML pattern files, each one a self-contained 1280×720 mockup with the brand CSS variables, top chrome, footer invariant zone, and the standing QC checklist baked in. Patterns cover the common consulting layouts: anchored cards, comparison matrices, hero stats, charts, frameworks, RAG dashboards, org charts, before/after, and so on.

### Step 1 — Read the index

```python
# Conceptual — adapt to actual file ops
read("_pattern-library/INDEX.md")  # full catalog with status (APPROVED / REVIEW / REJECTED)
```

The INDEX lists every pattern by number, name, and approval status. Skip rejected patterns. Prefer approved over review-pending. Each row links to the underlying HTML file (`_pattern-library/NN_<slug>.html`).

### Step 2 — Match by intent + visual structure

For each slide in the brief, score the candidate patterns. Signals:

| Signal | What to look for |
|---|---|
| **Slide intent / page-type** | Does the brief say "exec summary" / "RAG dashboard" / "case study" / "decision matrix" / "cover" / etc.? Map to a pattern family. |
| **Content shape** | Number of bullets, columns, rows. Brief has 4 stat tiles? Match pattern 12 (KPI dashboard) or 59 (stat bank). Brief has 3 vertical columns with rich bullets? Match pattern 02 (three pillars) or 60 (3-horizon roadmap). |
| **Editorial weight** | Brief calls for a single big stat? Pattern 26 was rejected — match 10 (chart with annotation) or 26-replacement instead. |
| **Brand chrome** | Cover slide → use the client template's cover layout via skeleton path, not a pattern (pattern library covers are generic). |

If a pattern scores ≥3 signals, take it. Otherwise drop to Tier 2 (skeleton match).

### Step 3 — Use the pattern as the slide template

The matched pattern HTML is **the spec**. Copy it into `_session/mockups.html` (or treat it as one option in the mockup file). Then:

1. **Replace content placeholders** — the pattern has sample content (e.g., "Sarah Kim · Senior Manager"). Swap with the brief's actual content (action title, sub-headline, bullets, stat values, attribution). Do NOT change layout, typography, or chrome.
2. **Re-theme brand colors** — if the user's template uses non-Accenture brand colors, update the CSS variables at the top of the pattern HTML (only `--brand-primary`, `--brand-primary-mid`, `--brand-accent`, `--brand-accent-soft`, `--card-bg`, `--card-border`). Everything else stays.
3. **Preserve the standing QC** — patterns are already QC'd; don't break them by adding visual treatments not in the original.

### Step 4 — Render as part of mockup review

Render the filled pattern HTML via Playwright to a PNG. Add it as an option in the mockup review. If multiple patterns could fit one slide, include 2 of them as alternates.

### Step 5 — Build (when user picks)

Pattern-matched slides build through `twins/composer.py`. Each approved pattern has a hand-built PPTX twin at `_renders/twins/NN_*.pptx`; the composer copies the twin and substitutes text + fill by shape name (the `data-shape-id` from the HTML maps 1:1 to `shape.name` in the twin). No Playwright. No HTML rendering at build time.

Two entry points:

- **Programmatic:** `from twins.composer import compose_deck; compose_deck(out_path, slides=[{"pattern": "12_kpi-tile-dashboard", "overrides": {"title": "...", "metric-1-value": "62%", ...}}, ...])`
- **YAML deck spec:** write a spec (see `twins/_example-deck.yaml`) and run `python -m twins.deck_spec twins/<your-deck>.yaml`. The spec lists `output:` + a `slides:` array of `{pattern, overrides}`.

Unknown shape ids in `overrides` are logged and skipped (find-or-skip — never raises). For small per-twin nudges that aren't covered by text/fill (move a shape, change a font size, recolor a card border), use `twins/translator.py`'s `apply(twin_path, adjustments)` — it takes an explicit `{shape_id: {text|fill|left|top|width|height|font_size|font_color|bold|italic|align}}` dict. The translator does NOT parse CSS; the caller supplies the deltas.

For the full system overview, read `twins/README.md`. For the canonical shape-id vocabulary, read `_pattern-library/SHAPE-ROLES.md`.

### Pattern library files to know

- `_pattern-library/INDEX.md` — catalog of all patterns with status
- `_pattern-library/REVIEW.html` — visual review UI (open in browser to see all patterns)
- `_pattern-library/BACKLOG.md` — queue of unbuilt patterns for future sessions
- `_pattern-library/_qc-reference/deck-page-quality-SKILL.md` — the 12-category audit that QC must apply at build time
- `_pattern-library/_HANDOFF-2026-05-18.md` (in `slide-builder/`) — architecture pivot history + brand conventions

### When to skip the pattern library

- Cover slides: the pattern library covers (06, 19) are generic — for branded client templates, use the skeleton path (`cover` skeleton applies the client's cover layout).
- Slides that require a chart type not in the library (Pareto, Sankey, etc. → check the BACKLOG; if it's listed, mark it pending and add to next autonomous build run).
- Truly bespoke / one-of-a-kind slides → drop to Tier 3 (HTML authoring).

### Standing rules (apply to every pattern-matched slide)

- **Standing QC checklist (must satisfy all 6):** visual hierarchy clear, single focal point, consistent margins, intentional whitespace, grid alignment, balanced page.
- **Legend placement rule:** legends always top-right, BELOW the title + subheadline + brand-accent rule. Never overlapping the title.
- **12-category deck-page-quality audit** — see `_pattern-library/_qc-reference/deck-page-quality-SKILL.md`. Patterns ship pre-QC'd, but content-fill mistakes can break QC (e.g., a too-long action title that wraps). Re-check after filling.

---

## v2 Skeleton Pipeline — Tier 2 (when no pattern matches)

> **Legacy fallback (pattern library) only.** Skeleton matching, token fill, structural patches, and the skeleton review loop below are the internal-build fallback. For client-facing decks use the Slide Lab build flow instead (see top of file).

The skeleton pipeline is the **second** path checked, used when the Pattern Library has no match for a slide intent. It is faster than HTML authoring, more consistent, and structurally validated. Best for: covers (brand-template-driven), dividers, two-panel comparisons, three-column-pillars, chart-with-takeaway variants.

### Overview

```
Brief slide intent
      ↓
Match skeleton family + variant
      ↓
Fill {{TOKEN}} placeholders from brief
      ↓
Apply structural patches (if content shape differs from skeleton default)
      ↓
Render PPTX → PNG via LibreOffice
      ↓
Generate review.html (A/B options) → user picks
      ↓
Apply targeted patches from selections
      ↓
Deliver final PPTX
```

### Step 1 — Skeleton matching

For each slide in the brief, determine the best skeleton family using the signals table below. Score each family against the slide's characteristics and pick the highest match. If no family scores 3+ signals → **fall back to Playwright** (see "Phase B build routing").

**Skeleton families and match signals:**

| Family | `page_types` keywords | Content signals | Strong signals |
|--------|----------------------|-----------------|----------------|
| `cover` | cover, title-slide, opening | Has a deck title and date/client | Slide position = 1 |
| `single-finding` | finding, hero-stat, big-number, insight, key-metric | Has one dominant quantitative value | Brief calls out "headline stat" or "hero number" |
| `two-panel` | comparison, before-after, two-options, side-by-side | 2 named options or scenarios being compared | Brief uses "vs.", "compare", "before/after" |
| `three-column` | three-pillars, objectives, priorities, three-column, workstreams | 3 parallel items with equal weight | Brief has 3 bullets/objectives with owners or KPIs |
| `recommendation` | recommendation, action-items, next-steps, closing | Concrete action items with owner + deadline fields | Slide position = last; brief has "owner" and "deadline" fields |
| `process-chevron` | process, timeline, phases, roadmap, milestones, workplan | Sequential named phases (2–4) with timing | Brief mentions "Phase N" or sequential steps |
| `chart-with-takeaway` | chart, data, trend, distribution, performance | `Chart type:` field is not "none" | Has quantitative data table or `Chart data:` field |

**chart-with-takeaway variants** — pick by takeaway prominence:

| Variant | Use when |
|---------|----------|
| `chart-with-takeaway-third` | Standard: chart takes ~2/3, takeaway panel takes ~1/3 |
| `chart-with-takeaway-third-hero` | Takeaway has a hero stat + supporting text (not just bullets) |
| `chart-with-takeaway-bottom-strip` | Takeaway is one concise sentence — strip at bottom |
| `chart-with-takeaway-quarter` | Chart is the dominant story — takeaway is secondary |
| `chart-with-takeaway-quarter-hero` | Chart dominant + hero stat callout in takeaway area |
| `chart-with-takeaway-dual` | Two charts side by side with shared takeaway below |
| `chart-with-takeaway-full` | Chart fills the full slide — no takeaway panel |

**Matching output format** — log this block before filling tokens:

```
SKELETON MATCH
==============
Slide N: [slide label from brief]
  Family   : recommendation
  Variant  : recommendation (single variant)
  Signals  : page_type=closing, action items present, owner+deadline fields
  Fallback : no — 4/5 signals matched
==============
```

If fallback is triggered, explain which signals were checked and why none matched, then proceed with Playwright path.

---

### Step 2 — Token fill

Read the matched skeleton's `skeleton.yaml` to get the token list. Map each token to the corresponding brief field using this table:

| Token name pattern | Brief field to use |
|--------------------|--------------------|
| `ACTION_TITLE` | Slide's governing thought (verbatim — do not rewrite) |
| `SUB_HEADLINE` | Sub-heading or supporting sentence below the title |
| `HEADING` | Hero stat value or deck title |
| `BODY_TEXT` | Supporting narrative, one or two sentences |
| `LEFT_HEADING` / `RIGHT_HEADING` | Panel headers (e.g. "Option A", "Current State") |
| `LEFT_BODY` / `RIGHT_BODY` | First content row in each panel |
| `LEFT_ITEM_N` / `RIGHT_ITEM_N` | Subsequent content rows |
| `COL_A_HEADING` | First row, column A (action/objective/phase description) |
| `COL_B_HEADING` | First row, column B (KPI/owner/timing) |
| `COL_C_HEADING` | First row, column C (owner/deadline/timing) |
| `COL_A_BODY` / `COL_B_BODY` / `COL_C_BODY` | Second row across three columns |
| `COL_A_ITEM_N` / etc. | Subsequent rows |
| `FOOTNOTE` | Footnote text (if brief has one; else skip) |
| `SOURCE` | Source citation (if brief has one; else skip) |

**Governing thought rule:** `ACTION_TITLE` always receives the slide's governing thought verbatim. Never paraphrase. Never truncate. If it is over 85 characters (serif 24pt) or 80 characters (sans 24pt), flag it before filling: "Governing thought is N chars — may wrap on single line. Shorten before filling?"

**Sparse briefs:** If the brief has fewer items than tokens, fill available tokens and leave unused ones as empty string `""`. Never invent content.

Fill tokens using:
```python
from patches.patches import fill_tokens
filled = fill_tokens(slide, token_map)
print(f"Filled: {filled}")
```

Print the filled token list so the output can be verified before rendering.

---

### Step 3 — Structural patches

After token fill, apply patches when content shape differs from the skeleton default. Use the trigger conditions in `patches/CATALOGUE.md`. Call patches by name — never write ad-hoc python-pptx code.

**Common trigger decisions:**

| Situation | Patch to call |
|-----------|--------------|
| Brief has 3+ discrete items in a zone that defaults to prose | `convert_to_bullets(shape, items)` |
| Brief mentions an icon-mapped concept (see `reference/icon-vocabulary.md`) | `insert_icon(slide, icon_name, x, y, size, accent_hex)` |
| Default skeleton position breaks reading path (Rule 4A) | `reposition_zone(shape, x_in, y_in)` |
| Content is longer/shorter than skeleton default height | `resize_zone(shape, height_in=N)` |
| Brief has a dominant quantitative stat to lead with | `add_hero_stat(slide, stat_value, stat_label, x, y, w, h, color)` |
| Status field maps to RAG indicator | `set_rag_status(shape, status)` |
| Table needs additional rows beyond skeleton default | `add_table_row(table_shape, row_data)` |

Log each patch call:

```
PATCHES APPLIED — Slide N
  convert_to_bullets: BODY_TEXT → 4 bullet items (brief had discrete items)
  insert_icon: "growth" icon at (8.5, 0.8) → accent #FF6600
```

---

### Step 4 — Render + Review UI

**Render PPTX → PNG** using LibreOffice:
```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-qc\scripts\render_slides.py" `
  "<session_folder>\option_A.pptx" `
  "<session_folder>\renders\"
```
Produces `slide_01.png` (and subsequent slides) in the renders folder. Rename to `slide_NN_A.png` convention: `slide_01_A.png`, `slide_01_B.png`.

**Generate review HTML:**
```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\generate_review.py" `
  "<session_folder>" `
  --title "Slide Review — [Deck Name]"
```

Produces `review.html` in the session folder. Give the user the full Windows path:
```
Review UI ready: C:\path\to\session\review.html
Open in browser, pick one option per slide, paste the selections back here.
```

**Selections format** (user pastes this back):
```
=== REVIEW SELECTIONS ===
Slide 1: Option A
  Comment: "Title too long, shorten"
Slide 2: Option B
=== END ===
```

---

### Step 5 — Apply selections + deliver

Read the selections. For each slide:
1. Take the chosen option's PPTX as the base
2. Apply any comment-driven patches (shorten title → rewrite token, update `ACTION_TITLE`)
3. Re-render if any patch changes the visual output
4. Assemble final deck: use python-pptx to insert slides in order
5. Deliver: output full Windows path to the assembled PPTX

**Skeleton fallback note for delivery:**
> "Built from [skeleton family] skeleton. Any slides built via Playwright will have the standard 80/20 render note — check those slides specifically in QC."

---

### Skeleton fallback to Playwright

Use Playwright when:
- No skeleton scores 3+ signals
- Slide is a chart-within-layout that doesn't fit chart-with-takeaway variants (e.g., chart + org chart + commentary)
- Slide is a custom visual model (2×2 matrix, bow-tie, concentric rings)
- User explicitly says "freeform" or "no template"

When falling back, note it in the match log and proceed with the existing Phase A HTML path.

---

## Hard constraints — never override

0. **READ `reference/phase-a-rules.md`, `reference/visual-treatment-library.md`, AND `reference/known-issues-and-improvements.md` BEFORE GENERATING ANY MOCKUP — then produce the Phase A Pre-Check block.** Reading is not enough on its own; the output block is what proves the rules were applied. No HTML may be written until the Phase A Pre-Check block (see "Phase A pre-check" section) has been output in the conversation. If the block is absent, Phase A has not been properly started. This constraint exists because skipping these files is the failure mode that produced empty-bottom slides, buried takeaways, and three decoratively-varied-but-structurally-identical options in real sessions.

0. **Skeleton matching runs FIRST for every slide. This precedes every other constraint in this list.** Before reading `reference/phase-a-rules.md`, before writing any HTML, before generating chart PNGs for HTML embedding, before any Phase A self-check — attempt to match every slide in the brief to a skeleton in `skeletons/`. Only slides with no skeleton match fall through to the HTML mockup path, and even then only for those specific slides. Constraints #1, #9, and any other constraint that references "the mockup" or `phase-a-rules.md` applies only to HTML-fallback slides, not to skeleton-matched slides. **If you find yourself reading `phase-a-rules.md` before you have a skeleton match log, you have skipped Step 4 of "What this skill does" — stop and go back.**

1. **The mockup is the spec (HTML-fallback slides only).** Don't add a re-interpretation layer between mockup and build. Don't ask the model to write content JSON. Don't pick blueprints. The HTML *is* the build instruction. This applies to slides that fell through to the HTML fallback — not to skeleton-matched slides, where the skeleton PPTX is the spec.

2. **Data visualization charts are matplotlib-generated PNG images, never native PPTX chart objects.** "Chart objects" means data charts — bar, line, pie, waterfall, etc. Tables, org charts, shape arrangements, and 2×2 frameworks are NOT chart objects and may use python-pptx APIs directly.

   Before Phase A, generate chart PNGs from the brief's chart data using `generate_chart.py` (see **Chart generation** section). Reference them in the mockup as `<img src="_session/chart-slide-N.png">`. If chart data is "TBD — placeholder," use an amber placeholder div instead. These are DRAFT images styled with brand colors — the consultant replaces them with think-cell charts before client delivery. Native python-pptx chart objects are forbidden because they cannot reproduce MBB-quality annotations (callout pills, growth arrows, forecast shading).

3. **Brand inheritance is theme-driven, not hardcoded.** Use the client template's `accent1..6` / `dk1` / `dk2` / `lt1` / `lt2` for any color that should follow the brand. Never hardcode RGB values in Python. The builder maps mockup hex codes that exactly match a theme slot to `<a:schemeClr val="accentN"/>`.

4. **Fonts inherit from the template.** The builder stamps `<a:latin typeface="..."/>` on every run using the template's major (heading) and minor (body) fonts. Mockups should declare the corporate font in CSS (so the browser preview tries to use it) but the PPTX output is correct regardless of whether the font is installed locally.

5. **Use `py -3` for every Python invocation on Windows.** Bare `python` may resolve to LibreOffice's sandboxed Python and fail with WinError 5.

6. **No `/tmp/` paths.** Session workspace is `<session_folder>/_session/`. See **Project Folder Convention** below. Platform-portable throughout.

7. **Never use bash heredocs for files over 5 lines.** Use the create_file tool.

8. **Always output absolute Windows file paths — never preview links.** The user's environment does not have a preview panel configured; `localhost:` preview links resolve to nothing. After saving any file (mockups.html, deck.pptx, xlsx companion, placeholder-examples.html, etc.), output its full Windows path in the reply so the user can open it directly. Format: `C:\path\to\file.ext`. Apply this to every file generated in every phase — Phase A mockup, Phase B deck, chart data xlsx, placeholder examples. No exceptions.

9. **Pre-show self-check is mandatory.** Before saving `_session/mockups.html` for user review, run the canonical checklist in `reference/phase-a-rules.md` § "Pre-save file checklist." Any option that fails any item must be regenerated. Do not show the user known-failing options.

10. **Use only the canonical type scale for all mockup CSS font sizes — no exceptions.** The builder converts px → pt using `pt = px × (72 / 96)`. Arbitrary px values produce irregular pt sizes that compound across slides and cause text to bleed, clip, or look inconsistent. Allowed values:

    | Role | CSS px | PPTX pt |
    |------|--------|---------|
    | Slide title / Governing thought | 28px | 21pt |
    | Sub-heading / Section label | 22px | 16.5pt |
    | Body text | 16px | 12pt |
    | Supporting detail / Caption / Source | 14px | 10.5pt — minimum |
    | Hero numbers (stat callouts) | 40–60px | 30–45pt |

    Never use a px value not in this table. Never use fractional px values. Hero numbers are the only exception — pick one size per deck and use it consistently. For python-pptx direct builds, use the Pt() equivalents in the table above.

11. **Build the slide — never build a slide-within-slide.** When the user asks to build a slide showing X, produce a full 1280×720px canvas showing X. Never build a mockup-review wrapper (a mini slide preview floating inside an annotated frame). Meta-commentary structures are not slides. If the goal is to show what a different tool would produce vs. what Slide Lab produces, each comparison item is its own full-canvas slide. Root violation symptom: the `width` of the main content div is smaller than 1280px.

12. **Never use PowerShell `Get-Content` / `Set-Content` for HTML file manipulation.** PowerShell reads UTF-8 files as Windows-1252 by default, corrupting multi-byte characters (`•`, `—`, `✓`, `═`) to mojibake. For any edit to `.html` files: use the Edit tool with exact text anchors, or a Python script with `open(path, encoding='utf-8')`. Never use PowerShell string operations on HTML files even for "simple" line deletions.

13. **Verify layout index before any `data-layout-index` assignment.** Before assigning `data-layout-master` + `data-layout-index` to a slide div, confirm via `--catalog-layouts` output (cached in `_session/layouts.json`) that the target layout is actually blank/white. Many template layouts have colored master decorations (gradient panels, branded sidebars) that override the mockup background. For slides that must be fully white or undecorated: use the blank layout (typically `master=0, index=0`) unless `--catalog-layouts` explicitly confirms a higher index is decoration-free.

14. **Edit calls on slide blocks must cover the full block — verify with Grep.** When replacing a slide div (from opening `<div data-slide=...>` to closing `</div>`), the `old_string` must extend from the opening tag to and including the final closing tag of that slide option. Partial replacements leave orphaned HTML below the new content, which corrupts the mockup and requires destructive cleanup. After every Edit on a slide block, run a Grep to confirm no content from the old block remains in the file below the new block.

15. **When layout feedback is ambiguous, ask one specific question before changing anything.** If the user says "too much whitespace" or "the spacing is off" and two interpretations are equally plausible (e.g. "compress the items together" vs. "stretch them to fill the height"), ask the specific question — do not guess and make a change. The question costs one message; a wrong guess costs 30 minutes of back-and-forth.

16. **Position audit required before editing any absolute-positioned value.** Position audit required before any absolute-positioned edit — see Rule 6 in `reference/phase-a-rules.md` for the required output block format.

17. **Describe annotated screenshots before proposing any fix.** When the user shares a screenshot with annotations (scribbles, arrows, red boxes, highlights), do NOT immediately make a change. First output:
    ```
    SCREENSHOT READ:
    I see: [describe annotations — location, color, what they mark]
    My interpretation: [what the annotation means — too high / too low / wrong element / wrong panel]
    Proposed change: [one sentence description of the edit]
    ```
    If the interpretation could go either way, ask one confirmation question before touching anything. Never make a second attempt at the same fix without first describing what you understood from the new feedback.

18. **Before re-editing after a correction, state what was wrong.** When the user corrects an edit, do NOT immediately make another change. First output:
    ```
    CORRECTION LOG:
    What I did wrong: [specific — "moved content down when it needed to go up"]
    Updated rule: [the new understanding — "action title anchors to top of panel, ~72px from panel edge"]
    Now editing: [what will change]
    ```
    If you cannot articulate #1 and #2 clearly, you do not actually understand the correction. Ask before editing.

19. **Loop detection — stop after two failed attempts of the same type.** If you have attempted the same class of edit (same element, same axis, same problem) more than twice and the user is still unsatisfied: STOP making edits. Say: "I've made [N] attempts at [the problem] and I'm clearly missing something. [One specific question]?" The question must be answerable in one sentence — a pixel value, a direction, a target element. "Does this look right?" is not acceptable. Do not make another attempt until you have an answer.

20. **Phase B freeze triggers — recognize "build it" as a mode switch, not frustration.** Any of these phrases immediately freeze Phase A and move to Phase B, no questions asked:
    - "just build it" / "just make it"
    - "make the slides" / "make the pptx"
    - "I'm done" / "I give up on the mockup"
    - "stop changing it" / "leave it as is"
    - "forget it, just do it" / "whatever, build"
    Confirm with one line: "Freezing mockup as-is. Moving to Phase B now." Then build from the current mockup state without further edits to the HTML.

    Immediately after confirming Phase B, output this one line to the user:
    > "Note: The PPTX is an 80/20 render — font fallbacks, minor spacing, and rounded corners will differ slightly from the mockup preview. `/slide-qc` will flag anything that needs correction before presenting."

21. **"Don't touch X" locks all direct AND indirect paths to changing X.** When the user says "don't change X" (a chart, an element, a size), identify every way X could be altered — directly (the element itself) and indirectly (its container, wrapper div, aspect-ratio constraints, parent flex/grid sizing). Lock all of them. Before the edit, state: "I will only change [Y]. I will not touch [X] including [list its container / sizing / aspect ratio]." If a proposed edit would change a parent that affects X's rendered size, it is forbidden — find a different approach.

22. **`data-placeholder="title"` is only for the actual slide title — nothing else.** Every other text element must use explicit `position:absolute` with defined `top`/`left`/`width`/`height` values. Misuse on quote blocks, subtitles, or body content routes that text into the layout's title placeholder at a fixed position — it may render outside the visible slide area or overlap other content with no visible error. The pre-build scan in `build_slide.py` will warn on `data-placeholder` on `<blockquote>`, `<p>`, or `<span>` elements, but the authoring rule is stricter: if it is not the slide's governing-thought title, it does not get `data-placeholder`.

23. **DOM order = PPTX layer order. `z-index` has no effect after Phase B.** DOM order = PPTX layer order; `z-index` has no effect after Phase B. See Rule 9 in `reference/phase-a-rules.md` for the full stacking guidance.

24. **Read the relevant section of `build_slide.py` before proposing any HTML fix.** If something is wrong in the PPTX, the root cause is in how the builder parses the HTML — not in the HTML itself. Before touching any element, read the relevant section of `build_slide.py` to understand what CSS properties it actually reads, what it skips, and what it cannot represent. Proposing an HTML edit based on inference about the builder's behavior — without reading the builder — is prohibited. The sequence is: read builder → understand what it will do → then and only then write HTML.

25. **Fix at the layer where the problem lives.** If the builder does not read a CSS property, the fix is in the builder — not in a post-processor, not in the HTML. If a shape is missing because the builder's extraction logic skips it, the fix is in the extraction logic — not in adding redundant wrappers. Applying a fix at the wrong layer produces output that passes the current build and fails the next one. State which layer the fix is at before writing any code.

26. **Do not report a fix as done until you have seen the output.** "This will work" is not a verification. A fix is done when the build has run, the output file exists, and you have either read the PPTX XML or run `/slide-qc` and confirmed the symptom is gone. If you cannot verify (build environment not available), say so explicitly — do not describe the expected outcome as a confirmed result.

27. **No defensive summaries after a failure.** When something you built is wrong, say what you got wrong — not what the builder's limitations are. "The builder doesn't support gradients" is a limitation. "I used a gradient without checking whether the builder reads `backgroundImage`" is what happened. The failure report goes in the first sentence. The limitation, if relevant, goes in the second. Never lead with the limitation.

28. **Scan the existing deck for colors before asking the user.** If slides already exist in the deck and a new or corrected slide needs a background color, read the existing slides' HTML mockups to find the color that was already approved and apply it. Do not ask the user "what color do you want?" when the answer is visible in the mockup or existing slides.

29. **Never use `run_in_background` or `TaskOutput` in the slide pipeline.** The build pipeline is linear and synchronous: edit → build → export → QC. Every command runs in the foreground and completes before the next one starts. `run_in_background` adds 2–3 minutes of dead polling time per build with no benefit. If the user explicitly asks for a background run, decline and explain why. This constraint applies to `build_slide.py`, `export_slides.py`, and any python-pptx patch script — no exceptions.

30. **Targeted PPTX fixes use a short python-pptx script — not the full build pipeline.** When the fix is limited to specific shapes (e.g., change background color on slides 1, 2, 4 — or fix one text value), write a 10–15 line python-pptx script that patches those shapes directly and run it. Do not run the full `build_slide.py` pipeline for targeted edits. The full pipeline re-renders every slide from HTML and takes minutes; a direct patch takes seconds. Use the full pipeline only when the HTML mockup itself has changed.

31. **Before diagnosing a stray dot or marker as a bullet formatting issue, check text box dimensions.** A floating dot or period at the left edge of a text area is almost always a period or character that wrapped to a new line because the text box had no `right` or `width` boundary — not a bullet inherited from the slide master. Check the element's CSS for a missing `right`/`width` before assuming it's a bullet problem. The fix is adding an explicit `width` or `right` value to the text box — not running any bullet-suppression script.

---

## Project Folder Convention

Every client engagement folder follows this structure. Apply it at the start of any new session.

```
<Client>/                              ← e.g. "FedEx/"
│
├── _templates/                        ← Shared PPTX templates. Never copied into sessions.
│   └── Template2.pptx
│
└── sessions/
    └── YYYY-MM-DD Topic Name/         ← One folder per working session
        ├── <output>.pptx              ← Claude's build output (no version suffix = current)
        ├── dot-dash-<topic>.md        ← Human-readable storyline for MD/EM review (visible at root)
        ├── build_<name>.py            ← Direct python-pptx script, if used
        ├── _reference/                ← Source data files used in this session (Excel, etc.)
        │   └── data.xlsx
        ├── _versions/                 ← Intermediate Claude builds within the session
        │   ├── <output>-v2.pptx
        │   └── <output>-v3.pptx
        └── _session/                  ← Skill working files (auto-created)
            ├── narrative-brief-<topic>.md   ← The session brief (slide-builder input)
            ├── theme.json             ← Brand colors + fonts from --print-theme (cached)
            ├── layouts.json           ← Template layout catalog from --catalog-layouts (cached)
            ├── mockups.html
            ├── selections.md
            ├── DECISIONS.md           ← Session decisions log — written throughout (see below)
            ├── debrief-YYYY-MM-DD.md  ← End-of-session debrief (see Session Debrief section)
            └── chart-slide-N.png     ← DRAFT chart images from generate_chart.py (one per chart slide)
```

**Rules:**
- **Templates stay at root.** `_templates/` is shared across all sessions. Never copy a template into a session folder — reference it with a relative path (`../../_templates/Template2.pptx`).
- **Each session is self-contained.** A colleague should be able to open the session folder and find everything used to build that deck: dot-dash storyline at the root (the readable version), narrative brief inside `_session/` (the slide-builder input), source data, build script, and output.
- **`_reference/` holds inputs, not outputs.** Copy any Excel or source file the user provides into `_reference/` at session start. This is how a future session (or person) knows what data drove the slide.
- **`_versions/` holds Claude's intermediate builds only.** The user's edited copy lives at the session root (no version suffix). Don't move or rename user edits.
- **Session folder name = `YYYY-MM-DD Topic`.** Use the actual date, not the meeting date. Topic should be short and descriptive (e.g. `2026-04-28 Scope Slide`, `2026-04-27 GCS-HTR Micah Update`).

**At the start of a new session:**
1. Confirm the session folder name with the user (or propose one based on context)
2. Create `sessions/YYYY-MM-DD Topic/` and `_reference/` inside it
3. Copy any user-provided data files into `_reference/`
4. **Resolve and state the output paths before writing anything.** Output this block and wait for the user to proceed:
   ```
   Session folder : C:\Users\...\Claude Projects\<Client>\sessions\YYYY-MM-DD Topic\
   Mockups will save to : ...\sessions\YYYY-MM-DD Topic\_session\mockups.html
   Deck will save to    : ...\sessions\YYYY-MM-DD Topic\<deck-name>.pptx
   ```
   Never default to `AppData\Temp` or any system path. If the session folder does not exist yet, create it first, then confirm.
5. Work entirely within the session folder — all outputs, scripts, and `_session/` go here

---

## Session Decisions Log (DECISIONS.md)

**Purpose:** Claude's context window compacts during long sessions. When that happens, the next Claude instance gets a summary — and critical decisions get lost. `DECISIONS.md` is a running log written to disk throughout the session. It survives compaction because it's a file, not context.

**When to write an entry:**
- A layout is approved by the user ("yes, that one" / user picks option A/B/C)
- A direction is explicitly rejected ("not that, go simpler" / "no panel, flat white")
- A workaround is applied (encoding fix, blank layout override, footer workaround)
- The user changes scope mid-session ("skip slide 4, add a new slide after 7")
- An interpretation is confirmed ("user confirmed: whitespace = compress items, not stretch")
- A constraint is established for this session ("all slides must use the ACN dark header")

**When NOT to write:** Don't log every tool call or every attempt. Log decisions — turning points where the session's direction was set or changed.

**Format:** Append each entry; never overwrite earlier entries.

```markdown
# Session Decisions Log
Session: [YYYY-MM-DD deck name]

---

[HH:MM] APPROVED — Slide 3 Option B (three-column dark cards). User: "yes, B."
[HH:MM] REJECTED — Slide 5 right panel layout. User: "no panel, keep it flat white."
[HH:MM] WORKAROUND — Slide 6a uses data-layout-master=0,index=0 (blank). Reason: layout index 1 injects purple gradient panel from ACN master.
[HH:MM] SCOPE CHANGE — Skip slide 8. User adding new slide after slide 7: "show what a bad AI slide looks like."
[HH:MM] INTERPRETATION CONFIRMED — "whitespace" on Slide 3 = items bunched at top, user wants them to stretch (flex:1). Not a gap issue.
[HH:MM] SESSION CONSTRAINT — All slides: use ACN dark header (#4D148C, 50px, position:absolute top:0).
```

**Save path:** `_session/DECISIONS.md`

**At session start:** Before asking the user anything, check whether `_session/DECISIONS.md` already exists in the session folder. If it does, read it immediately — it means this session has prior history and the decisions in that file are binding. Do not ask the user to re-confirm anything already logged there. Then create or append the header as needed.

**After compaction / resuming a session:** Read `_session/DECISIONS.md` as the first action. It is the authoritative record of what was decided — treat it as higher-priority than the compacted summary.

---

## Setup — extract theme + catalog layouts

At session start, complete these steps in order. **Do not run any commands or generate any mockups until Step 0 is complete.**

### Step -1 — Check for existing session state

Before Step 0, check the session folder for `_session/DECISIONS.md`. If it exists:
1. Read it in full.
2. State which slides have confirmed picks, which colors are approved, and which constraints are in effect.
3. Do not re-ask any question already answered in that file.
4. Proceed directly to whatever the next open action is.

If no `DECISIONS.md` exists, proceed to Step 0.

### Step 0 — Confirm the client template

**FIRST: read YAML front-matter from the brief.** If you were invoked with a brief path argument, open the brief file and parse the YAML block between the leading `---` fences. The front-matter (written by storyline-helper) includes `client_template:` and `deck_type:`. If `client_template:` is present and the file exists, USE THAT PATH — do not re-ask the user. If `client_template:` is missing or the path doesn't exist, ask the user to fix the brief or pass a path explicitly.

Example front-matter:
```yaml
---
client_template: C:\Users\...\FedEx\_templates\Template2.pptx
deck_type: Recommendation / Point of View
---
```

**Then check the project folder for a pre-extracted `template.json`.**

Each client's Claude Project folder (`C:\Users\...\OneDrive - Accenture\Claude Projects\<Client>\`) should contain a `template.json` (or `<name>-template.json` if the project has multiple templates). This file is generated once by `setup_template.py` and reused across all sessions.

1. Ask the user which template PPTX to use ONLY IF the brief front-matter does not specify one (or confirm the one they mention).
2. Derive the JSON name from the PPTX filename — e.g. `fedex-template.pptx` → look for `fedex-template.json` in the same folder as the PPTX, or in the Claude Project folder root.
3. If the JSON exists — read it directly. It contains colors, fonts, layouts, and all zones needed for Phase A. **Skip the `--print-theme` and `--catalog-layouts` steps below.**
4. If the JSON does not exist — this is a new template. Generate it once:

```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\setup_template.py" `
    "<path-to-template.pptx>" "<client-name>" `
    --output "<project-folder-path>"
```

This writes `template.json` and `template.md` into the project folder for future sessions. Confirm the file was created before proceeding.

Once you have `template.json`, state the resolved template name before proceeding:
```
Template confirmed: <client-name> (from template.json — Graphik-Semibold / #A100FF)
```

### A. Get colors and fonts from the client template

**If `template.json` exists in the project folder, read it** — it already contains the full theme (colors, fonts, layout coordinates). No need to run `--print-theme`.

**If `template.json` is absent** (first session, template not yet extracted): check `_session/theme.json` as a session-level fallback, then generate it:

```powershell
py -3 skills/slide-builder/scripts/build_slide.py --print-theme <client-template.pptx> | Out-File -FilePath "_session/theme.json" -Encoding utf8
```

Then read `_session/theme.json`. It contains:
```json
{
  "colors": {
    "dk1": "333333", "lt1": "FFFFFF", "dk2": "4D148C", "lt2": "FF6600",
    "accent1": "7D22C3", "accent2": "A63685", "accent3": "C74755",
    "accent4": "8E8E8E", "accent5": "E3E3E3", "accent6": "F2F2F2",
    "hlink": "333333", "folHlink": "4D148C"
  },
  "fonts": {
    "major": "FedEx Sans Bold",
    "minor": "FedEx Sans Regular"
  }
}
```

Use these values in the mockup CSS:
- Mockup primary color → use the slot that holds the brand color (FedEx puts purple in `dk2`, not `accent1`)
- Mockup accent color → second brand color (FedEx puts orange in `lt2`)
- Mockup body font-family → minor font: `font-family: "FedEx Sans Regular", -apple-system, sans-serif;`
- Mockup heading font-family → major font: `font-family: "FedEx Sans Bold", -apple-system, sans-serif;`

The fallback stack matters. If the user's machine lacks the corporate font, the HTML preview falls back to system. **The PPTX output uses the corporate font regardless** because the builder stamps it explicitly on every run.

### B. (Optional) Catalog the template's layouts

**Check for a cached file first.** If `_session/layouts.json` already exists, read it directly — do not re-run the command. Delete it first if you switched templates.

```powershell
py -3 skills/slide-builder/scripts/build_slide.py --catalog-layouts <client-template.pptx> | Out-File -FilePath "_session/layouts.json" -Encoding utf8
```

Returns a JSON array of every master/layout in the template with placeholder positions:
```json
[
  {
    "master_index": 6, "layout_index": 17,
    "name": "Title & 3 Stats",
    "n_placeholders": 11,
    "placeholders": [
      {"idx": 0, "type": "TITLE (1)", "name": "Title",
       "x_px": 60, "y_px": 60, "w_px": 964, "h_px": 63},
      {"idx": 17, "type": "BODY (2)", "name": "Statistic Placeholder 1",
       "x_px": 60, "y_px": 293, "w_px": 368, "h_px": 122}
    ],
    "background": "light"
  }
]
```

Run with `--filter "stats"` to narrow to layout names containing a keyword.

**Layout-aware threshold:** if `--catalog-layouts` returns 20 or more named layouts, prefer layout-aware mockups for any slide whose story fits an available layout — reusing the template's own placeholders gives better brand fidelity automatically. If the template has fewer than 20 layouts, default to blank mode and only use layout-aware when a named layout is an obvious match.

**After running `--catalog-layouts`, identify and record the default content layout** — the layout that has a `TITLE (1)` placeholder at `y ≈ 40px`, full width, and a light background. This is typically named "Title Only White," "Use as default," or similar. Record its `master_index` and `layout_index`. Use these as `data-layout-master` and `data-layout-index` on every content slide div in Phase A mockups. Without this wiring, all titles are built as floating overlay shapes that cannot follow layout changes in PowerPoint.

---

## Pre-build HTML audit — mandatory before first build_slide.py run (FALLBACK path only)

> **Legacy fallback (pattern library) only — HTML-fallback slides.** Skeleton-matched slides never produce `mockups.html` and never run `build_slide.py` — they apply patches directly to PPTX skeletons. Skip this section entirely for those slides. For client-facing decks use the Slide Lab build flow instead (see top of file).

Before running `build_slide.py` for the first time in a session on the HTML-fallback path, scan `_session/mockups.html` for all known unsupported CSS properties. Fix every violation in a single pass. Then build. Never build first and discover constraint violations from broken output.

**Scan for and fix:**

| Pattern | Problem | Fix |
|---------|---------|-----|
| `inset:0` or `inset:Npx` | Not parsed — background shape gets zero dimensions | Replace with `top:0; left:0; right:0; bottom:0` (or explicit values) |
| `background: linear-gradient(...)` or `background-image: linear-gradient(...)` | Gradient not rendered — becomes transparent fill | Replace with the first solid color stop from the gradient |
| `display: grid` with child elements | Grid children are skipped by DOM walker | Convert to `position:absolute` children with explicit coordinates |
| `display: flex` with children that have `flex:1` or no explicit size | Flex children have zero computed size | Give each child explicit `width` and `height` |
| `transform: translate...` or `transform: rotate...` | CSS transforms ignored | Use explicit `top`/`left` coordinates; rotation requires python-pptx `shape.rotation` |
| `border-radius: 50%` | Renders as rectangle | Replace with SVG `<circle>` element |
| `position:absolute` with `left` but no `right` or `width` | Shape too narrow, layout placeholder bleeds through | Add explicit `width` or `right` value |

**Process:**
1. Read mockups.html in full.
2. List every violation found (slide number, element, property).
3. Fix all violations in one Edit pass.
4. Confirm "Pre-build audit complete — N violations fixed" before running build_slide.py.

If the build script's `_pre_build_checks()` also fires warnings, treat them as missed audit items — fix before proceeding, not after.

---

## Phase B build routing — internal, never shown to user

> **Legacy fallback (pattern library) only.** Phase B routing (Playwright vs python-pptx direct) governs the HTML-fallback build path. The Slide Lab build flow bypasses Phase B entirely — each agent produces a standalone python-pptx script per option. For client-facing decks use the Slide Lab build flow instead (see top of file).

After the user picks one option per slide, Phase B selects the build engine for each slide. This decision is made silently — the user is never asked about it and never sees the routing logic.

### Use build_slide.py (Playwright) when:
- The slide is freeform or visual — charts, diagrams, visual models, hero numbers, split layouts
- Content doesn't map to a predictable grid of text and bullets

### Use python-pptx directly when:
- The slide is a **structured layout** — labeled rows, comparison tables, scope panels, scored matrices, org charts, swimlane timelines
- Content is primarily **text and bullets** in a predictable grid
- Bullet points must appear in the final PPTX (the HTML builder cannot reliably produce native bullets)

**Rule of thumb:** if you can describe the slide as "rows × columns with text in each cell," use python-pptx. The Playwright path introduces known conversion problems for grid layouts:

| Problem | Root cause | Impact |
|---|---|---|
| Font sizes wrong | px→pt conversion: 16px = 12pt, not 16pt | Undersized text |
| Bullet dots missing | CSS `::before` not in DOM | Bullets silently disappear |
| Text boxes overlap | Sibling `<span>` inside `<li>` become separate boxes | Slide unreadable |
| Label/row misalignment | Flexbox columns size rows independently | Labels don't align |

For python-pptx builds: read the approved HTML mockup as the layout spec and use `reference/direct-pptx-patterns.md` for validated build patterns.

### CSS Grid complex layouts (roadmaps, swim lanes, org charts)

Slides built with the CSS Grid patterns from `reference/page-types.md` (Roadmap & Timeline, Swim Lane, Org Chart) use the Playwright path — the grid layout is captured via the DOM walker's bounding boxes. Apply these additional rules:

**Two-pass rendering:**
1. First pass: walk all grid item divs and capture computed bounding boxes (left, top, width, height in px → convert to pt)
2. Second pass: draw python-pptx shapes using the captured bboxes

**Connector lines in org charts:** `<div style="width:2px; height:Npx; background:#CCCCCC;">` renders as a thin filled rectangle in PPTX (not a line shape — line shapes require explicit start/end coordinates that Phase B cannot infer). Use `add_shape(MSO_SHAPE_TYPE.RECTANGLE, ...)` with width = 1.5pt and the appropriate height.

**Activity bars in roadmaps and swim lanes:** Grid items with a background color that span multiple columns render as filled rectangles. Capture the merged bounding box (grid-column span) from the browser's computed layout — the DOM walker sees the final rendered bbox, not the grid declaration.

**Milestone markers:** `<div>` with `transform:rotate(45deg)` and a background color. Phase B renders as a diamond: draw a rectangle rotated 45° using `shape.rotation = 45` in python-pptx, sized to match the bounding box.

**Text inside grid cells:** Treat each grid cell's text content as a separate text frame overlaid on the cell's bounding box. Use the same font size and color as the mockup (convert px → pt).

**Limits enforced by Phase B:** If the DOM walker finds more than 5 workstream rows (roadmap) or more than 4 lanes (swim lane) or more than 3 org chart levels, insert a text box flagging the overflow: `"[Layout overflow — split this slide per page-types.md rules]"`.

---

## Adding Skeletons — user library growth

When the user finds a slide they like and wants to reuse its layout, promote it to the skeleton library with `promote_skeleton.py`. This is a first-class feature — not a dev tool.

### When to offer this

Offer after any successful build where the user says something like "I love this layout" or "we always use this structure." Say:
> "Want me to add this slide to your skeleton library? Next time you have a similar brief, I'll pick this layout automatically — one command."

### How to run

```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\promote_skeleton.py" `
  "<path-to-source.pptx>" `
  <slide_number> `
  "<skeleton-name>"
```

Example:
```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\promote_skeleton.py" `
  "<path-to-source-deck>.pptx" `
  3 `
  "fedex-scope-panel"
```

Output: `slide-builder/skeletons/fedex-scope-panel/fedex-scope-panel.pptx` + `skeleton.yaml`.

### After promoting

1. Open `skeleton.yaml` and fill in `page_types` and `best_for` — these drive matching.
2. Rename any auto-generated token keys that need clearer names (e.g. `COL_A_ITEM_3` → `RECOMMENDATION_TEXT`). Update both the YAML and the PPTX text.
3. Confirm by running one token fill against the skeleton with a sample brief.

---

## Template Fill Mode

Triggered when the user has an existing slide template and wants to populate it with new data — without redesigning the layout. This is one-option mode (no Phase A variants) and uses layout-aware Phase B exclusively.

### When to use
- User says "fill in [template name]" or "use this existing slide" and provides content
- PMO slides routed from storyline-helper (status dashboard, risk register, decision log)
- Any recurring report where the layout is locked and only the data changes

### Protocol (4 steps)

**Step 1 — Identify the template.**
Ask the user for the path to the existing PPTX template. Run `--catalog-layouts` if not already cached to identify the named layout that matches the slide the user wants to fill.

**Step 2 — Map content to placeholders.**
Ask the user to provide the content as a table, bullet list, or CSV. Map each provided field to a named placeholder in the layout using the placeholder name keywords from `--catalog-layouts` output (title → title placeholder, body/content → body placeholder, status fields → named data placeholders).

If content is provided but does not map to any named placeholder in the layout, add it as a freeform overlay shape and flag it to the user: "I could not find a placeholder for [field] — I've added it as a freeform shape. Let me know if you want it repositioned."

**Step 3 — Generate a single-option Phase A mockup.**
Build one HTML mockup option only (no A/B/C variants). The mockup must mirror the template's structure — no creative variation. Use `data-layout-master` and `data-layout-index` attributes on the slide root div, and `data-placeholder` on each content element.

**Step 4 — Phase B layout-aware build.**
Build using layout-aware mode exclusively. No freeform overlay shapes. The output PPTX should match the template's visual design with only the content changed.

### PMO placeholder mapping

For common PMO layouts, map user-provided data to these placeholder keywords:

**Status Dashboard:**
| Field | Placeholder keyword | Content type | Max chars | Format rule |
|-------|--------------------|----|----|----|
| Overall status | `status` | RAG text (Red/Amber/Green) | 10 | Use exact words: Red, Amber, Green |
| Project owner | `owner` | Person name | 40 | First name + Last name |
| Due date | `due_date` | Date | 15 | DD Mon YYYY |
| RAG color indicator | `rag_color` | Color label | 10 | Red / Amber / Green |
| Commentary | `comments` | Free text | 200 | No bullet formatting |

**Risk Register:**
| Field | Placeholder keyword | Content type | Max chars | Format rule |
|-------|--------------------|----|----|----|
| Risk ID | `risk_id` | Alphanumeric | 10 | R-001 format |
| Description | `description` | Free text | 150 | One sentence per risk |
| Likelihood | `likelihood` | H/M/L | 6 | High / Medium / Low |
| Impact | `impact` | H/M/L | 6 | High / Medium / Low |
| Mitigation | `mitigation` | Free text | 150 | Action-oriented |
| Risk owner | `owner` | Person name | 40 | First name + Last name |

**Decision Log:**
| Field | Placeholder keyword | Content type | Max chars | Format rule |
|-------|--------------------|----|----|----|
| Decision | `decision` | Free text | 150 | Verb-first: "Approved X", "Rejected Y" |
| Rationale | `rationale` | Free text | 200 | One sentence |
| Decision maker | `made_by` | Person name or role | 60 | Role or name |
| Date | `date` | Date | 15 | DD Mon YYYY |
| Impact | `impact` | Free text | 150 | What changes as a result |

---

## Chart generation — run before Phase A FALLBACK (HTML-mockup slides only)

> **For skeleton-matched slides, do NOT pre-generate chart PNGs here.** Skeletons with charts handle their own chart generation through the structural patches in Step 3 of the v2 Skeleton Pipeline. This section applies only to slides that fell through to the HTML mockup fallback path.

For any HTML-fallback slide where the narrative brief has `Chart type:` set to something other than `none`, generate the chart PNG before writing the HTML mockup. This gives the fallback authoring step a real image to reference for layout and sizing decisions instead of guessing at chart proportions.

### Step-by-step

**1. Read chart fields from the brief for each slide.**

For each slide, check:
- `Chart type:` — the chart type string (bar, line, waterfall, etc.), or `none`
- `Chart data:` — inline table, a file path, or "TBD — placeholder"

**2. For each slide with a chart and data available, run:**

```powershell
py -3 skills/slide-builder/scripts/generate_chart.py `
  --type <chart-type> `
  --data-file "_reference/<datafile>" `
  --theme "_session/theme.json" `
  --output "_session/chart-slide-<N>.png" `
  --title "<governing thought or chart title>" `
  --ylabel "<unit label if numeric>"
```

Or with inline data:

```powershell
py -3 skills/slide-builder/scripts/generate_chart.py `
  --type bar `
  --data "Quarter,Revenue\nQ1,1200\nQ2,1450\nQ3,1100\nQ4,1600" `
  --theme "_session/theme.json" `
  --output "_session/chart-slide-2.png" `
  --title "Revenue by Quarter" --ylabel "Revenue ($K)"
```

**3. For slides with "TBD — placeholder," skip generation.** The Phase A mockup uses an amber placeholder div (same treatment as any missing-data element). Label it: `[CHART PLACEHOLDER: <type> — data TBD]`.

**4. After generation, state what was produced before proceeding:**

```
CHART GENERATION
================
Slide 2: bar chart → _session/chart-slide-2.png ✓
Slide 4: waterfall → _session/chart-slide-4.png ✓
Slide 5: line chart → TBD placeholder (data not provided)
================
```

### Using the PNG in Phase A mockups

After `generate_chart.py` saves the PNG, the chart element in the mockup needs **three things** — the image, the path rule, and the data attribute. All three are required:

**1. The outer div** — `data-chart="true"` triggers the Phase B screenshot; `data-chart-data` carries the source data for the xlsx companion. **If `data-chart-data` is missing, the xlsx companion is silently skipped — no error, no warning.**

**2. The image** — relative filename only (never base64) inside `data-chart` containers. Playwright needs a real file path to resolve the bounding box.

**3. The data JSON** — copied from the brief's `Chart data:` field, formatted as:
```json
{
  "title": "Sheet name in xlsx",
  "categories": ["Q1", "Q2", "Q3", "Q4"],
  "series": [{"name": "Revenue ($M)", "values": [1.2, 1.45, 1.1, 1.6]}],
  "notes": "Optional context or caveats"
}
```

Complete chart element structure:
```html
<div data-chart="true"
     data-chart-data='{"title":"Revenue by Quarter","categories":["Q1","Q2","Q3","Q4"],"series":[{"name":"Revenue ($M)","values":[1.2,1.45,1.1,1.6]}]}'>
  <img src="chart-slide-2.png"
       style="width: 560px; height: 320px; object-fit: contain; display: block;">
</div>
```

For base64 embedding of the preview (outside `data-chart` — e.g. a standalone image that is not being screenshotted by Phase B):

```python
import base64, pathlib

png_path = pathlib.Path(session_folder) / "_session" / f"chart-slide-{n}.png"
uri = "data:image/png;base64," + base64.b64encode(png_path.read_bytes()).decode()
img_tag = f'<img src="{uri}" style="width: 560px; height: 320px; object-fit: contain; display: block;">'
```

**Path rules — two cases, different requirements:**

| Context | Required src format | Reason |
|---|---|---|
| `<img>` outside a `data-chart` container | `data:image/png;base64,...` | Renders in any preview context; no path dependency |
| `<img>` inside a `data-chart="true"` container | Relative filename only: `chart-slide-N.png` | Base64 collapses the flex container to zero height in Playwright — blank screenshot, blank PPTX |

For `data-chart` containers, the HTML preview will show a broken image icon — this is expected and acceptable. The PPTX build reads the file from disk and produces the correct output. Never use `src="_session/chart-slide-N.png"` — the `_session/` prefix makes the path resolve to `_session/_session/...` which does not exist.

Use `object-fit: contain` so the chart is never cropped. Phase B picks this up as an image element and embeds it at the matched dimensions.

For placeholder slides, use:

```html
<div style="width: 560px; height: 320px; background: #FFF3CD; border: 2px dashed #F0A500;
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; color: #856404; font-family: Arial, sans-serif;">
  CHART PLACEHOLDER: waterfall — data TBD
</div>
```

### Consultant note — think-cell handoff (mandatory)

**This note is required in the Phase B delivery message for any deck that contains matplotlib chart slides. Do not omit it.**

> **Chart slides: replace before delivery.** Slides [N, N] contain DRAFT matplotlib charts. Replace each with a think-cell chart using the same data before sending to the client. The chart type and data are in the narrative brief.

Include the specific slide numbers. If every slide has a chart, list them all. If no slides have matplotlib charts, omit this block entirely.

---

## Phase B — python-pptx build path (structured slides)

After the user picks an option in Phase A, use this path for any slide the Phase B routing identifies as structured (tables, bullet grids, labeled rows, comparison panels). The approved HTML mockup is the layout spec — build what the user picked.

### Build with python-pptx

Write a self-contained `build_<name>.py` script in the session folder. Rules:

- **Read `reference/direct-pptx-patterns.md` before writing any code.** This file contains validated patterns for clone-and-replace, text updates, and shape finding — all failure modes are silent without these patterns.
- **Native text frames and bullet paragraphs** — use `tf.text_frame.paragraphs` and `p.add_run()`. Never simulate bullets with dash characters or CSS `::before` content.
- **Theme colors** — use `prs.core_properties` or set `RGBColor` from the `--print-theme` output. Prefer `MSO_THEME_COLOR` constants (`ACCENT_1`, `DARK_2`, etc.) over hardcoded hex wherever python-pptx exposes them.
- **Font sizes** — set in Pt units directly: `run.font.size = Pt(12)`. Map from the canonical scale: title=21pt, sub-heading=16.5pt, body=12pt, detail/caption=10.5pt.
- **Slide layout** — pick a named layout from `--catalog-layouts` output if one matches. If none match, use the cleanest blank.
- **Output path** — write to `<session_folder>/<deck_name>.pptx`. Print the full absolute Windows path when done.

Run with:
```bash
py -3 <session_folder>/build_<name>.py
```

### Step 3 — Post-build reviewer pass

Run the same post-build reviewer pass as the HTML mockup path (see "Post-Build Reviewer Pass" section). The schema check, build log review, and per-slide visual checklist all apply equally to python-pptx builds.

Deliver with the same full absolute Windows path output format.

---

## Narrative Gate

**Route before reading any further:**

| Situation | Action |
|---|---|
| Storyline-helper ran this session and its five-part gate passed | **Skip this gate entirely → go directly to Content Sufficiency Gate** |
| Slide-builder invoked directly (no storyline-helper this session) | **Run this gate** |

If you came from storyline-helper, you do not need to re-verify governing thoughts — the five-part gate already did that. Go to Content Sufficiency Gate now.

**Purpose (direct-invocation path only):** This gate catches weak briefs early — a slide built from a vague or contradictory brief will require multiple rebuild rounds regardless of how good the design is.

The gate asks two questions per slide. Both must be answerable with a single clear sentence. If either answer is vague, compound, or uncertain, the brief needs to be sharpened before building starts.

### The two gate questions

**Q1 — Governing thought:** *"What is the single thing this slide wants the audience to know, decide, or do?"*

A passing answer is one specific, assertive statement:
> "The FY26 forecast beats commitment by $0.8M even after the correction."
> "Three talent exit scenarios each carry different cost implications — the gap is up to $1.2M/week."
> "Scope is split into four categories; only two are in direct GCS control."

A failing answer is vague, multi-part, or process-oriented:
> "Show the financial results." ← not a governing thought, it's a description of content
> "Overview of the scenarios and timelines and what we think about them." ← compound, no point of view
> "Walk through the data." ← no assertion, just a motion

**Q2 — Skeptic test:** *"If a skeptical executive read only the slide title, would they immediately understand what you're arguing — not just what the slide is about?"*

A passing title makes the argument: *"FY26 Forecast Exceeds Commitment by $0.8M"*
A failing title describes the content: *"FY26 Financial Summary"*

### Gate output format — required before any build path starts (Pattern Library, Skeleton, OR HTML authoring)

Write this block as a comment before checking the Pattern Library, running skeleton matching, or generating any from-scratch mockup HTML. The gate applies to all three tiers. If the gate block is missing, the gate did not run.

```
NARRATIVE GATE — [Deck name]
=============================
Slide 1 "[working title]"
  Governing thought: "The FY26 forecast beats commitment by $0.8M even after the $2.3M correction."
  Skeptic test: PASS — title asserts the result, not just the topic
  GATE: PASS

Slide 2 "[working title]"
  Governing thought: UNCLEAR — "Show the three exit scenarios" describes content, not an argument.
  → Sharpened to: "Exit timing drives up to $1.2M/week in cost — scenario choice is a financial decision."
  Skeptic test: PASS after sharpening
  GATE: PASS (after revision)

NARRATIVE GATE RESULT: ALL SLIDES PASS — proceeding to pipeline decision
=============================
```

### When a slide fails the narrative gate

Do not guess what the user intends. Ask one targeted question:

> "Before I design slide 2, I need the governing thought — what's the single point you want the audience to leave with? For example: 'Scenario 2 costs $X more than the base case' or 'All three scenarios require a decision by April 30.' One sentence."

Once the user answers, re-run the gate on that slide and proceed.

**Do not start Phase A while any slide is failing the narrative gate.** A weak governing thought produces a weak slide regardless of how good the design is. The gate is protecting the user's time, not adding friction.

---

## Content Sufficiency Gate — required after narrative gate, before any build path

**Purpose:** The narrative gate checks that the governing thought is clear. The content sufficiency gate checks that there is enough raw material to actually build a slide that supports that thought. A clear argument with thin evidence produces a visually well-designed but substantively empty slide — which goes to a client and reflects poorly.

This gate runs per slide, immediately after the narrative gate passes. It evaluates the content provided against the minimum threshold for the slide's page type.

### Minimum content thresholds by page type

**Financial / Business case**
- Minimum: at least 2 numbers (e.g. baseline + actual, or committed + forecast), a timeframe, and a label for each number
- Quality: breakdown by category or time period, variance/delta, comparison to target
- Common gap: one total number provided ("we saved $5M") with no baseline, no period, no breakdown

**Chart / Data visualization**
- Minimum: at least 2 data points, axis labels, series name, and category or time labels
- Quality: 4+ data points for a trend line, a comparison series, an annotated "the point" data point
- Common gap: "show our savings trend" with a single quarterly total

**Comparison**
- Minimum: at least 2 things being compared, at least 2 evaluation criteria, and some evidence per cell
- Quality: a recommended option, a rationale for each rating
- Common gap: options named but no criteria defined, or criteria listed but no per-option evidence

**Roadmap / Timeline**
- Minimum: at least 2 phases or milestones with names and dates or durations
- Quality: gate criteria between phases, owner per phase, current status marker
- Common gap: phase names provided but no dates, or dates but no phase content

**Insight / Finding**
- Minimum: the finding stated as an assertion + at least 1 supporting data point (a number, a quote, or a trend reference)
- Quality: a "so what" implication, a source reference, a comparison that makes the finding concrete
- Common gap: assertion provided ("adoption is low") but no quantification or evidence

**Scope**
- Minimum: at least 2 categories with at least 1 item per category
- Quality: items labeled as in/out/partial, owner per category, headcount or dollar value per item
- Common gap: category names only, no items; or items listed with no category structure

**Three-column / parallel structure**
- Minimum: all N columns have a header and at least 2 lines of body content
- Quality: a parallel structure across columns (same type of content in the same position in each)
- Common gap: one column is well-developed, others are placeholders or stubs

**Conceptual / Bucket / Pillar slide** *(framework, workstream map, capability grouping, strategic pillars)*
- These slides have a **two-level completeness problem** — the structure (bucket labels) and the content (what's inside each bucket) are independently incomplete.
- **Level 1 — Structure check:** Are all bucket/pillar names defined? If any bucket label is missing or TBD, that bucket gets a full amber structural placeholder (the visual signal that even the category is unknown — not just missing content inside a known category).
- **Level 2 — Content check:** For each named bucket, is there enough to fill it?
- Minimum: all bucket names defined + at least 2 items per bucket (initiative name + 1-line description each) + owner per bucket + a governing thought explaining why THIS grouping
- Quality: status per bucket, a metric or savings target per bucket, dependencies or enablers called out, a cross-bucket relationship or sequencing note
- Common gaps:
  - Bucket names provided but no items inside — "we have four workstreams: Vendor, Headcount, Automation, and Data" with nothing else
  - Items listed without the bucket structure — a flat list that should be organized into groups
  - One bucket well-developed, others are stubs — the "first pillar halo" problem
  - Governing thought missing — the slide just shows the structure with no assertion about why it's organized this way or what it implies

**Coaching questions specific to bucket slides** (use these in the active coaching loop):
1. "What are all the bucket/pillar names? I need all of them before I can build the structure."
2. "For each bucket: who owns it, and what are the 2–3 key initiatives or items inside it?"
3. "Is there a metric or target for each bucket — a savings number, a headcount figure, a milestone date?"
4. "What's the current status of each bucket — on track, at risk, or not yet started?"
5. "What is the governing thought? In one sentence: why are these the right buckets, and what does this grouping tell the audience?"
6. "Are any buckets related or sequential — does Bucket A need to complete before Bucket B starts, or are they parallel?"

**Placeholder treatment for bucket slides** *(different from content placeholders)*:
- Named bucket with missing content → purple header (structure exists) + amber inline placeholders inside
- Unnamed bucket → full amber card with amber header (structure itself is missing; the whole card signals undefined, not just its contents)
- Missing governing thought → amber takeaway strip spanning full slide width
- See `placeholder-examples.html` Slide 4 for the visual reference.

### How to handle insufficient content — three paths

#### Path 1 — Active coaching loop (preferred when the gap is specific and fillable)

When content is thin, do not ask a single question and accept whatever comes back. Enter an active coaching loop: explain what makes a quality slide of this type, show what "good" looks like with a concrete example, ask specific questions, evaluate the response, and push again if the answer is still thin.

**The coaching loop has four steps:**

**Step 1 — Show what quality looks like for this slide type**

Before asking anything, briefly describe what a strong version of this slide would contain and why each piece matters. This gives the user a quality benchmark so they know what they're aiming for — not just what you're asking for.

Example (financial business case slide):
> "A strong financial business case slide typically has four components working together:
> 1. **The commitment/baseline** — what was the starting target or what was promised ($X committed)
> 2. **The actual/forecast** — what's actually happening ($Y achieved or forecast)
> 3. **The delta and why it matters** — the gap between them, with a one-line explanation of what drove it
> 4. **A breakdown** — at least one dimension that shows where the number comes from (by quarter, by workstream, by geography)
>
> Without the baseline, the actual number floats without context — the audience can't evaluate whether $11.7M is good or bad. Without the breakdown, the argument is a single number with no supporting structure.
>
> What you've given me: the forecast ($11.7M). What would make this a strong slide:"

**Step 2 — Ask specific, structured questions with format examples**

Ask for the missing pieces explicitly. Show the format you need, not just the label. Give a real example so the user understands what level of detail is useful.

> "Can you fill in any of these?
>
> - **Commitment/target:** What was the original FY26 commitment? *(e.g., $10.9M — the number you said you'd hit)*
> - **Timeframe:** Is $11.7M for full FY26, or a specific period? *(e.g., FY26 full year, Jan–Dec)*
> - **Breakdown:** Where does the $11.7M come from? *(e.g., Q1: $2.4M, Q2: $2.8M, Q3: $3.1M, Q4: $3.4M — or by workstream: Network $6M, IT $3M, Ops $2.7M)*
> - **The story behind the number:** Was there anything unusual? *(e.g., a $2.3M one-time correction that makes the number look different than it is)*
>
> Even partial answers help. If you only have some of these, share what you have and I'll flag the gaps as placeholders."

**Step 3 — Evaluate the response before proceeding**

When the user responds, explicitly assess what was provided before deciding to proceed. Do not silently accept a thin response and proceed.

If the response adds meaningful data → acknowledge it and proceed:
> "Good — with the commitment ($10.9M), forecast ($11.7M), and the quarterly breakdown, I have enough to build a substantive slide. The $0.8M delta and the $2.3M correction story will anchor the takeaway."

If the response is still thin (adds one vague sentence, restates what was already given, or adds only one of several requested items) → push again, more specifically:
> "That helps with the baseline, but I still don't have a breakdown — just a total. Without at least one dimension of detail (quarter, workstream, region), the chart will be a single bar, which doesn't tell a story. Do you have any split at all? Even rough estimates are better than a single number."

**Step 4 — Exit the loop explicitly**

The coaching loop ends in one of two ways only:
- The user provides content that meets the sufficiency threshold → proceed to design
- The user explicitly says they don't have more data → switch to Path 2 (placeholders)

Do not exit the loop because the conversation feels long or the user's response seems impatient. If content is genuinely insufficient, a second or third round of coaching is protecting the user from a weak slide — not adding friction. The loop may take 2–3 exchanges. That is expected and correct.

**What "thin" looks like vs. "sufficient" — examples:**

| User provides | Assessment | Action |
|---|---|---|
| "We saved about $5M this year" | Thin — no baseline, no timeframe, no breakdown | Start coaching loop |
| "We saved $5M vs $4M target, FY26" | Getting there — has baseline + actual + period, still no breakdown | Push once for breakdown |
| "We saved $5M vs $4M target, FY26, split: Q1 $0.8M Q2 $1.2M Q3 $1.5M Q4 $1.5M" | Sufficient — 4 data points, baseline, actual, period | Proceed |
| "I only have the total, no breakdown" | Explicit opt-out | Switch to Path 2 (placeholders) |
| "It's complicated, just build something" | Impatient but not an opt-out | One more push: "I understand — give me just the commitment number and the timeframe and I can build the rest with placeholders" |

Do not ask for everything at once in Step 2. If the sufficiency gap has 4 missing pieces, ask for the 2 that matter most for the governing thought — the ones that are structural to the argument, not decorative. Add the others as optional in the same message.

**Second push — offer concrete format options, not just a repeat ask**

If the first round of questions returns a thin answer and a second push is needed, do not ask the same question again in the same format. Instead, offer 2–3 concrete pre-formatted options so the user only has to pick one — not figure out what format to answer in:

> "I still need a breakdown to give this slide structure. Here are three ways you could give it to me — pick whichever is closest to what you have:
>
> **Option A — By quarter:**
> *(e.g., Q1: $X · Q2: $X · Q3: $X · Q4: $X)*
>
> **Option B — By workstream or category:**
> *(e.g., Vendor contracts: $X · Headcount exits: $X · Process savings: $X)*
>
> **Option C — By site or geography:**
> *(e.g., Site A: $X · Site B: $X · Site C: $X)*
>
> Even rough estimates work. If none of these apply to your situation, describe how you'd naturally split the number and I'll work from that."

This lowers the barrier for users who know the data but don't know how to express it. One of the three options will usually be close enough.

**Step 5 — Confirm before building**

Once content is sufficient, read it back to the user before proceeding to design. This serves two purposes: it confirms there are no misunderstandings, and it gives the user a chance to catch errors before they're baked into the slide.

> "Here's what I'm building with — confirm this looks right before I start:
>
> - **Governing thought:** 'MSP transition savings are tracking $3M ahead of FY26 commitment'
> - **Commitment:** $18M · **Forecast:** $21M · **Delta:** +$3M (+16.7%)
> - **Breakdown:** Vendor contracts $9M · Headcount exits $8M · Process optimization $4M
> - **Slide type:** Financial business case with stacked bar chart + hero delta callout
>
> Any corrections before I design?"

Do not skip the confirmation step when the data was gathered through multiple exchanges. If the data came in one clean initial response, the confirmation can be shorter — but it should still happen.

**Data integrity check — flag before building, not after**

While reviewing the confirmed content, check for common data issues:

| Issue | Example | How to flag |
|---|---|---|
| Parts don't sum to total | Breakdown sums to $21.1M but total stated as $21M | "The breakdown ($9M + $8M + $4M) sums to $21M exactly — if these are rough estimates, I'd recommend labeling the breakdown as 'approximate' so it doesn't imply false precision." |
| Single period presented as trend | One quarter's number used to imply a full-year story | "The $5M figure is Q1 only — should I label it as Q1 or is there a full-year number?" |
| Delta math is off | Commitment $18M, actual $21M, but user says "+$2M" | "Quick check: $21M vs $18M is a +$3M delta, not +$2M. Which is correct?" |
| Baseline is missing but implied | "We're 20% ahead of plan" — no absolute numbers | "I need the absolute numbers to build the chart — 20% of what baseline? Even an approximate baseline helps." |

Flag these before building. A slide built on a math error has to be rebuilt. A 10-second flag prevents a full rebuild round.

#### Path 2 — Build with placeholders (when user can't provide more)

**Offer this path proactively — don't wait for the user to ask.**

After 2 rounds of coaching without sufficient content, or when the user signals they don't have the data, explicitly offer the placeholder path before the conversation stalls:

> "It sounds like you don't have all the numbers yet — that's fine. Here's what I can do: I'll build the full slide layout with clearly labeled placeholder blocks where the real data goes. You'll get a slide that looks exactly like the finished version, with every section in place. The placeholders tell you precisely what to fill in and why it matters. When you have the numbers, you open the slide, find the bracket labels, and drop in the real content — no redesign needed.
>
> Should I go ahead with a placeholder build?"

Once the user agrees, proceed immediately. Do not ask more questions.

**Before building, show the user what the placeholder slide will contain:**

Give a brief preview so the user knows what they're getting and can confirm the structure is right before the build runs:

> "Here's what the placeholder slide will look like:
>
> - **Header:** 'MSP Transition Cost Savings — FY26' *(you can update the title)*
> - **Hero number:** `[Forecast: $XX.XM]` vs `[Commitment: $XX.XM]` → `[Delta: +/-$X.XM]`
> - **Chart:** 3-bar breakdown with `[Workstream 1: $X.XM]` · `[Workstream 2: $X.XM]` · `[Workstream 3: $X.XM]`
> - **Takeaway strip:** `[Fill in: one sentence on what the delta means for the business case]`
>
> Does this structure work, or do you want to adjust it before I build?"

This prevents rebuilding the layout itself once data is available.

**Placeholder rules — what makes a good placeholder:**

Placeholders must be specific enough that anyone opening the file — including someone who wasn't in this conversation — knows exactly what to fill in.

| Rule | Wrong | Right |
|---|---|---|
| Name the field | `[data here]` | `[FY26 Savings Commitment: $X.XM]` |
| Name the format | `[add number]` | `[Enter as $X.XM — e.g., $18.4M]` |
| Name the source | `[TBD]` | `[Source: FY26 savings tracker — ask finance lead]` |
| For bullet content | `[add bullets]` | `[3–4 bullets: one per workstream. Format: Workstream — $X.XM saved — key driver]` |
| For narrative text | `[text here]` | `[2–3 sentences: what drove the savings, what's at risk, what decision is needed]` |
| For charts | Gray bars with labels | Gray bars + `[Replace with actuals from savings model — Q1–Q4 by workstream]` annotation |

**Placeholder types — data vs. content:**

There are two kinds of placeholders and both need to be handled:

*Data placeholders* — a specific number, date, or fact the user will look up:
- `[FY26 Commitment: $X.XM — from signed business case]`
- `[Headcount exits completed: XX of XX planned — from HR tracker]`
- `[Q3 actuals: $X.XM — from finance close]`

*Content placeholders* — text the user needs to write, not just look up:
- `[Takeaway: one sentence on what this means for the program — e.g., 'Savings are ahead of plan but concentrated in vendor exits; headcount savings lag by $X.XM']`
- `[Bullet 1: key risk or assumption that drives this number]`
- `[Context box: 2 sentences on why savings accelerated in Q1-Q2]`

Content placeholders are harder to fill in than data placeholders — they require thought, not just a lookup. Flag these explicitly in the fill-in checklist.

**Placeholder inventory — deliver this alongside the PPTX:**

After building a placeholder slide, output a numbered checklist of every placeholder in the slide, grouped by type. This becomes the user's to-do list when they have the data.

```
PLACEHOLDER INVENTORY — MSP Savings Slide
==========================================
DATA TO LOOK UP:
  □ 1. FY26 savings commitment ($X.XM) — check signed business case or finance lead
  □ 2. FY26 forecast/actual ($X.XM) — check savings tracker
  □ 3. Workstream 1 name and amount — check program office breakdown
  □ 4. Workstream 2 name and amount — check program office breakdown
  □ 5. Workstream 3 name and amount — check program office breakdown
  □ 6. Chart data (Q1–Q4 actuals by workstream) — check finance close reports

CONTENT TO WRITE:
  □ 7. Slide title — confirm or update "MSP Transition Cost Savings — FY26"
  □ 8. Takeaway strip — one sentence: what does the delta mean? What should the audience do?
  □ 9. Context annotation — why did savings land where they did? Any unusual items?

OPTIONAL ENHANCEMENTS (if available):
  □ 10. Source line — where does this data come from? (e.g., "Source: FY26 Savings Tracker v3, Apr 2026")
  □ 11. Footnote — any caveats? (e.g., "Excludes one-time items")
==========================================
Total placeholders: 11 (6 data, 3 content, 2 optional)
Estimated time to complete: 20–30 min once data is gathered
```

The inventory makes the handoff clean. Someone else on the team can pick up the slide and know exactly what's missing without having to open the file and hunt for bracket labels.

#### Path 3 — Flag and proceed (when the gap is non-critical)

If the governing thought is supportable with the content available, but secondary detail is missing, flag it and proceed. Do not block the build for cosmetic gaps.

> "Building slide 3 with the data provided. Note: the chart only has 2 data points — consider adding Q3 and Q4 actuals when available to make the trend more convincing. I've left a note in the slide footer."

### Gate output format

```
CONTENT SUFFICIENCY GATE — [Deck name]
========================================
Slide 1 "[title]" — page type: financial/business case
  Provided: forecast $11.7M, commitment $10.9M, delta $0.8M
  Missing: no quarterly breakdown, no category split
  Assessment: SUFFICIENT for governing thought — delta is the argument, not the breakdown
  Action: proceed. Note flagged for user: consider adding breakdown when available.
  GATE: PASS

Slide 2 "[title]" — page type: chart/data visualization
  Provided: "savings have been growing" — no specific data points
  Missing: all quantitative data
  Assessment: INSUFFICIENT — cannot build a chart without data
  Action: PATH 1 — asking user for data before proceeding
  GATE: HOLD

Slide 3 "[title]" — page type: three-column parallel
  Provided: column headers only, no body content
  Missing: body content for all 3 columns
  Assessment: INSUFFICIENT — but user confirmed no data available
  Action: PATH 2 — building with placeholders
  GATE: PASS (placeholder build)
========================================
```

Slides on HOLD are not built until the user responds. Slides on placeholder build proceed immediately with bracket notation content.

---

## Phase A pre-check — mandatory before any HTML is written (FALLBACK path only)

> **Legacy fallback (pattern library) only.** This pre-check applies only to slides on the HTML-mockup fallback path. Skeleton-matched slides do not go through Phase A and do not need this check. The pre-check exists to prevent HTML-authoring failures — it has no role in skeleton matching, token fill, or patch application. For client-facing decks use the Slide Lab build flow instead (see top of file).

**Read both reference files before authoring a single line of fallback mockup HTML.** This is not a reminder — it is a hard gate. These files contain the rules that prevent the most common HTML-authoring failures: empty bottom thirds, buried takeaways, three options that look structurally identical, and slides built to fill space rather than make an argument.

**Step 1 — Read the files:**
```
reference/phase-a-rules.md          ← 4 hard rules + pre-show checklist
reference/visual-treatment-library.md ← composition recipes per layout family
```

**Step 2 — Output this block before writing any HTML.** If this block is absent, Phase A has not been properly started.

**The pre-check block must prove the files were read — not just assert it.** Each file section must quote a specific rule by name with its enforcement level. Writing `✓ read` without a quote is the failure mode that produced slide-within-slide outputs and bottom-third dead space in real sessions: the block existed but the content was not applied.

```
PHASE A PRE-CHECK — [deck name]
================================
✓ reference/phase-a-rules.md read
  Rule 1 (Canvas Fill): bottom 30% must be intentionally used — [quote the specific pass/fail condition that applies to this deck's content density]
  Rule 8 (Hero Element): blocking gate — hero must be 40–60% canvas height; if not, option must be regenerated
  Rule noted for this deck: [cite the specific rule most likely to be triggered by this deck's slide types]

✓ reference/visual-treatment-library.md read
  Layout families in scope: [list by name — e.g. "Three-column parallel (Variant A), Roadmap, Two-column finding"]
  Swim Lane / Flowchart: [YES — present in this deck, Phase B warning delivered to user | NO — not applicable]

✓ reference/known-issues-and-improvements.md read
  Active workarounds for this deck: [list any open issues relevant to slide types in this deck, or "none applicable"]

✓ Deck-level design notes (from brief):
  Visual rhythm: [copy exact text from brief, or "none specified"]
  Accent color discipline: [copy exact text from brief, or "none specified — defaulting to one accent element per slide"]
  BINDING: [YES — these constraints apply to every option below | NO — section was empty]

Planned structural approaches:
  Slide 1: A=[layout family + variant] · B=[layout family + variant] · C=[layout family + variant]
  Slide 2: A=[...] · B=[...] · C=[...]
  [one line per slide]
================================
```

**If BINDING is YES:** every option for every slide must satisfy the stated visual rhythm and accent color discipline. These are not suggestions — they came from the user's explicit direction in the storyline session. An option that violates them must be regenerated before being shown.

Naming the structural approach before writing HTML forces genuine design thinking. If you cannot write this block, you do not yet have three distinct options — go back and think about the story until you do.

**Two outputs are required — they go to different places and serve different consumers:**
- The `PHASE A PRE-CHECK` block (Step 2 above) goes in the **conversation** — it is for the user and the session log, confirming that rules were read and layout families were named before any HTML was written.
- The HTML gate comment below goes in **`mockups.html`** — it is for Phase B to scan as a structural gate. Phase B cannot accidentally skip it because the build refuses to start if the comment is absent.

Do not conflate them or write both to the same place.

**Machine-readable gate comment (required in `mockups.html`):** After the pre-check passes, write the following HTML comment into `mockups.html` immediately before the closing `</body>` tag:

```html
<!-- PHASE-A-PRECHECK: PASS | [date] | [N] slides checked -->
```

Phase B scans for this comment before starting the build. If it is absent, Phase B must refuse to build and output:

> "Phase A pre-check comment not found in mockups.html. Re-run the Phase A pre-check and confirm all [N] slides pass before proceeding."

This turns the pre-check from an instruction into a structural gate — Phase B cannot accidentally skip it.

---

## Feedback-driven rebuild protocol

When the user provides per-slide feedback and requests any edit — a single slide tweak, a selections rebuild, or a full Phase A re-run — the following rules apply without exception. Violating them has caused data loss and hours of rework in production sessions.

### Rule 1 — Backup before any destructive write (CRITICAL)

Before any Write or Edit call that modifies or replaces `mockups.html`:

1. Check if `_session/mockups.html` already exists.
2. If it does, copy it to `_session/_versions/mockups-v[N]-backup.html` where N is the next version number (check existing backups to determine N).
3. Announce the backup path to the user before starting the write:
   > *"Backing up current mockups.html → `_session/_versions/mockups-v2-backup.html` before making changes."*

This is a hard constraint. A 12-slide mockup file represents hours of Phase A work. Overwriting it with no recovery path is a critical failure mode — the user should never need to check their Downloads folder to restore work.

### Rule 2 — Scope discipline (CRITICAL)

When feedback covers specific slides, only those slides may change. Slides the user has explicitly approved ("slide 1 is fine," "the quote was entirely fine," "keep this one") must be carried forward **byte-for-byte unchanged**. The skill must not treat a rebuild as an opportunity to redesign, reformat, or rewrite content that was not flagged.

Before writing anything, output an explicit scope declaration:

```
REBUILD SCOPE:
  Changing: Slide 2 (layout redesign per feedback), Slide 5 (bottom zone fix)
  Carrying forward unchanged: Slides 1, 3, 4, 6, 7, 8, Appendix A, Appendix B
```

Wait for the user to confirm the scope before proceeding. If the user says "that's not right," adjust the scope — do not write anything until the scope is confirmed.

### Rule 3 — One change at a time (CRITICAL)

For feedback-driven edits, process slides one at a time:

1. State what will change on the next slide and how — before writing any HTML.
2. Write the change for that slide only.
3. Show the result (file path, brief description of what changed).
4. Wait for explicit user confirmation ("looks good," "approve," or specific further feedback).
5. Only move to the next slide after confirmation.

**Do not batch multiple slide changes into one Edit call**, even if it would be faster. Batching means that when something goes wrong, the user cannot identify which change caused the problem — rollback requires restoring the entire backup rather than undoing one slide. One change costs one extra message. A bad batch costs hours.

This protocol applies to: Phase A rebuilds, selections-only file edits, content tweaks, layout adjustments, and any edit that touches `mockups.html`.

---

## Phase A — Tier 3 HTML Authoring (only when no pattern AND no skeleton matches)

> **This section applies only to slides that fell through BOTH Tier 1 (Pattern Library) AND Tier 2 (Skeleton). Pattern-matched and skeleton-matched slides do not touch any of the rules below.** If you have not yet checked the pattern library, stop here and go back to **Step 4** of "What this skill does."


### File split threshold — decks over 8 slides

A single `mockups.html` file with more than 8 slides (~24 options) exceeds ~100KB and causes noticeable browser render lag at preview time. It also spans enough Edit calls to hit context window limits mid-session, which forces auto-compaction and degrades constraint adherence on later slides.

**Rule:** If the deck has more than 8 slides, split the mockup into two files:
- `_session/mockups-slides-1-8.html` — slides 1 through 8
- `_session/mockups-slides-9-end.html` — remaining slides

Announce both file paths at the start. The user can open each file independently. Build the second file only after the first is fully written and announced. The builder accepts mockup files by path — there is no requirement that all slides be in one file.

For decks over 8 slides, also consider breaking the session into two parts: Phase A for slides 1–8 in one session, Phase A for remaining slides in a second session, then Phase B in a third. This prevents context compaction from forcing a mid-session summary that degrades constraint adherence on later slides.

---

### Batch writing — required for all decks

**Never write all slides to mockups.html in a single response.** Writing more than ~3 slides at once risks hitting the model's output token ceiling (32K default), which aborts the write mid-file and produces a broken or empty mockup.

Instead, use a rolling batch workflow:

**Batch size:** 3 slides per batch (9 options). Adjust down to 2 slides if any slide has complex SVG, a chart, or a flowchart layout.

**Workflow — write all batches automatically, ask for picks once at the end:**

1. Announce the plan and the file path before writing anything:
   > *"Writing mockups in [N] batches of 3 slides. File: `C:\...\sessions\..._session\mockups.html` — you can open it now and refresh after each batch to see slides appear. I'll write all batches without stopping and ask for your picks when everything is ready."*

2. Write batch 1 using the Write tool (creates the file with `<html>`, `<head>`, `<body>`, the first batch of slide divs, and `</body></html>`). Announce the batch:
   ```
   BATCH 1 of N — Slides 1–3 written.
   ```

3. Immediately continue to batch 2 — no pause, no user prompt needed. Use the Edit tool to append: remove `</body></html>` and insert the new slide divs, then close `</body></html>` again. Announce:
   ```
   BATCH 2 of N — Slides 4–6 written.
   ```

4. Continue until all batches are written. Do not stop between batches.

5. After the final batch, ask for all picks at once:
   > *"All [N] slides are ready in `C:\...\sessions\..._session\mockups.html`. Open it and pick one option per slide, then send me all picks together (e.g. '1A, 2C, 3A, 4B, 5C ...')."*

6. When the user responds with all picks → **produce a selections-only file before Phase B.**

**Selections-only rebuild (required after picks are confirmed):**

Write `_session/mockups-selections.html` containing only the picked option for each slide — one div per slide, no A/B/C variants. This file is ~67% smaller than the full mockup, renders instantly, and eliminates the risk of the builder reading the wrong option.

```
Picks confirmed: 1A, 2C, 3A, 4B, 5C ...
Writing selections-only file: _session/mockups-selections.html
```

Pass `--mockup _session/mockups-selections.html` to the builder, not the full mockups.html. Announce the selections file path to the user.

**Edit-append pattern (for batches 2, 3, ...):**

```
old_string:  </body></html>
new_string:  [new slide divs here]

</body></html>
```

This keeps one valid HTML file throughout. The user can open it once and refresh after each batch to see slides appear at the bottom as they are written — no need to wait for Phase B to start reviewing.

---

### Mockup file structure

`_session/mockups.html` contains every slide × every option as separate `<div>` elements, written in batches:

```html
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  body { margin: 0;
         font-family: "FedEx Sans Regular", -apple-system, sans-serif; }
  .slide { position: relative; width: 1280px; height: 720px;
           background: #fff; margin: 24px auto; }
</style></head><body>

<div class="slide" data-slide-index="1" data-option="A"> ... </div>
<div class="slide" data-slide-index="1" data-option="B"> ... </div>
<div class="slide" data-slide-index="1" data-option="C"> ... </div>
<div class="slide" data-slide-index="2" data-option="A"> ... </div>
</body></html>
```

Always 1280×720 px. Always position absolute or layout flex/grid for inner content (so the walker captures clean bboxes).

### Editing mockups.html safely — large block replacements

When replacing an entire slide option or any block larger than ~10 lines, the `old_string` anchor MUST span from a unique opening tag to a unique closing tag or comment. Anchoring only on the first line of a block will match partially — the new content is inserted but the rest of the old block survives in the file, often appearing after `</html>` where the browser still renders it as an overlay.

**Minimum safe pattern for slide block replacement:**

```
old_string starts:  <!-- OPTION X: description -->
                    <div class="slide" data-slide-index="N" data-option="X">
old_string ends:    </div><!-- end slide NX (description) -->
```

Both the opening comment/tag AND the closing `</div><!-- end ... -->` comment must be included in `old_string`. The closing comment is what makes the anchor unique — without it, a short anchor matches only the first line and leaves hundreds of lines of old content in place.

**Add closing comments to every slide div when writing mockups.html:**
```html
<div class="slide" data-slide-index="1" data-option="A">
  <!-- slide content -->
  <!-- CANVAS FILL CHECK: bottom 30% intentionally used? [yes — describe anchor | no — recovery applied: describe] -->
</div><!-- end slide 1A (governing thought summary) -->
```

The `CANVAS FILL CHECK` comment is mandatory on every slide option. It must appear immediately before the closing `</div><!-- end slide ... -->`. If the answer is "no," apply a Rule 8 recovery pattern (takeaway strip, stat callout, or full-height side panel) and update the comment before moving to the next slide. **Do not proceed to the next slide until this comment reads "yes."**

**"Yes" includes intentional symmetric white space.** A two-column comparison where both columns end at the same height — leaving equal bottom margins — passes Rule 1. The white space is balanced and reads as deliberate breathing room, not as an unfinished slide. Do NOT add decorative boxes or containers just to fill the zone — that makes the empty space more visible, not less. "Yes — symmetric two-column layout, both columns end at 60% height, equal breathing room below" is a valid answer.

**"No" means:** content stopped undesigned — one column is full and another is sparse, or the bottom 40–50% is obviously incomplete with no layout rationale.

This is the second enforcement point for Rule 1 — at authoring time, not just at the pre-check declaration. The pre-check fires once before HTML authoring begins; token pressure across multi-pass Edit calls causes the constraint to drift without this per-slide gate.

**If orphaned HTML is discovered after `</html>`:** truncate the file at the last valid `</html>` line — do not attempt to re-edit around the orphaned block.

### Mockup attributes the builder recognizes

**On the slide root `<div>`:**
- `data-slide-index="N"` — required, integer
- `data-option="A|B|C"` — required, single letter
- `data-layout-master="M"` — optional, integer; enables layout-aware mode
- `data-layout-index="L"` — optional, integer; enables layout-aware mode
- `data-layout-name="..."` — optional, informational only

**On any inner element:**
- `data-role="source|footnote|page-number"` — fills the matching master/layout placeholder; not double-rendered
- `data-placeholder="title|body|stat-1|sub-2|caption|..."` — fills the matching layout placeholder (only in layout-aware mode); position/font come from the layout, the mockup just supplies content
- `data-chart="true"` — element gets screenshotted as a PNG and inserted as a picture
- `data-chart-data='{"categories":[...], "series":[...], "notes":"..."}'` — JSON appended to xlsx companion
- `data-chart-title="..."` — sheet name in xlsx

### Two modes

**Blank mode (default).** No `data-layout-*` attrs. Builder picks the cleanest blank-style layout from the template (searches across all masters; prefers layouts named "Blank" with no master decorations). All elements in the mockup render as overlay shapes on top of the blank canvas. Use this when:
- The story doesn't fit any of the corporate-approved layouts
- The client template has weak or sparse layouts
- You want full design freedom

**Layout-aware mode.** Slide root has `data-layout-master` + `data-layout-index`. Builder uses that exact layout from the template, then fills its placeholders by matching `data-placeholder` attributes on inner elements. Untagged elements still render as overlay. Use this when:
- The corporate template has a layout that already matches the story
- The user wants the deck to look "officially branded"
- You want corporate-approved typography and proportions automatically

Layout-aware mode produces visibly stronger results when the template is rich (FedEx, McKinsey-style branded templates). Always check `--catalog-layouts` first to see what's available.

### Layout-aware example

```html
<div class="slide"
     data-slide-index="1" data-option="A"
     data-layout-master="6" data-layout-index="17"
     data-layout-name="Title & 3 Stats">

  <div data-placeholder="title">FY26 savings ahead of plan across every horizon.</div>
  <div data-placeholder="body">Three windows tell the story.</div>

  <div data-placeholder="stat-1">$11.6M</div>
  <div data-placeholder="sub-1"><strong>FY26 — current</strong><br>+$0.7M above commitment</div>

  <div data-placeholder="stat-2">$67.6M</div>
  <div data-placeholder="sub-2"><strong>FY29 — current</strong><br>+$1.6M above target</div>

  <div data-placeholder="stat-3">$187M</div>
  <div data-placeholder="sub-3"><strong>5-year cumulative</strong><br>Through FY30</div>

  <div data-placeholder="caption">Source: FY savings model | Project tracker</div>
</div>
```

The mockup is short — content only. Position, font sizes, spacing, brand colors all come from the FedEx template's "Title & 3 Stats" layout. Add CSS for the preview if you want the HTML mockup to look like the PPTX, but it's not required.

### Authoring a chart

```html
<div data-chart="true"
     data-chart-title="FY26 savings by quarter"
     data-chart-data='{
       "categories": ["Q1","Q2","Q3","Q4"],
       "series": [
         {"name":"Plan ($M)",   "values":[2.4, 2.6, 2.8, 3.1]},
         {"name":"Actual ($M)", "values":[2.6, 2.8, 3.0, 3.2]}
       ],
       "notes": "Plan = Jan FY26 commitment. Actual = run-rate Mar FY26 close."
     }'
     style="position:absolute; top:100px; left:60px; width:760px; height:480px;">

  <!-- Anything that renders in browser: SVG, styled HTML, etc. -->
  <svg viewBox="0 0 760 480"> ... </svg>

</div>
```

- The bbox of the chart container determines the picture size in PPTX
- The chart's *visual* comes from whatever HTML/SVG is inside the container — design it however the brief calls for; that exact rendering becomes the slide image
- `data-chart-data` is independent of the visual — it's the underlying data ThinkCell will use to recreate the chart natively
- The user gets the PNG version on the slide AND the xlsx for ThinkCell paste-in

### Three options per slide — structural variation only

**Read `reference/phase-a-rules.md` Rule 3 for the full rule.** Short version: three options must vary on the **structural axis** (split-screen vs hero vs grid vs timeline vs matrix), not on the decorative axis (circles vs cards vs dividers). Before writing HTML, name the three structural approaches you'll use. If you can't articulate three different approaches, you have one option, not three — go back and think about the story until you can.

**Once you've picked the layout family for an option, consult `reference/visual-treatment-library.md` BEFORE writing HTML.** Find the entry for that layout family and pick the recipe variant whose "when to use" criterion matches your slide's content (MECE declaration → dark headers; supporting evidence → tinted cards; rhythm break → rule + label only; etc.). The variant determines your composition, not just your color choices. Check the reference PDFs in `~/.claude/skills/references/` for examples that match your layout + variant.

This step is what produces deliberate composition instead of generic defaults. Skipping it means every three-column slide drifts toward looking the same regardless of what the slide is doing.

Concrete examples of acceptable structural variation:
- A: hero-number-dominant · B: bridge-as-waterfall · C: Q&A grid (three questions answered)
- A: direct-contrast (A vs B side-by-side) · B: scenario table dominant · C: closure visualization with action checklist
- A: kanban (Ready/Support/At-risk columns) · B: countdown-anchor with readiness bars · C: handoff-timeline-matrix

When the template has rich corporate layouts, mix the modes: option A might be a layout-aware "Title & 3 Stats", option B a custom blank-mode design, option C another corporate layout like "Title & Comparison".

---

## Phase A self-check — mandatory before showing mockups to user (FALLBACK path only)

> **HTML-fallback slides only.** Skeleton-matched slides do not produce HTML mockups, so this self-check does not apply to them. Skeleton slides have their own validation in Step 3 (structural patches) and Step 4 (render + review) of the v2 Skeleton Pipeline.

Run the canonical checklist in **`reference/phase-a-rules.md` § "The pre-show checklist"** on every slide × every option that's on the HTML-fallback path. That file is the single source of truth — do not maintain a parallel list here.

### Where to log the self-check

Write a brief audit at the top of `_session/mockups.html` as an HTML comment before saving for user review:

```html
<!--
  PHASE A SELF-CHECK — DECK [name]
  Slide 1: A=horizontal-card-grid · B=split-with-context · C=numbered-stack — all pass
  Slide 2: A=hero-number-dominant · B=bridge-as-waterfall · C=Q&A-grid — all pass
  ...
-->
```

Naming the structural approach forces you to actually have one. If you can't write the audit, you haven't checked.

---

## Phase B — Building the deck

> **Legacy fallback (pattern library) only.** This is the HTML-mockup → PPTX build path (`build_slide.py` + Playwright + python-pptx). For client-facing decks use the Slide Lab build flow instead (see top of file); the build flow agents generate python-pptx scripts directly and never invoke `build_slide.py`.

### Invocation

```bash
py -3 skills/slide-builder/scripts/build_slide.py \
  --mockup _session/mockups.html \
  --picks "1A,2C,3A,4B,5A" \
  --target <project>/<client>-deck.pptx \
  --client-template <project>/<client-template.pptx>
```

The picks string maps `slide-index + option` from the mockup. Order in the picks string is the order in the deck.

Outputs:
- `<deck>.pptx` — final deck
- `<deck>-chart-data.xlsx` — ThinkCell-compatible data, one sheet per chart, plus a Notes sheet (only created if any slide had a chart)

### What the builder does in detail

For each picked slide-option:

1. Renders `_session/mockups.html` in headless Chromium
2. Locates the slide root by `[data-slide-index][data-option]`
3. Reads optional `data-layout-master`/`data-layout-index` from the root
4. Walks every visible descendant via `getBoundingClientRect()` + `getComputedStyle()`, capturing for each: bbox, background color (with alpha), text color, font size/weight/style/family, text align/transform, letter-spacing, borders, parent flex info, and inline run breakdown (for `<span>` color/weight overrides inside paragraph text)
5. Picks the slide layout: the named one if layout-aware attrs were provided, else the cleanest blank
6. Adds the slide using that layout
7. If layout-aware: fills all `data-placeholder`-tagged elements into the layout's matching placeholders (matched by name keywords against the LAYOUT's placeholder names, then resolved to the slide's placeholder by `idx`)
8. Screenshots `data-chart` elements at 2x DPI, inserts as pictures
9. Renders all remaining elements (not placeholder-filled, not charts, not invariants) as overlay shapes/textboxes
10. Fills `data-role="source|footnote|page-number"` elements into master placeholders if found, falls back to a textbox at element coordinates
11. Theme-binds colors: any element color matching exactly a theme slot's hex emits as `<a:schemeClr val="..."/>`; others emit as `<a:srgbClr val="HEX"/>`
12. Stamps `<a:latin typeface="..."/>` on every run using the template's major (for ≥18pt or bold) or minor (everything else) typeface
13. Collects `data-chart-data` JSON for the xlsx companion
14. Inserts process icon PNGs: when a `div.process-icon[data-icon]` element is encountered, captures its bounding box, skips child SVG elements, and inserts `slide-builder/icons/<data-icon>.png` as a picture shape. Tints the icon using accent1 from `theme.json` (PIL required; falls back to untinted if PIL is unavailable).
15. **Flowchart SVG overlays:** The DOM walker excludes full-slide SVG overlays from the screenshot path (detection: `pointer-events === 'none'` AND width/height ≥ 90% of slide dimensions). This means flowchart connector arrows do NOT appear in the built PPTX — they must be added manually in PowerPoint after the build. The boxes, labels, and non-overlay shapes render correctly. Do NOT attempt to walk SVG `<path>` or `<marker>` elements as individual shapes — they are not renderable by python-pptx. See Issue 13 in `reference/known-issues-and-improvements.md`.
16. **Master footer bleed (fixed 2026-05-14):** `build_slide.py` now clears any `PP_PLACEHOLDER.FOOTER`-type placeholder immediately after slide creation, suppressing master footer text on all slides. `data-role="footer"` elements render correctly as overlay shapes on top. See Issue 16 in `reference/known-issues-and-improvements.md`.

### Parallel build mode (5+ slide decks)

For decks with 5 or more slides, offer the user a parallel build:

> "This deck has N slides. I can build them in parallel — each slide runs in its own worker, which saves roughly 60–90 seconds per slide after a 30-second startup cost. Worth it for 5+ slides. Want me to build in parallel?"

If the user confirms, use this flow instead of the standard invocation:

**Step 1 — Dispatch one subagent per slide:**

Each subagent runs a single-slide build:
```powershell
py -3 skills/slide-builder/scripts/build_slide.py `
  --mockup _session/mockups.html `
  --picks "1A,2C,3A,4B,5A" `
  --slide <N> `
  --target _session/slide-<N>-temp.pptx `
  --client-template <client-template.pptx>
```

The `--picks` string is the full picks string — the `--slide N` flag filters it to just slide N. This avoids rewriting the picks string per worker.

**Step 2 — Merge after all workers complete:**
```powershell
py -3 skills/slide-builder/scripts/merge_slides.py `
  --session _session `
  --client-template <client-template.pptx> `
  --target <project>/<client>-deck.pptx
```

**Parallel build constraints (must be respected to avoid known failures):**
- Each worker starts its own Playwright/headless Chromium instance — workers do NOT share a browser process
- `mockups.html` and `selections.md` are read-only during Phase B — no worker may write to them
- Each worker writes to its own temp PPTX — never to the final `deck.pptx` or to another worker's temp file
- If any worker fails, fall back to serial build for that slide only, then re-run merge
- Do not use in-place lxml modification on cloned slides inside parallel workers — always use `copy.deepcopy()`

**Fallback:** If the user declines or if any worker errors, build serially with the standard invocation.

### Built-in safeguards

- Skips placing the slide root `<div>` as a shape (it's the canvas, not content)
- Ignores layout-spec attrs that are out of range (bad master/layout numbers fall back to blank mode, with a warning)
- Heuristic source/footnote/page-number detection still runs for mockups that didn't tag invariants explicitly (bottom-of-slide tiny-font text starting with "source"/"footnote", short page-number tokens)
- Layout-aware placeholder matches accept aliases (`stat-1` → "Statistic Placeholder 1", `body` → "Text Placeholder N", `caption` → "Caption Placeholder 1")

---

## Post-Build Reviewer Pass

This runs after Phase B completes. It is a hard gate — issues flagged here must be reported to the user before delivery, with slide number, element description, and recommended fix. Do not silently ignore failures.

The reviewer pass catches things that looked fine in the HTML mockup but broke during PPTX conversion: font sizes that snapped unexpectedly, colors that didn't theme-bind, text that got clipped, charts that rendered too small.

**MANDATORY: Read `~/.claude/projects/.../memory/qc_mandatory_rules.md` before running this pass.** That file documents the past QC failures that this pass exists to prevent. Two rules from it bind every Phase B handover:

1. **Render the real PPTX.** XML and python-pptx introspection alone CANNOT see master-inherited styling, grouped-shape transform bugs (`<a:chOff>/<a:chExt>`), or width-driven text-wrap clipping. These bugs are invisible to Steps 1–3 below and only surface in a real render. Step 0 (added below) is non-negotiable.
2. **Per-zone inspection on every rendered PNG.** Glancing at thumbnails and saying "looks fine" is the failure mode that broke trust. Read every zone of every slide.

### Step 0 — Real PPTX render (run BEFORE Steps 1–4 below)

This step is non-negotiable. Skipping it means Steps 1–3 are reading XML and trusting properties that may be `None` (master-inherited) — the exact blind spot that produced past regressions.

```bash
py -3 <SLIDE_QC_SCRIPTS>/export_slides.py "<built_deck>.pptx" --out "<session_folder>/_qc/"
```

(Use the absolute path to `slide-qc/scripts/export_slides.py`.) The script renders at 1920px width via PowerPoint COM. If COM is unavailable in the user's environment, fall back to LibreOffice headless via `qc_render_pptx.py` (see slide-qc reference). HTML approximations of the PPTX are forbidden — they cannot see the failure modes Step 0 exists to catch.

Then, using the Read tool, load every exported PNG and run the per-zone inspection below for each slide. Do this BEFORE writing the reviewer summary:

```
SLIDE [N] — PER-ZONE INSPECTION (run on the rendered PNG, not on XML)
[ ] Action title — readable, correct font size, not centered (unless cover), not inheriting master colour
[ ] Sub-headline — readable, aligned with title, no leftover zone fill
[ ] Every numeral / hero stat / KPI chip — full digits visible (no "0" where "01" should be)
[ ] Every body text block — readable, not crammed, no orphan lines
[ ] Every chart — title, subtitle, axis labels, value labels, annotations all legible and non-overlapping
[ ] Every annotation / footnote-inside-chart — readable at body size, not jammed against axis labels
[ ] Icons / images — positioned where intended, not overlapping numerals or text (grouped-shape transform OK)
[ ] Footer row — footnote, source, page number all readable, no leftover gray fill behind them
[ ] Overall composition — no overflow, no unintended overlap, no zone fighting another
```

Any unchecked line is a FAIL or WARN — fix at source (mockup HTML, build script, or template), re-build, re-render, re-inspect.

### Step 1 — Schema and open check

```bash
py -3 -c "from pptx import Presentation; Presentation('<deck>.pptx'); print('OK')"
```

If this fails, the PPTX has a structural error and cannot be opened. Fix before proceeding.

### Step 2 — Build log review

Scan the builder's console output for:

| Log pattern | What it means | Action |
|---|---|---|
| `Theme colors detected: {...}` | Brand hex values found in template | Verify brand colors present (e.g. FedEx `4D148C` as `dk2`) |
| `Theme fonts detected: major='Arial'` | Template has generic theme fonts | Warn user — template may not have corporate font set |
| `WARN: data-placeholder='X' no match` | Layout-aware placeholder didn't match | Fix placeholder name in mockup or switch to blank mode |
| `WARNING: font-size Xpx → Y.Ypt (floored)` | Sub-10pt text was snapped up | Recommend increasing that element's CSS font size to 14px+ |
| `hardcoded color` (not logged by default) | Color hex didn't match any theme slot | Check for near-miss hex values in mockup CSS |

### Step 3 — Per-slide XML/python-pptx checklist (SUPPLEMENT to Step 0, not a replacement)

**This step is python-pptx + XML only and is BLIND to:** master-inherited styling (returns `None`), grouped-shape transform bugs (`<a:chOff>`/`<a:chExt>` not validated), width-driven text wrap/clipping, washed-out small text. Step 0's real-render per-zone inspection is the gate that catches those. This step adds XML-detectable issues on top.

Read the PPTX slide list (via python-pptx) and check each slide:

```
SLIDE [N] — POST-BUILD REVIEW:
□ Font sizes: no text run below 10pt in the slide XML
□ Text clipping: textbox height is plausible for its content
  (flag if: h < font_size_pt × 1.4 × estimated_line_count)
□ Color binding: no hardcoded hex that closely matches a theme slot
  (flag if: hex is within #10 of any theme color — likely a typo)
□ Chart quality: chart picture width ≥ 500px native resolution
  (flag if: chart element was < 400px wide in the mockup)
□ Empty zones: **visual inspection required** — open in PowerPoint and check that the bottom half of each slide is intentionally used. Cannot be detected via python-pptx. Flag any slide where the bottom 30% is blank.
□ Layout-aware slides: all tagged placeholders were filled
  (flag if: any placeholder on a layout-aware slide has its default text still present)
```

### Step 4 — Reviewer output format

After running the checklist, output a reviewer summary to the user before delivering the file:

```
POST-BUILD REVIEW — [deck name].pptx
=====================================
Slide 1: PASS
Slide 2: PASS
Slide 3: FLAG — textbox at (120, 340) height 28px may clip 2-line content at 12pt.
         Recommend opening in PowerPoint and expanding the textbox manually.
Slide 4: FLAG — color #4D148B used on header shape — closest theme slot dk2 is #4D148C.
         One-digit difference — likely a typo. Correcting to theme color automatically.
Slide 5: PASS

Auto-fixes applied: 1 (slide 4 color corrected to dk2)
Items requiring manual review: 1 (slide 3 textbox height)
=====================================
Delivering deck. Manual review items noted above before sharing with client.
```

Auto-fix where safe (color near-miss → snap to theme slot). Flag and explain where manual action is needed (textbox clipping requires opening the file). Never silently discard a flag.

### Step 4a — Mandatory auto-fixes (apply immediately, do not ask)

These are correctness failures, not design choices. When any of the following are found during the reviewer pass, fix them in the mockup HTML and re-run Phase B for affected slides without asking the user:

| Finding | Auto-fix |
|---------|----------|
| Text wraps to orphan lines (last line has 1–2 words only) | Trim the content, reduce line-height, or increase textbox width in the mockup |
| Font size below 14px in any element that will be user-read text | Raise to 14px (the minimum that survives px→pt conversion reliably) |
| Process box height too small for its text content | Increase height in the mockup until all content fits at the target font size |
| Page number placeholder still reads "X" or "N" | Replace with the actual slide number |
| Footer text element has no explicit width | Add `width:800px` (or span the footer zone explicitly) |

Do NOT list these as options or ask the user which to apply. Apply all that are found, then re-deliver. After re-delivery, note what was auto-fixed in the reviewer summary.

### Step 5 — Automated geometry QA (runs automatically after every build)

`build_slide.py` runs `check_slide_geometry.py` on every slide immediately after saving the PPTX. Output appears in the build log:

```
--- Geometry QA ---
  PASS slide1.xml
  FAIL slide2.xml:
    - Overlap: ['Revenue impact'] collides with ['Key assumption']
    - Bottom boundary violated by ['footnote text']: extends to y=7012000, slide height=6858000
  WARN slide3.xml: Empty-zone warning: bottom 40% of slide contains no non-footer content.
Geometry QA: FAILURES detected above — fix the mockup and rebuild before delivering.
```

**When FAIL appears:** do not deliver the PPTX. Fix the mockup for the failing slide(s) and rebuild. Overlap failures mean elements are visually on top of each other in PowerPoint. Boundary failures mean a shape extends outside the slide canvas.

**When WARN appears:** soft warning only — bottom zone is empty. Review the slide visually; if the layout is intentionally minimal (divider, quote) it is acceptable.

**Technical QA (manual checks):**
1. **Theme colors bound correctly** — brand colors use `<a:schemeClr>` not hardcoded `<a:srgbClr>` in slide XML
2. **No layout-aware placeholder left unfilled** — check for default placeholder text ("Click to edit...")
3. **No phantom indents, no DRAFT watermark, no source line duplication** — known edge cases from earlier builder versions; should not appear but worth a quick scan

---

## Session Debrief

**Run at the end of every session, immediately after delivering the PPTX.** This is the only mechanism for capturing failure patterns across sessions. Do not skip it.

Ask the user these four questions, then save their answers (including any "nothing" responses) to `_session/debrief-YYYY-MM-DD.md`:

> **Session debrief — 4 quick questions:**
>
> 1. **What needed manual fixing after delivery?** (e.g. arrows added in PowerPoint, slide reformatted, chart replaced)
> 2. **What part of this session took longer than it should have?** (Phase A mockups, brief coaching, Phase B build, something else)
> 3. **Did anything not survive Phase B as expected?** (formatting lost, element missing, color wrong)
> 4. **Anything you'd change about the brief structure or how coaching went?**

Save the debrief to:
```
_session/debrief-YYYY-MM-DD.md
```

Use this format:
```markdown
# Session Debrief — YYYY-MM-DD

**Deck:** [deck name or client]
**Slides built:** [N]

## 1. Manual fixes after delivery
[user's answer]

## 2. What took too long
[user's answer]

## 3. Phase B surprises
[user's answer]

## 4. Brief / coaching feedback
[user's answer]
```

Output the saved path when done:
```
Debrief saved: C:\path\to\_session\debrief-YYYY-MM-DD.md
```

---

## Dependencies

```bash
pip install python-pptx lxml playwright openpyxl
playwright install chromium
```

The xlsx companion only requires `openpyxl`; if missing, the rest of the build still works and a warning is logged. Playwright is required for the build itself; the `--print-theme` and `--catalog-layouts` modes don't need Playwright (they only read the template).

---

## Reference materials

- **`reference/phase-a-rules.md`** — operational checklist for mockup design (canvas fill, takeaway dominance, structural variation, story-first sequencing). **REQUIRED reading ONLY for slides on the HTML-mockup fallback path.** Do not read this file until skeleton matching has been attempted and at least one slide has fallen through to the HTML fallback. Skeleton-matched slides do not use these rules.
- **`reference/visual-treatment-library.md`** — per-layout composition recipes for HTML-fallback slides. Companion to `phase-a-rules.md`. Skip for skeleton-matched slides.
- **`reference/direct-pptx-patterns.md`** — canonical patterns for the direct python-pptx pipeline (clone-and-replace). READ THIS before writing any bespoke build script. Covers: clone-and-delete workflow (required order of operations), clear-and-recreate text pattern (never modify lxml in-place on clones), shape-finding by position with tolerance, type guards, and multi-run title detection. All patterns are validated from real session failures — the in-place approach fails silently.
- **`reference/known-issues-and-improvements.md`** — real session failures and fixes. Read before building slides. Covers: CSS pseudo-elements invisible in PPTX, px→pt font size conversion, canvas fill with CSS Grid/flex, bullet formatting conventions, panel color weight, and white space management.
- **`../references/index.md`** — searchable catalog of 89 reference template slides across 12 PPTX files, indexed by layout family and recipe variant. The first move when designing a slide is to search this for a starting template that matches your picked layout + variant. If a close match exists, copy and adapt; if not, compose fresh.
- `reference/glossary.md` — chassis spec, anchor grid, zone vocabulary
- `reference/page-types.md` — catalog of supported page types
- `reference/rules.md` — universal MBB rules

These remain authoritative for design decisions. The chassis spec governs what makes a slide MBB-quality; this skill governs how the spec is realized in PPTX.
