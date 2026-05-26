# vertical-rule-no-gutter — WHY NOT

**Family:** any (chrome-level failure)
**Verdict:** dont

## The problem

A vertical BRAND_ACCENT rule runs top-to-bottom of the body zone. Three numbered items (1. 2. 3.) sit immediately to its right with **zero horizontal padding**. The numerals butt directly against the rule.

The visual result: the line reads as **cutting into the content**, not framing it. The "1." looks like it's been sliced by the rule. The rule competes with the numbers for the same horizontal pixels instead of marking a boundary between two zones.

Vertical chrome only works when there is clean negative space between the chrome and the content it borders. Without that gutter, the rule stops being a frame and starts being noise that collides with the numerals.

**Rule violated:** vertical accent rules require **≥16px horizontal gutter** between the rule and any adjacent text or numerals. The rule and the content must not touch.

## Why this is a teaching anti-exemplar

This is a chrome failure, not a content failure. The numbers are fine. The rule is fine. The placement is what breaks the slide — and it's the kind of mistake that happens when a layout is assembled by stacking elements at their bounding-box edges instead of reasoning about negative space.

It teaches:

- Vertical chrome is a separator, not a baseline. Content cannot start at the chrome's right edge.
- The smaller the rule (4–6px), the easier it is to forget about its gutter. A thicker rule visually demands the gutter; a thin one looks like it should be safe to butt against, but it isn't.
- Numerals and uppercase glyphs are the most sensitive to this — their straight left edges align too closely with the rule, amplifying the collision.

## What to do instead

Three working options, in order of preference:

1. **Add the gutter.** Shift content right by ≥16px. The rule sits at x=64; content starts at x≥80. This is the default fix.
2. **Narrow the rule.** If horizontal space is tight (e.g., a content-dense body zone), drop the rule from 4–6px to 2–3px and keep ≥12px gutter. A hairline rule reads as a boundary even with less breathing room.
3. **Move the rule.** If the rule is decorative rather than structural, move it to the left edge of a panel (where the panel's internal padding gives you the gutter for free), or drop it entirely.

The rule and the content shouldn't touch. Ever.
