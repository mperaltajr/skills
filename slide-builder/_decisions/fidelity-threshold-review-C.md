# Fidelity Threshold Review - Reviewer C (Scope / Diminishing Returns)

**Date:** 2026-05-25
**Angle:** Is item 4 a "measure-to-confirm" requirement under Mario's production-grade bar, or is it satisfied by an honest recalibration of Hardline #4 against v1's existing empirical data?
**Reviewer:** C (blind to A and B)

---

## Verdict

**Option D (new option): Recalibrate Hardline #4 in the docs against v1's empirical numbers RIGHT NOW (~10-15 min). Do not run v2's script. Promote items 1 and 2 with the time saved.**

This is not the "downgrade to unmeasured" option C from v2's menu. It is "recalibrate to measured-by-v1, then keep the measurement infrastructure as a v0.1 ship item once v2 has its own corpus." The script runs against v2 *after* v2 has produced enough decks for a v2-specific distribution to matter. Right now it runs against the v1 corpus dressed up in v2 filenames - which is ritual.

---

## Is "recalibrate-without-measuring" satisfying the production bar?

**Yes - but only if the recalibration is honest about what we know and what we don't.**

Mario's bar forbids three things relevant here: (1) deferring known validation gaps to production, (2) honor-system rules with no measurement, (3) numeric claims with no data behind them. Walk each:

1. **Deferring to production.** Recalibrating Hardline #4 to 0.30/0.70 does *not* defer anything to production. It says: "the threshold v2's docs claimed (0.92) was author-estimated; v1's first real run showed the empirical distribution sits at 0.35-0.95 per option with deck-avg ~0.77; v2 inherits that distribution because v2 uses the same agents writing against the same brief tokens; therefore Hardline #4's numeric floor is 0.30 per-slide-min / 0.70 deck-avg until we have v2-specific data to revise it." That's a measured claim with a defensible provenance line.

2. **Honor-system rule with no measurement.** This is the key question. Right now Hardline #4 in SKILL.md says "Brief fidelity >= 0.92. Measured per slide." Nothing measures it. After recalibration, SKILL.md would say "Brief fidelity >= 0.30 per slide / >= 0.70 deck-avg, inherited from v1's empirical calibration (see check_brief_fidelity.py lines 26-34). Will be re-measured against a v2-specific corpus after 3 real v2 builds." That is no longer honor-system - it cites a real measurement file with real numbers from a real run. The measurement happens to have been run against v1's corpus, but **v1 and v2 produce the same artifact (option_X.py files writing the same brief tokens with the same chrome vocabulary)**, so the v1 measurement is a valid prior. Not perfect, not v2-native, but defensible.

3. **Numeric claim with no data.** "0.92" had no data. "0.30/0.70 from v1's recalibration" has data. The data is one run, not three, which is a real limitation - but it's a vastly stronger claim than the current "0.92."

**Where this would fail the bar:** if v2's score distribution is materially different from v1's. The argument that it isn't: v2 agents write option_X.py files that are token-for-token comparable to v1's option_X.py files (same brief input, same helpers, same chrome). The agents are the same Claude model with different prompts; the prompt difference is *which patterns they pick*, not *what brief tokens they paste into the script*. The fidelity score is a token-ratio measurement that's largely indifferent to pattern choice. The expected v2 distribution sits inside the v1 distribution +/-~5%, not at a different center of mass.

**Where it could be wrong:** if v2's 14-pattern vocabulary causes agents to invent more chrome/labels than v1's 19-chassis vocabulary did (because patterns are more abstract and agents fill in framework names), then v2's denominator grows faster than the numerator and the score drops. That's a real risk. It is not a risk the script catches against the current 30-PNG smoke output - because the smoke deck is `gate4-smoke`, which is one synthetic brief, not three. Running the script against it gives us *one* v2 datapoint, which is no better than v1's one datapoint, just newer.

So the production-bar answer is: **recalibrate is defensible; running v2's script against the existing smoke is not meaningfully better than recalibrating; the script earns its keep only after v2 has 3+ real decks**.

---

## If recalibrating, what should the new Hardline #4 say?

SKILL.md and prompt.md currently both say:

> **Brief fidelity >= 0.92.** Every visible word on every slide traces to brief content or documented chrome (footer, page number, section label). Measured per slide.

The honest version:

> **Brief fidelity - every visible word on every slide traces to brief content or documented chrome (footer, page number, section label).**
>
> **Per-slide floor:** >= 0.30 token-overlap ratio (worst sibling option). **Deck-average floor:** >= 0.70. These thresholds are inherited from v1's empirical calibration on first real run (slide-builder/tests/gate4/check_brief_fidelity.py, lines 26-34). The v1 run showed healthy decks score 0.35-0.95 per option with deck-avg ~0.77; the worst legitimate score (0.354) occurred on a composite slide where the agent expanded the brief without fabrication. **Structural-label fabrication** (Tier 3 regex in `_structural.py`) is the hard-fail signal; the token ratio is the soft signal.
>
> **Revision plan:** thresholds tighten toward 0.50/0.80 after 3 real v2 builds have produced a v2-specific score distribution. Until then, v2 inherits v1's calibration.

