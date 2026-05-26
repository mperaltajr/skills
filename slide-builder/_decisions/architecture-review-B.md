# Architecture Review — Reviewer B

**Scope:** Q1 (adjacency check ordering) and Q2 (rotation seed simplification) for slide-builder-simple v2.
**Reviewer:** Independent. Blind to A and C.

---

## Q1 Verdict: **A (prep-time pre-assignment) — coordinator's C is wrong**

The coordinator recommended C (post-pass detection at finalize, rule becomes review-time guidance). I'm breaking that.

**Why C fails.**

C demotes Hardline Rule #3 from a hardline rule to a review-time advisory. That is a category change, not an implementation choice, and it's being smuggled in under the framing of "where do we enforce it." Read the rule list in SKILL.md § Hardline rules: the five rules are deliberately framed as non-negotiable invariants the agent must satisfy at write time. Two of the other four (fabrication, brief-fidelity, SKELETON_REJECTED) are similarly checkable only with context the agent has. Rule #3 is the one that requires cross-slide context. Pulling it out and saying "actually this one is just guidance" weakens the architecture's claim that there are exactly five hardline rules — there are now four-and-a-half, with the half-rule policed by REVIEW.html banners the user can ignore.

Worse, C's remediation story is broken. If `finalize_deck.py` detects 4 slides in a row on Top-band+body, what happens? Three options:
1. Re-dispatch the offending slides — but that's just A with extra latency and wasted token spend.
2. Ship the deck with a warning — that's deprecating the rule.
3. Block on user confirmation — UX friction every build, and the user has no better information than the agent did.

None of these are better than just pre-assigning.

The prompt.md draft already concedes this. Look at § 4.3:

> Previous two slides' patterns: `{{PREVIOUS_TWO_PATTERNS}}` ... If your picked pattern matches **both** of the previous two slides' patterns ... demote your pick to the next-highest-scoring pattern.

That is **option A in disguise**, just done by the agent at dispatch time using a string that `build_deck.py` already had to compute. The only honest question is *who* makes the demotion decision: the prep script or the dispatched agent. Either way it's a prep-time computation that flows into the prompt.

**Why A is right.**

A is what v1 already does (chassis-skeleton pre-assignment) and it works. The supposed cost — "kills parallelism" — is wrong. Pre-assignment doesn't serialize fanout; it serializes a cheap deterministic computation *before* fanout. `build_deck.py` walks slides 1..N once, picks the highest-signal-match pattern for each (with the rotation seed as tiebreaker), checks the previous two against the current, demotes if needed, and writes that into `{{PREVIOUS_TWO_PATTERNS}}` plus an optional "pre-assigned pattern hint." Then N agents fan out in parallel exactly as designed.

There's a real subtlety: do you *pre-assign* the pattern or just *constrain* it? I'd argue **constrain-only**: `build_deck.py` computes the forbidden patterns for slide N (the intersection of slides N-1 and N-2's patterns) and injects them as a blocklist in the prompt. The agent still picks freely from the remaining 13. This preserves agent autonomy — which the architecture says is the whole point of v2 — while making rule #3 enforceable at write time.

**B (sequential fanout)** is correctly dismissed by the coordinator. Skip.

**Verdict:** A, implemented as a forbidden-pattern blocklist injected by `build_deck.py`. Not C.

---

## Q2 Verdict: **B (drop family and intent) — validate coordinator**

The coordinator recommended B. I'm validating.

**Why B is right.**

`family` and `intent` are v1 ontology terms. `family` is a chassis grouping (anchor-with-cards, dark-canvas-hero, etc.). `intent` is a content-purpose tag (recommendation, finding, divider, etc.). Both exist because v1 needed to route briefs through a 19-chassis vocabulary. v2 explicitly throws that vocabulary out — that's the whole thesis (DECISIONS.md lines 22-29). Keeping `family` and `intent` in the seed formula because v1 had them is cargo-culting. The seed must operate on inputs v2 actually has.

A (define new v2 vocabularies) would re-introduce a pre-classifier. Pre-classifiers are precisely what SKILL.md § Classifier explicitly forbids: *"There is no pre-classifier (a pre-classifier would re-introduce v1's chassis-routing logic)."* So A contradicts the locked architecture. Off the table.

C (define lighter family/intent) is open-ended hand-waving. If you can name a property of the brief that's load-bearing for variant rotation and isn't already captured by `content_hash + slide_n`, propose it. Otherwise you're just A with smaller words.

**One concern with B.** The seed has two jobs in v2:
1. **Variant tiebreaker** within a chosen pattern (which icon style, which accent placement, etc.)
2. **Pattern tiebreaker** when multiple patterns score equally on the signals table (per prompt.md § 4.2)

Job 1 is fine — `md5(content_hash + slide_n)` gives a stable, slide-unique value that differs per slide and survives brief edits. Job 2 is also fine for the same reason.

But: with `family + intent` removed, slides whose `content_hash` collides (unlikely but possible — two slides with identical normalized brief text) plus same `slide_n` (impossible) get the same seed. The collision risk is essentially zero. No blocker.

**Strengthen B with one tweak:** define `content_hash` precisely. Is it md5 of the brief block verbatim, or of `governing_thought + so_what + evidence`, or of the full slide YAML? Pick one and document it in `build_deck.py`. Right now neither file specifies it. That's a latent footgun — if `content_hash` is computed differently across v1 and v2, A/B test results aren't comparable.

**Verdict:** B, with `content_hash` definition spelled out in the build script. Not A, not C.

---

## Biggest concern across both decisions

The biggest concern isn't either Q1 or Q2 individually — it's that **prompt.md § 4.3 already implements Q1's answer (it's A, by another name) while the coordinator is asking whether to do C.** Either the coordinator hasn't read the prompt.md they wrote, or the prompt.md was drafted assuming a decision that hadn't been made. Either way: the artifacts and the question are out of sync, and shipping a v0 with prompt.md saying "demote your pick" while `build_deck.py` doesn't compute `{{PREVIOUS_TWO_PATTERNS}}` correctly will produce confused agents on slide 3 of every deck.

**Specifically:** `build_deck.py` is described in DECISIONS.md as "swap the chassis/rulebook injection for 14-pattern + anti-pattern-library injection." That phrasing makes it sound like a near-verbatim fork. It's not. `build_deck.py` for v2 has new responsibilities — computing per-slide rotation seeds with a new formula, computing previous-two-patterns or a forbidden-pattern blocklist, possibly pre-assigning patterns. None of that exists in v1's build_deck.py. The "fork verbatim" framing is going to cause the v0 build to ship with stub logic where adjacency enforcement should live.

**Recommended action before build:** rewrite the artifact #6 description in DECISIONS.md to call out exactly what `build_deck.py` must compute that v1's doesn't (rotation seed under new formula, previous-two-patterns string or blocklist, `content_hash` definition). Otherwise the build agent will copy v1's file, swap two strings, and ship a broken v2.

The two architectural decisions are individually fine (A and B). The risk is they get implemented inconsistently because the surrounding documentation hasn't been updated to reflect them.
