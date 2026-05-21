# Slide Lab

Turn a written narrative brief into a client-branded PowerPoint deck — with three real design options per slide, rendered against your client's template, ready to review and pick.

---

## What you'll get

- **Three real design options per slide, in parallel.** One Claude Code agent per slide writes three python-pptx scripts. Each option is a different layout family — not three recolors of the same idea.
- **Discipline baked into every prompt.** The full designer rulebook (title anchor, body font floor, one accent moment, chart-honoring, icon library, circle containers, brand palette only) ships inside every per-slide agent prompt. No partial-context drift.
- **Output grafted onto your client's template.** Slides are produced against the client's PPTX directly. The final deck inherits the client's master, theme colors, and fonts — no layout drift, no manual re-themeing.
- **Review-and-pick workflow.** A single `REVIEW.html` page shows every option as a PNG thumbnail, lets you click A/B/C per slide, and hands back a one-line command to compile the final deck.

---

## Install

### 1. Clone the repo

```powershell
cd $HOME\.claude
git clone https://github.com/mperaltajr/skills.git skills
```

(Slide Lab lives inside the Claude Code skills directory so the skill metadata is auto-discovered.)

### 2. Python 3.10 or newer

Verify:

```powershell
py -3 --version
```

If missing, install from <https://www.python.org/downloads/windows/>.

### 3. Python dependencies

The build scripts depend on `python-pptx` and `lxml`. Install with:

```powershell
py -3 -m pip install -r requirements.txt
```

This installs all dependencies for Slide Lab + the related Slide Lab skills (slide-qc, storyline-helper, rfp-helper, etc.).

### 4. LibreOffice (required for PNG rendering)

Slide Lab renders every option to PNG via LibreOffice headless so you can review thumbnails before picking. Without it, the review step has no images.

- Download: <https://www.libreoffice.org/download/download/>
- Install with defaults
- Confirm the `soffice` binary is on `PATH`:

```powershell
soffice --version
```

If the command isn't found, add the LibreOffice `program` folder to `PATH` (typically `C:\Program Files\LibreOffice\program`).

### 5. Claude Code

Slide Lab dispatches per-slide agents through Claude Code. Install from <https://claude.com/claude-code>.

### 6. Verify with the smoke test

```powershell
py -3 %USERPROFILE%\.claude\skills\slide-builder\tests\test_smoke.py
```

The test runs the full prep → finalize → review pipeline end-to-end with canned agent outputs. Expect ~80 seconds and a final `overall : PASS`. If it fails, the most common cause is LibreOffice not being on `PATH`.

---

## Quickstart — build your first deck in 10 minutes

### Step 1. Write a brief (or use a sample)

A brief is a markdown file with one `### Slide N — Title` heading per slide and four labelled fields under each:

```markdown
### Slide 1 — Why this matters now

**Governing thought:** The cost of doing nothing is now larger than the cost of acting.

**So-what:** Move from quarterly reviews to a standing weekly cadence by end of Q2.

**Editorial emphasis:** Hero number; comparison.

**Evidence / content:**
- $4.2M annualized leakage from the current cadence
- Three peers have already converted; two are reporting 18% reduction
- Q1 pilot inside ops showed a 9% reduction in 6 weeks

**Chart type:** waterfall
```

Field labels the parser recognises:
- `Governing thought` — the slide's headline argument (used as the slide title)
- `So-what` — the action the audience should take
- `Editorial emphasis` — hint about layout family (hero number, comparison, three pillars, etc.)
- `Evidence / content` — the raw material to render (bullets, tables, numbers)
- `Chart type` — if the slide needs a chart, name it (waterfall, bar, KPI tile, none)

A full brief example lives at `slide-builder/exemplars/INDEX.md` (the catalog) and the rules every brief follows are in `slide-builder/reference/designer-brief.md`.

### Step 2. Prep — generate per-slide agent prompts

