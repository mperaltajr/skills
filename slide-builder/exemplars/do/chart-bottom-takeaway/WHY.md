# chart-bottom-takeaway

**What this is.** The canonical chart-slide pattern with a full-width BRAND_PRIMARY takeaway band running across the bottom. Grouped multi-series bars above; the slide's so-what asserted in italic WHITE below.

**What makes it strong.**
- **Action title states the so-what, not the topic.** "APAC overtakes NA by Q4 — the engine of FY26 growth." NOT "Quarterly revenue by region." The chart subtitle (11px uppercase TEXT_MID eyebrow) carries the topic.
- **Four-element chart header.** (1) action title, (2) italic sub-headline + brand-rule, (3) right-aligned 3-chip legend below the brand-rule, (4) chart subtitle eyebrow above the chart. Reader's eye flows title → sub-headline → legend → subtitle → chart without doing any encoding work.
- **One accent moment = the callout pill.** A 130×32 BRAND_ACCENT pill anchored upper-right of the chart with a 2px BRAND_ACCENT leader line dropping toward the Q4 APAC bar (the load-bearing data point the title claims about). All three data series use neutral / brand-family colors (TEXT_MID, BRAND_PRIMARY_MID, BRAND_PRIMARY). Bars themselves are NEVER BRAND_ACCENT.
- **Direct-labeled value labels.** Only the APAC series gets value labels above its bars ($M figures) — direct-labeling the story series, not all three. The other two series read off the legend.
- **Bottom takeaway band.** 48h BRAND_PRIMARY rectangle spanning the full body width (1152w), carrying a 14px WHITE italic sentence — the so-what restated as the parting line. `anchor="middle", align="center"` for vertical and horizontal centering.
- **Faint y-axis baseline only.** 1px CARD_BORDER zero line; no gridlines, no y-axis ticks, no chartjunk.

**Reach for this when.** Multi-series chart (2-4 series, 3-6 groups) where the takeaway is one sentence and benefits from full-width emphasis. The bottom band gives the slide a strong terminal beat.

**Patterns to copy.** The 4-element chart header (title / sub-headline / legend / subtitle); right-aligned legend built right-to-left so the rightmost chip's right edge lands exactly on the canvas right margin; callout pill + leader line as the single accent; direct-label only the story series; full-width takeaway band as the closing beat.
