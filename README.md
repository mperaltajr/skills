# Claude Slide Lab

> AI-powered skills for building consultant-quality PowerPoint decks, Word documents, and spreadsheets — directly from Claude Code.

---

## What is Claude Slide Lab?

Claude Slide Lab is a collection of Claude Code skills that turn a narrative brief into a fully branded PowerPoint deck — complete with your client's colors, fonts, and layout. Instead of spending hours in PowerPoint, you describe what the slide should say and Claude builds it.

**What makes it different from just asking Claude to make slides:**
- Pulls colors and fonts directly from your client's `.pptx` template — no manual branding
- Generates 3 structurally distinct design options per slide, not just 3 color variations
- Runs quality gates before showing you anything — a narrative gate on the storyline and hardline build rules on every slide
- Flags missing data with placeholder blocks so you know exactly what to fill in before client delivery
- Outputs a real `.pptx` file you can open, edit, and send

---

## Skills Included

| Skill | What it does |
|---|---|
| `slide-lab` | **Front door — start here for any deck request.** Routes the request to the right skill (new narrative → storyline-helper; finished package/HTML mockup → validate → slide-builder; RFP → rfp-helper; edit an existing `.pptx` → slide-builder's edit mode; QC → slide-qc) and enforces the rule: never hand-roll a deck from a blank python-pptx Presentation for a branded deck; build on the client template's layouts; a deck isn't done until slide-qc has run. |
| `storyline-helper` | Coaches your deck narrative — governing thought, audience, per-slide story — before any slides are built |
| `slide-builder` | Builds a PowerPoint deck from a narrative brief via parallel agent fanout: prep → per-slide workers produce three structurally distinct design options each (image-first, then converted to native PowerPoint) → finalize → REVIEW.html → pick → compile. Brand colors + fonts + layouts come from your registered client template. Also handles small edits to an **existing** `.pptx` Slide Lab didn't build (text/shape tweaks, extraction). |
| `slide-qc` | Renders every slide to PNG (LibreOffice by default; opt-in PowerPoint COM) and reviews them with vision — produces a per-slide Critical / Major / Advisory report before you open the deck |
| `docx` | Word document generation — reports, memos, letters with proper formatting |
| `xlsx` | Spreadsheet creation, editing, and cleaning for any `.xlsx` / `.csv` task |
| `slidelab-log` | Generates a structured session report when something goes wrong — Claude writes the technical details, you submit it as a GitHub issue |
| `rfp-helper` | RFP / proposal response coaching — win themes, scoring criteria, section-by-section structure; produces a proposal brief that slide-builder can build from |

---

## Prerequisites

Before installing, make sure you have:

- **Claude Code** — [claude.ai/code](https://claude.ai/code)
- **Git** — [git-scm.com](https://git-scm.com) *(download and install, keep all defaults)*
- **Python 3** — [python.org](https://python.org) *(needed for slide-builder)*
- **LibreOffice** — [libreoffice.org](https://www.libreoffice.org) *(needed for slide-qc review and visual previews; the deck build itself runs without it. Defaults to `C:\Program Files\LibreOffice\`)*

---

## Installation

Open **PowerShell** and run these commands one at a time. Copy each block, paste it into PowerShell, and press Enter. Wait for it to finish before running the next one.

**1. Download the skills:**
```powershell
git clone https://github.com/mperaltajr/skills "$env:USERPROFILE\.claude\skills"
```

**2. Install Python dependencies** — the repo ships a `requirements.txt` with every dep across all skills:
```powershell
pip install -r "$env:USERPROFILE\.claude\skills\requirements.txt"
```

**Then install the Chromium browser that slide-builder renders with** — the default build path authors each slide as HTML and renders it to an image via headless Chromium, so this is required:
```powershell
py -3 -m playwright install chromium
```

> **On a corporate network (Accenture, Deloitte, etc.) and seeing SSL errors?**
> Your company's security software can block pip. Use this version of step 2 instead:
> ```powershell
> pip install -r "$env:USERPROFILE\.claude\skills\requirements.txt" --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org
> ```

> **LibreOffice not at the default location?**
> Set `SLIDE_LAB_SOFFICE` to the absolute path of `soffice.exe`, or add the LibreOffice `program\` folder to `PATH`. The render scripts look at the env var first, then `PATH`, then common default locations.

**3. *(Optional but recommended)* Configure recommended settings:**

This does two things: silently pulls the latest skills every time Claude Code starts, and allows Claude to run PowerShell commands during a session without prompting for permission each time.

```powershell
$s = "$env:USERPROFILE\.claude\settings.json"
$settings = '{"permissions":{"defaultMode":"bypassPermissions","allow":["Bash","PowerShell","Read","Write","Edit","Glob","Grep"]},"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"Set-Location \"$env:USERPROFILE\\.claude\\skills\"; git pull --quiet 2>$null; exit 0","shell":"powershell","async":true}]}]}}'
if (!(Test-Path $s)) { Set-Content $s $settings -Encoding utf8 } else { Write-Host "Global settings already exist — see Troubleshooting below." }
```

**4. Install the Slide Lab agents** — Claude Code reads agent definitions from `~/.claude/agents/`, a separate folder from skills. The deck pipeline uses two subagents, both shipped in `slide-builder/agents/`:
```powershell
if (!(Test-Path "$env:USERPROFILE\.claude\agents")) { New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\agents" | Out-Null }
Copy-Item -Path "$env:USERPROFILE\.claude\skills\slide-builder\agents\*.md" -Destination "$env:USERPROFILE\.claude\agents\" -Force
```
This installs `slide-builder-worker` (the Stage-2 per-slide fanout agent) and `slide-builder-translator` (the Stage-3.5 agent that converts a picked sketch-path HTML option to editable native python-pptx). These are the source-of-truth copies; `slide-builder/INSTALL.md` Steps 6–7 document the per-agent verification greps.

**5. Restart Claude Code.** The skills and agents are now active.

**6. *(Optional)* Verify the install with the Python-side smoke tests:**
```powershell
cd "$env:USERPROFILE\.claude\skills"
py -3 slide-builder/tests/run_sketch_smoke.py
py -3 slide-builder/tests/run_layout_inheritance_smoke.py
py -3 slide-builder/tests/run_rebuild_slice_smoke.py
py -3 slide-builder/tests/run_insert_slice_smoke.py
py -3 slide-builder/tests/run_font_lock_smoke.py
```
The first exercises the sketch (HTML-first) build path end-to-end on the Python side (prompt rendering, HTML→PNG render, classifier, R4 QC, native execution). The second builds a 4-slide deck against a layout-diverse fixture template. The third builds a deck then rebuilds one slide, confirming the rebuild only touches that slide. The fourth builds a deck then inserts a slide, confirming the deck renumbers correctly and the shifted slides keep their output. The fifth checks that every text size is locked to PowerPoint's default sizes (floor 8pt). All print `All phases passed.` / `SMOKE PASSED.` on success; any failure points at the broken piece.

---

## Troubleshooting

**`playwright` is not recognized**
Use `py -3 -m playwright install chromium` instead of `playwright install chromium`. The `-m` flag tells Python to find and run playwright directly.

**SSL errors / "certificate verify failed" during pip install**
Your company network is blocking the connection. Use the `--trusted-host` version of step 2 above.

**"Global settings already exist" during step 3**
You already have a Claude Code settings file. Open `%USERPROFILE%\.claude\settings.json` in Notepad and verify two things are present: (1) `"PowerShell"` is in the `permissions.allow` array — without it, Claude will prompt for permission on every shell command; (2) the `hooks.SessionStart` block is present for auto-updates. Add whichever is missing, then restart Claude Code.

**Skills not showing up after restart**
Check that the skills folder exists at `%USERPROFILE%\.claude\skills\`. If the folder is empty or missing, re-run step 1.

---

## Project Setup

Before building your first deck, set up a folder for your client:

```
YourClient/
├── _templates/
│   └── client-template.pptx     ← your client's branded PowerPoint template
└── sessions/
    └── 2026-05-01 Kickoff/       ← one folder per working session
```

- The `_templates/` folder holds your client's PowerPoint template. Claude extracts colors and fonts from it automatically.
- Each session gets its own dated folder. Claude saves the deck, mockups, and working files there.
- You only need to add the template once per client.

### Register the template (one-time, per client)

Before the first build on a new template, register it so Claude learns its brand colors, fonts, and layouts. In Claude Code, just say:

```
Register my template at _templates/client-template.pptx
```

Claude walks you through confirming the brand colors (it proposes them from the template; you correct anything wrong), then writes a small set of sidecar files next to the template. As part of registration it also saves a **cleaned copy** of your template that every build runs on — sample slides and stray named sections removed, placeholders repaired so titles and subtitles reliably show up. Your original `.pptx` is never modified.

Registration then builds a real **mock slide** (`selftest-mock.pptx`, next to your template) on your default layout. **Open it in PowerPoint and confirm the title and subtitle appear correctly and fit** — the automated check can pass when something is still off, so this human look is required. When it looks right, tell Claude to confirm it (it runs `register_template.py confirm`). Until you confirm, the template shows as **"(needs review)"** in your pick-list and builds will warn.

**This is required once per template** — if you skip it and start a build, Claude will stop and ask you to register first. Re-registering is only needed if the template itself changes.

Once registered, a template joins your **pick-list**: the next time you start a deck, Claude shows you your registered templates to choose from instead of asking for a file path. The list keeps itself current — it drops templates whose files have moved or been deleted, and finds ones that sync over from OneDrive — so you don't have to remember paths.

---

## Getting Started

Open Claude Code in your session folder and just describe what you need:

```
Build me a 5-slide steering committee update.
The main message is that we are ahead of our savings target by $0.8M.
Audience: CFO and COO.
Template: _templates/client-template.pptx
```

Claude will:
1. Coach you through the deck narrative one slide at a time
2. Show you **3 design options per slide** as a visual preview
3. Ask you to pick one option per slide
4. Build the full `.pptx` with your client's branding
5. Give you the exact file path to open it

### Reviewing the built deck
After a build completes, run QC before opening the file:
```
/slide-qc
```
Claude renders every slide to PNG (LibreOffice by default; opt-in PowerPoint COM for pixel-perfect fidelity), reads them with vision, and gives you a per-slide Critical / Major / Advisory report.

### Rebuilding a single slide
```
Rebuild slide 3
```

### If you don't have all the data yet
Tell Claude what's missing — it will build the slide with clearly labeled placeholder blocks so you know exactly what to fill in before sending to the client.

---

## Getting Updates

```powershell
cd "$env:USERPROFILE\.claude\skills"
git pull
```

Then restart Claude Code.

---

## Need Help?

- **Installation problem** → [open an issue](https://github.com/mperaltajr/skills/issues/new/choose) and describe what you see
- **Something went wrong mid-session** → type `/feedback` in Claude Code — Claude will write the bug report for you
- **Suggestion** → [open an improvement suggestion](https://github.com/mperaltajr/skills/issues/new?template=improvement-suggestion.md)
