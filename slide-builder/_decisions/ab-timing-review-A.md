# A/B Timing Review — Reviewer A (empirical / data-quality)

Status: blind review · Reviewer A of 3
Angle: which path produces decision-grade data
Date: 2026-05-25

---

## Verdict

**B — wait for v1 theme rewrite, then A/B.** With one strong amendment: while v1 is rewriting, run a **non-decision smoke A/B on a fresh brief** (not slidelab-intro) for shakedown purposes only. Do not let that smoke result drive any consolidation talk. The first *decision-grade* A/B happens against the `brand.yml`-canonical v1.

---

## Reasoning

The right question isn't "what produces the most data fastest." It's "what produces data clean enough that the consolidate-to-X decision survives scrutiny." Walk each path on that axis.

### What Path A's data actually tells you

Path A's output is a per-slide comparison where v1 ran with the slot-mapping loader bug and v2 ran with the same `twins/client_theme.py` bug inherited. Three failure modes contaminate the result:

1. **Confounded color failures.** When a v1 slide ships wrong colors, you cannot tell if it's the v1 architecture losing or the v1 loader losing. When a v2 slide ships wrong colors, you cannot tell if it's v2 architecture losing or v2-inheriting-v1's-loader losing. Every color-affected slide produces a measurement you can't attribute.
2. **Asymmetric impact you cannot model.** v1 has accumulated workarounds for the loader bug (the `OFF_PALETTE_*` aliases, `KNOWN_CLIENT_HUE_RANGES` halts, hardcoded slot conventions). v2's `validate_theme()` Check 3 is FedEx-only (per build-deck-review.md issue #3) — so for a FedEx template, v2 halts on the bug; for any other template, v2 ships through it. The two skills do *different wrong things* in response to the same underlying bug. That's not a fair comparison; it's a noise generator.
3. **v2 mid-build defects still present.** Per build-deck-review.md, critical issues #1/#2/#3 are flagged HARD STOP. The reviewer's verdict at line 131 is explicit: HALT, don't ship downstream against this build_deck.py. Until those patches land, Path A is measuring v2-in-broken-state, which tells you nothing useful about v2-in-shippable-state.

The honest read on Path A: it produces *anecdotes*, not data. You'd get five slides where reviewers point at PNGs and argue. You wouldn't be able to defend a consolidation call against any reasonably skeptical second pair of eyes — including your own, two weeks later.

### What Path B's data actually tells you

Path B runs both v1 and v2 against the same `brand.yml`-canonical theme. The loader is no longer a confound. Both skills get identical input (resolved semantic colors) and the comparison reduces to **architecture, prompt design, and pattern library** — which is exactly what you're trying to A/B.

The data Path B produces supports clean statements like:
- "v2's geometric-split picker chose pattern X; v1's chassis vocabulary chose chassis Y; for this slide, X looks better because [reason]."
- "v2 avoided fabrication on slide 9; v1 fabricated quadrant labels. Architecture, not loader."
- "v1's variant rotation produced cross-slide twins on 5/6; v2's didn't. Architecture, not loader."

Each of those is a defensible attribution. None of them is available in Path A.

Path B is not perfect. It still suffers from the brief bias (see next section) and from the fact that v2 is new code with surface-area bugs the regression harness hasn't tripped yet. But the *theme variable is held constant*, which is the prerequisite for any architecture-level claim.

### What Path C adds

Path C's delta data — "what did the v1 loader fix add?" — sounds informative but isn't decision-grade for the question being asked. The question is "v1 architecture vs v2 architecture, which one consolidates the org." The v1 loader fix is a sunk improvement: it will be in v1 either way. Comparing "v1 with bug" to "v1 fixed" tells you the loader rewrite worked, which you already know from the smoke build in proposal C's registration flow. It doesn't change the v1-vs-v2 verdict.

Doubled wall-clock cost (two full A/B runs, two side-by-side pages, two scoring passes) for marginal information. Reject Path C on cost-benefit. The exception: if you genuinely don't trust the smoke-build to validate the loader rewrite, Path C buys you that confirmation — but that's a v1-validation concern, not an A/B concern, and there are cheaper ways to validate the loader.

---

## Bias question — slidelab-intro vs fresh brief

