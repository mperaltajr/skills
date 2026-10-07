---
name: slide-builder
description: "Default build layer of Slide Lab and the ONLY sanctioned way to build a branded multi-slide PowerPoint on a client template — never hand-roll python-pptx from a blank Presentation for this. Takes a narrative brief + a registered client PPTX template and produces a full PPTX deck via parallel agent fanout, building on the template's own layouts/masters. The template must already be registered (a one-time standalone step); if it isn't, build stops and routes the user to register it — it never registers inline or builds on a blank deck. Architecture: 9 geometric splits + 3 diagram primitives + 2 special objects + 1 HTML→PNG fallback = 14 patterns governed by 5 hardline rules and a self-improving anti-pattern library. Invoked automatically by storyline-helper after the narrative gate passes, directly to build a full deck from an existing brief/storyline package on a registered template, or for 'rebuild slide N'."
---

# Slide Lab — slide-builder

The build layer of Slide Lab. The split is the spec.

> **Running the commands in this skill — Windows vs macOS/Linux.** Every `py -3 …`
> command below is written for Windows. On **macOS/Linux**, run the identical
> command with **`python3`** instead of `py -3` (e.g. `python3 scripts/build_deck.py …`);
> script paths, flags, and arguments are all the same. LibreOffice is located
> automatically on every OS (Windows `C:\Program Files\LibreOffice`, macOS
> `/Applications/LibreOffice.app`, Linux via PATH); set the `SLIDE_LAB_SOFFICE`
> environment variable to the `soffice` path only if you installed it somewhere
> non-standard.

---

## First time here?

If you have never run this skill before, read these in order before anything else:

1. **Install from the [README](../README.md)** (the one maintained walkthrough), then run `py -3 scripts/doctor.py`: its table says what is missing and how to fix it. [INSTALL.md](INSTALL.md) is maintainer detail.
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

   **Exit 4 = wrong slide size.** Slide Lab builds every page at 13.333 × 7.5 in (1280 × 720). A template saved at another size (10 × 5.625 in is common) is refused, because every measurement would be wrong; one session built and threw away a whole round against such a template. If it is 16:9, `py -3 scripts/rescale_template.py <template.pptx>` writes `<name> 1280x720.pptx` with every box, text size and line scaled to match; register that copy. If it is not 16:9 (4:3, say), the user changes the slide size in PowerPoint (Design > Slide Size) and registers that.

   **Client style references: ask every time.** In the same pass as the color questions, ask: *"Do you have a real deck that uses this template? If you point me to it, I'll pick 3 or 4 of its best content pages so the designs match the client's look."* A no is fine; skip it. With a yes, pick 3-4 of the deck's best content pages (a process page, a chart page, a dense page; not covers or dividers) and run `py -3 scripts/add_style_refs.py --template <registered template.pptx> --from <client deck.pptx> --pages 4,5,33,37`. Every build on that template then lists those pictures in each designer's context, with instructions to match the client's visual language (numbering, icons, chart style, density) without copying content. Without them, designers have only colors and box positions, and pages come back looking generic.

2. **Show + ask in chat.** Show the user `<stem>/palette.png` (numbered swatches) and `<stem>/preview.png` in chat; if the chat cannot show images, give the file paths to open. Then ask, and wait for the answers:
   - **Name every candidate color plainly:** a plain name, the hex code, and where it appears in the template ("dark purple, 460073, title bars on most content slides").
   - **Ask for each role separately:** the main brand color, the highlight color, and the cover background (and the dark background if different). Do not mark the automatic guess as "Recommended" or pre-pick it. It was wrong on 6 of 6 registered templates (often main and highlight swapped); you may mention it only as "what the file's color settings suggest".
   - **Check for colors that live on shapes.** If the theme colors look like Office defaults (gold FFC000, blue 4472C4) or do not match what the slides visibly use, say so and offer the colors actually seen on the slides.
   - **Ask the layout questions in the same pass:** the default content layout and the cover layout (show `<stem>/thumbnails/*.png`), and optionally a reference slide (below).

   > **⛔ Hard rule — no auto-accept.**
   >
   > - Showing `palette.png` does **not** substitute for the user's answer. The pictures confirm that colors EXIST, not that the role ASSIGNMENT (main vs highlight vs cover) is correct.
   > - `--accept` (take the automatic guess) is a **user-issued shortcut**, not an orchestrator default. Use it only when the user explicitly types "accept" or equivalent.
   > - Halt and ask, even if the automatic guess looks plausible. For brand-color roles the AI's "defensible default" is not a substitute for the user's knowledge of the brand. Halt and ask, every time.

