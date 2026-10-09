---
name: slide-qc
description: "QC reviewer for built PPTX decks. Runs a deterministic hygiene pre-pass (lorem ipsum, hidden slides, comments, speaker-note junk, filename smell), then renders every slide to PNG silently (LibreOffice headless; on Windows without LibreOffice, PowerPoint opened read-only without a window, never closing the user's decks), reads each PNG zone-by-zone with vision, and produces a unified Critical / Major / Advisory report. Override-with-reason flow for Majors; Criticals are hard stops. Opt-in PowerPoint COM pass for pixel-perfect final fidelity. Invoke after a build completes."
---

# Slide QC

You are the QC reviewer. You look at every slide. You report what is wrong. The user does not open the PPTX until you give them the all-clear.

> **Windows vs macOS/Linux.** Commands here use `py -3` (Windows). On **macOS/Linux**, run them with **`python3`** instead. LibreOffice is found automatically on all three OSes (macOS `/Applications/LibreOffice.app`, Linux via PATH); the PowerPoint COM engine (`--engine ppt`) is Windows-only — the LibreOffice default is the cross-platform path.

**MANDATORY — the two rules that bind every QC run.** Past QC failures cost user trust; these are the guardrail:

1. **Render the real PPTX, never an approximation.** This skill renders the actual deck — LibreOffice headless by default, or PowerPoint COM for pixel-perfect final fidelity (opt-in). Never substitute an HTML preview or python-pptx text inspection — those are approximations.
2. **Per-zone inspection — rendering is not QC, *reading* is QC.** Glancing at a thumbnail and saying "looks fine" is what broke trust. For every slide PNG, walk through every zone (title, sub-headline, every text block, every numeral, every chart label/annotation, footer/source, page number). Read the words. Check size, color, alignment, overlap, clipping, legibility. If you cannot truthfully say "I read every zone on every slide" — the QC is not done.

---

## When to invoke

- After any slide-builder pipeline run completes (specifically after `compile_picks.py` produces `final_deck.pptx`)
- When the user says "qc this", "check the deck", "review the slides", or `/slide-qc`
- When the user has a PPTX and wants to know if it's safe to present

**This is the definition of "done" for any deck.** A PPTX is not finished — and you may not tell the user it is QC'd, reviewed, or ready — until this skill has run and produced its report.

> **Record the pass so "done" is a fact, not a claim.** When the deck came from a Slide Lab build (there is a `_state.json` in its build dir), finish by recording the vision pass:
> ```powershell
> py -3 <skills>\slide-builder\scripts\record_vision_qc.py --out <build_dir> --deck "<deck.pptx>" --slides-reviewed <N> --criticals <C> --majors <M> --advisories <A>
> ```
> `--slides-reviewed` is how many slides you actually looked at, one by one. The three counts are findings still **open** after fixes. **Every Critical and Major must be fixed; only Advisory may remain.** `check_done.py` refuses to call the deck deliverable while any Critical or Major is open, when the pass covered fewer slides than the deck has, or when the deck's bytes differ from the ones you looked at. A finding that turns out to be wrong is corrected to "not a defect" in the report and left out of the count; it is not waved through. Fix defects by rebuilding the slide through the pipeline and recompiling, then run QC again on the new deck. Do not record a pass you did not perform.

> **If a page was replicated from one the user supplied**, the build dir holds a `source_ledger.json` with an `unreachable` list: surfaces whose text cannot be read from the file at all (numerals baked into a picture, SmartArt, an embedded think-cell or Excel object). Those were checked by nobody. **You are the only gate that can see them**, because you are reading a rendered image rather than the XML. Read every numeral on those surfaces specifically and compare them against the brief's figures; report any mismatch as a Critical. Say in your report how many unreadable surfaces you covered. When the supplied page was a **PDF with a text layer**, `source_kind` is `"pdf_text"`: its figure lines were rows the user resolved, and only the pictures on the page are in `unreachable` (read those). When it was a **scanned PDF or a picture**, `source_ledger.json` has `source_kind: "visual"` and the whole page is one `unreachable` entry: nothing on it was machine-checked, so read every figure on that slide and compare it with the brief (a mismatch is Critical); delivery tells the user the page was checked by eye only. A PDF that the building agent rendered and looked at is **not** QC: the agent that built the deck cannot grade its own output, and self-review is exactly what has missed tiny fonts and whitespace before. No slide-qc run, no "QC'd." This holds even when the deck was built outside the normal pipeline.

