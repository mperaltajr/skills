# Post-Stage 4 Plan Review - Reviewer C (Scope Creep / Time-Budget Discipline)

**Date:** 2026-05-25
**Angle:** Is the work scope expanding past usefulness? Where is the time-budget actually sitting?
**Reviewer:** C (blind to A and B)

---

## Verdict on sequencing

**Coordinator wins on the narrow question, but both miss the real one.**

Audit-first vs. fix-first is a sequencing argument over a 1-hour window. Either way you re-fire Stage 4 once, either way you end up with a working REVIEW.html, either way Category 2 is still queued behind it. v2's "fix #4 first" buys ~15 minutes of momentum at the cost of possibly re-firing twice if the audit catches a 5th defect. Coordinator's "audit first" buys insurance against that re-fire at the cost of delaying the only defect we know is real.

The defensible answer is **audit first, but timebox it to 30 minutes**, because the audit is bounded - `compile_picks.py` is a small file with a small contract surface, and the prior contract audit in `smoke-test-finding-2026-05-25.md` (lines 124-139) already enumerated the contract checks v2 thinks about. Re-running that checklist against `compile_picks.py` is mechanical work, not investigative work. If it goes over 30 minutes, that itself is signal that something more structural is wrong and we should stop.

But this is a small fight. The real question is whether either path is even worth running.

---

## Verdict on defect 1 classification

**The reclassification from v0.1 to v0 is unearned and the architectural claim behind it is bigger than v2 has been making.**

The honest version of "slide 1 option A has zero brand color" is: *one of three sibling variants for slide 1 came out monochrome.* The user picks at REVIEW.html. Options B and C presumably carry brand color. So the failure mode being fixed is not "the user might ship a monochrome cover" - it's "the user might see a monochrome option in the picker and form a bad first impression of v2."

That's a real concern, but it's an A/B-perception concern, not a build-quality concern. Promoting it to v0 implies v2 must guarantee that **every variant** is shippable, not just that **the picker surfaces a shippable option**. That is a much stronger contract than DECISIONS.md describes. The whole point of three sibling options is to provide range - including range that some users will reject.

Once you accept "fix the worst possible variant," the scope has no natural stop. The next agent will produce a variant with a too-small title. Then a variant where the accent moment lands in the wrong place. Each one is "partner-facing first impression" by the same logic. v2 either ships with bounded variance across A/B/C and trusts the picker, or it ships with deterministic per-option quality guarantees and gives up variance. Coordinator is sliding toward the latter without naming it.

**Recommendation:** keep defect 1 at v0.1. Document it in REVIEW.html-side guidance ("if all three options have a quality issue, regen the slide"). Do not retrofit the architecture to prevent low-quality variants from existing.

---

## Time-budget reality check

Original estimate (DECISIONS.md line 16): **"~2 days of net-new work."** Build estimate table (lines 218-226): **~3 days.** Call the original budget **2-3 days.**

Where we actually are, by inference from the artifact set:

