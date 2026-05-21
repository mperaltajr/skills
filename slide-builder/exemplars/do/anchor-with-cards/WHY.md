# anchor-with-cards

**What this is.** A two-zone layout for "anchor + supporting forces" slides: a tall left BRAND_PRIMARY panel carries the reframe, and a right column stacks three numbered evidence rows.

**What makes it strong.**
- **Left anchor panel asserts dominance.** ~38% canvas width, BRAND_PRIMARY fill, runs nearly full body height (156→640). The hero takeaway in 24px bold WHITE reads as the slide's conclusion before the eye gets to the supporting rows.
- **One accent moment, load-bearing.** A 4px BRAND_ACCENT vertical rule on the right edge of the dark panel — it visually marks the seam where the conclusion meets the evidence. No other BRAND_ACCENT anywhere on the slide.
- **Right side stays neutral.** Three numbered rows separated by 1px CARD_BORDER dividers (NOT accent). Numerals are BRAND_PRIMARY but non-bold — weight comes from 36px size. Labels are 18px bold TEXT_DARK; bodies are 14px TEXT_MID non-bold (`designer-brief § 6` bold discipline: title + anchor takeaway + 3 row labels = 5 bold ceiling).
- **Title bottom-anchored at y≈100** via `add_title_block(title=..., subtitle=...)` with inline `<strong>` tint on the operative phrase.
- **Invariant zones clean.** Only `add_footer(slide, page_num=N)` in the bottom; no DRAFT/CONFIDENTIAL/client tags.

**Reach for this when.** The slide has ONE conclusion and 2-4 supporting forces. The conclusion deserves panel-scale weight; the supporting forces should read as parallel, equal-weight evidence rather than competing arguments.

**Patterns to copy.** Panel width arithmetic (`(1280 - 128) * 0.38`); the WHITE-on-BRAND_PRIMARY 24px takeaway + BRAND_ACCENT_SOFT italic tagline pairing; numeral-as-rhythm pattern (big size + BRAND_PRIMARY, no bold).
