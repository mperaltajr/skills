---
name: slide-builder
description: "Default build layer of Slide Lab. Takes a narrative brief + a registered client PPTX template and produces a full PPTX deck via parallel agent fanout. Architecture: 9 geometric splits + 3 diagram primitives + 2 special objects + 1 HTML→PNG fallback = 14 patterns governed by 5 hardline rules and a self-improving anti-pattern library. Invoked automatically by storyline-helper after the narrative gate passes, or directly for 'rebuild slide N'."
---

# Slide Lab — slide-builder

The build layer of Slide Lab. The split is the spec.

---

## First time here?

If you have never run this skill before, read these in order before anything else:

1. **[INSTALL.md](INSTALL.md)** — pinned Python deps, mmdc 11.4.0, LibreOffice, sibling `slide-qc` skill, worker agent install. End with the verification step printing `install OK`.
2. **[examples/RUN.md](examples/RUN.md)** — the canonical end-to-end walkthrough (prep → agent dispatch → finalize → gate → compile → review) against the bundled example brief + your registered template. Ends with a `REVIEW.html` you can open in a browser.

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
   This creates a per-template sidecar folder at `<template-parent>/<stem>/` and writes `preview.pptx`, `preview.png`, `palette.png`, `register.html`, and `register.proposal.json` inside it. No prompts, no writes to `brand.yml` yet.

2. **Show + take picks.** The orchestrator **MUST display the `<stem>/register.html` file path to the user and wait** for the user to respond before writing `picks.json`. That page embeds the preview composite PNG + clickable palette swatches + the strip-master-backgrounds checkbox + a live picks-JSON payload. The user clicks swatches to pick primary / accent / cover-bg by visible color (no hex typing), toggles strip-bg, copies the picks JSON to clipboard, and pastes back to the chat.

   > **⛔ Hard rule — no auto-accept (added 2026-05-26 after OTC dry run failure).**
   >
   > - Reading `<stem>/preview.png` or `<stem>/palette.png` does **not** substitute for the user opening `register.html`. Those artifacts confirm that colors EXIST, not that the role ASSIGNMENT (primary vs accent vs cover-bg) is correct. Auto-pick has historically inverted on most client templates — the chat-driven flow exists precisely to catch that.
   > - The `{"accept": true}` flag is a **user-issued shortcut**, not an orchestrator default. It may only be written when the user explicitly types "accept" or equivalent in chat. If the user has not responded to the register.html prompt, the picks JSON has not been written.
   > - Halt and ask, even if the auto-best-guess in `register.proposal.json` looks plausible. Defensible-default bias caused the 2026-05-26 OTC dry run failure (orange/purple swap committed without user review). For design decisions like brand-slot assignment, the AI's "defensible default" is not a substitute for the user's tacit knowledge — halt and ask, every time.

3. **Commit.** The orchestrator writes a `picks.json` capturing the user's choices and runs:
   ```powershell
   py -3 scripts/register_template.py commit <path-to-template.pptx> --picks <picks.json>
   ```
   This writes `<stem>/brand.yml` + `<stem>/theme.json` (subfolder layout, v0.4+). Template is now registered.

The picks JSON shape and full subcommand documentation lives at the top of `scripts/register_template.py` (run with `--help`).

**Fallback for chat-only environments (`commit-cli`).** When the chat cannot open `register.html` (no local browser, JS-restricted preview panel, etc.), use the `commit-cli` subcommand instead. The orchestrator shows the user `palette.png` directly in chat, takes color picks conversationally, then invokes:

```powershell
py -3 scripts/register_template.py commit-cli <path-to-template.pptx> `
   --primary-slot dk2 --primary-hex 4D148C `
   --accent-slot lt2  --accent-hex FF6600
```

Optional flags: `--cover-bg-slot`, `--cover-bg-hex`, `--dark-bg-slot`, `--dark-bg-hex`, `--strip-master-backgrounds`, and repeatable `--layout-class "NAME=body-canonical|bespoke"`. Use `--accept` to take the Phase-1 best-guess verbatim (still requires explicit user opt-in per the no-auto-accept rule above).