- **Build phase** (artifacts 1-6): consumed at least the budgeted 3 days, possibly more - the artifact-3 and artifact-5 reviews triggered scope additions (editorial-intent verbs, four-seed-per-slide change, per-client Mermaid theme generation) that weren't in the original estimate.
- **Pre-smoke review cycles** (smoke-readiness reviews A, B, C, plus the AB-timing review referenced in Reviewer C's smoke-readiness doc): another half-day at least.
- **Smoke test itself**: Stage 2 dispatch + Stage 3 fail + contract-audit + Stage 3 re-run + Stage 4 fail + this current plan-review cycle. The smoke-test-finding doc alone is ~300 lines of architectural analysis. Conservatively, another full day, probably more.
- **Now-proposed work**: audit + 4 fixes + re-fire + Category 2 smokes (trigger-brief, ACN, NFL, brief-fidelity) at ~2 hours estimated.

**Best-case actual budget at convergence hold: ~5 days. Likely: 6-7.**

That's 2-3x the original estimate. And the "~2 hours" Category 2 number is doubtful - the smoke-readiness reviews described it as 1 hour, and that was for *one* trigger brief plus an Accenture run plus an adjacency unit test. Adding NFL and explicit brief-fidelity measurement (which doesn't exist in the codebase per Reviewer A's grep at line 22) is real work, not "2 hours" work. **Honest Category 2: 3-5 hours. Honest total remaining: 4-6 hours before convergence hold.**

So the question is: at 2.5x the original budget already, is another half-day of pre-A/B work the right investment, or is it diminishing returns?

---

## Is the "shippable" goalpost shifting?

Yes. Demonstrably.

The smoke-test-finding doc declared v2 "empirically shippable for A/B testing" at line 294. Then Stage 4 fired and surfaced 4 new Category 1 defects. The pattern is identical to v1's: each layer of validation surfaces defects the prior layer missed, and each round we re-declare shippability against the new defect-free state.

There are three explanations and we need to pick one:

1. **The bar is too loose.** "Shippable" has meant "no known critical defects right now," which is a moving target as new gates surface new defects. We need a *measurable* end criterion - e.g., "shippable = passes a defined smoke matrix of N brief x M templates with zero Category 1 defects."

2. **The architecture has more gaps than estimated.** The 12-agent / 17-PNG validation that locked v2 (DECISIONS.md line 184) tested patterns in isolation, not the full pipeline end-to-end with REVIEW.html. The full-pipeline gates (Stage 3, Stage 4) are surfacing pipeline-level defects the pattern-level validation couldn't have caught. If this is the truth, then convergence is further away than the budget assumes.

3. **The smoke is doing its job.** Each new gate exposes things static review missed. This is good - it's why we ran the smoke - but it argues *against* the "we keep saying shippable" framing. The right framing is "shippable" was always premature and the smoke was the actual gate.

I think explanation 2 is partly true (pipeline-level defects #1 and #4 were not findable from the pattern-gallery validation) and explanation 1 is also true (we never defined a measurable shippable criterion). Both push toward the same conclusion: **the goalpost has been shifting because there was no goalpost.**

---

## Biggest concern

**The third option neither v2 nor the coordinator is naming: stop iterating, declare convergence hold AS-IS with documented known issues, let real A/B builds surface remaining problems.**

The case for this path:

1. **We have spent 2.5x the original budget already.** Every additional gate has surfaced more defects. There is no principled reason to believe the *next* gate will be the last one. Category 2 will surface Category 3. ACN smoke will surface multi-client defects v2 was never validated against.

2. **The Category 1 defects we know about are not symmetric in severity.** Defect #4 (path-contract bug) is a real blocker - REVIEW.html doesn't work. Fix it. The other three are documentation, classification, and one-variant quality issues. None of them prevent the user from picking a slide.

3. **Real A/B builds are the only test that will surface the defects that actually matter.** v2 is in a hall-of-mirrors with synthetic smokes catching synthetic defects. Mario's standing position (memory: "Be direct, not polite") would push hard against another cycle of pre-A/B fortification.

4. **The smoke test was supposed to *save* time vs. shipping cold.** It's now consuming more time than the original convergence estimate. If we keep going, we're past the point where the smoke is rational insurance - we're paying for certainty we can't get.

The pragmatic shape of "convergence hold AS-IS":

- Fix defect #4 (real blocker, required for REVIEW.html to function). 30 minutes.
- Re-fire Stage 4. 15 minutes.
- Document defects #1, #2, #3 in a known-issues note attached to v2. ~15 minutes.
- **Stop. Ship v2 to the next real FedEx deck.** Let actual user interaction surface defects #5, #6, #N - the ones we can't predict from synthetic smokes.

This is ~1 hour vs. the proposed 4-6 hours. The 3-5 hours saved buys back some of the budget overrun. The defects we'd surface in Category 2 smokes are defects v2 *also* needs to fix eventually, but they don't block first A/B against a FedEx brief, which is the only scenario the smoke has empirically validated v2 against anyway.

**The case against this path:** if v2 ships with a known monochrome-variant defect, the user's first impression of v2 is bad, and the A/B is biased against v2 from the start. That's the coordinator's implicit argument. It's real. But the rebuttal is that the user can see for themselves that B and C have brand color, and a 30-second conversation ("option A on slide 1 came out monochrome - known issue, regen if you want") preserves more A/B integrity than another half-day of fortification at 2.5x budget.

**My recommendation:** Path D-minus. Fix defect #4 only. Document the other three. Convergence hold AS-IS. Run smokes #2/#3/#4 *after* the first real A/B, not before. Let the data from real use replace the data from synthetic smokes.

If the team chooses to fix all four defects and re-fire, **timebox the total work at 2 hours including audit + fixes + Category 2.** If it goes over, that's the signal to drop to Path D-minus mid-stream.

---

## Three-sentence verdict summary

The coordinator's audit-first sequencing is marginally correct but both proposals duck the real question: v2 is at 2.5x the original budget already, defect 1's reclassification implies an architectural guarantee v2 has never claimed, and the "shippable" goalpost has shifted three times in this session because no measurable end criterion was ever set. The honest move is to fix only defect #4 (the real blocker), document the other three as known issues, and let real A/B builds surface what synthetic smokes cannot - anything more is paying for certainty we cannot buy. If the team rejects that and proceeds with audit + fixes + Category 2, timebox the entire remaining work to 2 hours and abort to the minimal path if it overruns.
