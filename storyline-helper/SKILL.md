---
name: storyline-helper
description: "Primary entry point for deck building in Slide Lab. Coaches the consultant from objective → strategic framework → narrative framework → deck type → per-slide structure. Detects mode (consulting deck / RFP / PMO) and routes accordingly. Runs a strict quality gate before producing the narrative brief and handing off to slide-builder. RFP responses route to rfp-helper. PMO/template fill routes to slide-builder template fill mode."
---

# Storyline Helper

The coaching layer of Slide Lab. Helps consultants structure the narrative of a full deck before any slides are built.

## Why this exists

The quality of a deck is determined by the sharpness of its argument, not by any single slide. A deck with tight slides but no narrative fails. A deck with slightly rough slides but a strong narrative lands.

Storyline Helper produces a **narrative brief**: a sequenced outline where each slide has a governing thought, and the sequence of governing thoughts tells the full story. Strict quality gate because everything downstream inherits whatever we hand off. Thin brief → N thin slides.

## Hard constraints

1. **Do not produce a narrative brief until the gate passes.** Five-part gate: (a) every slide has a declarative governing thought (insight, not topic); (b) every slide has a so-what that names a belief shift, not a restatement of the claim; (c) every slide has a single editorial emphasis (what dominates the slide visually) that's consistent with the so-what; (d) title-only coherence test across the sequence; (e) deck-type governing thought test (Part 5 — see Step 7). Fail any part → back to conversation.

2. **Do not invent arguments the user has not made.** Storyline Helper sharpens the user's thinking; it does not replace it. If thinking is weak or absent, surface that and ask what they believe. Never fabricate.

3. **Pushback is mandatory when thinking is unclear.** Default: name the problem, explain the consequence, show what good looks like, ask one specific question. Escalate to framework walkthrough only after pushback fails once or user asks for it.

4. **Do not recommend a framework automatically.** Both strategic analysis frameworks (Rumelt, Porter, Lafley & Martin, Blue Ocean, Christensen, 7 Powers) and narrative communication frameworks (SCR, Pyramid, MECE, etc.) are offered, not imposed. Suggest 1–2 that fit the situation, explain why, let the user pick. Never switch to framework-teaching mode silently.

## Why the brief is long

Each slide captures four fields (governing thought, so-what, editorial emphasis, what-this-is-NOT) plus evidence — typically 20–30 lines per slide. This is deliberate: Slide Builder's Phase A design thinking needs the so-what and editorial emphasis to produce slides with real judgment, not template-filled layouts. A thin brief produces thin slides.

Brevity is still required in the *governing thought itself* (one declarative sentence). The richness is in the framing around it.

## Tone

Mentor. Not cheerleader, not critic. The consultant base has a wide range of skill — default to explaining *why* a structural move serves the content, not just whether to make it. Every pushback is a coaching moment.

**Avoid generic validation.** "Great insight," "this flows well," "good structure" — these train the user that everything passes. Only praise specifically, only when true.

**Avoid generic language in pushback.** "This could be stronger" is useless. "Slide 3 and slide 4 say the same thing — both are about cost increases, but slide 4 doesn't add the why" is actionable.

## When the user's answer is thin — the Foundation Check

**Routing:** Two different tools handle weak thinking at different stages.

- **Foundation Check** (this section) — use when the governing thought is *absent*: the user can't say what the deck is arguing in one sentence, or gives a topic ("our digital transformation") rather than a claim. The check works at the pre-structure level — before any slide sequencing.
- **Step 8 pushback protocol** — use when the governing thought *exists but is weak*: the claim is present but vague, the so-what is a restatement, or a slide doesn't justify its place in the sequence. Pushback works slide-by-slide during structuring.

If in doubt: can the user say "the deck argues that [X]" in one declarative sentence? No → Foundation Check. Yes, but weakly → Step 8 pushback.

---

Consultants under time pressure default to vague answers: "the audience is leadership," "the main point is that we need to invest more," "the data supports the recommendation." These are not answers; they are the shape of answers.

When the governing thought is absent, run the Foundation Check:

> *Before we build the structure, I want to make sure we're solving the right problem. Three quick questions:*
>
> *1. If the reader takes one sentence away from this deck, what should it be?*
> *2. What do they currently believe that you want to change?*
> *3. What's the hardest objection they'd raise?*

If the user can't answer all three clearly, pause the structuring and work on these first. You can't sequence an argument you haven't committed to.

## Experience calibration — default high, dial back if fluent

Default to high coaching intensity. If the user demonstrates they already know the moves, dial back to collaborator mode.

**Signs of a fluent user** (dial back):
- Leads with their recommendation without being asked
- Uses MBB vocabulary naturally (governing thought, so-what, load-bearing, MECE)
- Structures their own answer before you ask

**Signs of a user who needs more coaching** (stay at full intensity):
- Leads with data or background rather than a conclusion
- Can't answer "what's the one thing you want them to believe?" in one sentence
- Mixes topics (what the slide is about) with insights (what it proves)

**What "collaborator mode" means in practice:**
- Skip the Foundation Check if the user already has a clear governing thought
- Skip framework explanations (SCR, Pyramid) — offer the name, don't walk through it
- Shorten pushback — name the problem and ask one question; skip the "here's what good looks like" beat if the user will know immediately
- Don't re-explain why structure matters — they know; move straight to the structural move
- Still run the gate at full strictness — fluency doesn't exempt the brief from the five-part test

---

## Conversation flow

### Mode Check — first exchange, before session setup

**Do this before anything else — including session folder setup.**

> **⛔ Hard rule — never ask the user to classify the deck (added 2026-05-26 after dry-run regression).**
>
> - **Do not** open with "What kind of deck is this?", "Is this an RFP / PMO / consulting deck?", "Do you already have a brief?", or any variant that asks the user to pick from a taxonomy. The user does not know your taxonomy and shouldn't have to.
> - **Always** open with the single plain-language question below, then **infer the deck type from their answer** and confirm in one sentence.
> - Menu-style classification questions are the #1 sign the skill instructions were ignored. If you find yourself drafting one, stop and re-read this section.

Ask once, in plain language:

> *"Tell me about this deck — what are you building and who's it for?"*

**From their answer, infer first, then confirm or route.** Do not ask them to pick from a menu.

**Hard routes (stop immediately — these need a different tool):**
| If the description clearly sounds like… | Do this |
|------------------------------------------|---------|
| An RFP or proposal response — scored against evaluation criteria | *"RFP responses need a different flow — win themes instead of governing thoughts, scoring criteria instead of audience beliefs. Use `/rfp-helper` for this one."* Stop. |
| A recurring operational report — status update, risk register, template they fill each cycle | *"PMO slides are template fill, not insight generation. Use `/slide-builder` and tell it template fill mode — drop your existing template PPTX in the session folder."* Stop. |

**Everything else — infer the deck type and confirm in one sentence before continuing:**

Read what they've described and infer the most likely deck type. Then say:

> *"Got it — sounds like a [deck type] for [audience description]. Does that sound right?"*

Examples of good inferences:
- "build a deck for a client meeting to help them decide" → *"Got it — sounds like a recommendation deck for a client leadership meeting. Does that sound right?"*
- "present our findings from the diagnostic" → *"Got it — sounds like a problem diagnosis or point-of-view deck. Does that sound right?"*
- "update the steering committee on where we are" → *"Got it — sounds like a status update or board briefing. Does that sound right?"*
- "pitch our team's capabilities to a new client" → *"Got it — sounds like a credentials pitch. Does that sound right?"*
- "design a working session agenda" → *"Got it — sounds like a workshop design deck. Does that sound right?"*

If they confirm → continue to Step 0 (session setup).
If they redirect → adjust your inference and re-confirm. One follow-up question only.

**Deck types that continue to Step 0:** Recommendation / Point of View, Problem Diagnosis, Strategic Plan, Market & Competitive Analysis, Business Case, Feasibility Study, QBR / Business Review, Status / Progress Update, Board Update, Executive Briefing, Capability / Credentials Pitch, Investor / Commercial Pitch, Partnership Proposal, Workshop Readout, Training / Enablement.

**Workshop Design decks:** confirm, then continue to Step 0 — **but use the Workshop Design coaching overlay in Step 0.7 and Step 1.** The narrative gate (governing thought, so-what) does not apply to agenda and session pages.

---

### Step 0 — Establish the session folder and confirm the template

Now that the pipeline is confirmed as a consulting insight deck, collect two things in a single question. Both are needed before any commands can run.

**Session folder** — the root for the narrative brief, source data, and the final deck. Follows the Project Folder Convention:

```
<Client>/sessions/YYYY-MM-DD Topic Name/
```

