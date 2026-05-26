# Smoke-Readiness Review — Reviewer C (Strategic / Framing)

**Blind to:** Reviewers A and B.
**Angle:** What does this smoke actually prove, and is the convergence-hold framing the right next step?

---

## Verdict: SHIP WITH CAVEATS — but the caveat is "stop calling this a convergence hold."

The Stage 3 re-run cleanly proves a narrow slice of what v2 needs to prove. The coordinator's recommendation (green-light Stage 4, then convergence-hold until v1's `brand.yml` lands) is operationally fine but **strategically misframed**. "Convergence hold" implies v2 is finished and waiting; v2 is not finished — it is just finished with *this brief on this template*. Calling the hold what it is (a parking decision, not a completion milestone) matters because the next 2 days are exactly the window in which v2 *should* be exercising the architectural paths this smoke didn't touch.

Concrete recommendation: proceed to Stage 4 build_review.py. Do not enter "convergence hold." Instead, run a second smoke (different brief, different template) in parallel with v1's `brand.yml` work. The cost is one more dispatch; the upside is replacing two open architectural risks with empirical data before the A/B (or Path D) ships.

---

## What the smoke actually proved

Be exhaustive — this matters because the "v2 works" framing is overclaiming.

1. v2's parser handles the `### Slide N` brief format on a real consultant-authored brief.
2. v2's prep-time forecaster runs deterministically; same brief produces identical forecast across runs.
3. v2's 10-agent parallel fanout dispatches cleanly and 10/10 agents return PATTERN PICK metadata in the expected format.
4. The forecast-as-context-not-constraint design holds: agents override the forecaster correctly when brief signal is clear (slides 6 and 7 confirmed).
5. The seed-tiebreak mechanism is exercised at least once (slide 7 run 1) and produces deterministic, reproducible results given the seed.
6. The prompt.md to finalize_deck.py contract is now correct (after the sys.argv fix); 30/30 builds proves the contract is unambiguous for *this* brief's pattern set.
7. `finalize_deck.py`'s graft + theme + render pipeline works end-to-end against the FedEx template: 30/30 themed, 30/30 rendered.
8. The v1 `client_theme.py` loader produces canonical FedEx purple/orange on the FedEx Moving Forward template (empirical, not theoretical).
9. The QC self-check fires and surfaces the known cover-aware false-positive pattern (slide 1 all 3 options + slide 4/B BLOCK on PNG-size floor).
10. The post-pass adjacency check fires on slides 1-2-3-4 (4 consecutive Full canvas) and surfaces it as a soft advisory rather than halting the build.
11. Agent pattern-pick has bounded non-determinism: 8/10 slides identical across runs; 2/10 (slides 7 and 10) diverged onto patterns both eligible per `layouts.md`.
12. `validate_theme()` does not halt on FedEx (the failure mode it defends against — Accenture-default-bleed — is empirically absent here).
13. The directive-verb vocabulary covers 5 of 7 verbs on this brief; the 2 unexercised verbs (`warn`, `show urgency`) are brief-shape gaps, not architecture gaps.

That is a real list. But notice: **every item is about the happy path on a single brief that does not stress the interesting failure modes.**

---

## What the smoke did NOT prove

This is the section that should drive the next step.

1. **Hardline #4 (brief fidelity >= 0.92) was never measured.** No item in RESULT.md reports a brief-fidelity score per slide. The smoke proved builds happen; it did not prove builds *honor the brief*. Fabrication-resistance is one of v2's two headline claims (the other being twin-bug resistance). Untested.
2. **SKELETON_REJECTED never fired.** Zero rejections across 30 options x 2 runs. This brief gave the agents no reason to reject (no 4-cell-into-2-item mismatch, no ambiguous editorial intent, no fishbone/concentric request). The protocol's existence is asserted but not exercised. **A v2 smoke that never trips its own halt mechanism has not validated that mechanism.**
3. **FALLBACK_MERMAID never fired.** Zero fallbacks. The Mermaid render to PNG to embed to theme path is documented in `fallback.md` and pseudocoded in `finalize_deck.py`, but the smoke executed exactly none of it. This is the second-largest untested code path in v2.
4. **Multi-client.** v2 has been exercised against FedEx only. ACN and NFL templates may hit `validate_theme()` halts, slot-mapping differences in `client_theme.py`, font-substitution issues, or Mermaid theme generation gaps. Whether v2 *runs* against a non-FedEx template is an open empirical question.
5. **Cross-deck generalization.** One brief is one brief. The forecaster vocab, the directive-verb vocab, and the 14-pattern set were calibrated against slidelab-intro's shape. A different brief (KPI scorecard heavy, decision-tree heavy, swimlane heavy) might expose vocab gaps that look just like v1's chassis-vocab failure mode at a smaller scale.
6. **Adjacency-context staleness as a real-user problem.** Slides 1-2-3-4 surfaced as an advisory. The smoke did not test whether *Mario* would tolerate that advisory in REVIEW.html or whether he would treat it as a build failure. The architecture's "defer to user judgment" answer is untested at the user-judgment layer.
7. **`BRAND_PRIMARY_MID` semantic drift.** Confirmed non-deterministic — it surfaced in run 1, did not in run 2. The smoke proved the drift is real *and* that it depends on token-choice variance. It did not prove the drift is bounded or that it does not surface as a critical regression on a different brief.

