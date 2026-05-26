# Quickstart — build your first deck

Goal: build a small deck from a sample brief to confirm everything works before you point Slide Lab at a real client engagement.

Prerequisites: complete [INSTALL.md](INSTALL.md) and confirm the verification step prints `install OK`.

## The 3-command sequence

The Slide Lab build splits into three phases. All commands assume the skill at `C:\Users\<you>\.claude\skills\slide-builder\`.

```powershell
$skill = "$env:USERPROFILE\.claude\skills\slide-builder"
$session = "$env:USERPROFILE\Documents\slide-lab-quickstart"
New-Item -ItemType Directory -Force -Path $session\out | Out-Null

# Phase 1: prep — read brief + template, write per-slide prompts
py -3 "$skill\scripts\build_deck.py" `
    --brief "$skill\examples\quickstart-brief.md" `
    --template "$skill\examples\quickstart-template.pptx" `
    --out "$session\out"

# (Between Phase 1 and Phase 2, the parent chat session dispatches
#  per-slide agents that write option_A.py / option_B.py / option_C.py
#  into each slide_NN/ subdir. For this quickstart, run by hand —
#  see examples/RUN.md for the dispatch step.)

# Phase 2: finalize — execute option scripts + graft onto template + render PNGs
py -3 "$skill\scripts\finalize_deck.py" `
    --out "$session\out" `
    --template "$skill\examples\quickstart-template.pptx"

# Phase 3: review — generate GATE3-PREVIEW.html for visual sanity
py -3 "$skill\scripts\build_gate_preview.py" --out "$session\out"
```

Expected console output (abbreviated):

```
[Phase 1] build_deck.py
  Stage 1 sanity: brand.yml + mmdc OK
  Stage 2 prep:   <N> slide prompts rendered
  out: <session>\out

[Phase 2] finalize_deck.py
  built option_A.pptx (slide 1) — pattern: 50/50 vertical
  built option_B.pptx (slide 1) — pattern: full canvas
  ... etc.

[Phase 3] build_gate_preview.py
  GATE3-PREVIEW.html written:
    <session>\out\GATE3-PREVIEW.html
```

Open `GATE3-PREVIEW.html` in a browser. You should see one section per slide with three rendered PNG tiles (options A/B/C) side by side.

## After the quickstart

1. Replace `examples/quickstart-template.pptx` with your client's PPTX. **Register it first** — see "Register a new client template" in [SKILL.md](SKILL.md).
2. Replace `examples/quickstart-brief.md` with a real narrative brief. The format is documented at the top of [SKILL.md](SKILL.md) § "Input contract — narrative brief."
3. After the gate preview, pick winners and run `compile_picks.py` → final PPTX. See [SKILL.md](SKILL.md) § "Build flow" for the pick + compile step.

If anything in the 3-command sequence prints `ERROR:` or a Python traceback, re-run the verification step in [INSTALL.md](INSTALL.md) — the deps usually drift first.
