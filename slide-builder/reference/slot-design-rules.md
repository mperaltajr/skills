# Slot design rules — Tier 1 (Pattern Library composer)

The Tier 1 counterpart to `phase-a-rules.md`. Patterns are pre-designed canvases; this file is the rulebook for filling them with content so the result is a designed slide and not text dumped into slots.

**You must read this file before producing a slot-reasoning block. The composer refuses to build without that block.**

---

## Why this file exists

A pattern's slots have design roles, not just shapes. `panel-1-heading` is sized for a claim; `panel-1-body` is bulleted, not paragraphed; `convergence` is the slide's punchline. Pasting prose from the brief into every slot ignores those roles and produces template-shaped text dumps. Past failure: a 3-bullet recovery story shipped as one prose paragraph crammed into a body slot, with the load-bearing number ($7.5M) buried mid-sentence instead of elevated. The pattern looked broken; the patterns were fine. The fill was wrong.

---

## Slot roles and what belongs in each

| Slot family | Typical font | Belongs here | Does NOT belong here |
|---|---|---|---|
| `title` / `action-title` | 24–28pt bold | The slide's governing thought, one sentence | A topic noun ("Q3 update") |
| `subtitle` / `subhead` | 16pt (~21px) italic | One supporting sentence | A second governing thought |
| `eyebrow` | 11pt small-caps | Section label or category | A claim |
| `card-N-num` / `metric-N-value` | 40–60pt bold | A single number, the hero stat | A sentence, a unit, or two numbers |
| `card-N-heading` / `panel-N-heading` | 18–22pt bold | A claim or short title (≤6 words) | A bullet list, a paragraph |
| `card-N-body` / `panel-N-body` | 12pt (16px) | 2–4 short bulleted lines | A prose paragraph |
| `panel-N-label` | 10–12pt small-caps | Category tag ("LEVER 1") | A sentence |
| `convergence` | 14–16pt | The slide's punchline; one sentence | Multi-paragraph content |
| `source` / `footnote` / `page-number` | 8pt | Citation, footnote, slide number | Body content |

---

## Content transformation — required before writing overrides

Before any override is written, the brief's prose for that slide must be reshaped into the slot's expected form. Specifically:

1. **Find the hero number.** Per slide there is usually one load-bearing number. Elevate it to the hero slot (`card-N-num`, `metric-N-value`) at hero size. Do not bury it in a body sentence.
2. **Split prose into bullets.** Any body slot designed for bullets gets bullet characters (`•`) and newlines. A 3-fact paragraph becomes 3 bullet lines, never 1 prose run.
3. **Pull category labels out of the prose.** "Lever 1: field HR ratio" — "Lever 1" goes into the label slot, "Field HR ratio" goes into the heading slot.
4. **Strip filler clauses.** "Adopt the ACN-recommended ratio of 1 field HR per 800–1000 employee FTEs vs. current 1:1000" → "Adopt ACN ratio (vs. current 1:1000)". The pattern's typography carries the formality; the text doesn't need to.
5. **Move numbers to where the eye lands.** Recovery $, deltas, hero stats belong in slots that are visually elevated. Supporting context belongs in body slots.

---

## Accent discipline — one moment per slide

Each slide has **exactly one accent moment**: the single element the audience's eye should hit first. It's the load-bearing number, the punchline word, or the ask. Treatment options:

- Bold + brand accent color (orange, on light backgrounds)
- Bold + white (on dark/colored panels)
- Larger size than its neighbors

Rules:

- One accent moment per slide. Two competes with itself.
- The accent moment is named in the slot-reasoning block (see below).
- Don't accent every number — only the one that does the work for this slide.

---

## Chrome consistency

`source`, `footnote*`, `footer-*`, `page-number` shapes must all render at **8pt** across every slide in the deck. The composer's `normalize_chrome` flag (default on) enforces this — do not override it without a reason.

---

## Per-shape typography is explicit, not inherited

Every text shape that carries content for the deck's argument must have its font size set explicitly via `translator.py` or in the override spec. Pattern defaults are starting points, not finished design. If a slot's default size is wrong for the content (hero number rendered at 22pt because it landed in the heading slot, not the num slot), bump it.

---

## The slot-reasoning block — required output before any compose call

For each slide in the deck spec, the model must produce a slot-reasoning block before the composer will run. Save it to `_session/slot-reasoning-NN.md` where NN is the slide index. Required format:

```
# Slot reasoning — Slide N
Pattern: NN_pattern-name

## Slot fills
- panel-1-label: LABEL ZONE (10–12pt small-caps). Brief role: lever category. Override: "LEVER 1"
- panel-1-heading: CLAIM ZONE (22pt). Brief role: lever's titled claim. Override: "Field HR ratio · 1:800–1000"
- panel-1-body: BULLET ZONE (14pt × 2–4 bullets). Brief role: evidence for the claim. Override: 3 bullets — adopt ACN ratio; FTE delta; recovery number
- convergence: PUNCHLINE ZONE (14–16pt). Brief role: combined recovery + ask. Override: combined recovery sentence + "Greenlight both levers."

## Accent moment
$18.5M (in convergence) — bold + brand accent. Why: the recovery total is what the room must decide on.

## Content transformations applied
- panel-1-body: prose paragraph from brief split into 3 bullets; recovery number ($7.5M) moved from mid-sentence to last bullet and bolded.
- panel-2-body: same transformation, mirrored.
```

If a slot's brief content doesn't fit any slot role, either reshape the content or pick a different pattern. Don't paste prose into a slot designed for something else — that is the failure mode this file exists to prevent.

---

## What this file does NOT cover

- HTML authoring from scratch — see `phase-a-rules.md`
- Pattern selection criteria — see `SKILL.md` § "Pattern Library Match"
- Chart generation — see `SKILL.md` § "Chart generation"
- Visual treatment recipes — see `visual-treatment-library.md`
