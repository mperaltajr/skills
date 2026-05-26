# Post-Stage 4 plan review — Reviewer A (Process Discipline)

**Date:** 2026-05-25
**Angle:** Which sequencing produces better outcomes given the empirical evidence we have?
**Reviewer:** A (blind to B and C)

---

## Verdict on sequencing

**Coordinator''s audit-first sequencing, with a sharper scope than the coordinator stated.**

Not v2''s plan. v2 is wrong on the sequencing for one concrete reason: I opened `compile_picks.py` and grepped it before writing this. Line 210 reads:

```
src = out_dir / "themed" / key / f"option_{letter}.pptx"
```

That is the **exact same path-contract drift** as `build_review.py` — read from `<out>/themed/slide_NN/...` while `finalize_deck.py` writes to `<out>/slide_NN/...` (no `themed/` prefix; confirmed at `finalize_deck.py` lines 416, 769-773). Both reader scripts were branched from the same v1 layout assumption, and both still carry it. Compile_picks is the script that produces the **final deck the user actually keeps** — if you fire it today against the smoke output, the pick loop fails silently (every `src.exists()` check returns False) or crashes on first read. That is a Category 1 defect that is one keystroke away from biting.

So the 5th defect the coordinator was hedging about is real, not theoretical. Once you know that, v2''s "fix #4, re-fire Stage 4, then audit" sequencing is empirically wrong: it leaves a known-shape bug live in the script that runs at the end of the flow. The Gate 3 pattern (audit first, fix once, re-fire once) is the right reference. Use it again here.

But the coordinator''s framing is also slightly too loose. "Run a fork-contract audit on finalize/review/compile_picks" can become process theater if the auditor does not know what they are looking for. The audit needs a **specific predicate**: every script that reads slide outputs must read from `<out>/slide_NN/option_X.<ext>`, with no `themed/` segment. That predicate is mechanical: grep for `"themed"` or `/themed/` or `themed_dir` across `scripts/*.py` and inspect each hit. 5 minutes. Then fix the two confirmed sites (build_review.py:295,297 and compile_picks.py:210) in the same commit. Then re-fire Stage 4.

That is not "audit first" in the abstract — it is "run one targeted grep, fix two sites, re-fire once." Cheaper than v2''s plan, and it closes the known shape of the defect class instead of one instance.

## Verdict on defect 1 classification

**v0, but a narrower v0 than the coordinator described.**

Read `option_A.py`. It imports `BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT` on line 10, then uses none of them. The agent reached for the tokens, then chose not to use any of them, because the "safe default" variant instruction in prompt.md gave it license to. That is a prompt-design bug, not an agent-reasoning bug. The fix is local: change the cover-patterns "safe default" language in prompt.md to require **at least one brand-color element per variant** (product name in BRAND_PRIMARY, or BRAND_ACCENT counter-line, or a BRAND_PRIMARY-tinted footer rule).

That is a 5-minute prompt edit, not an architectural rewrite, and it does not open a can of worms about variant discipline because the rule is narrow: "every option_X must touch at least one brand token in `add_text(color=...)` or `add_rect(fill=...)`." It is grep-checkable post-build if you want to enforce it programmatically later.

What would open a can of worms is the broader version: "tighten safe-default discipline across all patterns." Do not do that. Do the narrow version: brand-token-floor on covers and dividers, where the partner-facing first impression bug lives. Body-slide safe-defaults can stay v0.1.

So: v0, scope = cover-patterns section of prompt.md + a one-line brand-token-floor rule in section 4 or wherever "safe default" is defined. Estimated cost: 5-10 min edit + verified in the re-fire.

## Per-defect handling recommendation

