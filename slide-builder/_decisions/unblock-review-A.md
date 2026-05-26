# Unblock review — Reviewer A (coordination / sequencing angle)

Blind review. Item 1 smoke halted at Stage 3 (finalize) on two unrelated blockers: v1 shipped its `brand.yml` / `theme.json` sidecar rewrite mid-smoke (every template now raises `BrandSidecarMissing`), and `mmdc` was never installed. v2 had proposed Path beta + a gamma-partial mmdc install. My angle: was this avoidable at the coordination layer, and what does Mario''s "no deferral patterns" bar imply about cross-stream contracts?

## Verdict on Path alpha / beta / gamma / delta

**Reject Path alpha as primary.** Alpha tries to push through the breakage in one combined motion: install mmdc, register two templates interactively, and patch v2''s `generate_mermaid_theme()` to consume `.theme.json`. The patch is the problem. Touching `build_deck.py`''s theme-resolution code path *while* an item-1 smoke is mid-flight, under unblock-pressure, is exactly how silent regressions enter v2. v2 spent two Gate-3/Gate-4 audits proving how easy it is to drift contracts across forked scripts (`sys.argv`, the `themed/` path). Doing a third contract change hot, in the middle of validating the first item, is reckless.

**Reject Path beta as written.** Beta documents the problem and waits. That''s fine for the v1 sidecar issue (genuinely upstream, genuinely Mario-blocking), but it''s wrong for mmdc. mmdc is a v2 prerequisite that v2''s own `fallback.md` declared and never validated. That''s not cross-stream — it''s a v2 hygiene miss. Bundling it with the v1 wait flatters v2.

**Accept Path gamma, with a stronger framing.** Install mmdc now — it closes a v2 prerequisite gap that should never have existed past v0 setup. Then halt items 1+2 on the v1 sidecar issue until two preconditions are met: (1) Mario has run `register_template.py` for FedEx and ACN, producing the sidecar pair next to each template; (2) v2 has landed and *self-tested* the `generate_mermaid_theme()` migration on a throwaway scratch slide — not as part of the item-1 smoke. Only then re-fire item 1.

**Path delta — freeze v1 at pre-migration commit for v2''s smoke duration — is the wrong instinct.** It treats the symptom (v1''s commit broke v2) by pinning v1, which violates v2''s "shared infrastructure: don''t touch, both versions depend on it" rule from DECISIONS.md section "Shared infrastructure." The shared chunk includes `twins/`. If v2 forks a frozen `twins/client_theme.py` to keep its smoke moving, the next v1 fix has to be re-merged into both copies. That''s the disease, not the cure. Pinning is acceptable only if the freeze is *measured in hours* and accompanied by a hard re-baseline commitment. As a structural pattern, no.

## Cross-stream coordination finding

v1 shipped a breaking change to shared infrastructure without a signal to v2. The commit message tells the story: `twins/client_theme.py` was rewritten to require sidecars; the FileNotFoundError-by-default behavior was a deliberate, documented refusal (`BrandSidecarMissing` with a "register first" hint). v1 knew the contract changed. v2 had a documented dependency (DECISIONS.md section "Open — cross-skill dependency on v1 theme rescope") explicitly *anticipating* this work landing. The two streams had the dependency mapped on paper. The protocol failure is that "mapped on paper" was the entire protocol.

**Minimum protocol going forward.** Any change to a `shared infrastructure` artifact (`twins/`, `slide-qc/`, Gate 4 scripts, rotation seeds) requires three things before merge:

1. **A pre-merge inventory of cross-stream callers.** v1 changing `twins/client_theme.py` needed to enumerate v2 callers: `finalize_deck.py`, `build_deck.py::validate_theme()`, `generate_mermaid_theme()`. The inventory becomes a checklist of "either still works, or v2 has a tracked follow-on."
2. **A migration signal — written, dated, visible to the other stream.** Not "Mario knows because Mario was in both chats." A file like `_shared/MIGRATION-LOG.md` that both streams append to and read at the start of any smoke. v1''s `brand.yml` migration entry should have read: "Effective <commit>, `load_client_theme` requires sidecars. v2 callers: re-register templates before next build."
3. **A prep-time sanity check at Stage 1.** Before agent dispatch, `build_deck.py` should call `load_client_theme()` on the target template as a warm-up. If it raises, halt before any agent compute is spent. This converts a Stage-3 runtime failure into a Stage-1 prep failure — orders of magnitude cheaper.

The first two are process. The third is a code change v2 should make this week, regardless of which unblock path is chosen.

## Should v2 have caught this earlier?

Yes — partially. Two distinct misses:

**Miss 1: shared-infra sanity check at prep time.** v2''s HALT-between-gates pattern is supposed to catch breakage early. It caught the sidecar issue at Gate 3 only because Gate 3 actually fired. Stage 1''s `build_deck.py` already does template-related work (`find_template_json`, `generate_mermaid_theme`, `validate_theme`). None of those exercises the v1 loader. A one-line `load_client_theme(template_path)` at the top of `build_deck.py::main()` would have raised `BrandSidecarMissing` before any agent dispatched. Cost to add: 5 minutes. Cost it would have saved: the entire Stage 2 fanout in this item-1 run.

**Miss 2: mmdc prerequisite validation.** `fallback.md` listed mmdc as required. v2''s `build_deck.py` doesn''t check for it. `render_mermaid.py` discovers the absence at runtime when an actual Mermaid fallback fires. For a brief that doesn''t need Mermaid, the check never runs. For a brief that does (item 1, slide 3), it explodes at Stage 3. The same prep-time check pattern applies: at Stage 1, if any slide is forecasted to require the Mermaid path, shell out to `mmdc --version` and halt if missing. If no slide needs it, skip the check.

Both misses are the same shape: **trust-the-runtime instead of verify-at-prep.** Mario''s standing rule — "real A/B will surface it" is not an acceptable deferral — applies here word-for-word. "Real builds will surface shared-infra breakage" is the same deferral pattern in a different costume.

## Biggest concern

The biggest concern is not the unblock — it''s the precedent. If v2 ships item-1 by patching `generate_mermaid_theme()` mid-smoke (Path alpha), the pattern becomes "fix v2''s downstream integration while validating the upstream architecture." That muddles the very thing the smoke is supposed to measure. Item 1 was supposed to answer "does the agent + classification mechanism work end-to-end?" Stage 1+2 results say yes (per the brief). If the unblock pulls Stage 3 fixes into the same audit, we''ll never cleanly say whether item 1 passed the architecture test or passed-with-a-band-aid.

Cleanly separate the streams: (a) install mmdc now (5 min, closes v2 hygiene gap), (b) Mario registers FedEx + ACN templates when convenient (~10 min total), (c) v2 lands `generate_mermaid_theme()` sidecar migration *as its own committed change*, validated against a scratch slide, before item-1 re-fires. The architecture lesson — that v2 needs a Stage-1 shared-infra sanity check and a written migration-log protocol with v1 — matters more than getting item 1 to 30/30 today.