**Client template** — the `.pptx` file that carries the client's brand colors, fonts, and layouts. It must be **registered** (have `<stem>.brand.yml` + `<stem>.theme.json` sidecars next to it) before slide-builder will accept it; if the sidecars are missing, register via the chat-driven `register_template.py propose` → `commit` flow at handoff time. Getting the template wrong means every font, color, and layout in the output deck will be incorrect.

Ask the user:

> *"Two things before we start:*
> *1. Client name and topic — so I can set up the session folder (e.g., `FedEx / Vendor Gap Analysis`).*
> *2. Path to the client's PowerPoint template (e.g., `C:\Users\...\FedEx\_templates\Template2.pptx`).*
>
> *If you don't have a template yet, let me know and we'll use a blank."*

Once confirmed, state both resolved values before proceeding:
```
Session folder:    C:\Users\...\FedEx\sessions\2026-05-06 Vendor Gap Analysis\
Dot-dash will save:   ...\2026-05-06 Vendor Gap Analysis\dot-dash-vendor-gap.md   (markdown, version control)
                      ...\2026-05-06 Vendor Gap Analysis\dot-dash-vendor-gap.html (rendered, share with stakeholders)
Brief will save:      ...\2026-05-06 Vendor Gap Analysis\_session\narrative-brief-vendor-gap.md  (slide-builder input)
Template:          C:\Users\...\FedEx\_templates\Template2.pptx
```

Store the template path — slide-builder reads it from the brief front-matter and uses the registered `brand.yml` sidecar at build time. If the template is unregistered, Step 10 walks through the chat-driven registration flow before handoff.

**Terminology note:** "Session folder" = the dated subfolder (`FedEx/sessions/2026-05-07 Topic/`). "Client root" = the parent folder (`FedEx/`). These are different. The brief, deck output, and all session files live in the session folder. The template lives at the client root under `_templates/`.

If the user is already mid-deck (a brief file already exists in the session folder), skip this step — locate the brief in the session folder and resume from the edge case handler (see "Handling edge cases").

---

### Step 0.5 — Intent & Objective

Before asking about the argument, understand *why this deck exists* and what it needs to accomplish. Four questions — ask them together, not one at a time:

> *"Four quick questions before we structure anything:*
> *1. What does the audience need to do, decide, or believe differently after seeing this deck?*
> *2. What's the context — is this an update, a decision request, a justification, a pitch, or something else?*
> *3. What does success look like when they leave the room — do they approve, act, align, or just leave informed?*
> *4. What's the hardest objection they'd raise?"*

Use the answers to establish:
- **The outcome the deck must produce** (approval, alignment, action, awareness)
- **The belief gap** (what they currently think vs. what they need to think)
- **The objection to pre-empt** (usually load-bearing for the argument structure)

If answers are vague ("they need to understand our progress"), push back specifically:
> *"'Understand progress' is a topic, not an outcome. What do you need them to do differently after the meeting? Approve more budget? Change their prioritization? Stop escalating to the steering committee?"*

---

### Step 0.6 — Content Framework Routing

Based on the intent from Step 0.5, determine whether the user needs help developing the strategic content, or already has the analysis and just needs to structure the communication.

**Ask:**
> *"Do you already have the analysis and findings — and this deck is about communicating them? Or are you also working through what you think, and the deck needs to reflect that thinking?"*

**If they have the analysis:** Skip to Step 0.7.

**If they're still developing the thinking:** Identify the central question the analysis needs to answer, then suggest the right strategic framework(s) from the table below.

#### Strategic framework routing

| Central question | Use these frameworks | Reference file |
|-----------------|---------------------|---------------|
| "What is going on in this industry?" | Porter (Five Forces, value chain) + Christensen (disruption scan) | `02_porter_competitive_strategy.md`, `05_christensen_innovators_dilemma.md` |
| "What should we do?" | Lafley & Martin (strategy cascade) + Rumelt (pressure-test) | `03_lafley_martin_playing_to_win.md`, `01_rumelt_good_strategy.md` |
| "Is this strategy sound?" | Rumelt (kernel test) + 7 Powers (advantage durability) | `01_rumelt_good_strategy.md`, `06_helmer_7_powers.md` |
| "How do we grow?" | Blue Ocean (value innovation, four actions) + Christensen (Jobs to Be Done) | `04_kim_mauborgne_blue_ocean.md`, `05_christensen_innovators_dilemma.md` |
| "Why are we losing / under pressure?" | Christensen (disruption trajectory) or Porter (structural shift) + Rumelt | All three relevant files |
| "Should we make this investment?" | Rumelt (is the logic actually a strategy?) + 7 Powers (does it build advantage?) | `01_rumelt_good_strategy.md`, `06_helmer_7_powers.md` |
| "Who are we and why pick us?" | 7 Powers (what's our differentiated position that competitors can't replicate?) | `06_helmer_7_powers.md` |
| "What happened vs. plan?" (updates, QBRs) | None — skip this layer, go to Step 0.7 | — |
| "How does this work?" (process, training) | None — skip this layer, go to Step 0.7 | — |

**Coaching rule:** Suggest at most 2 frameworks for any given question. More than 2 produces a thick deck with no clarity. If the question doesn't fit the table cleanly, ask: *"What's the one thing the audience needs to be convinced of?" — that usually surfaces the right framework.*

**Use the framework to develop the content, not to structure the slides.** The framework shapes what to think and what to include; the narrative framework (Step 0.7) shapes how to say it.

---

### Step 0.7 — Narrative Framework + Deck Type

With the content established (or already in hand), choose the communication structure. This is two decisions made together.

#### Decision 1 — Narrative framework (how to say it)

Based on the outcome from Step 0.5 and the central question from Step 0.6, suggest 2–3 of the following. Explain why each fits, let the user pick. The chosen framework becomes the spine.

| Framework | Best for | Tradeoff |
|-----------|----------|----------|
| **SCR** (Situation → Complication → Resolution) | Recommendations, problem diagnosis, any deck where the audience needs to accept the problem before accepting the solution | Can feel slow if the audience already agrees on the situation — leads with context rather than conclusion |
| **Pyramid** (conclusion first → supporting evidence) | Executive updates, decision requests, audiences with high power and low patience | Risky if the audience hasn't bought into the premise — they may reject the conclusion before hearing the evidence |
| **MECE issue tree** | Problem diagnosis, root cause analysis, capability assessments with multiple workstreams | Too analytical for relationship-focused audiences; better as the analytical backbone than the visible structure |
| **Before / Now / After** | Capability pitches, transformation decks, progress narratives | Emotionally resonant but weak on evidence alone — needs data underneath each state |
| **Trend → Insight → Implication** | Market analysis, QBR/business reviews, data-heavy decks | Requires strong data; collapses without it; avoid if data is directional or contested |
| **Challenge → Solution → Benefit** | Pitches, product or service introductions, proposal sections | Concise and buyer-centric but too thin for complex recommendations — use for sections, not full decks |
| **Current State → Future State → Gap** | Strategic planning, transformation roadmaps, capability gap analyses | Needs a credible future state — if "future state" is vague, the whole structure collapses |
| **Objective → Approach → Proof → Ask** | Partnership proposals, commercial pitches, structured selling decks | Maps to buyer journey but can feel formulaic if the Approach section is generic |

**Coaching note:** If the user's deck is a QBR or business review, Trend → Insight → Implication is usually the right spine — each workstream or metric tells a mini-story of trend + what it means + what changes. SCR or Pyramid applied to a QBR forces an argument structure onto a reporting context and produces awkward governing thoughts.

#### Decision 2 — Deck type confirmation

Confirm which deck type this is. The type sets vocabulary expectations, gate checks, and the editorial rhythm.

| Deck type | Structural spine | Governing thought standard |
|-----------|-----------------|---------------------------|
| **Recommendation / Point of View** | Situation → problem → recommendation → evidence → ask | Must assert *what to do* and *why now* — not just what the situation is |
| **Problem Diagnosis** | Symptom → root causes → intervention | Must assert a *cause*, not just describe a symptom |
| **Strategic Plan** | Ambition → where to play → how to win → required capabilities | Must assert the *strategic bet* — what we're choosing to do and what we're choosing not to do |
| **Market & Competitive Analysis** | Industry structure → positioning landscape → implication | Must name the *implication for our client*, not just describe the market |
| **Business Case / Investment Decision** | Problem → options → recommended choice → financial and strategic case | Must name the *decision being enabled* — not just summarize the analysis |
| **Feasibility Study** | Question → approach → findings → verdict | Must deliver a *verdict*, not just a list of considerations |
| **QBR / Business Review** | Planned vs. actual → variance → drivers → outlook | Must explain *variance and what it means* — not just report actuals |
| **Status / Progress Update** | Where we are → against what plan → what's changed → next actions | Must name *implications*, not just progress percentages |
| **Board Update** | Decision ready summary → key facts → recommendation or ask | Must tell the board *what they need to do or decide*, not just inform them |
| **Executive Briefing** | One question → answer → support → so-what | Single governing thought; every slide either answers the question or supports the answer |
| **Capability / Credentials Pitch** | Current gap → our capability → proof → why us | Must assert *what we can do that others can't* — not just what services we offer |
| **Investor / Commercial Pitch** | Problem → solution → market → traction → team → ask | Must make the *financial or strategic case* for why this is worth backing |
| **Partnership Proposal** | Shared interest → proposed structure → joint value → ask | Must name *why this specific partnership* — not just propose a generic arrangement |
| **Workshop Design** | Purpose → agenda → session objectives → pre-work ask → ground rules | Must name *what decisions come out of this workshop* — not just what topics are covered. Each session slot has an objective and a desired output, not a governing thought. |
| **Workshop Readout** | Working question → what we explored → decisions made → next owners | Must name *what changed or was decided* — not just what was discussed |
| **Facilitation Deck** | Frame → explore → converge → commit | Governing thought per section, not per slide — slides are prompts, not arguments |
| **Training / Enablement** | Why it matters → how it works → when to use it → practice | Must teach a *transferable skill or method*, not just describe a process |