3. **Commit.** Run `commit-cli` with the user's answers:
   ```powershell
   py -3 scripts/register_template.py commit-cli <path-to-template.pptx> `
      --primary-slot dk2 --primary-hex 4D148C `
      --accent-slot lt2  --accent-hex FF6600 `
      --default-content-layout "Title and Content" --cover-layout "Cover"
   ```
   This writes `<stem>/brand.yml` + `<stem>/theme.json` + `<stem>/chrome.yml`. Optional flags: `--cover-bg-slot`, `--cover-bg-hex`, `--dark-bg-slot`, `--dark-bg-hex`, `--cover-layout NAME`, `--reference-slide N`, `--strip-master-backgrounds`, and repeatable `--layout-class "NAME=body-canonical|bespoke"`. Layout names are checked against the template; a wrong name stops the commit with the list of real names.

4. **The sample slide is the final check.** Tell the user that the sample slide (`<stem>/selftest/mock.pptx`) is where a swapped main and highlight color would show, have them open it, and run `confirm` only when they say it looks right. Builds refuse unconfirmed templates.

**What registration reads from each layout (chrome.yml), beyond the title box:**

- **Text slots named for the takeaway and the source line.** Many templates make these ordinary text (BODY) placeholders and say what they are only in the name. Registration now counts a BODY placeholder named `Subtitle`, `Subheading` or `Takeaway` as the takeaway slot (`subtitle_placeholder_idx`) when it starts just under the title (within 80 px of its bottom), and one named `Source`, `Sources` or `Footnote` as the source-line slot (`source_placeholder_idx`) when it sits in the bottom 40% of the page. A PowerPoint SUBTITLE / FOOTER placeholder still wins; a `Takeaway` box at the foot of the page is not the line under the title. With the takeaway slot set, the body starts 12 px below it and the takeaway goes into the template's own box instead of being drawn as a loose shape; with the source slot set, the body ends above it and the source line is written into it. Before, both lines missed those slots: the takeaway sat indented and the source line was dropped (2026-10-06). The sample slide shows both lines in their slots, and the self-test fails if either misses its slot.
- **The background and the side margins** (`background_hex`, `background_kind`, `body_left_px`, `body_right_px`): the layout's own background (its own, else the master's) and the left and right edges of its title and text area. Each designer's `_context.md` gives them as `--slide-canvas-bg`, `--body-left` and `--body-right`, so sketches are drawn on the real background and inside the real margins, and `brand.css`'s canvas is the default content layout's background, not a fixed white.

A template registered before these fields existed keeps working as it was: prep reads the background and margins from the template file itself, and the takeaway and source slots are used only once it is registered again (re-registering changes where the body starts, so check the sample slide).

The full subcommand documentation lives at the top of `scripts/register_template.py` (run with `--help`). `propose` still writes `register.html`, an older click-through color page; it is no longer offered. Do not point the user at it unless they ask for a page to click instead of answering in chat (then `commit --picks <picks.json>` takes its output).

**Capture the default content layout at registration.** Distinct from per-layout classifications, the orchestrator MUST also ask the user: *"Which layout do you want your content slides to use by default?"* — and pass the answer through as `--default-content-layout NAME` on `commit-cli`. This is stored in `theme.json` and read by `build_deck.py` as the template-level layout fallback. Without it, every fresh brief that lacks a per-slide `Layout:` either auto-falls to the sole body-canonical layout (when unambiguous) or hard-fails — both leave the user picking layouts mid-build instead of once at registration.

**Capture the cover layout too.** Also ask: *"Which layout should cover / title slides use?"* and pass it as `--cover-layout NAME` on `commit-cli` (stored as `cover_layout` in `theme.json`). Any slide whose `page_type` resolves to `cover` (from the brief's `**Slide type:** Cover`) is then routed to that layout automatically, ahead of the deck default. Without it the pipeline falls back to an **unambiguous** name match (a single layout literally named "Cover" / "Title" / "Title Slide") and, failing that, treats the cover like any other slide — which is how a branded cover ends up on the content layout and gets hand-built outside the pipeline. A per-slide `**Layout:**` still overrides the routing.

**Why a reference slide matters.** When the user gives Slide Lab a reference slide at registration, every worker agent that builds a slide gets that slide's spec as part of its context bundle — title position, subtitle box, accent placement, footer chrome, observed brand colors. The worker reasons against that spec as a visual anchor, so output stays consistent with the user's canonical example of "how the template should look." Without a reference slide, workers fall back to Slide Lab's 5 generic hardline rules, which are correct but not template-specific — output may drift in subtle ways (subtitle position, accent placement, chrome alignment) that the user notices and the tool can't explain. **Strongly recommended when the template has specific chrome geometry the user wants every output slide to honor.**

**Optional: capture a reference slide.** The reference slide is ONE slide in the registered template that defines how every output slide should look — title position, subtitle box, accent placement, footer chrome. When the user designates a reference slide, every per-slide worker agent receives that slide's spec as part of its `_context.md` bundle, and the build can validate output against it.

The orchestrator should ask: *"Is there a slide in this template that's the canonical example of how output should look? Tell me the slide number."* Pass the answer through as `--reference-slide N` (1-based) on `commit-cli`. At commit time, register_template extracts the layout name, placeholder geometries (title/subtitle boxes), and observed colors from that slide, and appends a `reference_slide:` block to `brand.yml`. Skipping this step is supported — builds still work, but workers reason against the skill's 5 hardline rules + anti-pattern library alone, without a per-template geometric anchor.

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

N parallel agents per deck, **three options per slide by default** (configurable 1-3 via `settings.json::options_per_slide`; set 1 to save tokens; the reviewer can replace a slide's options with new ones). The per-slide prompt injects the option count + the 14-pattern reference + 5 hardline rules + anti-pattern library.

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
                          session renders to option_X.sketch.png via
                          scripts/render_html.py (1280×720 headless
                          Chromium). Workers self-check via the same path
                          before declaring done; this stage is a safety net.

STAGE 2.6 · FINALIZE      finalize_deck.py, before the review. Puts the
   (direct path)          direct-path options on the template so the review
                          shows them finished. Cheap: a script, no agents.
                          Sketch options are not converted yet; finalize says
                          they are waiting for a pick, not missing.

STAGE 3 · REVIEW          build_review.py -> REVIEW.html
   (HUMAN GATE)           Sketch options show as sketches (labeled), direct
                          options as finished slides. The user picks an option
                          for EVERY slide, marks it "Replace these" for new
                          designs, or "Leave out" to drop it from the deck (the
                          only way a slide is left out; compile --drop is gone).
                          designs. Build my deck stays inert until every slide
                          is decided. SHOW the user REVIEW.html and WAIT.
                          The command it copies runs record_picks.py, which
                          records exactly the user's picks (check-coded; an
                          edited or partial list is refused). Nothing else
                          records picks. A Replace request is a new design
                          round: build_deck.py --slide N, then review again.

STAGE 3.5 · TRANSLATE     (picked sketch options only) Unpicked sketches are
                          never converted: that is where the token saving is.
                          settings.json "translator" decides who converts:
                          "agent": one slide-builder-translator per PICKED
                            sketch option, at most 20 at a time;
                            record_picks.py prints the list.
                          "script": record_picks.py runs translate_html.py on
                            every pick itself (seconds, no agent), renders the
                            result once and compares each element with the
                            design. Only what it can't draw (curves, images,
                            rotated text) or what came out looking different
                            goes to the agent in FALLBACK MODE; record_picks
                            lists those, usually none.

STAGE 4 · FINALIZE        finalize_deck.py again. Executes option_X.py (direct)
                          and option_X_native.py (translated sketches), grafts
                          each onto its layout, themes, renders, and records a
                          QC result per option. Picks survive a re-finalize.

STAGE 4.5 · FINAL CHECK   build_review.py --final -> FINAL-CHECK.html
   (HUMAN GATE)           Every pick, finished, on the template: the real
                          title, takeaway and page number the sketches did not
                          have. SHOW it and WAIT. Its "Build it" command carries
                          the final token, bound to the bytes of every file
                          shown. Any later finalize clears it.

STAGE 5 · COMPILE         compile_picks.py --out <out> --final-token <t>
                          Picks come from the recorded approval, never a file.
                          REFUSES (exit 5) without the token, if any shown file
                          changed, if any slide is unpicked, or if any shipped
                          option has a blocking QC finding.
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

Adjacency (Hardline #3 — no 3+ consecutive same-split) is **soft-enforced at pick time** (agent uses the prep-time hint as adjacency context) and **surfaced post-build** by `build_review.py` (advisory section in `REVIEW.html`). The user resolves the run by picking a different option for one of the offending slides at compile time, or by re-dispatching the slide with a different forecasted pattern. Brief fidelity (Hardline #4) wins over adjacency at pick time — the agent does not bend its pattern pick to satisfy adjacency.

### Why this flow wins

1. **The primitive matches human perception.** A human can identify a 50/50 vertical split or a 3-column row from a thumbnail in under a second — far faster than recalling what a named semantic layout means.
2. **Quality is a 3-layer stack.** Helpers cover geometry (`twins/helpers.py`), 5 hardline rules cover process, and a self-improving anti-pattern library at `reference/anti-patterns.md` covers aesthetics. Every curator-flagged failure becomes a permanent library entry.
3. **No fabrication.** SKELETON_REJECTED fires when brief and assigned split fundamentally disagree (brief enumerates 2 items, classifier assigned a 4-cell layout). The slide is not built rather than invented to fit.

---

## What this skill does

1. **Setup.** Use the brief's `client_template:` (the user picked it at the start and confirmed it with the storyline); ask only if the brief has none. Read the brief and explicitly read the `## Deck-level design notes` section before proceeding; those constraints are binding.
2. **Narrative + content gates.** Verify governing thoughts are specific and assertive; verify enough raw content per slide. Skip if storyline-helper already gated this session.
3. **Stage 1 — Prep.** Run `build_deck.py` to render one self-contained `_prompt.md` per slide. Each prompt is `prompt.md` with brief content interpolated, layouts/anti-patterns reference paths injected, the rotation seed computed, and the per-slide pattern routing (`PATTERN: sketch|direct`) from the classifier.
4. **Stage 2 — Parallel fanout.** Dispatch one `slide-builder-worker` agent per slide IN PARALLEL from the parent session. **At most 20 agents at a time** — `dispatch_plan.md` lists the waves when the deck is bigger than that. Dispatches past the limit are rejected, and the rejection is quiet: on one 29-slide deck about 20 of them vanished and `finalize_deck.py` exited 11 with slides 23-29 missing. The same limit applies to the Stage 3.5 translator fan-out, which is one agent per picked slide-option and so can be several times the slide count. Each agent reads the rendered `_prompt.md` and branches on the PATTERN field:
   - **the sketch path** (default): worker produces the requested option HTML file(s) (`option_A.html`, plus `B`/`C` only when the count > 1), then self-checks by rendering each via `scripts/render_html.py` and reading the resulting 1280×720 PNG before declaring done.
   - **the direct path**: worker produces the requested option script(s) (`option_A.py`, plus `B`/`C` only when the count > 1).
