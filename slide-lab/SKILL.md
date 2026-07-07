---
name: slide-lab
description: "Front door for ALL deck and PowerPoint work in Slide Lab. Start here for ANY request to build, make, port, rebuild, or brand a multi-slide deck — from an objective, an outline, scratch notes, a finished storyline/package, or an HTML mockup. NEVER hand-roll python-pptx from a blank Presentation and NEVER use the generic pptx skill for a branded or narrative deck — that is the documented failure path (wrong template, tiny fonts, no review). This skill routes the request: a new narrative → storyline-helper; an already-written storyline/package or an HTML mockup → storyline-helper's validate-and-emit path, then slide-builder (build on the client template's real layouts); RFP/proposal → rfp-helper; reading or editing an existing .pptx → the pptx skill; QC of a built deck → slide-qc. A deck is not done until slide-qc has run."
---

# Slide Lab — front door / router

You are the single entry point for deck work. **You do not build anything yourself.** You read the request, pick the route, state it, and invoke the matching skill. If a request smells at all like "produce a PowerPoint," it comes through here first.

## Absolute rules (apply on every route)

- **Never** hand-roll `python-pptx` / `pptxgenjs` from a blank `Presentation()` for a branded or multi-slide deck. That is the documented failure path — it skips template registration, the layout system, REVIEW.html, and QC, and produces off-brand slides with invented font sizes.
- **"Use the client template" means build on its layouts/masters** — register it and build on it. Copying its theme colors into a blank deck is a deviation, not a build.
- **Do not use the generic `pptx` skill to create a branded or narrative deck.** `pptx` is only for reading or editing an existing `.pptx`.
- **A deck is not "done" until `slide-qc` has run and produced a report.** A PDF you rendered and looked at yourself is not QC — the agent that built the deck cannot grade its own output.
- **Font sizes** stay on PowerPoint's default grid with an 8pt floor; body copy sits at ~11–14pt. Never invent a px→pt scale.

## Routing

| The request is… | Route to |
|---|---|
| A new deck, narrative not written yet | **storyline-helper** — it coaches the narrative, runs the quality gate, emits the brief, and hands off to slide-builder. |
| A deck where the storyline/brief/**package** is already written, or an **HTML mockup** exists | **storyline-helper**, told to **validate** the existing package against the gate (not re-coach), emit the brief, and hand to **slide-builder**. HTML mockups build via slide-builder's **sketch path** — not a hand-written port. |
| An RFP / proposal response (scored against criteria) | **rfp-helper** → produces a proposal brief → slide-builder. |
| Reading, extracting, or editing an **existing** `.pptx` (no new narrative) | the **pptx** skill. |
| QC a built deck | **slide-qc**. |
| A recurring PMO / template-fill deck | **slide-builder** template-fill mode. |
| Rebuild one slide of an existing build | **slide-builder** (`build_deck.py --slide N` → worker → `finalize_deck.py --slide N` → pick → `compile_picks.py`). |

## After routing

State the route in one line, invoke the skill, and let it run. Do not duplicate its work or pre-empt its steps.

## Enforcement note (for maintainers, not a build instruction)

This front door and the skill descriptions **steer** routing strongly, but they are advisory — they cannot hard-block a hand-rolled script on their own. A true hard block requires a `PreToolUse` hook shipped as a Claude Code plugin and force-deployed by your org's Claude Code admin via managed settings (`extraKnownMarketplaces` + force-enabled plugin); it is not active by default and, in a managed-enterprise org, a self-installed plugin's hook may be suppressed by `allowManagedHooksOnly`. Until an admin deploys that, this router plus the skill descriptions are the enforcement layer.