The same hard rule applies: the orchestrator MUST take picks from the user in chat first; never invent slot assignments. Use `commit-cli` only when `register.html` cannot be displayed — the HTML picker is still the preferred path because it shows live swatch updates.

**Capture the default content layout at registration.** Distinct from per-layout classifications, the orchestrator MUST also ask the user: *"Which layout do you want your content slides to use by default?"* — and pass the answer through as `default_content_layout` (in the picks JSON or via `--default-content-layout NAME` on `commit-cli`). This is stored in `theme.json` and read by `build_deck.py` as the template-level layout fallback. Without it, every fresh brief that lacks a per-slide `Layout:` either auto-falls to the sole body-canonical layout (when unambiguous) or hard-fails — both leave the user picking layouts mid-build instead of once at registration.

**Why a reference slide matters.** When the user gives Slide Lab a reference slide at registration, every worker agent that builds a slide gets that slide's spec as part of its context bundle — title position, subtitle box, accent placement, footer chrome, observed brand colors. The worker reasons against that spec as a visual anchor, so output stays consistent with the user's canonical example of "how the template should look." Without a reference slide, workers fall back to Slide Lab's 5 generic hardline rules, which are correct but not template-specific — output may drift in subtle ways (subtitle position, accent placement, chrome alignment) that the user notices and the tool can't explain. **Strongly recommended when the template has specific chrome geometry the user wants every output slide to honor.**

**Optional: capture a reference slide (Gate A.1, 2026-06-08).** The reference slide is ONE slide in the registered template that defines how every output slide should look — title position, subtitle box, accent placement, footer chrome. When the user designates a reference slide, every per-slide worker agent receives that slide's spec as part of its `_context.md` bundle (Gate C.1), and the build can validate output against it.

The orchestrator should ask: *"Is there a slide in this template that's the canonical example of how output should look? Tell me the slide number."* Pass the answer through as `reference_slide_n` (integer, 1-indexed) in the picks JSON. At commit time, register_template extracts the layout name, placeholder geometries (title/subtitle boxes), and observed colors from that slide, and appends a `reference_slide:` block to `brand.yml`. Skipping this step is supported — builds still work, but workers reason against the skill's 5 hardline rules + anti-pattern library alone, without a per-template geometric anchor.

> **Never expose architectural vocabulary to the user.** The terms `body-canonical` and `bespoke` are implementation details for chrome resolution. When asking the user to pick a layout, always show layout thumbnails (`<sidecar-dir>/thumbnails/*.png`) and ask *"which one should the slide look like?"* — never *"which body-canonical layout do you want?"* The 2026-06-02 OTC rebuild surfaced this gap (user picked `2_Title & Text 01` thinking they had selected it; system treated the pick as classification metadata only).

---

## Routing

Any deck-build request — "build a slide", "make a deck", "rebuild slide N" — uses this skill. Briefs authored by storyline-helper route here automatically once the narrative gate passes. Historical context (why this architecture, what was retired) lives at the bottom under § "Appendix — architectural history."

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

## Build flow — four-stage architecture

> **Inherited briefs: confirm the layout before building.** If the brief carries `mode: rebuild-slice` in front-matter, OR the brief file was authored in a prior session (different `_session/` folder than the current working session, OR `generated_at` more than ~24 hours old), the orchestrator MUST restate the brief's `default_layout` (or the template's `default_content_layout` from `theme.json`) and ask the user: *"This brief will build against the **<layout name>** layout. Still the right choice? (Show thumbnails)"* — and wait for confirmation BEFORE running `build_deck.py`. Reference: `feedback_validate_user_architecture`. Inherited briefs were the proximate cause of the 2026-06-02 OTC chrome regression where the orchestrator silently trusted a stale `default_layout` value and produced slides with broken footer boxes.

