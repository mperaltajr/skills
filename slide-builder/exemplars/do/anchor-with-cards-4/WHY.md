# anchor-with-cards-4

**Family.** Structured text — four-column executive-summary / SCQA parallel.

**What this is.** A flat, four-column parallel layout sized to carry an SCQA-style executive summary in a single slide: Problem → Solution → Outcomes → Rationale. The action title up top is the deck's organizing thesis; the four cards underneath read left-to-right as the supporting sentence. No anchor panel, no dark caps — equal-weight cards, light bodies, one quiet accent.

**Use when.**
- The narrative is genuinely MECE in **four** parts (not three, not five). The classic case is SCQA: situation / complication / question / answer, OR problem / solution / outcomes / rationale.
- Each part fits in ~265px of column width — i.e., a short eyebrow + one-line heading + 2–3 sentences of body. If any column needs more, the layout breaks.
- The slide IS the exec summary — typically slide 2 of a deck, or the closer of a workstream readout.

**Use a sibling instead when.**
- Three parts → `three-column-vanilla` or `dark-header-cards` or `3pillar-icon-circles`.
- One conclusion + 2–4 supporting forces (asymmetric weight) → `anchor-with-cards` (3-row, with the dark anchor panel).
- Five+ parts → don't. Re-cut the narrative; five cards at 1280px is too cramped to read.

**What makes the structure work.**
- **Equal-width grid (~287px each, 16px gap).** Four parallel columns sized to be readable but not invite over-writing. Card width is the natural editorial cap — if your draft overflows, the brief, not the layout, is wrong.
- **One accent moment, load-bearing.** A 4px BRAND_ACCENT stripe sits on the TOP edge of Card 1 only. That signals "start reading here" — the SCQA arc has a direction. Cards 2-4 use a 1px CARD_BORDER outline. The accent never repeats across multiple cards.
- **Bold ceiling at exactly 5.** Title (1) + 4 card headings (4) = 5 bold runs. AT the brief's ceiling, no slack. Eyebrows uppercase NOT bold; bodies NOT bold; meta lines NOT bold.
- **Hierarchy from size + color, not gray gradients.** Eyebrow 11px BRAND_PRIMARY uppercase letter-spaced → heading 18px bold BRAND_PRIMARY → body 13px TEXT_DARK. Body sits one pixel under the 14px default because the column is narrow; still above the 12px floor.
- **Title bottom-anchored at y=100** via `add_title_block` — 2-line titles grow upward, never push the cards down.

**Anti-patterns to AVOID.**
1. **Stripe on every card.** Putting the BRAND_ACCENT top-stripe on all four cards (or on cards 1 and 4 to "bracket" the arc) is a tempting but wrong move — it kills the directional cue and burns the accent four times over. The stripe belongs on Card 1 only.
2. **Dark cap on every card.** Don't reach for the dark-header-cards treatment in the four-column variant. Four dark caps at 287px wide is a heavy banding effect that reads as "menu" rather than "argument" — the SCQA arc disappears.
3. **Body bloat.** This layout fails the moment any one column needs more than ~3 short sentences. If the Solution card has a sub-list of 5 steps, this isn't the right layout — promote the Solution to its own slide and use a roadmap or numbered-rows layout there.