The bias is real and it matters. slidelab-intro was engineered against the v1 failure modes: slide 9 was specifically constructed to surface the fabrication bug, slides 5/6 were constructed to surface the cross-slide twin bug. Running it through v2 is approximately testing the architecture against its own training corpus. A v2 win on slidelab-intro tells you "v2 fixes the bugs v2 was designed to fix" — which is necessary but not sufficient for "v2 generalizes."

**However, for a first A/B, biased-toward-v2 is acceptable *if* the bias is named in the conclusion.** Specifically: slidelab-intro is a regression test, not a generalization test. A v2 win there is a floor, not a ceiling. The valid statement is: "v2 cleanly handles the failure modes that motivated its construction." The invalid statement is: "v2 wins generally."

Recommendation: run slidelab-intro as part of Path B (it's the highest-signal brief for the bugs that matter) AND queue 2 fresh briefs from real engagements (OTC Reboot would be one — Mario has a rolling findings log per project memory) for the *next* A/B round. The consolidation decision needs at least one bias-controlled run before it ships. Per DECISIONS.md line 246: "Decision after 3 real briefs run through both." That ratio is right. Don't decide on slidelab-intro alone.

### Minimum data for confident consolidation

Three runs against three structurally-different briefs:
1. **slidelab-intro** (regression — proves v2 fixes the named bugs)
2. **A 5-7 slide PMO/status brief** (tests if v2 handles low-argument, high-data slides — its weakest pattern class)
3. **A 12-18 slide consulting deck with an argument arc** (tests narrative coherence across variant rotation — where v1's chassis-vocab path was strongest)

If v2 wins or ties on all three, consolidate to v2. If v2 wins on 1 and 3 but loses on 2, you have a routing decision per DECISIONS.md line 250 ("mixed → identify which slide types each handles better"). Anything less than 3 briefs gives you an answer you'll second-guess.

---

## Opportunity cost of waiting 2 days

Worth naming explicitly because Path B's only real cost is wall-clock. What does the 2-day delay actually cost?

- **Mario's calendar time:** ~0. The v1 rewrite is a dispatched agent, not Mario's hands-on work. He gets two days for OTC Reboot or other engagements.
- **v2 dev momentum:** ~0. v2 just finished artifact 6 and has critical parser fixes pending per build-deck-review.md. Those two days are *exactly* the window to land issues #1/#2/#3/#6/#7 from the review. Far from idle.
- **Decision urgency:** Apparently none stated. There's no shipping deadline tied to the A/B result.
- **Knowledge decay:** Minor. The architectural arguments and the v1 failure-mode catalog are documented in DECISIONS.md. Two days won't erode that.

The wall-clock cost is the smallest term in the equation. Path B's data-quality advantage swamps it.

---

## Biggest concern

That the v1 `brand.yml` rewrite takes longer than 2 days and the wait stretches to a week, during which v2 sits idle waiting for v1's blocker. Mitigations:

1. **Land the v2 build_deck.py critical fixes in parallel.** Issues #1/#2/#3 from build-deck-review.md don't depend on the theme rewrite. v2 should be in shippable shape when v1's rewrite lands, not still patching parser regexes.
2. **Time-box the wait.** If v1 rewrite slips past day 4, fall back to Path A *on a fresh non-slidelab brief* and explicitly mark the result as "loader-confounded, preliminary." Don't let perfect-data-quality block all data.
3. **Have the smoke brief ready.** Even before v1 ships, run v2 alone against a fresh brief end-to-end to shake out the build_deck.py + finalize + review chain. That's not an A/B; it's v2 self-validation. If v2 can't survive its own pipeline on a fresh brief, the A/B is moot.

The one thing I'm least confident about: whether the v1 loader rewrite, once it lands, *actually* produces semantically-equivalent themes across both skills. If v1 reads `brand.yml` and v2's transitional path still reads `template.json` via the slot-mapping table (per DECISIONS.md line 267), there's a window where the two skills disagree on color resolution. The fix in the DECISIONS.md follow-on list (v2 reads `brand.yml` primary, falls back to slot-mapping) needs to land *before* the A/B, not after. Otherwise Path B regresses to Path A in disguise.

---

**Summary:** Path B is correct. Use the 2-day wait to land the v2 build_deck.py critical fixes and to confirm v2 reads `brand.yml` first when v1 ships it. Run slidelab-intro plus 2 fresh briefs for a defensible consolidation call — not slidelab-intro alone.
