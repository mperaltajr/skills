---
name: slide-builder
description: "Default build layer of Slide Lab and the ONLY sanctioned way to build a branded multi-slide PowerPoint on a client template — never hand-roll python-pptx from a blank Presentation for this. Takes a narrative brief + a registered client PPTX template and produces a full PPTX deck via parallel agent fanout, building on the template's own layouts/masters. The template must already be registered (a one-time standalone step); if it isn't, build stops and routes the user to register it — it never registers inline or builds on a blank deck. Architecture: 9 geometric splits + 3 diagram primitives + 2 special objects + 1 HTML→PNG fallback = 14 patterns governed by 5 hardline rules and a self-improving anti-pattern library. Invoked automatically by storyline-helper after the narrative gate passes, directly to build a full deck from an existing brief/storyline package on a registered template, or for 'rebuild slide N'."
---

# Slide Lab — slide-builder

The build layer of Slide Lab. The split is the spec.

---

## First time here?

If you have never run this skill before, read these in order before anything else:

1. **[INSTALL.md](INSTALL.md)** — pinned Python deps, Playwright + headless Chromium (sketch-path render), LibreOffice, sibling `slide-qc` skill, worker + translator agent install. End with the verification step printing `install OK`.
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

**Slide type:** Synthesis / Findings

**Governing thought (the claim):** 72% of Q3 churn cancelled within 14 days of signup — the failure point is onboarding, not renewal.

**The takeaway:** Acme's instinct is to escalate marketing spend. The data argues the opposite: churn is concentrated in the first 14 days.

**Editorial emphasis:** the numbers — 38%, 72%, and the flat 6-month cohort are the load-bearing claims.

**Evidence / content:**

- **38% YoY CHURN SPIKE** — Monthly logo churn jumped 38% year-over-year in Q3, the steepest single-quarter increase since 2022.
- **72% CANCEL WITHIN 14 DAYS** — Of churned accounts, 72% cancelled within 14 days of signup. The activation flow is the failure point.
- **6-MONTH COHORTS FLAT** — Renewal cohorts older than 6 months show flat retention. Existing customers are sticky.
```

Field reference:

- **Front matter (YAML, deck-level):** `deck_type`, `audience`, `governing_thought` (the deck's single argument), `client_name` (drives template lookup), `client_template` (absolute path to the registered `.pptx`).
- **Slide header line:** `### Slide N — <Title>` (H3, with title separated by em-dash, en-dash, or colon). The title is required on the header line — the parser pulls it from there, not from a body field.
- **Per-slide bold-labeled fields:** `**Slide type:**`, `**Governing thought (the claim):**`, `**The takeaway:**`, `**Editorial emphasis:**`, `**Evidence / content:**`, `**What this slide is NOT:**`, `**Chart type:**`. Labels are case-insensitive. Field values can be inline (`**Label:** text`) or block (`**Label:**\nmulti-line text`).
- **Evidence bullets:** every bullet should use `- **HEADING** — body sentence` so the worker can lift the bold heading into a card/column/pillar label and the body into the supporting text. Loose prose bullets work but produce less-structured slides.
- **Editorial emphasis vocabulary (closed list):** `recommend`, `warn`, `diagnose`, `show urgency`, `show progress`, `compare neutrally`, `summarize`. The worker uses this to tilt the option(s) toward the directive.

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

   > **⛔ Hard rule — no auto-accept.**
   >
   > - Reading `<stem>/preview.png` or `<stem>/palette.png` does **not** substitute for the user opening `register.html`. Those artifacts confirm that colors EXIST, not that the role ASSIGNMENT (primary vs accent vs cover-bg) is correct. Auto-pick has historically inverted on most client templates — the chat-driven flow exists precisely to catch that.
   > - The `{"accept": true}` flag is a **user-issued shortcut**, not an orchestrator default. It may only be written when the user explicitly types "accept" or equivalent in chat. If the user has not responded to the register.html prompt, the picks JSON has not been written.
   > - Halt and ask, even if the auto-best-guess in `register.proposal.json` looks plausible. Defensible-default bias causes orange/purple swaps to be committed without user review. For design decisions like brand-slot assignment, the AI's "defensible default" is not a substitute for the user's tacit knowledge — halt and ask, every time.