Two specific edits required:

1. **SKILL.md section "Hardline rules (5)" rule 4** - replace `>= 0.92` with the language above.
2. **prompt.md section 6 rule 4** - same replacement, plus the agent's self-attestation header (`# Brief fidelity check:` line 3) gets a footnote: "this is metadata only; the gate is the deck-avg / per-slide-min ratio computed by the fidelity check, not your self-report."

And add to `_decisions/DECISIONS.md`:

> **Hardline #4 recalibration (2026-05-25).** The "0.92" threshold in the v2 architecture was author-estimated. v1's empirical first-run data (`slide-builder/tests/gate4/check_brief_fidelity.py`) showed the realistic distribution sits at 0.35-0.95 per option, deck-avg ~0.77. v2 inherits v1's calibration (0.30 per-slide-min, 0.70 deck-avg) because both versions produce token-comparable option scripts against the same brief format. Will be re-measured against v2-specific corpus after 3 real builds.

---

## Compared to running v2's script

Running the script against the existing 30-PNG smoke does add **one** thing v1's data doesn't have: a v2-specific datapoint. But it adds it on a synthetic brief (slidelab-intro), against one template (FedEx), with one agent dispatch round. That's n=1 for v2. Recalibrating to v1's n=1 and writing a "revise after 3 real builds" plan is the same epistemic state.

The script run *does* add value when v2's score distribution *might* differ from v1's. Two cases where it would:

- **Case A:** v2's pattern-pick rejection (SKELETON_REJECTED) fires in the smoke, producing zero-content slides. The script counts those as `skipped-rejected` and excludes them, so the distribution skews high. Would shift the floor *up*, not down. Not catastrophic.
- **Case B:** v2's 14-pattern vocabulary causes more agents to invent framework-name chrome (because patterns are more abstract than chassis labels). Would shift the floor *down*. This is a real concern but it's exactly the concern items 1 and 2 are designed to surface against more realistic briefs.

In both cases, **the real test isn't the existing 30-PNG smoke; it's items 1 (trigger-brief) and 2 (ACN multi-client)**. Running the fidelity script against gate4-smoke gives a number; running items 1 and 2 gives evidence about whether v2's agent behavior diverges from v1's at all. The latter is the prerequisite for the former being meaningful.

This is what makes item 4 ritual measurement at this moment. The infrastructure is fine. The *timing* is wrong. Run it after items 1 and 2 have produced a corpus that's worth measuring.

---

## Biggest concern

**That the team will conflate "recalibrate Hardline #4 honestly" with the original Option C ("downgrade to unmeasured"), and reject this path on the wrong grounds.**

Option C as v2 framed it was "remove the 0.92 number, ship without measurement." That is correctly rejected under Mario's bar - it's the honor-system failure mode. What I'm proposing is structurally different: replace 0.92 with 0.30/0.70 sourced from v1's measurement, cite the file and line numbers, document the n=1 limitation, and commit to revisiting after 3 real v2 builds. That's a measured claim with documented provenance and a revision plan. It's not "unmeasured" - it's "measured against the closest available corpus, with the limitation named."

The secondary concern: if items 1 and 2 reveal that v2 agents *do* invent more chrome than v1 agents (case B above), the 0.30/0.70 inheritance becomes wrong and we'll have to revisit anyway. That's fine - the revision is cheap (one-line constant changes in the script, two doc edits). The cost of being wrong here is small; the cost of running the script against synthetic data and treating the result as v2's "real" calibration is larger because it ossifies a meaningless number.

**Recommendation: Recalibrate now (15 min), spend the saved 30 min on item 1's trigger-brief smoke. Run v2's fidelity script for the first time against items 1 + 2's outputs, not against gate4-smoke.**

---

## Three-sentence verdict

Running v2's check_brief_fidelity.py against the existing 30-PNG smoke is ritual measurement - it produces one v2 datapoint on synthetic data while v1's existing data already tells us what the realistic distribution looks like, and the recalibrated thresholds (0.30/0.70) work for both versions because v1 and v2 produce token-comparable option scripts from the same brief format. The production-grade bar is satisfied by replacing the author-estimated "0.92" in SKILL.md and prompt.md with v1's empirically-calibrated 0.30/0.70, citing the source file and lines, and committing to re-measure after 3 real v2 builds - that is a measured claim with documented provenance, not the honor-system failure mode Mario's bar forbids. Spend the 30 minutes saved on item 1 (trigger-brief smoke) where the dark-code surface is large and v1's data does not apply, and run v2's fidelity script for the first time against items 1 and 2's outputs once those exist.