N parallel agents per deck, three options per slide. The per-slide prompt injects the 14-pattern reference + 5 hardline rules + anti-pattern library.

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
                          Each agent reads its _prompt.md and branches on
                          the PATTERN field (M5, 2026-06-17):
                            PATTERN: C → option_A.py / B.py / C.py
                                        (legacy python-pptx direct)
                            PATTERN: B → option_A.html / B.html / C.html
                                        (HTML-first; translator converts
                                         to native at Stage 3.5)
                          NOTE: dispatched from the parent session, not from
                          inside the agent itself.

STAGE 2.5 · HTML RENDER   (Pattern B only) For each option_X.html, parent
                          session renders to option_X.png via
                          scripts/render_html.py (1280×720 headless
                          Chromium). Workers self-check via the same path
                          before declaring done; this stage is a safety net.

STAGE 3 · REVIEW          build_review.py + REVIEW.html
                          Builds REVIEW.html with all 3N options (PNG
                          thumbnails for both Pattern C and Pattern B).
                          User picks per-slide; picks written to picks.json.

STAGE 3.5 · TRANSLATE     (Pattern B only) For each picked Pattern B slide,
                          parent session dispatches one slide-builder-
                          translator agent per pick. Translator reads the
                          picked option_X.html + its rendered PNG + brief
                          + brand context; emits option_X_native.py
                          (native python-pptx with editable text frames)
                          + option_X_translation_report.json (SSIM + QC).

STAGE 4 · FINALIZE        finalize_deck.py
                          Pattern C picks: execute option_X.py as before,
                            graft body, populate placeholders from brief
                            title/subtitle (legacy behavior).
                          Pattern B picks: execute option_X_native.py
                            (translator output), graft body, parse the
                            script's __template_fields__ header, populate
                            placeholders from THOSE values (extracted from
                            the HTML's data-template-field attributes,
                            takes priority over brief fallback).
                          Renders PNGs via LibreOffice headless.

STAGE 5 · COMPILE         compile_picks.py stitches the chosen option per
                          slide into the final deck.pptx grafted onto the
                          client template.
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

Adjacency (Hardline #3 — no 3+ consecutive same-split) is **soft-enforced at pick time** (agent uses the prep-time hint as adjacency context) and **surfaced post-build** by `build_gate_preview.py` (advisory banner in `GATE3-PREVIEW.html`) + `build_review.py` (advisory section in `REVIEW.html`). The user resolves the run by picking a different option for one of the offending slides at compile time, or by re-dispatching the slide with a different forecasted pattern. Brief fidelity (Hardline #4) wins over adjacency at pick time — the agent does not bend its pattern pick to satisfy adjacency.

### Why this flow wins

1. **The primitive matches human perception.** A human can identify a 50/50 vertical split or a 3-column row from a thumbnail in under a second. The 19-chassis vocabulary required reading a label and recalling its definition.
2. **Quality is a 3-layer stack, not a 31-rule constraint list.** Helpers cover geometry (`twins/helpers.py`), 5 hardline rules cover process, and a self-improving anti-pattern library at `reference/anti-patterns.md` covers aesthetics. Every curator-flagged failure becomes a permanent library entry.
3. **No fabrication.** SKELETON_REJECTED fires when brief and assigned split fundamentally disagree (brief enumerates 2 items, classifier assigned a 4-cell layout). The slide is not built rather than invented to fit.

---

## What this skill does

1. **Setup.** Confirm the client template path with the user. Read the brief and explicitly read the `## Deck-level design notes` section before proceeding; those constraints are binding.
2. **Narrative + content gates.** Verify governing thoughts are specific and assertive; verify enough raw content per slide. Skip if storyline-helper already gated this session.
3. **Stage 1 — Prep.** Run `build_deck.py` to render one self-contained `_prompt.md` per slide. Each prompt is `prompt.md` (the v2 template) with brief content interpolated, layouts/anti-patterns reference paths injected, the rotation seed computed, and (M5, 2026-06-17) the per-slide pattern routing (`PATTERN: B|C`) from M1's classifier.
4. **Stage 2 — Parallel fanout.** Dispatch one `slide-builder-worker` agent per slide IN PARALLEL from the parent session. Each agent reads the rendered `_prompt.md` and branches on the PATTERN field:
   - **Pattern C** (default, legacy): worker produces three standalone python-pptx option scripts `option_A.py / B / C`.
   - **Pattern B** (M5+, opt-in): worker produces three HTML files `option_A.html / B / C`, then self-checks by rendering each via `scripts/render_html.py` and reading the resulting 1280×720 PNG before declaring done.
5. **Stage 2.5 — HTML render (Pattern B only).** For each Pattern B slide's HTML options, the parent session renders to PNG via `py -3 scripts/render_html.py <html> <png>` so REVIEW.html has visual previews. Workers may also do this as part of their self-check; the parent renders any not-yet-rendered as a safety net.
6. **Stage 3 — Review + compile.** Run `build_review.py` to build REVIEW.html (shows PNGs for both Pattern C and Pattern B options); user picks per-slide; picks written to `picks.json`.
7. **Stage 3.5 — Translate (Pattern B only).** For each picked Pattern B slide, the parent session dispatches a `slide-builder-translator` agent. The translator reads the picked `option_X.html` + its rendered PNG + brief + brand context, produces `option_X_native.py` (native python-pptx script with editable text frames) + `option_X_translation_report.json` (SSIM zone scores + R4 QC findings).
8. **Stage 4 — Finalize.** Run `finalize_deck.py`:
   - For Pattern C picks: execute `option_X.py` as before, graft body onto template, populate placeholders from brief title/subtitle.
   - For Pattern B picks: execute `option_X_native.py`, graft body, parse the script's `__template_fields__` header, populate placeholders from THOSE values (translator-extracted from the HTML's `data-template-field` attributes, takes priority over brief fallback).
