# A/B Timing Review — Reviewer B (Operational / Risk angle)

**Status:** review · Reviewer B · blind to A and C
**Coordinator recommendation under review:** Path B (wait ~2 days for v1's theme rewrite).
**My angle:** which path minimizes downstream rework and operational risk, including risks the data-quality frame misses.

---

## Verdict: **OTHER — Path A-minus (run A/B now, but explicitly framed as a v2 smoke test, not as the comparative datapoint)**

The coordinator's framing assumes the first A/B is a *judgment moment* — that Mario will look at v1 vs v2 outputs and form a real opinion. That framing is wrong, and it's what makes Path B look attractive. The first run of v2 against a real brief, with v1's current loader bug present, is operationally a **smoke test of v2's own end-to-end path** — not a comparative judgment. Treating it as the latter inflates the cost of "bug-tainted data" because the data was never going to be load-bearing. Treating it as the former (smoke test) makes the bug irrelevant: we're not measuring v1's quality, we're measuring whether v2 runs at all on a real brief.

Path A as the coordinator framed it ("A/B now, data is bug-tainted") is wrong because it accepts the comparative framing. Path A-minus is the correct move: run v2 now against the real brief, render PNGs, eyeball v2's output in isolation, do not even bother building v1 in parallel this round. Then run the proper A/B after v1's `brand.yml` work lands. This is **not** Path C — Path C runs the *full comparative A/B twice*. Path A-minus runs a v2-only smoke now plus one proper A/B later. Half the wall-clock of C, more signal than B.

---

## Reasoning (risk + operational angle)

### What the coordinator's Path B is actually optimizing for

Clean data on a fair fight. Defensible methodology. The frame is "we are running an experiment; experiments need clean baselines." That is the right frame *for the comparative decision*. It is the wrong frame for the *next two days*, because during those two days v2 is sitting unexecuted against a real brief for the first time ever.

### The risk Path B walks into that nobody is naming

**Latent v2 bugs that only surface against a real brief, discovered on day 3 instead of day 1.** build-deck-review.md flagged three Criticals and several Majors in `build_deck.py` *that were caught by static review alone*. Static review caught issue #1 (regex misses `### Slide N` — every real brief exits code 2). The reviewer was reading code; they were not running it. What is the over/under that there are 2–5 more bugs of similar severity that only surface when v2 actually consumes a real brief end-to-end and dispatches workers? My estimate: high. The patches landed since that review address the static-caught issues, but they don't address the class of "wrong on contact with real data."

If v2 has another exit-2-class bug, Path B means we discover it on day 3, after the v1 rewrite has consumed its 2 days of attention. The v1 team has moved on, momentum is on v1's side, and v2's first real run still hasn't happened. Path A-minus discovers those bugs *today*, in parallel with the v1 rewrite, so by day 3 both sides are ready for a clean A/B.

### The three-question rework cost matrix

**If Path A is wrong** (decisions made on bug-tainted data → rework decisions later): low. The "decision" being made here is not "ship v2, retire v1." It's "is v2 architecturally sane on a real brief." That decision survives the v1 loader bug because v1's loader bug doesn't affect v2's output — the bug affects v1's output. Bug-tainted v1 PNGs do not contaminate the assessment of v2 PNGs unless Mario is forced to pick a winner per slide, which is the part we'd defer.

**If Path B is wrong** (waiting was unnecessary): cost is roughly 2 days of v2 idle time *plus* the risk that v1's rewrite takes 3–4 days (see below), *plus* the risk that v2 bugs discovered post-wait push the first real A/B to day 5–7. Compounding delay.

**If Path C is wrong** (deltas uninformative): doubled effort for both v2 build-out and Mario's review time. Mario reviewing two A/B passes is expensive; he has already spent two months on the chassis-vocab path that didn't work out. Burning his attention on a baseline run that produces no actionable signal is a real cost.

### Risks the coordinator and the data-quality frame both miss

1. **Momentum loss during a 2-day wait.** v2 just finished artifact 6 with a regression harness. The chat has high context, the architecture is fresh, the patches just landed. Two days of waiting is two days of context decay. When v2 resumes, the operator (Mario or his agent fleet) has to re-page in v2's architecture before running the first real build. Context re-loading is non-zero cost.

2. **Sunk-cost commitment if v2 ships into a half-built state.** If we wait for v1's rewrite, v1 will be in a *clean* state and v2 will be in its *current* state (untested against a real brief). The comparison is now v1-clean vs v2-untested. A bad first impression of v2 in that comparison is sticky — Mario will be tempted to conclude v2's architecture is wrong when the real cause was a latent v2 bug we never had time to surface. Path B *increases* this risk because it skips the smoke-test step.

3. **Integration bugs that only surface when both rewrites are live together.** v1's `brand.yml` work changes the canonical theme format. v2's `build_deck.py::generate_mermaid_theme()` and `validate_theme()` both read `template.json` today and have follow-on work documented in DECISIONS.md when `brand.yml` lands. If we wait for v1 *and* land v2's follow-on changes *and then* run the first A/B, we are debugging two rewrites' interaction simultaneously. Smoke-testing v2 against the *current* `template.json` path first means when `brand.yml` lands, we know exactly which v2 behavior changed because of the new theme source vs which behavior was already broken.

4. **What if v1's rewrite takes 3–4 days instead of 2?** This is not a hypothetical. v1's rewrite involves: shipping `register_template.py`, running registration against ACN/FedEx/NFL templates, committing the resulting `brand.yml` files, rewriting `load_client_theme()` as a YAML wrapper, deleting ~150 lines of heuristic code, and validating no existing builds regress. Two days is optimistic. If it slips to 4 days, Path B becomes "v2 sits idle for 4 days, then runs first A/B on day 5." Path A-minus is unaffected — v2's smoke ran on day 1.

5. **The "two purples" trap.** Both ACN and FedEx have purple primaries. If the first comparative A/B happens to be against an ACN brief and v1's old loader silently fabricates FedEx-ish colors, Path A's bug-tainted data is actually *visually indistinguishable* from clean data. We would conclude v1 looked fine and walk away with the wrong conclusion. This is an argument for Path B *or* for not doing the comparative judgment on Path A at all — i.e., Path A-minus.

---

## Risk-matrix table

Scoring: likelihood 1–5 (5 = near-certain), cost-if-it-goes-wrong 1–5 (5 = days of rework + bad architectural decision), product = expected risk.

| Path | Failure mode | Likelihood | Cost | Expected |
|---|---|---|---|---|
| A (full A/B now) | Bug-tainted v1 leads Mario to misjudge v2's comparative quality | 3 | 4 | 12 |
| A (full A/B now) | v1's loader bug masks an *actual* v2 problem because both decks look similarly off | 2 | 4 | 8 |
| B (wait 2 days) | v1 rewrite slips to 3–4 days; v2 stays idle | 3 | 3 | 9 |
| B (wait 2 days) | Latent v2 bug discovered on day 3+, pushing first A/B to day 5–7 | 4 | 4 | 16 |
| B (wait 2 days) | Context/momentum decay on v2 architecture during wait | 3 | 2 | 6 |
| B (wait 2 days) | v1 + v2 changes both live; integration bug attribution is ambiguous | 3 | 3 | 9 |
| C (baseline + post-rewrite) | Doubled Mario-review cost yields no actionable signal | 4 | 3 | 12 |
| C (baseline + post-rewrite) | Wall-clock doubles; v2 sits half-built waiting for round 2 | 3 | 3 | 9 |
| **A-minus (v2-only smoke now + proper A/B later)** | v2-only smoke can't detect comparative quality issues | 5 | 1 | 5 |
| **A-minus (v2-only smoke now + proper A/B later)** | Mario insists on comparing anyway and the bug taints the comparison | 2 | 3 | 6 |
| **A-minus (v2-only smoke now + proper A/B later)** | v2 smoke surfaces a bug class that takes more than 2 days to fix | 2 | 4 | 8 |

Totals (sum of expected risk per path):
- Path A: 20
- Path B: 40
- Path C: 21
- **Path A-minus: 19**

Path B's total is dominated by the single 16-point cell — "latent v2 bug discovered on day 3+." That cell is what the data-quality frame misses. The coordinator is correctly pricing the bug-taint risk in Path A but is not pricing the bug-discovery-delay risk in Path B.

---

## Biggest concern

**v2 has never run end-to-end against a real brief.** Every static review caught something. The patches landed since `build_deck.py` static review have not been validated by an actual run against `slidelab-intro-shippable.md`. The coordinator's Path B asks us to wait two days before doing that validation. That is the wrong sequencing — the first thing you do with a freshly-patched script that just had three Criticals flagged is run it, not wait. Decoupling "run v2 against a real brief" from "run the comparative A/B" is the operational move. Conflating them is what makes Path B look defensible.

If I have to pick from the coordinator's three options as stated: **Path A**, on the explicit understanding that the comparative judgment is deferred. If "Path A" is read strictly as "make A/B decisions on bug-tainted data," then **Path B**. The strict reading is what the coordinator priced; the loose reading is what I'd actually do.
