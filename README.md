# Claude Slide Lab

> AI-powered skills for building consultant-quality PowerPoint decks, Word documents, and spreadsheets, directly from Claude Code.

---

## What is Claude Slide Lab?

Claude Slide Lab is a collection of Claude Code skills that turn a narrative brief into a fully branded PowerPoint deck, complete with your client's colors, fonts, and layout. Instead of spending hours in PowerPoint, you describe what the slide should say and Claude builds it.

**What makes it different from just asking Claude to make slides:**
- Pulls colors and fonts directly from your client's `.pptx` template, no manual branding
- Designs three structurally different options for every slide (not just color variations), so you pick instead of describing; a redesign of one slide comes back as one new option
- Runs quality gates before showing you anything: a narrative gate on the storyline and hardline build rules on every slide
- Flags missing data with placeholder blocks so you know exactly what to fill in before client delivery
- Outputs a real `.pptx` file you can open, edit, and send

---

## Skills Included

| Skill | What it does |
|---|---|
| `slide-lab` | **Front door: start here for any deck request.** Routes the request to the right skill (new narrative → storyline-helper; finished package/HTML mockup → validate → slide-builder; RFP → rfp-helper; edit an existing `.pptx` → slide-builder's edit mode; QC → slide-qc) and enforces the rule: never hand-roll a deck from a blank python-pptx Presentation for a branded deck; build on the client template's layouts; a deck isn't done until slide-qc has run. |
| `storyline-helper` | Coaches your deck narrative (governing thought, audience, per-slide story) before any slides are built |
| `slide-builder` | Builds a PowerPoint deck from a narrative brief via parallel agent fanout: prep → per-slide workers produce three design options each on the first round (one on a redesign), image-first, then converted to native PowerPoint → finalize → REVIEW.html → pick → compile. Brand colors + fonts + layouts come from your registered client template. Also handles small edits to an **existing** `.pptx` Slide Lab didn't build (text/shape tweaks, extraction). |
| `slide-qc` | Renders every slide to PNG (LibreOffice by default; opt-in PowerPoint COM) and reviews them with vision, then produces a per-slide Critical / Major / Advisory report before you open the deck |
| `docx` | Word document generation: reports, memos, letters with proper formatting |
| `xlsx` | Spreadsheet creation, editing, and cleaning for any `.xlsx` / `.csv` task |
| `slidelab-log` | Generates a structured session report when something goes wrong: Claude writes the technical details, you submit it as a GitHub issue |
| `rfp-helper` | RFP / proposal response coaching: win themes, scoring criteria, section-by-section structure; produces a proposal brief that slide-builder can build from |

---

## Install (about 20 to 45 minutes the first time)

### Step 1. Install three programs yourself

Claude cannot install desktop software for you on a company laptop, so do these first. On a company PC, use your company's software portal (Software Center, Self Service or similar); otherwise use the links.

| Program | Why Slide Lab needs it | Where to get it |
|---|---|---|
| **Claude** (desktop app or Claude Code) | Runs Slide Lab | However your company provides Claude; otherwise [claude.ai/code](https://claude.ai/code) |
| **Python 3.10 or newer** | Runs the build scripts | Software portal, or [python.org](https://www.python.org/downloads/) |
| **LibreOffice** | Required. Draws slide previews during template registration, the final check page and the quality check | Software portal, or [libreoffice.org](https://www.libreoffice.org/download/). Request it on day one: on company PCs it can need approval |

Git is usually already there, because Claude Code on Windows uses it. If the setup check later says it is missing, get it from the portal or [git-scm.com](https://git-scm.com).

### Step 2. Let Claude do the rest

Open Claude and paste this:

```
Install Slide Lab for me. Clone https://github.com/mperaltajr/skills into my .claude\skills folder (~/.claude/skills on a Mac), then follow the "Doing it by hand" steps in its README.md for my computer. Run each command on its own so I can approve it, and finish by running doctor.py and showing me its table.
```

Claude asks before each download or install (your company's settings may require that). Click **Allow** each time. At the end it shows a table like this:

```
  Piece                          Status   What to do
  Python 3.12                    OK
  Python packages                OK
  Browser for rendering designs  OK
  LibreOffice                    OK
  Slide Lab agents               OK
  Claude settings                OK
  Local work folder              OK       C:\Users\<you>\Slide Lab\sessions
  Slide Lab is ready.
```

Any row that is not OK says exactly what to do.

### Step 3. Restart Claude

Close and reopen Claude so it loads Slide Lab. Then type `/slide-lab` or just ask for a deck.

### Doing it by hand (Windows, PowerShell)

Run these one at a time. Always use `py -3`, never bare `python` or `pip` (on many PCs `python` runs LibreOffice's private copy of Python).

```powershell
git clone https://github.com/mperaltajr/skills "$env:USERPROFILE\.claude\skills"
py -3 -m pip install --user -r "$env:USERPROFILE\.claude\skills\requirements.txt"
py -3 -m playwright install chromium
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\doctor.py" fix
```

- The third line downloads a browser used to draw design sketches. If your network blocks it, skip it: Slide Lab uses Microsoft Edge instead (tested to give the same results).
- The last line copies Slide Lab's two helper agents into `.claude\agents`, adds Slide Lab's permissions to `.claude\settings.json` (it adds to the file and keeps a backup, never replaces it), creates your local work folder `C:\Users\<you>\Slide Lab\sessions` with a Desktop shortcut, and prints the setup table. It never installs software.
- Restart Claude when done.

### Doing it by hand (Mac)

```bash
git clone https://github.com/mperaltajr/skills ~/.claude/skills
python3 -m pip install --user -r ~/.claude/skills/requirements.txt
python3 -m playwright install chromium
python3 ~/.claude/skills/slide-builder/scripts/doctor.py fix
```

LibreOffice is found automatically in `/Applications`. If the browser download is blocked, Google Chrome is used instead. Restart Claude when done.

### If something goes wrong

Run the setup check any time; it changes nothing and tells you what to do:

```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\doctor.py"
```

Or just tell Claude: *"check my Slide Lab setup"*.

- **"certificate verify failed" during the pip install.** Try again first; recent versions of pip use your company's certificates. Only if it keeps failing, add `--trusted-host pypi.org --trusted-host files.pythonhosted.org` to the pip line.
- **LibreOffice installed somewhere unusual.** Set the environment variable `SLIDE_LAB_SOFFICE` to the full path of `soffice.exe`. Do not add LibreOffice to your PATH.
- **A build stops saying the agents are out of date.** Run `doctor.py fix`, then restart Claude.
- **Claude keeps asking "allow?" during a build.** Run `doctor.py fix`, then restart Claude.

---

## Your first deck

### Where to keep your work

Keep session folders on your computer's own drive, not in OneDrive or Dropbox: `C:\Users\<you>\Slide Lab\sessions\<Client>\` (the setup step creates it, with a Desktop shortcut). Syncing hundreds of working files slowed builds from about 4 minutes per page to 9 to 20 and made previews time out. Copy the finished deck to OneDrive or SharePoint when you are done.

### Your client's template

The template can live anywhere. It must be a 16:9 PowerPoint at 13.333 x 7.5 inches (PowerPoint's standard widescreen). Other 16:9 sizes get a one-command fix; 4:3 templates are refused.

Register each template once (5 to 10 minutes). In Claude, say:

```
Register my template at C:\path\to\client-template.pptx
```

Claude shows you the colors it found and asks which is the main brand color, which is the highlight color and what the cover background should be, then which layouts to use for content slides and for the cover. Then it builds one sample slide: open it in PowerPoint, check the title, takeaway, footnote and source look right, and tell Claude it is fine. Your original file is never changed. Optional but recommended: give Claude 3 or 4 good pages from a real deck on that template, so designs match the client's look.

Registered templates join a pick-list, so next time you just choose from it.

### Start a deck

Start small, 5 to 8 slides. Bring the main message, the audience and your numbers or notes:

```
Build me a 6-slide steering committee update.
Main message: we are ahead of our savings target by $0.8M.
Audience: CFO and COO.
Here are my notes: ...
```

### What happens, and how long it takes

| Step | What you do | How long |
|---|---|---|
| Storyline | Answer Claude's questions; it writes a one-line-per-slide storyline and asks whether to build slides | 10 to 30 min |
| Designs | Wait. Claude designs every slide at the same time | 5 to 15 min for 10 to 20 slides (longer on OneDrive) |
| Review page | Open REVIEW.html. For each slide: **Pick** one of three designs, **Replace these** (redesign it, about 5 min), or **Leave out**. One-click feedback buttons cover common asks. Click **Build my deck** and paste the command into Claude | As long as you like |
| Final check page | Open FINAL-CHECK.html: every pick on your real template. Click **Build** | A few minutes |
| Quality check | Wait. Claude reviews every slide and fixes anything serious | 5 to 10 min |

A typical 10 to 15 slide deck takes 1 to 2 hours end to end, including your review time.

### After the deck

- **Change one slide:** "rebuild slide 3", "insert a slide after slide 4".
- **Missing data:** tell Claude what is missing; it marks placeholders so you know what to fill in.
- **Done:** say **"the deck is good"**. Slide Lab deletes the working files it no longer needs (about 90% of the folder) and keeps the deck and everything needed to edit it later. For older decks, say **"clean up my finished decks"**.

---

## Getting updates

Slide Lab checks for updates once a day when you start using it, and asks before installing: *"A Slide Lab update is available. OK to install it now?"* Say yes, and restart Claude if it asks you to. To check any time, say **"update Slide Lab"**.

(Older installs set up an automatic start-up update. Company-managed Claude ignores it, so do not rely on it.)

---

## Need help?

- **Installation problem:** run the setup check (above) and [open an issue](https://github.com/mperaltajr/skills/issues/new/choose) with its table
- **Something went wrong mid-session:** type `/slidelab-log` in Claude. It writes the bug report for you
- **Suggestion:** [open an improvement suggestion](https://github.com/mperaltajr/skills/issues/new?template=improvement-suggestion.md)
