# A/B Methodology Review — Reviewer C (Strategic)

**Date:** 2026-05-26
**Blind to:** Reviewers A and B.
**Angle:** Why are we A/B'ing at all? Does the data still support running it, given everything that closed in Category 2?
**Prior C positions in this thread:** Path D earlier (overridden by Mario's production-grade bar, correctly); revised to Items 1/2/4 fix + 3 accept (now closed).

---

## Should we A/B at all?

**No — not in the formal "v1-vs-v2 on the same brief, side-by-side scorecard, k=3 briefs, then consolidate" shape that's currently implied.**

Two things have changed since the A/B framing was written into DECISIONS.md "Testing protocol":

1. **The empirical question the A/B was supposed to answer is already answered.** v2 works. Item 1 closed SKELETON_REJECTED + FALLBACK_MERMAID end-to-end. Item 2 closed FedEx + ACN multi-client without `validate_theme()` halting and without "two purples" wrong-color bleed. The cross-client comparison closed 9/10 pattern agreement — the bounded-non-determinism floor is real and small. That is not "v2 might work"; that is the architecture-validation evidence the formal A/B was supposed to generate.

2. **v1 is not the v1 the 23% number was measured against.** v1 has had Phase 3 color correction, the brand.yml rewrite is landing, accent-bar discipline is documented, the theme rewrite resolved the loader bug v2 was partly built to escape. The A/B as originally conceived was "old-broken-v1 vs new-v2." What's actually on the table now is "v1-post-rewrite vs v2-v0." Those are not the same comparison. Most of the things v1-old failed at are things v1-post-rewrite no longer fails at. The honest read is that the *delta* the A/B is measuring has shrunk significantly since the protocol was written, and nobody has re-asked whether the remaining delta is worth a multi-day formal test.

The smokes have answered the original A/B question. The new question — does v2 produce better slides than v1-post-rewrite on a real client deck — is a *different* question and the slidelab-intro brief is the wrong instrument for it.

**The frame to attack:** "of course we A/B, that's what DECISIONS.md says." DECISIONS.md was written before Category 2 closed and before v1's theme rewrite landed. It was the right protocol for that state of the world. It is not automatically the right protocol for this state of the world.

---

## If yes: what's the strategic goal? If no: what replaces it?

What replaces it is **a structured rolling-pilot protocol** — Mario's risk-asymmetry intuition from the prompt's section 6, formalized.

The consolidation decision Mario actually needs is not "v1 wins / v2 wins / both win on a 30-slide head-to-head." It's: **on the next 3 real client decks Mario builds, which skill produces a deck that lands with the partner without escalation, and does either skill silently fail in a way the smokes didn't surface?** That's the production-grade question. The formal A/B doesn't answer it — it answers a stacked-deck question on a brief that was engineered against v1's failure modes.

Concrete replacement protocol:

1. **Next real FedEx or ACN deck -> v2.** Ship it. If it lands, log what worked and what was edited post-build. If it fails (escalation, partner rejection, silent fabrication, wrong colors), capture the failure mode in `_decisions/v2-production-failures.md` and route deck #2 to v1 as fallback.
2. **Deck #2 -> opposite skill.** If deck #1 was v2 and clean, deck #2 is v1 — to establish that v1-post-rewrite still works under current conditions and to give Mario a fresh side-by-side instinct on the same kind of brief shape.
3. **Deck #3 -> v2 again.** This is the regression check. Two v2 deliveries with a v1 deck between them creates a real comparison signal *on real work*, not on a brief that biases the result.
4. **Decision point after deck #3:** consolidate based on what happened across the three real deliveries. Criteria below.

This is what the smokes were *for*. They were the gate to make the rolling pilot safe to run. They closed. Now run the pilot, not a ceremony on top of the pilot.

If formal A/B persists as a parallel motion, scope it correctly: it is a **regression fixture**, not a competition arena. Keep the slidelab-intro brief as the synthetic regression input that runs before any v2 release tag. Don't use it to pick a winner.

---

## Is Path D back on the table now?

**Yes, and it's stronger now than it was when I first argued it.** The empirical argument against Path D earlier in this session was production-grade caution — Mario rightly said the smokes had to close before any "ship v2 as default" decision could be made without flying blind. That objection no longer applies because the smokes did close. The original Path D was premature; a re-stated Path D ("ship v2 as default for the next real FedEx/ACN deck, route NFL to v1, treat v1-post-rewrite as documented fallback") now has the validation behind it that the earlier version lacked.

What changed:

- **Mermaid dark code lit up.** Item 1 closed the largest unknown. FALLBACK_MERMAID end-to-end is no longer hypothetical.
- **Multi-client lit up.** Item 2 closed FedEx + ACN. The "v2 only works on the brief it was built around" critique no longer holds for the templates v2 v0 is scoped to.
- **Bounded non-determinism is measured.** 9/10 cross-client agreement on the same brief is the empirical floor we didn't have when I argued the original Path D. Agent stochasticity is documented, not feared.
- **Scope boundary is explicit.** NFL is out, in writing. The "two-client scope" framing replaces the "v2 might not handle X" hand-wave.

What hasn't changed and still argues against pure Path D:

- v0.1 gaps are still real (handoff contract drift, schema validation, contract test in CI).
- v2 has not yet shipped a real client deck. The first one is genuinely a test in production, regardless of how the smokes performed.
- v1 has the institutional muscle memory (months of real deliveries); v2 does not.

The synthesis: Path D is back on the table not as "ship v2, retire v1" but as **"v2 is the default for new work in the FedEx + ACN scope; v1 stays alive as fallback for failure modes v2 surfaces in production; NFL stays on v1 until v0.1."** That's a softer Path D than the original — but it's the right shape and the data supports it now.

---

## Decision criterion for "we're done — pick a winner"

The consolidation criterion should not be "v2 wins X of Y A/B scorecards." It should be **observed behavior across 3 real deliveries**, each independently producing an unambiguous signal:

**Consolidate to v2 (deprecate v1) when:**
- 3 of 3 real decks (or 2 of 3 with the failure traced to a non-architectural cause like brief quality) ship through v2 without escalation
- No silent fabrication or fidelity failure surfaces in partner review
- v0.1 hardening (schema validation, contract test, brand.yml integration) is complete
- The don't library has 50+ entries from real builds

**Keep both as routed peers when:**
- v2 ships clean on 2 of 3 but with consistent friction on a specific deck-shape (e.g., dense-table-heavy briefs) that v1 handles cleanly
- The friction is mechanism-specific, not architectural — a documented routing rule emerges naturally

**Deprecate v2, return to v1 when:**
- 2 of 3 real decks fail in front of a partner (silent fabrication, wrong colors, off-brand Mermaid that the smoke didn't predict)
- A failure mode appears that the architecture cannot absorb without v1-style lever-stacking

The criterion is observed production behavior, not synthetic scorecard wins. **Ceremony to manufacture conviction is what produced v1's lever-stack in the first place.** Don't repeat the pattern at the meta-level.

---

## Biggest concern

**The biggest concern is not "v2 might not work" — it's "we will spend two more days running an A/B that doesn't change the decision."**

Concretely: if the A/B runs as currently framed (slidelab-intro through both skills, side-by-side review, scorecard), three outcomes are possible:

1. **v2 wins clearly.** Predicted outcome given the brief was architected around v1's failure modes. Tells us nothing the smokes didn't already.
2. **v1 wins clearly.** Vanishingly unlikely given Item 1 + Item 2 + the cross-client comparison results. Would actually be a useful signal — but the conditional probability is so low that the *expected value* of running the test to get this signal is negative against the cost.
3. **Mixed/similar.** The "keep both, route by user preference" outcome embedded in DECISIONS.md line 246. This is the worst result because it converts a transient parallel-skill maintenance burden into a *permanent* one, and the framing makes it hard to revisit.

Outcome 3 is the trap. The A/B as currently framed has built-in epistemic gravity toward "keep both" — that outcome is pre-authorized in the protocol and looks responsible. It is not responsible. It is the consolidation decision being silently deferred under a procedural shape that looks like resolution.

Path D / rolling-pilot doesn't have that trap. The decision is forced after deck #3. There is no "keep both because the scorecard was inconclusive" branch; there is only "v2 shipped 3 deliveries cleanly, retire v1" or "v2 had specific failure modes, route around them."

**Adjacent concern:** the A/B framing is also masking a different conversation Mario should be having — what's v0.1 actually committed to, and what's the cost of getting v2 to feature-parity with v1's reach (NFL, fishbone, concentric rings). The A/B sucks oxygen away from that scoping conversation. Path D / rolling-pilot makes the scope question primary: v0.1's deliverables are whatever the first real-deck failures surface, not a pre-specified wishlist.

---

## Three-sentence verdict

**Don't run the formal A/B as framed.** The Category 2 smokes already produced the architecture-validation evidence the A/B was supposed to generate, v1-post-rewrite is not the v1 the A/B was scoped against, and the slidelab-intro brief is structurally biased toward v2 — running it as a winner-pick would be ceremony, not measurement. Replace the A/B with a rolling 3-deck production pilot (v2 -> v1 -> v2 on real FedEx/ACN work, decide after deck #3) and keep slidelab-intro as a regression fixture that gates v0.1 releases; Path D is now defensible in its softer "v2 default, v1 documented fallback, NFL routed to v1 until v0.1" form because the smokes that should have preceded it have closed.