3. **Commit.** The orchestrator writes a `picks.json` capturing the user's choices and runs:
   ```powershell
   py -3 scripts/register_template.py commit <path-to-template.pptx> --picks <picks.json>
   ```
   This writes `<stem>/brand.yml` + `<stem>/theme.json` + `<stem>/chrome.yml`. Template is now registered.

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

**Optional: capture a reference slide.** The reference slide is ONE slide in the registered template that defines how every output slide should look — title position, subtitle box, accent placement, footer chrome. When the user designates a reference slide, every per-slide worker agent receives that slide's spec as part of its `_context.md` bundle, and the build can validate output against it.

The orchestrator should ask: *"Is there a slide in this template that's the canonical example of how output should look? Tell me the slide number."* Pass the answer through as `reference_slide_n` (integer, 1-indexed) in the picks JSON. At commit time, register_template extracts the layout name, placeholder geometries (title/subtitle boxes), and observed colors from that slide, and appends a `reference_slide:` block to `brand.yml`. Skipping this step is supported — builds still work, but workers reason against the skill's 5 hardline rules + anti-pattern library alone, without a per-template geometric anchor.

> **Never expose architectural vocabulary to the user.** The terms `body-canonical` and `bespoke` are implementation details for chrome resolution. When asking the user to pick a layout, always show layout thumbnails (`<sidecar-dir>/thumbnails/*.png`) and ask *"which one should the slide look like?"* — never *"which body-canonical layout do you want?"* If you show the user only an internal classification name, they may think they picked a visible layout when the system recorded only metadata.

---

## Routing

Any deck-build request — "build a slide", "make a deck", "rebuild slide N" — uses this skill. Briefs authored by storyline-helper route here automatically once the narrative gate passes.

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

> **Inherited briefs: confirm the layout before building.** If the brief carries `mode: rebuild-slice` in front-matter, OR the brief file was authored in a prior session (different `_session/` folder than the current working session, OR `generated_at` more than ~24 hours old), the orchestrator MUST restate the brief's `default_layout` (or the template's `default_content_layout` from `theme.json`) and ask the user: *"This brief will build against the **<layout name>** layout. Still the right choice? (Show thumbnails)"* — and wait for confirmation BEFORE running `build_deck.py`. Silently trusting a stale `default_layout` from an inherited brief is a known way to produce slides with broken footer boxes, so confirm the layout when the brief did not originate in the current session.

N parallel agents per deck, **one option per slide by default** (configurable via `settings.json::options_per_slide`; the reviewer requests more per slide only where wanted). The per-slide prompt injects the option count + the 14-pattern reference + 5 hardline rules + anti-pattern library.

