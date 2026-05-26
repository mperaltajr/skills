---
name: slide-builder
description: "Default build layer of Slide Lab. Takes a narrative brief + a registered client PPTX template and produces a full PPTX deck via parallel agent fanout. Architecture: 9 geometric splits + 3 diagram primitives + 2 special objects + 1 HTML→PNG fallback = 14 patterns governed by 5 hardline rules and a self-improving anti-pattern library. Invoked automatically by storyline-helper after the narrative gate passes, or directly for 'rebuild slide N'."
---

# Slide Lab — slide-builder

The build layer of Slide Lab. The split is the spec.

---

## First time here?

If you have never run this skill before, read these in order before anything else:

1. **[INSTALL.md](INSTALL.md)** — pinned Python deps, mmdc 11.4.0, LibreOffice, sibling `slide-qc` skill. End with the verification step printing `install OK`.
2. **[QUICKSTART.md](QUICKSTART.md)** — the 3-command sequence against an example brief. End with a `GATE3-PREVIEW.html` you can open in a browser.
3. **[examples/RUN.md](examples/RUN.md)** — the full end-to-end (prep → agent dispatch → finalize → gate → compile → review) on the example brief plus your own registered client template.

After that, the input contract for real briefs is documented below in § "Input contract — narrative brief", and registering a new client template is below in § "Register a new client template."

Single-command sanity check (after install):

```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\build_deck.py" --help
```

Expected: argparse help text starting with `usage: build_deck.py`. Any `ImportError` means an INSTALL step was skipped.

---

## Input contract — narrative brief

The brief is a single markdown file with YAML front matter + one `### Slide N — <title>` block per slide. Each slide block uses **bold-labeled fields** (`**Label:** value`), NOT YAML keys. This is the canonical format `storyline-helper` produces.

Embedded shape (truncated — see `examples/quickstart-brief.md` for the full runnable version):

```markdown
---
deck_type: client-pitch
audience: "Acme Corp executive team — 30-min internal review"
governing_thought: "Acme should treat the Q3 customer-churn spike as a product-fit signal, not a marketing-spend gap."
client_name: "acme"
---

# Acme Q3 Churn — Strategic Pivot

## Governing thought (the whole deck)
Acme should treat the Q3 customer-churn spike as a product-fit signal, not a marketing-spend gap.

## Audience
Acme Corp executive team. Currently believe quarterly churn requires bigger marketing spend.

**Audience assumption to break:** "Q3 churn is a marketing problem — we need to spend more on brand."
**Audience belief to leave with:** "Churn is concentrated in the first 14 days; the fix is onboarding."
**The single sentence the room should say back:** "Reallocate $4M from Q4 brand to onboarding redesign."

## Sequence

---

### Slide 2 — Churn jumped 38% in Q3 — but the cause isn't where you'd expect

**Archetype:** Synthesis / Findings

**Governing thought (the claim):** 72% of Q3 churn cancelled within 14 days of signup — the failure point is onboarding, not renewal.

**So-what (the takeaway):** Acme's instinct is to escalate marketing spend. The data argues the opposite: churn is concentrated in the first 14 days.

**Editorial emphasis:** the numbers — 38%, 72%, and the flat 6-month cohort are the load-bearing claims.

**Evidence / content:**

- **38% YoY CHURN SPIKE** — Monthly logo churn jumped 38% year-over-year in Q3, the steepest single-quarter increase since 2022.
- **72% CANCEL WITHIN 14 DAYS** — Of churned accounts, 72% cancelled within 14 days of signup. The activation flow is the failure point.
- **6-MONTH COHORTS FLAT** — Renewal cohorts older than 6 months show flat retention. Existing customers are sticky.
```

Field reference:

- **Front matter (YAML, deck-level):** `deck_type`, `audience`, `governing_thought` (the deck's single argument), `client_name` (drives template lookup), `client_template` (absolute path to the registered `.pptx`).
- **Slide header line:** `### Slide N — <Title>` (H3, with title separated by em-dash, en-dash, or colon). The title is required on the header line — the parser pulls it from there, not from a body field.
- **Per-slide bold-labeled fields:** `**Archetype:**`, `**Governing thought (the claim):**`, `**So-what (the takeaway):**`, `**Editorial emphasis:**`, `**Evidence / content:**`, `**What this slide is NOT:**`, `**Chart type:**`. Labels are case-insensitive. Field values can be inline (`**Label:** text`) or block (`**Label:**\nmulti-line text`).
- **Evidence bullets:** every bullet should use `- **HEADING** — body sentence` so the worker can lift the bold heading into a card/column/pillar label and the body into the supporting text. Loose prose bullets work but produce less-structured slides.
- **Editorial emphasis vocabulary (closed list):** `recommend`, `warn`, `diagnose`, `show urgency`, `show progress`, `compare neutrally`, `summarize`. The worker uses this to tilt at least one of the three options toward the directive.

A live working example is at [examples/quickstart-brief.md](examples/quickstart-brief.md).

---

## Register a new client template

The chat-driven flow replaces the legacy PowerShell TTY flow (still available as `register_template.py interactive`).

**The orchestrator (this chat) walks through three steps:**

1. **Propose.** When the user mentions a new template, run:
   ```powershell
   py -3 scripts/register_template.py propose <path-to-template.pptx>
   ```
   This writes `<stem>.preview.pptx`, `<stem>.preview.png`, `<stem>.palette.png`, `<stem>.register.html`, and `<stem>.register.proposal.json` next to the template. No prompts, no writes to `brand.yml`.

2. **Show + take picks.** The orchestrator opens `<stem>.register.html` in the user's preview panel. That page embeds the preview composite PNG + clickable palette swatches + the strip-master-backgrounds checkbox + a live picks-JSON payload. The user clicks swatches to pick primary / accent / cover-bg by visible color (no hex typing), toggles strip-bg, copies the picks JSON to clipboard, and pastes back to the chat.

3. **Commit.** The orchestrator writes a `picks.json` capturing the user's choices and runs:
   ```powershell
   py -3 scripts/register_template.py commit <path-to-template.pptx> --picks <picks.json>
   ```
   This writes `<stem>.brand.yml` + `<stem>.theme.json`. Template is now registered.

The picks JSON shape and full subcommand documentation lives at the top of `scripts/register_template.py` (run with `--help`).

---

## Status — read before doing anything else

This skill is **the default Slide Lab build layer.** The v1 chassis-vocabulary skill (`slide-builder/`) is being retired (Path D, 2026-05-26 — see `_decisions/cleanup-plan-master-2026-05-26.md`). All deck-build requests route here.

**Routing:**

| Trigger | Correct action |
|---|---|
| Any deck-build request — "build a slide", "make a deck", "rebuild slide N" | Use this skill. |
| Brief authored by storyline-helper | Use this skill. The brief format is unchanged from v1. |
| User explicitly invokes the legacy v1 skill | Defer to user; v1 is archived but reachable if the user knows what they want. |

---

## Why v2 exists

v1's chassis-vocabulary path failed at 23% curator acceptance after four compensating layers (skeleton pre-assignment, SKELETON_REJECTED rule, cross-slide collision detection, deadlock audit). The abstraction was too granular for humans to validate by eye. v2 collapses the lever stack by changing the primitive — from named semantic chassis (`dark-canvas-hero`, `anchor-with-cards`) to **geometric splits** a human can identify from a thumbnail.

The full diagnosis, four rounds of empirical testing, and locked architecture are documented at:

```
C:\Users\m.a.peralta\.claude\skills\slide-builder\_decisions\DECISIONS.md
C:\Users\m.a.peralta\.claude\skills\slide-builder\_decisions\GALLERY.html
```

Read those two files before doing any v2 work.

---

## The architecture — 14 patterns + 1 fallback

The agent picks one pattern per slide. The pattern is the spec.

**Splits (9) — pure geometric layouts.** Full canvas · 50/50 vertical · Asymmetric vertical (75/25) · Top band + body · N-column row (3–9) · Vertical N-row stack · Dense grid (2..5 × 2..5) · Left rail + body · Horizontal bands.

**Diagram primitives (3) — native python-pptx, rectangles + explicit (x, y) connectors.** Org chart · Swimlane · Decision tree.

**Special objects (2) — first-class helpers with their own plumbing.** Chart (with quadrant mode — absorbs the old 2×2 matrix via `chart_type="quadrant"` + `quadrants: [name×4]`) · Table.

**Fallback path (1) — HTML→PNG screenshot.** For curved-container diagrams that python-pptx cannot render cleanly (hub-and-spoke, Porter's Five Forces, fishbone, ecosystem map, free-form network). The agent emits `SKELETON_REJECTED` for the native path and routes through the fallback renderer instead. See **Fallback path** below.

Full reference (one paragraph + one PNG per pattern) lives at `reference/layouts.md`. Use that as the authoritative catalog; the list above is a memory aid.

---

## Communication rules

**Always surface file paths as plain copyable text on their own line, in addition to any markdown link.** Every PPTX, PNG, HTML, MD, YAML, JSON, or PY file produced by this skill must print its full absolute Windows path verbatim — so the user can copy without parsing markdown.

---

## Build flow — four-stage architecture (mirrors v1)

The fanout shape is identical to v1's: N parallel agents per deck, three options per slide. Reusing the shape gives direct A/B comparability against v1 with zero migration risk. What changes is the **content of the per-slide prompt** — v2 injects the 14-pattern reference + 5 hardline rules + anti-pattern library, where v1 injects the chassis vocabulary + phase-a-rules + visual-treatment-library + page-types.

```
STAGE 1 · PREP            build_deck.py
                          Reads narrative brief + client template.
                          For each slide, renders prompt.md (the v2 template)
                          with brief content interpolated. Each per-slide
                          prompt loads reference/layouts.md +
                          reference/anti-patterns.md + the 5 hardline rules
                          + the variant rotation seed.
                          Output: <out>/slide_NN/_prompt.md + dispatch_plan.md

STAGE 2 · PARALLEL FANOUT slide-builder-worker agents
                          Parent session dispatches one agent per slide IN
                          PARALLEL (Task tool, single message with N calls).
                          Each agent reads its _prompt.md, picks one of the
                          14 patterns (with the rotation seed as tiebreaker),
                          and produces three standalone python-pptx scripts:
                          option_A.py / option_B.py / option_C.py
                          Each script builds ONE slide against the client
                          template.
                          NOTE: dispatched from the parent session, not from
                          inside the agent itself.

STAGE 3 · FINALIZE        finalize_deck.py
                          Executes every option_X.py, grafts each rendered
                          slide onto the client template, and renders PNGs
                          via LibreOffice headless. Produces option_A.pptx /
                          option_B.pptx / option_C.pptx + matching .png per
                          slide.

STAGE 4 · REVIEW          build_review.py + compile_picks.py
                          Builds REVIEW.html with all 3N options laid out
                          for user picks. User picks per-slide options.
                          compile_picks.py then stitches the chosen option
                          per slide into the final deck.pptx grafted onto
                          the client template.
```

### Classifier — not a classifier, just a hint + tiebreaker

The agent picks the split per slide directly from the brief content. There is no pre-classifier (a pre-classifier would re-introduce v1's chassis-routing logic). Two light layers help the agent without taking the decision away from it:

1. **Prep-time pattern-hint pass.** `build_deck.py` runs the **same signals table from `reference/layouts.md`** once per slide to forecast each slide's likely pattern. No new classifier logic — this IS the agent's picking procedure, run once at prep time as a forecast. The forecast is injected into the per-slide prompt as `{{LIKELY_PRIOR_PATTERNS}}` (the previous two slides' forecasts) so the agent has adjacency context at pick time. The agent can override the hint when its read of the brief differs.
2. **Pattern-pick seed.** When multiple patterns score equally on the agent's own scoring pass, the seed picks among them deterministically:
   ```
   pattern_pick_seed = md5(content_hash + slide_n)
   variant_seed      = md5(content_hash + slide_n + option_letter)
   content_hash      = md5(governing_thought + so_what + evidence_content)
   ```
   `content_hash` is locked in `build_deck.py` at prep time. Per-option variant seeds (one each for option_letter ∈ {A, B, C}) ensure the three sibling options pick different variants within the chosen pattern. Without `option_letter` in the seed, all three siblings would pick the same variant — that was a real bug caught by the architecture review.

Adjacency (Hardline #3 — no 3+ consecutive same-split) is **soft-enforced at pick time** (agent uses the prep-time hint as adjacency context) and **hard-enforced at finalize time** (`finalize_deck.py` post-pass surfaces any 3+ same-split run in REVIEW.html for the user to resolve). Brief fidelity (Hardline #4) wins over adjacency at pick time — the agent does not bend its pattern pick to satisfy adjacency.

### Why this flow wins

1. **The primitive matches human perception.** A human can identify a 50/50 vertical split or a 3-column row from a thumbnail in under a second. The 19-chassis vocabulary required reading a label and recalling its definition.
2. **Quality is a 3-layer stack, not a 31-rule constraint list.** Helpers cover geometry (`twins/helpers.py`), 5 hardline rules cover process, and a self-improving anti-pattern library at `reference/anti-patterns.md` covers aesthetics. Every curator-flagged failure becomes a permanent library entry.
3. **No fabrication.** SKELETON_REJECTED fires when brief and assigned split fundamentally disagree (brief enumerates 2 items, classifier assigned a 4-cell layout). The slide is not built rather than invented to fit.

---

## What this skill does

1. **Setup.** Confirm the client template path with the user. Read the brief and explicitly read the `## Deck-level design notes` section before proceeding; those constraints are binding.
2. **Narrative + content gates.** Verify governing thoughts are specific and assertive; verify enough raw content per slide. Skip if storyline-helper already gated this session.
3. **Stage 1 — Prep.** Run `build_deck.py` to render one self-contained `_prompt.md` per slide. Each prompt is `prompt.md` (the v2 template) with brief content interpolated, layouts/anti-patterns reference paths injected, and the rotation seed computed.
4. **Stage 2 — Parallel fanout.** Dispatch one `slide-builder-worker` agent per slide IN PARALLEL from the parent session. Each agent picks one pattern from the 14, applies the rotation seed if multiple patterns fit, and produces three standalone python-pptx option scripts.
5. **Stage 3 — Finalize.** Run `finalize_deck.py` to execute every option script, graft onto the client template, and render PNGs via LibreOffice.
6. **Stage 4 — Review + compile.** Run `build_review.py` to build REVIEW.html; user picks per-slide options; `compile_picks.py` stitches the final deck.
7. **QC.** Run slide-qc against the compiled deck.
8. **Deliver.** PPTX. Output full absolute Windows path. No preview links.

Rebuild individual slides with "rebuild slide N with v2" — re-prep the prompt for slide N, dispatch a single agent, finalize, replace the picked option.

---

## Input contract (verbatim from v1)

This skill consumes the same narrative-brief format that v1 consumes. The brief is produced by `storyline-helper` and lives in the session folder. Required YAML front-matter:

```yaml
---
client_template: C:\Users\...\<Client>\_templates\<template>.pptx
deck_type: <Recommendation / POV / RFP / PMO / etc.>
---
```

If `client_template:` is present and the file exists, USE THAT PATH — do not re-ask the user. If `client_template:` is missing, ask the user to fix the brief or pass a path explicitly. Same rules as v1.

The body of the brief contains the per-slide governing thoughts, supporting evidence, and any deck-level design notes. v2 does not require any v2-specific brief fields — the same brief that builds in v1 builds in v2.

**Briefs do not declare which skill builds them.** A user can take any brief produced by `storyline-helper` and route it through either v1 or v2 at invocation time.

---

## Hardline rules (5)

These five rules govern every v2 build. They are the entire process layer. The aesthetics layer is the anti-pattern library at `reference/anti-patterns.md`.

1. **Charts and tables only in their respective object layouts.** No fake chart-looking visuals in card grids. Inline sparklines and micro-charts in other layouts are allowed.

2. **No fabrication beyond brief enumeration.** If the brief says "2 paths," the slide has 2 items. No invented third, fourth, or "and others" filler.

3. **No 3+ consecutive slides use the same split.** Adjacent same-split slides are allowed (legitimate cadences like a 6-finding executive section need to be expressible); three in a row is not.

4. **Brief fidelity — thresholds defined in `slide-builder/tests/gate4/check_brief_fidelity.py`.** Every visible word on every slide traces to brief content or documented chrome (footer, page number, section label). Two-tier check: (a) **`structural_flag_count == 0`** is the hard non-negotiable — zero structural-count fabrications (e.g., 4 cards when the brief enumerates 2). (b) Token-ratio thresholds for calibration: `PER_SLIDE_MIN = 0.30` (worst option per slide), `DECK_AVG_MIN = 0.70` (deck average). Constants are inherited from v1's empirical recalibration (twice, post Gate 4 v2 first run). v2's own calibration baseline pending — re-validate after 3+ real v2 builds against items 1 (trigger-brief) and 2 (ACN) smoke outputs.

5. **SKELETON_REJECTED protocol.** If brief and assigned split fundamentally disagree (e.g., brief enumerates 2 items, classifier assigned a 4-cell layout), emit `# SKELETON_REJECTED: <reason>` as the first line of the option script and stop. Do not fabricate to fit. The user gets a "this slide needs a different pattern" flag in REVIEW.html and can either pick a different split for that slide or revise the brief.

The aesthetics layer (don't-library) starts with 26 entries from the v2 design session and grows from every curator-flagged failure on real builds. Read `reference/anti-patterns.md` for the live catalog. The anti-pattern library is wired into the per-slide agent prompt at prep time (preventive). It is **not** wired into slide-qc in v0; that decision is deferred until we have failure data from real A/B builds.

---

## Fallback path — HTML→PNG for curved-container diagrams

Triggers when a brief implies a hub-and-spoke, Porter's Five Forces, fishbone, ecosystem map, or free-form network. python-pptx cannot shape-fit text to ovals, so native rendering produces text that wraps badly across the curve.

**Stack (v0):** Mermaid with brand theme overrides. Mermaid covers the entire curved-container failure set with existing syntax and supports CSS-style theme customization for brand colors. The agent emits a Mermaid spec; the build script renders it to PNG via headless Mermaid CLI; the PNG is embedded as a full-bleed image on the slide.

If brand fidelity is visibly wrong on the first real test, v0.1 escalates to raw HTML+CSS rendered via Playwright. Playwright is not on the day-1 ship list.

The fallback path implementation is artifact #5 in the v2 build sequence. See `_decisions/DECISIONS.md § "What's new for v2"` for the artifact list.

---

## File paths

```
Skill root:        C:\Users\m.a.peralta\.claude\skills\slide-builder\

This file:         slide-builder\SKILL.md
Layout reference:  slide-builder\reference\layouts.md
Anti-patterns:     slide-builder\reference\anti-patterns.md
Agent prompt:      slide-builder\prompt.md
Decisions doc:     slide-builder\_decisions\DECISIONS.md
Gallery:           slide-builder\_decisions\GALLERY.html

Build scripts:     slide-builder\scripts\build_deck.py        (forked + modified from v1)
                   slide-builder\scripts\finalize_deck.py     (forked verbatim from v1)
                   slide-builder\scripts\build_review.py      (forked verbatim from v1)
                   slide-builder\scripts\compile_picks.py     (originally forked from the legacy skill)

Worker agent:      %USERPROFILE%\.claude\agents\slide-builder-worker.md
```

---

## Scripts — historical fork note

Historical (Path D, 2026-05-26). The build scripts (`build_deck.py`, `finalize_deck.py`, `build_review.py`, `compile_picks.py`) were originally forked from the legacy chassis-vocabulary skill that lives at `slide-builder_archived_2026-05-26/`. Three were near-verbatim copies; `build_deck.py` was the real new build — the chassis/rulebook injection was replaced with 14-pattern + anti-pattern-library injection.

The agent definition for `slide-builder-worker` (the per-slide worker dispatched from the parent session) lives at `%USERPROFILE%\.claude\agents\slide-builder-worker.md`. Without it, the fanout step cannot execute.

---

## Project folder convention, session decisions log, setup steps

Every session must:

- Use the `sessions/YYYY-MM-DD Topic/` folder structure under the client's project root.
- Write to `_session/DECISIONS.md` for any session-level decision worth keeping (template choice, scope cut, brand override, etc.).
- Ensure the client template is registered before any build — `<template-stem>.brand.yml` + `<template-stem>.theme.json` sidecars must exist next to the PPTX. See § "Register a new client template" above for the chat-driven flow.
- Output full absolute Windows paths for every artifact, never preview links (so the user can copy without parsing markdown).

Deck artifacts (brief, PPTX outputs, REVIEW.html, picks.json, DECISIONS.md) live in the project / session folder. They never live inside the skill directory.

---

## Variant rotation (simplified for v2)

Within a chosen split, agents have autonomy on variant choices: typography weight, accent placement, icon vs no-icon, numeral vs no-numeral, eyebrow vs no-eyebrow. Variants rotate deterministically to prevent variant-level convergence:

```
content_hash      = md5(governing_thought + so_what + evidence_content)
pattern_pick_seed = md5(content_hash + slide_n)                       # picks among tied patterns
variant_seed      = md5(content_hash + slide_n + option_letter)       # picks variant per option
```

**Simplification from v1.** v1's seed was `md5(family + intent + content_hash + slide_n)`. v2 drops `family` and `intent` (both required pre-classification work that v2 explicitly avoids) and adds `option_letter` so the three sibling options on the same slide pick different variants. Without `option_letter` in the seed, all three siblings would land on the same variant — caught and corrected during the architecture review.

`content_hash` is locked at prep time by `build_deck.py` from the brief's governing thought + so-what + evidence content. Brief edits do not re-shuffle pattern picks within unchanged slides because `content_hash` absorbs only the meaning-carrying fields, not formatting changes.

`pattern_pick_seed` also serves as the tiebreaker when multiple patterns fit the brief equally well — see **Build flow § Classifier** above.

---

## Open questions deferred to v0.1

- **Anti-patterns at QC time.** Wire `anti-patterns.md` into slide-qc's vision check, or rely on prompt-time prevention only? v0 picks prompt-time only. Revisit after real builds produce failure data.
- **Silent mis-pick risk (review-side fatigue).** SKELETON_REJECTED only catches enumeration mismatches and curved-container triggers. For a 20-slide deck with 3–4 silent mis-picks (agent picked a pattern the user wouldn't have), REVIEW.html fatigue ships wrong layouts. Candidate mitigations: surface the agent's top-2 pattern picks + the score gap in REVIEW.html; add a `# CONFIDENCE_LOW` marker when the score gap is narrow; build a regression harness that re-runs the picker against a held-out brief set after every `layouts.md` signals-table change. Decide before pattern #15 ships.
- **Anti-pattern library at scale.** Past ~100 entries, the library probably needs categorization (aesthetics / structural / content / chrome / encoding) and a deprecation rule. Defer until the library actually reaches that size.

---

## v1 retirement (Path D, 2026-05-26)

The legacy `slide-builder/` skill (chassis-vocabulary architecture) is being retired in Phase 8 of `_decisions/cleanup-plan-master-2026-05-26.md`. All shared modules — `twins/{client_theme,composer,helpers}.py`, `scripts/icon_helper.py`, and the `icons/` glyph catalog — have been re-homed inside this skill (Phase 2). v2 is now structurally independent of v1.

Artifacts that lived only in v1 and are not being ported:

- 19-chassis vocabulary, adjacency graph, content tags
- `list[1..2]` composite schema
- Layer 5 cross-slide collision detector
- Deadlock audit, chassis-#24 acceptance rule
- 489-slug chassis TAGS backfill
- Family×variant×intent×relation TAGS schema
- The full 31-rule "Hard constraints" stack in v1's SKILL.md

These are archived with v1, not maintained. v2's "pattern is the spec" architecture replaces them.
