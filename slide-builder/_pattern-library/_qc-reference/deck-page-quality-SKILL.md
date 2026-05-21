---
name: deck-page-quality
description: Use this skill whenever the user asks to audit, check, review, or quality-control the visual execution, formatting, rendering, or hygiene of a slide deck — any deck type, any audience. Trigger phrases include "check this deck for errors", "QA this slide deck", "is this deck clean", "review the formatting", "find typos and overlaps", "polish check", or when a deck is uploaded with a request for execution-quality feedback rather than substantive argument review. This skill evaluates whether whatever is on each page is rendered correctly and consistently — layout, typography, overlap, color, charts, tables, language mechanics, grammar, page-to-page consistency, and file hygiene. It is context-independent and applies to all deck types. It does NOT evaluate whether the argument is right, whether titles say the right thing, or whether the recommendation is sound — those questions belong to a separate storyline-review skill.
---

# Deck Page Quality Skill

## Purpose

Audit a slide deck for execution-quality defects — the items a senior partner or sharp client would notice and penalize regardless of whether the underlying argument is strong.

This skill answers: *"Is whatever is on the page rendered correctly?"*

It does not answer: *"Is this the right thing to say?"* — that question belongs to a separate, context-aware storyline evaluation.

## Scope — what this skill owns

| The skill evaluates | The skill does NOT evaluate |
|---|---|
| Whether title *formatting* is consistent across pages | Whether titles say the right *thing* (action titles) |
| Whether callout boxes are visually placed correctly | Whether the page has a clear takeaway to call out |
| Whether layouts are clean enough to read | Whether the page makes the right point |
| Bullet structure: parallelism, punctuation, length | Whether the bullets are the right bullets |
| Axes labeled, units present, legend readable | Whether the chart is the right chart to prove the point |
| Grammar, typos, hedging words, acronym expansion | Whether the language is decision-forcing |
| Layouts, footers, page numbers consistent across pages | Whether the argument holds across pages |

The rule: this skill owns *rendering* questions. Substance questions are out of scope.

## When to run this skill

- Before any deck leaves a team — internal hygiene pass.
- After every significant edit — defects re-introduce easily.
- Before a partner or client review — the catch-it-first pass.
- On any deck type — pitch, board, RFP, training, town hall, marketing. The rules don't change by audience.

## Inputs

1. **The deck file.** PPTX preferred (allows structural inspection); PDF acceptable for visual-only checks.
2. **Optional: the brand or template specification.** If the team has a defined palette, font set, or layout grid, the audit becomes a conformance check against that spec. Without it, the audit defaults to general MBB-grade conventions.
3. **Optional: the export format the deck will ship in.** PDF, printed, projected, embedded. Some defects only matter in specific formats (e.g., font substitution issues in PDF export).

This skill does *not* need the audience or the ask — those are storyline concerns.

## The audit categories

Twelve categories, each with specific check items. The agent walks every page through every applicable category and logs each violation with page number, category, and severity.

### 1. Layout & composition

- Visual hierarchy is clear — title, body, footnote sit at distinguishable weights.
- Each page has a single focal point.
- Margins are consistent across pages.
- Whitespace is intentional, not leftover.
- Elements align to a visible grid.
- Pages are balanced, not top-heavy or one-sided.

### 2. Overlap, overflow, collisions

- No text runs through any shape, line, or other text.
- No text box overflows its container; no clipped descenders.
- Titles wrapping unintentionally do not push downstream content out of place.
- Footnotes do not collide with body content above.
- Decorative lines or accents land where they should (not orphaned by a wrapped title).
- Icons fit cleanly inside containers.

### 3. Typography

- Font sizes consistent across pages of the same archetype.
- Sufficient size contrast between hierarchy levels (title ≥1.5× body).
- Body text legible — minimum 14pt for body, 10pt for footnotes.
- Line spacing consistent.
- No orphans (single word on last line) or widows (single line at top of column).
- Fonts consistent — no rogue substitutions from pasted content.
- Bold used sparingly, for emphasis only.
- Italic used for its purpose (citations, foreign terms, definitions), not for general emphasis.

### 4. Color & contrast