| # | Defect | When | What |
|---|---|---|---|
| 4 | finalize/review path-contract drift | NOW, before any re-fire | Grep `themed` across `scripts/*.py`; fix `build_review.py:295,297` AND `compile_picks.py:210` in same commit. Add a one-line comment at the top of each reader script documenting the canonical path `<out>/slide_NN/option_X.<ext>`. |
| (5) | compile_picks.py same drift | NOW, same commit as #4 | See above. This is the unnamed 5th defect; surfacing it is the whole point of audit-first. |
| 1 | Slide 1A zero brand color | NOW, before re-fire | Edit prompt.md cover-patterns "safe default" language: require >=1 brand token per variant. Narrow scope: covers/dividers only. |
| 3 | Color-recurrence doc error | NOW, batch with above | One-line correction to `smoke-test-finding-2026-05-25.md`. Trivial. |
| 2 | Adjacency unfixable at REVIEW.html | v0.1 — but document the user-visible escape hatch NOW | The architectural fix (cross-slide adjacency awareness at dispatch time) is genuinely v0.1. But add a sentence to REVIEW.html''s adjacency advisory: "To fix this, re-dispatch slides X-Y with a different pattern hint." That gives the user an escape hatch *outside* REVIEW.html without requiring the architectural rewrite. 10 min. |
| Then | Re-fire Stage 4 | After all four above commits | One re-fire. Watch-items: (a) REVIEW.html shows 30 tiles, (b) slide 1A has visible brand color, (c) compile_picks dry-run against the existing themed output succeeds. |
| Then | Category 2 smokes | After re-fire passes | trigger-brief, ACN, NFL, brief-fidelity. These are Reviewer A''s smoke-readiness recommendations from the prior round — still valid, still ~1 hr each, still the right next-phase work. |

## Biggest concern

**The audit-first decision is correct, but the audit must be predicate-driven or it degrades into ritual.**

The smoke produced defect #4 because nobody ran a `grep themed scripts/*.py` after finalize_deck.py''s path convention changed. That grep is the entire audit for the path-contract class. If the "fork-contract audit" the coordinator is asking for ends up being a human read-through of three scripts looking for "anything that feels wrong," it will miss defect classes that do not pattern-match human intuition (the next one might be filename casing, or stale token literals, or a hardcoded `"option_A"` instead of a loop). The audit needs to be **a list of predicates**, each of which is one grep or one diff:

1. Path contract: grep for `"themed"` or `/themed/` across `scripts/*.py` -> expect zero hits in reader scripts.
2. Filename contract: grep for `option_[ABC]\.(pptx|png|qc\.json|py)` across `scripts/*.py` -> confirm all readers use the exact pattern finalize writes.
3. Slide-N format contract: grep for `slide_\d`, `slide_NN`, `slide_\{` -> confirm zero-padded `slide_NN` everywhere.
4. Token contract: every reader/writer of `_pattern_pick.md`, `_meta.json`, `*.qc.json` agrees on the exact field names. Compare regex constants across files.
5. Hardcoded paths: grep for `C:\\`, `/Users/`, `.claude` -> only acceptable in fallback defaults, never in primary code paths.

Each is a 30-second mechanical check. Five minutes total. That is the right audit — not a vibe-check.

The risk that "audit-first becomes process theater" is real if the audit is unstructured. It is not real if the audit is five predicates. The mistake in v2''s plan is calling for "an audit" without naming what is being checked.

Secondary concern: v2 has now hit two contract-drift bugs in one smoke (prompt.md sys.argv at Stage 2, finalize/review path at Stage 4) and a third was live in compile_picks.py that the smoke did not reach. **This is a pattern, not a coincidence.** The v2 architecture has multiple producer/consumer boundaries (agents/prompt.md, finalize/raw scripts, finalize/themed output, review/themed input, compile_picks/themed input, picks.json/compile_picks input), and contract drift between any two breaks the pipeline. The mitigation is not heroic auditing every time something changes; it is **fewer contracts**. Specifically: one canonical path convention documented in `SKILL.md` (or `_decisions/PATHS.md`) that every script must conform to, with a CI-style check (a small `validate_paths.py` script that greps the predicates above and fails on any hit). Add that to v0.1 — not because today''s audit cannot be done by hand, but because *next* time something changes the path convention, the contract will hold.

That is the right post-mortem framing on this defect class. Not "we should have audited," but "we should have made the audit unnecessary by reducing the contract surface."

---

**Summary.** Audit-first wins on the data because compile_picks.py provably has the same shape of bug as build_review.py — I verified this directly. The audit needs to be a 5-predicate grep checklist, not a vibe-check. Defect 1 is v0 with narrow scope (cover/divider brand-token floor in prompt.md). Defects 2 and the broader v0.1 backlog stay where they are. After the audit commit + prompt.md fix + doc fix, one re-fire of Stage 4, then proceed to Category 2 smokes per Reviewer A''s prior recommendations (trigger-brief, ACN, NFL).