---

## Strategic question — convergence hold vs additional smoke

The convergence-hold framing assumes v2's next blocker is v1. That assumption is wrong on the data.

**v1's `brand.yml` rewrite does not change anything in items 1-7 above.** The brief-fidelity check, SKELETON_REJECTED, FALLBACK_MERMAID, multi-client run-or-halt behavior, and cross-deck generalization are all v2-internal architectural paths that v1's loader work cannot validate or invalidate. Waiting on v1 is waiting on the wrong dependency for those gaps.

Concretely, the next 2 days could productively exercise:

- **Smoke #2 on a fabrication-trap brief.** A short brief with one slide that says "2 paths" but where the forecaster might reach for a 4-cell pattern. Exercises Hardline #4 + SKELETON_REJECTED.
- **Smoke #3 on a Mermaid-required brief.** A 3-slide brief with a hub-spoke and an ecosystem map. Exercises FALLBACK_MERMAID end-to-end.
- **Smoke #4 on a non-FedEx template.** Pick ACN or NFL. The interesting test is whether v2 even *runs* — `validate_theme()` may halt and we would learn that before the A/B, not during it.

Each is roughly an hour of dispatch. None require v1's `brand.yml` to be done first. **The cost of running them is much lower than the cost of entering the A/B with three large architectural unknowns.**

---

## Is the A/B still the right next step, or is Path D back on the table?

Path D is more defensible after this smoke, not less.

The smoke confirms the strategic argument from `ab-timing-review-C.md`: slidelab-intro is a brief v2 was architected against. v2 built cleanly. v1 on the same brief will produce some output, and one of them will look better, but the comparison is structurally rigged. **The smoke did not produce any data that would update toward "A/B is the right test."** It produced data that should update toward "the interesting tests are the ones the smoke did not run."

But the FedEx-loader finding is a real argument *against* Path D for the moment. The smoke proved that `validate_theme()`'s belt-and-braces works for the FedEx case — but that is the *least interesting* test of the loader. The whole reason v1's loader is getting rewritten is that the slot-mapping bug leaks Accenture default colors into non-Accenture decks. The smoke proved "FedEx works" — which was never in serious doubt. The interesting loader test is ACN or NFL, and v2 inherits whatever v1 ships. Path D ("ship v2 as default for next real deck") only works cleanly if the next real deck is FedEx. If it is anything else, v2 inherits v1's loader risk and Path D becomes "ship v2 with a known transitive risk on non-FedEx templates."

**Revised Path D:** ship v2 as default for the next FedEx deck. Run smokes #2/#3/#4 in the meantime. Defer the multi-client commit to v2 until either v1's `brand.yml` lands or smoke #4 proves v2 runs cleanly against a non-FedEx template.

The A/B remains performance theater. The smoke did not change that.

---

## Biggest concern

**Non-determinism is being accepted as "architectural feature" before it has been measured at scale.**

The Option-2 recommendation in `smoke-test-finding-2026-05-25.md` reads reasonably for a 10-slide brief with 2 divergences. But the strategic implication was not followed through. If v2 produces deck X on one run and deck Y on the next, then any A/B against v1 is comparing *deterministic v1* to *one sample of stochastic v2*. The natural human bias is to pick the better v2 sample after the fact, which biases the A/B toward v2. That looks like good news for v2 but is actually a methodological hole: we would be inferring v2 wins from a biased comparison protocol.

Two options to close this:

1. **Make v2 deterministic** at A/B time (temperature=0, or commit to a fixed seed protocol). Cleaner comparison, but reduces variant diversity — possibly degrades the per-slide REVIEW.html option set.
2. **Run v2 multiple times** and define a representative sample protocol upfront. Honest, but expensive.

Neither has been chosen. The current de facto answer is "accept the variance, the user picks at REVIEW.html, and the A/B will be informal anyway." That is fine for an informal A/B and untenable for a formal one. **If the A/B is going to drive a deprecation decision on v1, the comparison protocol has to be defined before the data is collected, not after.**

Secondary concern: the coordinator's "convergence hold" framing is the kind of language that solidifies into a project assumption. Two weeks from now, "v2 was held pending v1" reads as "v2 was finished." It was not. Call the hold a parking decision, document the three untested paths explicitly, and put smokes #2/#3/#4 on the calendar before the language hardens.
