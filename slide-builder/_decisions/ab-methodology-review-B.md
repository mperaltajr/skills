# A/B Methodology Review — Reviewer B

**Angle:** What is the A/B test actually measuring?
**Date:** 2026-05-25
**Blind to:** Reviewer A (protocol), Reviewer C (strategic framing).

---

## What is the A/B test actually measuring?

The framing in DECISIONS.md § "Testing protocol" is "same brief -> both pipelines -> Mario picks winner per slide -> aggregate." That framing assumes the two pipelines emit comparable artifacts. **They dont.** v1 emits chassis-labeled slides drawn from a 19-chassis vocabulary with adjacency graphs and content tags. v2 emits pattern-labeled slides drawn from 14 patterns (9 splits + 3 diagrams + 2 special objects), governed by 5 hardline rules and a closed 7-verb directive vocabulary. A "win" on slide N for v2 doesnt mean v2s chassis pick beat v1s chassis pick — it means a *different vocabulary at a different abstraction level* produced a PNG Mario preferred.

Mario will be looking at two REVIEW.html surfaces with semantically incommensurate metadata: anchor-with-cards-4 vs Asymmetric vertical 75/25. He can compare the rendered PNGs; he cannot compare the *labels*. So the A/B test, as currently scoped, measures **rendered slide quality conditional on whatever each pipeline happened to pick.** It does not measure pick quality, vocabulary quality, or architectural correctness on its own.

Thats the honest answer. The shipped framing ("well see which wins") is doing more work than it admits.

---

## Three different things you could measure, with trade-offs

| Dimension | What it captures | What it confounds | Cost |
|---|---|---|---|
| **(1) Slide quality** — which rendered PNG looks more like a professional consulting slide | The user-visible outcome | Confounds: agent vocabulary, agent identity (deck-builder vs slide-builder-simple-worker), pattern/chassis sampling distribution, stochastic LLM variance. A "v2 wins slide 3" datum cannot be attributed cleanly to any one of these. | Cheap — Mario eyeballs PNGs. |
| **(2) Agent decision quality** — given the brief content, did the agent pick the *right structure*? | The pipelines editorial judgment | Requires a ground-truth answer for each brief slide ("the right structure for this content is X"). Mario has to pre-commit to what the right structure is BEFORE seeing either output. Otherwise the "right answer" is hindsight-rationalized against whichever PNG looks better. | Expensive — Mario annotates expected structures for every brief slide before either pipeline runs. |
| **(3) Architectural correctness** — do the rules + anti-patterns + classification mechanisms behave correctly across the test set | The architectures resilience and safety properties | Mostly *already validated in smokes.* SKELETON_REJECTED fired correctly on Item 1. FALLBACK_MERMAID classification routed correctly. Hardline #3 adjacency surfaced at finalize as designed. The A/B test would re-confirm these on more briefs but wouldnt tell us anything fundamentally new. | Cheap if you piggyback on (1); near-zero marginal information. |

The Slide Lab build flow vs slide-builder-simple comparison **as currently described in DECISIONS.md tests only (1)**. It claims to inform "consolidation strategy" but (1) alone cannot answer consolidation questions because consolidation is an architectural choice, not a slide-quality choice.

---

## What "v2 wins" actually means (and doesnt mean)

When Mario looks at two PNGs for the same brief slide and prefers v2s:

**What it DOES mean:**
- The brief content rendered against v2s pattern (e.g., Asymmetric vertical 75/25) produced a more compelling slide *for this specific instance, this specific run, this specific stochastic sample*.

**What it DOES NOT mean:**
- v2s pattern vocabulary is better than v1s chassis vocabulary in general.
- v2s worker agent prompt is better than v1s deck-builder agent prompt in general.
- v2 will win on a structurally different brief slide.
- v2 is "right" and v1 is "wrong" — both might be valid renderings of the same brief content; Mario just preferred one aesthetic idiom.

The smoke evidence reinforces this: on the slidelab-intro re-run, **8 of 10 slides picked the same v2 pattern across two runs of the same brief, and 2 diverged onto alternative valid patterns** (slide 7: Vertical N-row stack vs N-column row (3); slide 10: Full canvas vs Asymmetric 75/25). v2 is stochastic by design. If two runs of v2 alone produce different picks on 2/10 slides, then a single v1-vs-v2 comparison run captures *roughly* a 1-in-5 chance of a pick-variance event obscuring the underlying pipeline-quality signal. **A single-run A/B has signal-to-noise problems v2s own variance already documents.**

Mitigation: every A/B comparison should run **each pipeline twice** on the same brief, and the per-slide question becomes "is v2s *better of two* better than v1s *better of two*?" Not free, but it controls for within-pipeline variance.

---

## Baseline question — whats v1-NOWs quality vs v1-AT-23%?

This is the biggest hole in the current framing.

**v2 exists because v1 hit 23% curator acceptance** (DECISIONS.md § "Why v2 exists"). That number is the entire reason for v2s parallel existence. But since that measurement:

- v1s theme rewrite shipped (brand.yml sidecars, register_template.py).
- v1s reader-side path bugs were caught (Defect 4 cross-stream finding).
- v1s Phase 3 color correction landed.
- v1 has continued post-build hardening per the work plan.

