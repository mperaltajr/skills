# Stage A Denominator Mismatch Review — Reviewer B

**Angle:** measurement integrity. No measurement is better than a confounded measurement.
**Date:** 2026-05-25
**Prior position (review-B):** "rubric drift via threshold modification produces confidently wrong numbers rather than noisy ones." I am now reviewing whether the proposed denominator translations violate that warning.

---

## TL;DR — Verdict

**Pick (D) with a hard scope cut, OR (E). Reject (A), (B), (C) categorically.**

The locked rule is `>=8/10 SHIP AND <=1 fab`, `<=3/10 SHIP OR >=3 fab`, `4-7/10` middle, `>=2 fab` override. The brief has 7 content slides and 12 total. **There is no arithmetically defensible translation from the locked /10 thresholds to either /7 or /12 that preserves what the original committee actually locked.** Translating IS the failure mode I named in my prior review. Either re-author the brief to exactly 10 content slides (option D, ~30-60 min Mario time), or abandon Stage A as a numerical measurement and commit directly to Path D-soft on the evidence we already have (option E).

My recommendation: **(D) if Mario wants a defended number; (E) if Mario wants to stop spending protocol effort on a measurement whose marginal value is now lower than the cost of getting it right.** I lean (E) and explain why below.

---

## 1. Is ANY translation acceptable? Categorically no.

The locked rule was not ">=80% ship-as-is." It was **">=8/10 ship-as-is AND <=1 fabrication flag."** Those are two integer thresholds joined by an `AND`, not a percentage. The /10 denominator is load-bearing on both axes for three reasons:

**(a) The fabrication threshold is integer-quantal, not proportional.** `<=1 fab` on /10 means "one fabrication is tolerable, two is the override trigger." That is a hard count, not a rate. Translating `<=1/10` to `<=0.7/7` and rounding to "<=1/7" silently moves the override trigger from 2 fabrications to 2 fabrications — but now the band-3 ceiling sits on a smaller base, which means the conditional probability of a single fab being "tolerable noise vs. categorical signal" has shifted. The committee never reasoned about that shift. Quoting Reviewer A''s locked language: fabrication is the "load-bearing v2-justifies bucket and cannot be outvoted." Re-scaling silently re-weights it.

**(b) The ship thresholds were chosen as gestalt anchors, not interpolation points.** `>=8/10` was "Mario would ship 8 of 10 unedited" — a concrete imaginable scene. `>=6/7` is not the same scene; `>=10/12` is a third different scene with five non-content covers/dividers mixed in. The committee did not lock a function; it locked three specific integer points on a specific number line. Linear interpolation across denominators is unjustified extrapolation from three data points to a continuous threshold curve nobody approved.

**(c) Option (C) the axis-split is the most seductive and the most wrong.** Splitting "content slides -> ship+fab axes; covers/dividers -> fab only" sounds principled but introduces an unmeasured asymmetry: it gives the fab axis a denominator of 12 and the ship axis a denominator of 7. Now `>=2 fab` override threshold on /12 is a different test from `>=2 fab` on /10 (the original lock). The committee never sized fabrication-prevalence against a covers-included corpus. The threshold was sized against 10 content-bearing slides. We have no calibration for "what is the base rate of fabrication on a divider slide" — probably very low, which means folding 5 dividers into the fab denominator silently makes the override harder to trigger. That is precisely the rubric drift I flagged.

**Categorical answer: no translation preserves the lock. Every translation is a re-derivation that the original committee did not sign off on.** Per my own pre-commit: rubric drift via threshold modification = confidently wrong numbers. Options (A), (B), (C) all violate this and should be refused.

---

## 2. If (D) re-author: what is the new brief shape?

**Required shape: exactly 10 content slides, scored on the locked rule unchanged.**

To avoid the "shaped to favor v1 or v2" failure mode, the re-author must satisfy three constraints:

**Constraint 1: Add 3 content slides; do not remove or modify the existing 7.** The existing 7 content slides (3, 5, 6, 7, 9, 11, 12) were authored before this committee and represent the brief Mario actually wants to ship. Modifying them post-hoc to fit the protocol is the worst form of confound — it shapes the instrument around the protocol rather than the question. **Keep all 7; add 3 net-new content slides.**

**Constraint 2: The 3 new slides must be authored from chassis families v1 and v2 both support symmetrically.** No v2-only chassis (no diagram primitives v1 cannot match). No v1-favored chassis (no plain bullet lists with no structural ask). Three candidates that are roughly chassis-neutral:
- A 2x2 quadrant comparison slide (both can attempt; both can fail in instructive ways).
- A single-stat hero finding slide with one supporting bullet (the chassis where v1 is at its strongest; including it prevents the brief from being v2-shaped).
- A timeline / sequence slide (the chassis where v2''s G-family rebuild is queued; including it prevents the brief from being v1-shaped).

**Constraint 3: The 3 new slides'' governing thoughts and content must be written BEFORE either v1 or v2 sees them.** Mario writes the briefs cold, commits them to git, then runs v1. No iterating on the brief after observing a v1 output. This is the same pre-commitment discipline as the per-slide predictions step.

**Why not just renumber and call it "10 of 12 are content"?** Because the locked rule was sized against 10 *scorable* slides. Renumbering does not change that the brief has 7 scorable slides — it just hides the denominator mismatch behind nomenclature. The fix has to be real content, not bookkeeping.

**Cost:** ~30-60 min Mario time for three new slide briefs. Plus one re-run of v1 on the expanded brief. The re-run is cheap (deterministic, ~10 min compute).

**Risk:** the new slides are still "synthetic regression brief" content (Reviewer C''s standing complaint from the prior committee). Expanding from 7 to 10 does not change the structural-bias problem; it just makes the denominator match the lock. (D) buys denominator correctness, not corpus validity.

