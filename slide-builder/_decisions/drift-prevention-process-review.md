# Drift Prevention - Process Review (v0.1 Cleanup to v0.2 Backlog)

**Date:** 2026-05-26
**Author:** Process-review committee (this chat)
**Audience:** Mario, his next cleanup chat, his next audit chat
**Scope:** Workflow protocols, not code. How to stop the "green check / real bug" pattern from recurring.

---

## Verdict (read first)

The protocol is broken in three places: **definition-of-done is existence-only, not content-equivalence**; **self-verification is treated as terminal when it should be a draft**; and **the master plan status log abruptly stopped getting written at the v0.1 ship line, so the next chat has no on-disk record of what is actually pending**. Highest-leverage change: a **mandatory two-line "DoD card"** that every fix-ticket must produce on disk (`_decisions/dod-cards/T<n>.md`) carrying (1) the content-level invariant the fix established and (2) the grep/command that would catch its regression - and a hard rule that **no cleanup chat is permitted to declare a Tier complete; only the audit chat declares**. Everything else in this doc is mechanics for those two rules. Tier-3 ordering and memory encoding are minor compared to fixing the gate.

---

## 1. Definition of done - per fix-class

"Test-Path passes" is not done. It is existence. A fix is done when the *intent* is enforced - the behavior the doc claims is the behavior on disk. Different fix-classes have different intents; one checklist does not work.

### Mandatory DoD card (universal)

For every Tier-1 / Tier-2 fix, the cleanup chat writes `slide-builder/_decisions/dod-cards/T<tier>.<n>-<slug>.md` with **exactly this structure** before declaring the fix complete:

```
# T1.2 - Worker agent install step

## Intent (what "fixed" means)
A coworker following INSTALL.md ends up with a file at
%USERPROFILE%\.claude\agents\slide-builder-worker.md whose content
matches slide-builder/agents/slide-builder-worker.md byte-for-byte.

## Files touched
- slide-builder/INSTALL.md (Step 6 added, lines 86-125)
- slide-builder/agents/slide-builder-worker.md (source-of-truth created)

## Regression guard (one-liner that would fail if this regresses)
fc /b "%USERPROFILE%\.claude\agents\slide-builder-worker.md"
   "%USERPROFILE%\.claude\skills\slide-builder\agents\slide-builder-worker.md"

## Content invariant
The shipped agent first 10 lines must contain "geometric pattern",
"14 patterns", and "FALLBACK_MERMAID" - markers proving v0.1 (not v1) content.

## Self-verification run
[paste the actual command output here, not a check mark]
```

The "content invariant" line is the load-bearing one. It is the answer to "Test-Path passed but the content was v1-era." If the cleanup chat cannot articulate an invariant stronger than existence, the fix is not ready.

### Per-class invariants

| Fix class | Existence check (insufficient) | Content invariant (sufficient) |
|---|---|---|
| File install (worker agent, brand.yml) | Test-Path | byte-equal or hash-equal to source-of-truth; OR grep for 2-3 v0.1-distinguishing markers |
| Doc rewrite (SKILL.md section) | section header exists | Grep for the OLD false claim, expect zero hits; Grep for the NEW claim, expect >=1 hit |
| Script behavior change (clean.py safety) | script imports / --help works | execute the failure path: `clean.py --out C:\` must refuse with documented error |
| Cross-skill reference (storyline-helper handoff) | the target file still exists | Grep the CONSUMER skill for the dead command name, expect zero; manual end-to-end handoff invocation |
| Path rename (Phase 8) | new path exists | Grep -r the entire .claude/ tree + memory + settings.json for the OLD name, expect only documented forensic hits |
| Schema bump (META_SCHEMA_VERSION) | constant changed | contract test exercises the new schema AND every reader pydantic-validates a fixture at the new version |
| Deletion (12 v1 slugs) | Test-Path returns false | Grep the rest of the tree for REFERENCES to the deleted item, expect zero broken pointers |

### Rule

A DoD card lives next to the master plan. If a Tier item has no DoD card, **it is not done**, regardless of what the cleanup chat summary says. The audit chat reads only the DoD cards plus the master plan status log - not the chat transcript.

---

## 2. Self-verification vs independent audit

**Current pattern (broken):** cleanup chat fixes -> cleanup chat self-verifies -> cleanup chat declares done -> Mario asks audit chat -> audit catches regression -> loop.

**The cleanup chat self-verification is not adequate to declare done, ever.** Three reasons:
1. The cleanup chat DEFINED the scope of the fix, so it cannot impartially scope the verification. The worker-agent example is exactly this: cleanup chat scoped "file installed" so verified existence. An independent chat would have scoped "coworker can run Stage 2" and verified content.
2. The cleanup chat has narrative momentum. After 5 hours of work, "done" pressure is real. Confirmation bias is structural, not a moral failing.
3. The cleanup chat carries the master plan in its context. It has read the rationale for the fix. The audit chat reads only the code and the docs - which is exactly what a coworker reads.

### Forcing function

The cleanup chat **never declares a Tier complete**. It declares each FIX complete (writes the DoD card), then writes a Tier-status entry to the master plan that says one of:

- `T1 - claimed-complete-by-cleanup, pending-audit-2026-05-26`
- `T1 - audit-confirmed, 2026-05-26`
- `T1 - audit-flagged regressions: <list>, recycled-to-cleanup, 2026-05-26`

Only an audit chat - running in a fresh session, given only the master plan + DoD cards + the v0.1 disk state - can move a Tier to `audit-confirmed`. Mario triggers the audit; the cleanup chat is not allowed to skip this step "because the changes were small."

### When self-verification IS adequate

- Single-file syntactic fixes where the regression guard is mechanical (e.g., `_contract.py` passes; `--help` exit 0). These can be self-attested in the DoD card without an audit chat.
- Pure deletes where the DoD card grep-for-references comes back clean.

Everything cross-cutting (rename, install path, cross-skill, schema, doc-vs-code) requires audit-chat sign-off.

### Handoff template

The cleanup chat ends its session with a single paste-ready prompt for the audit chat. Format:

```
Audit T1 of slide-builder v0.1 cleanup.