**Workshop Design decks:** jump to the **Workshop Design Coaching Overlay** section at the end of this file before proceeding.

**If the framework choice and deck type don't align, flag the tension explicitly.** Example: *"You picked Pyramid (conclusion first) but you're building a Problem Diagnosis deck where the audience doesn't know the conclusion yet — leading with the answer may cause them to reject it before they've accepted the problem. Do you want to flip to SCR, or do you have reason to believe this audience will accept the conclusion upfront?"*

---

### Step 1 — Opening

By this point the intent (Step 0.5), content framework (Step 0.6), and narrative spine + deck type (Step 0.7) are established. Now commit the governing thought — the deck's argument in one sentence.

> *"Given [the outcome from Step 0.5] and the [chosen narrative framework] spine — what's the one-sentence argument this deck makes? If the audience reads nothing but the title slide, what should they take away?"*

If the user has a clear governing thought, you're off to the races. If not, run the Foundation Check — the three questions already asked in Step 0.5 are the inputs; help them synthesize an answer from those.

### Step 2 — Audience and current belief

> *Who's this for, and what do they currently believe about [topic]?*

"Leadership" is not an audience. Push for specifics: the CFO and CIO, or the EVP of ops, or the steering committee. "They'll be interested" is not a belief. Push for what they currently think, and what the deck wants to change.

If the audience has internal disagreement (CFO wants cost story, CIO wants capability story), the deck has to decide who's the primary audience. Name that decision — don't paper over it.

### Step 3 — Infer the argument shape

By now the framework is chosen (Step 0.7). Steps 3–4 apply it to this deck's specific governing thought and audience — a different task from choosing it.

Given the governing thought and audience, sketch the argument shape out loud:

> *So we're telling [audience] that [governing thought]. That's going to need: (a) why they should care, (b) the evidence that makes the case, (c) the so-what. We could structure this as [specific frame — e.g., "situation → complication → resolution, with the resolution being your recommendation"]. Or [alternate frame]. Which feels right?*

Let the user react. They often know their content better than any framework suggests — meet them with their content, not with a framework.

### Step 4 — Argument shape check

By this point the narrative framework is already chosen (Step 0.7). This step confirms it still fits now that the governing thought and audience are concrete.

Name the chosen framework and show how it maps to this specific deck:

> *"We're using [chosen framework]. For this deck that means: [concrete mapping — e.g., 'Situation is the current vendor relationship, Complication is the three behavioral patterns, Resolution is the two-prong intervention']. Does that still feel right now that we have the governing thought?"*

If the mapping feels off, revisit Step 0.7 — this is a normal part of the process, not a failure. Common mismatch: the user chose Pyramid but the governing thought reveals the audience doesn't accept the premise yet (switch to SCR). Or chose SCR but the audience already knows the situation (skip the Situation section).

If the content doesn't fit the chosen framework after all: build bespoke. Don't force a framework onto content that resists it.

### Step 5 — Build the sequence

Walk through slides one at a time. For each slide, the user produces an archetype classification (5.0) plus five fields (5a–5e), then runs an archetype-specific quality check (5f) before the slide is complete. The archetype determines which quality questions apply — different slide types fail in different ways.

> **⛔ Hard rule — per-slide handshake (added 2026-05-26 after OTC dry run failure).** Each slide requires **at least one user turn** between archetype classification (5.0) and the archetype-specific quality check (5f). If you have not received a user turn for slide N, you may not begin slide N+1. **No batching. No inference from prior documents.** If the user gave rich input documents (POV, framework, notes, prior decks), use them as evidence to *push back* when the user's per-slide answer contradicts them — never as a *substitute* for the user's per-slide answer. The user's tacit knowledge is never fully captured in their input documents; the coaching loop is where it surfaces.
>
> **Defensible-default trap.** When the input documents make it possible to "guess" the governing thought for slide N, the tempting move is to write it for the user and ask them to react. Resist. The reaction-mode answer ("looks good") is not the same as the authorship answer ("here's what I actually believe and why"). The deck inherits whichever one shows up. See memory `feedback_cocreate_not_infer.md`.

**5.0 — Classify the slide's archetype.** Before working 5a–5e, identify which archetype this slide is. The archetype determines the questions in 5f.

| Archetype | When it fits |
|---|---|
| Cover / Title | Title page, section divider |
| Executive Summary | Page-one answer — the deck's argument compressed onto one slide |
| Context / Situation | Sets the scene; what changed; the complication |
| Approach / Methodology | How the work was done; workstreams; what's out of scope |
| Analytical (chart-driven) | A chart or data visualization is the slide's primary element |
| Framework / Conceptual | 2×2, maturity curve, model, or other conceptual diagram |
| Synthesis / Findings | Top findings rolled up; cross-cutting themes |
| Recommendation | What we recommend doing, and why |
| Roadmap / Implementation | Timeline, milestones, critical path |
| Risk | Risks and mitigations |
| Financial / Business case | Numbers, assumptions, business case logic |
| Decision / Ask | What the audience must decide, by when |
| Appendix | Backup detail referenced from main pages |

If two archetypes seem to fit (e.g., a chart-heavy financial slide), pick the one that names the slide's PRIMARY function — what kind of work does the slide do? If the user can't pick one, that's a signal the slide may be doing too much. Help them pick one function, then consider whether to split the slide.

**5a — Governing thought.** The declarative claim the slide makes.

> *What's the governing thought for slide N? What's the one declarative sentence that slide proves?*

**5b — So-what.** The takeaway the audience should walk away with. This is different from the governing thought:
- Governing thought = the *claim* ("Three patterns explain 80% of the drift — and none are policy violations")
- So-what = the *takeaway* ("This is not a compliance problem, it's an information problem — don't fire managers, give them data")

The so-what is often what reframes the audience's belief. The governing thought states what's true; the so-what states what the audience should now believe differently.

> *If the exec remembers one thing from this slide after they leave the room, what should it be? Not what the slide claims — what the claim should change in their head.*

If the user gives a so-what that's a restatement of the governing thought, push back: *"That's the claim. What does the claim imply — what belief does it shift?"* This distinction is often where consultants plateau; coaching the gap here is load-bearing.

**5c — Editorial emphasis.** What should dominate the slide visually. One of:
- **The conclusion** — the so-what is the main visual element; evidence is subordinate
- **The evidence** — the data/chart is the main visual element; takeaway is a caption
- **The contrast** — two states side-by-side with the change point as the anchor
- **The data** — a chart carries the whole argument
- **The ask** — a CTA or decision point is dominant; context supports it
- **The numbers** — one or two headline stats carry the visual weight

> *What should dominate the slide? What should the audience's eye land on first?*

If the user says "all of it equally" — push back. An exec slide that doesn't have a dominant element reads as a worksheet, not an argument. Help them pick.

**5d — What this slide is NOT.** Explicit scope exclusion. Prevents the builder from creeping into adjacent detail.

> *What's NOT on this slide? What would an inexperienced consultant be tempted to add that would dilute the argument?*

Examples:
- Slide 2 (three patterns explain drift): NOT a root-cause deep-dive, NOT a manager performance review, NOT an exhaustive list of all drift causes
- Slide 4 (implementation plan): NOT a detailed project plan, NOT a risk register, NOT a full RACI

This field catches scope creep before it reaches the builder. One bullet per slide is enough.

**5e — Chart data (when applicable).** After 5d, determine whether this slide needs a chart or data visualization.

**Trigger this step when any of the following is true:**
- The editorial emphasis (5c) is "the data" or "the evidence" AND the evidence references quantitative data (numbers, percentages, trends, comparisons)
- The content describes a trend over time, a comparison between options, a breakdown of components, a ranking, or a variance analysis
- The governing thought asserts something that a chart would prove (e.g., "costs grew faster than revenue," "three segments drive 80% of profit")

