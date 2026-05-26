# Stage A Protocol Review — Reviewer A (protocol design / numeric discipline)

**Status:** committee · Reviewer A of 3
**Angle:** lock specific numbers; refuse to lock numbers I do not have the data to lock
**Date:** 2026-05-25
**Inputs:** `ab-methodology-review-{A,B,C}.md`, `DECISIONS.md` §"Replacement: two-stage gate" (lines 420-453), `slidelab-intro-shippable.md` (10 slides)

---

## TL;DR — the locked Stage A protocol

| Parameter | Locked value | Rationale |
|---|---|---|
| v1 runs of slidelab-intro | **1** | v1 is md5-seeded deterministic; a second run produces the same artifacts. The variance Reviewer B's prior worried about is v2's stochasticity, not v1's. |
| Scoring methodology | **Per-slide binary: "would I ship this to a partner tomorrow, yes/no" + one-line reason** | Same shape as the original 23% measurement (curator first-pass-reject). No 5-point Likert. No multi-dim. |
| Scorer | **Mario, in a structured single sitting, with the pre-commitment artifact described in §"Failure mode" below** | Bias is real; the answer is forensic constraint, not a fictional independent scorer. |
| "Materially better than 23%" | **>= 60% accept (6/10 slides) -> cancel Stage B and go Path D-soft. <= 40% accept (<= 4/10) -> Stage B fires. 50% (5/10) -> structured tiebreaker (see "The 50% case")** | 60% is what DECISIONS.md line 427 already pre-committed to. I am not moving it. |
| Hard stop | **5 Mario-hours total, 7 calendar days from kickoff, whichever comes first** | Below. |
| Apples-to-apples to 23%? | **No, and we should stop pretending otherwise.** The number we are producing is `v1-NOW-slidelab-intro-acceptance`, not a re-measurement of the 23% corpus. See §"On the apples-to-apples question." |

---

## 1. How many v1 runs?

**One.**

v1 is md5-seeded deterministic rotation. Re-running v1 on the same brief with the same template produces the same pattern picks; the only variation is downstream agent prose drift, which is sub-slide-quality noise and does not flip an acceptance call. Running v1 three times burns ~30 minutes of compute and ~30 minutes of Mario re-scoring for zero new information.

The k=3 v2 / k=1 v1 asymmetry from the earlier methodology debate exists to control for *v2's* documented stochasticity (the 2026-05-26 9/10 cross-client agreement directly measured a 1-in-10 pick-divergence rate on v2). Stage A is v1-only. The asymmetry doesn't apply.

If Mario suspects determinism has regressed (e.g., a recent reader-side fix changed the seed surface), spot-check by running a second pass on slides 5/6/9 only (the three slides flagged as `SHIPPABLE` in the earlier 5-agent simpler-arch test per DECISIONS.md line 178). That's a 3-slide verification, not a full second run.

---

## 2. Scoring methodology

**Per-slide binary accept/reject + one-line reason. 10 slides -> 10 yes/no calls -> one acceptance percentage.**

This mirrors the original 23% measurement (per DECISIONS.md: "the first curator pass rejected 77% of agent chassis proposals" — that is a binary first-pass-reject rate, not a Likert). Matching the metric shape is the only way the Stage A number means anything when compared to 23%.

**What "accept" means, locked before Mario opens the PNG:**

> *"Could I send this slide to a partner-level reviewer tomorrow with no edits I'd be embarrassed to skip? If I would touch the slide before sending, it is a reject."*

That sentence is the gate. It is the same gate the 23% measurement implicitly used (curator first-pass-reject = "would not ship as-is"). Anything looser ("good enough with light edits", "directionally right") inflates acceptance and produces a misleading Stage A number.

**One-line reason required on every slide, accept OR reject.** This forces Mario to articulate *why* before the running tally biases the next call. The reasons become the failure-mode log feeding Stage B's bucket question if Stage B fires.

**Blinding: not feasible and not necessary.** v1 outputs are visually distinguishable from v2 outputs even at PNG-thumbnail level (chassis labels, accent-bar discipline, layout fingerprints). Pretending to blind would be theater. Instead, the bias mitigation is the pre-commitment artifact in §"Failure mode."

**No deck-level coherence vote at Stage A.** Stage A is a single brief through a single pipeline; coherence is a Stage B question. Adding it here is scope creep.

---

## 3. Who scores?

**Mario. Alone. In one sitting.**

The prompt rules out an independent scorer. The honest accommodation is to constrain Mario's scoring procedurally, not pretend the bias isn't there. The pre-commitment artifact in §"Failure mode" is the load-bearing piece.

