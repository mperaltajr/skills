# A/B Methodology Review — Reviewer A (empirical / data-quality)

**Status:** blind review · Reviewer A of 3
**Angle:** which protocol produces a defensible consolidation decision
**Date:** 2026-05-25

---

## Verdict (the actual methodology)

**Protocol: 3 briefs × 2 clients × k=3 v2 runs + k=1 v1 run, blinded per-slide scoring with a tiebreaker rule and a pre-committed numeric decision criterion.**

Concretely, what Mario executes tomorrow:

### Brief set (locked before any build)
1. **slidelab-intro** — regression floor. v2 was architected against this. If v2 *loses* here, the architecture itself is broken and the A/B is moot. (Acts as a sanity gate, not a vote.)
2. **A real OTC Reboot brief** (FedEx engagement, per memory — Mario has a rolling findings log). 10–14 slides, argument-arc shape. This is the brief v2 was NOT designed for and where the real signal lives.
3. **A dense PMO/KPI brief** — 6–8 slides, scorecard-heavy, low argument, high data. Tests v2 weakest pattern class (dense grids, tables) and v1 strongest (where the 19-chassis vocabulary was richest).

Three briefs is the minimum for the consolidation call per DECISIONS.md line 246 and my prior timing review. Fewer means Mario second-guesses. More wastes time without changing the verdict — the marginal information from brief #4 will not flip a 3-brief consensus.

### Client matrix
- **FedEx for all 3 briefs.** Primary signal.
- **ACN for brief #2 only** (the OTC-shaped brief, rebranded). One ACN cell, not three. The cross-client 9/10 agreement from 2026-05-26 already established that client identity does not drive picks; we only need one ACN cell as a brand-fidelity check, not three for statistical strength. Doubling the matrix to 6 cells doubles cost without doubling info.

Total cells: 4 (FedEx × {brief 1, 2, 3} + ACN × brief 2).

### Runs per cell
- **v2: k=3 per cell.** v2 is stochastic. Three runs collapse the dice-roll asymmetry and let Mario see the *distribution* of v2 outputs, not a single sample. The 2026-05-26 smoke confirmed bounded non-determinism is real (slides 7 and 10 shifted between runs) and within-eligibility-set.
- **v1: k=1 per cell.** v1 is deterministic (md5-seeded rotation). One run is the answer it would produce in production.

Total decks built: 4 cells × (3 v2 + 1 v1) = **16 decks**.

### Scoring (blinded, per-slide)

REVIEW.html shows for each slide: 4 panels labeled Option W / X / Y / Z (the three v2 variants and the one v1 variant, randomly assigned to letters per slide so Mario cannot learn the position convention). Mario picks **one winner per slide** on a single dimension: "if I had to ship one of these to a client tomorrow, which one." No multi-dimensional scoring. Multi-dim scoring sounds rigorous and produces uninterpretable ties -- one prefers visual quality, the other brief fidelity, and the conjoint vote is noise.

A second pass, *after* the per-slide picks are locked, asks Mario one deck-level question per cell: **"which side felt more coherent across the deck?"** Single answer: v1, v2, or tie. This catches narrative-arc effects per-slide picking misses.

**The unblinding happens after both passes are complete and recorded.** No going back to revise.

### Decision criterion (numeric, pre-committed)

Let `W2` = number of slides v2 won across all 4 cells (each slide is one vote -- sum of v2-variant wins). Let `W1` = number v1 won. Ties go uncounted. Total slide votes across the 4 cells approx 38-46 slides depending on brief lengths; call it `N approx 40`.

- **v2 wins >= 60% (W2 >= 0.60 * N) AND v2 wins or ties the deck-level coherence on >= 3 of 4 cells -> consolidate to v2.** Deprecate v1 chassis path on a 30-day clock, migrate v0.1 work to v2.
- **v1 wins >= 60% AND v1 wins or ties coherence on >= 3 of 4 cells -> retire v2.** Abandon `slide-builder-simple/`, commit fully to v1 hardening plan.
- **Anything else -> split routing.** Tabulate which slide types each won (cover, anchor, KPI grid, swimlane, narrative compare, etc.). If a pattern emerges (v1 wins KPI grids 5/5, v2 wins narrative slides 12/14), encode it as a classifier in `storyline-helper` and ship both. If no pattern emerges, default to v2 (it is the simpler architecture and the cheaper to maintain) and keep v1 alive only for the fishbone/concentric-rings cases v2 explicitly defers per DECISIONS.md line 67.

60% is the threshold because 50% is coin-flip noise on `N=40` and 70% requires v2 to dominate so completely that the empirical data already-in-hand would have predicted it (it does not -- the 9/10 cross-client run is on v2-vs-v2, not v2-vs-v1). 60% is the smallest number that produces a defensible "X clearly wins" statement on this sample size.

### Stop condition (the explicit one)

The A/B is **DONE** the moment the 16 decks are built and the two scoring passes are complete. The decision is made the same week. **There is no "let us run one more brief to be sure."** If after 16 decks Mario wants more data, that is evidence the criterion was wrong, not that the data was insufficient -- and the right response is to re-examine the criterion, not to keep running briefs.

Hard date: **3 calendar weeks from kickoff.** Past that, the A/B is declared inconclusive, default to v2 routing per the "anything else" branch, and move on.

---

## Why this protocol vs alternatives