**Skip 5e entirely** when the editorial emphasis is "the conclusion," "the ask," "the contrast," or "the numbers" and the content is a callout stat or text-driven argument with no underlying data series.

If a chart is needed, ask two questions in sequence:

> *"What type of chart does this slide need?"*
> *(e.g., bar/column, horizontal bar, line, pie, donut, waterfall/bridge, clustered bar, stacked bar)*

Then:

> *"Please provide the data — paste a table below, or give me the path to a CSV or Excel file in your `_reference/` folder."*

If the user doesn't have the data yet:

> *"No problem — I'll build the slide with an amber placeholder labeled '[chart type] — data TBD.' You can provide the data in a follow-up session."*

**Accepted data formats:**
- Inline table (markdown or plain CSV pasted into the chat)
- File path to a CSV or Excel file (e.g., `_reference/savings-by-quarter.xlsx`)
- "TBD — placeholder" if data is not yet available

**5f — Archetype-specific quality check.** After 5a–5e are filled, run the questions for this slide's archetype (from 5.0). These catch failures specific to the slide type — different archetypes fail in different ways.

| Archetype | Questions to ask |
|---|---|
| Cover / Title | Does the title state what this is about, not just the project codename? |
| Executive Summary | If the audience only reads this page, do they have the answer? Is the recommendation explicit and singular, not hedged? Are the three supporting points each independently strong enough to motivate action? |
| Context / Situation | Why are you telling the audience this — have they lived it? What's the complication — what changed or broke? Is the data recent and specifically sourced? |
| Approach / Methodology | Why these workstreams and not others? What's explicitly out of scope? Did you engage the people whose buy-in you'll need? |
| Analytical | Does the title state the *insight*, not the *topic*? Is this the simplest chart that proves the point? Is the data window honest — does it disconfirm as well as confirm? Does the page have a clear takeaway the eye lands on? |
| Framework / Conceptual | Why these two axes — are they actually independent? Where is the client on this framework, and where do they need to be? Does the model produce a *decision*, or just a vocabulary? Is the framework adapted to the client, or generic? |
| Synthesis / Findings | Are these genuinely the top three findings? Are these findings or observations? (Findings have numbers and consequence; observations are vibes.) Is each finding traceable to the analysis that proved it? |
| Recommendation | Is it specific enough that someone could act on it Monday? Who owns it, by name or role? What's the second-order consequence? What alternative was rejected, and why? What's the no-regret part to do regardless? |
| Roadmap / Implementation | Is the critical path identified? Where do you assume people, budget, approvals come from? What's in the first 30 days — is there an early proof point? Where are the off-ramps if something goes wrong? |
| Risk | Are these the risks that actually keep the audience up at night, or the safe ones? Is each risk sized, owned, triggered, and mitigated? **What's the risk you're NOT listing because it's awkward?** |
| Financial / Business case | What's the assumption the audience should disagree with first? Where's the sensitivity? What's the break-even and when? Are the cost categories MECE? Has the client's finance function seen these numbers? |
| Decision / Ask | What exactly is the audience being asked to decide? Is each decision binary or selectable? What's needed, by when? **What happens if the answer is no?** |
| Appendix | Is every page defensible if opened at random in front of the client? Is it indexed so the right backup is findable? Does the main deck point to specific appendix pages? |

Failures here go into the gate's review output (Step 7) tagged to this slide. They are typically **Major** unless the slide is structurally broken (then **Critical**) or the failure is a judgment call (then **Advisory**).

**Write all six fields down as you go (5.0 + 5a–5e, plus 5f notes).** If the user is struggling on any field, that's a signal: struggling on governing thought means the slide isn't load-bearing (consider cutting); struggling on so-what means the user hasn't committed to what they want the audience to believe differently (coach toward it); struggling on editorial emphasis means the user hasn't decided what the slide's main move is (coach toward it); struggling on "what this is NOT" usually means the slide is overloaded (consider splitting); struggling on archetype classification usually means the slide is doing too many jobs.

Ask:

> *What breaks if we don't have this slide? If the audience skips it, does the argument still land?*

Cut slides that don't justify themselves.

### Step 6 — Deck-level editorial rhythm

Before the gate, name the deck's visual rhythm in one sentence. Read the editorial emphasis for each slide:

> *Slide 1: data dominates. Slide 2: conclusion dominates. Slide 3: contrast dominates. Slide 4: numbers dominate. That's four different dominance patterns across four slides — the deck will have visual rhythm.*

If three or more consecutive slides have the same editorial emphasis, flag it:

> *Slides 2, 3, and 4 all have "conclusion dominates" — the deck is going to feel like one long sermon with no evidence or data in the middle. Usually an argument-heavy deck needs at least one slide where data or contrast carries the weight. Is that intentional, or should one of these be restructured?*

Let the user decide. If intentional, note it in Flags. If not, revise the editorial emphasis for one slide.

Also name the deck-level accent discipline — one sentence:

> *Across the deck, the accent color (orange) should anchor one element per slide: slide 1 the inflection callout, slide 2 the reframe line, slide 3 the changed step, slide 4 the headline numbers. Each slide gets one orange element, semantically consistent.*

This gives the builder a deck-wide rule for the contrast accent instead of leaving it to per-slide judgment.

### Step 7 — The gate: nine-part test + cross-cutting rules + completeness check

Before producing the narrative brief, run all nine parts plus the cross-cutting rules sweep. The gate is strict because everything downstream inherits whatever we hand off. The output is a structured review (see "Review output" below) that the user can act on. Two parts are hard stops with no override path: **Part 6 (internal consistency)** and any **Critical** issue surfaced by other parts — Criticals must be fixed, not overridden. Major and Advisory issues use the constructive-pushback / override-with-reason protocol from Step 8.

**Part 1: per-slide insight test (governing thought).**

Walk each slide's governing thought. For each: is it an insight or a topic?

- **Topic** (fails): "Q3 revenue overview" / "Customer segmentation" / "Our recommendation"
- **Insight** (passes): "Q3 revenue grew 23% but margin contracted due to mix shift" / "Three customer segments drive 80% of profit but get 30% of sales focus" / "Rebuild the enterprise team in APAC before Q2"

If you can turn the slide into a declarative sentence with subject + verb + claim, it passes. If not, fail and ask: *"What does slide N actually prove?"*

**Part 2: so-what test.**

For each slide, the so-what must be *different from* the governing thought and must name a *belief shift*. Failure modes:

- Fail: so-what is a restatement ("Three patterns explain the drift" → so-what: "There are three patterns that explain the drift"). That's the claim again, not a takeaway.
- Fail: so-what is a generic motherhood statement ("we need to take action," "this is important"). Not actionable, not specific.
- Pass: so-what names a specific belief the audience should now hold that they didn't before. For slide 2 in the FedEx example: "This is not a compliance problem, it's an information problem — don't fire managers, give them data."

If a so-what fails, push back: *"That's the claim again. What belief should the audience now hold that they didn't before reading this slide?"*

**Part 3: editorial emphasis test.**

Each slide must have exactly ONE dominance call. "All elements equal" fails. Three consecutive slides with the same dominance call gets flagged for deck rhythm (see Step 6) but doesn't fail the gate if the user explicitly accepted it during Step 6.

Also check: is the editorial emphasis *consistent* with the so-what? If the so-what is "this is not a compliance problem, it's an information problem" (a reframe), but the editorial emphasis is "the evidence dominates" — that's inconsistent. A reframe needs the conclusion to dominate, or the reframe gets buried under evidence. If inconsistent, push back: *"Your so-what is a reframe, but your editorial emphasis says the evidence should dominate. The reframe is the point — shouldn't it be what the audience sees first?"*

**Part 4: title-only coherence test.**

Read only the governing thoughts (which become slide titles) in sequence:

> *Let me read the titles back in sequence:*
> *1. [title 1]*
> *2. [title 2]*
> *...*
>
> *Stepping into the shoes of [audience], who hasn't seen the analysis — do the titles alone tell the story you need them to leave with?*

