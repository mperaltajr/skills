# Stage A Denominator Mismatch Review — Reviewer C (Cost-Benefit / Sunk-Cost Discipline)

**Date:** 2026-05-25
**Angle:** Stop measuring when measuring stopped being worth it.
**Prior position (stage-a-protocol-review-C):** Do not run Stage A. Every plausible outcome routes to Path D-soft. The slidelab-intro brief is a regression fixture engineered against v1''s failure modes, not a generalizable benchmark.
**Today''s new information:** The locked rule''s /10 thresholds do not match the brief. The brief has 12 slides total — 5 covers/dividers (1, 2, 4, 8, 10) and 7 content slides (3, 5, 6, 7, 9, 11, 12). Stage A scoring runs on 7, not 10.

---

## 1. At what point does the brief itself become disqualifying as a Stage A fixture?

**It already is. The denominator mismatch is the second strike, and two strikes is enough.**

The first structural problem I flagged in `stage-a-protocol-review-C.md` was that slidelab-intro is *architected against v1''s failure modes* — chassis-heavy on multi-panel / anchor-with-cards / KPI tile (where v1 historically stacks levers and breaks), chassis-light on single-finding / dense text / exec summary (where v1 has muscle memory). I called that a regression-fixture number masquerading as a strategic metric. The committee acknowledged the bias and routed it into the band-3 default ("structurally biased; running an A/B on it would be ceremony, not measurement").

Now we discover the denominator is 7, not 10. That is not a tuning problem. It is a sign that **the rule was written against an imagined deck, not the actual brief.** A scoring rubric that did not survive contact with the artifact it scores is a rubric that was never load-bearing — it was procedural shape.

The disqualification test I would apply: *if you have to translate the thresholds to make the rule fit the fixture, the fixture is wrong for the rule, the rule is wrong for the fixture, or both.* Either way, the instrument is no longer trustworthy as a decision input. We have already paid the cost of discovering it twice. Continuing to patch it is the sunk-cost trap.

**Verdict on Q1:** The brief was disqualifying after the first structural finding. The denominator mismatch is confirmation, not new information. Stage A on this brief is dead.

---

## 2. Is sunk cost the only reason to keep going?

**Yes. There is no genuine information value remaining in Stage A.**

Walk the value calculation honestly:

- **What would Stage A produce that we do not already have?** A per-slide ship-as-is count and a fabrication-flag count on a brief we already know is worst-case-shape for v1. The Category 2 smokes already produced the architecture-validation evidence (Items 1, 2, cross-client 9/10). The 23% historical number already gave us the v1 baseline.
- **What decision does that produce that is not already determined?** None. Bands 1, 2, and 3 all route somewhere we would land anyway: band 1 → Path D-soft, band 3 → Path D-soft, band 2 → consolidate-to-v2 (and band 2 requires either ≤3/7 ship or ≥3 fabrication on a 7-slide content set, which on a v1-hostile brief is the *expected* outcome, not a discriminating signal).
- **What new uncertainty would Stage A resolve?** The only branch where Stage A would change behavior is if v1-NOW lands at, say, 7/7 ship with 0 fabrications on a brief engineered against v1''s failure modes. The prior probability of that outcome on this fixture is near zero. Spending Mario-hours chasing a near-zero-probability branch has negative expected value.

The ~2 hours already spent on Stage A protocol setup is the textbook sunk-cost scenario: the cost is paid, the question is only what the *next* hour buys. The next hour buys nothing the prior 2 hours did not already buy, because the prior 2 hours produced a rule that does not fit the fixture — a finding that itself argues for abandonment.

**Verdict on Q2:** Sunk cost is the only argument left. There is no forward information value. Continuing is paying twice for a decision that has already been made.

---

## 3. What does Mario lose by committing Path D-soft right now vs. running a translated-threshold Stage A?

**He loses nothing of decision value. He gains ~2-3 hours and avoids manufacturing a durable misleading number.**

What he *does not* lose:

- **The architecture-validation evidence.** Already in the Category 2 smokes. Not contingent on Stage A.
- **v1-NOW as a fallback.** Path D-soft keeps v1 alive as documented fallback. Stage A is not gating that.
- **The ability to discover v2 is wrong.** The rolling production pilot (first 2 real FedEx/ACN decks) is the actual decision instrument for that. Stage A does not contribute to it.
- **Optionality.** Path D-soft is reversible. Three real decks from now, if v2 is failing in production, the routing flips. Stage A''s number does not constrain that decision either way.

What he *would* lose by running a translated-threshold Stage A:

- **2-3 hours of Mario-time on the critical path of a time-boxed week.**
- **A durable misleading number in the artifacts.** Per my prior review''s Q6 finding: the highest-risk failure mode of Stage A is not a bad measurement — it is a good-looking measurement that gets cited later as authoritative. A translated-threshold Stage A is *worse* on this dimension than the original, because the translation step itself becomes a footnote that gets dropped in future citations. "v1-NOW shipped 4/7 on slidelab-intro" will be cited as "v1 is at 57%" within three months, the brief-bias caveat will be gone, and the denominator-translation note will be gone too.
- **The signal of decisiveness.** Mario asked "am I close to comparing yet?" five minutes ago. The answer "let me first translate the thresholds and run the measurement" is the answer of someone who has not committed. The answer "I committed Path D-soft, here is the rolling pilot trigger" is the answer of someone running a product.

