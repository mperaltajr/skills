# Convergence-hold declaration — slide-builder v0

> **⛔ FORENSIC — RESOLVED by Path D (2026-05-26).** Everything below describes the pre-Path-D state and is historical. Path D is the current state of record.
>
> What's still true: the 9+3+2+1 pattern catalog, FALLBACK_MERMAID protocol, SKELETON_REJECTED protocol, brand.yml canonical sidecar contract, Stage-1 sanity check, and per-slide variant seeds — all preserved post-Path-D and documented in [DECISIONS.md](DECISIONS.md) + [SKILL.md](../SKILL.md).
>
> What's now wrong in the body below:
> - `_meta.json` is at schema_version **2**, not 1 (P1.3 added `brand_primary` + `brand_accent`).
> - **NFL** is fully out of scope. No v1 fallback. `nfl-scope-boundary.md` was deleted in Phase 8.9.
> - **Any other client** is fine — register their template via the chat-driven flow. No `client_allowlist` enforced.
> - `theme/mermaid-brand.json` was deleted in P1.4a (FedEx-shaped default created false-positive). Per-client `mermaid-<slug>.json` only.
> - Stage A / Stage B / Path D-soft lift conditions are moot — Mario overrode them on 2026-05-26 with the Path D consolidation.
> - All "NOT allowed during the hold" items are now allowed (new patterns, schema bumps, refactors, etc.) — they happen under the [cleanup-plan-master](cleanup-plan-master-2026-05-26.md) phase structure.
>
> File retained as the historical record of the convergence rationale. Do not edit the body — the inline contradictions ARE the audit trail.

**Declared**: 2026-05-26
**Status**: RESOLVED — superseded by Path D (same day; Mario override).
**See instead**: [DECISIONS.md](DECISIONS.md) (current architecture) + [cleanup-plan-master-2026-05-26.md](cleanup-plan-master-2026-05-26.md) (Phase 1-8 execution).

---

## Statement

The slide-builder v0 architecture is **locked**. No new features, no refactors of locked components, no scope additions, no client expansions until Stage A returns a result and the next decision is taken.

This is a deliberate hold, not a stall. The lock exists so that:
1. Stage A's v1-NOW baseline measures against a stationary v2, not a moving one.
2. Production use during the hold window is on a known surface — no "did the bug exist last week or this week?" debugging.
3. The accumulated v0 evidence (Item 1, Item 2, cross-client comparison) remains the canonical reference for decisions taken during the hold.

---

## What is locked

### Architecture core

| Component | Status | Reference |
|---|---|---|
| **9 geometric splits** (Full canvas; 50/50 vertical; Asymmetric vertical 75/25; Top band + body; N-column row; Vertical N-row stack; Dense grid; Left rail + body; Horizontal bands) | LOCKED | `reference/layouts.md` |
| **3 diagram primitives** (Org chart; Swimlane; Decision tree) | LOCKED | `reference/layouts.md` |
| **2 special objects** (Chart with quadrant mode; Table) | LOCKED | `reference/layouts.md` |
| **1 fallback path** (FALLBACK_MERMAID for curved-container topologies) | LOCKED | `reference/fallback.md` |
| **5 hardline rules** | LOCKED | `prompt.md` § 6 |
| **7-verb editorial vocabulary** (recommend / warn / diagnose / show urgency / show progress / compare neutrally / summarize) | LOCKED | `prompt.md` § 5 |

### Pipeline contracts

