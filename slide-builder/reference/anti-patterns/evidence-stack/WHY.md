# evidence-stack — WHY NOT

**Family:** Insight / Finding  
**Verdict:** dont

## The problem

The finding-hero text block + its BRAND_ACCENT accent rule creates a second "section start" zone directly below the title block. The slide now has two elements that both read as page openers:

1. The `add_title_block` title + subtitle + brand-rule at y≈20–134 (the real title zone)
2. The finding-hero text + a second BRAND_ACCENT rule at y≈156–222 (looks like another title zone)

The result: the slide reads as two separate pages stacked — the top looks like its own page header, the body content below looks like a separate slide. The accent bar divides instead of anchoring.

**Rule it breaks:** one accent moment per slide. This layout uses BRAND_ACCENT twice (title block rule + finding-hero rule) and creates competing visual entry points.

## What to do instead

If the finding needs a large restatement below the title, use a single large text block at body level — no second accent bar. The accent moment is already consumed by the title block's brand-rule. Any secondary callout element must use BRAND_PRIMARY or TEXT_MID, not BRAND_ACCENT.

Alternative structure: remove the finding-hero text entirely and let the title carry the full insight claim. The evidence bars speak for themselves.
