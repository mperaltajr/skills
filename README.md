# Claude Slide Lab

> AI-powered skills for building consultant-quality PowerPoint decks, Word documents, and spreadsheets — directly from Claude Code.

---

## What is Claude Slide Lab?

Claude Slide Lab is a collection of Claude Code skills that turn a narrative brief into a fully branded PowerPoint deck — complete with your client's colors, fonts, and layout. Instead of spending hours in PowerPoint, you describe what the slide should say and Claude builds it.

**What makes it different from just asking Claude to make slides:**
- Pulls colors and fonts directly from your client's `.pptx` template — no manual branding
- Generates 3 structurally distinct design options per slide, not just 3 color variations
- Runs quality gates before showing you anything — canvas fill, takeaway dominance, story-first structure
- Flags missing data with placeholder blocks so you know exactly what to fill in before client delivery
- Outputs a real `.pptx` file you can open, edit, and send

---

## Skills Included

| Skill | What it does |
|---|---|
| `storyline-helper` | Coaches your deck narrative — governing thought, audience, per-slide story — before any slides are built |
| `slide-builder` | Builds a PowerPoint deck from a narrative brief via parallel agent fanout: prep → per-slide workers produce three python-pptx option scripts each → finalize → REVIEW.html → pick → compile. Brand colors + fonts come from your registered client template. |
| `slide-qc` | Exports every slide to PNG via PowerPoint COM and reviews them with vision — produces a per-slide PASS/WARN/FAIL report before you open the deck |
| `pptx` | General PowerPoint read / edit / create for any `.pptx` task |
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
- **LibreOffice** — [libreoffice.org](https://www.libreoffice.org) *(needed for the silent PPTX→PNG render path; defaults to `C:\Program Files\LibreOffice\`)*

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
*(Optional — only required if you use a separate HTML-mockup preview workflow outside slide-builder. The standard slide-builder pipeline does not need Chromium; it renders via LibreOffice + python-pptx.)*
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

**4. Install the Slide Lab agents** — Claude Code reads agent definitions from `~/.claude/agents/`, a separate folder from skills. Copy the four agent files there:
```powershell
if (!(Test-Path "$env:USERPROFILE\.claude\agents")) { New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\agents" | Out-Null }
Copy-Item -Path "$env:USERPROFILE\.claude\skills\agents\*.md" -Destination "$env:USERPROFILE\.claude\agents\" -Force
```
This installs `deck-builder`, `slide-designer`, `slide-builder`, and `slide-builder-worker` — the four subagents the deck pipeline uses for parallel work. See `agents/README.md` for what each one does and how to symlink instead of copy if you want auto-sync on `git pull`.

**5. Restart Claude Code.** The skills and agents are now active.

**6. *(Optional)* Verify the install with the end-to-end smoke test:**
```powershell
cd "$env:USERPROFILE\.claude\skills"
py -3 smoke_test.py
```
The script builds a 3-slide test deck on a generic template, runs brief-time + render-time QC, and renders PNGs via LibreOffice. Should print `RESULT: PASS` and produce files under `_smoke_out/`. If any step fails, the traceback points at the broken piece.

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
Claude exports every slide to PNG, reads them with vision, and gives you a per-slide PASS/WARN/FAIL report. Requires Microsoft PowerPoint to be installed.

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
