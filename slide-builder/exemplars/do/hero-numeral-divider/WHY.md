# hero-numeral-divider — WHY

## Page-type
**Cover/Divider — numbered section divider (light variant).**

A wayfinding slide that marks the boundary between deck sections. The hero
numeral is a chapter index ("you are entering section 02"), not a measured
quantity. The slide carries no body content, no claim prose, no chart, no
footer — just the section number, the section name, two framing hairlines,
and a single accent mark.

## When to use it
- **Section breaks between body slides** in a deck with numbered structure
  (e.g., "01 Context / 02 Findings / 03 Recommendations").
- **Chapter openers** at the start of each major narrative beat — gives the
  audience a beat to reset before the next argument begins.
- **Appendix dividers** when the appendix has multiple labeled sub-sections.
- **Light-canvas alternative** to the dark-backdrop divider (e.g.,
  `divider-numbered-dark`). Pick this one when:
  - The body slides around it are light-canvas and a dark divider would feel
    like a tonal whiplash.
  - The deck's brand palette uses BRAND_PRIMARY heavily as ink (not
    background) and a dark divider would over-emphasize the brand chrome.
  - The client template defaults to white slides and dark dividers read as
    off-brand.

## Structural distinctness vs. hero-kpi-tile
`hero-kpi-tile` is a BODY page-type — it names a single metric, supports it
with a horizontal bar strip, and includes a claim paragraph + footer + page
number. The hero numeral there is a **measured quantity** (a dollar amount,
a percentage). This divider has no chart, no claim prose, no footer, no
supporting evidence — and the numeral is a **section index**, not a metric.
Different page-type, different content model, different invariant
treatment. NET-NEW.

## Distinctness vs. existing `_staging/cover-divider/section-divider-number`
That staging candidate **inverts** the composition (numeral LEFT, title
RIGHT) and uses a dark bottom strip as its chrome event. This file is the
cleaner light/right-numeral version called for by the skeleton — no dark
strip, two hairlines instead, accent reduced to a single 64px mark on the
bottom rule.

## Anti-patterns (do NOT use this slide when…)
- The "number" is a real metric (revenue, count, percentage). That is a
  BODY page-type — use `hero-kpi-tile` or a hero-stat layout, with a
  supporting chart or claim.
- The deck has no numbered section structure. A standalone "02" with no
  preceding "01" or following "03" reads as a typo, not wayfinding.
- The section name is longer than ~3 words. Past ~24 characters at 36px
  the title wraps and the baseline alignment with the numeral breaks.
  Either tighten the section name or move to a divider that gives the
  title two lines (e.g., `divider-two-col`).
- You need to preview what's IN the section (objectives, agenda, three
  bullets). That is a richer page-type — use `divider-agenda-preview` or
  `divider-objective`. This slide is intentionally empty as a beat.
- The deck only has one section. Dividers are inherently comparative —
  one of them alone is meaningless.

## Bold count
**2** — hero numeral + section title. Eyebrow is uppercase+letter-spaced
(not bold). No claim prose, no body text, no footer.

## Accent moment
**1** — the 64px BRAND_ACCENT mark on the bottom hairline directly under
the section title. Everything else is BRAND_PRIMARY ink on white, with
1px CARD_BORDER hairlines as neutral structure.