Two things to NOT do:
- **Don't have Mario re-score on day 2 "to confirm."** Re-scoring drifts toward whatever conclusion the day-1 reflection produced. The day-1 call is the call.
- **Don't have v2 score v2's competitor.** A separate Claude session reviewing v1's output is not an independent scorer — it's a parrot of the prompt that framed it. Anyone proposing this is solving for the appearance of independence, not the substance.

---

## 4. What does "materially better than 23%" mean numerically?

DECISIONS.md line 427 already locked **>= 60% (>= 6/10 slides accepted) = gap closed, Path D-soft, A/B cancelled permanently.**

I am holding that number. It is what the prior committee pre-committed to and re-litigating it now is exactly the goalpost-shift Reviewer A's methodology review (myself, prior round) flagged.

The full decision table for Stage A:

| v1-NOW acceptance on slidelab-intro | Verdict |
|---|---|
| **>= 7/10 (70%+)** | Gap not just closed — v1 has *passed* v2 on its own training corpus. Path D-soft, plus Mario should re-read the v0.1 backlog to see what assumed v1 was broken. |
| **6/10 (60%)** | Threshold met. Path D-soft. Stage B cancelled. |
| **5/10 (50%)** | Ambiguous. See "The 50% case." |
| **4/10 (40%)** | Gap narrowed but not closed. Stage B fires. |
| **<= 3/10 (<= 30%)** | Gap persists at original magnitude. Stage B fires; Reviewer B's "v2 capability surface" measurements become primary. |

### The 50% case

5/10 is the one outcome where pre-committed rules give no answer and where Mario will be most tempted to round. The structured tiebreaker:

1. **Which 5 rejected?** If the 5 rejected slides include any of the three slides v2's architecture was *specifically* designed to fix (slides 5, 6, 9 per DECISIONS.md line 178 — twin bug + fabrication bug fixtures), the gap is in the exact place v2 exists to solve -> **Stage B fires.**
2. **If the 5 rejected are random across the brief**, v1's failures are non-architectural (prose drift, theme polish, sizing) -> **Path D-soft.** The gap is real but doesn't justify a parallel architecture.

This is the only place I'm adding a sub-criterion. Everywhere else, the number is the number.

---

## 5. Hard stop on Stage A

**5 Mario-hours total. 7 calendar days from kickoff. Whichever comes first.**

Breakdown:
- v1 chat: build slidelab-intro through current v1 (theme rewrite + path fixes + Phase 3 color correction + brand.yml sidecar all applied). Mario time: **~1.5 hours** (kick the build, monitor for failures, regenerate any slide that needs rerun, finalize). Most of this is wall-clock waiting, not active Mario attention.
- Scoring: 10 slides x ~5 min/slide (open PNG, read brief content for that slide, accept/reject + reason) = **~1 hour focused attention**.
- Pre-commitment artifact + write-up: **~1 hour** (see "Failure mode" for the artifact).
- Slack for the unexpected: **~1.5 hours**.