```powershell
py -3 %USERPROFILE%\.claude\skills\slide-builder\scripts\build_deck.py `
    --brief  C:\path\to\BRIEF.md `
    --template C:\path\to\CLIENT_TEMPLATE.pptx `
    --out C:\path\to\OUT_DIR
```

Writes one `OUT_DIR\slide_NN\_prompt.md` per slide (each with the full designer rulebook inlined), plus `dispatch_plan.md` and `_meta.json`.

### Step 3. Dispatch — fan out parallel agents from Claude Code

From an active Claude Code session, ask Claude to dispatch the `deck-builder` agent. That orchestrator reads `dispatch_plan.md` and instructs your parent session to fan out one general-purpose agent per slide **in a single parallel batch**. Each agent reads its `_prompt.md` and writes three standalone files into its slide directory:

- `OUT_DIR\slide_NN\option_A.py`
- `OUT_DIR\slide_NN\option_B.py`
- `OUT_DIR\slide_NN\option_C.py`

The dispatch must happen from the parent Claude Code session, not from inside a sub-agent — sub-agents don't have Task tool access.

### Step 4. Finalize — execute, graft, render PNGs

```powershell
py -3 %USERPROFILE%\.claude\skills\slide-builder\scripts\finalize_deck.py `
    --out C:\path\to\OUT_DIR `
    --template C:\path\to\CLIENT_TEMPLATE.pptx
```

For every `option_X.py`:
1. Runs the script to produce `option_X.pptx`.
2. Grafts the slide onto the client template and applies theme remap (client colors + fonts).
3. Renders the themed PPTX to PNG via LibreOffice (four in parallel).
4. Writes per-option QC.

Status lands in `OUT_DIR\RESULT.md`.

### Step 5. Build the review page

```powershell
py -3 %USERPROFILE%\.claude\skills\slide-builder\scripts\build_review.py `
    --out C:\path\to\OUT_DIR
```

Writes `OUT_DIR\REVIEW.html`.

### Step 6. Pick and compile

Open `REVIEW.html` in any browser. For each slide, click **PICK A**, **PICK B**, or **PICK C**. Add per-slide notes if you want them logged. Click **Build my deck** — the page copies a one-line command to your clipboard. Paste it into your Claude Code session to run:

```powershell
py -3 %USERPROFILE%\.claude\skills\slide-builder\scripts\compile_picks.py `
    --out C:\path\to\OUT_DIR `
    --template C:\path\to\CLIENT_TEMPLATE.pptx
```