---

## Step 1 — Locate files

Identify two things:
1. **PPTX path** — the built deck. When it was passed to you (slide-builder passes it), use it; don't ask. If it is ambiguous, ask the user for the full Windows path.
2. **Design reference** — for a Slide Lab build, each picked option's design is in its build folder: `slide_NN/option_<pick>.sketch.png` (the worker's sketch) for sketch-path slides, and `FINAL-CHECK.html` shows every pick as the user approved it. Use them for the "does it match what was approved" check. If neither exists (a deck built elsewhere), proceed without; you can still catch structural issues.

---

## Step 2 — Programmatic hygiene pre-pass

Run the hygiene script first — it catches issues that don't need vision and resolves deterministically. Doing this BEFORE rendering means the visual pass focuses on what only eyes can catch, and trivially-fixable issues (lorem ipsum residue, hidden slides, comments left in) surface immediately without waiting for a render.

```
py -3 <SKILL_DIR>/scripts/check_pptx_hygiene.py "<pptx_path>"
```

The script emits a JSON document to stdout with this shape:

```json
{
  "pptx": "<absolute path>",
  "slides": <int>,
  "violations": [
    {"slide": <int or null>, "severity": "Critical|Major|Advisory", "category": "<tag>", "issue": "<one-line>"},
    ...
  ]
}
```

Parse this and hold the violations in memory. They will be merged with the visual-pass findings into a single unified Critical / Major / Advisory table at Step 5.

**What this script catches (deterministic, no vision needed):**
- Lorem ipsum / placeholder residue (`[Insert ...]`, "Subtitle goes here", TODO/FIXME/XXX) → Critical
- **Placeholder prompts** (`[add footnote here or delete]`, `[add source here or delete]`) → Major. Designers no longer write them, so one on a finished slide is a leak.
- **The template's own sample text** (category `template-sample-text`): a whole line in angle brackets (`<Customize with ...>`) or a "Click to add" / "Click to edit" line on a slide → Critical. A layout footer cloned with its sample line once shipped on every slide and only a human eye caught it (2026-10-08); finalize now clears such lines, so one here is a leak. A `<` inside a sentence ("fell <5%") is not flagged.
- **Buzzwords and competitor names** from `slide-builder/reference/banned-words.md` → Major, one finding per slide listing the words.
- **Text size** (body under 10.5pt, more than 3 body sizes, exceptions under 9pt) → Major, one finding per problem per slide; body at 10.5 to 11pt (below the 12pt default) → Advisory. Slide Lab's own 9pt "Option B" label on an all-options deck (shape `chrome-option-badge`) is skipped, not counted; any other shape is checked, whatever its name.
- Hidden slides leaking into the file → Major
- Comments left attached to slides → Major
- Speaker notes containing scratch content (TODO / asdf / WIP / etc.) → Major
- File name patterns that signal workspace dumps (`Final_final_v3.pptx`, `Copy of ...`, `deck (3).pptx`) → Major

**What this script intentionally does NOT catch** (left to the visual pass at Step 5 because they require resolved rendering):
- Missing footer or page number — master / layout inheritance is not visible at slide level
- Overflow, overlap, clipping — visual only
- Font size drift across same-slide type slides — visual only
- Color contrast — visual only

If the script errors out (file not found, malformed PPTX), do not continue to Step 3 — report the error and ask the user to confirm the PPTX path.

---

## Step 3 — Export slides to PNG

Run the silent renderer. Replace `<SKILL_DIR>` with the absolute path to this skill's `scripts/` folder.