```
STAGE 1 · PREP            build_deck.py
                          Reads narrative brief + client template.
                          For each slide, renders prompt.md (the current template)
                          with brief content interpolated. Each per-slide
                          prompt loads reference/layouts.md +
                          reference/anti-patterns.md + the 5 hardline rules
                          + the variant rotation seed.
                          Output: <out>/slide_NN/_prompt.md + dispatch_plan.md

STAGE 2 · PARALLEL FANOUT slide-builder-worker agents
                          Parent session dispatches one agent per slide IN
                          PARALLEL (Task tool, single message with N calls).
                          Each agent reads its _prompt.md and branches on
                          the PATTERN field:
                            PATTERN: direct → option_A.py (+ B/C only when
                                        the option count > 1; python-pptx)
                            PATTERN: sketch → option_A.html (+ B/C only when
                                        the option count > 1; HTML-first,
                                        translator converts at Stage 3.5)
                          NOTE: dispatched from the parent session, not from
                          inside the agent itself.

STAGE 2.5 · HTML RENDER   (sketch-path only) For each option_X.html, parent
                          session renders to option_X.png via
                          scripts/render_html.py (1280×720 headless
                          Chromium). Workers self-check via the same path
                          before declaring done; this stage is a safety net.

STAGE 3 · REVIEW          build_review.py + REVIEW.html
                          Builds REVIEW.html with each slide's option(s) (PNG
                          thumbnails for both the direct and sketch paths); the
                          reviewer can request 1-3 more per slide.
                          User picks per-slide; picks written to picks.json.

STAGE 3.5 · TRANSLATE     (sketch-path only) For each picked sketch-path slide,
                          parent session dispatches one slide-builder-
                          translator agent per pick. Translator reads the
                          picked option_X.html + its rendered PNG + brief
                          + brand context; emits option_X_native.py
                          (native python-pptx with editable text frames)
                          + option_X_translation_report.json (SSIM + QC).

STAGE 4 · FINALIZE        finalize_deck.py
                          direct-path picks: execute option_X.py as before,
                            graft body, populate placeholders from brief
                            title/subtitle (legacy behavior).
                          sketch-path picks: execute option_X_native.py
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

The agent picks the split per slide directly from the brief content. There is no pre-classifier that takes the decision away from the agent. Two light layers help it instead:

1. **Prep-time pattern-hint pass.** `build_deck.py` runs the **same signals table from `reference/layouts.md`** once per slide to forecast each slide's likely pattern. No new classifier logic — this IS the agent's picking procedure, run once at prep time as a forecast. The forecast is injected into the per-slide prompt as `{{LIKELY_PRIOR_PATTERNS}}` (the previous two slides' forecasts) so the agent has adjacency context at pick time. The agent can override the hint when its read of the brief differs.
2. **Pattern-pick seed.** When multiple patterns score equally on the agent's own scoring pass, the seed picks among them deterministically:
   ```
   pattern_pick_seed = md5(content_hash + slide_n)
   variant_seed      = md5(content_hash + slide_n + option_letter)
   content_hash      = md5(governing_thought + so_what + evidence_content)
   ```
   `content_hash` is locked in `build_deck.py` at prep time. Per-option variant seeds (one per requested `option_letter`) ensure sibling options — when more than one is generated — pick different variants within the chosen pattern. Without `option_letter` in the seed, all siblings would pick the same variant — that was a real bug caught by the architecture review.

Adjacency (Hardline #3 — no 3+ consecutive same-split) is **soft-enforced at pick time** (agent uses the prep-time hint as adjacency context) and **surfaced post-build** by `build_gate_preview.py` (advisory banner in `GATE3-PREVIEW.html`) + `build_review.py` (advisory section in `REVIEW.html`). The user resolves the run by picking a different option for one of the offending slides at compile time, or by re-dispatching the slide with a different forecasted pattern. Brief fidelity (Hardline #4) wins over adjacency at pick time — the agent does not bend its pattern pick to satisfy adjacency.

### Why this flow wins

1. **The primitive matches human perception.** A human can identify a 50/50 vertical split or a 3-column row from a thumbnail in under a second — far faster than recalling what a named semantic layout means.
2. **Quality is a 3-layer stack.** Helpers cover geometry (`twins/helpers.py`), 5 hardline rules cover process, and a self-improving anti-pattern library at `reference/anti-patterns.md` covers aesthetics. Every curator-flagged failure becomes a permanent library entry.
3. **No fabrication.** SKELETON_REJECTED fires when brief and assigned split fundamentally disagree (brief enumerates 2 items, classifier assigned a 4-cell layout). The slide is not built rather than invented to fit.

---

## What this skill does

1. **Setup.** Confirm the client template path with the user. Read the brief and explicitly read the `## Deck-level design notes` section before proceeding; those constraints are binding.
2. **Narrative + content gates.** Verify governing thoughts are specific and assertive; verify enough raw content per slide. Skip if storyline-helper already gated this session.
3. **Stage 1 — Prep.** Run `build_deck.py` to render one self-contained `_prompt.md` per slide. Each prompt is `prompt.md` with brief content interpolated, layouts/anti-patterns reference paths injected, the rotation seed computed, and the per-slide pattern routing (`PATTERN: sketch|direct`) from the classifier.
4. **Stage 2 — Parallel fanout.** Dispatch one `slide-builder-worker` agent per slide IN PARALLEL from the parent session. Each agent reads the rendered `_prompt.md` and branches on the PATTERN field:
   - **the sketch path** (default): worker produces the requested option HTML file(s) (`option_A.html`, plus `B`/`C` only when the count > 1), then self-checks by rendering each via `scripts/render_html.py` and reading the resulting 1280×720 PNG before declaring done.
   - **the direct path**: worker produces the requested option script(s) (`option_A.py`, plus `B`/`C` only when the count > 1).