- Palette consistent with brand or template specification.
- Sufficient contrast for legibility (no light-on-light, no dark-on-dark).
- Color carries meaning consistently across pages (red always means the same thing).
- Color choices accessible to color-blind viewers — never red/green as the sole differentiator.
- Palette restrained — no more than 2–3 accent colors competing on one page.

### 5. Charts & data visualization

- Every axis labeled with a unit.
- Time period explicit on time-series charts.
- Decimal places consistent and appropriate within a chart.
- Chart type fits the data (no pie charts with eight slices; no line charts for categorical data).
- Gridlines help, not distract.
- Legend readable and well-placed.
- Visual annotation directs the eye to the takeaway (the takeaway itself is storyline's problem; the *presence* of an annotation is page-quality's).
- Axes truncated honestly — no zoomed Y-axis exaggerating small differences.
- Aspect ratio truthful — no squashed axes.
- Data labels not redundant with axis labels.

### 6. Tables

- Columns aligned by type — numbers right, text left, headers consistent.
- Number formats consistent within a column.
- Table density appropriate to the medium (a 47-row table on a projected slide is unreadable).
- Borders and shading help the eye, not distract.
- Totals clearly distinguished from data rows.

### 7. Icons, images, and graphics

- Icons from a consistent set (one style throughout — no mixing flat, outline, and emoji).
- Images high-resolution, no pixelation or JPEG artifacts.
- Stock photography avoided unless genuinely informative.
- Diagrams hand-built where they matter — no default SmartArt with default colors.
- Arrows consistent in weight, style, and direction.
- Every visual element serves a function — no decorative icons next to every bullet.

### 8. Language mechanics

- Tone appropriate to audience — neither over-casual nor falsely grand.
- Sentences active, not passive.
- Bullets parallel in structure (all noun phrases, or all verb phrases, or all sentences — not mixed).
- One idea per bullet — no semicolons stacking concepts.
- Bullets concise — typically under two lines.
- Hedging language minimized ("could potentially perhaps consider").
- Weasel words flagged when used without substantiation ("robust", "scalable", "best-in-class", "world-class", "seamless").
- Numbers written consistently (5% vs. five percent vs. 5 percent — pick one).
- Acronyms expanded on first use.
- Tense consistent across the deck.

### 9. Grammar, spelling, proofreading

- No typos. (One typo on a high-stakes deck is one too many.)
- Client name spelled correctly *everywhere*, not just on the cover.
- People's names spelled correctly and titles current.
- Dates current and consistent.
- Pronoun antecedents clear.
- Punctuation consistent in bullets (all end with periods, or none — not mixed).
- Capitalization consistent across the deck.
- Curly quotation marks and apostrophes used, not straight.
- Hyphens, en-dashes, and em-dashes used correctly and not interchangeably.

### 10. Page-to-page consistency

- All pages of the same archetype share the same layout.
- Title placement consistent across pages.
- Page numbers present and consistently formatted.
- Footers (confidentiality, client name, project) consistent and present where expected.
- Source citation format identical across all pages.
- Visual rhythm varies intentionally — not five identical layouts in a row, not five chaotic ones.

### 11. Animation, builds, transitions (when present)

- Each build adds information, not just delays it.
- Transitions are invisible, not theatrical.
- The deck still works when printed or PDF-exported flat.

### 12. File hygiene

- File name clear and dated — no "Final_final_v3_USE_THIS_ONE.pptx".
- Speaker notes either substantive or empty — no draft scratch, no internal snark.
- Tracked changes accepted and comments cleared before export.
- Linked objects embedded, not broken.
- Hidden slides actually hidden and not slipping into the export.
- PDF export renders identically to the PPTX — no font substitution, no chart shifts.
- No leftover placeholder content ("Lorem ipsum", "[Insert client logo]", "Subtitle goes here").

## Severity tiers

Each violation logged at one of three severities:

| Tier | Definition | Examples |
|---|---|---|
| **Critical** | Will embarrass the team in front of the audience; instant credibility loss | Misspelled client name, broken chart, leftover "[Insert logo]" placeholder, overflowing text on the recommendation page, wrong CFO title |
| **Major** | Visible to a senior reviewer; will be flagged and slow approval | Inconsistent footers, mixed icon styles, missing axis units, hedged language, broken page numbering |
| **Minor** | Cosmetic; reviewer may or may not notice; worth fixing for craft | Inconsistent decimal places within a chart, straight quotation marks, minor margin variance |