| Contract | Status | Reference |
|---|---|---|
| **brand.yml sidecar** as canonical brand source (read via v1's `twins.client_theme.load_brand_sidecar`) | LOCKED | `scripts/build_deck.py:91` |
| **`_meta.json` deck manifest** at schema_version 1 (template / brief / out / mermaid_theme / client_slug / slide_count / generated_at / slides[{n,title,forecasted_pattern,page_type}] / deck_meta{deck_type,governing_thought,audience}) | LOCKED | `scripts/build_deck.py::write_meta_json` |
| **Stage-1 sanity check** (brand sidecar exists + valid; mmdc installed) before any agent dispatch | LOCKED | `scripts/build_deck.py::stage1_sanity_check` |
| **Per-client Mermaid theme** at `theme/mermaid-<client_slug>.json`, written by build_deck, consumed by finalize_deck via `_meta.json["mermaid_theme"]` | LOCKED | `scripts/build_deck.py::generate_mermaid_theme`, `scripts/finalize_deck.py::_resolve_mermaid_theme` |
| **Loud-failure on missing manifest** (no silent fallback to default theme; exit code 7 with paste-ready re-run command) | LOCKED | `scripts/finalize_deck.py::_resolve_mermaid_theme` |
| **Hardline #5 protocol** (`# SKELETON_REJECTED:` line-1 token; finalize classifies, refuses to build, surfaces with REJECTED badge in REVIEW.html) | LOCKED | `reference/fallback.md`, `scripts/finalize_deck.py::_classify_option` |
| **FALLBACK_MERMAID protocol** (`# FALLBACK_MERMAID:` line-1 token; sibling `.mmd` spec; mmdc renders 1240×540 PNG; embedded in body zone; MERMAID badge in REVIEW.html) | LOCKED | `reference/fallback.md`, `scripts/finalize_deck.py::_render_mermaid_png`, `scripts/finalize_deck.py::_assemble_fallback_pptx` |
| **Forecast-as-context-not-constraint** (forecaster runs at prep; pick happens at agent dispatch; agent overrides when brief signal differs) | LOCKED | `scripts/build_deck.py::forecast_pattern`, `prompt.md` § 3 |
| **Per-slide variant seeds** (`md5(content_hash + slide_n + option_letter)`) | LOCKED | `scripts/build_deck.py::compute_seeds` |
| **Anti-convergence brand-token rule** (each of 3 sibling options must use brand tokens on a DIFFERENT load-bearing element) | LOCKED | `prompt.md` § 5 |
| **Loud-failure on malformed brand.yml hex** (`_hex()` raises ValueError; main() exits 6 with re-register command) | LOCKED | `scripts/build_deck.py::_compute_theme_variables` |
| **Structural theme validation** (primary != accent; plausible saturation; plausible luminance; optional client-hue-range check) | LOCKED | `scripts/build_deck.py::validate_theme` |

### Client scope

| Client | Status | Routing |
|---|---|---|
| **FedEx** | IN SCOPE | v2 default, registered template at `FedEx\_templates\Moving Forward PPT Template.{pptx,brand.yml,theme.json}` |
| **Accenture** | IN SCOPE | v2 default, registered template at `Accenture\_templates\ACN Graphik Template.{pptx,brand.yml,theme.json}` |
| **NFL** | OUT OF SCOPE | Routes to v1. Lift criteria documented in `nfl-scope-boundary.md` |
| **Any other client** | OUT OF SCOPE | Routes to v1. v0.1 candidate: `client_allowlist` field enforcing this at Stage-1 sanity check |

### Evidence base

Three artifacts on disk constitute the v0 evidence base. Decisions taken during the hold reference these:

1. **Item 1** — FedEx trigger-brief smoke. Outcome documented at `_decisions/smoke-test-finding-2026-05-25.md`. Six architectural claims validated end-to-end.
2. **Item 2** — ACN slidelab-intro smoke. Output dir `v2-smoke-2026-05-26-acn`; REVIEW.html at same. 30/30 native built + themed + rendered; ACN purples correct; adjacency advisory fired; topbar `Client: Accenture`.
3. **Cross-client pattern-pick comparison** — `_decisions/cross-client-pattern-pick-comparison-2026-05-26.md`. 9/10 pattern-level agreement between FedEx and ACN runs on the same brief. Single divergence inside documented eligibility set. Bounded non-determinism confirmed.

---

## What is NOT locked (the hold's carve-outs)

The following are explicitly allowed during the hold because they do not change the v2 surface that Stage A is measuring against:

1. **Bug fixes** to code in the locked surface — anything that brings the code into closer agreement with what the locked behavior is supposed to be. (Example: the Windows-console em-dash codepage issue was fixed during Item 2 because it was a cosmetic bug in an already-locked error message, not an architectural change.)
2. **Documentation updates** in `_decisions/` and `README.md`. Including this declaration.
3. **Production use** of v2 on real FedEx or ACN briefs by Mario or registered consultants. The hold means we don't ship changes, not that we don't use the tool.
4. **Template registration** for FedEx or ACN. Adding a new FedEx template or re-registering ACN to correct a Phase 3 inversion is in-scope.
5. **REVIEW.html review-side work** that doesn't touch the build pipeline (e.g., curator workflow, picks.json hand-off, vision-QC dispatching).
6. **Reading and analysis** — running the existing scripts to characterize v2 behavior on additional briefs, producing comparison data, building catalog evidence. None of this writes code in `scripts/`.

The following are explicitly **NOT** allowed during the hold:

1. **New patterns** added to `reference/layouts.md` or any new entries in the 9+3+2+1 set.
2. **New hardlines** beyond the current five, or modifications to the threshold values in Hardline #4 (`PER_SLIDE_MIN`, `DECK_AVG_MIN`, `structural_flag_count`).
3. **Verb vocabulary changes** beyond the seven.
4. **`_meta.json` schema_version bumps** or any reader-visible field renames.
5. **New clients in scope** beyond FedEx + ACN. This includes NFL (held by `nfl-scope-boundary.md`).
6. **Refactors that change the surface area** of `build_deck.py`, `finalize_deck.py`, `build_review.py`, or `compile_picks.py`. Internal cleanups that don't change observable behavior are fine; signature changes, new CLI flags, new outputs are not.
7. **v0.1 work** — the four-item systemic triple (`shared/paths.py`, contract test, pydantic schema validation, CI gate) is documented but NOT being implemented during the hold. v0.1 starts after Stage A returns.

---

## Lift conditions

The hold lifts in exactly one of three ways:

### (1) Stage A returns "gap closed" → permanent A/B cancellation → Path D-soft

If v1-NOW lands materially better than the historical 23% acceptance (concretely: ≥ 60% slide-level acceptance from a v1-aware reviewer on the slidelab-intro brief), the engineering gap that justified v2 has closed inside v1.

In this case:
- The formal A/B is permanently cancelled.
- The project goes **Path D-soft**: v2 is the default for FedEx + ACN; v1 is the documented fallback for any case the operator prefers; NFL stays on v1 until v0.1 lifts the scope boundary.
- The hold lifts and v0.1 work begins. v0.1 priorities (in order): handoff-hardening triple → NFL scope acceptance criteria → QC heuristic tightening → post-pass adjacency check → optional `client_allowlist`.

### (2) Stage A returns "gap persists" → Stage B fires

If v1-NOW still shows the historical gap (≤ ~30% acceptance on the same brief and template), Stage B fires:
- Production pilot on 2 real briefs (FedEx OTC + ACN), 2 v2 + 2 v1 runs each = 8 decks.
- Capability-bucketing BEFORE scoring; only the symmetric-shippable subset is scored.
- Decision criterion: ≥ 60% slide-wins in symmetric subset AND clear deck-level coherence win.
- 3-week hard stop. Ambiguity → Path D-soft.

During Stage B, the hold remains in effect. v2 cannot change while the pilot runs.

Stage B's outcome then either lifts the hold to Path D-soft (ambiguous or v2 wins) or escalates to a fuller consolidation decision (v2 dominant win → consider deprecating v1 chassis library, on a separate timeline).

### (3) Explicit Mario override

Mario can lift or suspend the hold at any time with a clear rationale. The override does not need committee review; it does need to be logged in this document (append a "Hold lifted" section with date + reason + linked decisions).

---

## Open items the hold defers (not v0.1 backlog, but tracked)

These are real questions, but not load-bearing enough to lift the hold for:

- **Tighten `_hex()` failure detection** at registration-time — currently brand.yml malformed-hex is caught at build_deck.py runtime (good), but could be caught at `register_template.py` Phase 3 (better). v0.1 candidate.
- **`KNOWN_CLIENT_HUE_RANGES` wrap-around for red** — needed for NFL. v0.1 candidate per `nfl-scope-boundary.md`.
- **`PNG too small` QC floor** — currently 50KB heuristic; produces false-positive BLOCKs on simple slides. v0.1 candidate.
- **Post-pass adjacency advisory at Stage 2** — current adjacency context fed to workers is prep-time forecast, not sibling workers' actual picks; the Gate 4 catch-net works but is reactive. v0.1 candidate.
- **REVIEW.html topbar `client_slug` display polish** — `accenture` title-cases to `Accenture` correctly but `fedex` produces `Fedex` instead of the camelCased `FedEx`. v0.1 candidate: slug→display lookup table.
- **Mid-deck mermaid theme override** — `--theme` CLI arg on finalize_deck currently overrides `_meta.json[mermaid_theme]` if the override file exists. Useful escape hatch; documented behavior; deferred review at v0.1.

None of these block production use during the hold.

---

## Files referenced

- `DECISIONS.md` § "A/B test (formal head-to-head) — CANCELLED. Replaced by two-stage gate."
- `nfl-scope-boundary.md`
- `cross-client-pattern-pick-comparison-2026-05-26.md`
- `smoke-test-finding-2026-05-25.md`
- `ab-methodology-review-A.md` / `-B.md` / `-C.md` (A/B cancellation committee)
- `stage-a-protocol-review-A.md` / `-B.md` / `-C.md` (Stage A protocol-lock committee — locked the 3-band outcome tree + ≥2-fabrication-flag override + Stage B reframing as Path D-soft rolling validation)
- `scripts/build_deck.py`, `scripts/finalize_deck.py`, `scripts/build_review.py`, `scripts/compile_picks.py`
- `reference/layouts.md`, `reference/fallback.md`, `reference/anti-patterns.md`
- `prompt.md`
- `theme/mermaid-fedex.json`, `theme/mermaid-accenture.json`, `theme/mermaid-brand.json`
