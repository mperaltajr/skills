# single-finding

**What this is.** One bold conclusion dominates the top half; three parallel supporting bullets sit clearly subordinate below. The slide reads as "here is the finding — these three points support it."

**What makes it strong.**
- **Hero takeaway at 36px bold TEXT_DARK** occupies the top of the body zone (y≈168). 70-78% canvas width — wide enough to look like a statement, not narrow enough to feel like a column header. Inline `<strong>` with `emphasis_color=BRAND_PRIMARY` tints the operative phrase (here: "thought partner").
- **One accent moment.** A 56px x 4px BRAND_ACCENT rule directly under the hero takeaway. The bullet markers below are BRAND_PRIMARY squares — NOT accent — so the rule remains the sole accent.
- **Bullets are visibly subordinate.** 14px TEXT_MID, NEVER bold (per the updated `designer-brief § 6` rule: body never bold). Each prefixed by a 12px BRAND_PRIMARY square (the only "graphic" device on the row — minimal).
- **Bold ceiling honored.** Title (1) + hero-claim inline emphasis (1) + 0 bold bullets = 2 bold text runs. The bullet squares are visual emphasis, not bold text.
- **Hero supporting claim at 16px TEXT_MID** sits below the accent rule, restating the so-what at a smaller scale before the eye drops to the bullets.

**Reach for this when.** The slide has ONE strong reframe or finding and 2-4 short supporting points. Editorial emphasis is "conclusion dominates" or "one finding, parallel evidence."

**Patterns to copy.** Hero takeaway with inline `<strong>` + `emphasis_color`; the small BRAND_PRIMARY-square bullet pattern (NEVER use bullet characters or • glyphs — always small `add_rect` markers); subordinate body at 14-16px so it can't compete with the 36px hero.
