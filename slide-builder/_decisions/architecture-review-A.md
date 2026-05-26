# Architecture Review A — Slide Lab v2 (slide-builder-simple)

**Reviewer:** A (blind, independent)
**Date:** 2026-05-25
**Files read in full:** `_decisions/DECISIONS.md`, `SKILL.md`, `reference/layouts.md`, `prompt.md`

---

## Q1 Verdict: OTHER — hybrid of B-lite + C

Adopt the **coordinator''s C** as the visible mechanism, but acknowledge that `prompt.md` already implies a prep-time adjacency hint via the `{{PREVIOUS_TWO_PATTERNS}}` token. That token is currently undefined under pure C. Either delete it from the template, or fill it with a real **signal-based forecast** (not a locked pre-assignment). Net: C is correct as the safety-net mechanism, but the architecture is already a 2-layer hybrid and the prompt template needs to be reconciled with whichever choice lands.

---

## Q1 Reasoning

The coordinator framed this as a clean A vs. B vs. C choice. It isn''t. Reading `prompt.md` § 4.3 shows the architecture already references `{{PREVIOUS_TWO_PATTERNS}}` — meaning at prep time, each agent is supposed to see the patterns picked for slides N-1 and N-2. The trap: at prep time, those slides haven''t picked yet either, because they''re all about to dispatch in parallel. So that token cannot literally hold real picks. It is currently underspecified.

So the real question is: what does `build_deck.py` interpolate into `{{PREVIOUS_TWO_PATTERNS}}`?

- **Option A (pre-assignment):** `build_deck.py` classifies and assigns. This re-introduces the v1 chassis classifier under a new name. Rejected — the entire v2 thesis is "no centralized classifier." Break.
- **Option B (sequential fanout):** kills the parallel architecture, scales linearly. On a 25-slide deck that''s 25× wall time. Break — defeats v2''s shape.
- **Option C (post-pass detection):** works, but leaves `{{PREVIOUS_TWO_PATTERNS}}` in `prompt.md` either deleted or filled with a lie. Both need to be resolved.

**The hybrid I propose:** at prep time, `build_deck.py` runs a *very lightweight* signal scan over the brief — not a classifier, just a **dominant-signal hint** (e.g., "slide N-1''s brief mentions 2 items; slide N-2 mentions a hub-and-spoke"). It writes that hint, not a locked pattern, into `{{PREVIOUS_TWO_PATTERNS}}` as a *forecast* (e.g., "slide N-1 likely lands on 50/50 or Horizontal bands; slide N-2 likely Chart"). The agent treats it as soft guidance: if its own pick collides with both predicted neighbors, it demotes to next-best.

Then **at finalize time, C runs anyway** as the safety net. REVIEW.html surfaces real 3-in-a-row violations from the declared pattern headers (which `prompt.md` § 8 already mandates as line 1 of every option script). User adjudicates per slide.

**Why this is better than pure C:**
- Pure C is purely advisory. If users ship 3-in-a-row decks repeatedly, Rule #3 is dead letter. The Hardline rule list shrinks from 5 to 4 in practice.
- Pure C also leaves `{{PREVIOUS_TWO_PATTERNS}}` either deleted (acceptable) or lying (worse).

**Why this is better than A or B:**
- A''s classifier is the v1 failure mode. A "lightweight signal hint" is not a classifier — it does not pre-assign a pattern, it just forecasts which patterns are *probable*. Agent still picks freely.
- B''s sequential dispatch loses parallelism. Non-starter.

**What the coordinator gets right:** rejecting A and B. Both genuinely break v2''s architecture.

**What the coordinator gets wrong:** treating C as sufficient. C is sufficient only if `prompt.md` is updated to either (a) delete `{{PREVIOUS_TWO_PATTERNS}}` entirely, or (b) interpolate a real signal-based forecast. The current template references a token that has no plausible value under pure C.

**If you reject the hybrid:** then go with pure C **and delete `{{PREVIOUS_TWO_PATTERNS}}`** from `prompt.md` § 4.3. Don''t leave a dangling token that implies prep-time pre-assignment.

