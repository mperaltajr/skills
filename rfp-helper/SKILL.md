---
name: rfp-helper
description: "Coaching skill for RFP and proposal responses. Fundamentally different from storyline-helper: governing thought becomes a win theme, the goal is to score points against evaluation criteria rather than persuade with an argument, and the structure is often prescribed by the RFP itself. Produces a proposal brief that slide-builder can build from."
---

# RFP Helper

Coaching layer for RFP and competitive proposal responses. The rules here are different from an insight-driven consulting deck — understand those differences before coaching anything.

## Why this is a separate skill

| Consulting deck (storyline-helper) | RFP / proposal (this skill) |
|------------------------------------|----------------------------|
| You choose the narrative arc | Structure is often prescribed by the RFP (required sections, page limits) |
| Governing thought = an insight or recommendation | Governing thought becomes a **win theme** — a 1–2 word differentiator that threads through every section |
| Goal: change what the audience believes | Goal: score points against the evaluator's criteria |
| Structure follows the argument | Structure follows the RFP requirements |
| "Why us" is implied by the argument | "Why us vs. competitors" is explicit, not implied |
| Body content = evidence for a claim | Body content = ghost-written to scoring criteria — make it easy for the evaluator to give you full marks |

---

## Hard constraints

1. **Win theme first.** Before writing a single section, establish the win theme — the 1–2 word differentiator that makes this firm the obvious choice over the next-best alternative. Every section must thread the win theme through its content.

2. **Read the RFP before coaching.** The RFP's required sections, page limits, evaluation criteria, and weighting are the structural constraints. Do not coach around them — work within them.

3. **Ghost-write to the scoring criteria.** Every section of content should be written so the evaluator can check a box. If the criteria say "demonstrate experience in supply chain transformation," the response must explicitly state experience, name engagements, and show outcomes — not imply capability.

4. **"Why us" must be explicit.** In a consulting insight deck, differentiation is implied by the quality of the argument. In an RFP, it must be stated directly and specifically. Generic claims ("we have deep expertise") fail. Specific claims with proof ("we have deployed this method at 14 companies in this sector, with an average time-to-value of 6 months") pass.

---

## Conversation flow

### Step 0 — Session setup and RFP intake

Collect three things before coaching begins:

> *"Three things before we start:*
> *1. Session folder path (e.g., `ClientName/sessions/YYYY-MM-DD RFP Topic/`)*
> *2. Path to the client's PowerPoint template*
> *3. The RFP document — paste it in, or give me a file path. I need to read the required sections, page/slide limits, evaluation criteria, and weightings before we structure anything."*

Read the RFP in full. Extract and confirm:
- Required sections and their order
- Page or slide limits per section
- Evaluation criteria and their weightings (if stated)
- Submission deadline
- Any explicit formatting requirements

State what you've extracted:
```
Required sections: [list]
Page limits: [per section or overall]
Evaluation criteria: [list with weights if stated]
Deadline: [date]
```

### Step 1 — Win theme

The win theme is the single most important decision in a proposal. It is not a tagline — it is the strategic claim that makes this firm the obvious choice over the next-best alternative for *this specific client and this specific opportunity*.

> *"What is the one thing that makes you the obvious choice for this client — not obvious in general, but obvious for this specific opportunity? If the evaluator had to summarize why they chose you in two words, what would those words be?"*

A strong win theme:
- Is specific to this client and this RFP — not a generic firm positioning
- Names something the next-best competitor cannot credibly claim
- Can be demonstrated, not just asserted
- Threads naturally through every required section

Examples:
- "Lowest risk" — only works if you can point to track record, methods, or team experience that credibly de-risks the engagement
- "Fastest to value" — only works if you have a proprietary accelerator, methodology, or team composition that delivers faster than alternatives
- "Deepest [sector] knowledge" — only works if the team's credentials are demonstrably sector-specific

If the user can't articulate a win theme, run this diagnostic:
> *"Three questions: (1) What does this client fear most about this engagement? (2) What do you have — team, method, tool, past work — that directly addresses that fear? (3) Can a competitor credibly claim the same thing?"*

If no genuine differentiator exists, name that directly. A proposal with no real win theme loses to one that does, regardless of writing quality.

### Step 2 — Evaluation criteria mapping

Map each required section to the evaluation criterion it serves. This determines where to concentrate the strongest proof points.

For each section:
- What criterion does this section score against?
- What weight does that criterion carry?
- What does "full marks" look like for this criterion?

> *"For [section name], the evaluation criteria say [criterion]. Full marks go to responses that [describe what evaluators are looking for]. What's your strongest proof point for this criterion?"*

Flag sections where proof is weak — these need to be shored up before writing, not during.

### Step 3 — Section-by-section structure

For each required section, establish:

**3a — Opening claim.** What is the section's governing statement — the one thing the evaluator should take away even if they skim? This is not the win theme (which threads through all sections), but the section-specific proof of the win theme.

**3b — Proof points.** Three to five concrete, specific items that substantiate the opening claim. Each should be directly checkable against the evaluation criteria. Generic claims without proof get scored low.

**3c — Win theme echo.** How does this section reinforce the win theme? If it doesn't, the section is not pulling its weight in the overall proposal narrative.

**3d — "Why us" statement.** An explicit statement of why this firm — not a generic firm — is the right choice for this section's content. Should name a specific credential, engagement, tool, or team member where possible.

### Step 4 — Gate

**Do not produce the proposal brief until all four checks below pass. If any check fails, return to the affected section and ask the specific question listed before continuing.**

Before producing the proposal brief, run these checks:

1. **Win theme test.** Can you read the win theme in every section's opening claim? If not, the proposal is not threaded.

2. **Criteria coverage test.** Does every evaluation criterion have at least one section whose content directly addresses it? Any uncovered criterion is a scoring gap.

