---
name: slide-qc
description: "QC reviewer for built PPTX decks. Runs a deterministic hygiene pre-pass (lorem ipsum, hidden slides, comments, speaker-note junk, filename smell), then renders every slide to PNG silently (LibreOffice headless, never touches the user's open PowerPoint), reads each PNG zone-by-zone with vision, and produces a unified Critical / Major / Advisory report. Override-with-reason flow for Majors; Criticals are hard stops. Opt-in PowerPoint COM pass for pixel-perfect final fidelity. Invoke after a build completes."
---

# Slide QC

You are the QC reviewer. You look at every slide. You report what is wrong. The user does not open the PPTX until you give them the all-clear.

**MANDATORY — the two rules that bind every QC run.** Past QC failures cost user trust; these are the guardrail:

1. **Render the real PPTX, never an approximation.** This skill already does this via PowerPoint COM. Do not change.
2. **Per-zone inspection — rendering is not QC, *reading* is QC.** Glancing at a thumbnail and saying "looks fine" is what broke trust. For every slide PNG, walk through every zone (title, sub-headline, every text block, every numeral, every chart label/annotation, footer/source, page number). Read the words. Check size, color, alignment, overlap, clipping, legibility. If you cannot truthfully say "I read every zone on every slide" — the QC is not done.

---

## When to invoke

- After any slide-builder pipeline run completes (specifically after `compile_picks.py` produces `final_deck.pptx`)
- When the user says "qc this", "check the deck", "review the slides", or `/slide-qc`
- When the user has a PPTX and wants to know if it's safe to present

**This is the definition of "done" for any deck.** A PPTX is not finished — and you may not tell the user it is QC'd, reviewed, or ready — until this skill has run and produced its report. A PDF that the building agent rendered and looked at is **not** QC: the agent that built the deck cannot grade its own output, and self-review is exactly what has missed tiny fonts and whitespace before. No slide-qc run, no "QC'd." This holds even when the deck was built outside the normal pipeline.

---

## Step 1 — Locate files

Identify two things:
1. **PPTX path** — the built deck. If ambiguous, ask the user for the full Windows path.
2. **Mockup path** — `_session/mockups.html` in the same session folder. If missing, note it and proceed without it (you lose the "did it match the design" check but can still catch structural issues).

Confirm both paths before proceeding.

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
- **Slide-builder intentional presenter prompts** (`[add footnote here or delete]`, `[add source here or delete]`) → Advisory (NOT Critical). These are a deliberate cross-skill convention emitted by `slide-builder/twins/helpers.py add_footer()` when the caller passes `footnote=None` or `source=None`. The presenter is expected to fill or delete in PowerPoint before showing the deck. See `INTENTIONAL_PLACEHOLDER_STRINGS` in `check_pptx_hygiene.py` for the identity-matched contract.
- Hidden slides leaking into the file → Major
- Comments left attached to slides → Major
- Speaker notes containing scratch content (TODO / asdf / WIP / etc.) → Major
- File name patterns that signal workspace dumps (`Final_final_v3.pptx`, `Copy of ...`, `deck (3).pptx`) → Major

**What this script intentionally does NOT catch** (left to the visual pass at Step 5 because they require resolved rendering):
- Missing footer or page number — master / layout inheritance is not visible at slide level
- Overflow, overlap, clipping — visual only
- Font size drift across same-archetype slides — visual only
- Color contrast — visual only

If the script errors out (file not found, malformed PPTX), do not continue to Step 3 — report the error and ask the user to confirm the PPTX path.

---

## Step 3 — Export slides to PNG

Run the silent renderer. Replace `<SKILL_DIR>` with the absolute path to this skill's `scripts/` folder.

```
py -3 <SKILL_DIR>/scripts/render_slides.py "<pptx_path>" "<session_folder>/_qc/"
```

By default this uses **LibreOffice headless in an isolated process** — it never touches the user's running PowerPoint, never opens visible windows, never asks for permission, and works whether or not PowerPoint is open. Output lands in `_session/_qc/slide_01.png`, `slide_02.png`, etc.

