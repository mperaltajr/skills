---
name: deck-storyline-review
description: Use this skill whenever the user asks to review, critique, evaluate, or pressure-test the storyline, argument, narrative, or substance of a slide deck — pitch decks, board decks, strategy readouts, recommendation decks, RFP responses, all-hands, or any deck where an argument is being made. Trigger phrases include "review this deck's storyline", "is the argument clear", "pressure-test this narrative", "does this hold up to a partner review", "would this pass a CIO/CEO read", or when a deck is uploaded with a request for substantive feedback rather than visual polish. This skill evaluates whether the right things are being said in the right order for the audience — it is judgment-heavy and context-aware. It does NOT evaluate rendering, formatting, typography, overlap, or grammar — those belong to a separate page-quality skill.
---

# Deck Storyline Review Skill

## Purpose

Evaluate whether a slide deck makes the right argument, in the right order, for the right audience — at the standard a senior MBB partner or a sharp client executive would apply.

This skill answers: *"Is this the right thing to say?"*

It does not answer: *"Is whatever is on the page rendered correctly?"* — that question belongs to a separate, context-independent page-quality evaluation.

## Scope — what this skill owns

| The skill evaluates | The skill does NOT evaluate |
|---|---|
| Whether titles are *action titles* (state the takeaway) | Whether title formatting is consistent across pages |
| Whether charts have a clear *takeaway* | Whether callout boxes are visually placed correctly |
| Whether each page makes *one disciplined point* | Whether the layout is clean enough to read it |
| Whether bullets are findings vs. observations | Whether bullets are parallel in structure or punctuation |
| Whether the right chart is used to prove the point | Whether axes are labeled, units present, legend readable |
| Whether language is decision-forcing and clear | Grammar, typos, hedging words, acronym expansion |
| Whether the argument holds across pages | Whether layouts, footers, page numbers match across pages |

The rule: this skill owns *"is this the right thing?"* questions. Rendering questions are out of scope.

## Inputs to gather before reviewing

1. **The deck itself.**
2. **The audience.** Who reads or sits in the room? (CEO, CFO, CIO, board, client procurement panel, investment committee, etc.) Different audiences demand different storylines. Without this, the agent guesses — and gets it wrong.
3. **The ask.** What decision is the deck driving toward? Approval, investment, alignment, prioritization, status acknowledgment? If the deck has no ask, that itself is a finding.
4. **The deck type.** Pitch / board update / strategy readout / RFP response / recommendation / kickoff / all-hands. Different types have different default storylines.
5. **The context.** Is this a first read or a follow-up? Has the audience seen the work in flight? Is there a competitor in the deal?

If audience and ask are unknown, the agent asks before scoring rather than guessing.

## The framework — three layers

### Layer 1: Macro storyline tests (gate)

These eight tests apply to the deck as a whole. Failing the critical ones (marked *Gate*) caps the verdict at "major rework needed" regardless of how strong individual pages are.

| Test | What it checks | Gate? |
|---|---|---|
| **30-second answer** | Can the deck's answer be stated in 30 seconds? If it requires three minutes of setup, the storyline is bottom-up. | Gate |
| **Title-flow** | Strip the body. Read only page titles in sequence. Do they tell the full story? | Gate |
| **SCQA opening** | Does the deck open with Situation → Complication → Question → Answer, or with methodology? | Gate |
| **MECE pillars** | Are supporting arguments mutually exclusive and collectively exhaustive? | No |
| **"So what" on every page** | Does every page answer "so what?" crisply, or are some decoration? | No |
| **Decision required** | What decision is the audience asked to make? Is it named explicitly? | Gate |
| **Monday-morning test** | If accepted, who does what on Monday? "Form a working group" is not specific enough. | No |
| **Dissent test** | Does the deck pre-empt the two or three obvious challenges, or pretend they don't exist? | No |

Any Gate failure → verdict capped at "major rework needed."

### Layer 2: Page-archetype argument quality

Each page gets classified into an archetype, then scored against the questions for that archetype.

**Cover / Title**
- Does the title state what this is *about*, not just the project codename?
- Does the visual gravity match the audience?

**Executive summary / Page-one answer**
- If I only read this page, do I have the answer?
- Is the recommendation explicit and singular, not hedged?
- Are the three supporting points each independently sufficient to motivate action?

**Context / Situation**
- Why are you telling me this — have I lived it?
- What's the *complication* — what changed or broke?
- Is the data recent and specifically sourced?

**Approach / Methodology**
- Why these workstreams and not others?
- What's explicitly out of scope?
- Did you engage the people whose buy-in we'll need?

**Analytical page (chart-driven)**
- Does the title state the *insight*, not the *topic*?
- Is this the simplest chart that proves the point?
- Is the data window honest — does it disconfirm as well as confirm?
- Does the page have a clear takeaway the eye should land on?

**Framework / Conceptual (2x2s, models, maturity curves)**
- Why these two axes — are they actually independent?
- Where is the client on this framework, and where do they need to be?
- Does the model produce a *decision*, or just a vocabulary?
- Have I seen this exact framework on a deck before — is it adapted?

**Synthesis / Findings consolidation**
- Are these genuinely the top three findings?
- Are these findings or observations? (Findings have numbers and consequence; observations are vibes.)
- Is each finding traceable to the analysis page that proved it?

**Recommendation**
- Is it specific enough that someone could act on it Monday?
- Who owns it, by name or role?
- What's the second-order consequence?
- What alternative was rejected, and why?
- What's the no-regret part to do regardless?

