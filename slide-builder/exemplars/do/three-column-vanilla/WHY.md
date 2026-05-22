# three-column-vanilla

**Page type.** Three-column parallel (vanilla / no-icon variant).

**What this is.** Three vertical tinted cards (CARD_BG fill, CARD_BORDER outline) laid out as parallel pillars. Each card opens with a small uppercase eyebrow, then a BRAND_PRIMARY bold column heading, then left-aligned body copy. No icons, no circles. One accent moment: a 3px BRAND_ACCENT top-edge stripe on the single load-bearing column.

**Differentiator vs `3pillar-icon-circles`.**
- `3pillar-icon-circles` opens each card with an 88px BRAND_PRIMARY circle + WHITE glyph. The icon is the visual anchor; the heading sits below at 18px center-aligned.
- `three-column-vanilla` has no icon at all. The 20px BRAND_PRIMARY bold heading IS the anchor. Layout is left-aligned (editorial), not center-aligned (poster-like).
- These produce different reads: icon-circles feels like a product/method poster; vanilla feels like a strategy memo.

**Reach for this when.**
- Content is **text-heavy** — each pillar carries 2-3 sentences of substance and an icon would compete with the heading rather than support it.
- The **client template has no icon precedent** — dropping a glyph in would feel imported. Vanilla typography reads as native to any corporate template.
- The pillars are **objectives, priorities, or workstreams** where the column heading does most of the meaning-carrying work (KPIs, targets, owners can live in the body).
- You want a **calmer, more editorial** three-column read than the icon-led variant.

**Reach for `3pillar-icon-circles` instead when.**
- Content is short / poster-like — each pillar is one sentence and the visual anchor matters more than the prose.
- The pillars are **method stages, product branches, or named phases** where a glyph genuinely helps recognition (e.g., Think / Argue / Build → lightbulb / speech / package).

**Structure rationale.**
- **One accent moment = top-edge stripe on column 1 (load-bearing).** `add_title_block` no longer auto-emits a brand-rule, so the accent is free to live on the column that carries the takeaway. The other two columns are neutral CARD_BORDER outlines — never paint accent on all three columns (kills the "one accent moment" rule and fragments the parallel read).
- **Bold count = 4.** Title + three column headings. Eyebrows uppercase letter-spaced NOT bold; body NOT bold. Under the ≤5 ceiling.
- **20px column headings (vs 18px in icon variant).** With no icon competing for visual weight at the top of the card, the heading can run slightly larger and own the card on its own.
- **Left-aligned body** (vs center-aligned in icon variant). Editorial vertical rhythm — eye drops down the left edge of each card the way a memo reads. Center-alignment is reserved for poster-like icon-led variants.
- **Card geometry.** `body_left=64, gap=24, card_w=368, card_top=178, card_h=440`. Identical to the icon variant so the two exemplars are visually swappable in a deck.

**Anti-patterns (what NOT to do).**
- Do NOT paint the accent stripe on all three columns. That breaks "one accent moment" and equalizes columns that should not be equal — pick the load-bearing one.
- Do NOT add an icon "just to fill space" at the top of each card. If the brief truly needs icons, switch to `3pillar-icon-circles` instead of bolting glyphs onto this layout.
- Do NOT use BRAND_ACCENT or BRAND_ACCENT_SOFT for the card fill or the column-heading color. Card fill is CARD_BG (tinted white); heading color is BRAND_PRIMARY. Accent stays on the stripe only.
- Do NOT center-align the body. The whole point of the vanilla variant is editorial left-aligned readability — center-alignment defeats it.
- Do NOT use gray for the body. TEXT_MID / TEXT_FAINT are aliased to TEXT_DARK on purpose — hierarchy is size + weight + italic, not gray gradients.
- Do NOT re-introduce a brand-rule under the subtitle. `add_title_block` no longer emits one; if you draw one manually you double-spend the accent moment.

**Patterns to copy.**
- The card geometry constants (`body_left`, `gap`, `card_w`, `card_top`, `card_h`) — share these with `3pillar-icon-circles` so the two layouts feel like siblings.
- The eyebrow → heading → body 3-line vertical rhythm with left-alignment.
- The `accent_col_idx` pattern — single integer naming the load-bearing column, drawn AFTER the card rectangle so the stripe paints over the top border edge.