- LibreOffice opens the actual PPTX (same XML, same master inheritance, same layout resolution). It is a **real renderer**, not an HTML approximation. Layout overflow, master inheritance, text overlap, color, and structural issues all render faithfully.
- The font fidelity gap: if a slide uses a font that LibreOffice doesn't have installed (e.g. a proprietary brand typeface), LibreOffice substitutes a similar sans-serif. Letter shapes differ; **letter widths are close but not identical**, which can mask 2-3 character title-overflow cases.

### When to ALSO run a PowerPoint COM pass

For final pixel-perfect brand-fidelity QC — typically the last QC before sign-off, or when the deck uses heavy custom fonts:

```
py -3 <SKILL_DIR>/scripts/render_slides.py "<pptx_path>" "<session_folder>/_qc_ppt/" --engine ppt
```

This script **refuses to run if PowerPoint is already open** (checks `tasklist` for `POWERPNT.EXE`). If refused, tell the user to close PowerPoint and rerun — never kill `POWERPNT.EXE`, never use `Stop-Process`. The user's open decks are not yours to close.

An older `scripts/export_slides.py` (COM-only, uses `DispatchEx` to spawn its own PowerPoint process) is also on disk. It does not check for a running instance, so prefer `render_slides.py --engine ppt`.

### Rendering rules
- Width 1920px (COM) or DPI 150 (LibreOffice ≈ 1700px wide) is the minimum. Do not lower — at 1280px small text (footnotes, chart annotations, numerals) is unreadable and small-text bugs slip past QC.
- If LibreOffice fails (missing install at `C:\Program Files\LibreOffice\program\soffice.exe`): tell the user how to install or fall back to `--engine ppt`. Never substitute python-pptx text inspection or HTML preview — those ARE approximations and the rule against them stands.
- Do not continue to Step 4 until the export succeeds and all PNG files exist.

---

## Step 4 — Read every slide PNG

Use the Read tool to load each PNG file. Read them all before writing your report — do not report slide by slide as you go; review everything first so you can catch cross-slide consistency issues.

Also read `mockups.html` if it exists — you need to know what was intended for each slide to judge whether content is missing.

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
| **Intentional presenter prompt** | Advisory (NOT Critical) | The exact strings `[add footnote here or delete]` and `[add source here or delete]` are slide-builder's deliberate cross-skill convention emitted by `helpers.py add_footer()` when the caller doesn't supply text. Flag as Advisory with the note "intentional presenter prompt — fill or delete in PowerPoint before showing the deck." Do NOT escalate to Critical even though it looks like placeholder residue. Other bracketed text (`[Kickoff activities — fill from ...]`, `[your_company]`, etc.) is NOT this convention and stays Critical. |
| **Overflow / clipping** | Critical if text/data clipped; Major if shape bleeds past boundary without losing content | Text or shapes bleeding past the slide boundary; clipped numerals or descenders; chart axis labels cut off |
| **Blank chart / broken visual** | Critical | A blank white rectangle where the mockup had a chart; missing image placeholder; broken icon |
| **Unreadable overlap** | Critical | Text obscured by another element so it cannot be read |
| **Background contrast** | Critical | White text on white background; same-color-on-same-color violations that hide content |
| **Action title content** | Major | Title missing on a non-cover slide; title is a topic label not an action title (refer to storyline brief if available) |
| **Font size drift across same archetype** | Major | Slide N title is materially different size from slide M title where both are the same archetype |
| **Missing footer / page number** | Major | No footer or page number on a non-cover slide (the visual pass catches this because rendered output resolves master inheritance) |
| **Chart axis missing unit** | Major | Y-axis labeled "Value" / "Amount" with no unit — is it $M, count, percent? |
| **Mixed icon styles within deck** | Major | Flat icons on some slides, outline on others, emoji elsewhere |
| **Hedged or weasel language** | Major | "Robust," "scalable," "best-in-class," "world-class," "seamless" without substantiation; "could potentially consider" type hedging |
| **Bullets not parallel** | Major | One slide's bullets mix sentence structures (some verb phrases, some noun phrases, some full sentences) |
| **Chart Y-axis truncation** | Major | Y-axis starts above zero in a way that exaggerates differences without disclosure |
| **Chart aspect ratio dishonesty** | Major | Squashed or stretched axes that distort the visual message |
| **Source line missing where mockup expected one** | Major | Mockup had a `data-role="source"` element; PPTX shows no source |
| **Curly vs straight quotation marks** | Advisory | Straight quotes used instead of curly — small but flagged |
| **Stock photo with no informational value** | Advisory | Generic businesspeople photo that adds nothing |
| **Whitespace / hierarchy / composition** | Advisory | Subjective: page feels cluttered, hierarchy unclear, whitespace uneven |
| **Bold used everywhere** | Advisory | Bold should be sparing emphasis; if half the slide is bold, it has no emphasis |