9. **Stage 5 — Compile.** `compile_picks.py` stitches the final deck.
10. **QC.** Run slide-qc against the compiled deck.
11. **Deliver.** PPTX. Output full absolute Windows path. No preview links.

Rebuild individual slides with "rebuild slide N with v2" — re-prep the prompt for slide N, dispatch a single agent, finalize, replace the picked option.

### Pattern routing flag (M1, 2026-06-16) — opt-in until M7

`build_deck.py` accepts a `--pattern` flag that controls which slide-build path the deck uses. The shipped default is `legacy` — the pipeline behaves exactly as before. Pattern B (HTML-spec → translator → native python-pptx) is opt-in until the M7 cutover validation completes.

```powershell
py -3 scripts/build_deck.py --brief <brief.md> --template <template.pptx> --out <out>
#   ↑ no flag → uses settings.json::default_pattern (ships at "legacy")

py -3 scripts/build_deck.py --brief ... --template ... --out ... --pattern legacy
#   ↑ explicit legacy = pre-Pattern-B pipeline verbatim

py -3 scripts/build_deck.py --brief ... --template ... --out ... --pattern auto
#   ↑ per-slide routing via the Decision-2 classifier (bullets/dividers → C;
#     visual structure → B). Requires settings.json::enable_pattern_b: true.

py -3 scripts/build_deck.py --brief ... --template ... --out ... --pattern B
#   ↑ force all slides through Pattern B (HTML stage + translator)

py -3 scripts/build_deck.py --brief ... --template ... --out ... --pattern C
#   ↑ force all slides through Pattern C (native python-pptx direct)
```

Master switch is `settings.json::enable_pattern_b` (shipped `false`). When `false`, any non-legacy value is downgraded to `legacy` with a stderr warning — flipping `enable_pattern_b: false` is the skill-wide rollback if Pattern B underperforms.

Full Pattern B spec + locked decisions live in `_decisions/pattern-b/`. Build plan lives in `_decisions/pattern-b/build-plan/` (after M0 lands). The four quality guarantees that must hold across the refactor are documented in `_decisions/pattern-b/README.md`.

---

## Hardline rules (5)

These five rules govern every v2 build. They are the entire process layer. The aesthetics layer is the anti-pattern library at `reference/anti-patterns.md`.