5. **Stage 2.5 — HTML render (sketch-path only).** For each the sketch-path slide's HTML options, the parent session renders to PNG via `py -3 scripts/render_html.py <html> <png>` so REVIEW.html has visual previews. Workers may also do this as part of their self-check; the parent renders any not-yet-rendered as a safety net.
6. **Stage 3 — Review + compile.** Run `build_review.py` to build REVIEW.html (shows PNGs for both the direct and sketch paths options); user picks per-slide; picks written to `picks.json`.
7. **Stage 3.5 — Translate (sketch-path only).** For each picked sketch-path slide, the parent session dispatches a `slide-builder-translator` agent. The translator reads the picked `option_X.html` + its rendered PNG + brief + brand context, produces `option_X_native.py` (native python-pptx script with editable text frames) + `option_X_translation_report.json` (SSIM zone scores + R4 QC findings).
8. **Stage 4 — Finalize.** Run `finalize_deck.py`:
   - For direct-path picks: execute `option_X.py` as before, graft body onto template, populate placeholders from brief title/subtitle.
   - For sketch-path picks: execute `option_X_native.py`, graft body, parse the script's `__template_fields__` header, populate placeholders from THOSE values (translator-extracted from the HTML's `data-template-field` attributes, takes priority over brief fallback).
9. **Stage 5 — Compile.** `compile_picks.py` stitches the final deck.
10. **QC — mandatory, not optional.** Invoke slide-qc with an explicit Skill call, passing the compiled deck path so it doesn't re-discover it — `Skill tool call: skill="slide-qc", args="<absolute path to final_deck.pptx>"`. This is the definition of done: do not tell the user the deck is finished or "QC'd" until slide-qc has run and produced its report. A PDF you rendered and eyeballed is not QC — the agent that built the deck cannot grade its own output. (compile_picks.py also prints this reminder when it finishes.)
11. **Deliver.** PPTX. Output full absolute Windows path. No preview links.

Rebuild individual slides with "rebuild slide N". This re-prep + re-finalize touches only slide N and grafts it back into the existing deck — every other slide's prompt, themed PPTX, and pick are left exactly as they were:

1. `build_deck.py --slide N --out <existing-out> --template <template>` — re-preps only slide N, merging into the existing `_meta.json` (reuses the brief recorded in `_meta.json`; pass `--brief` to rebuild from edited content). Other slides are untouched.
2. Dispatch one `slide-builder-worker` for slide N (reads `slide_NN/_context.md` then `_prompt.md`).
3. `finalize_deck.py --slide N --out <out> --template <template>` — re-themes/renders/QCs only slide N; writes `RESULT-slide-NN.md` so the deck `RESULT.md` is preserved.
4. Take the user's new pick for slide N; update `picks.json`.
5. `compile_picks.py --out <out>` — rebuilds `final_deck.pptx` from every slide's themed PPTX, grafting the rebuilt slide N into place.

**Insert a new slide** at position N with `build_deck.py --insert N`. First add the new slide to the brief at position N and renumber the later slide headers (the brief must have exactly one more slide than the current build). `--insert N` then shifts slides ≥ N up by one — their `slide_NN/` dirs, `_meta.json` entries, and `picks.json` keys — and preps only the new slide N; the shifted slides keep their built output under their new numbers. Then dispatch one worker for slide N, run `finalize_deck.py --slide N`, take the pick, and re-run `compile_picks.py`. (Adding a page to an *external* `.pptx` Slide Lab didn't build is an existing-file edit — see "Edit an existing PowerPoint" below — not this flow; `--insert`/`--slide` only work on decks with the pipeline's `_meta.json`.)

