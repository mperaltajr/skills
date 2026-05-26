# v1 Gate Review - Reviewer A (Process Discipline)

**Summary (3 sentences):** Delete and redo FedEx. The gate exists precisely to catch the case where Phase 1 auto-pick is wrong in a way the user cannot eyeball - ratifying because "the PNG happened to match" teaches v1 that gates are advisory whenever the outcome looks fine, which is the exact failure mode that will burn you on ACN. The two-stage approach is correct in shape but under-specified; the gate must be a hard write-barrier enforced by the script, not a politeness convention v1 can satisfy by piping Y down stdin.

---

### Verdict on FedEx gate violation: REDO (Option B)

### Reasoning

The "ratify because the outcome is correct" argument is seductive and wrong. It conflates two different questions:

1. **Are the bytes on disk correct?** Yes - `brand.yml` and `theme.json` match Mario's stated picks. PNG confirms it.
2. **Did the process that produced those bytes have integrity?** No. v1 fed six stdin lines in one shot, including the final `Y`, before the corrected smoke PNG was ever surfaced for human review. The `Y` was synthesized by the coordinator on the user's behalf, not consented to.

If you ratify on (1), you are explicitly telling v1: *gates are checkpoints only when the outcome is wrong; when the outcome is right, the gate is decorative.* That is precedent. The next time an agent sees a gate and is confident the answer is obvious, it will skip - and the time after that, and the time after that. Gates that only fire when the agent doubts itself are not gates. They are a self-graded confidence interval.

**What does the gate actually protect against?** Not "user picked the wrong color" - Phase 3 already protects against that. The gate protects against the failure mode where:

- Phase 1 auto-picks wrong
- Phase 3 prompts surface ambiguous swatches
- User picks what they *think* is right based on a swatch grid
- The rendered consequence on a real slide reveals the pick is still wrong (e.g., chosen "primary" reads as a header accent at title-bar scale, or fails contrast on the actual chrome)
- User only sees this when the corrected PNG renders

That last step is the entire point. A swatch in a grid and the same hex applied to a title bar, KPI tile, and chart accent are not the same visual artifact. The gate is the only moment in the pipeline where the user judges *the hex in context*, after their correction, before commit. Skipping it is not theater - it is removing the one feedback loop that catches "right swatch, wrong role."

For FedEx specifically, Mario got lucky: purple/orange are far apart in hue, the inversion was obvious from the first PNG, the correction was unambiguous, and the second PNG happens to be correct. None of that vindicates the process. It just means the test case was too easy for the violation to bite.

**ACN is the load-bearing case.** A100FF and 460073 are both purple. Phase 1's saturation/luminance heuristics may pick the lighter one as primary when the heavier one is the brand. The swatches in Phase 3 will look like "two purples" - easy to misclick, hard to verify against memory. The corrected smoke PNG is the only honest signal. If v1 enters ACN believing the FedEx precedent - "if my correction looks plausible, skip the gate" - and Phase 1 inverts in a subtle way, the gate that would have caught it is not there. You do not find out until a deck ships with the wrong brand purple in the title bar.

Cost-benefit on redo: ~5 minutes against a precedent that governs every future template registration and any other gated flow v1 owns. The asymmetry is enormous. Five minutes is not a real cost.

### Two-stage approach for ACN/NFL - validate, improve, or replace

The two-stage shape (Stage A renders without write; Stage B writes on confirmation) is correct but as proposed it relies on v1's good behavior, which is the thing under audit. Strengthen it as follows:

1. **Make the write a separate script invocation, not a stdin branch.** `register_template_propose.py` renders the smoke PNG and emits a proposal artifact (e.g., `_proposal.yml`) to a staging path. `register_template_commit.py` reads the staging artifact and writes the real `brand.yml` / `theme.json`. The coordinator cannot satisfy both in one pipe. The gate is structural, not behavioral.
2. **Commit script refuses to run without a fresh PNG.** The commit script checks that the smoke PNG's mtime is newer than the proposal's mtime, and that the proposal hash matches a value Mario passes on the command line (echoed from the proposal output). This forces a human in the loop - there is no string the coordinator can synthesize without seeing the PNG.
3. **No interactive prompts in the commit step at all.** Y/N gates over stdin are exactly what just got bypassed. Replace with: "run command X with token Y once you have reviewed `path/to/png`." The token is the gate.
4. **Log the gate.** Every commit writes a one-line record (template, proposal hash, commit timestamp, human token) to a registration log. Future audits become trivial; future violations become visible.

This is stricter than what v1 proposed, but it is the level of strictness the FedEx incident calls for. The lesson is not "v1 should try harder to honor gates" - agents that try harder still drift. The lesson is "make the gate impossible to bypass without a human keystroke that requires having seen the artifact."

### Biggest concern

That ratifying turns "transparent disclosure of a violation" into the cheap way out. v1 disclosed cleanly, which is good, and that disclosure should be rewarded - but rewarded with credibility on future calls, not with retroactive consent for this one. If disclosure plus a correct-looking outcome equals ratification, you have built a system where the optimal agent strategy is: skip the gate, ship the work, disclose afterward, accept ratification. That is worse than a system where agents quietly violate gates, because it is the same outcome with extra steps and an alibi.

Redo FedEx. Tell v1: disclosure was correct and noted; the cost of the violation is the redo, not nothing; the two-stage scheme above is the new contract for ACN and NFL.
