# Stage A Protocol Review — Reviewer C (Strategic / Cost-Benefit)

**Date:** 2026-05-25
**Angle:** Is Stage A worth running at all? Is the decision value greater than the Mario-hour cost?
**Prior position:** In ab-methodology-review-C I argued against the formal A/B and for a rolling 3-deck production pilot under a soft Path D. The committee landed on a two-stage gate with Stage A = re-measure v1-NOW on slidelab-intro. Run count, scoring rubric, and "materially better" threshold were never specified. That omission is not a detail to fill in — it is the whole problem.

---

## 1. Is Stage A load-bearing or ceremony?

**Ceremony, in the shape it is currently in.** Walk the decision tree honestly:

- **v1-NOW lands at ~20%.** Decision: go v2 / Path D-soft. But we would go there anyway — the smokes already validated v2 architecture, and v1 at 20% is the pre-rewrite baseline we already assumed.
- **v1-NOW lands at ~60%.** Decision: Path D-soft (v2 default in scoped clients, v1 fallback, NFL on v1). But that is the recommended landing *regardless* of v1-NOW's number, per the prior committee.
- **v1-NOW lands at ~40% (the middle).** No specified rule. In practice Mario will do what he was going to do anyway — Path D-soft — and rationalize the number after.

If every plausible Stage A outcome routes to Path D-soft, Stage A is not a decision instrument. It is a confidence-building exercise dressed as a measurement. That is exactly the trap I named in the prior review (outcome 3 of the original A/B): a procedural shape that looks like resolution but silently defers the consolidation decision.

The one branch where Stage A *would* be load-bearing is v1-NOW landing at, say, **75%+** on slidelab-intro — high enough to argue "v1 is fine, do not bother with v2 default." That outcome has near-zero prior probability given (a) slidelab-intro was architected against v1's failure modes, (b) the theme rewrite addressed loader bugs but did not redesign v1's chassis vocabulary, and (c) the 23% measurement was on the *vocabulary*, not the colors. Mario-hours spent chasing a near-zero-probability branch are negative expected value.

**Verdict on Q1:** Stage A as currently scoped is ceremony. It does not change the decision in any plausible outcome.

---

## 2. Lowest-cost invalidation — what can Mario observe in <1 hour?

The cheapest invalidation is not a number; it is a one-deck eyeball. Specifically:

**Mario runs slidelab-intro through v1-NOW. One run. Opens the .pptx. Spends 10 minutes flipping slides. Asks himself one question: "Would I send this to a partner without rebuilding anything?"**

Three possible answers, each terminal:

- **No / hell no.** Stage A is invalidated downward. We already know v1-NOW is not partner-grade on this brief shape; running 5 more iterations to get a score does not add information. Go to Path D-soft now.
- **Yes, with light edits.** Stage A is invalidated upward in the only way that matters. v1-NOW is viable, which means the consolidation question is genuinely about *which is better*, not *whether v1 is broken*. That is the question only the rolling production pilot can answer — not slidelab-intro. Skip Stage A, run the rolling pilot.
- **Mixed — some slides clean, some bad.** This is the most likely outcome and also the most diagnostic. It tells Mario the v1-NOW failure mode is per-pattern (chassis-level), not per-deck (architecture-level). That is a Path D-soft signal *and* a v0.1 prioritization signal in the same observation.

All three answers route to Path D-soft. The 10-minute eyeball produces the same decision as the formal Stage A would, at ~5% of the cost.

**Verdict on Q2:** A single v1-NOW build of slidelab-intro plus a 10-minute eyeball invalidates the need for Stage A. Mario does not need a scoring rubric to make this call.

---

## 3. Should Stage A be replaced by the eyeball?

**Yes, with one structural addition.** The eyeball alone risks being unwritten — six weeks from now Mario will not remember which slides were clean and which were not, and the v0.1 backlog will drift. Replace Stage A with:

1. **One v1-NOW build of slidelab-intro.** Standard run, no special config.
2. **10-minute slide-by-slide flip.** Mario writes, in `_decisions/v1-now-eyeball-2026-05-25.md`, for each slide: "ship as-is / light edit / rebuild" plus a one-line reason for any "rebuild" tag.
3. **Decision rule, pre-committed before he opens the deck:**
   - If >=80% of slides are "ship as-is" or "light edit" -> v1-NOW is viable, go Path D-soft, rolling pilot decides consolidation.
   - If <80% -> v1-NOW is not partner-grade on this brief shape, v2 is the default for scoped clients, rolling pilot decides whether v1-NOW survives as fallback or gets deprecated.

Total cost: ~45 minutes including the writeup. That is a measurement, not a vibe. And it commits the decision rule *before* the data, which is the only way to prevent post-hoc rationalization.

This is what Stage A should have been from the start: a single-pass production-instinct check with a pre-committed routing rule, not a scoring rubric.

**Verdict on Q3:** Yes, replace Stage A with a single-build pre-committed eyeball. Numbers add nothing the eyeball plus a pre-committed threshold does not already give.

---

## 4. Risk that Stage A produces a slidelab-intro-specific artifact

**Yes, and the risk is higher for Stage A than for the original A/B, not lower.**