**Has v1s curator acceptance moved from 23%?** Nobody has measured. The shipped framing of the A/B test asks "v1 vs v2" but the v1 in that comparison is *v1-NOW*, not *v1-at-23%*. If v1-NOW is at 45% and v2 is at 70%, v2 still wins but the urgency story changes. If v1-NOW is at 65%, the consolidation calculus changes substantially — keeping both may be the right answer rather than migrating.

**Without a v1-NOW baseline, the A/B test has no reference point.** A "v2 wins 6 of 10 slides" datum is meaningless without knowing whether v1-now-baseline is structurally broken (the 23% world) or roughly competitive (the maybe-45-65% world that intervening fixes might have produced).

**This must be done first.** Run v1 alone against the slidelab-intro brief (already exists as a v2 smoke). Measure curator acceptance — the same first-pass-reject metric that produced the 23% number. If v1-NOW is meaningfully better than v1-at-23%, the framing of the A/B test changes from "replacement candidate" to "complementary parallel architecture."

---

## What v2 DOES that v1 cannot — the asymmetric capability

The "wins/losses" framing assumes both pipelines have equivalent capabilities and were comparing execution. **They dont.** v2 has SKELETON_REJECTED (Hardline #5) and FALLBACK_MERMAID — explicit refusal-to-fabricate mechanisms. The Item 1 trigger-brief smoke demonstrates this: slide 2s brief enumerated 2 phases but the agents pattern needed 4 cells -> all 3 options correctly emitted "# SKELETON_REJECTED: brief enumerates 2 phases, N-column row pattern needs 4 cells" and stopped. **v1 has no analogous mechanism.** v1s deck-builder agent would build *something* — quite possibly fabricating Phase 3 and Phase 4 to fill the pattern (this is exactly the slide-9 fabrication bug that motivated v2).

A "v1 wins this slide" datum on a fabrication-prone brief is potentially measuring v1s *willingness to fabricate* as a feature. The A/B framing of "which slide do you prefer?" rewards the pipeline that always ships a slide over the pipeline that correctly refuses on ambiguous input. **Thats a measurement inversion.**

---

## Recommendation: what to measure (specifically) and what to NOT bother measuring

### Measure these (in this order):

1. **v1-NOW curator acceptance baseline.** Re-run the same first-pass-reject methodology that produced 23%. Single number. Until this lands, do not start v1-vs-v2 comparisons — there is no reference point.

2. **Capability surface, not slide quality.** For each brief in the A/B set, count:
   - Slides where v2 emitted SKELETON_REJECTED or FALLBACK_MERMAID (capability events).
   - Slides where v1 built something despite a fabrication-prone brief signal (latent-fabrication events — Mario QCs against the brief, not the slide).
   - Slides where both pipelines produced shippable output (the symmetric-capability subset, where slide quality comparison is meaningful).
   Only the third bucket admits the "which PNG wins?" question.

3. **Within the symmetric-capability subset:** run each pipeline twice, compare best-of-two to best-of-two, score per-slide. Aggregate across 3+ briefs of structurally different shape (consulting recommendation, RFP-style, problem/solution).

4. **Architectural drift events.** Cross-stream findings (reader-side themed/ path bug surfaced in v1 too, client_theme.py migration blockers, etc.). These are operational signals about consolidation cost, not slide-quality signals — but theyre the actual decision input for "should we consolidate?" Cheap to track because they surface during normal runs.

### Do NOT bother measuring:

1. **Pattern-label vs chassis-label "correctness."** These are incommensurate vocabularies. There is no ground truth that says "this slide should have been an anchor-with-cards-4" or "this slide should have been an Asymmetric vertical 75/25." Both are valid abstractions of valid renderings.

2. **Pure aesthetic win-counts across all slides.** Without the capability surface split (item 2 above), aggregate slide-quality wins are confounded by fabrication tolerance. v1 will accumulate "wins" on slides where it built-something-instead-of-refusing — a measurement inversion.

3. **Architectural-correctness signals you already have.** The smokes have already validated SKELETON_REJECTED, FALLBACK_MERMAID classification, adjacency post-pass, anti-convergence brand-token rule, and forecast-override-by-agent. Running the A/B test "to confirm v2s architecture works" is redundant. The A/Bs job is the capability-surface and quality questions, not architecture re-validation.

4. **Single-run results.** v2s documented 2-of-10 pick-variance means single-run comparisons cannot distinguish architecture differences from sampling noise. If you can only afford single runs, you cannot afford this A/B test — youre just gathering anecdotes.

---

## TL;DR

The A/B test as framed in DECISIONS.md measures one thing (slide quality conditional on whatever each pipeline picked) and claims to inform a different question (consolidation strategy). It confounds vocabulary, agent identity, and stochastic variance. It has no v1-NOW baseline to compare against the 23% origin number, so its results are unanchored. And it rewards v1s *willingness to fabricate* as a "win" because it doesnt account for v2s asymmetric capability to refuse on ambiguous briefs.

Before running comparison rounds: (a) measure v1-NOW curator acceptance against the same methodology that produced 23%, (b) split each briefs slides into capability buckets (SKELETON_REJECTED, FALLBACK_MERMAID, latent-fabrication, symmetric-shippable), and (c) only run the slide-quality A/B inside the symmetric-shippable subset, with 2 runs per pipeline to control for the documented 1-in-5 pick variance. Architectural correctness is already validated in smokes — dont pay for it again.