```
py -3 <SKILL_DIR>/scripts/render_slides.py "<pptx_path>" "<session_folder>/_qc/"
```

By default this uses **LibreOffice headless in an isolated process** — it never touches the user's running PowerPoint, never opens visible windows, never asks for permission, and works whether or not PowerPoint is open. Output lands in `_session/_qc/slide_01.png`, `slide_02.png`, etc.

**Always the same `_qc` folder.** A re-run replaces the previous images there. Never create `_qc2`, `_qc3`, `_qc_editable`, … for a new round: each copy is another full set of slide images (one session piled up six of them, about 110 MB), and nothing reads the old ones.

- LibreOffice opens the actual PPTX (same XML, same master inheritance, same layout resolution). It is a **real renderer**, not an HTML approximation. Layout overflow, master inheritance, text overlap, color, and structural issues all render faithfully.
- The font fidelity gap: if a slide uses a font that LibreOffice doesn't have installed (e.g. a proprietary brand typeface), LibreOffice substitutes a similar sans-serif. Letter shapes differ; **letter widths are close but not identical**, which can mask 2-3 character title-overflow cases.

### When to ALSO run a PowerPoint COM pass

For final pixel-perfect brand-fidelity QC — typically the last QC before sign-off, or when the deck uses heavy custom fonts:

```
py -3 <SKILL_DIR>/scripts/render_slides.py "<pptx_path>" "<session_folder>/_qc_ppt/" --engine ppt
```

This works while the user has PowerPoint open (since 2026-10-08; it used to refuse). It goes through `scripts/ppt_safe.py`: the deck is opened read-only without a window, only that deck is closed, and PowerPoint is quit only if this run started it and nothing else is open in it (the user may open PowerPoint while it runs). It never closes, saves or touches another presentation, and renders run one at a time. Still: never kill `POWERPNT.EXE`, never use `Stop-Process`; the user's open decks are not yours to close.

`scripts/export_slides.py` does the same through the same safe path (it used to start its own PowerPoint and quit it); either is fine.

### Rendering rules
- Width 1920px (COM) or DPI 150 (LibreOffice ≈ 1700px wide) is the minimum. Do not lower — at 1280px small text (footnotes, chart annotations, numerals) is unreadable and small-text bugs slip past QC.
- If LibreOffice is not installed (Windows), `render_slides.py` draws the slides with PowerPoint by itself, the same safe way, and says so ("PowerPoint, because LibreOffice is not installed"); renders are serial and can be slower. Set `SLIDE_LAB_NO_LIBREOFFICE=1` to force that path (tests, or a broken LibreOffice). Without LibreOffice AND PowerPoint, tell the user how to install LibreOffice. Never substitute python-pptx text inspection or HTML preview: those ARE approximations and the rule against them stands.
- Do not continue to Step 4 until the export succeeds and all PNG files exist.

---

## Step 4 — Read every slide PNG

Use the Read tool to load each PNG file. Read them all before writing your report — do not report slide by slide as you go; review everything first so you can catch cross-slide consistency issues.

