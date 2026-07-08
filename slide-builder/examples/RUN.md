# Running the quickstart

This example uses `quickstart-brief.md` (4 slides) and any registered client PPTX template you have on hand.

## What you need

- A registered client template — a `.pptx` file with a `<stem>/` template-settings subfolder next to it (containing `brand.yml` and `theme.json`).
- The verification step from INSTALL.md passing.

## If you don't have a registered template yet (do this first)

Slide Lab can't build against a raw `.pptx`; it builds against a *registered* template (one with `brand.yml` + `theme.json` + `chrome.yml` template-settings files capturing the client's colors, fonts, layouts). Registration is a one-time chat-driven flow per template:

```powershell
# Phase 1 — propose (no writes to brand.yml yet)
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\register_template.py" propose `
    "<path to your raw template.pptx>"
```

This produces a `register.html` page next to your template. Open it. The page asks you to:

1. **Pick a primary brand color** — click a swatch (no hex typing).
2. **Pick an accent color** — click a swatch.
3. **Pick the default content layout** — the layout your slides should use 95% of the time.
4. **Optionally pick a reference slide** — point at one slide in your template that defines how every output should look (title position, subtitle box, accent placement, footer chrome). Recommended when your template has specific chrome geometry. Skip if your template is only covers/dividers.
5. **Strip-master-backgrounds toggle** — usually leave unchecked.

Copy the picks JSON from register.html, save it as `picks.json` next to the template, then commit:

```powershell
# Phase 2 — commit (writes brand.yml + theme.json + chrome.yml)
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\register_template.py" commit `
    "<path to your template.pptx>" `
    --picks "<path to picks.json>"
```

That's it — your template is now registered. The template-settings files (`brand.yml`, `theme.json`, `chrome.yml`) sit in a `<stem>/` subfolder next to the `.pptx`. You only need to repeat this if the template's master/layouts change.

For the full registration flow with diagrams, see SKILL.md § "Register a new client template."

## The full sequence

```powershell
$skill   = "$env:USERPROFILE\.claude\skills\slide-builder"
$session = "$env:USERPROFILE\Documents\slide-lab-quickstart"
$template = "<path to your registered template.pptx>"

New-Item -ItemType Directory -Force -Path "$session\out" | Out-Null

# Phase 1 — prep
py -3 "$skill\scripts\build_deck.py" `
    --brief "$skill\examples\quickstart-brief.md" `
    --template "$template" `
    --out "$session\out"
```

Phase 1 should print the Stage-1 sanity check (brand settings + slide-qc sibling), then write `slide_01/_prompt.md` through `slide_04/_prompt.md` plus `_meta.json` and `dispatch_plan.md` to `$session\out\`.

## Phase 2 — dispatch agents (the part Claude does)

Phase 1 wrote one `_prompt.md` per slide. The parent chat session reads `dispatch_plan.md` and dispatches **one worker agent per slide in parallel**. Each agent reads its `_prompt.md` and writes `option_A.py`, `option_B.py`, `option_C.py` into its `slide_NN/` directory.

In a real run, your chat orchestrator (Claude Code session) handles this step. To exercise it manually here, you can open `$session\out\dispatch_plan.md` and ask Claude in your current chat to dispatch the 4 worker agents per the plan.

## Phase 3 — finalize

After all 4 slides have option scripts:

```powershell
py -3 "$skill\scripts\finalize_deck.py" `
    --out "$session\out" `
    --template "$template"
```

This executes each `option_X.py`, grafts the produced slide onto your template, and renders the per-option PNGs.

## Phase 4 — visual gate

```powershell
py -3 "$skill\scripts\build_gate_preview.py" --out "$session\out"
```

Open `$session\out\GATE3-PREVIEW.html` in a browser. Each of the 4 slides should appear with 3 option tiles side by side. The brand colors (from your registered template's `brand.yml`) drive the chrome.

## Phase 5 — pick + compile (the real-deck step)

Pick winners by writing a `picks.json`:

```json
{ "slide_01": "A", "slide_02": "B", "slide_03": "A", "slide_04": "C" }
```

Then:

```powershell
py -3 "$skill\scripts\compile_picks.py" `
    --out "$session\out" `
    --picks "$session\picks.json" `
    --final "$session\final.pptx"

py -3 "$skill\scripts\build_review.py" --out "$session\out"
```

`final.pptx` is your deliverable. `REVIEW.html` is the picking + QC record.

## Expected total time

A 4-slide deck on a modern laptop: ~3–5 minutes for Phases 1, 3, 4. Phase 2 (agent dispatch) depends on Claude latency — usually 30–90 seconds for 4 parallel agents.
