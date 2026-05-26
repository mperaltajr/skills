# placeholder-as-content

## Page-type family
Chart + right takeaway panel (a `chart-right-takeaway` variant).

## Failure in one line
Every text slot still says its own slot label. The slide shipped its template comments as content.

## Rule violated
Every text slot must carry a CLAIM, not its own slot label. The action title must state the action. The takeaway panel must state the takeaway. Bullets must list evidence, not announce that bullets exist. (See Hardline #2 in `slide-builder/SKILL.md` — "no fabrication" — and `reference/anti-patterns.md` for the canonical entry.)

Compounding failures (kept in so the anti-exemplar is recognisable as a real Slide Lab "before" slide, not a strawman):

1. **"Action Title" is the title.** Not a so-what. The strongest single slot on the page is wasted on the slot's name.
2. **"Sub-headline" is the sub-headline.** Same disease.
3. **"Takeaway / Insight Panel" is the panel header.** A panel labelled "the panel where the takeaway goes" is not a takeaway.
4. **"Concise text on so what. Explains takeaway."** is the so-what. The author wrote about writing the so-what.
5. **"Bullet point – text description"** appears three times as the bullet text.
6. **Axis labels are swapped.** "X Axis Title" sits on the Y axis (vertical, left). "Y-Axis Title" sits on the X axis (bottom). When labels are treated as decoration nobody notices they lie.
7. **DRAFT tag in the top invariant zone.** Violates MEMORY → invariant-zone-chrome rule (top zone holds content, not status flags).
8. **Off-brand mint chart panel + cool-grey takeaway panel.** Decorative panels announce themselves as "the chart area" and "the panel area" — they don't disappear into the page, so the content has to fight the chrome.

## Why it's a teaching anti-exemplar
This is the failure that hides best. The slide passes a thumbnail glance, passes a "is the hierarchy right?" check (title is biggest, subtitle smaller, body smaller still), passes a "is the palette on-brand?" check at arm's length. It fails the only check that matters — "does this slide say anything?"

It is also the most common real-world Slide Lab failure: a consultant duplicates a template slide, fills two of the eight slots, and ships the rest as-is because they're busy. The reviewer's job is to recognise this on sight.

## What to do instead
Take the same layout, but apply these corrections:

- The action title states the action: `[Action title: state the so-what]`
- Numbers are bracketed placeholders that **cannot** be confused for content: `[$X.XM]`, `[N%]`, `[Workstream A]`
- The panel header is the takeaway in one line, not a label saying "takeaway goes here"
- Bullets carry evidence pairs: `[bucket A] — [supporting evidence]`
- Axis labels match the axis they sit on
- No DRAFT tag in the top zone — status belongs in PowerPoint comments or slide notes, not on the canvas
- One panel uses card-bg, not a competing fill; chart area is unframed and breathes
