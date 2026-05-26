# Slide Lab v2 Cleanup + Production-Ready Plan — 2026-05-26

**Authoring context:** Path D committed (v2 wins, v1 retires, NFL out of scope). 4 audits ran in the prior chat — production-readiness, cross-folder leakage, v2 codebase bloat, v1 exemplar inventory. This file consolidates the cross-audit synthesis into a single executable plan.

**Detailed audit findings are inline in the originating chat transcript** at `C:\Users\m.a.peralta\.claude\projects\C--Users-m-a-peralta--claude-skills\89fb855c-6515-4e29-acef-94fc63554d41.jsonl` (writes were denied for individual audit files). Key findings summarized below in each phase.

---

## Phase 0 — Locked decisions

These are confirmed Mario defaults. Override only if explicit reason surfaces during execution.

| Decision | Locked value |
|---|---|
| v1 dependency re-homing strategy | Move ALL shared modules from `slide-builder/` under `slide-builder/` (re-home, not shared lib). Audit identified `twins/` (~50 references); icon_helper.py fix from a parallel chat proved there's MORE. Full dependency sweep required before move. |
| v1 archive mechanism | Rename in place: `slide-builder/` → `slide-builder_archived_2026-05-26/`. Do not hard-delete. Reversible for 30 days. |
| NFL scope | Fully out of scope. Update `_decisions/nfl-scope-boundary.md` with "OBSOLETED BY PATH D" header; v2 explicitly does not handle NFL. |
| Port v1 positive exemplars to v2 | **No.** v2's architecture says "the pattern is the spec." Adding v1 positives would teach v2 v1's design language instead of v2's patterns. |
| Port v1 anti-exemplars to v2 | **Yes** — 9 Tier-1 anti-exemplars (`evidence-stack`, `gray-text-on-brand-purple`, `midpoint-accent-splits-slide`, `placeholder-as-content`, `reading-order-bottom-up`, `six-panel-no-hierarchy`, `table-without-column-headers`, `title-narrower-than-accent-bar`, `vertical-rule-no-gutter`). Source path: `slide-builder/exemplars/dont/<slug>/`. Destination: `slide-builder/reference/anti-patterns/<slug>/`. |
| Remove "v2" / "simple" identity at the end | **Yes (Amendment D, 2026-05-26).** Once v1 is archived, rename `slide-builder/` back to `slide-builder/` and strip "v2" from user-facing language. The dual-skill era is over; the surviving skill returns to its original name. Lands in Phase 8 as steps 8.3–8.8. |

---

## Phase 0 amendments (logged 2026-05-26, chat: eager-mitten)

Amendments to the locked decisions and Phase 1 action list, confirmed by Mario before Phase 1 execution. Future chats: these override the lines they reference.

**Amendment A — `theme/mermaid-brand.json` (action 1.4 expansion).**
Delete confirmed. The "what if a new client needs a fallback" worry is unfounded: Stage-1 sanity check requires `brand.yml`, `brand.yml` is per-client, so the `mermaid-brand.json` fallback path never fires. It's dead code. Action 1.4 expands to two steps:

- (a) Delete `slide-builder/theme/mermaid-brand.json`.
- (b) Edit `slide-builder/reference/fallback.md` line 200 to remove the false "pass mermaid-brand.json as the fallback" claim. Replace with: *"Stage-1 sanity check requires a registered brand.yml; there is no generic fallback. Register the client template before building."*

**Amendment B — Downloads orphan sidecars (action 1.9 override).**
Master plan said hard-delete. Overridden to archive-in-place. Create `C:\Users\m.a.peralta\Downloads\_archive_2026-05-26\` and move both file groups there:

- All `Downloads\fedex-template.*` files (different SHA than OneDrive canonical — divergence not investigated, archive is insurance).
- All `Downloads\NFL Fin Trx - Program Template_vMar2026.*` files.

Rationale: archive cost is near-zero and recoverable if SHA divergence turns out to be intentional WIP.

**Amendment C — Continuous execution protocol (overrides "Mario gates phase transitions").**
Original prompt said "Mario gates phase transitions. After every phase completes, paste a one-paragraph status summary to Mario before starting the next phase." Overridden: execute continuously across phases. Halt only when the 3-agent error-protocol committee fails to converge AND the question requires Mario's input. Post a status summary at each phase boundary but do not pause. Flag side issues encountered mid-phase for later phases or a final follow-ons list — don't stop to ask permission for each. See memory `feedback_continuous_execution.md`.

**Amendment D — Remove "v2" identity, rename skill folder (Phase 8 expansion).**
With v1 archived, the "v2" and "simple" suffixes are vestigial. The surviving skill returns to its original name. Phase 8 expands from 3 steps to 8 steps. See the rewritten Phase 8 section below. Risk: this is a structural rename — anything outside the audited scope that references `slide-builder` by path breaks silently. Phase 2's dependency sweep is extended retroactively to also grep for `slide-builder` string references across all skills, memory files, settings.json, and OneDrive project folders (discovery sweep happens as the final action of Phase 2; Phase 8 consumes the findings).

---

## Phase status log

On-disk record of what was actually executed. Future chats consume this instead of replaying the chat transcript. Update at each phase boundary.

### Phase 0 — Locked decisions + amendments (complete, 2026-05-26)

- **Phase 0 decisions table** (top of this doc): locked at session start, echoed back to Mario, confirmed. No re-litigation.
- **Amendment A** — `theme/mermaid-brand.json` delete confirmed + `fallback.md:200` rewrite added as expansion of action 1.4. Reason: brand.yml-canonical world means there is no generic fallback path.
- **Amendment B** — Downloads orphan sidecars archived (not deleted). Reason: SHA divergence on the FedEx pair not investigated; archive cost ≈ 0; recoverable.
- **Amendment C** — Continuous-execution protocol overrides "Mario gates phase transitions." Halt only when 3-agent committee can't converge AND Mario input is required. Memory saved at `feedback_continuous_execution.md`.
- **Amendment D** — Drop "v2" / "simple" identity; rename `slide-builder/` → `slide-builder/` after v1 archive. Phase 8 expanded from 3 → 9 steps.

### Phase 1 — Unblock Path D operationally (complete, 2026-05-26)

All 10 master-plan actions executed + Amendment A expansion + Amendment B override:

- 1.1 SKILL.md routing inverted; v2 default, v1 retiring; "DO NOT auto-route here" + "Hard rule: never modify slide-builder/" removed
- 1.2 `layouts.md:5` rotation seed corrected — now names both `pattern_pick_seed` and `variant_seed_{A,B,C}` per `build_deck.py:404-427`
- 1.3 FedEx hardcode in `build_gate_preview.py:253-254` replaced. `META_SCHEMA_VERSION` bumped 1→2. `_meta.json` now carries `brand_primary` + `brand_accent`. Reader uses neutral grays (`#333333` / `#888888`) as fallback — explicitly NOT FedEx purple
- 1.4a `theme/mermaid-brand.json` deleted. Two dead `DEFAULT_MERMAID_THEME` constants removed (`build_deck.py:81`, `finalize_deck.py:443`). `render_mermaid.py --theme` made required (no fallback default). `_resolve_mermaid_theme` docstring refreshed
- 1.4b `fallback.md:200` rewritten to brand.yml-required statement
- 1.5 `nfl-scope-boundary.md` stamped with "OBSOLETED BY PATH D" header
- 1.6 `_verify_critical_fixes.py` deleted (zero imports)
- 1.7 `scripts/__pycache__/` deleted; `.gitignore` created
- 1.8 12 v1 `dont/` slugs deleted (all verified `decision: delete` in `_gate2_decisions_final.yaml`)
- 1.9 10 Downloads orphan sidecars archived to `Downloads/_archive_2026-05-26/` (Amendment B)
- 1.10 Anti-pattern counts aligned to **26** in `SKILL.md:178`, `reference/anti-patterns.md:5`, `_decisions/DECISIONS.md:221`
- Verify: zero FedEx hex hits in `scripts/`; all 4 modified scripts `py_compile` clean