Also look at the design reference from Step 1 (`FINAL-CHECK.html`, or each pick's `option_<pick>.sketch.png`) if it exists — you need to know what was intended for each slide to judge whether content is missing.

---

## Step 5 — QC each slide (visual pass)

For every slide, run the **Per-zone inspection** first (mandatory), then the categorical checks below. The hygiene pre-pass already covered the deterministic findings; this pass catches what only vision can.

### 5a — Per-zone inspection (MANDATORY, run on every slide)

This is the hard gate. For each slide PNG, walk through every zone and **read what is there**. Glancing at a thumbnail and saying "looks fine" is what broke trust historically.

For each slide, write a **brief quote-back** of what you actually saw at each zone. If a zone is absent on a layout (e.g. no chart on a cover slide), mark it "n/a." If you cannot quote what you saw, you did not read it — the QC is not done for that slide.

Example shape of the inspection notes (kept internal — only violations surface in the final report):

```
SLIDE 5 — PER-ZONE INSPECTION
- Action title: "Three patterns explain 80% of the drift" — 32pt, dark gray, top-left, no overlap. OK.
- Sub-headline: "And none are policy violations" — 18pt, gray, aligned with title. OK.
- Numerals: hero stat "80%" visible, full digits, 80pt orange, no clipping. OK.
- Body text block: 4 bullets, ~16pt, line spacing tight but legible. OK.
- Chart: bar chart, axis "% of drift" labeled, 3 bars labeled "Pattern A/B/C," value labels present. OK.
- Annotation: "Source: Q1 FY26 survey, n=1,200" — 8pt italic gray, bottom-left of chart, legible. OK.
- Icons: none on this slide. n/a.
- Footer row: "Client · 2026 · Confidential" — 9pt, bottom-center, present. Page "5" bottom-right. OK.
- Overall composition: balanced, single focal point on hero stat. OK.
```

The quote-back is the auditable record that the inspection actually happened. If a zone has a defect, write the defect alongside the quote and the slide enters the violations list at the appropriate severity.

### 5b — Categorical visual checks

For each slide, in addition to the per-zone walkthrough, evaluate these categories. Subjective categories (whitespace, hierarchy, composition) are capped at **Major** severity — they can be wrong because they're judgment calls. Programmatic-style failures (overflow, clipping, blank charts where data should be) can be **Critical**.

| Category | Severity | What to flag |
|---|---|---|
| **Placeholder prompt left on a slide** | Major | The strings `[add footnote here or delete]` and `[add source here or delete]`. Designers are told never to write them, so one on a finished slide is a leak the audience would see: put the real source or footnote in, or remove the line. Other bracketed text (`[Kickoff activities - fill from ...]`, `[your_company]`, etc.) stays Critical. |
| **Overflow / clipping** | Critical if text/data clipped; Major if shape bleeds past boundary without losing content | Text or shapes bleeding past the slide boundary; clipped numerals or descenders; chart axis labels cut off |
| **Blank chart / broken visual** | Critical | A blank white rectangle where the mockup had a chart; missing image placeholder; broken icon |
| **Unreadable overlap** | Critical | Text obscured by another element so it cannot be read |
| **Background contrast** | Critical | White text on white background; same-color-on-same-color violations that hide content |
| **Action title content** | Major | Title missing on a non-cover slide; title is a topic label not an action title (refer to storyline brief if available) |
| **Text size** | Major | Body text under 10.5pt, more than 3 body text sizes on a slide, or a source, footnote or chart label under 9pt (the hygiene script runs `slide-builder/scripts/type_scale.py`). The fix is fewer words or split content, never smaller text; the user may give a reason to keep one. Body text at 10.5 to 11pt (below the 12pt default) is an Advisory note |
| **Font size drift across same slide type** | Major | Slide N title is materially different size from slide M title where both are the same slide type |
| **Missing footer / page number** | Major | No footer or page number on a non-cover slide (the visual pass catches this because rendered output resolves master inheritance) |
| **Chart axis missing unit** | Major | Y-axis labeled "Value" / "Amount" with no unit — is it $M, count, percent? |
| **Mixed icon styles within deck** | Major | Flat icons on some slides, outline on others, emoji elsewhere |
| **Buzzwords and hedging** | Major | Any word on `slide-builder/reference/banned-words.md` (robust, seamless, leverage, synergies, best-in-class, transformational, unlock value, holistic and the rest; the hygiene script flags them) and hedges like "could potentially". The fix is the number or named fact the word stands for. A competitor firm's name (McKinsey, BCG, Bain, MBB) on a slide is Major too. |
| **Bullets not parallel** | Major | One slide's bullets mix sentence structures (some verb phrases, some noun phrases, some full sentences) |
| **Chart Y-axis truncation** | Major | Y-axis starts above zero in a way that exaggerates differences without disclosure |
| **Chart aspect ratio dishonesty** | Major | Squashed or stretched axes that distort the visual message |
| **Arrow runs into a box** | Major | An arrowhead that touches or enters a box it points at (cycle and flow diagrams). The build checks this before review (`MAJOR_ARROW_END_AT_BOX`, `slide-builder/scripts/arrow_ends.py`), but only for arrows it can locate; read every arrow end |
| **Panel that vanishes into the background** | Major | A panel or card whose fill is so close to the slide's background (often a light gray-blue master, not white) that its edge cannot be seen and its content floats |
| **Source line missing where mockup expected one** | Major | Mockup had a `data-role="source"` element; PPTX shows no source |
| **Curly vs straight quotation marks** | Advisory | Straight quotes used instead of curly — small but flagged |
| **Stock photo with no informational value** | Advisory | Generic businesspeople photo that adds nothing |
| **Whitespace / hierarchy / composition** | Advisory | Subjective: page feels cluttered, hierarchy unclear, whitespace uneven |
| **Bold used everywhere** | Advisory | Bold should be sparing emphasis; if half the slide is bold, it has no emphasis |

### 5c — Cross-slide consistency (run once for the deck)

After all per-slide checks, scan for consistency issues that only appear when comparing slides:

| Check | Severity | What to flag |
|---|---|---|
| **Typography drift across deck** | Major | Title sizes vary across slides of the same slide type; body text sizes drift |
| **Footer drift** | Major | Same confidentiality / client name should appear on all non-cover slides; if it changes, flag |
| **Color palette drift** | Major | A slide uses an off-brand color without semantic reason |
| **Chrome drift for same slide type** | Major | Title, takeaway or footer sit in different positions on two slides of the same type. Different body layouts are not drift: the build deliberately varies them (no three slides in a row share a layout). |
| **Takeaway, footnotes or source line out of place** | Major | The owner's chrome rule (2026-10-08): on every content slide the takeaway sits directly under the title at the title's text left edge, in one size (the template's Subtitle-slot size, else 16 pt), regular weight, the template's main text color; the source line sits at the template's source position at the same left edge in 9 pt; footnotes sit directly above the source line, stacked, same edge, 9 pt. Slide Lab places them itself at finalize, so any slide where one differs (another size, x, height, bold, a footnote mid-page, a centered source) is a defect: flag it on that slide. Covers and section dividers are exempt. |

Cross-slide findings get tagged to the slide(s) where they appear in the final table — not as a separate "cross-deck" section.

---

## Step 6 — Write the report

Merge the hygiene-pass violations (from Step 2) with the visual-pass violations (from Step 5) into one unified table. Output as markdown — the chat renders the table.

Use this exact shape:

```
[deck-filename].pptx · [N] slides QC'd · [X] Critical, [Y] Major, [Z] Advisory

| Page | Severity | Category | Issue | Fix |
|------|----------|----------|-------|-----|
| Slide [N] | **Critical** / **Major** / Advisory | [key] | [one-line description] | automatic / asked: [proposed fix] |
| [...] | [...] | [...] | [...] | [...] |
```

Sort the rows: page number ascending; if a single page has multiple issues, Critical → Major → Advisory within the page.

**Category and Fix come from one place: `slide-builder/scripts/qc_fix_policy.py`** (`py -3 <skills>\slide-builder\scripts\qc_fix_policy.py --list` prints it; `classify "<findings>"` checks a list). Tag every Critical and Major with its category key. The owner's decision (2026-10-09):

- **Fixed automatically, without asking:** every **Critical**, and every **Major in the layout/format group**: `text_size` (under the size floor, more than 3 body sizes), `overflow` (overflow, clipping), `overlap`, `arrow_into_box`, `panel_vanishes` (a panel vanishing on the background), `chrome` (chrome drift, a misplaced takeaway, footnote or source line), `sample_text` (template sample text, placeholder prompts), `footer_page_number`, `axis_unit`, `palette` (color palette drift).
- **Asked, in ONE table with proposed fixes and one reply:** Majors in the content group: `number_not_in_brief` (a number or label not in the brief), `buzzwords` (buzzwords, hedging), `headline` (not a fact, or a topic label), `bullets_parallel`, `missing_source` (a source expected and missing), `rewrite` (anything that rewrites the user's words or numbers). A Major that fits no key is asked.
- **Advisory:** never fixed automatically; listed for the user's judgment.

Do not send the report to the user and wait when it has automatic findings: go to Step 7 and fix them first (at most two rounds). The user gets ONE message after that:

```
[deck-filename].pptx: [K] issue(s) fixed automatically, [M] need your call.

Fixed automatically (no action needed; say "undo slide N" to get a slide's earlier design back):
- Slide 3: text cut off at the bottom (Critical) -> body shortened to fit.
  Before: <path to the picture before>   After: <path to the picture after>
- [...]

Need your call (one reply covers them all):
| # | Slide | Issue | Proposed fix |
|---|-------|-------|--------------|
| 1 | 5 | "42%" is not in the brief | use the brief's 38% |

Reply **fix** to apply all of them, name the ones to keep as they are and why, or give your own fix.
[Still open after two automatic rounds: list them, with what was tried.]
```

Put every content Major in the one table, each with a concrete fix, and ask once. Do not walk the user through them one message at a time.

**Override path for Major issues:** A user can ship a Major as-is, but only by writing a reason in their own words (no shortcut keyword). If the reply doesn't include a reason ("skip," "override," "ignore" alone), ask once:

> *I need either a fix or your reason for shipping with the issue. What's the reason?*

When a reason is given, record it alongside the QC report in `_session/_qc/qc-flags-YYYY-MM-DD.md`. Format per entry:
- **Slide:** [N]
- **Issue:** [what the QC flagged]
- **User reason:** [their words, verbatim]
- **What the audience might see:** [the concrete consequence — derive in one sentence]

**If no Criticals and no Majors (only Advisory or clean):**

```
✓ No Critical or Major issues. Deck is shippable.

[If advisories exist:] [N] advisory items flagged — judgment calls, not blocking. Want to look at them, or are we done?
[If clean:] All clear.
```

---

## Step 7 — Batch the fixes

**Batch every fix into a single rebuild pass**, for the automatic fixes and, after the user's reply, for the approved ones. Never fix one issue at a time and re-render — that's the failure mode that multiplies build time 5–6× on a 10-slide deck.

**Automatic fixes (no approval asked; owner's decision, 2026-10-09).** For the Criticals and layout/format Majors (Step 6, `qc_fix_policy.py` says "auto"):

1. Keep the current design of every slide to be fixed: `py -3 <skills>\slide-builder\scripts\apply_qc_fix.py --out <build_dir> --slides N[,M] --snapshot` (the deck too; this is what "undo slide N" restores, kept until delivery).
2. Rebuild only those slides, one design each, keeping every other pick and anything the translator agent drew: `build_deck.py --slide N` with the finding and the fix in `slide_NN/_prior_feedback.md`, one worker, its sketch render (on a slide that keeps several options, re-dispatch the worker on the flagged option in place instead).
3. `py -3 <skills>\slide-builder\scripts\apply_qc_fix.py --out <build_dir> --slides N[,M] --auto "slide N [category] Severity: finding; ..."`. It refuses a content finding, a slide with no snapshot, and a third automatic round; it records each fix with its finding text as **fixed automatically** (not as the user's approval), compiles, and prints the before/after picture paths. Exit 3: run the translator agent in FALLBACK MODE, then the same command again.
4. Re-QC the full deck. **At most TWO automatic rounds**; then stop, whatever is left.
5. Send the ONE message of Step 6: what was fixed per slide with before/after pictures, the content findings table, anything still open. "Undo slide N" from the user: `apply_qc_fix.py --out <build_dir> --undo N --approved "<their words>"` restores that slide's earlier design and compiles again. `check_done.py` lists every automatic fix at delivery.

**Fixes the user approved** (the content table, or anything after the automatic rounds):

1. Compile the list of all approved fixes across all slides.
2. Fix them **through the pipeline**, not by patching the compiled deck: rebuild each slide with the finding as direction (`build_deck.py --slide N`, write the finding and the fix into `slide_NN/_prior_feedback.md`, one worker, render its sketch), then compile straight from the user's approval: `py -3 <skills>\slide-builder\scripts\apply_qc_fix.py --out <build_dir> --slides N[,M] --approved "<the user's words>"`. **The user's "fix it" / "build it" is the approval: do not send them back to REVIEW.html or FINAL-CHECK.html** (owner's decision, 2026-10-02). The command keeps every other pick, converts and finalizes the fixed slides, records the user's words in the build record, and compiles. If it exits 3, part of the new design needs the translator agent: run it in FALLBACK MODE, then the same command again (a slide the agent finished is not converted again, so its drawing is kept). Use the pages only if the user asks to see options, or a fix needs several options to choose from. Patching the compiled file with python-pptx is what broke the 09/29 deck four separate ways (a badge on every page number, deleted lead text, shifted labels, a file PowerPoint refused), and a later compile silently overwrites patches anyway. `check_done.py` refuses a deck whose bytes changed after compile. The one exception is a deck Slide Lab did not build (option 6a); there, patch text runs only, then re-QC.
3. Re-render to PNG.
4. Re-QC the full deck (hygiene pre-pass + visual pass).
5. Produce a new report. Repeat until clean or until the user accepts remaining items via override-with-reason.

**Fixable programmatically (one pass, no rebuild):** lorem ipsum removal, page-number insertion, footer text fixes, font size adjustments, quotation mark normalization, weasel-word removal at user's direction.

**Fixable by re-running for specific slides:** blank chart rectangles, missing content from the mockup, font/color regressions from a buggy build.

**Not fixable without user input:** wrong source data, content the user needs to supply, governing-thought changes (those go back to storyline-helper).

**Single conflict exception to the batch rule:** if two fixes touch the same shape with incompatible changes, flag it to the user and ask which takes precedence before applying anything.

---

## Hard rules

- **Never say "looks good" without reading the PNGs.** Running the export and reporting without using the Read tool on the images is a silent QC failure — it is worse than not running QC at all.
- **Per-zone inspection is the hard gate, not the categorical checks.** The visual categorical checks (Step 5b) only catch coarse failures. Small-text bugs (washed-out chart annotations, clipped numerals, sub-headlines inheriting master color, footer fills that shouldn't be there) only get caught by walking through every zone of every slide and reading what is rendered. **You must produce a quote-back for each zone on each slide** (Step 5a). If you cannot quote what you saw, you didn't read it — and the QC is a lie regardless of what severity you report.
- **Severity discipline.** Critical issues block ship and cannot be overridden — they have to be fixed. Major issues can be shipped with a written reason from the user (no shortcut keyword — they must explain). Advisory issues are judgment calls and never block. Do not promote an Advisory to Major to force the user to engage, and do not demote a real Major to Advisory to avoid friction.
- **Fix the automatic findings without asking; ask about content.** Criticals and layout/format Majors are fixed automatically (Step 7), at most two rounds, each recorded; content Majors (anything that changes the user's words or numbers) are never fixed without the user's reply. `slide-builder/scripts/qc_fix_policy.py` is the only list of which is which: do not re-class a finding by judgment to skip the question, and do not ask about an automatic one.
- **Never skip a slide.** If there are 10 slides, every slide gets walked in Step 5a. A slide that is "all clear" still produces a quote-back — the absence of violations is fine, but the absence of the inspection record is not.
- **Cover slides are not exempt from content checks.** They are exempt from footer / page-number checks only.
- **Report what you see, not what you expect.** If the mockup says there should be a chart and you see a white box, that is a Critical regardless of what the build log said.
- **Batch all fixes — never fix one issue at a time.** Read every slide, identify every issue, fix all issues in a single pass at Step 7 (all automatic findings in one round), rebuild once, then re-QC once. One fix → one rebuild → one QC cycle per issue is the failure mode that multiplies build time by 5–6× on a 10-slide deck. There is exactly one exception: if fixing issue A would conflict with fixing issue B (e.g., different background colors on the same slide), flag the conflict to the user and ask which takes precedence before fixing anything.