**If a build fails or the output is wrong:** tell the user they can type `/feedback` to capture a structured session report (the `slidelab-log` skill writes the technical detail; the user just submits the GitHub link). Offer this whenever a stage exits non-zero or the user says something looks broken.

### Edit an existing PowerPoint (not built by Slide Lab)

For a small change to a `.pptx` that Slide Lab did **not** build — fix a typo, swap a number, tweak or pull out some text — edit it directly with `python-pptx` (already a dependency). This is **not** a rebuild: no brief, no template registration, no options, no QC pipeline. Use it only for small text/shape tweaks on a file the user already has.

- **Read / extract:** open the file, walk `slide.shapes`, and for each shape guard with `if shape.has_text_frame:` before reading `shape.text_frame.text` (pictures, lines, and connectors have no text frame and raise otherwise).
- **Edit text:** locate the shape (by slide index + shape name, or by matching its current text) and set `run.text` on the target run — editing the run (not `text_frame.text`) preserves the existing font, size, and color. Save to a **new** path (e.g. `<name>-edited.pptx`) unless the user explicitly asks to overwrite; never overwrite the user's file without confirming.
- **Scope guard:** if the real ask is "make this deck good," "rebrand it," or "rebuild these slides," that is **not** an edit — route to the storyline → slide-builder pipeline so it is rebuilt on a registered template. **Never** hand-roll a whole deck from a blank `Presentation()`.

Always output the full absolute path of the saved file as plain text.

### Pattern routing flag

`build_deck.py` accepts a `--pattern` flag that controls which build path each slide uses. The shipped default is `auto`: the classifier routes each slide by its content — bullet/divider-heavy slides take the direct path, visually structured slides take the sketch path.

```powershell
py -3 scripts/build_deck.py --brief <brief.md> --template <template.pptx> --out <out>
#   ↑ no flag → uses settings.json::default_pattern (ships at "auto")

py -3 scripts/build_deck.py --brief ... --template ... --out ... --pattern auto
#   ↑ per-slide routing: bullets/dividers → direct, visual structure → sketch

py -3 scripts/build_deck.py --brief ... --template ... --out ... --pattern sketch
#   ↑ force every slide through the sketch path (HTML authoring → translator → native python-pptx)

py -3 scripts/build_deck.py --brief ... --template ... --out ... --pattern direct
#   ↑ force every slide through the direct path (native python-pptx, no HTML stage)

py -3 scripts/build_deck.py --brief ... --template ... --out ... --pattern legacy
#   ↑ python-pptx-direct pipeline with no per-slide classification
```

Master switch is `settings.json::enable_sketch` (shipped `true`). Set it to `false` to disable the sketch path entirely: `auto` and `sketch` are then downgraded to `legacy` with a stderr warning, and no slide renders through Chromium. The sketch path requires the Playwright Chromium binary (see INSTALL.md Step 1.5).

---

## Hardline rules (5)

These five rules govern every build. They are the entire process layer. The aesthetics layer is the anti-pattern library at `reference/anti-patterns.md`.

1. **Charts and tables only in their respective object layouts.** No fake chart-looking visuals in card grids. Inline sparklines and micro-charts in other layouts are allowed.

2. **No fabrication beyond brief enumeration.** If the brief says "2 paths," the slide has 2 items. No invented third, fourth, or "and others" filler.

3. **No 3+ consecutive slides use the same split.** Adjacent same-split slides are allowed (legitimate cadences like a 6-finding executive section need to be expressible); three in a row is not.

4. **Brief fidelity.** Every visible word on every slide traces to brief content or documented chrome (footer, page number, section label). The agent self-attests in line 3 of each `option_X.py` header (`# Brief fidelity check: <one-line statement>`). The rule is enforced by that attestation plus human inspection in REVIEW.html — no invented third card when the brief enumerates two, no filler copy.