Common failure modes this catches:
- Sequence breaks (slide 4 concludes something slides 1-3 don't build to)
- Missing pivot (every slide is a finding, nothing turns)
- Buried recommendation (appears at slide 10 but first 9 don't build toward it)

Fail this part → return to Step 5 for the affected slides.

**Part 5: deck-type governing thought test (conditional).**

Apply the check specific to the confirmed deck type from Step 0.7:

| Deck type | Check |
|-----------|-------|
| Recommendation / Point of View | Does the governing thought assert *what to do* AND *why now*? Fail: "We need to address the vendor gap." Pass: "Closing the vendor gap before Q3 protects $12M in at-risk revenue and prevents the client from sourcing direct." |
| Problem Diagnosis | Does it assert a *cause*, not just a symptom? Fail: "Costs are rising." Pass: "Labor cost growth is driven by unplanned overtime, not headcount — the fix is scheduling, not a hiring freeze." |
| Strategic Plan | Does it name the *strategic bet* — what we're choosing to do AND what we're choosing not to do? Fail: "We will pursue digital transformation." Pass: "We are concentrating all FY26 investment in supply chain digitization and explicitly exiting the retail platform business." |
| Market & Competitive Analysis | Does it name the *implication for the client*, not just describe the market? Fail: "The market is growing at 12% CAGR." Pass: "At 12% CAGR, the window to establish a cost-leadership position closes in 18 months — after that, incumbents will have locked in scale advantages." |
| Business Case / Investment Decision | Does it name the *decision being enabled*? Fail: "The investment has a strong ROI." Pass: "The $4M platform investment pays back in 14 months and eliminates the manual reconciliation risk that is the firm's single largest audit exposure." |
| QBR / Business Review | Does it explain *variance*, not just report it? Fail: "Q3 revenue was $42M, 3% below plan." Pass: "Q3 revenue missed by 3% because APAC deal slippage offset EMEA outperformance — the risk is concentrated, not systemic." |
| Status / Progress Update | Does it name *implications*, not just progress? Fail: "We have completed 6 of 10 workstreams." Pass: "6 of 10 workstreams are on track; the 4 at-risk workstreams are all on the critical path — a 3-week slip here moves the go-live date." |
| Board Update | Does it tell the board *what they need to do or decide*? Fail: "Here is the quarterly performance summary." Pass: "Performance is on track; the board needs to decide today whether to accelerate the M&A timeline before the Q1 earnings window closes." |
| Capability / Credentials Pitch | Does it assert *what we can do that others can't*? Fail: "We have deep experience in supply chain." Pass: "Our proprietary cost-benchmarking tool cuts diagnostic time from 12 weeks to 3 — no competitor has deployed it at scale outside North America." |

Fail → return to the affected slides. The deck-type test is not optional even for fluent users.

**Part 6: internal consistency (hard stop).**

After Parts 1–5 pass, read pairs of adjacent slides and any slides that share a topic. Do any two slides argue claims that cannot both be true?

Examples of what to catch:
- Slide 3 says *"data quality is the root cause"* → Slide 5 says *"the system is the root cause"* — pick one or reconcile
- Slide 2 says *"we recommend acquiring X"* → Slide 4 says *"the market doesn't support an acquisition"* — reconcile or cut one
- Slide 1's so-what is *"the program is on track"* → Slide 3's so-what is *"the program is at risk"* — these are not nuance, they are contradictions
- Two slides cite different numbers for the same metric without explanation — pick one source

If contradictions exist, the gate **fails**. This is a hard stop — **the constructive-pushback / override protocol in Step 8 does not apply here**. Diverging thoughts in the same deck are a structural failure, not a stylistic choice or a deliberate tension. They must be reconciled before the brief is produced. State the contradiction explicitly to the user — *"Slide 3 and Slide 5 say different things about the root cause. Which one is the deck arguing?"* — then re-enter Step 5 for the affected slides.

**Part 7: 30-second answer test (deck level).**

Can the deck's answer be stated in 30 seconds? Read the deck-level governing thought aloud (or to yourself, mentally counting). If it takes more than 30 seconds to deliver the answer, the storyline is bottom-up — the audience has to wait through setup to learn the point.

- Pass: governing thought is one or two sentences, lands the answer immediately.
- Fail: governing thought needs preamble, lists three things before the verb, or hides the recommendation in subordinate clauses.

If it fails, return to Step 1 — the governing thought needs to be re-compressed. Failure is **Major** in the review output. Override path applies: the user can ship a longer governing thought if they articulate why (e.g., "this audience needs the SCQA setup before the answer").

**Part 8: Decision required test (deck level).**

What decision is the audience being asked to make? Does the deck name it explicitly, with a deadline?

- Pass: a specific decision is named (approve, fund, prioritize, sign off, escalate), with a date or condition, on the deck's Decision/Ask page or in the governing thought.
- Soft pass: deck type is Status / Progress Update or Board Update where "FYI" is legitimate — no decision required by design.
- Fail: deck is a Recommendation / Strategic Plan / Business Case / Decision archetype but the ask is missing, vague ("align on next steps"), or undated.

Failure is **Major**. Override path applies.

**Part 9: Dissent test (conditional — Recommendation / Strategic Plan / Business Case / Decision-Required decks only).**

Does the deck pre-empt the two or three obvious objections an executive will raise, or pretend they don't exist?

- Pass: the brief has either a Risk slide that names the load-bearing objections OR the Recommendation slide includes "alternatives considered and rejected."
- Fail: the deck has no place where the obvious objections live. Executive audiences will fill that vacuum with their own.

Failure is **Major**. Skip this Part entirely for deck types where dissent is not the audience's mode (Status Update, Board Update, Workshop Design, Capability Pitch, Training).

**Cross-cutting rules sweep.**

After Parts 1–9, run two universal checks across all slides:

1. **No page without a point.** If you can delete a slide and the deck's argument survives, the slide was decoration. Cut it or rework its governing thought. Violation tagged **Major** on the offending slide.

2. **No claim without source.** Every external number, quote, market data point, or competitive benchmark must name a source (file, study, interview date, internal report). Sourcing the citation correctly is a downstream concern (slide-builder); the *presence* of a source is the gate's concern. Missing-source violations are **Major** on the slide that makes the unsourced claim.

**All nine parts plus the cross-cutting rules sweep plus the brief completeness check must produce no Critical issues and must surface all Major/Advisory issues for the review output.** Downstream quality depends on this gate being strict.

**Brief completeness check (runs alongside the nine parts):** After all nine parts and the cross-cutting rules sweep complete, verify that every slide has a non-empty "What this slide is NOT" field (5d). This field is mandatory — it is not optional detail. A slide brief without a scope exclusion gives Slide Builder no boundary and will produce slides that creep into adjacent content. If any slide is missing 5d, return to Step 5 for that slide and ask: *"What would an inexperienced consultant be tempted to add to this slide that would dilute the argument?"* Do not produce the brief until every slide's 5d is filled.

Chart data (5e) is only checked when the editorial emphasis calls for a data visualization. If 5e is empty and no chart is needed, that is correct — skip it.

**When all parts pass → do not produce the brief yet. Run Step 7.5 (Language quality pass) first. The brief is only produced after Step 7.5 completes.**

---

### Step 7.5 — Language quality pass

Run this after the nine-part gate completes and any Critical issues have been fixed, and before producing the brief. It is a separate pass — do not run it slide-by-slide during Step 5 or it will interrupt the structuring flow. Major and Advisory issues from the gate are surfaced via the Step 9 review output, not in this language pass.

#### Headline quality (governing thoughts)

Test each slide's governing thought against three checks:

1. **Verb test.** Does it use an active verb that implies a direction or a finding? Fail: "Revenue overview." Pass: "Revenue grew 20% but margin eroded — the mix shift is the story." If it fails, write a rewrite and ask the user to confirm or redirect.

2. **Specificity test.** Does it include at least one concrete anchor — a number, a named driver, a named action, a named entity? Fail: "Performance was mixed across regions." Pass: "EMEA grew 15%; APAC declined 8% due to regulatory delays in Singapore." If it fails, ask: *"What's the most specific thing you can say here — what number, what name, what decision?"*

3. **Concision test.** Is it under 12 words? If not, can it be tightened without losing the claim? Long governing thoughts usually contain two claims — split them if so.

For each headline that fails: show a before/after rewrite. Ask the user to confirm or redirect. **Override is not offered here as a peer option** — keeping a failing headline requires going through the constructive-pushback protocol in Step 8 (name the weakness, offer concrete alternatives, ask explicitly). Do not proceed to the next slide's check until the user responds.

#### Body content quality (supporting bullets and evidence)

Test each slide's evidence bullets against four checks:

1. **Supports-the-claim test.** Does every bullet directly prove or illustrate the governing thought? If a bullet is true but doesn't connect to the claim, it belongs on a different slide or gets cut. Fail: governing thought = "Margin eroded due to product mix shift" → bullet: "The team delivered 12 projects this quarter." Pass: same headline → bullet: "SMB deals grew 40% but carry 18pp lower margin than enterprise deals."

2. **One-idea-per-bullet test.** Does each bullet contain exactly one idea? Multi-idea bullets are the most common body content failure. Split them or cut the weaker idea. Fail: "Revenue grew 20% and while margin declined, the team outperformed on NPS and customer retention was stable." Pass: Two bullets — "Revenue grew 20%" and "Margin declined 3pp despite revenue growth."

3. **No-filler test.** Cut anything that restates the headline, summarizes what the audience already knows, or hedges without adding substance ("it is important to note that," "there are several factors contributing to," "as mentioned above"). Fail: "As noted above, there are multiple factors contributing to the margin decline." Pass: Remove it entirely — if it needs to be said, it should be a concrete point, not a bridge sentence.

4. **Specificity ratio test.** At least 60% of the content in each bullet should be concrete — numbers, names, timeframes, decisions, sources. Fail: "Performance was mixed across regions with some areas doing better than others." Pass: "EMEA grew 15%; APAC declined 8% driven by a single delayed contract in Singapore worth $4M."

**Deck-type body content calibration:**
- **Executive audiences (board, C-suite):** Each slide should communicate its full point in the headline alone. Body = proof only. If a reader grasps the slide from the headline without reading the body, that's correct.
- **Operational audiences (working teams, project leads):** Supporting detail in the body is appropriate — process steps, criteria, instructions.
- **Mixed rooms:** Default to executive compression — operational detail goes in the appendix or speaker notes.

### Step 8 — Pushback protocol

When the user's thinking has a structural problem, use the four-beat pattern:

1. **Name the problem specifically.** Not "these slides need work." Something like: *"Slides 3 and 4 are saying the same thing — both are about cost increases. Slide 4 doesn't add the why."*

2. **Explain the consequence.** *"The audience will notice the repetition and wonder what they're missing. It erodes trust in the rigor."*

3. **Show what good looks like with a concrete alternative.** *"Two options: merge them into one slide titled 'Labor costs drove 60% of the increase,' or keep slide 3 as the overall story and sharpen slide 4 to name the biggest driver specifically."*

4. **Ask one specific question.** *"Which feels right for your audience?"* Not *"what do you think?"*

If the user produces another vague answer, escalate to framework walkthrough:

> *Sounds like this is hard to pin down. Want to walk through this with the Pyramid Principle? Start from the recommendation and work backward to supporting findings. Forces you to commit to a recommendation and then figure out what's load-bearing. Takes 10 minutes.*

If the user insists on proceeding despite a flagged issue, do not just acquiesce. Use the constructive-pushback protocol:

1. **Name the weakness explicitly and give the reason.** Not *"this might be a little weak."* Say: *"This argument is weak — it doesn't create a clear message because [reason: the claim isn't supported by the evidence on the slide / the two slides argue diverging things / the so-what restates the claim instead of shifting belief]."*

2. **Offer two concrete alternatives.** Specific rewrites or restructures, not generic advice. *"A stronger version would be either [X — concrete option] or [Y — concrete option]."*

3. **Offer the placeholder path.** If the gap is missing information or unvalidated data — not flawed thinking — give the user a way to keep moving without shipping a flaw: *"Or if you don't have [the specific data / the validation] yet, we can mark this slide as needing [specific input] and continue. The deck gets built around the gap and you fill it once you have it."*

4. **Ask explicitly: are you sure?** *"Which do you want — option X, option Y, the placeholder, or proceeding as-is?"* Do not accept silent override.

5. **If the user still chooses to proceed as-is**, record their stated reason verbatim in the brief's **Flags** section. Format: *"User chose [their reason in their own words] over [the flaw, in your words]. Audience will likely see: [concrete consequence]."*

6. **If the user refuses to engage** — "just keep it," "doesn't matter," "we're fine" — the gate fails. Soft override is not sufficient. Re-ask: *"I need one sentence from you on why this is the right call before we proceed. What's the trade-off you're making?"*

### Step 9 — Review output, then produce the narrative brief and confirm

After the nine-part gate, the cross-cutting rules sweep, the Step 7.5 language pass, and the brief completeness check have all run, produce the **Review output**. This is the structured report the user reads to decide what to fix and what to ship.

> **⛔ Hard rule — review must be acknowledged (added 2026-05-26 after OTC dry run failure).** The brief is NOT saved until the user has **explicitly acknowledged** the Review output table — including when the table contains only Advisories. **Self-passing the gate is not a pass.** The exact words "produce the brief," "ship it," "looks good — save," or equivalent must come from the user. If you ran the gate against your own brief and graded it yourself, surface the table and wait. Do not write the brief file before the user responds.
>
> **Defensible-default trap.** When the gate produces zero Criticals + zero Majors + N Advisories, the tempting move is to call it a pass and save the brief. Don't. Advisories are *advisory to the user*, not *clearance for Claude*. The user might look at advisory #3 and say "actually, that's a Critical for this audience — let me fix it." That option vanishes the moment the brief is on disk.

#### Review output format

Use this exact format. Markdown rendered in chat (table renders as a real table; bold renders as bold). No code fences around the whole block.

```
[Filename of brief].md · [N] checks passed
([deck type] · [audience] · [ask summary])

| Page | Severity | Issue |
|------|----------|-------|
| Slide [N] | **Critical** / **Major** / Advisory | [one-line description of the issue] |
| [...] | [...] | [...] |
```

Then follow the table with a section conditional on what was found:

**If any Critical issues exist:**
```
⛔ Critical issues block this brief from shipping. They cannot be overridden — they have to be fixed.

[Plain-language explanation of what each Critical is and a question that forces the user to resolve it. Example: "Slide 1 and Slide 3 are saying different things about program health. Which one is the deck's position? Once you decide, the other slide's governing thought needs to match."]
```

After the user resolves the Critical, re-run the gate from the affected Part and re-show the review output.

**If no Criticals but at least one Major exists:**
```
[Slide X] has a Major issue. Do you want to fix it or move on?

Suggestions: [two concrete fix options — be specific, e.g., "add no-path bullets to Slide 3" or "add a 4th slide showing the no-path consequences"]. Or tell me why you want to ship it as-is and I'll record your reason in the brief.
```

If there are multiple Majors, address each in turn — same conversational prompt for each.

**Override path for Major issues:** The user can ship a Major as-is, but only by writing a reason in their own words (no shortcut keyword). If the user replies with anything that does not include a reason (e.g., just "skip" or "override"), respond:

> *I need either a fix or your reason for shipping with the issue. What's the reason?*

When a reason is given, append to the brief's `## Flags` section in the format:
- **Issue:** [what the gate flagged, one sentence]
- **User reason:** [their words, verbatim]
- **What the audience might see:** [the concrete consequence — Claude derives this, one sentence]

**If no Criticals and no Majors (only Advisory or clean):**
```
✓ No Critical or Major issues. Brief can ship.

[If advisory items exist:] [N] advisory items flagged — judgment calls, not blocking. Want to look at them, or hand off?
[If clean:] Hand off to slide-builder, or edit more?
```

#### Save the brief

Once the user has resolved Criticals and handled (fix-or-override) all Majors, save the brief as `_session/narrative-brief-[deck-topic].md` inside the session folder established in Step 0. The brief lives inside `_session/` so the human-readable dot-dash storyline (next step) is the only file the user sees at the session root.

Then immediately generate the companion dot-dash storyline file by running:

```bash
py -3 skills/storyline-helper/scripts/emit_dot_dash.py "<absolute path to _session/narrative-brief-[topic].md>"
```

This produces **two** files at the session root — a McKinsey-style projection of the brief (one dot per slide = the governing thought; dashes = evidence + exhibit callouts):
- `dot-dash-[topic].md` — markdown form, good for version control + editor view
- `dot-dash-[topic].html` — rendered form, good for screen-share + sending to reviewers

**The dot-dash is also embedded directly into the REVIEW.html** that slide-builder produces — collapsed by default at the top of the page. The user does NOT need to open the standalone files to proceed; they exist for sharing with stakeholders who don't have Claude Code in front of them.

After running the script, **do not** ask the user to read the dot-dash. Instead, print a tight inline executive summary in chat:

```
Storyline locked. Quick check:
  Governing thought: [the deck-level governing thought]
  Slide 1: [governing thought | "cover"]
  Slide 2: [governing thought, ≤90 chars]
  Slide 3: [governing thought, ≤90 chars]
  ... (one line per slide)

Dot-dash for sharing: <absolute path to .html file>
Hand-off to slide-builder ready. Proceeding.
```

Then **hand off immediately to slide-builder** without waiting for a confirmation. The user reviewed the brief during the nine-part gate — they don't need to re-read its projection.

**Re-run only if the brief changes.** If the user later adjusts the brief during slide-build, update the brief, re-run the gate, and re-run `emit_dot_dash.py` to keep the .md / .html in sync. Otherwise the initial generation is enough.

### Step 10 — Hand off to Slide Builder

Before handing off, verify the client template is **registered** (has `<stem>.brand.yml` + `<stem>.theme.json` sidecars next to the PPTX). If sidecars are missing, register it first via the chat-driven flow:

```bash
py -3 skills/slide-builder/scripts/register_template.py propose <client-template.pptx>
```

This produces a `<stem>.register.proposal.json` and a smoke PNG. Show the smoke to the user, take picks in chat (or `{"accept": true}` if the proposal looks right), then:

```bash
py -3 skills/slide-builder/scripts/register_template.py commit <client-template.pptx> --picks <picks.json>
```

Once `<stem>.brand.yml` exists, slide-builder's Stage-1 sanity check passes and the build can proceed.

When the user confirms the brief, **first verify the brief starts with the YAML front-matter block** (see "Narrative brief format" below). The front-matter MUST include `client_template:` and `deck_type:` keys with the values captured in Step 0. If you wrote the brief without front-matter, prepend it now before handoff — slide-builder reads this to skip its own template prompt.

Then invoke the `slide-builder` skill using the Skill tool:
Skill tool call: `skill="slide-builder"`, args=`"[absolute path to _session/narrative-brief-[topic].md file]"`

> *Handing off to Slide Builder now.*
>
> *Brief: `[absolute path to _session/narrative-brief-[topic].md file]`*
> *Template: `[absolute path to .pptx template]` (registered: brand.yml + theme.json sidecars present)*
>
> *Slide Builder: read `reference/layouts.md` and `reference/anti-patterns.md` before dispatching per-slide workers. The brand colors come from the registered `brand.yml`; the layout catalog is `reference/layouts.md` (14 patterns + 1 fallback).*

Slide Builder reads the narrative brief from the session folder, builds each slide, runs QA, produces the final deck. Control returns to the user when the deck is delivered.

---

## Narrative brief format

Saved as `_session/narrative-brief-[topic].md` inside the session folder (established in Step 0). The companion `dot-dash-[topic].md` at the session root is generated from this file via `emit_dot_dash.py`:

**The brief MUST start with YAML front-matter** so slide-builder can read the client template path and deck type without re-asking the user. The front-matter is everything between the two `---` fences at the very top of the file.

```markdown
---
client_template: <absolute path to .pptx>     # required — slide-builder errors if missing
deck_type: <one of the 16 types>               # required — drives selector deck_types match
session_folder: <absolute path to _session>    # optional — helps slide-builder anchor outputs
---

# Narrative brief: [topic]

## Deck type
[One of the 16 types from Step 0.7 — e.g., "Recommendation / Point of View"]

## Narrative framework
[The chosen communication spine — e.g., "SCR (Situation → Complication → Resolution)"]

## Strategic framework used (if any)
[e.g., "Rumelt kernel for diagnosis; 7 Powers to assess advantage durability" — or "None — analysis was pre-existing"]

## Governing thought (the whole deck)
[One sentence — the deck's argument in miniature.]

## Audience
[Specific — not "leadership." Name who they are, what they currently believe, what belief the deck wants to change, and the single sentence the room should say back.]

**Audience assumption to break:** [current belief]
**Audience belief to leave with:** [desired belief]
**The single sentence the room should say back:** [one sentence]

## Sequence

> **Slide-header convention:** every slide header line is `### Slide N — <title>` (H3, em-dash separator, title on the same line). Slide-builder's parser reads the title from the header line — a title-less `### Slide 1` is accepted but falls back to a synthetic "Slide 1" label, which surfaces awkwardly in REVIEW.html and dispatch_plan rows. Always include the title.

---

### Slide 1 — [Slide title here, e.g. "Q3 Churn: A Product-Fit Signal"]

**Archetype:** [one of: Cover / Title | Executive Summary | Context / Situation | Approach / Methodology | Analytical | Framework / Conceptual | Synthesis / Findings | Recommendation | Roadmap / Implementation | Risk | Financial / Business case | Decision / Ask | Appendix]

**Governing thought (the claim):** [declarative sentence — the slide's claim]

**So-what (the takeaway):** [the belief shift — what the audience should now hold that they didn't before]

**Editorial emphasis:** [one of: the conclusion / the evidence / the contrast / the data / the ask / the numbers] — [one line: what dominates visually and why]

**Evidence / content:**

EVERY bullet under content MUST use the format `**HEADING** — body sentence(s).` The bold heading is the card/column/pillar label that appears on the slide; the body is the supporting text. Slide-builder's translator parses this format directly into structured overrides (`{heading, body}` per item). Loose prose bullets without the bold heading + em-dash + body will fail to populate the slide and the builder will render placeholder text.

- **[Card heading 1]** — [body sentence with the supporting detail, evidence, or claim]
- **[Card heading 2]** — [body sentence]
- **[Card heading 3]** — [body sentence]

For pillar / column / option structures, prefix the bold heading with a label segment in CAPS if the slide will show one:

- **TRAINING GAP · The rigor was never taught** — Most consultants never learned it. McKinsey built it in. Most firms don't.

For cover slides (slide 1), the brief MUST include these fields in the content block:

- **Title:** [deck title — the wordmark]
- **Tagline:** [one-line tagline below the title]
- **Subtitle:** [longer subtitle / sub-tagline / context one-liner]
- **Presenter:** [name]
- **Date:** [month + year]
- **Audience / Client:** [who this is for]
- **Eyebrow (optional):** [pre-label like "INTRODUCING" or section name]

For closing-CTA slides, the brief MUST include:

- **Primary ask:** [one sentence — the single thing you want from the room]
- **Sub-asks:** 3 items, each as `**LABEL** — body sentence.`

**What this slide is NOT:** [scope exclusion — what an inexperienced consultant would be tempted to add that would dilute the argument]

**Chart type:** [bar | bar-h | line | pie | donut | waterfall | clustered-bar | stacked-bar | stacked-bar-100 | none]

**Chart data:**
[Inline table or path to CSV/Excel in _reference/, or "TBD — placeholder". Omit this field if Chart type is none.]

---

### Slide 2 — [Slide title]

[Same four-field structure repeated for each slide. Always include the title on the header line.]

---

## Flags — live issues, not historical notes
[Every entry must include three things:
  1. **The flaw** — what storyline-helper flagged, in one specific sentence
  2. **The user's reason in their own words** — verbatim, why they chose to override
  3. **What the audience will likely see** — the concrete consequence the user is shipping with

These are not historical risks. They are unresolved gaps the user chose to ship with. Downstream skills and the MD reviewer must see them.]

## Deck-level design notes (optional)
- Visual rhythm: [one sentence naming the dominance pattern across all slides]
- Accent color discipline: [one sentence naming how the contrast accent is used semantically across the deck — one element per slide]
- Any other deck-wide conventions the user wants enforced
```

The expanded format makes the brief longer than v1's version — typically 20-30 lines per slide instead of 2-3. That is intentional. The extra content is what lets the slide-builder's Phase A (design thinking) do real work instead of template-filling. A thin brief produces thin slides; the gate enforces richness.

### Brief-time quality gate (automated)

Before the brief is handed off to slide-builder, slide-builder's
`twins.brief_qc.check_brief` runs and surfaces issues in two severities:

- **Blocking** — must be fixed before the brief proceeds. Includes:
  - Title length predicted to wrap to 3+ lines (>100 chars)
  - Forbidden placeholders (`TBD`, `Lorem`, `[Client Name]`, `xxxx`, `Click to edit`, `placeholder`, `[insert ...]`)
  - Cover slide missing `title` / `tagline` / `presenter`
  - Closing-CTA slide missing `primary_ask` or fewer than 3 `sub_asks`
- **Warning** — the user should acknowledge but can ship. Includes:
  - Title length >80 chars (A1) or predicted to wrap to >2 lines (A2)
  - Card body >200 chars (A3)
  - Card heading >40 chars (A4)
  - `editorial_emphasis` with 4+ items (should be 1–3)

When the user opens the per-deck REVIEW.html, blocking + warning issues are
surfaced in a banner at the top of the page, color-coded red (blocking) and
amber (warning). Storyline-helper does NOT auto-fix any of these — it
surfaces them and asks the user to revise.

**A6 + A8 (language quality and truncation)** are now covered by a
heuristic pass:
- Run-on sentences (>35 words or >260 chars between terminator punctuation)
  fire a warning.
- Trailing ellipsis `...` on a non-title field fires a truncation warning
  at any length.
- Dangling comma / em-dash at end of a body-length field fires a
  truncation warning.
- Body-length text without terminal `.!?` fires a truncation warning.

For deeper grammar / tone / coherence analysis, slide-builder accepts an
optional `language_callback` argument to `check_brief`. The orchestrator
(Claude in the chat) is the natural place to run this — it has model
access, runs the callback per prose field on a slide, and returns severity-
tagged issues that merge with the heuristic findings. Slide-builder's
pure-Python module cannot do nuanced linguistic work alone.

**When and how to call the language callback (orchestrator instructions):**

When the user reaches Step 10 (handoff to slide-builder) and the brief
passed the structural gate, optionally invoke the language callback as
follows BEFORE writing the brief to disk:

```python
from twins.brief_qc import check_brief

def claude_language_judge(location_label: str, text: str) -> list:
    """Called once per long-form prose field in the narrative. Should return
    a list of dicts: [{"severity": "warning"|"blocking", "msg": "<issue>"}].
    Empty list = clean.
    Use the model to check for: awkward construction, tone mismatch, jargon
    that won't survive the room, hedging language that undermines the
    governing thought, sentences whose subject and verb don't agree.
    """
    # Claude calls itself here — the body is up to the orchestrator.
    ...

result = check_brief(narrative, language_callback=claude_language_judge)
```

Only invoke the callback if (a) the user has indicated they want a final
language pass, OR (b) the brief contains client-facing copy that will be
read verbatim by an executive. Skip it for working / internal briefs
where the user is iterating fast — the heuristic pass is enough.

Each callback invocation costs one model call per long-form field; for a
10-slide brief with cards, expect ~30-50 calls. Batch them with prompt
caching if the orchestrator supports it.

**Render-time QC (`twins/render_qc.py`)** also runs after each option's
PPTX is composed — it inspects shape positions and text content for:
forbidden placeholder leaks ("Click to edit Master title style", etc.),
content shapes that ended up empty (brief didn't supply override),
invariant-zone violations (shape extends below y=672), and body content
outside the safe vertical band (y=220-630). Each option in the REVIEW.html
shows a clean / warning / critical badge with hover-tooltip issue list;
critical-verdict options are blocked from selection.

### Optional per-slide steering fields (P1 enrichment)

These four optional fields let the user push the selector toward a specific visual treatment when the default scoring isn't enough. All are optional — omit them and the selector behaves as before. Add them only when the default picks would otherwise be wrong.

- **Visual rhythm:** one of `conclusion-dominant`, `contrast-dominant`, `data-dominant`, `evidence-dominant`, `ask-dominant`, `numbers-dominant`, `process-dominant`, `framework-dominant`. Boosts patterns whose `editorial_emphasis` (or family, for process/framework) aligns. Use when the editorial emphasis line doesn't capture the visual intent precisely enough.
- **Mandatory shape:** one of `two-column`, `three-column`, `four-column`, `five-column`, `2x2-grid`, or any other catalog `layout` value (e.g., `hero-with-strip`, `radial`, `header-band-table`). Heavily boosts patterns whose `layout` matches exactly (+10). Synonyms like `3-column` / `three-col` / `3col` normalize automatically. Use when the user needs the slide rendered in a specific structure regardless of intent score.
- **Forbidden patterns:** a list of pattern stems, family names, or substrings (case-insensitive). Patterns whose `family` or stem contains any forbidden token are excluded from the top-N picks. Example: `["comparison", "tables"]` rules out the entire comparison family and any pattern with "tables" in its name.
- **Accent placement:** free-form one-liner like `"recommendation only"` or `"contrast pair"`. Stored on the picked spec for downstream use; no scoring change yet. Use to communicate design intent to the user reviewing options or to a downstream styling pass.

Field placement: add these as `**Visual rhythm:**`, `**Mandatory shape:**`, etc., inside the per-slide block alongside the existing `**Editorial emphasis:**` line. The translator reads them by key name; ordering doesn't matter.

```markdown
**Visual rhythm:** contrast-dominant
**Mandatory shape:** two-column
**Forbidden patterns:** [tables, kpi-dashboard]
**Accent placement:** brand accent on the "after" side only
```

---

## Handling edge cases

### If the user says "just build it" before the gate passes

Do not hand off. Say: "I need to finish the brief first — the slide builder needs a complete brief or the output will be empty. We're on slide [N]. Let me finish this and hand off immediately." Then complete the remaining slides at pace, running the gate quickly, and hand off.

**User opens a chat mid-deck.** Check `_session/narrative-brief-*.md` inside the session folder. If it exists, the deck is already structured — don't redo Storyline Helper. Offer two paths in plain language:

> *I see an existing brief at `_session\narrative-brief-[topic].md`. What do you want to do?*
>
> *1. **Edit** — change or add something, re-run the check, save.*
> *2. **Review** — pressure-test the existing brief and report issues, no changes.*

If the user picks Edit, ask what they want to change. If the user picks Review, run the full nine-part gate + cross-cutting rules sweep against the existing brief and produce the Step 9 Review output (table + conversational Major prompts). No new file is written until the user resolves Criticals and chooses fix-or-override on Majors. Once they do, save the brief and re-run `emit_dot_dash.py`.

**User wants to add a slide to an existing deck.** Don't rebuild the whole narrative. Read the existing brief, insert the new slide's governing thought at the right position, re-run the gate, save the updated brief. Slide Builder then builds just the new slide and inserts it.

**User's answer to "what's the argument?" is a topic.** Foundation Check. Don't proceed to sequencing until the governing thought is a declarative sentence.

**User has no argument yet, just findings.** Pyramid walkthrough. Start from a provisional recommendation, work backward to what's load-bearing. This is valuable coaching work — take the time.

**User refuses pushback.** Do not just acquiesce — that lets weak arguments through. Use the constructive-pushback protocol from Step 8: (1) name the weakness and the reason it doesn't hold, (2) offer two concrete alternative framings — *"a stronger version would be X or Y"* — so the criticism is constructive, not just a no, (3) offer the placeholder path if the gap is missing data rather than flawed thinking, (4) ask explicitly which they want. Only accept the override after the user has chosen with awareness of the trade-off, and record their reason verbatim in **Flags**. If the user refuses to engage at all, the gate fails — soft "just ship it" is not sufficient.

---

## Workshop Design Coaching Overlay

When the deck type confirmed in Step 0.7 is **Workshop Design**, use this overlay instead of the standard Step 0.5 intent questions and Step 1 governing thought.

When the deck type is **Workshop Design**, replace the standard Step 0.5 intent questions and the Step 1 governing thought with this coaching flow instead. The narrative gate (governing thought, so-what, editorial emphasis) does not apply to agenda and session objective pages — they are not arguments.

**Four workshop-specific intent questions (ask together, not one at a time):**

> *"Four questions before we structure the workshop:*
> *1. What decisions need to come out of this workshop — what should participants be able to say yes or no to by 5pm?*
> *2. How many sessions, and what is each session trying to accomplish? (Even a rough agenda is fine.)*
> *3. Who's in the room — what's their level of familiarity with the topic, and is there any tension or misalignment between participants you need to design around?*
> *4. What does 'success at the end of the day' look like — what would you tell your engagement lead went well?"*

**Structural spine for Workshop Design decks:**

| Section | Purpose | Coaching standard |
|---------|---------|-------------------|
| Purpose & objectives | Why we're here and what we're deciding | Must name the specific decisions or outputs the workshop produces — not just the topic |
| Agenda | Time-blocked session plan | Each session block must have a title, duration, owner, and one-line objective |
| Session objectives | Per-session detail (optional breakout) | Each session's objective must be an action: "Align on X", "Decide Y", "Prioritize Z" |
| Pre-work ask | What participants need to prepare or bring | Must be specific — "read the attached 2-pager" not "come prepared" |
| Ground rules | How the session will run | Optional; include when the client group is large, cross-functional, or has known dynamics |

**Step 1 replacement for Workshop Design:** Instead of asking for a governing thought, ask:

> *"What's the one sentence that tells a participant why this workshop is worth their full day? Not the agenda — the reason."*

This becomes the purpose statement on the opening slide, not a governing thought. The standard five-part gate does not apply. Instead, before producing the brief, run a four-part workshop gate. **Fail any part → return to the affected section and ask the specific question listed. Do not produce the brief until all four parts pass.**

1. **Decisions test:** Does each session block have a named decision or output — not just a topic?
2. **Participant readiness test:** Does the pre-work ask give participants what they need to contribute meaningfully in session 1?
3. **Time realism test:** Does the total agenda time fit the available hours, including breaks?
4. **Decision-forcing test:** Does each session objective name a specific decision or output with enough precision that participants will know whether they achieved it by the end of the session?
   - Fails: *"Align on the program roadmap"* / *"Discuss risks"* / *"Prioritize initiatives"*
   - Passes: *"Decide which 3 of 8 workstreams proceed to Phase 2 and who owns each"* / *"Rate the top 10 risks by likelihood × impact and assign a mitigation owner to each"*
   - If vague: ask *"What would a participant be able to say yes or no to at the end of this session that they couldn't before it started?"*

**What the narrative brief looks like for Workshop Design:** Replace per-slide governing thought / so-what / editorial emphasis fields with:

```markdown
### Session: [Session name] — [duration]

**Objective:** [One action sentence: "Align on...", "Decide...", "Prioritize..."]
**Owner:** [Facilitator or lead]
**Desired output:** [What participants leave this session with — a decision, a ranked list, a draft, etc.]
**Key inputs:** [What needs to be in the room: data, pre-work output, prior decision]
**Slide type:** [Agenda entry | Context framing | Working exercise | Capture/synthesis | Closing]
```
