# midpoint-accent-splits-slide — WHY NOT

**Page-type family:** any (chrome-level failure — page-type independent)
**Verdict:** dont

## The problem

A full-width BRAND_ACCENT bar (1152px × 6px) is parked at y≈336 — roughly the visual midpoint of the body area, halfway between the title block (bottom y≈134) and the bottom of the body content (y≈560).

That bar is not attached to anything. It floats in whitespace. The eye reads it as a page break, and the slide collapses into two stacked half-pages:

1. **Upper half** (title + subtitle + hero takeaway + supporting line) reads as a complete slide whose chunky bottom rule terminates the composition.
2. **Lower half** (three supporting cards) reads as a separate slide whose page header is the accent bar.

One coherent slide becomes two competing pages. The hero takeaway and the cards that should expand on it are visually severed.

**Rules it breaks:**
- **Accent discipline:** one accent moment per slide, and the accent must ATTACH to a load-bearing element — the title block, a card edge, a chart row, a column cap. A full-width accent floating in body whitespace is not "one accent moment", it's a false page break. (See `reference/anti-patterns.md` — accent-discipline entries.)
- **Divider misuse:** full-width horizontal rules are reserved for between-section dividers in dense decks. Inside a single body composition they sabotage reading order. (See `reference/layouts.md` § "Horizontal bands" for the legitimate use.)

## Why this is a teaching anti-exemplar

Agents sometimes plant their own "decorative" full-width bars to fill perceived empty space — especially in layouts where the title block already has its own brand-rule and the body has visual gaps the agent reads as "needs something here". The fix is almost never adding more chrome; it's either tightening the body composition or attaching the accent to a real element.

This anti-exemplar is structurally clean otherwise (proper title block, footer, hero takeaway, three cards) — the ONLY failure is the misplaced bar. That isolates the lesson: same content, same chrome, same palette — just the accent in the wrong place — and the slide breaks.

## What to do instead

Pick one of these placements for any accent bar:

- **Directly under the title block (y ≤ 140).** The accent reads as a title-block underline. `add_title_block` already does this — do not add a second rule.
- **On a load-bearing body element.** Left edge of a card (4–6px vertical stripe), top stripe of a column, cap above a chart row, callout pill on a specific bar in an evidence stack. The accent is attached to specific content.
- **As the lone hero accent under a hero takeaway.** A short rule (≤ 64px wide), tied tight to the hero text below it — never full-width.

**Forbidden:** any full-width (>500px) accent rectangle in the body-area midpoint zone (roughly y=200 → y=500) that is not visually attached to a specific element. That position will always split the slide.

If the body feels visually empty, fix the composition (larger hero text, tighter card spacing, more decisive cards) — do not add a midpoint bar.
