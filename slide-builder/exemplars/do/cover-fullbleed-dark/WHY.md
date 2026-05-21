# cover-fullbleed-dark

**What this is.** The canonical Slide Lab cover: full-bleed BRAND_PRIMARY canvas, typography is the visual, single accent moment carries the entire slide.

**What makes it strong.**
- **Full-bleed brand fill.** A single `add_rect(0, 0, 1280, 720, BRAND_PRIMARY)` paints the entire canvas. No white margins, no chrome competing with the title.
- **Hero title at editorial scale.** 48px bold WHITE — capped per `page-types.md § Cover/Divider` (36-48px for multi-word titles; 60-96px reserved for single-numeral hero slides). Bottom-anchored inside a 100h box so descenders sit on a stable baseline.
- **One accent moment.** A single 64px x 4px BRAND_ACCENT rule under the tagline. That is the only BRAND_ACCENT on the slide — everything else is BRAND_PRIMARY ground, WHITE type, or BRAND_ACCENT_SOFT (tagline + meta labels).
- **Bold discipline = 1.** Only the hero title is bold. Eyebrow + tagline + body + meta all rely on size, italic, or letter-spacing for emphasis (`slot-design-rules.md § Bold discipline`).
- **No footer.** Cover/divider page-types do not require page numbers; the meta block sits ABOVE the bottom invariant zone at y=628, not in it.

**Reach for this when.** Any deck cover or major-section divider where the title carries the entire emotional weight. Anything where the audience should pause on the words before turning the page.

**Patterns to copy.** Full-bleed fill technique; `anchor="bottom"` on the hero title; eyebrow with `uppercase=True, letter_spacing_px=2, bold=False`; BRAND_ACCENT_SOFT for ALL subordinate type on the dark ground (never raw WHITE for subordinate copy — it competes with the title).