## Scoring

The score is a function of violation count weighted by severity. Default weights:

- Critical: −10 points each
- Major: −3 points each
- Minor: −0.5 points each

Starting from 100, the deck's page-quality score is `100 − weighted-violation-sum`, floored at 0.

## Verdict thresholds

- Any **Critical** violation present → **Do not ship; fix Criticals first**
- No Criticals, score 60–84 → **Ship after fixing all Majors**
- No Criticals, score 85–94 → **Ship after fixing Majors; Minors optional**
- No Criticals, score 95+ → **Ship-ready**

## Output format — one-screen view

```
DECK: [name]
PAGES AUDITED: N

PAGE QUALITY SCORE: NN / 100
VERDICT: [one of: Do not ship | Ship after fixing Majors | Ship after Majors, Minors optional | Ship-ready]

VIOLATIONS BY SEVERITY:
  Critical: N
  Major:    N
  Minor:    N

CRITICAL VIOLATIONS (all listed — must be fixed):
  - p2:  Client name misspelled in subtitle ("Acmme" → "Acme")
  - p7:  Chart axis overflows shape; bottom labels clipped
  - p14: Leftover placeholder text "[Insert recommendation here]"

MAJOR VIOLATIONS (top 5 shown; full list available on request):
  - p4:  Title is 28pt; same archetype on p5 uses 32pt
  - p6:  Y-axis labeled "Value" with no unit
  - p9:  Mixed icon styles — flat icons on left, outline icons on right
  - p11: Footer missing (present on every other page)
  - p13: Bullets mix sentence and fragment structures

MINOR VIOLATIONS: N total (full list available on request)

CATEGORY HOT SPOTS:
  - Typography: 7 violations (font sizes drift across pages)
  - Charts: 5 violations (axis labeling, units)
  - Consistency: 4 violations (footers, page numbers)
```

## Worked example

```
DECK: Q4 Strategy Readout — Final
PAGES AUDITED: 22

PAGE QUALITY SCORE: 67 / 100
VERDICT: Do not ship; fix Criticals first

VIOLATIONS BY SEVERITY:
  Critical: 2
  Major:    7
  Minor:    11

CRITICAL VIOLATIONS:
  - p1: Cover date is "Q4 2024" — deck is for Q4 2025 readout
  - p17: Text overflows the recommendation box on the closing page;
    last sentence cut off mid-word

MAJOR VIOLATIONS (top 5):
  - p3:  Title size inconsistent with same archetype on p4, p8
  - p6:  Chart axis labeled "Amount" — no unit (is this $M, $K, count?)
  - p10: Stock photo of generic businesspeople — adds no information
  - p12: Mixed icon styles within a single 2x2 framework
  - p15: Footer present on all pages except this one

MINOR VIOLATIONS: 11 total
  (mixed decimal places in chart on p7, straight quotation marks
  throughout, footnote font drift on p9, etc.)

CATEGORY HOT SPOTS:
  - Consistency: 6 violations — multiple drift points across pages
  - Typography: 5 violations — font sizing not locked to template
  - Charts: 3 violations — axis labeling and units
```

Note how the two Critical violations cap the verdict regardless of the otherwise-moderate score. A 67 with no Criticals would be a "ship after fixing Majors"; with Criticals present, the deck cannot ship until they're resolved.

## What this skill does NOT do

- It does not evaluate the argument, the storyline, or the substance.
- It does not rewrite the deck — it diagnoses defects.
- It does not enforce a specific design aesthetic unless a template spec is provided.
- It does not evaluate whether the *right* chart was chosen — only whether the chart present is rendered correctly.

## Checklist for the agent before declaring an audit complete

1. Every page walked through every applicable category.
2. Every violation logged with page number, category, and severity.
3. Criticals listed in full (never truncated).
4. Score computed from severity-weighted violation count.
5. Verdict matches the threshold table.
6. Category hot spots surfaced so the team sees patterns, not just instances.
7. Output fits the one-screen format.