5. **SKELETON_REJECTED protocol.** If brief and assigned split fundamentally disagree (e.g., brief enumerates 2 items, classifier assigned a 4-cell layout), emit `# SKELETON_REJECTED: <reason>` as the first line of the option script and stop. Do not fabricate to fit. The user gets a "this slide needs a different pattern" flag in REVIEW.html and can either pick a different split for that slide or revise the brief.

The aesthetics layer (don't-library) grows from every curator-flagged failure on real builds. Read `reference/anti-patterns.md` for the live catalog. The anti-pattern library is wired into the per-slide agent prompt at prep time, so it works as prevention rather than after-the-fact QC.

---

## Fallback path — HTML→PNG for curved-container diagrams

Triggers when a brief implies a hub-and-spoke, Porter's Five Forces, fishbone, ecosystem map, or free-form network. python-pptx cannot shape-fit text to ovals, so native rendering produces text that wraps badly across the curve.

**Stack: sketch-path HTML+SVG rendered via Playwright.** The worker authors the diagram natively in HTML/SVG within the body zone (using `data-shape-id` to mark elements the translator should convert to native shapes); Playwright renders the page to a 1280×720 PNG; the translator (`agents/slide-builder-translator.md`) converts the picked HTML to editable native python-pptx at Stage 3.5.

Under **the direct path**, curved containers route to `# SKELETON_REJECTED:` — the user re-routes the slide through the sketch path for the visual treatment.

---

## File paths

```
Skill root:        C:\Users\m.a.peralta\.claude\skills\slide-builder\

This file:         slide-builder\SKILL.md
Layout reference:  slide-builder\reference\layouts.md
Anti-patterns:     slide-builder\reference\anti-patterns.md
Agent prompt:      slide-builder\prompt.md

Build scripts:     slide-builder\scripts\build_deck.py
                   slide-builder\scripts\finalize_deck.py
                   slide-builder\scripts\build_review.py
                   slide-builder\scripts\compile_picks.py

Worker agent:      %USERPROFILE%\.claude\agents\slide-builder-worker.md
Translator agent:  %USERPROFILE%\.claude\agents\slide-builder-translator.md
```

Both agent definitions are installed from `slide-builder/agents/`. Without `slide-builder-worker`, the Stage-2 fanout cannot execute; without `slide-builder-translator`, picked sketch-path slides cannot be converted to editable native python-pptx.

---

## Project folder convention, session decisions log, setup steps

Every session must:

- Use the `sessions/YYYY-MM-DD Topic/` folder structure under the client's project root.
- Write to `_session/DECISIONS.md` for any session-level decision worth keeping (template choice, scope cut, brand override, etc.).
- Ensure the client template is registered before any build — `<template-stem>/brand.yml` + `<template-stem>/theme.json` sidecars must exist in the per-template subfolder next to the PPTX (subfolder layout). See § "Register a new client template" above for the chat-driven flow.
- Output full absolute Windows paths for every artifact, never preview links (so the user can copy without parsing markdown).

Deck artifacts (brief, PPTX outputs, REVIEW.html, picks.json, DECISIONS.md) live in the project / session folder. They never live inside the skill directory.

---

## Variant rotation

Within a chosen split, agents have autonomy on variant choices: typography weight, accent placement, icon vs no-icon, numeral vs no-numeral, eyebrow vs no-eyebrow. Variants rotate deterministically to prevent variant-level convergence:

```
content_hash      = md5(governing_thought + so_what + evidence_content)
pattern_pick_seed = md5(content_hash + slide_n)                       # picks among tied patterns
variant_seed      = md5(content_hash + slide_n + option_letter)       # picks variant per option
```

`option_letter` is part of `variant_seed` so that, when more than one option is generated on the same slide, the sibling options pick different variants; without it, all siblings would land on the same variant.

`content_hash` is locked at prep time by `build_deck.py` from the brief's governing thought + takeaway + evidence content. Brief edits do not re-shuffle pattern picks within unchanged slides because `content_hash` absorbs only the meaning-carrying fields, not formatting changes.

`pattern_pick_seed` also serves as the tiebreaker when multiple patterns fit the brief equally well — see **Build flow § Classifier** above.
