# Architecture Review C — Slide Lab v2

**Reviewer:** C (independent, blind to A and B)
**Date:** 2026-05-25
**Scope:** Q1 (adjacency check ordering) + Q2 (rotation seed shape)

---

## Q1 Verdict — Coordinator is WRONG. The correct answer is D (hybrid: prep-time best-effort hint + post-pass detection).

**Reasoning.**

The framing of the question is half wrong. The coordinator says "parallel fanout makes this hard to enforce because no agent sees neighbors' picks." But `prompt.md § 4.3` already declares a `{{PREVIOUS_TWO_PATTERNS}}` token that the agent is told to consult. This token cannot be filled at prep time under true parallel fanout — slide N-1 and N-2 have not been built yet when slide N's prompt is rendered. So the architecture as written contains a token that resolves to a lie ("(this is the first/second slide)" for every slide), or to a value the build script cannot actually compute.

That is the real problem. The coordinator's option C (post-pass at finalize) papers over it by treating the rule as advisory. That is not enforcement, it is a comment. Three things will happen with pure C:

1. **REVIEW.html shows a yellow banner.** "Slides 4, 5, 6 use the same split." The user looks at the three PNGs. If they look OK, the user clicks through. Within two real decks, the user is desensitized to the banner. Within four, the banner is wallpaper.
2. **No tiebreak escape exists for slide 5.** If all three options for slide 5 land on N-column row (because the brief says "five capabilities" and N-column-row is the obvious pick), and slides 4 and 6 are also N-column row, the user has no good pick. The post-pass either accepts the violation or forces a rebuild of one slide with no guidance about which alternative pattern to substitute. The coordinator's recommendation does not specify which.
3. **The rule degrades to noise.** A rule that fires at review-time but has no consequence other than a warning is, empirically, not a rule.

