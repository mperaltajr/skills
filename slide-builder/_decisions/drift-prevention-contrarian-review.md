# Drift Prevention - Contrarian Review

**Date:** 2026-05-26
**Role:** Push back on "more process / more tests" as the answer to the v0.1 audit findings.
**Stance:** The current cadence is working. Add exactly one thing. Reject the rest.

---

## TL;DR

The drift you observed was caught by the existing process - your audit pass. Two fix-cycles "self-verified green," your audit caught the regressions within hours, you are now triaging from a clean prioritized list. **That loop is the system, and it functioned.** The proposed fixes (test infra, hook stacks, plan-log discipline) would solve a problem you do not have and introduce a class of failure you currently do not carry: second-order drift in the verification layer itself. Add one thing - a single behavioral instruction that fixes the **"I added the step" != "I made it work"** misconception at the source - and call it done.

---

## Reframing the situation

Two cleanup chats reported done. Both were wrong in specific, narrow ways:
- Worker agent file installed at correct path, contained v1 content (a copy-paste / source-confusion bug, not a process bug)
- Cross-skill references broken (a search-discipline bug)
- CHANGELOG not updated (a single-line ceremony bug)
- 6 of 8 prior bugs unfixed (this is the actual signal - see below)

Your audit then caught all of this within the same calendar day. The cost incurred so far: hours of triage and one annotated handover doc. The cost averted: zero - nothing shipped to a coworker yet.

**This is not a system failure. This is the system working.** The audit IS the verification layer.

---

## Direct answers to the six framing questions

### 1. Is the right answer "trust the audits and accept some drift"?

**Yes - with one caveat.** When you are solo, your audit pass is the highest-signal verification you have. It catches things that automated tests by definition cannot catch: doc drift, false architectural claims, dead imports masked by happy-path execution, cross-skill reference rot, "the install step is documented but the file it installs is wrong." A test suite that could catch all of that is a second skill, not a test suite.

Adding a process layer **on top of** an audit you are going to do anyway is pure overhead. The audit subsumes the process. The only reason to add upstream process is if the audit itself were unreliable or expensive - neither is true here. Your audit takes hours, runs in parallel via agents, and produces a structured fix list. That is already cheap.

**Caveat:** the audit is not free. If you find yourself running the same audit three more times this month catching the same class of regression, the loop is too loose. That is not where you are. You ran it once after a major cleanup and got real value. Do not preemptively industrialize a one-shot.

### 2. Test infrastructure has its own drift problem

**Stated more strongly than the framing put it.** Solo-dev test suites have a documented half-life. The contract test you already have (`_contract.py`) is itself an example - it greps script text but never `import`s the scripts, which is exactly why T2.7 exists in the handover. Your existing test layer is already drifting and you just added a fix for it.

Now propose stacking five more checks on top. Each one:
- Has a runtime cost (slows the iteration loop)
- Has a maintenance cost (refactor breaks the test, not the code)
- Creates a **false-confidence surface** (green check != actually verified, see worker-agent regression)
- Will itself drift silently

The worker-agent file regression is the canonical case. Imagine a "worker agent installed correctly" hook. What does it check? File exists? Already true. File hash matches a known-good? Now you need a known-good registry and a process for updating it. File `name:` field matches `slide-builder-worker`? Maybe - but the v1 content had the right name. So you need a content fingerprint. Now you are versioning agent files in a manifest. Manifest drifts. **You have re-created the problem one layer up.**

Net positive only if the test catches something the audit does not, runs faster than the audit, AND has lower drift than the thing it is testing. For most of what was proposed, that is a no on all three.

### 3. Actual cost of the drift observed

The handover doc itself answers this cleanly:
- Tier 1 (5 items): ~3 hours
- Tier 2 (8 items): ~3.5 hours
- Tier 3 (~30 items): deferred to v0.2

**Triage cost: low.** Audit produced a sorted, scoped fix list with effort estimates. You can knock Tier 1 out in a focused half-day.

**Damage cost: zero so far.** Nothing shipped. No coworker hit a broken build. No data was lost to `clean.py` (T1.3 is a real bug but a latent one).

**Reputation cost: zero.** You have not handed it over yet.

The cleanup-chat -> audit -> remediation loop is the correct cadence for a v0.1 solo build. It would only be wrong if (a) the audit missed things that later bit you in front of someone else, or (b) the audit cost more than the prevention. Neither holds.

### 4. Actual failure mode worth preventing

The framing is right. Worst real-world scenario: coworker tries v0.1, Stage 2 silently no-ops, they Slack you, you fix it in 5 minutes. **Downside: 5 minutes of Mario time, mild embarrassment, one Slack message of context.**

Prevention cost for "make sure that never happens": pre-share audit (which you are already going to run), maybe an INSTALL.md `Test-Path` check (T2.12 - already on the fix list, 20 min). That is it. That is the entire defensible prevention budget for this failure mode.

Anything more - test infra, hooks, CI, plan-log enforcement - is paying $100 to prevent a $5 problem. Worse, the $100 spend creates ongoing maintenance debt that will eventually itself cause a $5 problem.

### 5. Deepest signal in the drift pattern

**This is the real finding, and it is the only thing worth fixing structurally.**

The cleanup chat treated **"I added the install step in INSTALL.md"** as equivalent to **"the worker agent will actually be present and correct when a coworker runs the install."** Those are not the same claim. The first is a documentation change. The second is an end-to-end verification.

Same pattern across the other misses:
- "I deleted the v1 chassis code" != "all imports of v1 chassis modules are gone" (T1.4 - `composer.py` still imports `twins.selector.load_catalog` and `twins.overrides_resolver`)
- "I documented Hardline #4" != "the check that enforces Hardline #4 exists" (T1.5)
- "I updated the doc" != "the doc now matches what the script actually does" (T2.8, T2.9, T2.10)