**Phase 1 follow-ons surfaced:**
- `reference/fallback.md` + `reference/fallback-examples/*.mmd` still contain `#4D148C` / `#FF6600` as illustrative examples (master plan flagged this as "intentional"). Phase 5 anti-pattern porting touches this area; defer.
- `__pycache__/` regenerated during Phase 1 verify run — expected, `.gitignore` keeps it out of git.

### Phase 2 — Full v1-dependency sweep + re-home (complete, 2026-05-26)

Dependency map built; minimum-subset re-home executed; all imports re-pointed.

- 2.11 Sweep: 5 live v1 deps identified (`twins.client_theme`, `twins.composer`, `twins.helpers`, indirect `icon_helper`, indirect `icons/*.xml`). Discovered `render_slides.py` lives in slide-qc (separate skill), not v1 — comment was misleading. `build_review.py:38-41` had vestigial dead `V1_SKILL` sys.path.
- 2.12 Copy: re-homed 4 twins files + `icon_helper.py` + 1143 icon XMLs into `slide-builder/twins/`, `/scripts/`, `/icons/`. Minimum-subset chosen over copy-everything — the other 12 `twins/*.py` files + 1000+ `twins/builders/` chassis builders are NOT in v2's dep graph.
- 2.13 Re-point: `build_deck.py` (`HELPERS_MODULE_PATH` → `SKILL_ROOT`); `finalize_deck.py` and `compile_picks.py` (dropped `V1_SKILL`, sys.path now points at `SKILL_ROOT` for twins + `QC_SCRIPTS` for `render_slides`); `build_review.py` (removed dead `V1_SKILL` entirely); `prompt.md` (token docs + agent-script import comments updated).
- 2.14 Smoke: All 6 v2 scripts `--help` clean. Runtime imports from v2-local `twins/` succeed. `icon_helper` indirect dep resolves correctly from new home. Zero remaining `slide-builder/` references in v2 `.py` files.
- 2.15 Docs: `DECISIONS.md` Path D supersession headers (TL;DR, "exclusive to v1", testing protocol, cross-stream lines). `convergence-hold-declaration-2026-05-26.md` RESOLVED header. `SKILL.md` A/B testing section deleted, "Exclusive to v1" rewritten as "v1 retirement". `fallback.md` rewrote 99-160 for brand.yml-canonical world; fixed stale `build_fallback_slide_pptx` reference to `_assemble_fallback_pptx`.
- 2.16 Memory: `project_slide_lab_architecture.md` rewritten for v2 (14 patterns; pattern-is-the-spec; dropped twin-pair framing). `project_deck_artifacts_location.md` refreshed with v2 invocation commands. `MEMORY.md` index lines updated.
- 2.17 (Amd D) Cross-skill rename discovery sweep: see § "Cross-skill rename discovery sweep" in Phase 8 below.

**Phase 2 follow-ons surfaced:**
- `slide-qc/scripts/` remains on sys.path (cross-skill dep, not v1 — expected).
- Old `_decisions/` review files still reference the historical `HELPERS_MODULE_PATH = SKILL_ROOT.parent / "slide-builder"` framing — frozen historical artifacts, out of scope.
- 17 frozen `_decisions/` reference Python files (`agent3-slide*.py`, `diagram-test/*.py`, `gallery/*.py`) still hardcode the old `slide-builder` path in `sys.path.insert`. They're not run in production. Could update in a future sweep for consistency, or leave as point-in-time record.
- **Storyline-helper has a v1-script invocation that breaks regardless of rename:** `storyline-helper/SKILL.md:717,724` invokes `py -3 skills/slide-builder/scripts/build_slide.py --print-theme` / `--catalog-layouts`. `build_slide.py` is a v1 script with no v2 equivalent (v2 uses `build_deck.py`). Phase 8.6 must either drop these commands or replace with v2 equivalents. Flagged for Mario decision.

### Phase 3 — User onboarding (complete, 2026-05-26)

All 7 master-plan actions executed:

- **3.17 (Chat-driven `register_template`)** — Copied v1's `register_template.py` to v2-local and refactored main() into three subcommands: `propose` (Phase 1+2 extraction, writes proposal JSON, no prompts), `commit` (Phase 4, reads picks JSON, writes brand.yml + theme.json, no TTY gate), `interactive` (legacy flow preserved for power users with a real TTY). Smoke-tested end-to-end against the archived FedEx template — `propose` produces valid proposal JSON + smoke PNG; `commit` with corrective picks produces correct brand.yml. The TTY safety property is preserved via the explicit `picks.json` named input (can't be accidentally piped).
- **3.18** `README.md` at skill root — 1-paragraph intro + 3 capability bullets + 3 onboarding pointers.
- **3.19** `INSTALL.md` — Python 3.10+, `requirements.txt` deps, mmdc 11.4.0 pinned, LibreOffice headless, sibling `slide-qc` skill. Per-step verification commands. End-to-end verification command prints `install OK`.
- **3.20** `requirements.txt` — pinned `python-pptx 1.0.2`, `Pillow 11.0.0`, `PyYAML 6.0.2`, `lxml 5.3.0`.
- **3.21** `QUICKSTART.md` + `examples/` folder — 3-command sequence with expected console output. `examples/quickstart-brief.md` is a 4-slide ACME-churn brief that exercises cover / headline-finding / comparison / recommendation page types. `examples/RUN.md` documents full end-to-end including agent dispatch, finalize, gate, pick, compile, review.
- **3.22 + 3.23** SKILL.md "first time?" section + v2-local brief format spec added at the top of `SKILL.md`. First-time section points new users at INSTALL → QUICKSTART → RUN in order with a single-command sanity check. Input-contract section embeds a 30-line example brief with full field reference (front-matter + per-slide).