Inputs:
- Master plan: slide-builder/_decisions/cleanup-plan-master-2026-05-26.md
- DoD cards: slide-builder/_decisions/dod-cards/T1.*
- Tier-1 fix list source: slide-builder/_decisions/v0.1-audit-handover-2026-05-26.md

For each T1.x:
1. Read the DoD card Content invariant and Regression guard.
2. Execute the regression guard from a fresh shell.
3. Independently re-grep the codebase for the OLD false claim the fix supposedly removed.
4. Flag any T1.x where the regression guard passes but you find a way to break the intent.

Output a single audit report at:
slide-builder/_decisions/audit-T1-<date>.md
with one of: audit-confirmed | audit-flagged: <list>.
```

Mario keeps this paste-ready prompt in `_decisions/_handoff-templates/cleanup-to-audit.md` so he does not have to recompose it each cycle.

---

## 3. Master plan status log

The master plan log stops being maintained at the Phase 8 verification entry. There are now post-v0.1 fix cycles ("Tier 1 blockers + Tier 2 audit fixes" per the recent commit) that exist in git history but NOT in the master plan. The next chat starting cold has no on-disk index of what was done after v0.1 ship.

### Discipline

Three rules, no exceptions:

1. **Append-only status log section.** After the Phase 8 verification block, add a new section `## Post-v0.1 fix cycles`. Every fix cycle gets a dated subsection with: tier scope, DoD cards landed, audit verdict, follow-ons surfaced. The cycle is not declared complete until this section is updated.
2. **Writeback gate.** The cleanup chat last act of the session is to update this section. Treat it as part of the work, not documentation about the work. If the master plan was not updated, the cycle did not happen.
3. **CHANGELOG mirror.** The `[Unreleased]` section of CHANGELOG.md gets one bullet per audit-confirmed fix cycle (not per fix - per cycle). When v0.2 ships, `[Unreleased]` becomes `[v0.2]`. This is the user-facing mirror of the internal master plan log.

The CHANGELOG today has empty Added/Changed/Fixed placeholders in `[Unreleased]` and zero post-v0.1 entries despite real post-v0.1 work having shipped (per git log: "Tier 1 blockers + Tier 2 audit fixes"). That is the visible symptom of the missing discipline.

---

## 4. Tier ordering

Current pattern: Tier 1 done, Tier 2 partial, Tier 3 ignored, backlog grows.

The right answer is NOT to attack Tier 3 earlier. The right answer is **time-boxed Tier 3 sweeps interleaved between Tier-1/2 cycles** so the backlog has a known maximum age.

### Protocol

- **Tier 1** runs to completion in each cleanup cycle. Non-negotiable; T1 items are blockers by definition.
- **Tier 2** runs to completion IF the cycle has remaining budget after T1 + the T1 audit pass.
- **Tier 3** does NOT compete with T1/T2 for the cleanup chat attention. Instead: **every third cleanup cycle is a "Tier-3 sweep cycle"** - no new T1/T2 work, just batch-process 10 T3 items. Items not addressed in a sweep cycle stay in the backlog with an age counter. When an item age counter hits 3 (survived three T3 sweep cycles), it is either promoted to T2 (Mario decides it matters) or formally retired with a one-line rationale in the master plan.

The "age counter" forces honesty. Items that bounce three sweeps are either important enough to be T2 or unimportant enough to delete. The graveyard of "we will get to it" goes away.

