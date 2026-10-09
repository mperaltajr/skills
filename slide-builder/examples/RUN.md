# Running the quickstart

This example uses `quickstart-brief.md` (4 slides) and any registered client PPTX template you have on hand.

## What you need

- A registered **and confirmed** client template — a `.pptx` file with a `<stem>/` template-settings subfolder next to it (containing `brand.yml` and `theme.json`).
- The verification step from INSTALL.md passing.

## If you don't have a registered template yet (do this first)

Slide Lab can't build against a raw `.pptx`; it builds against a *registered* template (one with `brand.yml` + `theme.json` + `chrome.yml` template-settings files capturing the client's colors, fonts, layouts). Registration is a one-time chat step per template. In Claude, say:

> Register this template: <path to your template.pptx>

Claude shows you the colors it found (with a plain name, the color code, and where each one appears) and asks, one question at a time:

1. **Which is the main brand color?**
2. **Which is the highlight color?**
3. **What should the cover background be?**
4. **Which layout should content slides use by default?** (it shows you the layouts as pictures)
5. **Which layout is the cover?**
6. **Optionally, which slide in the template is the best example of a content page?** Recommended when your template has specific title and footer placement.

Claude never pre-picks the colors: the automatic guess was wrong on every template registered so far (often the main and highlight colors swapped).

Then **confirm** it. Registration builds a mock slide (`<stem>/selftest/mock.pptx`); open it in PowerPoint and check that the title, takeaway, footnote and source land where they should. Once a person has looked:

```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\register_template.py" confirm `
    "<path to your template.pptx>"
```

Prep refuses to build on an unconfirmed template (exit 12). The template-settings files sit in a `<stem>/` subfolder next to the `.pptx`; you only repeat this if the template's master or layouts change.

For the full registration flow, see SKILL.md § "Register a new client template."

## The full sequence

Every step below either runs a script or waits for you. The two waits are real: nothing compiles until you have picked on the review page and looked at the finished slides on the final check page.

```powershell
$skill    = "$env:USERPROFILE\.claude\skills\slide-builder"
$session  = "$env:USERPROFILE\Documents\slide-lab-quickstart"
$template = "<path to your registered, confirmed template.pptx>"
New-Item -ItemType Directory -Force -Path "$session" | Out-Null

# 1. Your own copy of the brief, sealed. In a real build storyline-helper
#    does this when the brief passes its quality gate; a typed marker is refused.
Copy-Item "$skill\examples\quickstart-brief.md" "$session\brief.md"
py -3 "$skill\scripts\seal_brief.py" --brief "$session\brief.md"

# 2. Prep: one prompt per slide, plus dispatch_plan.md
py -3 "$skill\scripts\build_deck.py" --brief "$session\brief.md" `
    --template "$template" --out "$session\out"
```

**3. Designs (Claude does this).** Ask Claude to dispatch one `slide-builder-worker` per slide from `dispatch_plan.md` (at most 20 at a time). Each writes its option(s): `.py` for direct-path slides, `.html` for sketch-path slides (rendered to `option_X.sketch.png`).

```powershell
# 4. Put the direct-path options on the template, so the review shows them finished
py -3 "$skill\scripts\finalize_deck.py" --out "$session\out" --template "$template"

# 5. The review page
py -3 "$skill\scripts\build_review.py" --out "$session\out"
```

**6. You pick.** Open `$session\out\REVIEW.html`. Pick an option on every slide (or **Replace these** to get new designs, or **Leave out** to drop it), then click **Build my deck** and paste what it copies into Claude. That command runs `record_picks.py`, which records exactly your picks. (When Claude opened the page with `build_review.py --open`, you can also type the picks in chat, such as "use 1B 2C"; to keep two options of a slide, name both letters, "1BC".)

**7. Claude converts only your picked sketches** (one `slide-builder-translator` each), then runs:

```powershell
py -3 "$skill\scripts\finalize_deck.py" --out "$session\out" --template "$template"
py -3 "$skill\scripts\build_review.py" --out "$session\out" --final
```

**8. You look at the finished slides.** Open `$session\out\FINAL-CHECK.html`: every pick, on your template, with its real title and page number. If it is right, click **Build it** and paste the command into Claude (or, when Claude opened it with `--final --open`, just say "build it"). It compiles the deck into `$session\out`, named after the topic (one deck; `final_deck.pptx` only when the brief has no title).

**9. QC, then done.** Claude runs slide-qc on the deck, records the pass, and runs:

```powershell
py -3 "$skill\scripts\check_done.py" --out "$session\out"
```

The deck is done only when that prints DELIVERABLE.

## Expected total time

A 4-slide deck: a few minutes of scripts, plus agent time for the designs (usually under two minutes for 4 in parallel) and the translation of any picked sketches, plus however long you take on the two review pages.