### 5c — Cross-slide consistency (run once for the deck)

After all per-slide checks, scan for consistency issues that only appear when comparing slides:

| Check | Severity | What to flag |
|---|---|---|
| **Typography drift across deck** | Major | Title sizes vary across slides of the same archetype; body text sizes drift |
| **Footer drift** | Major | Same confidentiality / client name should appear on all non-cover slides; if it changes, flag |
| **Color palette drift** | Major | A slide uses an off-brand color without semantic reason |
| **Layout drift for same archetype** | Major | Two Analytical slides have noticeably different layouts; two Risk slides structured differently |

Cross-slide findings get tagged to the slide(s) where they appear in the final table — not as a separate "cross-deck" section.

---

## Step 6 — Write the report

Merge the hygiene-pass violations (from Step 2) with the visual-pass violations (from Step 5) into one unified table. Output as markdown — the chat renders the table.

Use this exact shape:

```
[deck-filename].pptx · [N] slides QC'd · [X] Critical, [Y] Major, [Z] Advisory

| Page | Severity | Issue |
|------|----------|-------|
| Slide [N] | **Critical** / **Major** / Advisory | [one-line description] |
| [...] | [...] | [...] |
```

Sort the rows: page number ascending; if a single page has multiple issues, Critical → Major → Advisory within the page.

Then follow the table with a conditional section based on what was found:

**If any Critical issues exist:**

```
⛔ Critical issues block this deck from shipping. They cannot be overridden — they have to be fixed.

[For each Critical, name the specific fix you can apply, in plain language. Example:]
- Slide 3: I can remove the lorem ipsum body block.
- Slide 7: The chart is blank — I need to re-run the build for that slide.

Want me to fix all of these in one pass?
```

**If no Criticals but at least one Major exists:**

```
[Slide N] has a Major issue. Do you want to fix it or move on?

[Each Major addressed in turn — same conversational prompt, with one or two concrete fix suggestions. Example:]

Slide 4 — title is 28pt but Slide 1 (same archetype) is 32pt.
Suggestions: resize Slide 4 to 32pt, or resize Slide 1 to match Slide 4. Or tell me why you want to ship it as-is and I'll record your reason.
```

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

If the user signs off on fixes (or after handling all Majors via the conversational prompt), **batch every fix into a single rebuild pass**. Never fix one issue at a time and re-render — that's the failure mode that multiplies build time 5–6× on a 10-slide deck.

Order of operations:

1. Compile the list of all approved fixes across all slides.
2. Apply them via targeted python-pptx patches (preferred), or by re-running specific slides through the slide-builder pipeline (re-dispatch the worker for that slide, then `finalize_deck.py` + `compile_picks.py`) if the fix requires regeneration.
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
- **Never skip a slide.** If there are 10 slides, every slide gets walked in Step 5a. A slide that is "all clear" still produces a quote-back — the absence of violations is fine, but the absence of the inspection record is not.
- **Cover slides are not exempt from content checks.** They are exempt from footer / page-number checks only.
- **Report what you see, not what you expect.** If the mockup says there should be a chart and you see a white box, that is a Critical regardless of what the build log said.
- **Batch all fixes — never fix one issue at a time.** Read every slide, identify every issue, fix all issues in a single pass at Step 7, rebuild once, then re-QC once. One fix → one rebuild → one QC cycle per issue is the failure mode that multiplies build time by 5–6× on a 10-slide deck. There is exactly one exception: if fixing issue A would conflict with fixing issue B (e.g., different background colors on the same slide), flag the conflict to the user and ask which takes precedence before fixing anything.
