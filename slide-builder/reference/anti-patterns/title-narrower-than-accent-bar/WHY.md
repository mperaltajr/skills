# title-narrower-than-accent-bar — WHY NOT

**Page-type family:** any (chrome-level failure — can occur on any page type)
**Verdict:** dont

## The problem

The title text is a short phrase ("[Short title]") whose rendered width is far narrower than the full-bleed `BRAND_ACCENT` bar drawn directly beneath it. The bar spans the full body content width (1152px); the title text spans maybe 120–180px. The accent bar dominates the title.

Visual hierarchy is inverted:
- The eye lands on the heavy purple bar first — it reads as the primary visual element.
- The title text reads as a small footnote sitting on top of an accent block, not as the page's headline.
- An ornament is out-shouting the load-bearing text.

## Rule violated

**Title text width must dominate any accent bar/rule placed underneath it.** Never let the accent bar exceed the title's visual width.

The default helper accent rule (≤64px) is sized this way on purpose: a short tick mark anchors the title without competing with it. Agents who replace the default with a wider custom band must first check the title's rendered width — and shrink the bar to match (or place the accent elsewhere).

## Why this is a teaching anti-exemplar

When an agent decides to draw its own accent bar under the title — usually to "make the page feel more designed" — and uses a generous width (full body, or 800px+) without checking the title text, it produces this exact inversion. The agent thinks it's adding emphasis to the title; it's actually overpowering the title.

This failure is invisible until you look at the slide as a whole: each element in isolation seems fine. It only breaks under the relational rule "title must dominate its own underline."

## What to do instead

- **Keep the accent bar ≤ title text width.** A 48–64px tick under a short title is the safe default. If the title is long, the bar can grow — but only up to the title's rendered width.
- **If you want a wider accent moment, put it on a different element.** A card border on the right column. A stripe down the side of a chart. A BRAND_ACCENT fill on a recommendation band at the bottom of the slide. Anywhere that isn't directly under a short title.
- **Spend the accent moment on the load-bearing element, not on chrome.** The accent's job is to mark where the takeaway lives — a highlight on the hero number, a callout on the key bullet — not to underline the title for decoration.
