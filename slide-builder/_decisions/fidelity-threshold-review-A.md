# Reviewer A — Brief-fidelity threshold review (item 4 path)

**Angle:** Threshold interpretation. What does the number mean?

---

## Verdict on cost path: B (patch + run, ~45 min)

A is a half-measure. C is the abdication the user named in advance. B is the only one that earns its claim under the production-grade bar.

A's shim gets a number out but leaves a known landmine for item 1 (FALLBACK_MERMAID smoke) — patch debt that compounds in <24h. We already know item 1 needs the FALLBACK_MERMAID skip. Doing A means doing B next week with cold context and a fresh round of "wait, what was the convention again." Sequencing the fix once costs ~15 extra min; sequencing it twice costs a context reload.

The shim itself is also worse than the patch. A shim ("write a `_meta.json` v2 doesn't otherwise need") introduces v2-only convention drift dressed up as compatibility. It papers over the real finding: **v2 doesn't have a manifest, and the QC stack assumes one.** That gap will bite again. Either v2 commits to writing `_meta.json` (then the script doesn't need patching for that part) or the script gets a v2-aware path resolver. Pick one and own it. Don't shim.

C — defer entirely — is the option Mario already pre-rejected when he killed "let real A/B builds surface it." Hardline #4 is in `SKILL.md` and `prompt.md` as a non-negotiable. Saying "we'll measure it later" while shipping a number we know is empirically false is exactly the quiet-bug pattern the v2 architecture exists to refuse.

**B. Patch the script for FALLBACK_MERMAID, run, measure.**

---

## Recalibration sub-option: 1 (recalibrate Hardline #4 to v1's empirical baseline), with a specific framing change

Update `prompt.md` § 6 and `SKILL.md` Hardline #4 to **0.30 per-slide-min / 0.70 deck-avg**, with the inline note that these are v1's empirical recalibration and v2 inherits the baseline pending its own calibration run.

But that's not enough. The current Hardline #4 text — "Brief fidelity ≥ 0.92" — is *also* wrong in shape, not just in number. It implies a single per-slide threshold. The actual measurement is two-thresholds-plus-structural-flags. Carrying "≥ 0.92" forward as a single-number hardline ignores that the script's pass condition is `per_slide_min >= X AND deck_avg >= Y AND structural_flag_count == 0`. The structural-flag tier is the actual hard signal; the token ratio is soft. v1's own inline comment in `check_brief_fidelity.py` says this explicitly: *"Structural-label tier-3 regex remains the hard-fail signal — token ratio is the soft signal."*

So the rewrite is two-part:

1. **Number:** drop 0.92. Adopt 0.30 / 0.70 from v1's empirical baseline. State the source. State the planned recalibration after 3–5 v2 engagement decks.
2. **Shape:** state the rule correctly. "Brief fidelity has two soft floors (per-slide-min 0.30, deck-avg 0.70) and one hard floor (zero `STRUCTURAL_COUNT_FABRICATION` flags). The structural flag is the actual non-negotiable; the ratios are advisory until the v2 calibration run completes."

Without the shape fix, we just trade one wrong number for another wrong claim.

---

## Reasoning under the production-grade bar

Mario's bar previously rejected "let real A/B builds surface it." Apply that to the three sub-options:

**Sub-option 2 (keep 0.92, treat v2 as failing):** Looks rigorous but is theater. The 0.92 was author-estimated against zero empirical data. v1's first run showed healthy decks scoring 0.35–0.95 per option with deck-avg ~0.77. Insisting on 0.92 means insisting on a bar that real, good decks empirically do not hit. The honest interpretation is not "v2 fails" — it is "0.92 was never the bar; it was a guess." Calling that a fail is dishonest about the measurement, not honest about the build.

**Sub-option 3 (defer):** Mario already rejected the defer-and-see pattern. Repeating the rejected pattern in the brief-fidelity stream specifically — the stream where Hardline #4 lives in two locations of skill-level documentation — is worse than deferring on a quieter claim. This is the load-bearing claim of the rule; it cannot ride on author estimate.

**Sub-option 1 (recalibrate now):** This is the option that admits what the data already says. v1 ran the script against a real deck, the script told v1 the threshold was wrong, v1 lowered it. v2 is about to run the same script against a real deck. The threshold v2 should compare against is the one v1 already calibrated against the same script's behavior on similar agent output. v2 inheriting that baseline is not a shortcut — it's the only honest starting point. Running v2's own calibration baseline (the parenthetical option in the prompt) is the *next* step, not the gate.

The key move: **stop carrying the strawman number forward at all.** Every minute Hardline #4 in `SKILL.md` and `prompt.md` says ">= 0.92" while the script enforces 0.30/0.70 is a minute v2 ships a documented claim it can't substantiate. That's the quiet-bug pattern.

### What the numbers will mean once we run

- **0.77 deck-avg:** v2 hits v1's empirical baseline. Honest framing: "v2 matches v1's measured behavior on this brief; the recalibrated thresholds pass." NOT "v2 passes 0.92." 0.92 is gone from the claim.
- **0.85 deck-avg:** v2 outperforms v1's typical. Honest framing: "v2 scored above v1's empirical baseline on this single brief — directional, not conclusive. Calibrate v2's own range after 3 more decks."
- **0.50 deck-avg:** v2 is in the lower half of v1's observed range (0.35–0.95). Honest framing: "v2 scored low on this brief; investigate per-slide which options dragged it down (likely composite slides with legitimate brief expansion). If structural-flag count is zero, this is soft-signal noise, not a fail."

The script's two-tier design is exactly built to disambiguate "low ratio + no structural flags = legitimate" from "low ratio + structural flags = fabrication." That disambiguation is the actual measurement. Hardline #4 has to encode that, not a single ratio.

---

## Biggest concern

**The 0.92 in v2's docs is not just empirically false — it's load-bearing for the v2 narrative.** v2 was scoped around five hardline rules that each carry weight. Hardline #4 is one of five. If Hardline #4's number is fiction, the implicit claim that "v2's five hardlines are rigorously enforced" is a quarter false. The next hardline a curator audits ("rule 4 said >=0.92, the script enforces 0.30, what else here is decorative?") gets the same scrutiny — and rightly. The cost of carrying the strawman is not just on rule 4. It corrodes trust in the other four.

The fork-time inheritance pattern that produced the `themed/` bug and the `sys.argv` bug is the same pattern producing this one: a number was written into one artifact (the strawman), copied into another (prompt.md + SKILL.md), and never traced back when the source of truth moved. The fix is the same in shape: **make the script the source of truth, have the docs cite it, not invent a separate number.** `prompt.md` § 6 and `SKILL.md` Hardline #4 should literally read "see `check_brief_fidelity.py::PER_SLIDE_MIN` and `DECK_AVG_MIN`" rather than hardcoding the number. Drift becomes impossible.

That's the v0.1 follow-up to the v0 fix. v0 fix: change 0.92 to 0.30/0.70 in both docs. v0.1: have the docs reference the constants instead of duplicating them. Same disease as the missing `paths.py`. Same cure.