**Verdict on Q3:** Path D-soft commit now is strictly dominant. There is no downside scenario where the translated-threshold Stage A produces a decision Path D-soft would not also produce, and the Stage A path is strictly more expensive *and* strictly more prone to producing durable misleading artifacts.

---

## 4. Lowest-cost defensible commitment

**A 30-minute commitment artifact, not a measurement.**

Concretely, Mario writes one file — `_decisions/path-d-soft-commit-2026-05-25.md` — with five sections, hard time-boxed at 30 minutes total:

1. **Decision:** Path D-soft is in effect as of 2026-05-25. v2 (slide-builder-simple) is default for the next FedEx + ACN deck. v1 (slide-builder) stays alive as documented fallback. NFL deck routes to v1 until v0.1 lands per `nfl-scope-boundary.md`.
2. **Evidence base:** Category 2 smokes (Items 1, 2, cross-client 9/10) produced the architecture-validation evidence. The 23% historical v1 number established baseline. Stage A was retired because (a) the fixture is structurally biased against v1, (b) the locked rule''s denominator did not match the actual brief, and (c) every plausible outcome routed to Path D-soft regardless.
3. **Rolling pilot trigger:** After the first 2 real FedEx/ACN production decks complete under Path D-soft routing, re-evaluate per the criteria already in `DECISIONS.md` lines 474-477 (≥60% slide-level wins in symmetric-shippable subset AND clear deck-level coherence win → v2 stays default; 3-week hard stop from kick-off; ambiguity → Path D-soft continues as-is).
4. **Reversibility:** If v2 produces a deck that fails partner review during the pilot, the failure mode goes in `_decisions/v2-production-failures.md` and that deck rebuilds on v1. After 3 real client deliveries, Mario decides: deprecate v1, keep both as routed peers, or roll back v2.
5. **What Stage A would have measured, and why it is not on the critical path:** One paragraph naming the regression-fixture problem and the denominator mismatch, so that six months from now no one re-asks "why didn''t we just run Stage A."

That is a defensible commitment. It cites the evidence base, names what it rejected and why, defines the next decision event, and bounds the reversibility cost. It is auditable. It does not require a number.

**Verdict on Q4:** 30 minutes of writing produces a more defensible commitment than 2-3 hours of measurement, because the commitment is grounded in evidence Mario already has and decision rules already specified, not in a number that needs caveats to be honest.

---

## 5. Translated Stage A vs. abandon-and-commit — pick one

**Abandon Stage A. Commit Path D-soft today. The rolling production pilot is the routing decision instrument.**

The case for "translate thresholds and run Stage A" is:

- We have a locked rule, translating it is a 15-minute fix, the measurement is then defensible.
- It produces a number that gives a feeling of rigor.

The case against, in order of weight:

1. **The fixture is structurally disqualified.** The brief was engineered against v1''s failure modes. Whatever number Stage A produces is a worst-case-shape floor, not a general acceptance rate. Translating thresholds does not fix the fixture problem. It compounds it by laundering the bias through a re-specified rule.
2. **The denominator mismatch is a *symptom*, not the disease.** The disease is that Stage A was designed against an imagined deck shape, not the actual brief. Patching the symptom leaves the disease.
3. **The decision tree collapses.** Every plausible outcome routes to Path D-soft. A measurement that does not discriminate between outcomes is not a measurement.
4. **The durable-artifact failure mode is worse, not better, after translation.** Future citations will drop the translation footnote first, the bias caveat second, and report the raw number as authoritative.
5. **Mario is time-boxed.** He asked "am I close to comparing yet?" The honest answer is "comparison is not the decision instrument; routing under Path D-soft and reading the rolling pilot is." Translating thresholds is more procedural shape on the critical path of a constrained week.

**The replacement for Stage A as the routing decision instrument:** the rolling production pilot already specified in `DECISIONS.md` lines 459-477. It runs WITHIN Path D-soft as the natural validation, triggered by the first 2 real FedEx/ACN production decks completing. It has a 3-week hard stop, pre-committed criteria, and is grounded in real client work — none of which Stage A had.

**Verdict on Q5:** Abandon Stage A. Commit Path D-soft today via the 30-minute commitment artifact in Q4. The rolling production pilot is the routing decision instrument. There is no third option that is not sunk-cost rationalization.

---

## Three-sentence verdict

**Abandon Stage A.** The denominator mismatch is the second structural disqualification of slidelab-intro as a Stage A fixture (the first was the regression-fixture brief bias I flagged previously), every plausible outcome of a translated-threshold Stage A routes to Path D-soft anyway, and the ~2 hours already spent on protocol setup are sunk cost that buys nothing the next hour does not also re-buy. Mario should spend the next 30 minutes writing `_decisions/path-d-soft-commit-2026-05-25.md` (decision, evidence base from the Category 2 smokes, rolling-pilot trigger after 2 real production decks per `DECISIONS.md` lines 459-477, reversibility clause, one-paragraph Stage A retirement note) — that is the commitment artifact, and the rolling production pilot is the actual routing decision instrument going forward.