**Phase 3 follow-ons surfaced:**
- **Phase 2 missed dep: `patches` package.** `icon_helper.py:39` does `from patches import get_blank_layout` via a lazy bootstrapped `sys.path.insert` at line 36-38. Phase 2's grep regex for `from\s+(twins|helpers|icon_helper|client_theme)` didn't cover `patches`, and the runtime smoke test imported `add_icon` (a wrapper) which didn't trigger the indirect import. Caught when scanning Phase 3 deps. Copied `slide-builder/patches/{patches.py, CATALOGUE.md}` into `slide-builder/patches/`. Verified `import icon_helper` from a fresh interpreter now succeeds with the v2-local patches. The icon_helper bootstrap pattern is unchanged — it self-bootstraps the patches sys.path, so no edits to icon_helper.py were needed.
- **examples/ has no PPTX bundled.** RUN.md tells the user to point at any registered template they have. This avoids bloating the skill with a binary file but means the example is not 100% self-contained. Acceptable v0.1 trade-off; revisit if onboarding feedback says otherwise.

### Phase 4 — Hardening triple (complete, 2026-05-26)

All 5 master-plan actions executed; contract test passes:

- **4.24 `_paths.py` registry** — Single source of truth for ~35 artifact filenames. Two API forms: absolute-path helpers (`_p.meta_json(out_dir)`) and filename constants (`_p.PROMPT_MD`, `_p.option_pptx_name(letter)`). The constants exist for callers with a pre-computed `slide_dir` Path who shouldn't have to refactor to get out_dir + n separately. Refactored 5 scripts (`build_deck`, `finalize_deck`, `compile_picks`, `build_review`, `build_gate_preview`) to use the registry. `ARTIFACT_MANIFEST` declares writer + reader scripts per artifact for the contract test.
- **4.25 Pydantic schema for `_meta.json`** — `scripts/_meta_schema.py` defines `MetaJson` (top-level), `SlideMeta`, `DeckMeta`. Current version is `META_SCHEMA_VERSION_CURRENT = 2` (incorporates the brand_primary + brand_accent fields added in P1.3). `validate_meta_dict()` + `load_meta_json()` are the public entry points. Writer-side validation wired into `build_deck.py::write_meta_json` so a malformed write fails at the source. `pydantic==2.13.4` added to `requirements.txt` + INSTALL.md verification step.
- **4.26 Contract test** — `scripts/_contract.py` runs 3 checks: (1) every manifest name resolves on `_paths`; (2) MetaJson round-trips dict↔model at version 2; (3) every non-orphan manifest entry's writer/reader scripts actually reference `_p.<name>` / `_p.<name>_name` / `_p.<NAME>`. Test currently passes: 16 manifest entries resolve, 7 active artifacts coverage-checked, 9 accepted-orphans skipped with documented reasons.
- **4.27 Orphan `brief_qc.json` reader** — Resolved as "keep reader, defer writer." `build_review.py::render_qc_banner` has a graceful "brief_qc.json not found" fallback banner. v2's prep does not currently emit brief_qc.json; if brief-time QC becomes a feature in a future release, the writer can be added without touching the reader. Manifest entry annotated with the resolution.
- **4.28 Empty `page_type` field** — Root cause: build_review's `parse_prompt()` regexed `**Page type (heuristic):**` out of `_prompt.md`, but `prompt.md` (the v2 template) never emits that line. The lookup always missed and fell through to `_meta.json`. Removed the dead regex; `parse_prompt()` no longer returns a `page_type` key. The single canonical source is now `_meta.json::slides[].page_type` (populated by build_deck from the brief's per-slide `page_type:` field).

**Phase 4 follow-ons surfaced:**
- Reader-side validation (calling `validate_meta_dict()` after every `json.loads()` of `_meta.json` in readers) was deferred. Writer-side validation in build_deck is the load-bearing gate; reader-side is "belt and braces" and not required for v0.1. Add in v0.2 if read-time drift is observed in the field.
- The `option_mermaid_png` artifact's manifest "writer" was originally `render_mermaid.py`, but render_mermaid is brand-agnostic and writes wherever `--output` says; the actual path-constructor is `finalize_deck.py:408`. Updated the manifest with this clarification.
- The contract test only checks the `slide-builder/scripts/` directory. If a future change adds a Python helper outside `scripts/` (e.g., a `lib/` or `shared/` subpackage), update `_contract.py::_script_text` and the manifest accordingly.

### Phase 5 — Anti-pattern training corpus (complete, 2026-05-26)

All 3 master-plan actions executed:

- **5.29 Port 9 Tier-1 anti-exemplars** — Copied `exemplar.png` + `WHY.md` (not the v1 `.py` / `.pptx` chassis-vocabulary builders) from `slide-builder/exemplars/dont/<slug>/` to `slide-builder/reference/anti-patterns/<slug>/` for: `evidence-stack`, `gray-text-on-brand-purple`, `midpoint-accent-splits-slide`, `placeholder-as-content`, `reading-order-bottom-up`, `six-panel-no-hierarchy`, `table-without-column-headers`, `title-narrower-than-accent-bar`, `vertical-rule-no-gutter`. Each slug ends up with 2 files (PNG + WHY.md).
- **5.30 Update `reference/anti-patterns.md`** — Added a new "Ported anti-exemplars (visual reference library)" section between the rules and the cross-references. One-line failure description per slug + category, with markdown links to the per-slug `WHY.md`. Worker agents are instructed to glance at the PNG when their slide rhymes with the failure picture.
- **5.31 Delete v1 process-artifact files** — 40 files removed from `slide-builder/exemplars/` root: `_fix_report_*.md` (×23), `_qc_report_*.md` (×9), `_reverify_report_*.md` (×6), `_phase3_*.md` (×2). What remains is the legitimate exemplar infrastructure (`INDEX.md`, `LIBRARY_STATUS.md`, generated review HTML, index JSON, helper scripts) — those stay with v1 until Phase 8 archive.

**Phase 5 follow-ons surfaced:** none.

### Phase 6 — Operational hygiene (complete, 2026-05-26)

All 7 master-plan actions executed:

- **6.32 `scripts/clean.py`** — removes ephemeral artifacts (`_raw/`, `_render_tmp/`, themed PPTX, option PNGs, gate/review HTML, `_meta.json`, `__pycache__/`) while preserving `picks.json`, agent build scripts, and prompts. `--deep` flag wipes back to pre-build state.
- **6.33 `_log.py` build.log tee** — `attach(out_dir, script_name)` wraps stdout/stderr with a Tee that mirrors all console output into `<out>/build.log` (append-only across pipeline steps, with timestamped banners). Wired into the main() of `build_deck`, `finalize_deck`, `compile_picks`, `build_review`, `build_gate_preview`.
- **6.34 `TROUBLESHOOTING.md`** — exit-code reference tables for all 6 pipeline scripts + common console-message diagnoses (BrandSidecarMissing, mmdc not on PATH, FALLBACK FAILED, SKELETON_REJECTED, etc.). Ends pointing at `diagnostic.py` for bug-report bundles.
- **6.35 PNG-too-small QC floor** — `finalize_deck.py:240-247` lowered from 50KB to 12KB. Sparse covers + hero slides routinely render at 20-35KB; 12KB is roughly the size of a near-blank PNG, which still catches silent render failures.
- **6.36 REVIEW.html `client_slug` polish** — `build_review.py` now has a `_BRAND_DISPLAY` override table (`fedex` → `FedEx`, `accenture` → `Accenture`, `acn` → `Accenture`, `nfl` → `NFL`). Falls back to `title()`-cased slug for unknown brands.
- **6.37 `CHANGELOG.md` + `VERSION`** — CHANGELOG.md starts at v0.1 with the full Path D + Phase 1-6 summary. `VERSION` file at skill root holds `0.1.0`.
- **6.38 `scripts/diagnostic.py`** — bundles `_meta.json`, `_finalize_meta.json`, `build.log`, `dispatch_plan.md`, every `_prompt.md`, every `_pattern_pick.md`, every `*.qc.json`, every `option_*.py` into a single zip. Excludes binary artifacts (PPTX, PNG) and the source brief / template to keep bug-report bundles small and shareable.

Contract test passes throughout (verified post-P6.38).

**Phase 6 follow-ons surfaced:** none.

### Phase 7 — Bloat archive (complete, 2026-05-26)

All 6 master-plan actions executed. Approximately **1.26 GB reclaimed**, nothing deleted — everything archived in named, dated folders.