### Where the Tier list lives

Today: `_decisions/v0.1-audit-handover-2026-05-26.md`. Fine for v0.1.

Going forward: the Tier list should be a single living file, `_decisions/_backlog.md`, with sections `## Tier 1 (open)`, `## Tier 2 (open)`, `## Tier 3 (open)`, `## Done (chronological)`. Each item carries `added: YYYY-MM-DD` and `age-counter: N`. When items move tiers, the move is logged in `## Done`. This file is the single source of truth - every audit and every cleanup chat reads only this and the master plan.

---

## 5. Cleanup to audit handoff

Mario manually moves between chats today. That is a forcing function (because the chats cannot see each other) but it is also a drop-on-the-floor risk.

### Protocol

Three artifacts, all on disk:

1. **`_decisions/_handoff-templates/cleanup-to-audit.md`** - the paste-ready prompt template (Section 2). Mario copy-pastes when starting the audit chat. The template hardcodes the file paths so the audit chat reads the right inputs.
2. **`_decisions/_handoff-templates/audit-to-cleanup.md`** - the reverse, used when the audit flags regressions and Mario opens a fresh cleanup chat. Format: "T1.x flagged: <regression>. Read the original DoD card at <path>. Produce a new DoD card at <path> for the fix."
3. **`_decisions/dod-cards/_INDEX.md`** - running index, one line per DoD card with status `[claimed | audit-confirmed | flagged | recycled]`. Mario glances at the index between chats and instantly sees what is pending.

The pattern Mario should adopt: **one chat session = one tier worth of work**. Do not try to do T1 + T2 in the same cleanup chat. Do not try to do "T1 cleanup + T1 audit" in the same chat (that is the broken self-verification). One session = one of {cleanup-T1, audit-T1, cleanup-T2, audit-T2, sweep-T3}.

### Anti-pattern to retire

The "let us keep working in the same chat across phases" pattern (Amendment C / `feedback_continuous_execution.md`) was right for the master Phase 1-8 plan because each phase had explicit DoD criteria from Phase 0 and an audit-chat verification at the end. It is the WRONG pattern for post-v0.1 fixes where the cleanup chat is also the verifier. Amend the continuous-execution memo to say: "continuous across phases inside a single planned cleanup - yes; continuous across fix -> verify -> declare-done - no."

---

## 6. Memory of past drift

Two pieces of drift-class knowledge should land as memory files. Both should be created.

### memory/feedback_existence_vs_content.md

```
Title: "Existence-check is not done. Content-equivalence is done."

When verifying a fix that installs, copies, or restores a file:
- Test-Path / file-exists / ls confirms only that A file is there.
- The file content can still be v1-era / stub / wrong version.
- The DoD must include a content invariant: byte-hash, marker-grep,
  or executed-behavior. No exceptions.
- Originating example: worker agent file "installed" but content was
  v1-era; existence check passed; coworker would have hit the wrong
  agent at runtime.

Cross-reference: slide-builder/_decisions/dod-cards/<*>.md
```

### memory/feedback_cleanup_chat_cannot_self_declare.md

```
Title: "Cleanup chat declares fixes complete, never tiers."

A chat that did the fix work cannot impartially verify the fix
landed. It scoped the fix, has narrative momentum, and carries
context that the next reader (coworker / audit chat) does not.

Protocol:
- Cleanup chat: writes per-fix DoD cards, marks Tier as
  "claimed-complete-by-cleanup, pending-audit."
- Audit chat: runs fresh session, reads only DoD cards + master
  plan + disk state. Moves Tier to "audit-confirmed" or "flagged."

Originating example: post-v0.1 Tier-1 work declared complete by
cleanup; subsequent audit chat caught: worker-agent content drift,
INSTALL Step 6 existence-only, Phase 8 missed cross-skill refs in
slide-qc + rfp-helper, CHANGELOG not updated, master plan log
abandoned at v0.1 line.
```

### Updates to existing memory

- **feedback_committee_on_everything.md** - add a carve-out clarification: "Audits performed by a fresh chat with no cleanup-narrative context substitute for committee on verification questions. The fresh-chat-vs-same-chat axis matters more than the agent-count axis for verification."
- **feedback_continuous_execution.md** - append the amendment from Section 5 above ("continuous across phases yes; continuous across fix -> verify no").

### Memory index update

Add the two new entries to MEMORY.md index in the same line-style as the existing entries.

---

## 7. Mario actions - step-by-step (per memory feedback_action_step_by_step.md)

### Action 1 - Create the DoD card directory + template

