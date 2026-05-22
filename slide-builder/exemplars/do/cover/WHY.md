# cover-band-footer

**Page-type.** Cover / Divider (third variant).

**What this is.** Full-bleed BRAND_PRIMARY canvas with a distinct dark footer band running across the bottom. Hero title sits lower than the other two cover variants (~60% canvas height), with subtitle and a single byline line (client . date) stacking directly underneath. The footer strip is a quiet base - it carries ONLY source / footnote, never branding tags.

**When to use this vs. the other two cover variants.**

| Variant | Reach for it when... |
|---|---|
| `cover-fullbleed-dark` | The title carries the entire emotional weight and the deck has an editorial register (tagline + three "Think / Argue / Build"-style definition rows reinforce the brand promise). Conference / point-of-view / internal-launch covers. |
| `dark-hero-foil` | The cover ALSO needs to list scope, audience, prepared-by, and date as visible meta - the 35/65 asymmetric split gives the right panel room to spell that out without competing with the title. Working-session / steering-committee covers. |
| `cover-band-footer` (this one) | A **nameplate** cover. Conventional client-deliverable opening: title, one subtitle line, "Client . Date" byline, and that's it. No supporting rows, no scope columns. The footer band gives the eye a stable visual base and reserves the invariant zone for source / footnote. Most external client decks where the cover should be quiet, not editorial. |

**What makes it work.**
- **Footer band on BRAND_PRIMARY_MID** (not raw BRAND_ACCENT). The band is a structural element, not an accent - keeping it on a mid-purple tone separates it from the canvas without spending the slide's one accent moment.
- **Title bottom-anchored at y_px=300, h_px=120.** Lower than the other cover variants because subtitle + byline stack BELOW the title, not above. The bottom edge of the title block lands at y=420, which leaves a clean 18px gap to the accent rule.
- **One accent moment.** A single 64px x 4px BRAND_ACCENT rule between the title and the subtitle. Everything else is BRAND_PRIMARY ground, BRAND_PRIMARY_MID band, WHITE title/byline, or BRAND_ACCENT_SOFT subtitle/footer copy.
- **Bold discipline = 1.** Only the hero title is bold.
- **Invariant zone hygiene.** The footer band carries ONLY footnote + source. No "ACCENTURE", no "DRAFT", no "CONFIDENTIAL", no page number (cover/divider doesn't require one).
- **Direct `add_text` for the hero** - covers bypass `add_title_block` because the hero scale (44px) and color treatment (WHITE on dark) don't fit the standard 28/16 title-block contract.

**Anti-patterns.**
- Adding an eyebrow above the title. That converts this into a different slide (closer to `cover-fullbleed-dark`). If you need an eyebrow, use that variant instead.
- Stacking three definition rows below the byline. Same - use `cover-fullbleed-dark`.
- Putting "ACCENTURE" or "DRAFT" in the footer band. The invariant zone is reserved for source / footnote / (optional) page number ONLY.
- Using BRAND_ACCENT for the footer band fill. That spends the slide's only accent moment on a structural element and leaves nothing for the rule under the title.
- Raising the title to 60px+. The 60-96px range is reserved for single-numeral hero slides, not multi-word client titles.
- Raw WHITE for the subtitle. Subordinate copy on a dark ground should be BRAND_ACCENT_SOFT so it sits visually below the title; raw WHITE competes.