Final deck lands at `OUT_DIR\final_deck.pptx` with per-slide PNG snapshots in `OUT_DIR\final_pngs\`.

---

## What the system produces

For every slide in your brief:

- **Three reproducible Python scripts.** `option_A.py`, `option_B.py`, `option_C.py` — each a standalone python-pptx script you can re-run, edit, or commit.
- **Three PNG thumbnails.** Themed against your client's PPTX. Use these to compare options at a glance.
- **A `REVIEW.html`.** A single self-contained page with the dot-dash storyline, brief-QC findings in plain English, PNG thumbnails, per-option QC badges, and a single "Build my deck" button that pipes your picks into the compile step.

For the deck overall:

- **`RESULT.md`** — per-option status (built / themed / rendered).
- **`final_deck.pptx`** — the compiled deck of your picks, ready to open in PowerPoint.

---

## Designer brief — the discipline the agents follow

Every per-slide agent receives the full designer rulebook in its prompt. The rules cover:

1. **Hard layout constraints** — 1280×720 canvas, title bottom-anchored, footer pinned, body font floor of 14px, brand palette only.
2. **Privacy + content rules** — no personal email/contact info, no "CONFIDENTIAL" tags in invariant zones, no lorem ipsum or TODO strings.
3. **Chart-honoring** — if the brief asks for a waterfall, the agent must build one (no quietly substituting bullets). Tables of 3+ numeric rows render as visual tables, not bullet lists.
4. **Page types** — one of nine structural families (single finding, recommendation, comparison, three-column, hero number, visual model, roadmap, cover, quote).
5. **Visual treatments** — full-bleed dark, tinted cards, dark-header cards, two-column with insight panel, hero stat, convergence band, accent rule.
6. **Icon library** — 1,143 vector icons; agents pick by name (`gear`, `compass`, `lightbulb`, etc.). No generic Unicode glyphs.
7. **Circle containers** — icon backgrounds are circles, never squares. Squares read as web-app tiles; circles read as editorial design.
8. **Slot design** — eyebrow / heading / body / hero sizes, bold ceiling of 5 bold elements per slide, no empty bottom half.

Full rulebook: `slide-builder/reference/designer-brief.md`.

---

## Exemplars

`slide-builder/exemplars/do/` holds hand-validated example slides organised by page-type. Each folder has:

- `exemplar.py` — the python-pptx source the agent should study
- `exemplar.png` — the rendered output
- `WHY.md` — 100-200 word rationale (what makes it strong, when to use it, patterns to copy)

The prep script classifies each brief slide to a page-type and inlines 1-2 matching exemplars into the agent's prompt. Catalog: `slide-builder/exemplars/INDEX.md`.

---

## Client template support

Any `.pptx` template works as long as it has a layout named **Blank** (most do — it's the default layout).

The finalize step extracts the client's theme colors and fonts from the template and remaps Slide Lab's brand palette constants (`BRAND_PRIMARY`, `BRAND_ACCENT`, etc.) to the client's actual colors. Same for fonts. No per-client configuration required.

Tested templates:
- FedEx Moving Forward
- Accenture Graphik

Other templates work; the first run against a new template may need a one-time theme cache warm-up.

---

## Troubleshooting

**LibreOffice render fails / no PNGs appear.**
Confirm `soffice --version` runs from PowerShell. If not, add `C:\Program Files\LibreOffice\program` to `PATH` and restart your shell.

**PNG previews look font-substituted.**
The client's brand fonts aren't installed on your machine. Install them system-wide for cleaner previews. The final PPTX still renders correctly in PowerPoint on a machine that has the fonts.

**The dispatch step doesn't fan out.**
The parallel fanout must run from your parent Claude Code session. Sub-agents don't have Task-tool access — if you tried to dispatch from inside a sub-agent it silently no-ops. Re-issue the request from the top-level Claude Code chat.

**Brief parser errors on a slide.**
Confirm each slide heading is `### Slide N — Title` or `### Slide N` (em dash or hyphen both fine). The parser handles letter IDs (`### Slide A`) and missing titles, but a heading like `## Slide 1` (only two `#`) is skipped.

**Smoke test fails.**
Run with `--keep` to inspect the temp directory it leaves behind:

```powershell
py -3 %USERPROFILE%\.claude\skills\slide-builder\tests\test_smoke.py --keep
```

The printed temp path holds the half-built artifacts so you can see where it stopped.

**Final deck opens but a slide is blank.**
Check `RESULT.md` for that slide's status. A theme step that failed silently shows up there. Re-run finalize with `--skip-build` to retry just the graft + render.

---

## Architecture in one paragraph

Slide Lab has four deterministic stages: **PREP** parses the brief and writes per-slide agent prompts (designer rulebook inlined). **DISPATCH** runs from your Claude Code session — one general-purpose agent per slide, in parallel, each producing three python-pptx scripts. **FINALIZE** executes those scripts, grafts the slides onto the client template, applies theme remap, and renders PNGs. **REVIEW** generates the HTML picker; once you've chosen, **COMPILE** stitches the picks into a single final deck. The designer brief travels with every per-slide prompt so the rules are never out of scope — the parallel agents can run independently without coordinating.

---

## Where things live

- Scripts: `slide-builder/scripts/`
- Designer rulebook: `slide-builder/reference/designer-brief.md`
- Exemplar catalog: `slide-builder/exemplars/INDEX.md`
- Agent definition: `~/.claude/agents/deck-builder.md`
- Smoke test: `slide-builder/tests/test_smoke.py`
- Skill metadata + deep architectural notes: `slide-builder/SKILL.md`
