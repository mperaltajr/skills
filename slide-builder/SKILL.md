---
name: slide-builder
description: "Default build layer of Slide Lab and the ONLY sanctioned way to build a branded multi-slide PowerPoint on a client template — never hand-roll python-pptx from a blank Presentation for this. Takes a narrative brief + a registered client PPTX template and produces a full PPTX deck via parallel agent fanout, building on the template's own layouts/masters. The template must already be registered (a one-time standalone step); if it isn't, build stops and routes the user to register it — it never registers inline or builds on a blank deck. Architecture: 9 geometric splits + 3 diagram primitives + 2 special objects + 1 HTML→PNG fallback = 14 patterns governed by 5 hardline rules and a self-improving anti-pattern library. Invoked automatically by storyline-helper after the narrative gate passes, directly to build a full deck from an existing brief/storyline package on a registered template, or for 'rebuild slide N'."
---

# Slide Lab — slide-builder

The build layer of Slide Lab. The split is the spec.

> **Running the commands in this skill — Windows vs macOS/Linux.** Every `py -3 …`
> command below is written for Windows. On **macOS/Linux**, run the identical
> command with **`python3`** instead of `py -3` (e.g. `python3 scripts/build_deck.py …`);
> script paths, flags, and arguments are all the same.
>
> **Which program draws the slides (owner's decision, 2026-10-09).** On Windows
> with PowerPoint installed, PowerPoint draws every render (the converter's
> self-check, finalize, the final check page, compile, slide-qc, template setup),
> the safe way (`slide-qc/scripts/ppt_safe.py`: read-only, no window, closes only
> its own file, quits only a PowerPoint it started with nothing else open).
> LibreOffice is only a backup there, and optional. On a Mac, LibreOffice draws
> them (located automatically: macOS `/Applications/LibreOffice.app`, Windows
> `C:\Program Files\LibreOffice`, Linux via PATH; set `SLIDE_LAB_SOFFICE` only
> for a non-standard install). If a render fails twice on one program, the other
> takes over. `settings.json::renderer` (`auto` | `powerpoint` | `libreoffice`)
> overrides the choice; `SLIDE_LAB_RENDERER` does it for one run.
> Many slides are rendered as **one** temporary deck and split back per slide
> (`scripts/one_deck.py`), so a round costs one PowerPoint open, not one per slide.
>
> **Tell the user before a PowerPoint render.** Before running a step that
> renders through PowerPoint (stages 6, 8, 9 and 11 below, and template
> registration), say in one plain line: *"PowerPoint may pause for a few seconds
> while Slide Lab renders slides; editing in PowerPoint during that time slows
> the build."* The scripts print the same line once per command when they start
> rendering through PowerPoint.
>
> **Tables and lists (sketch path).** Workers draw tables as an HTML `<table>`
> (header row in `<thead>`) and lists as `<ul>`/`<ol>`; the converter turns
> them into ONE native PowerPoint table and ONE text box with real bullets,
> checks its render, and falls back to separate shapes with a warning when
> they don't match (`reference/sketch-html-spec.md` § 6b).

---

## First time here?

If you have never run this skill before, read these in order before anything else:

1. **Install from the [README](../README.md)** (the one maintained walkthrough), then run `py -3 scripts/doctor.py`: its table says what is missing and how to fix it. [INSTALL.md](INSTALL.md) is maintainer detail.
2. **[examples/RUN.md](examples/RUN.md)** — the canonical end-to-end walkthrough (prep → agent dispatch → finalize → gate → compile → review) against the bundled example brief + your registered template. Ends with a `REVIEW.html` you can open in a browser.

After that, the input contract for real briefs is documented below in § "Input contract — narrative brief", and registering a new client template is below in § "Register a new client template."

**Agent files (the worker and translator Claude Code runs from `~/.claude/agents`).** A build session never copies, installs or restores them, not even when the user says it is fine (2026-10-13: a build session restored older files by hand and left the build undeliverable). Installs go through `doctor.py fix` (it backs the installed files up first) or `update.py after-pull` only, from main; the Slide Lab owner's main session installs right after a merge, the same way, never by hand. Every build step that dispatches agents (prep, `--slide`, `--insert`, `record_picks.py --edits-done`) records the installed files' versions. If they change mid-build and every version is on main, the build carries on: the step prints a note, compile prints one line and writes it into COMPILED.md ("built with slide-builder-worker from main 9e81cf4 and 1ea67d5"), and `check_done.py` repeats it; suggest a new Claude session before the next round. A version only on a branch, never committed, or one git cannot look up stops compile (exit 7) and check_done; follow the message (a new session and a new prep), never swap files back. Since 2026-10-14 compile judges only the translator file (the one agent that can still run after compile, in FALLBACK MODE for a QC fix), and check_done judges the versions the build's steps ran with: a file installed after the last agent step is a WARNING there, not a refusal, since no page was made with it.

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
- **`**Slide id:** risks`** (owner's decision, 2026-10-14): a fixed short name per slide, written by `scripts/slide_ids.py` when the storyline is approved (`emit_dot_dash.py` runs it). Never renumbered or reused; a new slide gets a new id. Prep copies it into `_meta.json` (`slide_id`), and rulings, the page map and REVIEW.html ("SLIDE 25 (risks)") use it, so an inserted divider cannot move a ruling onto the wrong page. Two slides with one id stop prep (exit 2). The seal does not count `**Slide id:**` or `**Pinned source page:**` lines (a brief sealed before 2026-10-14 still builds once it has its ids).

## The user's rulings, the page map and the context pack (owner's decisions, 2026-10-14)

About 6 in 10 of the user's steers on two decks repeated something already said, and the chat's own retelling got three wrong. So the user's direction reaches designers only in their exact words, by script:

- **Every ruling goes through `add_ruling.py`**: `py -3 scripts/add_ruling.py --out <deck> --id <slide id or deck> --topic "<short topic>" --quote "<the user's words, exactly>" --reading "<what you understood>"`. It refuses a quote that is not word for word in a message the user typed in this session (the live Claude Code transcript; join pieces of one message with `...`), stores your understanding on its own "Chat's reading" line, and writes `_session\rulings.md` (people) and `rulings.json` (scripts). A newer ruling on the same slide and topic replaces the older one, which stays struck out. Record a steer the moment the user gives it, before acting on it. **Never write the user's direction into `_prior_feedback.md`, `_context.md` or a prompt yourself**: prep leaves a hand-written "Direction from the user" block out of `_context.md` and prints the add_ruling command instead.
- **Every pipeline script prints `RULINGS: <path>`** when it ends. Read that file before replying about any slide, and after a compaction.
- **The context pack.** Every dispatch's `slide_NN/_context.md` (and `_edit_request.md`) opens with § 0b, under 2 KB: the slide's Source line, its pinned page, the deck's sources with their status, its number trail, that slide's rulings and the deck-wide rulings, all verbatim. `add_ruling.py` and `deck_sources.py` refresh it in place. Sources and figures: `py -3 scripts/deck_sources.py add --out <deck> --name "<name>" --path "<file>" [--slides <ids>|all] [--validated --approved-in-chat "<the user's words>"]` and `deck_sources.py trail --figure "120%" --where "<file, tab, cell>"`. A source the user validated is not checked again: the copied-page check counts its figures instead of asking, and source_check.py does not list them.
- **The steer receipt on REVIEW.html.** The designer answers each ruling of its slide in `slide_NN/_steer_answers.txt` (`R7: <what I changed>`). Each card shows one row per ruling with that answer; a ruling with no answer, or added after the design was made, is red. Below it, what the repeated-steer checks found.
- **Repeated steers become checks.** `scripts/steer_checks.py` runs nine checks on every design: five always (no final periods, legend top right, unit without brackets, one summary line, option A on every pinned slide) and four only once the user approved them for the deck with its own words (a word kept off main-deck slides such as "scenario", banned phrases, preferred terms such as "buyers" to "customers", names allowed only in a footnote). When `add_ruling.py` prints REPEAT, propose one (`steer_checks.py propose --out <deck> --kind <kind> --param ...`, or `--from-deck <earlier deck>` to reuse that deck's checks), ask the user, and turn it on only with their words (`steer_checks.py approve --proposal P1 --approved-in-chat "<their words>"`). A ruling no kind can check is a code change: describe it and write it only after the user approves.
- **The page map, before the build.** When earlier decks exist (a draft, a v2), run `py -3 scripts/map_source_pages.py propose --brief <brief> --from <deck.pptx> [--from <deck.pdf>]`: it proposes a source page (or "new") for every slide id, draws the pages into `_session\page_map\` and prints the list (every slide, its proposed page and picture, the next candidates). Show the user the whole list in one message, with the pictures, and wait. The map has no page of its own (owner's direction: the user does not open several HTML files); REVIEW.html shows it under the storyline as "Pages you gave us" (each supplied page, its picture, the slide it goes to or "not used"; `map_source_pages.render_section`). The user's changes: `map_source_pages.py set --brief <brief> risks=44 leaders=new`; their approval: `map_source_pages.py approve --brief <brief> --approved-in-chat "<their words>"`, which writes the `**Pinned source page:**` lines (see "Replicating a supplied page"). Never write design-reference lines such as "layout inspiration only, do not copy" into the brief: a page is either pinned (option A copies it) or not.
- **Compaction.** When the storyline is approved (emit_dot_dash.py) and after the picks (record_picks.py), the script prints a suggestion: compacting saves tokens on every later turn, and nothing is lost because everything is in files. Pass it on to the user with the command it prints (`/compact keep the path to <...>\_session\rulings.md and the page map`).
- **Where the build stands:** `py -3 scripts/build_status.py --out <deck>` prints the stage and the one next command (and the rulings count, repeats, red receipts); use it instead of opening files to work it out.
- **One wording change everywhere:** `py -3 scripts/replace_phrase.py --out <deck> --find "<old>" --replace "<new>"` lists every place in the brief, the storyline files (.md, .html, .docx) and every slide design; add `--apply` to change them all (HTML text only, whole words, converted scripts untouched). It prints the steps after (re-seal the brief, re-render, record the edit). Only for wording the user gave word for word.
- **Evidence bullets:** every bullet should use `- **HEADING** — body sentence` so the worker can lift the bold heading into a card/column/pillar label and the body into the supporting text. Loose prose bullets work but produce less-structured slides.
- **Editorial emphasis vocabulary (closed list):** `recommend`, `warn`, `diagnose`, `show urgency`, `show progress`, `compare neutrally`, `summarize`. The worker uses this to tilt the option(s) toward the directive.

A live working example is at [examples/quickstart-brief.md](examples/quickstart-brief.md).

---

## Register a new client template

The chat-driven flow replaces the legacy PowerShell TTY flow (still available as `register_template.py interactive`).

**The orchestrator (this chat) walks through three steps:**

1. **Propose.** When the user mentions a new template, give the one-line PowerPoint notice (the preview, the layout thumbnails and the sample slide are rendered through PowerPoint on Windows), then run:
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

- **The brand font's files, chosen from the fonts' own data.** Registration reads each installed font file's name table (family, style, weight, width) and picks the heading family's regular face (upright, normal width, weight nearest 400) and its bold face, plus the body family's regular face, and copies them into `<stem>/` (`title_font_ttf_path`, `title_font_bold_ttf_path`, `body_font_ttf_path` in `brand.yml`). It prints the face it chose and warns when only a narrow ("condensed") or wide version is installed. It used to guess the file from the family's name, and one family ships its condensed face as the bare `<Family>.ttf`: the sketches and the title-fit checks were drawn about a quarter narrower than the finished slide (2026-10-08). `brand.yml` also records the theme's own face names (`theme_heading_face`, `theme_body_face`, e.g. a heading face that is the family's bold face), and registration warns when heading and body are one family with a bold heading face. Title-fit measurement (the brief check, finalize, the sample slide) uses the bold face when the template's title style is bold or the theme's heading face is a bold face.

A template registered before these fields existed keeps working as it was: prep reads the background and margins from the template file itself, and the takeaway and source slots are used only once it is registered again (re-registering changes where the body starts, so check the sample slide). A template registered before 2026-10-08 keeps the font file it bundled then; register it again (with the user's look at the sample slide) to have the faces chosen from the fonts' own data.

**Where the takeaway, footnotes and source line go (owner's rule, 2026-10-08).** On every finished slide Slide Lab places these three lines itself, whatever the designer drew, so they sit in one place and size on every slide of the deck (`twins/chrome_rules.py`, run per slide at finalize on every path: direct, sketch, redesign, QC fix; also on the registration sample slide):
- **Takeaway:** directly under the title (in the template's takeaway slot when it has one, else 8 px below the title box), starting at the title's text left edge and as wide as the title's text, in the template's own Subtitle-slot size when the template has one, else 16 pt, not bold, in the template's main text color.
- **Source line:** at the template's source position (its registered Source slot, else its footer slot, else Slide Lab's standard source line), starting at the title's text left edge, 9 pt. A template footer box that is centered is moved and left-aligned.
- **Footnotes:** directly above the source line, stacked upward in order when there are several, same left edge, 9 pt.
Roles are found from the template's fields (the registered takeaway and source slots, SUBTITLE and FOOTER placeholders) and, for a loose shape, by one rule (`scripts/_chrome_schema.py` `is_page_takeaway` / `note_role`, 2026-10-09): the takeaway is a box named exactly `subtitle`, or `subtitle-...` in the top 35% of the page; a `source...` or `footnote...` box counts only in the bottom 25% of the page or when its text starts like one ("Source", "Note", "1.", "*"). A name starting `takeaway` is never the takeaway, and a shape that matches nothing is not moved. So the names `subtitle`, `source-...` and `footnote-...` are reserved for those jobs; designers name a bottom band or so-what card `band-...` or `so-what-...`. Covers and section dividers (bespoke layouts without a page number) keep their own lines.

**Page numbers are real slide-number fields, never typed text (owner's rule, 2026-10-12).** Every page-number box holds the template's own slide-number field (`<a:fld type="slidenum">`, with the template's formatting); finalize and compile set only the number it stores to the slide's position. PowerPoint and LibreOffice both compute the number from the field when they draw the page, so it stays right when slides are moved, added or deleted. slide-qc's hygiene check flags a typed page number as Major (`page_number_field`, fixed automatically).

**The template's own sample text is cleared.** A layout's footer or other slot that carries bracketed sample text (`<Customize with ...>`) or a "Click to add" line is cleared at finalize when the design supplies no text for it (real text is kept). It used to ship on every slide (2026-10-08). slide-qc's hygiene check flags any such line left on a slide as Critical.

**Pictures and charts survive finalize and assembly.** Both copy steps carry a shape's files with it: pictures (also inside groups), logos, charts with their workbooks, media and links (`twins/composer.py` `copy_shape_with_parts`). They used to copy only the shape, so a page with a photo or a chart made compile refuse the whole deck with a message about an edit "outside the pipeline" (2026-10-08).

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

N parallel agents per deck, **the option count per slide comes from settings: 1 out of the box** (`settings.json::options_per_slide`; one computer can set 3 in its own `slide-builder/settings.local.json`, never published). Three only when the user asks in chat (`--options 3` for those slides) or clicks **+3 designs** on a slide's card in REVIEW.html; do not ask. Never tell a worker a different count than its `_prompt.md` says. The per-slide prompt injects the option count + the 14-pattern reference + 5 hardline rules + anti-pattern library.

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
                          edited or partial list is refused). Picks the user
                          TYPES in chat with the page open (--open) are
                          recorded too: record_picks.py --approved-in-chat
                          "<their words>" --picks "1BC 2A". Nothing else
                          records picks. A Replace request is a new design
                          round: build_deck.py --slide N, then review again.
                          A pick with comments is edited in place first
                          (EDIT MODE worker, record_picks --edits-done),
                          then converted; picks carry over to the next page.

STAGE 3.5 · TRANSLATE     (picked sketch options only) Unpicked sketches are
                          never converted: that is where the token saving is.
                          settings.json "translator" decides who converts:
                          "agent": one slide-builder-translator per PICKED
                            sketch option, at most 20 at a time;
                            record_picks.py prints the list.
                          "script": record_picks.py runs translate_html.py on
                            every pick itself (seconds, no agent), renders the
                            result once and compares each element with the
                            design. Only what it can't draw (curves, web or
                            filtered pictures, rotated text) or what came out looking different
                            goes to the agent in FALLBACK MODE; record_picks
                            lists those, usually none.

STAGE 4 · FINALIZE        finalize_deck.py again. Executes option_X.py (direct)
                          and option_X_native.py (translated sketches), grafts
                          each onto its layout, themes, renders, and records a
                          QC result per option. Picks survive a re-finalize.

STAGE 4.5 · FINAL CHECK   build_review.py --final -> FINAL-CHECK.html
   (HUMAN GATE)           Every pick, finished, on the template: the real
                          title, takeaway and page number the sketches did not
                          have. SHOW it (--open) and WAIT. Its "Build it"
                          command carries the final token, bound to the bytes
                          of every file shown. Any later finalize clears it.
                          A "build it" the user types in chat while it is open
                          counts too (compile --approved-in-chat "<words>").

STAGE 5 · COMPILE         compile_picks.py --out <out> --final-token <t>
                          (or --approved-in-chat "<the user's words>")
                          Picks come from the recorded approval, never a file.
                          REFUSES (exit 5) without the token, if any shown file
                          changed, if any slide is unpicked, or if any shipped
                          option has a blocking QC finding.
```

### Classifier — not a classifier, just a hint + tiebreaker

The agent picks the split per slide directly from the brief content. There is no pre-classifier that takes the decision away from the agent. Two light layers help it instead:

1. **Prep-time pattern-hint pass.** `build_deck.py` runs the **same signals table from `reference/layouts.md`** once per slide to forecast each slide's likely pattern. No new classifier logic — this IS the agent's picking procedure, run once at prep time as a forecast. The forecast feeds `dispatch_plan.md` only; it is **not** given to the designers (the forecasts were stale, and most came out "Full canvas"), so designers are told not to guess their neighbors' picks.
2. **Pattern-pick seed.** When multiple patterns score equally on the agent's own scoring pass, the seed picks among them deterministically:
   ```
   pattern_pick_seed = md5(content_hash + slide_n)
   variant_seed      = md5(content_hash + slide_n + option_letter)
   content_hash      = md5(governing_thought + so_what + evidence_content)
   ```
   `content_hash` is locked in `build_deck.py` at prep time. Per-option variant seeds (one per requested `option_letter`) ensure sibling options — when more than one is generated — pick different variants within the chosen pattern. Without `option_letter` in the seed, all siblings would pick the same variant — that was a real bug caught by the architecture review.

Adjacency (Hardline #3 — no 3+ consecutive same-split) is **surfaced post-build** by `build_review.py` (advisory section in `REVIEW.html`). On sketch decks the review page also counts the **visual form** each sketch declares (`data-visual-form` on its canvas: cards, table, chart, flow, ...) and shows a deck-level "Many pages look alike" warning when one form is on at least half of the pages or on three neighbors in a row; a sketch with no form is listed as unknown. Split names cannot see sameness (cards and tables both sit under "Full canvas"), which is how a deck of nearly all cards reached the user (2026-10-08). Before showing the review, look at the forms strip; if it warns, tell the user. The user resolves the run by picking a different option for one of the offending slides at compile time, or by re-dispatching the slide with a different forecasted pattern. Brief fidelity (Hardline #4) wins over adjacency at pick time — the agent does not bend its pattern pick to satisfy adjacency.

### Why this flow wins

1. **The primitive matches human perception.** A human can identify a 50/50 vertical split or a 3-column row from a thumbnail in under a second — far faster than recalling what a named semantic layout means.
2. **Quality is a 3-layer stack.** Helpers cover geometry (`twins/helpers.py`), 5 hardline rules cover process, and a self-improving anti-pattern library at `reference/anti-patterns.md` covers aesthetics. Every curator-flagged failure becomes a permanent library entry.
3. **No fabrication.** SKELETON_REJECTED fires when brief and assigned split fundamentally disagree (brief enumerates 2 items, classifier assigned a 4-cell layout). The slide is not built rather than invented to fit.

---

## What this skill does

1. **Setup.** Use the brief's `client_template:` (the user picked it at the start and confirmed it with the storyline); ask only if the brief has none. Read the brief and explicitly read the `## Deck-level design notes` section before proceeding; those constraints are binding. Prep also reads them under common variant headings ("Deck rules", "Deck-wide content rules", "Section content rules (binding on every page)", any heading with "design notes"). Each slide's `**Source:**` line and `**Section tag:**` reach the designer's `_prompt.md` / `_context.md` and `_meta.json` (`source`, `section_tag`). **Prep prints `WARNING (brief):` for every `##` section and every slide field it does not read** (and repeats them at the end of its output): fix the brief or tell the user what is being left out, never let it drop silently.
2. **Narrative + content gates.** Verify governing thoughts are specific and assertive; verify enough raw content per slide. Skip if storyline-helper already gated this session.
3. **Stage 1 — Prep.** Run `build_deck.py` to render one self-contained `_prompt.md` per slide. Each prompt is `prompt.md` with brief content interpolated, layouts/anti-patterns reference paths injected, the rotation seed computed, and the per-slide pattern routing (`PATTERN: sketch|direct`) from the classifier.
4. **Stage 2 — Parallel fanout.** Dispatch one `slide-builder-worker` agent per slide IN PARALLEL from the parent session. **At most 20 agents at a time** — `dispatch_plan.md` lists the waves when the deck is bigger than that. Dispatches past the limit are rejected, and the rejection is quiet: on one 29-slide deck about 20 of them vanished and `finalize_deck.py` exited 11 with slides 23-29 missing. The same limit applies to the Stage 3.5 translator fan-out, which is one agent per picked slide-option and so can be several times the slide count. Each agent reads the rendered `_prompt.md` and branches on the PATTERN field:
   - **the sketch path** (default): worker produces the requested option HTML file(s) (`option_A.html`, plus `B`/`C` only when the count > 1), then self-checks by rendering each via `scripts/render_html.py` and reading the resulting 1280×720 PNG before declaring done.
   - **the direct path**: worker produces the requested option script(s) (`option_A.py`, plus `B`/`C` only when the count > 1).
5. **Stage 2.5 — HTML render (sketch-path only).** For each the sketch-path slide's HTML options, the parent session renders to `option_X.sketch.png` via `py -3 scripts/render_html.py <html> <slide_NN/option_X.sketch.png>` so REVIEW.html has visual previews. Workers may also do this as part of their self-check; the parent renders any not-yet-rendered as a safety net. The render adds the slide's `_chrome.css` (written by prep from the values finalize uses) last, so every picture shows the template's real title, takeaway and section tag whatever the design's CSS says; the HTML is not changed. The review card shows a Major note for a title of 3 or more lines (`TITLE_TOO_LONG`) or a body shape under the title or takeaway (`BODY_UNDER_CHROME`), checked against the template, not against other pages (2026-10-13). Library icons (`<i data-icon-name>`) are drawn from the shipped previews in `icons/svg/` in the designer's color, and the translator puts the real vector icon on the finished slide. Designers use only names from `icons/checked-icons.json` (about half the other names do not match their pictures); an unknown name prints `ICON_UNKNOWN` and shows a labeled placeholder, and the review card lists it.
6. **Stage 2.6 + 3 — Finalize, then review (a HUMAN gate — stop and wait).** First tell the user, in one line, that PowerPoint may pause for a few seconds while Slide Lab renders slides and that editing in PowerPoint meanwhile slows the build (Windows with PowerPoint). Run `finalize_deck.py` (puts direct-path options on the template; sketch options wait for a pick), then `build_review.py --open` (it opens the page in the user's browser and prints the path). **Tell the user it is open and WAIT.** Never write picks yourself and never treat the review as a formality.
   - **Every slide needs a decision.** The page's Build my deck button does nothing until each slide is picked, marked **Replace these**, or marked **Leave out**. Leaving a slide out is only ever the user's choice on this page; compile no longer has a flag for it. One option per slide is still not an auto-pick.
   - **Do not review a half-rendered deck.** If the page says options have no preview, finish rendering first. A review the user cannot see is not a review.
   - **The user pastes a plain message** from the page: `Build my Slide Lab deck.` / `Folder: <out>` / `Picks: 1B 2C 3A ... (check 1a2b3c4d)`, often followed by a `Feedback:` block (the quick-feedback chips and notes per slide). Run `record_picks.py --out <Folder> --approved "<the WHOLE message, exactly as pasted>"` so the Feedback block is read too. It verifies the picks against the check code computed in the page and refuses an edited, partial or stale list. It is the only way picks get recorded; do not write `picks.json` by hand.
   - **Comments on a pick are applied before conversion** (owner's decision, 2026-10-09). `record_picks.py` reads the Feedback block (in chat: pass each comment the user typed as `--comment "N: <their words>"`; it must appear in their words). A picked slide with comments is recorded **edit first** and is NOT converted; the other picks are. It writes `slide_NN/_edit_request.md` and prints the list. Dispatch one `slide-builder-worker` per such slide in **EDIT MODE** on that file (it edits the PICKED design in place: same layout, the comments applied, option letter unchanged), re-render each edited sketch, then run `record_picks.py --out <out> --edits-done`: it refuses a slide whose design did not change or whose option letters changed, marks the comments applied, keeps the picks, converts the edited picks together in one call, and prints the finalize / final-check steps. Never apply comments by hand after conversion (the slide was converted twice and agent-drawn parts were redone). A comment that asks for a different design (the **Wrong layout / structure** chip, "try a chart instead", "a different layout") is a **Replace request**: `record_picks.py` drops that pick, writes the comment to `slide_NN/_prior_feedback.md` and records the redesign round itself (no `redesign_round.py start`). It gets **one new design; do not ask** (owner's decision, 2026-10-13): `build_deck.py --slide N` (add `--options 3` only when the user asked for three in their words), its worker, the sketch render; with three, `build_review.py --open` (every other pick is preselected) and the user picks; with one, `redesign_round.py finish` (after `--edits-done` when slides also wait on edits; finish refuses until then). A comment on a slide the user left out is recorded as not needed. Every comment is in the build record with how it was applied; the final check refuses while one is pending, and `check_done.py` lists them all at delivery (and refuses a deck with one never applied).
   - **Parent direct edit (owner's decisions, 2026-10-09 and 2026-10-13).** When the change is only a color, a font size, or wording the user gave word for word, you may make it yourself instead of dispatching a worker, on a **direct-path** page (edit the picked `option_X.py`) or a **sketch** page (edit the picked `option_X.html`): same layout, same letter, only what the user said. Name colors by their brand color name from `_context.md` (never a raw hex). Any new number or claim is not this kind of edit: ask the user. Record it with `record_picks.py --out <out> --edits-done --edited-by-parent "N: <what changed>"` (repeat per slide you edited; slides a worker edited need no flag). It works with or without a comment waiting (an edit the user asked for in chat): it refuses a slide whose picked design did not change, converts every picked sketch design that changed since it was converted (`translate_html.refresh_stale`, below), and prints the next steps; with nothing changed it says so. After finalize, look at the slide's new picture and confirm the change shows as asked (colors told apart, text fits) before the final check. Never hand-edit `option_X_native.py` (not even its `__template_fields__` header: the conversion rewrites it), and any layout change goes to a worker. `check_done.py` lists every such edit at delivery as "edited by parent".
   - **A design edited after it was converted reaches the deck (2026-10-13).** The conversion records each design's fingerprint. `record_picks.py` (picks and `--edits-done`) and `finalize_deck.py` convert again every picked sketch design that changed since, by themselves: when it converts the same, or only the title or takeaway text changed, the script is kept (header updated); when the body changed and the translator agent drew nothing, it is replaced; when the agent drew, its drawing is kept only if every element it draws is unchanged (same elements, same HTML, box and picture bytes) and the script still runs, else the option waits on the agent again (FALLBACK MODE) with the old drawing pasted in as comments to adapt, and finalize stops with that step. The old script is copied to `slide_NN/_prev_translation/<time>/` first, every time. A hand run of `translate_html.py --slide` over a script the agent drew in is refused unless `--force`. Compile refuses an option whose design changed after finalize built it, naming the slide and the finalize command.
   - **The page keeps picks between rounds.** Each slide's stamp covers only the designer's files (`option_X.html` / `option_X.py`), so converting a pick no longer makes it look changed. Picks recorded by `record_picks.py` are written into the next REVIEW.html and preselected (in any browser) while that slide's designs are unchanged, with a small "Kept from last round" mark; a slide edited in place from comments keeps its pick ("edited from your comments") and its applied comments are cleared; a redesigned slide starts with no pick and no comments; comments on untouched slides stay. A pick never lands on a slide whose designs changed under it, except that edit in place, which keeps the letter.
   - **Or the user types the picks in chat** with the page open ("use 1A 2C", "build B and C"; the owner's decision D2, 2026-10-06). Run `record_picks.py --out <out> --approved-in-chat "<the user's words, verbatim>" --picks "1A 2C"`. It counts only when this build's REVIEW.html was opened with `build_review.py --open` and no slide's options changed since (otherwise it refuses: run `build_review.py --open` again and let the user look). Every letter in `--picks` must appear in the user's words, so write down what they said, never what you think they meant; if they did not name a letter for a slide, ask. The words are recorded with the page's token and file stamps, and `check_done.py` lists them at delivery as a chat approval. Never read the check code from the page instead.
   - **Several options of one slide** ("B and C of slide 1, not A"): the pick names several letters, `Picks: 1BC 2A (check ...)` (canonical `slide_01=BC;slide_02=A`), or `--picks "1BC 2A"` in chat. It is recorded as the user's choice and compiled as a labeled all-options deck of exactly the kept options: nothing is moved aside and finalize needs no `--allow-missing`. Do not move option files to `_prev` to drop one.
   - **Replace these** means a new design round for that slide. The page's message lists the slides to redesign and, when other slides are already picked, a `Keep: 1B 3A ... (check ...)` line. First record those: `redesign_round.py start --out <out> --slides N[,M] --kept "<the Keep line>"` (omit `--kept` if there is none). Each slide gets ONE new design; a slide the user clicked **+3 DESIGNS** on (the message's `Three designs for:` line), or asked three for in chat, goes in `--three N`, and `build_deck.py --slide N` then builds three for it (the message itself spells out the start command). Then for each slide `build_deck.py --slide N` (the old options move to `slide_NN/_prev/`), its worker, and the sketch render. Then `redesign_round.py finish --out <out>`: with one new design per slide it picks them, converts, finalizes and opens FINAL-CHECK.html directly (no second picking page; the final check is still required). Like `apply_qc_fix.py`, it converts a design only when it changed since its last conversion, so after an exit 3 and the translator agent's FALLBACK MODE run, `finish` again keeps what the agent drew. If the user asked for alternatives (several options), finish refuses: build REVIEW.html again with `--open` and let them pick. A rebuild designs **one** option (`settings.json::options_per_slide_revision`), because the user has already said what to change and three options tripled the wait; put the user's direction in `slide_NN/_prior_feedback.md` so the worker sees it. Use `--options 3` when the user asks for alternatives again.
   - **"All options in one deck"** is a separate button on the page. Its first click puts a **Kept in the all-options deck** switch on every option (all kept); the user switches off the ones to leave out and clicks again, and the page copies `Picks: 1BC 2A ... (check ...)` with the kept letters (run it like any Picks line). It converts every kept option, not just one pick per slide, so it costs several times the tokens; the page says so before sending. If the user asks for this in chat ("accept all", "put them all in a deck"), ask first: *"All options in one deck, or option A for every slide?"* Reading it the wrong way once cost 58 extra worker runs.
7. **Stage 3.5 — Translate the picked sketches only.** Unpicked sketches are never converted, and a pick with comments is converted only after its edit (`record_picks.py --edits-done` converts all edited picks in one call, so the self-check renders them in one pass). Who converts depends on `settings.json::translator`:
   - `"agent"`: `record_picks.py` prints the list. Dispatch one `slide-builder-translator` per picked sketch option (at most 20 at a time). It reads `option_X.html` + `option_X.sketch.png` + brief + brand context and writes `option_X_native.py` + `option_X_translation_report.json`.
   - `"script"`: `record_picks.py` has already run `scripts/translate_html.py` on every pick and written the same files (plus `option_X_native.plan.json`, the drawing plan). It then rendered the result and compared every element with the design (`scripts/translate_alarm.py`). Elements it can't draw, and elements that came out looking different, are listed in the report's `fallback` and in `record_picks`' output; dispatch the translator in **FALLBACK MODE** on just those options. It draws only the listed elements. Finalize refuses an option whose `option_X_native.py` still starts with `# FALLBACK_PENDING`. Converting a design again keeps what the agent drew only while every element it draws is unchanged (see "A design edited after it was converted" above).
   - Two conversion rules: text at weight 600 or more (800 and 900 too) becomes the base font with bold on. PowerPoint only has bold on or off, and naming the heavy face instead (Arial Black, a brand "Semibold") did not survive finalize's theme font swap, so it shipped regular; the theme swap now also keeps bold on any heavy face name it replaces. When one family is registered for both heading and body (and the theme's heading face is its bold face), text in that family binds to the body font, so body text stays regular; it used to bind to the heading font and every body box came out bold (2026-10-08). On a layout with no subtitle slot the takeaway is drawn as a text box named `subtitle` (on purpose, see the translator's rules); finalize then places it by the chrome rule above.
   - **Text is placed where PowerPoint draws it (2026-10-09).** The converter writes line spacing in whole points (PowerPoint rounds it anyway) and sets each text box's top from PowerPoint's measured rule for the first line (`translate_html.ppt_first_baseline`); a one-line text box gets spacing 0.8 x its size, where PowerPoint and LibreOffice agree. The self-check renders with the default renderer (PowerPoint on Windows); on LibreOffice it expects text on several lines a little lower (by LibreOffice's own rule), so it does not flag that. Gradients get in-between stops so PowerPoint blends them like the browser.
   - **Box growth (owner's rule, 2026-10-08).** To keep text off a filled box's bottom (or right) edge, the converter grows the box a few px, but only into empty space, keeping a 2 px gap to the next shape, and leaves it at its design size when there is no room. It does this after the self-check, so the check compares the design as drawn. It used to grow every such box before the check, so thin stacked boxes grew into each other and nearly every one was sent to the agent.
   - **Fonts are the installed ones.** The browser that draws the review picture and reads the design for conversion (`scripts/_browser.py`) removes any `@font-face` rule that points a font installed on this computer at a font file, and prints a warning (`FONT_FACE_REMOVED` in the report). A designer once pointed the brand family at a copied file holding its narrow face, so the approved picture was narrower than the finished slide. When the self-check finds every text in one font wider or narrower by the same ratio, `RENDER_FONT_RATIO` says so: with the font installed, "the design was drawn in a different version of this font; the finished text runs N% wider" (a design issue to check for overflow); with the font missing, the check used a stand-in and text size was not judged.
   - **Converter round of 2026-10-13.** Photos from files are native pictures (cropped and shaped as the design shows them: an oval for a 50% radius); pictures from a web address, filtered, see-through, bordered, clipped by their container or inside a table or list still go to the agent. A straight line with a plain triangle marker is a line with a PowerPoint arrowhead in its place in the stacking order (a head far bigger than PowerPoint's largest is a filled triangle); other markers go to the agent. The self-check leaves out the areas the agent draws (a photo on a card no longer makes the card look wrong) and judges thin letters by their color, not their strength. Elements the agent draws keep their place in the design's stacking order: the generated `option_X_native.py` calls `html_emit.restack_fallbacks` after the agent's block, which moves shapes named `<element id>` or `<element id>-N` there and stops the script when a new shape is named after no element. List bullets are read from the marker itself (60-200% of the text size, inside its panel, else the browser's marker with `BULLET_FALLBACK`). The line-break prediction breaks after hyphens between letters and after en/em dashes, and text is never shrunk a size to keep its lines: when widening 6% is not enough it keeps its size with `WRAP_RISK` (Major on the review page; check that text on the finished slide). Top-anchored text boxes get a top inset (`pad_top_px`) so their capitals sit inside the box when selected; the text does not move. `TEXT_ABOVE_FRAME` is the advisory for a box whose capitals still stick out.
   - A canvas painted with the layout's own background (`--slide-canvas-bg` from `_context.md`) is left to the template, not drawn as a full-slide rectangle over the master's artwork. Two design checks go into the translation report and onto the review page: `MAJOR_ARROW_END_AT_BOX` (an arrowhead inside a box or within 6 px of one; `scripts/arrow_ends.py`) and the advisory `PALE_FILL_ON_BACKGROUND` (a large panel within a few shades of what is behind it). In FALLBACK MODE the translator agent renders its self-check with `scripts/selfcheck_render.py`, which uses a folder per option (two options of one slide used to share one picture) and runs the same arrow check on what it drew.
8. **Stage 4 — Finalize again.** Give the one-line PowerPoint notice first (it renders, and so does Stage 3.5's converter self-check). `finalize_deck.py` first converts again any picked sketch design that changed since it was converted (it stops only when the translator agent's drawing would change), then executes `option_X.py` (direct) and `option_X_native.py` (translated sketches), grafts each onto its layout, themes, renders, and records a QC result per option. All of a run's options are rendered as one deck and split back per option; one that fails to render is marked failed with its own reason while the others render. Recorded picks survive it. A source line on a layout with no footer slot (the template's source slot is an ordinary text box, or there is none) is drawn as a text box at the template's source position and finalize prints a `WARN: slide N: layout ... has no footer slot for the source line` line; check it on the final-check page (it used to be dropped silently). A render that fails is retried once automatically (LibreOffice with a fresh profile and from a local copy, always from a local copy when the deck sits in a OneDrive folder); after two failures the other program takes over when it is installed. When everything fails, finalize prints the whole error, not its first 50 characters.
9. **Stage 4.5 — Final check (a HUMAN gate — stop and wait).** `build_review.py --out <out> --final` writes `FINAL-CHECK.html`: every pick, finished, on the template, with the real title, takeaway and page number the sketches did not have. This is where a collision with the template becomes visible. It refuses if any pick is unfinished or blocked. Its pictures are finalize's PowerPoint renders (on Windows with PowerPoint), so the page shows what PowerPoint will show; if finalize must run again first, give the one-line PowerPoint notice. Run it with `--open`. **Tell the user it is open and WAIT** for the message its Build it button copies (`Build it: I checked the finished slides.` / `Folder: <out>` / `Final check: <token>`, plus `Deck: all options, labeled` or `Put back into: <file>` when they apply), or for the user to say "build it" in chat (step 10). If finalize printed `REFUSED (exit N)`, nothing new was built: the option pictures on disk are from an earlier run, so do not show or send them; fix the reason first. When finalize says options are **waiting on the translator agent**, it names them and the next step (with no picks recorded yet: record the picks first, then the agent).
10. **Stage 5 — Compile.** From that message run `compile_picks.py --out <Folder> --final-token <token>`, adding `--all-variations --badge` when it says `Deck: all options, labeled` (the 9 pt "Option B" label `--badge` stamps, shape `chrome-option-badge`, is Slide Lab's own review labeling: slide-qc's text-size check skips it, so it is neither under the floor nor an extra size) and `--splice-into "<file>"` when it says `Put back into: <file>`. Picks come from the recorded approval. It refuses if any file shown in the final check has changed since, if any picked design changed after finalize built it (it names the slides and the finalize command), if any slide has no pick, or if any shipped option has a blocking finding. Never invent the token, and never read it from the page. Before it replaces the previous deck, compile opens the saved file in PowerPoint itself (read-only, no window): a file PowerPoint refuses or asks to repair, or opens with a different slide count, is refused and kept as `final_deck.REJECTED.pptx`; COMPILED.md records "Opens in PowerPoint". On a computer without PowerPoint it says the check did not run.
    **"Build it" typed in chat** (the owner's decision D1, 2026-10-06) counts as the click, but only while FINAL-CHECK.html is open for the current files: run `compile_picks.py --out <out> --approved-in-chat "<the user's words, verbatim>"` instead of `--final-token` (it takes the all-options flags from the recorded picks; add `--splice-into` for an adopted deck). It refuses when the page was not opened with `build_review.py --final --open`, when a finalize ran after it was opened, or when a finished file changed since; then open the current page again and let the user look. The words are recorded with the page's token and file digests, and `check_done.py` lists them at delivery as a chat approval.
11. **QC — mandatory, not optional.** Give the one-line PowerPoint notice first (slide-qc renders through PowerPoint on Windows). Invoke slide-qc with an explicit Skill call, passing the compiled deck path so it doesn't re-discover it — `Skill tool call: skill="slide-qc", args="<absolute path to the deck compile printed as Deck:>"` (the deck is named after the topic; `_state.compiled_deck(out)` resolves it). This is the definition of done: do not tell the user the deck is finished or "QC'd" until slide-qc has run and produced its report. A PDF you rendered and eyeballed is not QC — the agent that built the deck cannot grade its own output. (compile_picks.py also prints this reminder when it finishes.)
    **Automatic fixes first, without asking** (owner's decision, 2026-10-09). Every Critical and every Major in the layout/format group is fixed automatically: text under the size floor or more than 3 body sizes, overflow or clipping, overlap, an arrow into a box, a panel vanishing on the background, chrome drift or a misplaced takeaway / footnote / source line, template sample text, a missing footer or page number, an axis without a unit, color palette drift, a text item ending with a final period, a chart without its "Chart title, Unit" header line (or with the unit in brackets), a legend not one row at the chart's top right (the last three are the owner's rules of 2026-10-09, checked by `scripts/chart_rules.py`; finalize already removes final periods and lists each in RESULT.md and COMPILED.md). Majors in the content group (a number or label not in the brief, buzzwords or hedging, a headline that is not a fact or is a topic label, bullets not parallel, a missing source where one was expected, anything that rewrites words or numbers) still go to the user. `scripts/qc_fix_policy.py` is the one place that says which (`--list` prints it; slide-qc tags each finding with its key). A content finding is asked even when it is marked Critical. Write each finding `slide N [key] Severity: text`: the severity is read only from its place after the tag (the word "critical" elsewhere in the text means nothing), the tag only from its place after the slide number (hyphens work: `[text-size]`, `[template-sample-text]`), and findings are split only where `;` or a new line is followed by `slide N` (fix detail after a `;` stays with its finding). A finding with no tag or a tag that is not a key is never automatic, a layout tag on text that reads like content is asked, and `--auto` refuses a finding for a slide not in `--slides`. The loop: QC report, then for the automatic findings `apply_qc_fix.py --out <out> --slides N[,M] --snapshot` (keeps each slide's current design and the deck for an undo), the rebuild of only those slides with one design each (`build_deck.py --slide N` with the finding in `_prior_feedback.md`, or the in-place edit of the kept option), then `apply_qc_fix.py --out <out> --slides N[,M] --auto "slide N [category] Severity: finding; ..."`. It keeps every other pick and agent-drawn part, refuses a content finding, refuses a slide with no snapshot, records the fix with its finding text (not as a user approval), compiles and prints before/after picture paths. Re-run slide-qc. **At most two automatic rounds** (a third is refused). Then send the user ONE message: what was fixed per slide (before/after picture paths), the content findings in one table with proposed fixes and one reply, and anything still open. "Undo slide N": `apply_qc_fix.py --out <out> --undo N --approved "<their words>"` restores that slide's design from before its fix and compiles the deck again; the kept versions stay until delivery. `check_done.py` lists every automatic fix at delivery as "fixed automatically", with its findings and any undo.
    **When the user approves QC fixes ("fix it", "build it"), go straight to the deck.** Rebuild each flagged slide with one option (`build_deck.py --slide N`, the finding in `slide_NN/_prior_feedback.md`, one worker), then run `py -3 scripts/apply_qc_fix.py --out <out> --slides N[,M] --approved "<the user's words>"`. It keeps every other pick, converts and finalizes the fixed slides, writes the final-check record, compiles, and records the user's words (check_done lists it at delivery). It converts a fixed sketch only when its design changed since the last conversion, and keeps what the translator agent drew when no element it draws changed: if it exits 3 (part of the new design needs the agent; a drawing it must adapt is pasted in), run the agent in FALLBACK MODE and then the same command again; the slide the agent finished is kept as is, its drawing included (it used to be converted again, erasing the drawing and exiting 3 for ever). Do not send the user back to REVIEW.html or FINAL-CHECK.html for a fix they already approved; re-run slide-qc on the new deck. **A color, a font size, or the user's exact wording** needs no worker and no rebuild: edit the picked `option_X.py` (direct-path page) or `option_X.html` (sketch page, since 2026-10-13; it is converted again) in place yourself (brand color names, not hex; a new number or claim goes back to the user; layout changes still go to a worker), then `apply_qc_fix.py --out <out> --slides N --approved "<the user's words>" --edited-by-parent "<what changed>"`. It records the edit, compiles, and prints the new pictures: look at each and confirm the change shows as asked and the colors can be told apart. `check_done.py` lists it at delivery as "edited by parent". apply_qc_fix also refuses any fix while a slide NOT being fixed got a new design after the last compile that nobody picked (`slide_NN/_prev/` newer than the compile), since the compile would ship it unseen: finish that slide first, or name it in `--slides` if it is one of the fixed ones.
    **On a slide where the user kept several options** (an all-options deck, or `Picks: 1BC`), do not run `build_deck.py --slide N`: it moves every option of the slide aside. Put the finding in `slide_NN/_prior_feedback.md` and re-dispatch the worker on that slide's `_prompt.md` for the flagged option only, telling it the letter, so it rewrites `option_B.html` (or `option_B.py`) in place. Then `apply_qc_fix.py --out <out> --slides 1B --approved "<the user's words>"` (`1BC` when both were fixed). Only the named options are converted again; the slide's other kept options stay as they are and stay in the deck, and the labeled all-options deck is compiled again. A plain `--slides 1` on such a slide is refused (say which option), and so is a letter the user did not keep. It still needs a first compile.
    **A slide keeping ONE of several designs** (an all-options deck where the user kept only A, with B and C still on disk) is fixed by editing the kept design in place (the worker, or you for a direct-path color / size / exact-wording edit). Then `apply_qc_fix.py --out <out> --slides 1 --approved "<the user's words>"` (or `1A`): it converts A only and leaves the slide's pick as it is, so B and C stay out of the deck. It is refused for a letter the user did not keep, and when another option of that slide was designed after the last compile (a new alternative the user has not seen: they pick it in REVIEW.html). Unpicked options are not removed at compile on an all-options deck.
12. **Prove it's done — `check_done.py`.** "Done" is no longer something the orchestrator may assert. Run:
    ```powershell
    py -3 scripts/check_done.py --out <out>
    ```
    It checks one chain of recorded facts and exits non-zero if any link breaks: a compile **succeeded** and recorded its output; the deck is **that file, byte for byte** (no edits since); it was built from the **current** brief; it opens with nothing PowerPoint refuses; every option in it finalized with **zero** blocking findings; **every page was reviewed as it looks in the current render of those same bytes**, with a deck-wide look recorded for them (slide-qc records each round via `qc_pages.py plan` and `record_vision_qc.py`, with proof each page's picture was opened; unchanged pages carry their review and open findings forward); and **no Critical or Major finding is open** (only Advisory may remain). The deterministic self-check does not count: it is structurally blind to shapes overlapping and to large empty areas, which is exactly the class that has shipped before. Do not tell the user the deck is finished until this passes.
    It also lists every gate passed over in the build (`--assume-gated`, `--allow-unconfirmed`, `--allow-missing`, a `mode:` line that skipped the storyline gate). **Tell the user about each one when you deliver.** It refuses a deck that is older than the latest rebuild or finalize.
13. **Deliver.** Give the full path of the deck named after its topic (compile prints it as `deck to share:`). It is the only deck at the top of the folder: compile writes it once under the topic (`final_deck.pptx` only when the brief has no title), records the path for check_done and slide-qc, keeps just the latest previous version in `_session/old-decks/`, and removes `final_deck.REJECTED.pptx` once a newer compile passes. After a successful compile it also removes render scratch folders and the options the user did not pick (an all-options comparison deck keeps every option), and prints the folder size before and after. No preview links. Add any overrides `check_done.py` listed, in plain words, and its `chat approvals` lines (picks, the final check or a QC fix the user approved by typing in chat; they are approvals, not gates passed over, but the user should know which steps were approved in chat rather than on the page), its `comments` lines (each review-page comment and how it was applied) and its `fixed automatically` lines (each automatic QC fix with its findings, and any undo).
14. **When the user says the deck is good** ("looks good", "approved", "final", "ship it", "publish it"), free the build files it no longer needs:
    ```powershell
    py -3 scripts/publish_cleanup.py --out <out>
    ```
    It also deletes the session's scratch folder under `C:\Temp\slidelab\` (the dry run lists it with its size). For "clean up my finished decks", `--scan <folder>` lists the decks and `--temp` lists Slide Lab scratch folders not changed for 7 days, with sizes; delete only the ones the user names (`--temp --delete "<name>" ...`, or `--temp --all-listed` when they say all of them). Folders in use are skipped and the output says so.
    It keeps the deck, the final-check page, the storyline, the brief, decisions and the user's own files in `_session/`, the deck's records, and per slide only what a rebuild needs: the picked option's design and script (`option_X.html`, `option_X.py` or `option_X_native.py`, its `.plan.json` and translation report), its pictures in `img/`, any file the kept script names, and `_prior_feedback.md`. It deletes everything else: unpicked options, every image and per-option PowerPoint file, `_prompt.md` and `_context.md` (`build_deck.py --slide N` writes them again), the quality-check render folders (`_qc*`, written notes in them are kept), final page images, replaced options, `_session/old-decks/` and a rejected deck (typically about 90% of the folder). Tell the user how much it freed. The deck can still be edited later: a rebuild or insert works as usual, and the next finalize regenerates the images and files from the kept designs. Run it only on that say-so, never on your own judgment that the deck is finished; `--dry-run` shows what would go without deleting. For decks finished earlier, `--scan <sessions folder>` lists every finished deck with the space it would free; the user picks which to clean.

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

1. **Pin it** so it cannot be quietly dropped: in the brief's slide block, add `**Pinned source page:** <path to the supplied file> slide N` (a path next to the brief is fine). For a whole earlier deck, `map_source_pages.py` proposes the pins for every slide in one list for one answer and writes these lines once the user approves (see "The user's rulings, the page map and the context pack"). Any number of slides can be pinned, to pages of several files. Prep records each pin in `_meta.json`, prints a note naming the pinned slides (it does not stop), the worker is told that **option A reproduces that page** (structure, sections, wording, on the client template), and the review page labels the slide.
2. **Nothing to run by hand.** Once the user has picked, `finalize_deck.py` checks every pinned slide against its **picked, finished design** (`source_ledger.py build --all-picked`, one section per slide in `source_ledger.json`). It lists only the figures that are on **both** the copied page and the picked design: a figure the design dropped is not asked about; slide numbers, Source/Note lines, footers, dates and years are skipped; a figure that also appears in the brief word for word is **counted** ("12 match the brief"), not listed, and never answered automatically. It reads table cells, grouped shapes and chart labels, and lists in `unreachable` what it cannot read (numerals in a picture, SmartArt, think-cell/OLE) for the vision pass.
3. **The user answers on FINAL-CHECK.html.** One table, "Numbers copied from your pages": slide, the figure, where it was on the copied page, the closest brief line, and Keep / Replace. **Build it** stays shut until every row is answered; a Replace turns the message into a fix request (edit the slide, finalize, final check again). Their approval of that final check (Build it, or "build it" in chat with the page open) answers every row the table showed: compile records each as kept on the final check. Do not ask the user about rows one by one in chat, and do not type answers into the file for them.
4. **Every pinned slide is checked.** `compile_picks.py` (exit 5) and `check_done.py` refuse while any pinned slide that ships has no section, a section made from another design than the one picked now, or a figure not answered, and they name the slides and give the one command (`source_ledger.py build --out <out> --all-picked`, then `build_review.py --final --open`). `check_done.py` lists per slide how many figures were kept, how many matched the brief and how many surfaces were unreadable. **Never remove a pin to get past the check**, and never drop one automatically after a redesign: a redesign that keeps none of the copied figures simply has no rows.

> **Why a ledger and not an automatic check.** A differ would compare each figure against the brief and pass or fail. It cannot: the brief carries prose, not typed numbers, so deciding that "6-12 months" and "sold out" denote the same quantity is a judgment the machine does not own. A check reporting "0 conflicts" would assert exactly that judgment and the pipeline would consume it as fact. The machine records only what it knows: **this figure came from the copied page onto the slide that ships, and a human has or has not answered for it.** Unreadable surfaces are referred to the slide-qc vision pass, which reads a rendered image and is the only gate that can see them.

> **If the supplied page is a PDF or a picture** (a screenshot, a scan), pin it the same way (N = the PDF page; a picture needs no number).
>
> - **A PDF page with a text layer** (exported from PowerPoint or Word, not scanned) is read like a PowerPoint page: its figures that came through onto the picked design go into the same table. Pictures on that page are listed in `unreachable` for the vision pass.
> - **A scanned PDF page or a picture** has nothing to read. Its section is honest: no rows (nothing on the page is claimed as checked), the whole page in `unreachable` as **checked by eye only**. slide-qc's vision pass covers that slide, and `check_done.py` says at delivery that the page was checked by eye only; tell the user. The worker is still told that option A reproduces the page, so its numbers can come through: take every figure from the brief, or confirm it with the user.
> - By hand, for one slide: `source_ledger.py build --out <out> --deck "<page>" --slide N --target-slide T` replaces only slide T's section.
>
> A Word page: save it as a PDF first (`build` refuses other file types with that advice).

**Insert a new slide** at position N with `build_deck.py --insert N`. First add the new slide to the brief at position N and renumber the later slide headers (the brief must have exactly one more slide than the current build). `--insert N` then shifts slides ≥ N up by one — their `slide_NN/` dirs, `_meta.json` entries, and `picks.json` keys — and preps only the new slide N; the shifted slides keep their built output under their new numbers. **How many designs:** a new slide gets the settings' count (`options_per_slide`, 1 out of the box); do not ask. Add `--options 3` only when the user asked for three. The count is frozen into `_meta.json` and the slide's `_prompt.md`, and the insert prints it: never tell a worker a different number than its `_prompt.md` says (one session told workers "option A only" and finalize then refused eight slides). To change it, prep the slide again with `build_deck.py --slide N --options 3` (or 1) before its worker runs. If Windows will not rename a slide folder (a program or File Explorer window is sitting in it), the insert tries again, then stops with nothing changed, lists the processes whose command line mentions the build folder, and asks: end nothing unless the user says yes to exactly those PIDs. Then dispatch one worker for slide N, run `finalize_deck.py --slide N`, and go through the same review sequence as a full build (steps 6-10): the shifted slides need a fresh look in the review page too, since their numbers changed. (Adding a page to an *external* `.pptx` Slide Lab didn't build is an existing-file edit — see "Edit an existing PowerPoint" below — not this flow; `--insert`/`--slide` only work on decks with the pipeline's `_meta.json`.)

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
- **The storyline panel on REVIEW.html shows the approved storyline as written** (owner's decision, 2026-10-13). The brief's front matter line `approved_storyline: <absolute path>` names it (emit_dot_dash.py writes it; for a prose storyline written by hand, add it yourself; the seal does not count that line), or `build_deck.py --storyline <file>`. Prep records its path, size, time and fingerprint in `_meta.json`; nothing is found by name. The page shows an .html or .md file inline (its own styles and scripts dropped), links a Word file, and prints one-line warnings: file missing, changed after prep, brief newer than it, a storyline headline worded differently on a slide (both wordings) or on no slide. With no pointer it shows the slide headlines only. `build_review.py` exits 6 without opening the page if the panel's text is not the file's text or carries "Supporting points:", an ALL CAPS designer label or an em-dash; fix the file (or the pointer) and run it again.

Master switch is `settings.json::enable_sketch` (shipped `true`). Set it to `false` to disable the sketch path entirely: `auto` and `sketch` are then downgraded to `legacy` with a stderr warning, and no slide renders through Chromium. The sketch path requires the Playwright Chromium binary (see INSTALL.md Step 1.5).

---

## Content reviews and number checks

Owner's decisions of 2026-10-14 (speed verdict Q2, decisions B and D). They matter most with three designs per slide; with one design (the default) the picked pages are all the pages.

1. **One fact check of the brief's numbers, before the designers start** (after prep, before Stage 2). One reviewer agent compares every figure in the brief (and the storyline it came from) with its source: the model, the research, the user's files. Number errors live in the text, so this catches each one once, instead of once in every option. Fix the brief (or ask the user), re-run prep if the brief changed, then dispatch the workers.
2. **The content committee runs after the picks, on the picked pages only.** Once `record_picks.py` has recorded the picks, the reviewers (the several agents that read the deck's content, wording and logic) read only each slide's picked option (`slide_NN/option_<pick>.sketch.png` or its render, and FINAL-CHECK.html), never the options the user did not pick. On the Leo deck 285 edits went into 134 fixes, and only 37% of them landed on the option that shipped. Give the reviewers the deck's rulings file (`_session\rulings.md`) so they do not reopen what the user settled.
3. **The number-check rounds on the finished deck stay on every page**, and each round is recorded so the second round can be measured:
   - before a round's checkers start: `py -3 scripts/number_check.py start --out <out> --round N`
   - after it: `py -3 scripts/number_check.py record --out <out> --round N --findings <file>` (one `slide N: issue` line per finding, or a JSON list). Every round-2 finding is tagged with whether its page changed since round 1 (page numbers ignored, so an inserted page does not make the later pages look changed); the script prints the tally, and `number_check.py tally --out <out>` shows every round.
   - After two decks: if no round-2 finding ever landed on an unchanged page, round 2 can move to the changed pages only (about 10-15M tokens a deck). That switch is the owner's decision; until then round 2 covers every page.

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

**Scratch files: one place.** Put any scratch files (copies, renders, checks) under C:\Temp\slidelab\<session>\ (scripts/_scratch.py); never invent new folders in C:\Temp. `py -3 scripts/_scratch.py --session "<session folder>"` prints (and makes) the session's folder; on a Mac it is the system temp folder plus `slidelab/`. Slide Lab's own scripts already put their temporary folders, browser profiles and LibreOffice profiles there and delete them after use (owner's decision 2026-10-09). "The deck is good" (publish_cleanup.py) deletes the session's scratch folder too.

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