1. Open a fresh chat or PowerShell.
2. Create: `New-Item -ItemType Directory "C:\Users\m.a.peralta\.claude\skills\slide-builder\_decisions\dod-cards" -Force`.
3. Create: `New-Item -ItemType Directory "C:\Users\m.a.peralta\.claude\skills\slide-builder\_decisions\_handoff-templates" -Force`.
4. Ask the next chat to populate `_handoff-templates/cleanup-to-audit.md` and `_handoff-templates/audit-to-cleanup.md` using the templates in Sections 2 and 5 above.
5. Done state: both directories exist; both template files exist; Test-Path on each returns true; the templates contain the paste-ready prompt text.

### Action 2 - Backfill DoD cards for the post-v0.1 Tier 1 + Tier 2 work that already shipped

1. Ask a fresh chat (audit role): "Read commits 838a364 and any subsequent. For each fix in Tier 1 blockers + Tier 2 audit fixes, produce a DoD card per the template at _decisions/dod-cards/_TEMPLATE.md. Save to _decisions/dod-cards/T<n>.<m>-<slug>.md."
2. Expected output: ~10-15 DoD cards covering the fixes that already shipped without DoD discipline.
3. Done state: every commit message item in 838a364 has a corresponding DoD card on disk; running an audit cycle against those DoD cards either confirms or flags each one.

### Action 3 - Update the master plan with a Post-v0.1 fix cycles section

1. Open `_decisions/cleanup-plan-master-2026-05-26.md`.
2. After the Phase 8 verification block (ends around line 232), append a new section:
   ```
   ## Post-v0.1 fix cycles

   ### Cycle 1 - Tier 1 blockers + Tier 2 audit fixes (2026-05-26, commit 838a364)
   Status: claimed-complete-by-cleanup, pending-audit.
   DoD cards: see _decisions/dod-cards/T1.* + T2.* (backfilled per Action 2).
   Follow-ons: (list any that surfaced)
   ```
3. Done state: section exists; the next cleanup chat reading this file sees both the v0.1 ship line AND the post-v0.1 cycle status.

### Action 4 - Update CHANGELOG [Unreleased] to mirror the master plan post-v0.1 cycles

1. Open `slide-builder/CHANGELOG.md`.
2. Under `[Unreleased] / Fixed`, add bullets for the Cycle-1 work (worker-agent install, INSTALL Step 6 content, clean.py safety, etc.). Source: the master plan Post-v0.1 section, summarized.
3. Done state: `[Unreleased]` is no longer empty; it mirrors the master plan post-v0.1 entry.

### Action 5 - Create the two new memory files

1. Write `memory/feedback_existence_vs_content.md` with the content in Section 6 above.
2. Write `memory/feedback_cleanup_chat_cannot_self_declare.md` with the content in Section 6 above.
3. Update MEMORY.md index with two new entries (one line each, same format as existing).
4. Append the amendment to `feedback_continuous_execution.md` and the carve-out to `feedback_committee_on_everything.md`.
5. Done state: 2 new files exist; MEMORY.md has 2 new index entries; 2 existing memory files have the appended clarifications; total memory file count went from 16 to 18.

### Action 6 - Trigger the audit of Cycle 1

1. Open a fresh chat.
2. Paste the cleanup-to-audit template (populated to point at the Cycle-1 DoD cards from Action 2).
3. Wait for the audit verdict file at `_decisions/audit-T1-<date>.md`.
4. If verdict is `audit-confirmed`: update master plan + CHANGELOG to move Cycle-1 from `pending-audit` to `audit-confirmed`.
5. If verdict is `audit-flagged`: open a fresh CLEANUP chat with the audit-to-cleanup template; the cycle stays open.
6. Done state: Cycle 1 has a verdict on disk; the master plan reflects the verdict; the next cycle can begin.

---

## What I am NOT recommending (deliberately)

- A pre-commit hook that runs the contract test. The contract test already passes today; the bugs we are catching are not contract-test-detectable. Adding more automation around the wrong gate does not help.
- Splitting the master plan into multiple files. Single living doc + appended cycle log is cleaner for a solo consultant.
- A formal ticket tracker (GitHub Issues, Linear, etc.). Backlog.md inside the repo is enough; the friction of an external tool is not worth it at this team size.
- Requiring three audit chats per cycle. One fresh audit chat is sufficient if the DoD cards are tight. Committee-on-everything applies to STRATEGIC decisions, not to verification mechanics - the audit chat is itself the second opinion.

---

## TL;DR (action surface only)

1. Create `_decisions/dod-cards/` and `_decisions/_handoff-templates/`.
2. Backfill DoD cards for the post-v0.1 work that already shipped.
3. Add `## Post-v0.1 fix cycles` to the master plan; keep it updated.
4. Update CHANGELOG `[Unreleased]` to mirror the master plan.
5. Add two memory files (feedback_existence_vs_content, feedback_cleanup_chat_cannot_self_declare); amend two existing.
6. Trigger an audit chat for Cycle 1. Only the audit chat can move a Tier to audit-confirmed.
