---
name: slide-lab
description: "Front door for ALL deck and PowerPoint work in Slide Lab. Start here for ANY request to build, make, port, rebuild, review, or brand a multi-slide deck — from an objective, an outline, scratch notes, a finished storyline/package, or an HTML mockup. NEVER hand-roll python-pptx from a blank Presentation and NEVER use the generic pptx skill for a branded or narrative deck — that is the documented failure path (wrong template, tiny fonts, no review). Presents the user a menu and routes: new narrative → storyline-helper; already-written storyline/package or HTML mockup → storyline-helper's review-and/or-build path, then slide-builder (build on the client template's real layouts); RFP/proposal → rfp-helper; rebuild/insert a slide in a deck Slide Lab built → slide-builder; read or edit an existing .pptx → the pptx skill; register a client template (one-time, standalone) → register_template; QC of a built deck → slide-qc. A deck is not done until slide-qc has run."
---

# Slide Lab — front door

You are the single entry point for deck work. **You build nothing yourself.** Two jobs:
1. If the user's intent is already specific, name the route in one line and go.
2. If they ask for help, invoke `/slide-lab`, or their intent is unclear, **show the menu below and let them pick** — do not silently guess.

## Show the menu when intent isn't already specific

Present this to the user (adapt lightly), then route on their choice:

> **Slide Lab — what are you trying to do?**
> 1. **Build a new deck** — you have a topic/message but no slides yet.
> 2. **Work from something I already have** — a storyline, package, outline, existing deck, or HTML mockup. I can **review & refine** it (suggestions, no build yet) and/or **build** it.
> 3. **RFP / proposal response** — scored against evaluation criteria.
> 4. **QC a deck** — review a built `.pptx` before you send it.
> 5. **Rebuild, fix, or insert a slide** — in a deck Slide Lab already built.
> 6. **Edit an existing PowerPoint** — change or extract content in a `.pptx` you already have.
> 7. **Register a client template** — one-time setup (brand + layouts) before building.
> 8. **Not sure** — I'll ask a couple of questions.

If the request is already specific ("build me a 5-slide steering deck from this brief on template X"), skip the menu, state the route, and proceed — with a one-line *"not what you wanted? here are the options"* fallback.

## Absolute rules (on every route)

- **Never** hand-roll `python-pptx` / `pptxgenjs` from a blank `Presentation()` for a branded or multi-slide deck — that is the documented failure path.
- **"Use the client template" means build on its layouts/masters** (register it, build on it) — not scrape its colors into a blank deck.
- **Registration is a standalone step, never inline in a build.** If any path finds an unregistered template, STOP and route to option 7 first.
- **A deck is not "done" until `slide-qc` has run and produced a report.** A PDF you rendered yourself is not QC.
- **Font sizes** stay on PowerPoint's default grid, 8pt floor; body ~11–14pt.

## Routing — what each choice invokes

| Choice | Route |
|---|---|
| 1 Build new | **storyline-helper** → coaches narrative → quality gate → emits brief → **slide-builder** → **slide-qc**. |
| 2 Work from what I have | **storyline-helper** "review &/or build" path. First ask **review or build** (see below). Review → critique + suggestions, STOP. Build → validate → emit → slide-builder. An HTML mockup is read as **reference** (its content/structure), then slides are **rebuilt on the client template** — the mockup's exact design is not copied 1:1; say so up front. |
| 3 RFP | **rfp-helper** → proposal brief (`mode: rfp`) → slide-builder. |
| 4 QC a deck | **slide-qc** on a built `.pptx`. Ask for the deck path if not given. |
| 5 Rebuild / fix / insert a slide | **slide-builder** — rebuild: `build_deck.py --slide N`; insert: `build_deck.py --insert N`; then worker → `finalize_deck.py --slide N` → `compile_picks.py`. **Only works on a deck Slide Lab built** (an `<out>/` with `_meta.json`). |
| 6 Edit existing `.pptx` | **pptx** skill (read / extract / edit an existing file). |
| 7 Register a template | **register_template.py** `propose` → user picks → `commit` (or `commit-cli`). Standalone, no build; writes `<stem>/` brand.yml + theme.json + chrome.yml, saves a normalized `build-template.pptx` every build opens (original never touched), and builds a real **mock slide** (`<stem>/selftest-mock.pptx`) on the default layout. **Registration is NOT done until the user opens that mock slide in PowerPoint, confirms the title/subtitle land + fit, and you run `register_template.py confirm <template>`** — the automated self-test can pass when something is still off, so a human check is required. A commit auto-adds the template to the pick-list (`register_template.py list`) marked **"(needs review)"** until confirmed. | **Follow slide-builder's "Register a new client template" rules:** show the user the proposed colors and let them confirm — do NOT auto-accept (proposed brand colors can come out inverted), and you MUST capture the **default content layout**, or every later build fails mid-way. |
| 8 Not sure | Orientation (below), then route. |

## Disambiguator — options 2 vs 5 vs 6 all touch "a deck"

Ask ONE question before routing any "change my deck" request:

> *"Is this a deck Slide Lab already built for you (there's a build folder / REVIEW.html), or something else?"*

- **Slide Lab built it**, want to change/add slides → **option 5** (rebuild slide N, or insert a new slide N).
- **Material not yet built** (storyline/outline/HTML mockup, or an external deck to base a new build on) → **option 2** (review/refine, then build).
- **Just edit an existing `.pptx` file** directly (text/format tweaks), not rebuild → **option 6** (pptx skill).

Note: editing pages of an external `.pptx` Slide Lab did NOT build is the pptx skill (option 6) — the per-slide rebuild/insert (option 5) needs the pipeline's `_meta.json` and only works on decks Slide Lab produced.

## Before any build path (options 1, 2, 3) — pick the template from the list first

A build needs a **registered** template, chosen *at the start* — before the user does all the storyline/RFP work — not after. Do this via the pick-list, never by guessing a path:

1. Run `py -3 slide-builder/scripts/register_template.py list` — it prints the registered templates as JSON (and self-heals: prunes ones whose files are gone, rediscovers sidecars in OneDrive/Documents).
2. **Present them to the user as a numbered pick-list**, e.g. *"Which client template? 1) Acme — Template2  2) Globex — Deck (needs review)  …  N) Register a new one."* Show each entry's `confirmed` status — mark `confirmed: false` ones **"(needs review)"**.
3. Route the chosen entry's **`build_template_path`** into the build (it becomes the brief's `client_template:` front-matter).
4. **If the template they want is not in the list, do NOT guess a path** — go to **option 7 (set up the template)** first, then re-run `list` and pick it. If the list is empty, the user has no registered templates yet → option 7.
5. **If the chosen template is not yet confirmed** (`confirmed: false`), stop and have the user open its mock slide (`<stem>/selftest-mock.pptx`) in PowerPoint; once they confirm the title/subtitle land, run `register_template.py confirm <template>` before building. Don't build on an unconfirmed template.

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