**Roadmap / Implementation**
- Is the critical path identified?
- Where do we assume people, budget, approvals come from?
- What's in the first 30 days — is there an early proof point?
- Where are the off-ramps if something goes wrong?

**Risk**
- Are these the risks that actually keep the audience up at night, or the safe ones?
- Is each risk sized, owned, triggered, and mitigated?
- What's the risk you're *not* listing because it's awkward?

**Financial / Business case**
- What's the assumption I should disagree with first?
- Where's the sensitivity?
- What's the break-even and when?
- Are the cost categories MECE?
- Has the client's finance function seen these numbers?

**Decision / Ask page**
- What exactly is the audience being asked to decide?
- Is each decision binary or selectable?
- What's needed, by when?
- What happens if the answer is no?

**Appendix**
- Is every page defensible if opened at random in front of the client?
- Is it indexed so the right backup is findable?
- Does the main deck point to specific appendix pages?

### Layer 3: Cross-cutting argument rules

Universal violations. Any single one is a red flag.

- **No page exists without a point.** If you can delete the page and the argument survives, the page was decoration.
- **No chart exists without a takeaway.** The substantive insight must be named on the page.
- **No claim exists without a source.** Every external number, quote, or statistic must be sourced (substance check — the rendering of the source citation is page-quality's problem).
- **No promises the team can't keep.** A roadmap slide is a commitment, not an aspiration.
- **No stolen arguments.** A framework or analysis ported from another client without adaptation.

## Scoring rubric

**Macro storyline tests:** each marked Pass / Fail. Gate-tagged tests failing → verdict cap.

**Per-page-archetype scoring (1–5):**

| Score | Anchor |
|-------|--------|
| **5** | Best-in-class. A partner would reuse this page structure as a template. |
| **4** | Strong. Minor tightening possible. |
| **3** | Adequate. Makes its point but unremarkable. |
| **2** | Weak. The page exists but does not earn its place. |
| **1** | Critical. The page actively hurts the argument or is decoration. |

**Overall storyline score:** weighted average across pages, normalized to 0–100. Weight pages by archetype importance — Executive Summary, Recommendation, and Decision pages count double; Appendix counts half.

## Verdict thresholds

- Any Gate test failed, **OR** weighted < 60 → **Major rework needed**
- All gates pass + 60–74 → **Argument needs tightening before presenting**
- All gates pass + 75–84 → **Solid storyline; refine named pages**
- All gates pass + 85+ → **Strong storyline; mine for reusable patterns**

## Output format — one-screen decision-maker view

```
DECK: [name]
AUDIENCE: [named reviewers]
ASK: [decision the deck drives toward]

MACRO STORYLINE GATES:
  30-second answer:    Pass / Fail
  Title-flow:          Pass / Fail
  SCQA opening:        Pass / Fail
  Decision required:   Pass / Fail
  [other tests]:       Pass / Fail with note

STORYLINE SCORE: NN / 100
VERDICT: [one of: Major rework | Tighten before presenting | Solid, refine named pages | Strong storyline]

RED FLAGS (up to 3):
  - [specific, named issue tied to a page or pattern]
  - ...

GREEN FLAGS (up to 3):
  - [specific strength worth reusing]
  - ...

PAGE-LEVEL SCORES (only flag scores of 1 or 2):
  p3 (Context):         2 — recites brief back to client who wrote it
  p7 (Analytical):      1 — topic title, no takeaway, decorative chart
  p14 (Recommendation): 2 — "strengthen operating model" is not actionable
  [...]
```

## Worked example

```
DECK: Customer Portal Modernization — Final Readout
AUDIENCE: CIO, CISO, CFO
ASK: Approve Phase 2 funding ($4.2M) and named program owner

MACRO STORYLINE GATES:
  30-second answer:    Pass — page 2 states the answer
  Title-flow:          Fail — titles read as topic labels (p4–p11)
  SCQA opening:        Pass
  Decision required:   Pass — three named decisions on closing page

STORYLINE SCORE: 64 / 100
VERDICT: Major rework needed (title-flow gate failed)

RED FLAGS:
  - Title-flow failure: pages 4–11 use topic titles ("Architecture",
    "Security Posture") instead of action titles; stripping the body
    leaves a reader unable to follow the argument
  - Recommendation page (p14) hedges — "consider exploring options" —
    when the audience needs a singular recommendation
  - Risk page (p16) lists only three risks; the CFO will probe at
    least two more (cost-overrun, vendor lock-in) that are absent

GREEN FLAGS:
  - SCQA opening is clean — situation, complication, and answer
    sequenced on pages 1–2
  - Decision page closes with three binary asks tied to deadlines
  - Financial page on p13 shows sensitivity range, not a single point

PAGE-LEVEL SCORES (scores of 1 or 2 only):
  p4  (Analytical):     2 — topic title, no insight
  p7  (Framework):      2 — generic 2x2, no client placement
  p11 (Synthesis):      2 — six findings, no prioritization
  p14 (Recommendation): 2 — hedged language, no Monday-action
  p16 (Risk):           2 — risk surface too narrow for CFO review
```

Note how the title-flow gate failure caps the verdict at "major rework" even though several pages scored 3+ and three green flags are present. The gate is doing intentional work.

## Checklist for the agent before declaring a grade

1. Audience and ask named.
2. Deck type identified.
3. Macro storyline gates run, each marked Pass/Fail with a one-line note.
4. Every page classified into an archetype and scored 1–5.
5. Cross-cutting argument rules applied across the deck.
6. Red flags and green flags written specifically, capped at 3 each.
7. Verdict matches the threshold table.
8. Output fits the one-screen format.