5. **Stage 2.5 — HTML render (sketch-path only).** For each the sketch-path slide's HTML options, the parent session renders to `option_X.sketch.png` via `py -3 scripts/render_html.py <html> <slide_NN/option_X.sketch.png>` so REVIEW.html has visual previews. Workers may also do this as part of their self-check; the parent renders any not-yet-rendered as a safety net.
6. **Stage 2.6 + 3 — Finalize, then review (a HUMAN gate — stop and wait).** Run `finalize_deck.py` (puts direct-path options on the template; sketch options wait for a pick), then `build_review.py --open` (it opens the page in the user's browser and prints the path). **Tell the user it is open and WAIT.** Never write picks yourself and never treat the review as a formality.
   - **Every slide needs a decision.** The page's Build my deck button does nothing until each slide is picked, marked **Replace these**, or marked **Leave out**. Leaving a slide out is only ever the user's choice on this page; compile no longer has a flag for it. One option per slide is still not an auto-pick.
   - **Do not review a half-rendered deck.** If the page says options have no preview, finish rendering first. A review the user cannot see is not a review.
   - **The user pastes a plain message** from the page: `Build my Slide Lab deck.` / `Folder: <out>` / `Picks: 1B 2C 3A ... (check 1a2b3c4d)`. Run `record_picks.py --out <Folder> --approved "<the Picks line, exactly>"`. It verifies the picks against the check code computed in the page and refuses an edited, partial or stale list. It is the only way picks get recorded; do not write `picks.json` by hand.
   - **Replace these** means a new design round for that slide. The page's message lists the slides to redesign and, when other slides are already picked, a `Keep: 1B 3A ... (check ...)` line. First record those: `redesign_round.py start --out <out> --slides N[,M] --kept "<the Keep line>"` (omit `--kept` if there is none). Then for each slide `build_deck.py --slide N` (the old options move to `slide_NN/_prev/`), its worker, and the sketch render. Then `redesign_round.py finish --out <out>`: with one new design per slide it picks them, converts, finalizes and opens FINAL-CHECK.html directly (no second picking page; the final check is still required). Like `apply_qc_fix.py`, it converts a design only when it changed since its last conversion, so after an exit 3 and the translator agent's FALLBACK MODE run, `finish` again keeps what the agent drew. If the user asked for alternatives (several options), finish refuses: build REVIEW.html again with `--open` and let them pick. A rebuild designs **one** option (`settings.json::options_per_slide_revision`), because the user has already said what to change and three options tripled the wait; put the user's direction in `slide_NN/_prior_feedback.md` so the worker sees it. Use `--options 3` when the user asks for alternatives again.
   - **"All options in one deck"** is a separate button on the page. It converts every option, not just the picks, so it costs several times the tokens; the page says so before sending. If the user asks for this in chat ("accept all", "put them all in a deck"), ask first: *"All options in one deck, or option A for every slide?"* Reading it the wrong way once cost 58 extra worker runs.
7. **Stage 3.5 — Translate the picked sketches only.** Unpicked sketches are never converted. Who converts depends on `settings.json::translator`:
   - `"agent"`: `record_picks.py` prints the list. Dispatch one `slide-builder-translator` per picked sketch option (at most 20 at a time). It reads `option_X.html` + `option_X.sketch.png` + brief + brand context and writes `option_X_native.py` + `option_X_translation_report.json`.
   - `"script"`: `record_picks.py` has already run `scripts/translate_html.py` on every pick and written the same files (plus `option_X_native.plan.json`, the drawing plan). It then rendered the result and compared every element with the design (`scripts/translate_alarm.py`). Elements it can't draw, and elements that came out looking different, are listed in the report's `fallback` and in `record_picks`' output; dispatch the translator in **FALLBACK MODE** on just those options. It draws only the listed elements. Finalize refuses an option whose `option_X_native.py` still starts with `# FALLBACK_PENDING`.
   - Two conversion rules: text at weight 600 or more (800 and 900 too) becomes the base font with bold on. PowerPoint only has bold on or off, and naming the heavy face instead (Arial Black, a brand "Semibold") did not survive finalize's theme font swap, so it shipped regular; the theme swap now also keeps bold on any heavy face name it replaces. On a layout with no subtitle slot the takeaway is drawn as a text box named `subtitle` (on purpose, see the translator's rules); its text is lined up with the title's left edge and width, and keeps the design's height position.
   - A canvas painted with the layout's own background (`--slide-canvas-bg` from `_context.md`) is left to the template, not drawn as a full-slide rectangle over the master's artwork. Two design checks go into the translation report and onto the review page: `MAJOR_ARROW_END_AT_BOX` (an arrowhead inside a box or within 6 px of one; `scripts/arrow_ends.py`) and the advisory `PALE_FILL_ON_BACKGROUND` (a large panel within a few shades of what is behind it). In FALLBACK MODE the translator agent renders its self-check with `scripts/selfcheck_render.py`, which uses a folder per option (two options of one slide used to share one picture) and runs the same arrow check on what it drew.