---

## Q2 Verdict: B

Drop `family` and `intent`. Seed on `md5(content_hash + slide_n)`.

---

## Q2 Reasoning

The coordinator is right. A recreates v1''s classifier with a different label set and reintroduces the very pre-classification step v2 explicitly rejects. C is open-ended hand-waving — "define them in a lighter way" without committing to what they are is not a decision.

**Why B works:**

- The seed''s job in v2 is tiebreaking among multiple eligible patterns and rotating variants within a pattern. It does **not** need to encode semantic family/intent because the **agent already does that classification implicitly when it scores patterns**. The seed only operates *after* the score is computed. Entropy of `content_hash + slide_n` is sufficient for that downstream coin-flip role.
- `slide_n` differing guarantees adjacent slides get different seeds even with identical content (rare but possible — e.g., two near-identical KPI scorecards). The coordinator''s concern about "two slides with similar content but different positions getting the same tiebreak" is mathematically wrong: if `slide_n` differs, the full md5 differs, so the seed differs. Period.
- The `content_hash` term still absorbs brief edits — the original property that mattered in v1.

**Edge case the coordinator missed (minor):** the rotation seed in v2 has two consumers — (1) tiebreaker between patterns, (2) variant picker within the chosen pattern. With B, both consumers get the same seed. That means if pattern P is tiebroken-into for slide N *and* the variant choice within P uses the same seed, the two decisions are correlated. Probably fine — they''re sequential decisions on the same slide and a human would expect them to feel coherent. But worth noting: if variant divergence across the 3 options (A/B/C) ever feels too tight, the fix is to derive separate sub-seeds (e.g., `md5(seed + "tiebreak")` vs `md5(seed + "variant_A")`), not to add family/intent back in.

**Edge case the coordinator also missed:** `content_hash` needs to be explicitly defined. Is it md5 of the full per-slide brief block? Of just governing thought + so-what + evidence? `prompt.md` shows `{{ROTATION_SEED}}` as already pre-computed — so `build_deck.py` needs an explicit content_hash spec. Lock it: `md5(governing_thought + "\n" + so_what + "\n" + evidence_content)`. Editorial emphasis and "what this slide is NOT" excluded because they don''t change the slide''s identity, only its rendering nuance.

**Verdict stands: B, with content_hash explicitly defined in `build_deck.py`.**

---

## Biggest concern across both decisions

**The `{{PREVIOUS_TWO_PATTERNS}}` token in `prompt.md` § 4.3 is currently undefined under all three Q1 options.** This is the single thing I''d push back on hardest.

If Q1 lands on pure C, the token must be deleted from the prompt template — leaving it in tells the agent to expect prep-time pattern foreknowledge that doesn''t exist in a no-classifier architecture. If Q1 lands on the hybrid I proposed, the token must be redefined as a *forecast* (probability distribution over patterns), not a locked pick — and `build_deck.py` needs the signal-scanner logic to produce that forecast.

Either way, **`prompt.md` § 4.3 as currently written is a latent bug**: the dispatched agent will receive a token value at prompt-render time, and if that value is "(unknown)" or empty, the adjacency check (Hardline #3) is silently skipped at build time. The agent will think it''s enforcing Rule #3 because the prompt tells it to; the prompt will pass empty values; the rule will not be enforced. Then C''s post-pass detection catches it at REVIEW.html, but only as advisory.

This is the exact failure pattern v1 suffered from — multiple compensating layers each assuming the layer below caught the case. Pick one mechanism for Rule #3 and make it real, or downgrade Rule #3 from "hardline" to "advisory" in `SKILL.md`. Don''t leave it in both places half-implemented.

The other thing I''m less confident about: whether `md5(content_hash + slide_n)` produces enough variant divergence across 3 options for the *same* slide. The 3 options share the same seed (same slide_n, same content_hash), which means without sub-seeding the agent must consciously diverge variants A/B/C rather than relying on the seed to do it. `prompt.md` § 5 does instruct this ("three structurally distinct options"), so probably fine. But empirically untested.