---

## 3. If (E) abandon: is the existing evidence sufficient for Path D-soft directly?

**Yes, with one caveat.** The evidence already on the table:

**Evidence point 1 — v2 architectural tests pass cross-client.** Category 2 smokes show v2 slides 6+7 (the chassis-pick + collision-detection architectural test slides) building cleanly in both client contexts. This is the load-bearing capability claim for v2: the architecture does what it says it does. That claim is independent of any v1-NOW measurement on slidelab-intro.

**Evidence point 2 — the Category 2 smokes themselves.** v2 produced SKELETON_REJECTED and FALLBACK_MERMAID events on briefs v1 would have built-anyway-with-invented-content. That is the asymmetric refusal capability that motivated v2''s existence. The events fired in real smokes; this is not a hypothesis.

**Evidence point 3 — v1''s theme rewrite and Phase 3 color correction are in.** v1-NOW is materially different from v1-at-23%. We do not need a number to know that; the code diff tells us.

**What Stage A would have added on top of this:** a single integer on a single brief that, per my prior review (sec.1), is **not commensurate with the 23% historical baseline anyway** and is **structurally biased toward surfacing v1 failures** (slidelab-intro was engineered against v1''s failure modes). The locked Stage A rule was already a retreat from the original re-measurement framing — it is now a "binary ship-test" whose only function is to either confirm Path D-soft (band 1 + 3) or force consolidation (band 2). **Band 2 requires `<=3/10 ship OR >=3 fab`** — a strong failure. Given that v1''s theme rewrite is in, band 2 is improbable on priors. The most likely outcomes of Stage A are band 1 or band 3, both of which route to Path D-soft.

**So the question becomes:** is running Stage A worth ~30-60 min of brief re-authoring + ~30 min of scoring (~60-90 min total) to confirm the most likely outcome that we would land on anyway by Reviewer C''s argument from the prior committee?

**My answer:** no, if Mario can live with Path D-soft committed on architectural evidence alone. **Caveat:** Path D-soft has a built-in re-evaluation gate after the first 2 real FedEx/ACN production decks. That gate is the natural place to surface v1-NOW shortcomings on real corpus, where the measurement actually means something. Stage A on slidelab-intro was always a synthetic stand-in for that real-deck signal; abandoning it loses nothing the rolling validation does not recover.

**Reviewer C''s position from the prior committee was exactly this.** The denominator mismatch is the empirical evidence that C was right and B (me) and A were over-instrumenting. The protocol committee locked a /10 rule against a /7 brief; that mismatch was latent in the lock and surfaced only when Mario went to execute it. That is a sign the protocol was sized to a brief Mario was not actually going to build.

---

## 4. Cheapest path to a defensible routing decision

**(E) at ~0 marginal cost. Then Path D-soft, with the rolling 2-deck re-evaluation already locked.**

The defensibility argument writes itself:

1. v2''s architectural capabilities (SKELETON_REJECTED, FALLBACK_MERMAID, sec.2a no-fabrication, Layer 4 intent-filter, Layer 5 collision detection) are demonstrated by smoke events that already fired — capability is established, not hypothesized.

2. v1-NOW has had theme rewrite + Phase 3 color + path fixes + brand.yml sidecar applied — the code diff is the evidence that v1 is materially different from v1-at-23%. No re-measurement on a synthetic brief tells us anything the diff does not already.

3. Path D-soft (v2 default for scoped clients, v1 documented fallback) is the routing decision; it is **already conservative** because it preserves both pipelines. The cost of being wrong about Path D-soft is bounded — we run v2 for two real decks and find out.

4. The 2-real-deck re-evaluation gate is the actual measurement that matters. slidelab-intro was never going to be that gate because it is a regression fixture, not a representative corpus.

**Why not (D)?** Because (D) buys ~60-90 min of work to produce a number that, in expectation, lands in band 1 or band 3, both of which route to Path D-soft. We already know where we are going. (D) is honest measurement but unnecessary measurement. The cheapest defensible path is to skip it.

**Sunk-cost note for Mario.** Substantial protocol work is sunk. Reviewer C warned this could become ceremony to manufacture conviction. The denominator mismatch is the universe handing us a low-cost exit from that ceremony: the brief does not fit the protocol; rather than torturing the protocol to fit the brief, take the exit.

---

## What I am NOT saying

- I am not saying Stage A was a mistake to lock. It was the right next step given what was known at lock-time. The brief shape was not known to the committee when the rule was written.
- I am not saying measurement is bad. I am saying *this specific measurement, on this specific brief, with translated thresholds*, is worse than no measurement because it carries rhetorical weight without epistemic weight.
- I am not saying v1 is fine. I am saying v1-NOW vs v1-at-23% is the wrong axis; v2-architectural-capability vs v1-architectural-capability is the right axis, and that axis is already decided.

---

## Final verdict (3-sentence form for return)

Translating the locked /10 thresholds onto a /7 or /12 denominator IS the rubric-drift failure mode I pre-committed against; options (A), (B), and (C) violate that pre-commit and must be refused categorically. The cheapest defensible move is (E) — abandon Stage A as a numerical measurement, commit to Path D-soft on the architectural evidence already in hand (cross-client v2 smokes, SKELETON_REJECTED / FALLBACK_MERMAID events on fabrication-prone briefs, v1''s theme rewrite landing), and let the locked 2-real-deck re-evaluation gate do the work slidelab-intro was a synthetic stand-in for. If Mario wants a defended number anyway, (D) is the only honest path: add 3 chassis-neutral content slides (pre-commit cold, no v1/v2 observation), re-run, score on the unmodified locked rule — but I would not spend the 60-90 min when the answer is Path D-soft on priors.
