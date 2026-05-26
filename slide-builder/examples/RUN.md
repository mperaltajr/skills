# Running the quickstart

This example uses `quickstart-brief.md` (4 slides) and any registered client PPTX template you have on hand.

## What you need

- A registered client template — a `.pptx` file with `<stem>.brand.yml` and `<stem>.theme.json` sidecars next to it. If you don't have one, see SKILL.md § "Register a new client template" for the chat-driven flow.
- The verification step from INSTALL.md passing.

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

Phase 1 should print Stage-1 sanity (brand.yml + mmdc), then write `slide_01/_prompt.md` through `slide_04/_prompt.md` plus `_meta.json` and `dispatch_plan.md` to `$session\out\`.

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

This executes each `option_X.py`, grafts the produced slide onto your template, renders PNGs, and assembles fallback PPTXs for any `# FALLBACK_MERMAID:` options.

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