1. **Charts and tables only in their respective object layouts.** No fake chart-looking visuals in card grids. Inline sparklines and micro-charts in other layouts are allowed.

2. **No fabrication beyond brief enumeration.** If the brief says "2 paths," the slide has 2 items. No invented third, fourth, or "and others" filler.

3. **No 3+ consecutive slides use the same split.** Adjacent same-split slides are allowed (legitimate cadences like a 6-finding executive section need to be expressible); three in a row is not.

4. **Brief fidelity — prompt-time-only in v0.1.** Every visible word on every slide traces to brief content or documented chrome (footer, page number, section label). The agent self-attests in line 3 of each `option_X.py` header (`# Brief fidelity check: <one-line statement>`). **No automated checker runs in the v0.1 pipeline.** Target thresholds for v0.2 (when an enforcement script lands): (a) `structural_flag_count == 0` — zero structural-count fabrications (e.g., 4 cards when the brief enumerates 2); (b) token-ratio `PER_SLIDE_MIN = 0.30` / `DECK_AVG_MIN = 0.70`, inherited from the legacy chassis-vocabulary skill's empirical recalibration. Until the script ships, the rule depends on the agent's self-attestation + REVIEW.html human inspection. See `_decisions/v0.1-audit-handover-2026-05-26.md` T1.5 for the port-vs-rewrite trade-off; v0.1 chose rewrite (this doc) over port.

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

Historical (Path D, 2026-05-26). The build scripts (`build_deck.py`, `finalize_deck.py`, `build_review.py`, `compile_picks.py`) were originally forked from the legacy chassis-vocabulary skill, which has since been archived and is no longer on disk. Three were near-verbatim copies; `build_deck.py` was the real new build — the chassis/rulebook injection was replaced with 14-pattern + anti-pattern-library injection.

The agent definition for `slide-builder-worker` (the per-slide worker dispatched from the parent session) lives at `%USERPROFILE%\.claude\agents\slide-builder-worker.md`. Without it, the fanout step cannot execute.

---

## Project folder convention, session decisions log, setup steps

Every session must:

- Use the `sessions/YYYY-MM-DD Topic/` folder structure under the client's project root.
- Write to `_session/DECISIONS.md` for any session-level decision worth keeping (template choice, scope cut, brand override, etc.).
- Ensure the client template is registered before any build — `<template-stem>/brand.yml` + `<template-stem>/theme.json` sidecars must exist in the per-template subfolder next to the PPTX (v0.4+ layout). See § "Register a new client template" above for the chat-driven flow.
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

## Appendix — architectural history

Background only. Not required reading to build a deck.

**Why the current architecture exists.** The predecessor (chassis-vocabulary) path hit 23% curator acceptance after four compensating layers — skeleton pre-assignment, SKELETON_REJECTED rule, cross-slide collision detection, deadlock audit. The abstraction was too granular for humans to validate by eye. The current architecture collapses the lever stack by changing the primitive: from named semantic chassis (`dark-canvas-hero`, `anchor-with-cards`) to **geometric splits** a human can identify from a thumbnail. Full diagnosis and four rounds of empirical testing live in `_decisions/DECISIONS.md` and `_decisions/GALLERY.html`.

**Legacy retirement (Path D, 2026-05-26).** The legacy chassis-vocabulary skill is being retired per `_decisions/cleanup-plan-master-2026-05-26.md`. Shared modules — `twins/{client_theme,composer,helpers}.py`, `scripts/icon_helper.py`, and the `icons/` catalog — have been re-homed inside this skill. The build layer is now structurally independent of the legacy code.

Artifacts archived with the legacy skill and not maintained: 19-chassis vocabulary + adjacency graph + content tags; `list[1..2]` composite schema; Layer 5 cross-slide collision detector; deadlock audit + chassis-#24 acceptance rule; 489-slug chassis TAGS backfill; family×variant×intent×relation TAGS schema; the 31-rule "Hard constraints" stack. The "pattern is the spec" architecture replaces them.