The original A/B had at least the possibility of brief diversity (k=3 briefs was on the table). Stage A is structurally pinned to slidelab-intro — that is its definition. So whatever number it produces, that number is "v1-NOW's acceptance rate on the brief that was engineered against v1's failure modes." That is not generalizable. It is a regression-fixture number masquerading as a strategic metric.

Concretely: slidelab-intro is heavy on chassis types where v1's lever-stacking historically broke (multi-panel, anchor-with-cards, KPI tile). It is light on chassis where v1 has years of muscle memory (single-finding, dense text, exec summary). v1-NOW's slidelab-intro score is *deliberately* a worst-case-for-v1 number. Using it as the trigger for "v1 is dead / v1 is alive" is methodologically backwards.

This is the same critique I leveled at the original A/B in my prior review — and the move from "k=3 briefs" to "1 brief, slidelab-intro" made the bias problem *worse*, not better. Stage A inherited the bias and dropped the diversity that partially compensated for it.

**Mitigation if Stage A runs anyway:** treat the number as "v1-NOW's worst-case-shape floor," not "v1-NOW's overall acceptance rate." Do not compare it to the 23% historical number — that was a different brief mix. Anchoring on the 23% delta is the single most likely way Stage A produces a misleading conclusion.

**Verdict on Q4:** The artifact risk is high and the structure of Stage A makes it worse than the original A/B on this dimension. Any score from Stage A needs an explicit "this is a worst-case-shape floor" caveat attached at the source, or it will be cited later as if it were a general acceptance rate.

---

## 5. "Give me the answer right now, no more measurement"

**Path D-soft, starting Monday. No Stage A, no eyeball, just commit.**

- v2 (slide-builder-simple) is the default for the next FedEx and ACN deck.
- v1 (slide-builder) stays alive as documented fallback. If v2 produces a deck that fails partner review, the failure mode goes in `_decisions/v2-production-failures.md` and that deck rebuilds on v1.
- NFL deck routes to v1 until v0.1 lands (per the existing nfl-scope-boundary.md).
- After 3 real client deliveries through this routing, Mario decides: deprecate v1, keep both as routed peers, or roll back v2. Criteria are the ones in ab-methodology-review-C.md lines 71-83.

Why this is safe to commit without Stage A:
- The architecture-validation evidence the formal A/B was supposed to produce already exists in the Category 2 smokes (Items 1, 2, cross-client 9/10).
- v1-NOW is *not deprecated* — it stays available. The downside of being wrong about v2 is "one deck rebuilds on v1," not "Mario is stuck with a broken skill in front of a partner."
- The rolling pilot is the actual decision instrument. Stage A is not on the critical path to that pilot.

The only reason to run Stage A is to produce a number that retroactively justifies a decision Mario is going to make anyway. That is a tax on Mario-hours, paid to manufacture a feeling of rigor. Skip it.

**Verdict on Q5:** Path D-soft, commit Monday, rolling pilot is the decision instrument. Stage A is not required for any branch of the decision tree.

---

## 6. Highest-risk failure mode of Stage A

**The highest-risk failure mode is not a bad measurement — it is a *good-looking* measurement that gets cited later as authoritative.**

Specifically: Stage A produces a v1-NOW score of, say, 45%. Mario goes Path D-soft (as he would have anyway). Three months from now, in a different conversation, someone asks "is v1 still alive?" and Mario or a future Claude session cites "v1-NOW is at 45% on the standard brief, so it is the documented fallback." That number gets treated as v1's real acceptance rate. It is not. It is v1-NOW's worst-case-shape regression-fixture number, and using it as a general benchmark will mis-route future decisions — especially the v0.1 scoping conversation, which should be driven by *real production failure modes*, not a slidelab-intro score.

The number, once produced, will outlive the caveats around it. That is the structural failure mode.

**What I would do about it:**

1. If Stage A runs, **do not record a single number for v1-NOW.** Record per-chassis scores, never aggregated. That makes it impossible to cite "v1 is at X%" later, because there is no X.
2. **Tag the writeup as a regression fixture, not a benchmark, in the file header.** First line of the artifact: "This is a regression-fixture measurement on a brief engineered against v1's historical failure modes. It is not v1's general acceptance rate. Do not compare to the 23% historical number."
3. **Pre-commit that Stage A's output is read once and archived.** It does not get re-cited in future decisions. If a future decision needs v1-NOW data, run a new measurement on the brief shape that decision is actually about.

Better yet: do not run Stage A, and the failure mode does not exist.

**Verdict on Q6:** The risk is not a bad number — it is a durable misleading number. Mitigation is per-chassis-only reporting, regression-fixture framing in the file header, and a one-time-use policy. Best mitigation is not running Stage A.

---

## Three-sentence verdict

**Do not run Stage A.** Every plausible outcome routes to Path D-soft, the slidelab-intro brief structurally biases any number it produces into a worst-case-shape floor that will be misused later as a general benchmark, and the smokes already produced the architecture-validation evidence Stage A would re-produce at higher cost — so Stage A is ceremony, not measurement. If Mario wants a sanity check before committing, replace Stage A with a 45-minute single-build eyeball of v1-NOW on slidelab-intro with a pre-committed 80%-ship-or-light-edit routing rule recorded in `_decisions/v1-now-eyeball-2026-05-25.md`; otherwise commit Path D-soft Monday and let the rolling 3-deck production pilot be the actual decision instrument.
