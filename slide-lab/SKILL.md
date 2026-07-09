---
name: slide-lab
description: "Front door for ALL deck and PowerPoint work in Slide Lab. Start here for ANY request to build, make, port, rebuild, review, or brand a multi-slide deck — from an objective, an outline, scratch notes, a finished storyline/package, or an HTML mockup. NEVER hand-roll a deck from a blank python-pptx Presentation for a branded or narrative deck — that is the documented failure path (wrong template, tiny fonts, no review). Presents the user a menu and routes: new narrative → storyline-helper; already-written storyline/package or HTML mockup → storyline-helper's review-and/or-build path, then slide-builder (build on the client template's real layouts); RFP/proposal → rfp-helper; rebuild/insert a slide in a deck Slide Lab built → slide-builder; work on an existing .pptx Slide Lab didn't build → slide-builder's external-deck door (6a fix text, 6b redesign a slide via adopt_deck + splice-back, 6c refresh a recurring/PMO deck); register a client template (one-time, standalone) → register_template; QC of a built deck → slide-qc. A deck is not done until slide-qc has run."
---

# Slide Lab — front door

> **Windows vs macOS/Linux — applies to every Slide Lab skill.** Commands are written with `py -3` (Windows). On **macOS/Linux**, run the identical command with **`python3`** instead of `py -3`. Paths/flags are unchanged. LibreOffice (used for rendering) is located automatically on all three OSes; PowerPoint COM QC is Windows-only and opt-in.

You are the single entry point for deck work. **You build nothing yourself.** Two jobs:
1. If the user's intent is already specific, name the route in one line and go.
2. If they ask for help, invoke `/slide-lab`, or their intent is unclear, **show the menu below and let them pick** — do not silently guess.

## Show the menu when intent isn't already specific

Present this to the user (adapt lightly), then route on their choice:

> **Slide Lab — what are you trying to do?**
> 1. **Build a new deck** — you have a topic/message but no slides yet.
> 2. **Work from material I already have** — a storyline, package, outline, notes, or HTML mockup, *or an existing deck to use as the **source for a fresh deck***. I can **review & refine** and/or **build**. *(builds a new deck — does not edit your file in place; to change an existing file, that's option 6.)*
> 3. **RFP / proposal response** — scored against evaluation criteria.
> 4. **QC a deck** — review a built `.pptx` before you send it.
> 5. **Change a deck Slide Lab built** — rebuild, fix, or insert a slide (there's a Slide Lab build folder / REVIEW.html).
> 6. **Work on a deck Slide Lab did *not* build** — an existing `.pptx` you already have. I'll ask what you're changing:
>    &nbsp;&nbsp;**a. Fix text or numbers**, keep the design — small edits.
>    &nbsp;&nbsp;**b. Redesign / upgrade a slide** (or a few) — rebuilt on the deck's own template, then dropped back into your file.
>    &nbsp;&nbsp;**c. Refresh a recurring / PMO deck** — drop this cycle's text into the fixed template, design unchanged. *(text boxes only; tables/charts by hand)*
> 7. **Register a client template** — one-time setup (brand + layouts) before building.
> 8. **Not sure** — I'll ask a couple of questions.

If the request is already specific ("build me a 5-slide steering deck from this brief on template X"), skip the menu, state the route, and proceed — with a one-line *"not what you wanted? here are the options"* fallback.

## Absolute rules (on every route)

- **Never** hand-roll `python-pptx` / `pptxgenjs` from a blank `Presentation()` for a branded or multi-slide deck — that is the documented failure path.
- **"Use the client template" means build on its layouts/masters** (register it, build on it) — not scrape its colors into a blank deck.
- **Registration is a standalone step, never inline in a build.** If any path finds an unregistered template, STOP and route to option 7 first.
- **A deck is not "done" until `slide-qc` has run and produced a report.** A PDF you rendered yourself is not QC. (Applies to any built or rebuilt deck — options 1/2/3/5, and 6b/6c. A **6a** text-only tweak is exempt, but run QC anyway if the edit changed text length, since a longer run can overflow its box.)
- **Font sizes** stay on PowerPoint's default grid, 8pt floor; body ~11–14pt.

## Routing — what each choice invokes

| Choice | Route |
|---|---|
| 1 Build new | **storyline-helper** → coaches narrative → quality gate → emits brief + storyline (dot-dash) → **then stops and asks whether to build**. On yes: **slide-builder** → **slide-qc**. (A user who just wants a storyline/dot-dash stops here — that's a valid finish.) |
| 2 Work from what I have | **storyline-helper** "review &/or build" path — produces a **new** deck; it does **not** edit an existing file in place (that's option 6). First ask **review or build** (see below). Review → critique + suggestions, STOP. Build → validate → emit → slide-builder. An existing deck or HTML mockup is read as **reference/source** (its content/structure), then slides are **rebuilt on the client template** — the source's exact design is not copied 1:1; say so up front. |
| 3 RFP | **rfp-helper** → proposal brief (`mode: rfp`) → slide-builder. |
| 4 QC a deck | **slide-qc** on a built `.pptx`. Ask for the deck path if not given. |
| 5 Change a Slide-Lab-built deck | **slide-builder** — rebuild: `build_deck.py --slide N`; insert: `build_deck.py --insert N`; then worker → `finalize_deck.py --slide N` → `compile_picks.py`. **Only works on a deck Slide Lab built** (an `<out>/` with `_meta.json`). For an external deck, use option 6. |
| 6 Work on an external `.pptx` (Slide Lab didn't build it) | **slide-builder**, forked by what's changing (ask **6a/6b/6c**): **6a — tiny text/number edit** → "Edit an existing PowerPoint" mode: open with python-pptx, tweak/extract text, save a copy (small tweaks only, no build/QC). **6b — redesign a slide (or a few)** → `adopt_deck.py` (extract the deck's content → brief; register the deck's **own** template; synthesize `_meta.json` + slide dirs) → `build_deck.py --slide N` → worker → `finalize_deck.py --slide N` → pick → **`compile_picks.py --splice-into`** (replaces slide N in a copy of the original, keeps every other slide) → **slide-qc**. **6c — refresh a recurring/PMO deck** → `refresh_deck.py` (dump text shapes → user tags the volatile fields → saved refresh spec → batch in-place `run.text` updates to a dated copy, design frozen) → **slide-qc**. Never overwrite the user's original — always write a new file. |
| 7 Register a template | **register_template.py** `propose` → user picks → `commit` (or `commit-cli`). Standalone, no build; writes `<stem>/` brand.yml + theme.json + chrome.yml, saves a normalized `build-template.pptx` every build opens (original never touched), and builds a real **mock slide** (`<stem>/selftest/mock.pptx`) on the default layout. **Registration is NOT done until the user opens that mock slide in PowerPoint, confirms the title/takeaway/footnote/source land + fit, and you run `register_template.py confirm <template>`** (which also deletes the self-test folder) — the automated self-test can pass when something is still off, so a human check is required. A commit auto-adds the template to the pick-list (`register_template.py list`) marked **"(needs review)"** until confirmed. | **Follow slide-builder's "Register a new client template" rules:** show the user the proposed colors and let them confirm — do NOT auto-accept (proposed brand colors can come out inverted), and you MUST capture the **default content layout**, or every later build fails mid-way. |
| 8 Not sure | Orientation (below), then route. |

## Disambiguator — options 2 vs 5 vs 6 all touch "a deck"

Route on **provenance first, then effort** — two short questions.

**Level 1 — provenance.** *"Is there a deck file involved, and did Slide Lab build it?"*

- **No deck yet / I have material to build from** (storyline, outline, notes, HTML mockup, or an existing deck to use as *source* for a new one) → **option 1** (from scratch) or **option 2** (from material). Both produce a **new** deck; neither edits an existing file in place.
- **Yes — Slide Lab built it** (there's a build folder / REVIEW.html / `_meta.json`) → **option 5** (rebuild slide N or insert a slide), or **option 4** to QC it.
- **It's an external `.pptx` Slide Lab did NOT build** → **option 6**, then ask Level 2.

**Level 2 — effort (only for option 6, the external-deck door).** *"What are you changing in it?"*

- **Just the words / numbers, design stays** → **6a** (direct python-pptx edit, save a copy).
- **The look of a slide — layout or visual treatment** → **6b** (adopt → rebuild slide N on the deck's own template → splice back into a copy → QC).
- **It's a recurring deck on a fixed template and you're dropping in this cycle's content** → **6c** (content refresh from a saved spec, design frozen → QC).

Two boundary tests to keep straight: **option 2 vs option 6** — *"a new deck built from this one's ideas (2), or change this actual file (6)?"* **6a vs 6b** — *"changing words/numbers = 6a; changing how it looks = 6b."* The per-slide rebuild/insert of **option 5** needs the pipeline's `_meta.json` and only works on decks Slide Lab produced; **6b** is how you get equivalent redesign on an external deck (it synthesizes that `_meta.json` via `adopt_deck.py`).

## Before any build path (options 1, 2, 3) — pick the template from the list first

A build needs a **registered** template, chosen *at the start* — before the user does all the storyline/RFP work — not after. Do this via the pick-list, never by guessing a path:

1. Run `py -3 slide-builder/scripts/register_template.py list` — it prints the registered templates as JSON (and self-heals: prunes ones whose files are gone, rediscovers a template's settings files in OneDrive/Documents).
2. **Present them to the user as a numbered pick-list**, e.g. *"Which client template? 1) Acme — Template2  2) Globex — Deck (needs review)  …  N) Register a new one."* Show each entry's `confirmed` status — mark `confirmed: false` ones **"(needs review)"**.
3. Route the chosen entry's **`template_path`** (the original `.pptx`) into the build as the brief's `client_template:` front-matter. Always pass the **original** path — the pipeline opens the normalized build copy automatically (via `resolve_build_template`); the entry's `build_template_path` is informational only. Passing the copy as `client_template:` would fail the build (its sidecars live under the original stem).
4. **If the template they want is not in the list, do NOT guess a path** — go to **option 7 (set up the template)** first, then re-run `list` and pick it. If the list is empty, the user has no registered templates yet → option 7.
5. **If the chosen template is not yet confirmed** (`confirmed: false`), stop and have the user open its mock slide (`<stem>/selftest/mock.pptx`) in PowerPoint; once they confirm the title/takeaway/footnote/source land, run `register_template.py confirm <template>` before building. Don't build on an unconfirmed template.

Picking at the start spares a first-timer from finishing the whole narrative only to hit a "set up your template first" wall at the end.

## Orientation — option 8 ("not sure")

Ask up to three, then route:
1. Is this the **first time** building with this client's template? → set it up first (**option 7**).
2. Do you already have a deck **Slide Lab built** (a build folder / REVIEW.html)? → yes: fix/insert a slide (5) or QC it (4).
3. Starting fresh, or do you already have a **storyline / outline / mockup**? → fresh: (1); have material: (2). Is it an **RFP / proposal**? → (3). Just editing an **existing `.pptx`**? → (6).

## After routing

State the route in one line, invoke the skill, and let it run. Do not duplicate its work.

## Enforcement note (for maintainers, not a build instruction)

This front door and the skill descriptions **steer** routing strongly, but they are advisory — they cannot hard-block a hand-rolled script on their own. A true hard block requires a `PreToolUse` hook shipped as a Claude Code plugin and force-deployed by your org's Claude Code admin via managed settings; it is not active by default, and in a managed-enterprise org a self-installed plugin's hook may be suppressed by `allowManagedHooksOnly`. Until an admin deploys that, this router plus the skill descriptions are the enforcement layer.