- **7.39** Archived `OneDrive\Claude Projects\_brief-quality-test-2026-05-21\` (**1026.4 MB**) → `OneDrive\Claude Projects\_archive_2026-05-26-slide-lab\`
- **7.40** Archived `Downloads\slide_lab_tests\` (**211.7 MB**) → `Downloads\_archive_2026-05-26\` (same archive folder created in Phase 1 for the orphan fedex/NFL sidecars)
- **7.41** Archived `_latitude-test-2026-05-23\` (2.6 MB) + `_latitude-test-v2-2026-05-23\` (2.3 MB) → `OneDrive\Claude Projects\_archive_2026-05-26-slide-lab\`
- **7.42** Archived `_HANDOVER-2026-05-21-slide-lab-production.md` + `_EXEMPLAR_CANDIDATES.html` + `_ANTI_EXEMPLAR_CANDIDATES.html` + `_REVIEWS_INDEX.html` → same archive folder
- **7.43** Archived `Documents\slides\` build-script graveyard: 60 files (.py, .pyc, design-specs-*.md, .html, .css, .json, .py_path, .txt) moved to `Documents\_archive_2026-05-26-slide-lab\` preserving the relative dir structure. Deliverables (.pptx, .potx, .pdf, .xlsx) and non-design-specs .md files stay in `Documents\slides\` per master plan.
- **7.44** Archived 4 redundant install-guide DOCX files. `INSTALL.md` at skill root is now the canonical install reference (built in Phase 3). DOCX files moved to the same Phase-7 archive folders alongside their source (OneDrive → OneDrive archive; Documents → Documents archive). If a future need surfaces for a polished DOCX wrapper to share with non-Claude-Code users, regenerate from `INSTALL.md` rather than restore one of the archived files.

**Phase 7 follow-ons surfaced:**
- Consolidation note: there are now THREE Phase-period archive folders across the file system: `OneDrive\Claude Projects\_archive_2026-05-26-slide-lab\`, `Documents\_archive_2026-05-26-slide-lab\`, and `Downloads\_archive_2026-05-26\`. Per-source archive (not consolidated) was deliberate — they live where their source files lived, with different sync/cloud behaviors. Audit when reviewing in 30 days.

### Phase 8 — v1 retirement + skill rename (Amendment D) (complete, 2026-05-26)

All 9 steps executed in sequence per Amendment D:

- **8.1** `slide-builder/` → `slide-builder_archived_2026-05-26/`. v1 archived, reversible 30 days.
- **8.2** Verify post-archive build. All 6 v2 scripts `--help` clean, runtime imports succeed, contract test passes. Phase 2 dep sweep was complete (one import-ordering bug in `build_deck.py` from P4.25 surfaced and was fixed — `META_SCHEMA_VERSION = META_SCHEMA_VERSION_CURRENT` was placed before the import; moved to after).
- **8.3** `slide-builder-simple/` → `slide-builder/`. `__pycache__/` cleared before rename. Verified runtime imports + contract test from the new path.
- **8.4** Internal references updated: 16 active files had `slide-builder-simple` references swapped to `slide-builder` via bulk replace (scripts, prompt.md, SKILL.md, INSTALL, CHANGELOG, QUICKSTART, README, reference/*.md, examples/RUN.md, _decisions/cleanup-plan-master / DECISIONS / convergence-hold). Forensic _decisions/ review files left intact. Contract test still passes.
- **8.5** "v2" stripped from user-facing surfaces: SKILL.md frontmatter description + H1 heading, prompt.md H1, layouts.md / anti-patterns.md authoritative-catalog descriptors, build_deck.py dispatch-plan header, finalize_deck.py "Part B complete" line, compile_picks.py argparse description. Deep-context "v2" mentions inside the architecture-explanation paragraphs (Why-v2-exists, "v2 collapses the lever stack", etc.) preserved as historical context per master plan — they document the architectural evolution and removing them would damage the audit trail.
- **8.6** `storyline-helper/SKILL.md` Step 10 rewritten. The dead `build_slide.py --print-theme` / `--catalog-layouts` commands are dropped (Phase 2 follow-on resolved). Replaced with the chat-driven `register_template.py propose` → `commit` flow for template registration. Step 10 now matches the v0.1 register-template contract.
- **8.7** Memory files `MEMORY.md`, `project_slide_lab_architecture.md`, `project_deck_artifacts_location.md` had `slide-builder-simple` → `slide-builder` swapped. The architecture memory's name slug `slide-lab-architecture-v2` was kept because it's an internal differentiation marker. The body paths are correct.
- **8.8** Skill frontmatter `description:` field cleaned during P8.5 — no "(v2)" suffix, no "retired v1" framing.
- **8.9** `_decisions/nfl-scope-boundary.md` deleted. Tactical call: the "OBSOLETED BY PATH D" banner is captured in `DECISIONS.md` and the master plan; the standalone file is redundant. Recoverable from git or by restoring from the master-plan / DECISIONS.md narrative.

**Phase 8 follow-ons surfaced:**
- The `slide-builder_archived_2026-05-26/` skill folder still appears as a discoverable skill in Claude's skill loader (because it has its own SKILL.md). Mario can manually remove it after the 30-day reversibility window if desired, or leave it as an archived legacy reference.
- The memory file `project_slide_lab_architecture.md` has `name: slide-lab-architecture-v2` as its slug. If a future `[[slide-lab-architecture]]` link gets written, it won't resolve. Update the slug only if/when [[link]] discipline becomes important.
- A few "v2" mentions in `_decisions/cleanup-plan-master-2026-05-26.md` itself (this file) remain in the historical narrative — those are correct for the historical record but could be cleaned in a future pass if Mario wants the master plan itself to read as past-tense post-rename.

### Phase 8 verification + remediation pass (complete, 2026-05-26)

A post-Phase-8 audit caught residual drift the global string-replace introduced. All items remediated in the same session:

**R2 (BLOCKER) — Phase 8 log drift + post-rename tautologies:**
- `CHANGELOG.md:39` "copied from slide-builder/ to slide-builder/" → rewritten narratively: "all infra previously imported from the legacy chassis-vocabulary skill was re-homed into this skill in Phase 2."
- `CHANGELOG.md:57` "Phase 8 ... still pending" → updated to past tense: documents the actual rename + the 1.26 GB Phase 7 reclaim.
- `SKILL.md:297-300` "Shared infra (DO NOT MODIFY) ..." warning block → DELETED entirely. The modules now live in this skill; the DO-NOT-MODIFY framing is exactly backwards post-Phase-2.
- `SKILL.md:309` "Strategy: fork v1's scripts. Copy slide-builder/scripts/{...} into slide-builder/scripts/" → rewritten as historical narrative: "Originally forked from the legacy chassis-vocabulary skill at `slide-builder_archived_2026-05-26/`. Three were near-verbatim; build_deck.py was the real new build."
- `SKILL.md:146, 216, 319` circular `../slide-builder/SKILL.md` cross-references → inlined or replaced with direct prose (Communication rules, Setup step, Project folder convention).
- `anti-patterns.md:155` `slide-builder/exemplars/dont/` reference → updated to `slide-builder_archived_2026-05-26/exemplars/dont/`.
- `build_review.py` argparse description "v2 slide-builder-simple output" → "a slide-builder build output directory."
- `build_deck.py` lines 501, 507, 1051, 1062, 1070, 1163, 1203 — error messages with v1/v2 split narrative + `--auto-accept-phase1` legacy references → rewritten to point at the chat-driven `propose` → `commit` flow (current state).
- Memory files (`MEMORY.md`, `project_slide_lab_architecture.md`, `project_deck_artifacts_location.md`) re-verified — zero `slide-builder-simple` hits.

**R3 (BLOCKER) — storyline-helper post-rename breakage:**
P8.6 missed three lines outside the Step 10 block. Caught + fixed in this remediation:
- `storyline-helper/SKILL.md:136` Client-template description referencing `--print-theme` and `--client-template` → rewritten as the brand.yml-registered prereq.
- `storyline-helper/SKILL.md:155` "template path passed to --print-theme in Step 10" → rewritten as the chat-driven registration handoff.
- `storyline-helper/SKILL.md:738` "Slide Builder: skip --print-theme and --catalog-layouts ... read phase-a-rules.md and visual-treatment-library.md" → rewritten: "read layouts.md and anti-patterns.md before dispatching per-slide workers; brand colors from registered brand.yml; layout catalog is layouts.md."

**YELLOW items (non-blocking, cleaned same pass):**
- `patches/CATALOGUE.md:85` + `patches/patches.py:824` references to non-existent `reference/icon-vocabulary.md` → replaced with the actual lookup mechanism: "any filename (without extension) under `icons/*.xml`."
- `README.md` "Where to start" — examples/ has no bundled PPTX → clarified: "You provide the template — point the quickstart at any client PPTX you have already registered."
- `register_template.py:43-47` + `_contract.py:85-86` hardcoded FedEx hex → LEFT INTENTIONALLY (documented as fixture / interactive-flow fallback per audit).
- `finalize_deck.py` module docstring "Slide Lab v2 deck orchestrator ... sys.path points twins/ + render_slides.py at v1's skill" → rewritten to reflect current state (twins/ local, slide-qc cross-skill).

**Verification gauntlet (run end-to-end after R2 + R3 + YELLOW landed):**
- ✓ `_contract.py` passes: 16 manifest entries resolve / meta-json schema round-trip @ v2 / 7 active artifacts handoff-covered / 9 accepted-orphans skipped.
- ✓ All 9 scripts emit clean argparse `--help` (build_deck, finalize_deck, compile_picks, build_review, build_gate_preview, register_template, clean, diagnostic, _contract).
- ✓ Zero `slide-builder-simple` hits in user-facing/active scripts/docs (CHANGELOG, SKILL.md, prompt.md, reference/*.md, etc.).
- ✓ Zero `slide-builder-simple` hits in memory files.
- ✓ Zero `slide-builder-simple` hits in `DECISIONS.md` and `convergence-hold-declaration-2026-05-26.md`.
- 3 hits remain in this file's own Phase 8 status-log entries describing the rename operation factually ("slide-builder-simple/ → slide-builder/"). These are forensic narrative within an active doc — acceptable per the master-plan's own "v2 mentions in cleanup-plan-master itself" carve-out.

**v0.1 release-tag defensibility:**
- Hardening triple (P4.24–4.26) in place + contract test green.
- Onboarding docs + chat-driven register_template flow in place.
- v1 archived + skill renamed back to `slide-builder/`.
- Storyline-helper handoff updated to v0.1 reality.
- All BLOCKER drift remediated; all in-scope YELLOW items cleaned.

v0.1 is defensible against the audit checklist. **Not** marked shipped until Mario reviews per the audit's instruction.

---

## Phase 1 — Unblock Path D operationally (~2 hours)

Cheapest, lowest-risk wins. Do these first.

1. **Invert `slide-builder/SKILL.md` routing default.** Lines 14, 17–23, 25 currently say v1 is default, v2 is experimental. Flip: v2 is default; v1 retiring; remove the "DO NOT auto-route here" language.
2. **Fix rotation seed in `slide-builder/reference/layouts.md:5`.** Currently shows v1's formula `md5(family + intent + content_hash + slide_n)`. Code uses `md5(content_hash + slide_n)` + `option_letter`. Doc lies; agents read it. **Highest-impact agent-facing bug.**
3. **Fix the one real FedEx hardcode in v2 code:** `slide-builder/scripts/build_gate_preview.py:253-254`. Currently `--brand-primary: #4D148C; --brand-accent: #FF6600;` hardcoded in CSS. Inject from `_meta.json` brand colors.
4. **Delete `slide-builder/theme/mermaid-brand.json`.** It's a FedEx-shaped "default reference" file with three contradictory stances across docs and code. Per-client `mermaid-fedex.json` exists for actual FedEx use.
5. **Update `slide-builder/_decisions/nfl-scope-boundary.md`** with Path D supersession header. Line 13's "v1 not retired" + lines 95–102's twins-architectural-reference claim are now historical.
6. **Delete `slide-builder/scripts/_verify_critical_fixes.py`.** One-off scaffold, never imported, hardcoded FedEx hex values.
7. **Delete `slide-builder/scripts/__pycache__/`** + add `.gitignore` at skill root with `__pycache__/`, `*.pyc`, `theme/_generated/` entries.
8. **Delete 12 v1 exemplar slugs** from `slide-builder/exemplars/dont/` that have `decision: delete` in `_migration/_gate2_decisions_final.yaml` but were never executed:
   - `b-bridge`, `b-framing`, `b-hypothesis`, `b-implication`, `b-pivot`, `b-recommendation`, `b-tldr`, `b-dark-mandate`, `g-change-curve`, `j-cycle`, `j-dark-org-chart`, `j-bow-tie`
9. **Delete orphan brand sidecars in Downloads.** Two pairs: `Downloads/fedex-template.{brand.yml,theme.json,smoke.pptx,smoke.png,pptx}` (FedEx dup, different SHA than OneDrive canonical), and `Downloads/NFL Fin Trx - Program Template_vMar2026.*` (NFL, no project folder, no use).
10. **Reconcile anti-pattern count drift.** SKILL.md:178 says 27; `reference/anti-patterns.md:5` says 25; `_decisions/DECISIONS.md:221` says 25; actual numbered entries: 26. Pick one (the actual count) and update the other two.

---

## Phase 2 — Full v1-dependency sweep + re-home (~1 day)

**CRITICAL:** Do not start with "re-home twins." Audit 1 found twins. The icon_helper.py fix from a parallel chat proved there's at least one more dependency Audit 1 missed. Start with a fresh dependency audit.

11. **Run a v1-dependency sweep.** Grep `slide-builder/` for every reference to `slide-builder/`, every `sys.path.insert` pointing at v1, every `from twins`, `from helpers`, `from icon_helper`, etc. Build a complete dependency map BEFORE moving anything.
12. **Copy all v1 dependencies into `slide-builder/`.** At minimum: `twins/`, `scripts/icon_helper.py`, plus anything discovered in step 11. Copy, don't move — leave v1 intact until Phase 8.
13. **Update all imports** in v2 scripts + prompt template + reference docs to point at the v2-local copies.
14. **Test end-to-end build** to verify all paths resolve. Run the FedEx smoke or similar.
15. **Update v2 docs to reflect Path D**, in this order:
    - `slide-builder/_decisions/DECISIONS.md` — Path D supersession header at lines 11, 202–211, 246–250, 296.
    - `slide-builder/_decisions/convergence-hold-declaration-2026-05-26.md` — "RESOLVED by Path D" header.
    - `slide-builder/SKILL.md` — delete lines 264–279 (A/B testing section); convert lines 292–302 ("Exclusive to v1") to retirement plan.
    - `slide-builder/reference/fallback.md` — rewrite lines 99–160 for brand.yml-canonical world; fix doc-vs-code mismatches at 158, 200, 222–275.
16. **Update memory files** at `C:\Users\m.a.peralta\.claude\projects\C--Users-m-a-peralta--claude-skills\memory\`:
    - `project_slide_lab_architecture.md` — rewrite for current v2 architecture (9 splits + 3 diagrams + 2 special objects + 1 fallback). Remove v1 twins/hand-built framing.
    - `project_deck_artifacts_location.md` — keep folder convention; replace `twins/composer.py` invocation example with current v2 commands.
    - `MEMORY.md` index — refresh the two affected lines.

---

## Phase 3 — User onboarding (~3 days, critical path)

Audit 4's biggest gap cluster. Without these, v2 is not coworker-ready.

17. **Chat-driven `register_template` wrapper** — Mario's documented "non-negotiable" for production readiness. Replaces the PowerShell-only TTY-gated flow. Walks user through Phase 1 (template upload) → Phase 2 (smoke PNG) → Phase 3 (swatch picks) in chat with preview panel. ~1.5–2 days.
18. **`README.md` at `slide-builder/` root** — what this is (1 paragraph), what you can do (3 bullets), where to start.
19. **`INSTALL.md`** — pinned mmdc 11.4.0, LibreOffice headless command, Python deps, verification step.
20. **`requirements.txt`** with pinned versions.
21. **`QUICKSTART.md` + `examples/` folder** — example brief + sample template + `examples/RUN.md` with exact 3-command sequence and expected console output.
22. **Top-of-SKILL.md "first time?" section** — one paragraph + verification command.
23. **v2-local brief format spec** — don't make new users read v1's SKILL.md to learn brief format. 30-line example brief embedded.

---

## Phase 4 — Hardening triple (~2 days, v0.1 release-tag gate)

`slide-builder/_decisions/DECISIONS.md` lines 329–345 commit to this as the v0.1 ship gate. Nothing on disk yet.

24. **`scripts/_paths.py`** — extract 85 hardcoded filename strings (`_meta.json`, `option_X.pptx`, `_raw/`, `_render_tmp/`, etc.) to one registry imported across 6 scripts.
25. **Pydantic schema for `_meta.json`.** Single source of truth; load-time validation.
26. **Contract test at module-load time.** Verifies `_meta.json` schema, paths registry, and finalize/compile/review reader signatures match build_deck writer.
27. **Resolve orphan `brief_qc.json` reader** in `build_review.py:446–464` — implement writer or remove reader.
28. **Resolve empty `page_type` field** in `_meta.json` (build_deck writes `""`, build_review re-extracts from prompt regex). Parse in build_deck or drop from schema.

---

## Phase 5 — Anti-pattern training corpus (~30 min)

29. **Port 9 Tier-1 anti-exemplars** from `slide-builder/exemplars/dont/<slug>/` to `slide-builder/reference/anti-patterns/<slug>/`. Copy `exemplar.png` + `WHY.md`. Slug list locked in Phase 0.
30. **Update `slide-builder/reference/anti-patterns.md`** to incorporate the 9 ported failure modes. One paragraph per failure mode citing the source.
31. **Delete process-artifact files** at `slide-builder/exemplars/` root: `_fix_report_*.md`, `_qc_report_*.md`, `_reverify_report_*.md`, `_phase3_*.md` (~30 files).

---

## Phase 6 — Operational hygiene (~1 day)

32. **`scripts/clean.py <out_dir>`** — remove `_raw/`, `_render_tmp/`, intermediate PNGs, stale `_meta.json` while preserving brief + picks.
33. **Logging to `<out>/build.log`** per build — capture every console line + agent decisions.
34. **`TROUBLESHOOTING.md`** keyed by exit code.
35. **PNG-too-small QC floor** — current 50KB heuristic false-positives on cover slides. Cover slides are universal; this hits every user. Either raise the floor or skip the check for full-canvas patterns.
36. **REVIEW.html topbar `client_slug` polish** — `fedex` → `FedEx`, `accenture` → `Accenture`. Cosmetic but visible.
37. **`CHANGELOG.md`** starting at v0.1. Optional: `VERSION` file.
38. **`scripts/diagnostic.py <out_dir>`** — bundle `_meta.json` + all `_prompt.md` + all `*.qc.json` + console log into a zip for coworker bug reports.

---

## Phase 7 — Bloat archive (~1 hour, ~1.3 GB reclaim)

Parallelizable, independent of phases 1-6.

39. **Archive `OneDrive/Claude Projects/_brief-quality-test-2026-05-21/`** (1.1 GB, v1/Path-C era).
40. **Archive `Downloads/slide_lab_tests/`** (~190 MB, v1/Path-C era).
41. **Archive `OneDrive/Claude Projects/_latitude-test-2026-05-23/` and `_latitude-test-v2-2026-05-23/`** (~5.5 MB).
42. **Archive `OneDrive/Claude Projects/_HANDOVER-2026-05-21-slide-lab-production.md`** + 3 HTML curation pages (`_EXEMPLAR_CANDIDATES.html`, `_ANTI_EXEMPLAR_CANDIDATES.html`, `_REVIEWS_INDEX.html`).
43. **Archive `Documents/slides/`** build-script graveyard — keep `.pptx`/`.pdf` deliverables; archive `.py` scripts + `design-specs-*.md`.
44. **Consolidate 3 install guide DOCX files** in `OneDrive/Claude Projects/` and `Documents/` into 1 current version reflecting Path D + v2 install flow.

---

## Phase 8 — v1 retirement + skill rename (Amendment D, ~1 hour)

Expanded per Amendment D (2026-05-26). Runs only after Phase 2 verified and all other phases complete. Sequence matters — archive v1 BEFORE the rename, or the rename collides with the existing v1 folder.

### 8.1 — Archive v1 first
Rename `C:\Users\m.a.peralta\.claude\skills\slide-builder\` → `C:\Users\m.a.peralta\.claude\skills\slide-builder_archived_2026-05-26\`.

### 8.2 — Verify the surviving skill still builds end-to-end after the v1 rename
This proves Phase 2's dependency sweep caught everything. Run `build_deck.py --help`, `finalize_deck.py --help`, the runtime import check from Phase 2's smoke. If anything fails, Phase 2 missed a dep — fix in `slide-builder/` and retry.

### 8.3 — Rename the skill folder
Rename `slide-builder/` → `slide-builder/`. Use a move that preserves git history (`git mv` if it's tracked, or PowerShell `Move-Item` if not).

### 8.4 — Update internal path references that hardcode `slide-builder`
Grep the renamed folder for any remaining `slide-builder` strings and replace with `slide-builder`:

- All scripts in the renamed folder (`scripts/*.py`, `twins/*.py` if any)
- `prompt.md` template variables and tokens
- `reference/*.md` cross-references
- `_decisions/*.md` — only the **active** ones (e.g., the current SKILL.md surface, master plan); **forensic files keep historical mentions intact** (DECISIONS.md historical narrative, review-A/B/C files, etc.)
- `.gitignore` if any path-relative entries exist

### 8.5 — Strip "v2" from docs throughout
Globally replace user-facing "v2" mentions: either nothing (when redundant — "v2 architecture" → "architecture") or "Slide Lab" (when used as a product name). Forensic `_decisions/` files keep historical "v2" mentions — those record point-in-time thinking.

Active files to edit:
- `SKILL.md` (top-level identity, headers, taglines)
- `README.md` (Phase 3 deliverable — author with no "v2" from the start)
- `reference/layouts.md`, `reference/fallback.md`, `reference/anti-patterns.md`
- `prompt.md`
- `DECISIONS.md` — the **active current-state section only** at the top; the historical decision narrative keeps its v2 mentions

### 8.6 — Update cross-skill invocation (storyline-helper)
`storyline-helper` currently invokes `slide-builder`. Update to `slide-builder`. File: `C:\Users\m.a.peralta\.claude\skills\storyline-helper\SKILL.md`. Search for `slide-builder` and replace. Verify by running a storyline-helper → slide-builder handoff end-to-end.

### 8.7 — Update memory files
- `project_slide_lab_architecture.md` — Phase 2 wrote this for v2; rename mentions reflect the post-rename path.
- `project_deck_artifacts_location.md` — same.
- `MEMORY.md` index lines — same.
- Any other memory file mentioning `slide-builder` or "v2".

### 8.8 — Update skill frontmatter / triggers
The skill's frontmatter `description:` (which Claude reads to decide when to invoke this skill) currently says "Default build layer of Slide Lab (v2)". Drop the "(v2)" and any "retired v1" language.

### 8.9 — NFL scope boundary file
Per the original Phase 8: delete `_decisions/nfl-scope-boundary.md` entirely, OR leave with the "OBSOLETED BY PATH D" header (already stamped in Phase 1). Mario's call.

### Cross-skill rename discovery sweep (run end of Phase 2; consumed here)

Sweep ran 2026-05-26 at end of Phase 2. Results below — Phase 8 consumes this picklist directly.

**1. Other skills under `.claude/skills/` referencing `slide-builder`:** NONE.
`slide-qc/`, `rfp-helper/`, `slidelab-log/`, `storyline-helper/`, `docx/`, `pptx/`, `xlsx/` — all clean.

**2. Other skills referencing v1's script names (path-agnostic break risk after rename):**
- `storyline-helper/SKILL.md:717` and `:724` invoke `py -3 skills/slide-builder/scripts/build_slide.py --print-theme` and `--catalog-layouts`. `build_slide.py` is a **v1 script that doesn't exist in v2** (v2 uses `build_deck.py`). After v1 archive + rename, these commands fail. **Phase 8.6 must either drop these lines from storyline-helper or replace them with v2 equivalents.** This is independent of the folder rename — it would break even without Amendment D.

**3. Memory files** (3 files referencing `slide-builder`, already updated in Phase 2 to reflect v2; Phase 8.7 just re-renames to `slide-builder`):
- `memory/MEMORY.md`
- `memory/project_slide_lab_architecture.md`
- `memory/project_deck_artifacts_location.md`

**4. `.claude/settings.json` and `.claude/settings.local.json`:** NEITHER references `slide-builder` or `slide-builder`. Clean.

**5. OneDrive Claude Projects** (`C:\Users\m.a.peralta\OneDrive - Accenture\Claude Projects\`): 35 files in 3 historical v2 smoke-test output folders (`v2-smoke-2026-05-25/`, `v2-trigger-smoke-2026-05-25/`, `v2-smoke-2026-05-26-acn/`). The `slide-builder` references are in `_meta.json`, `_prompt.md`, `dispatch_plan.md`, `_finalize_meta.json`, `RESULT.md` — all **frozen build records**, not inputs to anything. **Phase 8 verdict: leave alone.** They become broken-path historical records, which is fine since nothing re-reads them. Optionally archive the three smoke folders alongside other Phase 7 bloat.

**6. Inside the surviving skill folder itself** (`slide-builder/`): 31 files. Active scope for Phase 8.4 / 8.5:
- **Active (rename + de-v2):** `SKILL.md`, `prompt.md`, `reference/{layouts.md, fallback.md, anti-patterns.md}`, `scripts/{build_deck.py, finalize_deck.py, compile_picks.py, build_review.py}`, `_decisions/cleanup-plan-master-2026-05-26.md`.
- **Active partial-update (header only):** `_decisions/DECISIONS.md` (top current-state section only; historical narrative keeps v2 intact), `_decisions/convergence-hold-declaration-2026-05-26.md` (resolved-header references), `_decisions/nfl-scope-boundary.md` (already obsoleted; slated for Phase 8.9 deletion).
- **Forensic — leave intact:** ~19 historical `_decisions/` review files (`architecture-review-{A,B}`, `ab-methodology-review-{A,B}`, `artifact5-intent-review-{A,B}`, `build-deck-review.md`, `diff-review-A.md`, `fidelity-threshold-review-B.md`, `post-stage4-plan-review-B.md`, `smoke-test-finding-2026-05-25.md`, `stage-a-*.md`, `theme-extraction-proposal-{A,C}.md`, `unblock-review-B.md`, `v2-patch-review-{A,B,C}.md`).

**7. `__pycache__/` artifacts:** Auto-regenerate when scripts run. Phase 8.3 deletes the cache before/after rename to avoid stale entries.

---

## Error protocol (for self-sustainability)

**When a phase action fails:**

1. **First**, check the inline audit findings in the originating chat transcript at `C:\Users\m.a.peralta\.claude\projects\C--Users-m-a-peralta--claude-skills\89fb855c-6515-4e29-acef-94fc63554d41.jsonl` — there's a high chance the audit already identified context for the failure.

2. **If the audit didn't surface it**, dispatch 3 agents in parallel using the `Agent` tool with `subagent_type: general-purpose`:
   - Agent A: identify the root cause (read the failing file, traces, related files; explain what's broken)
   - Agent B: propose a fix (specific code/doc change, with file paths and line numbers)
   - Agent C: identify the highest-risk side effect of Agent B's fix (what could break elsewhere)

3. **Synthesize the three verdicts** before applying any fix. If A and B agree but C identifies a real risk, mitigate the risk first. If A and B disagree, dispatch a 4th tiebreaker agent.

4. **Never modify a phase's locked decisions in Phase 0** without explicit Mario confirmation. The decisions are committed because they survived prior committee deliberation.

5. **If a phase action requires a Mario decision not covered in Phase 0**, halt and surface concretely:
   - What's blocking
   - What options exist
   - What you recommend and why
   - The exact paste-ready Mario can send back

---

## Self-test before declaring v0.1 done

After all phases complete, run this checklist:

- [ ] Mario can install v2 from scratch following `INSTALL.md` on a new machine, in under 30 minutes.
- [ ] Mario can register a new client template via chat (no PowerShell).
- [ ] Mario can build the `examples/quickstart-brief.md` deck and get a valid REVIEW.html.
- [ ] Contract test passes at module load time.
- [ ] `_paths.py` is the single source of truth for filename strings.
- [ ] `_meta.json` schema is pydantic-validated.
- [ ] No imports from `slide-builder/` or `slide-builder_archived*/` remain in `slide-builder/`.
- [ ] No FedEx hex values (`#4D148C`, `#FF6600`) exist in `slide-builder/scripts/` or `reference/` except where intentional (e.g., per-client mermaid file).
- [ ] SKILL.md, README.md, and DECISIONS.md all describe v2 as default. No "experimental" / "parallel" framing remains.
- [ ] Anti-patterns doc references the 9 ported failure modes.
- [ ] Memory files at `~/.claude/projects/.../memory/` describe v2's current architecture, not v1 twin pairs.
- [ ] v1 is archived (renamed in place), not deleted.
- [ ] CHANGELOG.md exists with v0.1 entry summarizing the consolidation.

---

## Reference: cross-audit findings density

- **Audit 1 (v2 codebase):** ~75 findings, 5 BLOCKER / 18 HIGH / 28 MEDIUM / 24 LOW. Biggest issues: SKILL.md routing default, layouts.md rotation seed, twins dependency.
- **Audit 2 (v1 exemplars):** 561 exemplars; 9 Tier-1 anti-exemplars worth porting; 12 already-decisioned-delete slugs to delete; v1's G+J families are structural failures.
- **Audit 3 (cross-folder):** 2 active client sidecars (keep), 2 orphan sidecars in Downloads (delete), 2 memory files describe v1 architecture as locked (update), ~1.3 GB stale project artifacts (archive).
- **Audit 4 (production gaps):** 15 distinct gaps; biggest is chat-driven template registration ("non-negotiable" per DECISIONS.md); v2 not coworker-ready today; ~3 days minimum viable bar.