If Stage A is not complete in 5 hours or 7 days, **default to Stage B firing**. The hard-stop default is the *conservative* branch (run more, don't auto-Path-D) because an undermeasured "gap closed" call irreversibly retires v2 effort.

This is tight. It is tight on purpose. The Reviewer A timing-review concern from a prior committee was that Stage A's calendar cost would balloon and consume the v0.1 window. 5 hours / 7 days is the upper bound at which Stage A is still cheaper than Stage B.

---

## 6. Biggest failure mode + specific mitigation

**Failure mode: Mario looks at slide 1, has a directional feeling about the deck ("this is better than I remembered" or "this still feels off"), and that feeling sets the acceptance rate for slides 2-10. The Stage A number then encodes Mario's gestalt judgment, not 10 independent calls.**

This is the failure mode most likely to produce a number that *looks* clean but is actually anchored. It would not be visible in the artifact. It would corrupt the most important downstream decision in the project.

**Specific mitigation — the pre-commitment artifact, locked before any PNG is opened:**

Before Mario opens a single Stage A PNG, he writes a short markdown file (`stage-a-precommit.md`) containing:

1. **Per-slide expectation** (one line each, 10 lines total): *"For slide N, the v1-NOW pipeline is likely to fail / pass because ____."* Mario commits a per-slide prediction. This forces him to enumerate his priors before observing the outcome.
2. **The blanket gate restated verbatim**: *"Accept = could ship to a partner tomorrow with no edits I'd be embarrassed to skip."*
3. **The acceptance threshold restated verbatim**: *">= 6/10 = Path D-soft, <= 4/10 = Stage B, 5/10 = use the structured tiebreaker on slides 5/6/9."*
4. **The post-scoring calibration check**: after scoring, count how many of Mario's per-slide predictions matched the outcome. If prediction-vs-outcome agreement is >= 8/10, his priors were well-calibrated and the acceptance number is trustworthy. If <= 5/10, his priors were inverted and *the scoring data is suspect* — the right move is to flag Stage A as inconclusive and default to Stage B firing.

The artifact is cheap (~30 minutes). It is the closest thing to forensic bias control available without an independent scorer.

The second-order mitigation: **Mario scores in PNG-only mode first** (read brief slide; look at PNG; accept/reject; write reason). He does NOT open the YAML, the chassis label, the agent reasoning trace, or the build log on the first pass. Those are post-hoc forensics, not scoring inputs. Looking at the metadata before deciding contaminates the call with the system's self-narrative.

---

## On the apples-to-apples question (because the prompt asked)

**Comparing slidelab-intro % to 23% is NOT apples-to-apples. The number we produce is not "v1-NOW curator acceptance." It is "v1-NOW slidelab-intro acceptance by Mario, single scorer, single deck, n=10 slides."**

Three confounds:

1. **Corpus size.** The 23% was on a much larger corpus (per the prompt). slidelab-intro is 10 slides. The variance on a 10-slide measurement is large enough that the difference between 5/10 and 6/10 is one slide's judgment call. The 23% had statistical mass; Stage A does not.
2. **Corpus bias.** slidelab-intro was authored after v2's design vocabulary stabilized (per Reviewer C's prior, DECISIONS.md line 414). The brief is structurally favorable to v2 patterns and may be either favorable OR unfavorable to v1 chassis depending on which slide. The 23% corpus had no such bias — it was the real-deck mix that originally surfaced the failure mode.
3. **Scorer.** The 23% was a curator pass (multiple unnamed curators, per the methodology trace in DECISIONS.md). Stage A is one self-interested scorer. Even with the pre-commitment artifact, this is structurally different.

**What Stage A's number actually tells us:** whether v1-NOW can ship *this specific brief* at partner quality. That is a real signal — it just isn't the same signal as the 23%. The right framing for the verdict write-up:

> *"v1-NOW achieves X/10 acceptance on slidelab-intro. The historical 23% measurement was on a different, larger corpus; this number is not directly comparable. However, >= 6/10 on this brief — which was authored against v2's design vocabulary — is a strong indicator that v1-NOW's failure modes have shifted sufficiently that the original-corpus 23% is unlikely to still hold. The inference 'gap closed' is defensible at >= 6/10; it is an inference, not a re-measurement."*

That paragraph belongs in the Stage A write-up. It is the truthful framing. Anything that says "v1-NOW is at X% which is materially better than 23%" without that caveat is overselling the measurement.

**What additional data would unlock real apples-to-apples?** Re-running the original 23% methodology on a corpus comparable to the original (i.e., the multi-deck FedEx + ACN + NFL real-work mix that produced the 77% reject rate). That is multi-week, multi-deck, and is exactly the cost Stage B was designed to avoid. So: we do not get apples-to-apples in Stage A. We get a defensible inference. Name it as an inference.

---

## What I am NOT locking, and why

- **Whether Mario does Stage A at all this week.** That's a scheduling call against FedEx OTC load, not a protocol call. The protocol is ready when Mario is.
- **Whether the v1 chat is the same v1 chat that runs v1 in production.** I'm assuming yes; if there's drift between Mario's v1 chat and the production v1 codebase, the Stage A number measures the wrong thing. Worth a 60-second sanity check before kickoff.
- **The exact contents of the pre-commitment artifact.** Sketched above; Mario refines on first use.

---

## Three-sentence verdict

**Stage A locks: 1 v1 run (v1 is deterministic), per-slide binary accept/reject mirroring the 23% curator gate, >= 6/10 acceptance triggers Path D-soft and permanently cancels the A/B (per DECISIONS.md line 427), <= 4/10 fires Stage B, 5/10 resolves via a structured tiebreaker on whether slides 5/6/9 (the architectural fixtures) are in the rejected set; hard stop is 5 Mario-hours / 7 calendar days, default-on-timeout is "Stage B fires." The single highest-risk failure mode is Mario's first-slide gestalt anchoring all 10 calls — mitigated by a pre-commitment artifact (per-slide priors written before any PNG opens, plus post-scoring calibration check that flags Stage A inconclusive if Mario's priors disagree with his outcomes on >= 5/10 slides). Comparing the Stage A number to the historical 23% is NOT apples-to-apples (smaller corpus, biased brief, single scorer vs curator panel), so the verdict write-up must frame >= 6/10 as a *defensible inference that the 23% gap has closed*, not as a re-measurement of the 23%.