8. **Stage 4 — Finalize again.** `finalize_deck.py` executes `option_X.py` (direct) and `option_X_native.py` (translated sketches), grafts each onto its layout, themes, renders, and records a QC result per option. Recorded picks survive it. A source line on a layout with no footer slot (the template's source slot is an ordinary text box, or there is none) is drawn as a text box at the template's source position and finalize prints a `WARN: slide N: layout ... has no footer slot for the source line` line; check it on the final-check page (it used to be dropped silently).
9. **Stage 4.5 — Final check (a HUMAN gate — stop and wait).** `build_review.py --out <out> --final` writes `FINAL-CHECK.html`: every pick, finished, on the template, with the real title, takeaway and page number the sketches did not have. This is where a collision with the template becomes visible. It refuses if any pick is unfinished or blocked. Run it with `--open`. **Tell the user it is open and WAIT** for the message its Build it button copies (`Build it: I checked the finished slides.` / `Folder: <out>` / `Final check: <token>`, plus `Deck: all options, labeled` or `Put back into: <file>` when they apply).
10. **Stage 5 — Compile.** From that message run `compile_picks.py --out <Folder> --final-token <token>`, adding `--all-variations --badge` when it says `Deck: all options, labeled` (the 9 pt "Option B" label `--badge` stamps, shape `chrome-option-badge`, is Slide Lab's own review labeling: slide-qc's text-size check skips it, so it is neither under the floor nor an extra size) and `--splice-into "<file>"` when it says `Put back into: <file>`. Picks come from the recorded approval. It refuses if any file shown in the final check has changed since, if any slide has no pick, or if any shipped option has a blocking finding. Never invent the token.
11. **QC — mandatory, not optional.** Invoke slide-qc with an explicit Skill call, passing the compiled deck path so it doesn't re-discover it — `Skill tool call: skill="slide-qc", args="<absolute path to final_deck.pptx>"`. This is the definition of done: do not tell the user the deck is finished or "QC'd" until slide-qc has run and produced its report. A PDF you rendered and eyeballed is not QC — the agent that built the deck cannot grade its own output. (compile_picks.py also prints this reminder when it finishes.)
    **When the user approves QC fixes ("fix it", "build it"), go straight to the deck.** Rebuild each flagged slide with one option (`build_deck.py --slide N`, the finding in `slide_NN/_prior_feedback.md`, one worker), then run `py -3 scripts/apply_qc_fix.py --out <out> --slides N[,M] --approved "<the user's words>"`. It keeps every other pick, converts and finalizes the fixed slides, writes the final-check record, compiles, and records the user's words (check_done lists it at delivery). It converts a fixed sketch only when its design changed since the last conversion: if it exits 3 (part of the new design needs the translator agent), run the agent in FALLBACK MODE and then the same command again; the slide the agent finished is kept as is, its drawing included (it used to be converted again, erasing the drawing and exiting 3 for ever). Do not send the user back to REVIEW.html or FINAL-CHECK.html for a fix they already approved; re-run slide-qc on the new deck.
12. **Prove it's done — `check_done.py`.** "Done" is no longer something the orchestrator may assert. Run:
    ```powershell
    py -3 scripts/check_done.py --out <out>
    ```
    It checks one chain of recorded facts and exits non-zero if any link breaks: a compile **succeeded** and recorded its output; the deck is **that file, byte for byte** (no edits since); it was built from the **current** brief; it opens with nothing PowerPoint refuses; every option in it finalized with **zero** blocking findings; a **vision pass over those same bytes covered every slide** (slide-qc records it via `record_vision_qc.py`); and **no Critical or Major finding is open** (only Advisory may remain). The deterministic self-check does not count: it is structurally blind to shapes overlapping and to large empty areas, which is exactly the class that has shipped before. Do not tell the user the deck is finished until this passes.
    It also lists every gate passed over in the build (`--assume-gated`, `--allow-unconfirmed`, `--allow-missing`, a `mode:` line that skipped the storyline gate). **Tell the user about each one when you deliver.** It refuses a deck that is older than the latest rebuild or finalize.
13. **Deliver.** Give the full path of the deck named after its topic (compile prints it as `deck to share:`; `final_deck.pptx` beside it is the same file under the build's own name). No preview links. Add any overrides `check_done.py` listed, in plain words.
14. **When the user says the deck is good** ("looks good", "approved", "final", "ship it", "publish it"), free the build files it no longer needs:
    ```powershell
    py -3 scripts/publish_cleanup.py --out <out>
    ```
    It keeps the deck, the final-check page, the storyline, the brief and decisions, the deck's records and the picked slides' designs, and deletes unpicked options, every option's images and per-option PowerPoint files, the quality-check render folders, final page images and replaced options (typically about 90% of the folder). Tell the user how much it freed. The deck can still be edited later: a rebuild or insert works as usual, and the next finalize regenerates the images and files from the kept designs. Run it only on that say-so, never on your own judgment that the deck is finished; `--dry-run` shows what would go without deleting. For decks finished earlier, `--scan <sessions folder>` lists every finished deck with the space it would free; the user picks which to clean.

Rebuild individual slides with "rebuild slide N". This re-prep + re-finalize touches only slide N and grafts it back into the existing deck — every other slide's prompt, themed PPTX, and pick are left exactly as they were:

0. **One design (the default): first** `py -3 scripts/redesign_round.py start --out <out> --slides N --keep-previous` (before prep, which clears the old approval). It keeps every other slide's pick from the last build.
1. `build_deck.py --slide N --out <existing-out> --template <template>` — re-preps only slide N, merging into the existing `_meta.json` (reuses the brief recorded in `_meta.json`; pass `--brief` to rebuild from edited content). Slide N's old option files move to `slide_NN/_prev/`, so nothing stale can be picked up. Other slides are untouched. **If the user says "make slide N look like slide M,"** add `--like-slide M`: it pins slide N to slide M's recorded build path (sketch/direct) instead of re-classifying — the reference slide's cleaner look usually comes from its path, and re-classifying would silently re-route N.
2. Dispatch one `slide-builder-worker` for slide N (reads `slide_NN/_context.md` then `_prompt.md`). Render its sketches if it built on the sketch path.
3. `finalize_deck.py --slide N --out <out> --template <template>` — re-themes/renders/QCs only slide N; writes `RESULT-slide-NN.md` so the deck `RESULT.md` is preserved.
4. **One design:** `py -3 scripts/redesign_round.py finish --out <out>`. It picks the new design, converts and finalizes it, and opens FINAL-CHECK.html; continue at step 10 (the user's Build it message). There is no second picking page for a single option. **With alternatives ("with 3 options"):** skip step 0 and finish with the same review sequence as a full build (steps 6-10 above): `build_review.py`, the user decides every slide (the page has kept every other slide's pick; slide N needs a new one), `record_picks.py`, translate slide N if it is a picked sketch, finalize, `build_review.py --final`, and compile with the final token. Prep cleared the old approval, so a rebuild cannot ride it.

### Replicating a supplied page

When the user hands over a page and wants **that page** (a one-pager, a mockup), do not substitute your own summary of it. That substitution is a known failure: a supplied one-pager was replaced by an exec-summary nobody asked for.

But replicating a page faithfully also replicates its **numbers**, and that is the second known failure: a replica shipped `$300B / 6-12 months / 3x` when the brief already carried the verified `~$450B / sold out / ~4x`. Both failures are live, and fixing one naively causes the other.

The flow:

1. **Pin it** so it cannot be quietly dropped: in the brief's slide block, add `**Pinned source page:** <path to the supplied file> slide N`. Prep records it in `_meta.json`, the worker is told that **option A reproduces that page** (structure, sections, wording, on the client template), and the review page labels the slide. Compile refuses until step 2 has been run.
2. **Enumerate its figures:**
   ```powershell
   py -3 scripts/source_ledger.py build --out <out> --deck "<supplied.pptx or .pdf>" --slide N
   ```
   This lists only the **figure-bearing** slots (a dense page has 30+ text surfaces; prompting on all of them produces a bulk-accept reflex). It reads table cells, grouped shapes and chart labels, and it writes an `unreachable` list of surfaces it genuinely cannot read (numerals baked into a picture, SmartArt, think-cell/OLE).
3. **Resolve every row with the user.** Each takes exactly one of `bind_from_brief` (the value comes from the brief), `keep_source` (the user states the page's value is still right), or `replace_with` (+ a `replacement`). `null` is not a resolution.
4. **Compile refuses** (exit 5) while any row is unresolved, and `check_done.py` reports how many figures were kept verbatim and how many surfaces were unreadable, so what was taken on trust is visible at delivery.

> **Why a ledger and not an automatic check.** A differ would compare each figure against the brief and pass or fail. It cannot: the brief carries prose, not typed numbers, so deciding that "6-12 months" and "sold out" denote the same quantity is a judgment the machine does not own. A check reporting "0 conflicts" would assert exactly that judgment and the pipeline would consume it as fact. The machine records only what it knows: **this slot has not been resolved by a human.** Unreadable surfaces are referred to the slide-qc vision pass, which reads a rendered image and is the only gate that can see them.

> **If the supplied page is a PDF or a picture** (a screenshot, a scan), pin it the same way and run the same command with the file: `source_ledger.py build --out <out> --deck "<page.pdf>" --slide N` (N = the PDF page; a picture is `--slide 1`).
>
> - **A PDF page with a text layer** (exported from PowerPoint or Word, not scanned) is read like a PowerPoint page: every line of its text that carries a figure becomes a row, and **compile waits until the user resolves each one** (`bind_from_brief` / `keep_source` / `replace_with`), exactly as in step 3 (owner decision, 2026-10-06). Pictures on that page are listed in `unreachable` for the vision pass.
> - **A scanned PDF page or a picture** has nothing to read. The ledger is honest: no rows (nothing on the page is claimed as checked), the whole page in `unreachable` as **checked by eye only**, and the record compile needs, so the build can compile. slide-qc's vision pass covers that slide, and `check_done.py` says at delivery that the page was checked by eye only; tell the user. The worker is still told that option A reproduces the page, so its numbers can come through: take every figure from the brief, or confirm it with the user.
>
> A Word page: save it as a PDF first (`build` refuses other file types with that advice).

**Insert a new slide** at position N with `build_deck.py --insert N`. First add the new slide to the brief at position N and renumber the later slide headers (the brief must have exactly one more slide than the current build). `--insert N` then shifts slides ≥ N up by one — their `slide_NN/` dirs, `_meta.json` entries, and `picks.json` keys — and preps only the new slide N; the shifted slides keep their built output under their new numbers. Then dispatch one worker for slide N, run `finalize_deck.py --slide N`, and go through the same review sequence as a full build (steps 6-10): the shifted slides need a fresh look in the review page too, since their numbers changed. (Adding a page to an *external* `.pptx` Slide Lab didn't build is an existing-file edit — see "Edit an existing PowerPoint" below — not this flow; `--insert`/`--slide` only work on decks with the pipeline's `_meta.json`.)

**If a build fails or the output is wrong:** tell the user they can type `/slidelab-log` to capture a structured session report (the `slidelab-log` skill writes the technical detail and saves it locally; the user sends the file privately to Mario Peralta on Teams or by email, never to GitHub, which is public). Offer this whenever a stage exits non-zero or the user says something looks broken.

**`finalize_deck.py` exits 8 with a `[4c] TITLE / BAND OVERLAP` list** when a slide's title wraps to more lines than its title box holds (it would overlap the heading band/body — a defect class seen in an earlier user report). It's measured with the brand font, so it reflects PowerPoint even when the local preview looks fine. Fix: shorten the flagged title(s) — for a direct-path build, in the brief's `### Slide N — <title>` header (editing `_meta.json` alone is overwritten on the next `build_deck` run); for a sketch/6b slide, the `data-template-field="title"` in the worker HTML — then re-run finalize. A 2-line title never trips this; only 3+ lines that exceed the box.

### Work on a deck Slide Lab did NOT build (external `.pptx`) — options 6a / 6b / 6c

An external `.pptx` has none of the pipeline's metadata (`_meta.json`, a brief, a registered template), so the option-5 rebuild can't touch it directly. Route by **what's changing** — ask the user, then pick the fork. All three write a **new** file; never overwrite the user's original.

**6a — Fix text or numbers, keep the design (small edit).** Edit directly with `python-pptx` (already a dependency). Not a rebuild: no brief, no options, no QC pipeline.
- **Read / extract:** open the file, walk `slide.shapes`, guard each with `if shape.has_text_frame:` before reading `shape.text_frame.text` (pictures/lines/connectors have no text frame and raise otherwise).
- **Edit text:** locate the shape (slide index + shape name, or by matching its current text) and set `run.text` on the target run — editing the run (not `text_frame.text`) preserves the font, size, and color. Save to a new path.
- **Scope guard:** if the real ask is "redesign this slide" → **6b**; "refresh this recurring deck" → **6c**; "rebuild the whole thing / rebrand" → route to the storyline → slide-builder pipeline (option 1/2). **Never** hand-roll a whole deck from a blank `Presentation()`.

**6b — Redesign a slide (or a few) at full quality, then splice it back.** Rebuilds specific slides on the deck's own template and drops them back into the original, leaving every other slide untouched.
1. **Register the deck as its OWN template** first (option 7 — standalone, never inline). This makes the rebuilt slide match its neighbors' masters/layouts/brand.
2. `py -3 scripts/adopt_deck.py <deck.pptx> --slides N[,M] --out <out>` — extracts each slide's text into a `mode: rebuild-slice` brief, reads each slide's real layout, and writes `_meta.json` (marked `adopted_source`) + a copy of the original at `<out>/adopted_source.pptx`. Enrich the target slide's Evidence in `adopted_brief.md` if the extract is thin (charts/images/SmartArt don't extract).
3. `py -3 scripts/build_deck.py --slide N --out <out> --template <deck.pptx>` → dispatch the **worker** for slide N → `finalize_deck.py --slide N` → the same review sequence as a full build (steps 6-10): the review page shows only the slides being rebuilt; `record_picks.py`; translate the pick if it is a sketch; finalize; `build_review.py --final`. (The deck must be confirmed as a template first; `build_deck` stops with exit 12 otherwise.)
4. Run the Build command from FINAL-CHECK.html. For an adopted deck it already includes `--splice-into "<deck.pptx>"`: compile replaces slide N **in place** in a copy of the original (via `_sldIdLst` surgery), keeping every other slide, and writes it next to the original as `<name>_slidelab.pptx`. The `adopted_source` marker makes a plain compile refuse (it would drop the un-rebuilt slides). Then **slide-qc**; `check_done.py` finds the spliced deck from the compile record.

**6c — Refresh a recurring / PMO deck (content only, design frozen).** For a status/PMO deck on a fixed template re-issued each cycle with new numbers, same look.
1. `py -3 scripts/refresh_deck.py spec <deck.pptx>` — dumps every **text box / placeholder** field into an editable `*_refresh_spec.json`. **Limitation:** table cells, chart data, and SmartArt are NOT captured (they aren't text frames) — update those by hand, or route the slide to 6b. Say this to the user up front for a status deck with RAG tables.
2. Fill `new_text` for the fields that change this cycle; leave the rest `null`.
3. `py -3 scripts/refresh_deck.py apply <deck.pptx> <spec.json>` — writes a dated copy with those text runs replaced in place (formatting preserved), design untouched; a drift guard skips any field whose text moved since the spec was made. Then **slide-qc**.

Always output the full absolute path of the saved file as plain text.

### Editable chart data (think-cell / Excel)

Slide Lab **draws** charts as shapes (`add_rect` + `add_text`) — clean and on-brand, but not a data-bound chart you can edit in place. When the user wants charts they can re-point at data (e.g. in **think-cell**), export the underlying numbers to Excel:

```
py -3 scripts/export_chart_data.py <out_dir | narrative-brief.md> [--out chart-data.xlsx]
```

It reads each slide's `**Chart data:**` block from the brief and writes one workbook with a sheet per chart slide (data table from row 3, numbers as numbers). The user opens it, copies a sheet's range, and pastes it into a think-cell datasheet or a native PowerPoint chart's data grid. Slides with `chart type: none`, no data, or a `TBD` placeholder are skipped. This is on-request — the built deck's charts stay drawn shapes.

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

**Two gates prep enforces, and what to do about each:**

- **The template must be confirmed by a person** (`register_template.py confirm`, after looking at the mock slide). An unconfirmed template stops prep with **exit 12**. `--allow-unconfirmed` builds anyway and is written into the build's `_state.json`. There is no yes/no prompt any more; `--confirm-template` is accepted but does nothing.
- **The brief must be sealed after it passes storyline-helper's quality gate:**
  ```powershell
  py -3 scripts/seal_brief.py --brief <brief.md>
  ```
  This writes `storyline_gate_passed`, a timestamp, and a fingerprint of the brief's text. Prep checks the fingerprint, so **typing the marker by hand does not work**, and editing the brief after the gate stops prep with **exit 10** until the gate is re-run and the brief re-sealed. A brief written in this session without the gate is built with `--assume-gated`, which is also written into `_state.json`. Non-narrative flows still use `mode: template-fill | rebuild-slice | rfp`.

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