### On slidelab-intro bias
Reviewer C is right that slidelab-intro was engineered around v1 failures. That is why it is a **regression floor, not a vote** in this protocol. If v2 loses on slidelab-intro, we do not need the other two briefs -- the architecture has regressed against its own training corpus and that is the headline. If v2 wins on slidelab-intro, the OTC and PMO briefs are what actually decide consolidation. Using slidelab-intro as a sanity gate rather than evidence removes its bias from the consolidation call.

### On stochastic-vs-deterministic asymmetry
k=3 v2 vs k=1 v1 is the asymmetric-but-fair protocol. v1 deterministic single answer IS its production output -- running v1 three times produces the same deck three times. v2 three runs let Mario see the variance and pick from the distribution, which is also what production users would do (they would run it once, see REVIEW.html, and either accept or rerun). Giving v2 three rolls and v1 one is not handicapping v1 -- it is mirroring how each architecture actually ships.

The alternative (v2 k=1) bakes in a 30-40% chance v2 gets a bad roll on a boundary slide and loses for a sampling reason. That is exactly the bias my prior timing review flagged.

### On goalpost-shifting
The decision criterion is pre-committed numerically and the stop condition is hard-dated. The only way to shift the goalposts is to amend this document before scoring begins, with a written rationale, signed by Mario. That is the same anti-pattern v1 lever-stack produced and the discipline v2 hardline rules exist to enforce -- apply it to the meta-decision too.

If the data comes in ambiguous (e.g., v2 wins 58%, just under threshold), the protocol says split-route. It does NOT say run brief #4. Resist that.

### On Reviewer C Path D ("ship v2 as default, skip A/B")
Path D was defensible when v2 had not been smoke-tested. It is less defensible now -- v2 is shippable, both clients work, and the marginal cost of running 16 decks is about 3 days of Mario calendar time vs. an indefinite parallel-maintenance tax if we ship v2 and find later it loses on KPI scorecards. The A/B is cheap insurance against an irreversible commitment. The honest objection to Path D is exactly the v1 lever-stack failure mode at the meta-level: shipping v2 because we like it, not because we measured it.

But Reviewer C underlying concern -- that "keep both" is a face-saving deferral -- is real, and this protocol addresses it: there is no "keep both as parallel skills" outcome. The split-route outcome encodes routing as a classifier, which is a real architectural decision, not a deferral.

---

## Cost estimate

**Wall-clock:**
- 16 decks x ~12 min build (per smoke-test-finding data, v2 build is ~10 min, v1 is ~15 min; average 12) = ~3.2 hours of compute, parallelizable down to ~1 hour if dispatched in batches of 4.
- Scoring: ~4 min per slide x 40 slides = 2.7 hours of focused Mario time. Plus 4 deck-level reads x 8 min = 32 min. Total Mario time: **~3.2 hours**, ideally split across 2 sessions.
- Brief prep for the OTC and PMO briefs: 1.5 hours if Mario reuses existing OTC findings log content, 3 hours if writing fresh PMO brief from scratch. Call it **2 hours**.

**Total Mario calendar time: ~5-6 hours over 1 week.**
**Total wall-clock from kickoff to consolidation decision: 1-2 weeks** (build time is small; gating factor is finding 2 contiguous Mario scoring sessions).

This is honest. It is not "2 days." Reviewer C prior worry about 2-day delays compounding was right to flag, but the answer is to bound the cost explicitly (5-6 hours, 3-week hard deadline), not to skip the measurement.

---

## Biggest concern

**Mario scoring fatigue at slide 30+.** 40 slides of blinded 4-panel comparison is a lot to hold attention through. By slide 35, the picks degrade toward "whichever option I see first" or "whichever has more orange in it." This is the single failure mode that would corrupt the data the most and would be invisible -- it produces a number, just the wrong number.

Mitigations:
1. **Split scoring across 2 sessions**, not one. First session: cells 1+2 (~20 slides). Second session, different day: cells 3+4. Force a context break.
2. **Insert 3 calibration slides** mid-scoring per session: known-bad PNG vs known-good PNG, both v1, both v2. If Mario picks on calibration slides drift across the session, his judgment is fatigued and that session data is suspect. Cheap insurance, ~2 min of Mario time.
3. **Score deck-coherence FIRST, per-slide SECOND.** Reverse the natural order. Deck-coherence is fresh-eye judgment; per-slide picking is the grind. If we score deck-coherence after the per-slide grind, the coherence judgment is contaminated by the slide-level fight Mario just had.

The thing I am least confident about: whether the 60% threshold is correctly calibrated. It is defensible on paper but it is a single number applied to a small sample. If after the first two cells v2 is sitting at 55% and v1 at 45%, the remaining two cells become high-leverage and the temptation to look at the running tally and adjust the threshold will be strong. Resist it. The threshold is locked.

---

## Critical

The protocol above is what I would actually run. Two things I would push back on if the coordinator framing softens them:

1. **No "let us see how the first brief goes before deciding the rest."** That is the lazy-defer pattern. All 4 cells, all 16 builds, all the scoring -- or no A/B. Half-A/B produces worse data than no A/B because it gives the illusion of measurement.
2. **No multi-dimensional scoring.** "Brand fidelity 7/10, visual quality 6/10, brief fidelity 8/10" is uninterpretable across 40 slides and gives infinite room to retroactively weight dimensions toward a preferred outcome. One pick per slide. One coherence call per deck. Done.

The decision criterion lives or dies on those two disciplines.

---

**Summary:** Run 3 briefs x 2 clients x (k=3 v2 + k=1 v1) = 16 decks. Blinded per-slide picks plus deck-level coherence. 60% threshold for clear win; otherwise split-route by slide type. 3-week hard stop. ~5-6 hours of Mario calendar time.