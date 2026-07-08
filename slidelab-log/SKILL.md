---
name: slidelab-log
description: "Generates a structured session failure or improvement report by reviewing what happened in the current session. Claude writes the report — not the user. Invoke when something went wrong mid-session, when the output wasn't right, or at the end of any session worth logging. Saves report to _session/feedback-YYYY-MM-DD.md and gives the user a GitHub link to submit it."
---

# Feedback — Session Report Generator

Claude writes the report. The user submits it. No technical knowledge required from the user.

---

## When to invoke this skill

- Something went wrong and the user says "log this," "report this," "something broke," or "/feedback"
- The output was wrong and the user accepted a workaround
- The skill skipped a step, ignored an instruction, or produced unexpected output
- The session went well and the user wants to log what worked for future reference

---

## What to do

### Step 1 — Ask one question

Ask the user for their description in plain language. One open question, no forms:

> *"What happened — describe it however feels natural. I'll turn it into a structured report."*

Wait for their response. Even a vague answer ("the colors were wrong," "it skipped the template question") is enough — you have the session context to fill in the technical details.

### Step 2 — Review the session and generate the report

Using the full session context (conversation history, commands run, outputs produced, any errors), generate a structured technical report. The user's description is one field — the rest comes from what you observed.

Fill in every field you can from the session. If something is genuinely unknown, say so — do not guess.

**Report format:**

```markdown
# Session Feedback Report
Date: YYYY-MM-DD
Session folder: [absolute path, or "not established"]

## What was being built
[Slide type, deck topic, client if known]

## Skill(s) involved
[slide-lab | storyline-helper | slide-builder | slide-qc | rfp-helper — list all that ran]

## Pipeline used
[HTML mockup | direct python-pptx | N/A]

## Steps skipped or mis-sequenced
[List any SKILL.md steps that were skipped, run out of order, or applied to the wrong slides.
If all steps were followed correctly, say "None identified."]

## Commands run
[List every py -3 command that ran and whether it succeeded, failed, or was skipped]
- py -3 ... --print-theme → ✓ succeeded / ✗ failed / — skipped
- py -3 ... --catalog-layouts → ✓ / ✗ / —
- py -3 ... (build) → ✓ / ✗ / —

## Deviations from skill instructions
[Where this session diverged from what SKILL.md instructs — be specific: which constraint,
which step, which section. If no deviations, say "None identified."]

## Symptom
[What the wrong output looked like, or what the user observed]

## Root cause
[Your best assessment of why it happened — not the user's assessment, yours.
Reference specific skill rules, constraint numbers, or document structure if relevant.]

## Workaround applied
[What was done to recover. "None — session abandoned" if applicable.]

## What worked well (if logging a successful session)
[Any patterns, steps, or decisions that produced notably good output]

## User description
"[Exact quote from the user's Step 1 answer]"

## Suggested skill improvement (optional)
[If this failure points to a gap in the SKILL.md — missing instruction, ambiguous step,
wrong section order — describe the fix. Reference the specific section.]
```

### Step 3 — Save and give the user a submission link

Save the report to the session folder:
```
_session/feedback-YYYY-MM-DD.md
```

Output the full absolute Windows path.

Then output this block:

```
FEEDBACK REPORT SAVED
=====================
File: C:\path\to\_session\feedback-YYYY-MM-DD.md

To submit:
1. Open this link → https://github.com/mperaltajr/skills/issues/new?template=session-failure.md
2. Paste the contents of the file above into the issue body
3. Edit the title to summarize the problem in one line
4. Click Submit

Or for a general improvement suggestion:
→ https://github.com/mperaltajr/skills/issues/new?template=improvement-suggestion.md
=====================
```

---

## Report quality rules

- **You write the technical content.** The user's description is one field, not the whole report. The rest comes from your session observation.
- **Be specific.** "Model skipped the the pre-build hygiene check output" is useful. "Something went wrong in the build setup" is not.
- **Name the root cause from the skill's perspective.** If the model deviated from a constraint, say which constraint. If a section was in the wrong order, say which section.
- **Do not soften failures.** If you skipped a step you were supposed to run, say so directly. The point of the report is to improve the skill — not to look good.
- **If the session was clean, say so.** A "no issues" report is still useful — it confirms what's working.

---

## Example report (failure case)

```markdown
# Session Feedback Report
Date: 2026-05-07
Session folder: <path-to-your-session-folder>\sessions\2026-05-07 ProjectName\

## What was being built
3-slide steering committee update. HTML mockup pipeline.

## Skill(s) involved
storyline-helper, slide-builder

## Pipeline used
HTML mockup

## Steps skipped or mis-sequenced
- Pre-build hygiene check output was not produced before HTML was written
- Deck-level design notes were read but not stated before Phase A began

## Commands run
- py -3 ... --print-theme → ✓ succeeded
- py -3 ... --catalog-layouts → — skipped (template has <20 layouts)
- py -3 ... (build) → ✓ succeeded

## Deviations from skill instructions
- Pre-build hygiene check was absent. HTML mockup was written without
  producing the required confirmation block first.
- Setup step 1: Deck-level design notes section was not explicitly stated before Phase A.

## Symptom
Slide 2 body text appeared larger than slides 1 and 3. User noticed inconsistency after build.

## Root cause
The pre-build hygiene check was skipped, so the canonical type scale was not
confirmed before HTML authoring. Slide 2 used 18px body text (not in the allowed scale)
which converted to 13.5pt — visibly larger than the 12pt on the other slides.

## Workaround applied
User accepted output. Slide 2 body text inconsistency was noted for manual correction.

## User description
"the text on slide 2 looked bigger than the others"

## Suggested skill improvement
The canonical type scale should also appear in the pre-build hygiene check output as
a required confirmation line, not just in the hard constraints list. This creates a
second enforcement point at the moment of HTML authoring.
```

---

## Example report (success case)

```markdown
# Session Feedback Report
Date: 2026-05-07
Session folder: <path-to-your-session-folder>\sessions\2026-05-07 ProjectName\

## What was being built
5-slide kickoff deck. HTML mockup pipeline.

## Skill(s) involved
storyline-helper, slide-builder

## Pipeline used
HTML mockup

## Steps skipped or mis-sequenced
None identified.

## Commands run
- py -3 ... --print-theme → ✓ (output cached to _session/theme.json)
- py -3 ... --catalog-layouts → ✓ (output cached to _session/layouts.json)
- py -3 ... (build) → ✓

## Deviations from skill instructions
None identified.

## Symptom
N/A — session completed successfully.

## Root cause
N/A

## Workaround applied
None required.

## What worked well
Pipeline decision ran before narrative gate — model correctly identified slide 3 as
direct python-pptx and skipped Phase A for that slide only. Deck-level design notes
("one orange accent element per slide") were applied consistently across all 5 options.

## User description
"everything looked good, wanted to log this one"
```