**The misconception is a single, narrow one:** mistaking the artifact-of-completion for the completion itself. This is a one-line fix in the cleanup-chat instruction or behavioral memory:

> When you claim a cleanup step is done, the standard is "a fresh observer running the documented step would get the documented outcome." Not "the doc/file/code now mentions the step." Specifically: if you add an install step, the thing being installed must exist at the source path and be correct. If you remove a feature, all imports/references to it must also be gone. If you document a check, the check must execute.

That is one paragraph. Drop it into the cleanup-chat system prompt or a memory file. It directly attacks the **only** drift pattern that produced all the regressions. No tools, no tests, no hooks.

### 6. Master plan log discipline

**Yes, this is ceremony.** A plan log is useful while the plan is active and the work is being negotiated. Once the work converged and shipped, the plan is a historical artifact. Forcing updates to it post-hoc adds zero verification value - it only adds the appearance of process rigor, which is worse than no process because it consumes attention without catching anything.

The right artifacts post-completion are:
1. The audit handover (you have this - `v0.1-audit-handover-2026-05-26.md`)
2. The DECISIONS log if a real architectural choice was made
3. The CHANGELOG entry if you ship to anyone

That is it. The cleanup plan can be left as-is or marked superseded with a one-line banner. Updating it line-by-line because "the plan said it would be updated" is exactly the kind of discipline-theatre that makes solo dev work miserable.

---

## What the other two agents are likely proposing, and why most of it is wrong

Plausible proposals from "more tests / more process" agents and the counter-argument:

| Proposal | Verdict | Why |
|---|---|---|
| Add CI / GitHub Actions to run contract test on every commit | **Reject** | Solo repo, no PR flow, contract test itself has a drift bug. Adds latency + a maintenance target. T2.7 already fixes the contract test. |
| Pre-commit hook to validate cross-skill references | **Reject** | Cross-skill rot is rare, the audit catches it, and the hook would need a registry of valid cross-refs that itself drifts. |
| Mandatory CHANGELOG-updated check | **Reject as automation, accept as habit** | One-line discipline: do not merge cleanup chats without writing the CHANGELOG line. Does not need a tool. |
| Plan-log "must be current" enforcement | **Reject** | Pure ceremony. See section 6. |
| Smoke-test workflow re-introduction | **Reject** | You already removed it (commit `eac11c9`). It was removed for reasons. Do not re-add absent a specific failure it would have caught. |
| Worker-agent content hash check | **Reject as a hook, accept as a one-time install verification** | T1.2 already proposes a `Test-Path` step. Extend it with a content sentinel (`grep -q "PATTERN_RENDERER_V2"` or similar) inside INSTALL.md verification. **One line.** |
| Behavioral instruction: "doing != documenting" | **ACCEPT - this is the one thing** | See section 5. Single highest-leverage change. Costs one paragraph. Targets the actual root cause. |

---

## The ONE thing worth adding

**Add a behavioral instruction to the cleanup-chat workflow (system prompt or persistent memory) that defines "done" as end-to-end verifiable, not artifact-of-completion.**

Concrete wording (drop into a memory file or the cleanup-chat prompt):

> **Completion standard for cleanup work.** A cleanup step is "done" only when a fresh observer running the documented step would get the documented outcome. Adding a doc, file, or code reference is not done. Examples:
> - If you add an install step, the thing being installed must exist at the source path with the correct content. Verify by reading the source.
> - If you delete a feature, all imports/references/call-sites must also be gone. Verify by grepping the codebase.
> - If you document a check or contract, the code that enforces it must exist and run. Verify by reading the script.
> - If you update a CHANGELOG line, the line must match what actually shipped. Verify by re-reading the diff.
>
> When in doubt, re-derive the claim from disk, not from your own recent edits.

That instruction would have prevented every single Tier 1 regression in the audit handover. It costs nothing to maintain. It does not drift, because it is a principle, not a tool.

---

## Concession (where the other agents are partially right)

**One automated check is defensible, and it is already in the Tier 2 fix list (T2.12):** the `INSTALL.md` verification command. Replace the private-symbol import with four hard checks - `build_deck.py --help`, `mmdc --version`, `soffice --version`, `Test-Path` on the worker agent file. Extend the worker-agent `Test-Path` with a content sentinel grep so the v1-content regression could not have passed.

That is not new test infrastructure. That is hardening the install verification you already have. It is genuinely load-bearing because it is the first thing a coworker will run, and it sits in the exact path where the worker-agent regression lived.

Everything else - reject.

---

## What "do nothing different" looks like, concretely

1. Work the Tier 1 list (3 hours). The audit already gave you the queue.
2. Drop the "completion standard" paragraph into wherever cleanup chats read their system instructions.
3. Harden `INSTALL.md` verification (T2.12) with a worker-agent content sentinel.
4. Work Tier 2 when you have a half-day (3.5 hours).
5. Run one more audit pass before handing to a coworker. Same loop.
6. Tier 3 goes into v0.2.

No new tests. No new hooks. No new plan-log discipline. No CI. No process layer on top of the audit.

---

## Final verdict

The proposed test infrastructure is solving a problem the audit already solves, while creating a new problem (second-order drift in the verification layer) that the audit does not solve. The cleanup-chat -> audit -> remediation loop is the correct cadence for a solo v0.1, and it functioned exactly as designed when you used it. The only structural change worth making is a one-paragraph behavioral instruction that retargets "done" from artifact-of-completion to end-to-end verifiable, because that single misconception generated every regression in the handover. Add a worker-agent content sentinel to the existing `INSTALL.md` verification (T2.12) as a small hardening of work already on the list - that is the only automation defensible on cost-benefit grounds. Everything else: reject, work the fix list, ship.