3. **Specificity test.** Does every proof point name a specific engagement, number, person, tool, or outcome — or is it still generic? Generic = low score.

4. **"Why us" test.** Is the differentiation explicit and specific in every section? If a competitor could make the same claim with the same words, it's not differentiated.

### Step 5 — Produce the proposal brief

When the gate passes, produce the proposal brief and save it to the session folder. **The brief MUST be slide-builder-compatible** — see "Proposal brief format" below. It carries YAML front-matter with `mode: rfp` (which bypasses slide-builder's narrative gate, since RFP quality is enforced by the Step-4 checks above, not by a narrative argument), `### Slide N — <section>` headers, and the standard slide-builder field labels. Without this exact shape, `build_deck.py` exits before building.

```
Proposal brief saved:
  C:\Users\...\ClientName\sessions\2026-05-14 RFP Topic\proposal-brief-rfp.md
```

### Step 6 — Hand off to Slide Builder

**Before handing off, confirm the client template is registered.** Slide Builder requires a registered template (a `<stem>/` sidecar subfolder next to the `.pptx` containing `brand.yml` + `theme.json`). If the template hasn't been registered this engagement, run the chat-driven flow documented in `slide-builder/SKILL.md` § "Register a new client template" — `register_template.py propose` then `commit`. The registration produces the canonical theme + brand sidecars.

**When the user confirms the brief, invoke the `slide-builder` skill using the Skill tool:**

> *Handing off to Slide Builder now.*
>
> *Brief: `[absolute path to proposal-brief file]`*
> *Template: `[absolute path to .pptx template]` (registered — `<stem>/brand.yml` present)*
>
> *This is a proposal/RFP build — note the following:*
> *— One option per section, not three design variants. Layout should be clean and professional.*
> *— Win theme: `[state it]` — thread this visually on the cover, section dividers, and where appropriate in body slides.*
> *— Structure is prescribed by the RFP (section order fixed). Do not reorder.*
>
> *Slide Builder: read `slide-builder/reference/layouts.md` and `slide-builder/reference/anti-patterns.md` before dispatching per-slide workers. Brand colors come from the registered `brand.yml`; the 14-pattern catalog is in `layouts.md`.*

---

## Proposal brief format

The proposal brief is consumed by `slide-builder/scripts/build_deck.py`, so it must
match slide-builder's brief contract exactly: YAML front-matter, `### Slide N —`
headers, and the standard field labels. RFP-specific concepts map onto those labels;
RFP-only metadata (criterion, weight) is kept as bold fields the parser ignores, so it
stays visible for the human and QC without polluting the slide.

**Field mapping (RFP concept → slide-builder field):**

| RFP concept | slide-builder field |
|---|---|
| Section name | `### Slide N — <section name>` header |
| Opening claim | `**Governing thought (the claim):**` |
| Win theme echo | `**So-what (the takeaway):**` |
| Proof points | `**Evidence / content:**` bullets, each as `**HEADING** — body.` |
| "Why us" / Full marks | folded into Evidence as labeled bullets (so they render on the slide) |
| Evaluation criterion / Weight | kept as bold fields (parser ignores; visible for scoring) |
| Page / slide limit | `## Deck-level design notes` |

Why `**HEADING** — body` on the evidence bullets: slide-builder's translator parses that
shape into structured slide content; loose prose bullets render as placeholder text.

```markdown
---
client_template: [absolute path to the registered .pptx template]
deck_type: Capability Pitch
default_layout: [layout name from the template's theme.json::default_content_layout]
session_folder: [absolute path to the session folder]
mode: rfp
win_theme: [1–2 word differentiator]
---

# Proposal brief: [RFP name / client]

## Deck-level design notes
- Win theme: [1–2 words + one sentence]. Thread it on the cover, section dividers, and where appropriate in body slides.
- Page / slide limits: [per-section limits from the RFP — hard constraints].
- One clean layout per section (no three design variants — evaluators score content, not design).
- Structure is prescribed by the RFP; section order is fixed.

## Evaluation criteria
[List with weights if stated — deck-level reference for the human and QC.]

---

### Slide 1 — [Section name as stated in the RFP]

**Evaluation criterion:** [criterion this section scores against]
**Weight:** [% or relative weight]

**Governing thought (the claim):** [the section's opening claim — the single governing statement]

**So-what (the takeaway):** [how this section reinforces the win theme — the belief it drives]

**Evidence / content:**
- **[PROOF POINT LABEL]** — [specific engagement / number / tool / person].
- **[PROOF POINT LABEL]** — [specific engagement / number / tool / person].
- **WHY US** — [explicit, specific differentiator a competitor could not claim verbatim].
- **FULL MARKS** — [what the evaluator wants to see, stated as the slide proves it].

**What this slide is NOT:** [scope exclusion — what would dilute the section's score]

---

[Repeat — `### Slide 2 — …`, `### Slide 3 — …` — one slide per required section, in RFP order]

## Flags
[Weak proof points, uncovered criteria, or sections where differentiation is thin]
```

---

## Notes passed to Slide Builder at handoff

The following points are included in the Step 6 handoff message — they are instructions for Slide Builder, not for the user.

- **No three design variants.** Proposals get one clean layout per section — the client doesn't want to see design options, they want to score the content.
- **Page limits are hard constraints.** If the RFP says 2 pages per section, slide-builder must design to fit. Flag if content cannot fit.
- **Win theme = visual anchor.** The win theme should appear visually on the cover, on section dividers, and as a footer or watermark if permitted by the RFP formatting rules.
- **"Why us" callouts.** Each section should have one visual callout (stat box, quote, or highlight) that makes the differentiator impossible to miss — evaluators often skim, and the differentiator should be scannable.