The fix is cheap and the architecture already has the hooks for it. Run a deterministic pre-assignment **pass** (not v1's full chassis-skeleton — just a 50-line pattern hint) that takes the brief and computes the **likely** pattern per slide using the same signals table the agents will use. Inject that as `{{PREVIOUS_TWO_PATTERNS}}` for context. The agent can still deviate from the prep-time hint when the seed or signals warrant — but two of the three deviation paths (matching both N-1 and N-2) get blocked at prompt time, not at finalize. Then keep C as a backstop: a post-pass detector that fires only when the agent overrode the hint and still landed on a 3-in-a-row.

This is **not** v1's chassis-skeleton mechanism rebuilt. The chassis problem was 19 fine-grained semantic categories with adjacency-graph forbids; this is 14 coarse-grained geometric patterns with one rule (no 3-in-a-row). The signals table that the agent uses is also the signals table the prep script uses — there is no second classifier. The prep-time pass is the same logic, run once cheaply, to seed adjacency awareness across the parallel fanout. Total added code: probably under 80 lines in `build_deck.py`.

The coordinator's C-alone is not safe enough. The B (sequential fanout) is unnecessary. The right answer is A-lite + C as backstop — call it D.

---

## Q2 Verdict — Coordinator is RIGHT on the direction (B), but the implementation is incomplete.

**Reasoning.**

family/intent in v1 served two purposes: (a) routing within the chassis vocabulary, and (b) injecting cross-slide diversity into the seed so that a deck full of "finding" slides did not pick the same variant on every slide. v2 has no chassis vocabulary, so purpose (a) is moot. Purpose (b) is still needed but does not require family/intent specifically — `slide_n` already varies per slide, and `content_hash` already varies per brief edit.

Option A (define new v2 family/intent vocabularies) is exactly the failure mode v2 exists to escape. It reintroduces a pre-classifier whose taxonomy needs maintenance, validation against real briefs, curator review, and a deprecation rule. That is the path that failed at 23% acceptance in v1. Hard no on A.

Option B (`md5(content_hash + slide_n)`) is the correct direction. It is simpler, has no taxonomy to maintain, and gives every slide a different seed.

**But B as stated is incomplete.** Two issues:

1. **It needs to be `md5(content_hash + slide_n + pattern_picked)` for variant rotation, not just for tiebreak.** The seed has two jobs in v2: (a) break ties among 2-3 eligible patterns, and (b) prevent variant-level convergence within a chosen pattern. Job (b) needs the pattern name baked in or two adjacent same-pattern slides land on the same variant by construction — the opposite of what we want. The coordinator's B-as-written conflates the two jobs and gets job (b) wrong.

2. **Three parallel agents on the same slide need to diverge on variants.** Each option (A/B/C) must land on a different variant. If the seed is `md5(content_hash + slide_n)` with no per-option salt, all three agents derive the same seed and pick the same variant. `prompt.md § 5` says "use the rotation seed to vary your starting variant choice" but does not specify how three sibling options diverge. Needs an `option_letter` salt: `md5(content_hash + slide_n + pattern + option_letter)`.

So: B in spirit (drop family/intent), but the actual seed is `md5(content_hash + slide_n + pattern + option_letter)`. The coordinator's recommendation passes on principle but fails on completeness. Treat as conditional approval.

---

## Biggest concern

**The single biggest concern is the user-experience cliff between v1 and v2 when the brief is too underspecified for the architecture to land confidently.**

v1 had four compensating layers because its primitive was fine-grained. The leaks happened in narrow places. v2 has 14 coarse patterns; when the agent picks wrong, the wrongness is *visible at thumbnail scale* — and the user will see it in REVIEW.html with no diagnostic next to it. What does the user do when slide 5's three options are all "N-column row" but the brief actually wanted a chart?

The architecture has no concept of "the agent picked the wrong pattern entirely." SKELETON_REJECTED handles brief/pattern disagreement on enumeration count (2 items in a 4-cell slot), and handles curved-container routing. It does not handle "agent scored Top-band-+-body highest but a human would have picked Chart." The seed-as-tiebreaker rule assumes ties are between roughly-equally-good patterns; in practice, the agent will sometimes mis-score and there is no second opinion.

In v1, the chassis-skeleton mechanism plus the curator pass caught this kind of miss. In v2 the only catch is the user clicking through REVIEW.html. That works for one or two slides per deck. For a 20-slide deck with three or four mis-picks scattered through it, the user gets fatigued and ships the wrong layout. The 23%-acceptance failure of v1 was not just "the taxonomy is too granular" — it was also "the curator gate caught a lot of things." Removing both the granularity *and* the gate is two simplifications at once.

Three concrete mitigations that should land before the first A/B real-brief test:

1. **Per-slide "second-best pattern" annotation in REVIEW.html.** The agent already scored all 14; surface the top-2 picks and the score gap. If the gap is < 20%, flag for human review. This costs nothing — the data already exists at pick time.
2. **A `# CONFIDENCE_LOW: <reason>` marker** parallel to SKELETON_REJECTED, fired when the top score is below an absolute threshold (the brief did not give a strong signal to any pattern). This routes the slide to a "needs human pattern selection" rail in REVIEW.html instead of building three options on a guessed pattern.
3. **For pattern #15 in 6 months:** the architecture is fine as long as patterns are additive. The risk is that pattern #15 partially overlaps an existing pattern's signal space (e.g., a new "annotated timeline" pattern partially overlapping N-column-row and Swimlane). The signals table is the contract; adding a pattern means revising the signals table and re-running the A/B against archived briefs. There is no test harness for that today. Before #15 ships, a regression suite of "10 archived briefs -> expected pattern picks" is needed. Without it, every new pattern silently shifts the picks for existing brief shapes and the deck quality drifts. Build the regression harness as a deferred v0.1 item — it is the long-term scalability moat for the 14-pattern primitive.

The coordinator's Q1+Q2 recommendations are roughly right but treat the architecture as if it were already proven. The 12-agent / 17-PNG validation is encouraging but is *not* a real A/B against v1 on a real consultant brief. Lock the decisions, ship v0, but build the regression harness and the CONFIDENCE_LOW marker into v0.1 before the second real deck runs.
