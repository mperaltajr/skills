# Changelog — Slide Lab

All notable changes to this skill. Versioning follows [Semantic Versioning](https://semver.org/) loosely: major bumps signal architectural changes, minor bumps signal feature additions, patch bumps signal fixes.

## [Unreleased] — Pattern B refactor (M1 – M7, 2026-06-16 → 2026-06-17)

### Added — Pattern B HTML-first build path (M1 – M5)
- **M1** (`9623efb`): `--pattern {auto,B,C,legacy}` CLI flag on `build_deck.py`; per-slide classifier `_classify_slide_pattern`; `_meta.json` schema-v3 extension with optional Pattern B fields (`pattern_default`, `pattern_per_slide`, `html_render_canvas`, `translator_dispatched`, `translation_reports`, per-slide `pattern` / `artifacts`); shipped `settings.json` with `default_pattern: legacy` + `enable_pattern_b: false` master switch.
- **M2** (`6c246a3`): SSIM regression-test harness (`tests/capture_baseline.py` + `tests/regression_check.py`); `scikit-image>=0.21,<1.0` dep.
- **M3** (`2981661`): `scripts/render_html.py` Playwright wrapper (headless Chromium → 1280×720 PNG); public color helpers in `twins/client_theme.py` (`hex_to_rgbcolor`, `css_color_to_rgbcolor`, `resolve_css_var`, `wcag_contrast`, public `mix_hex`); `EMU_PER_PX_AT_1280` + `emu_to_px` / `px_to_emu` / `_emu_to_px_dict` in `scripts/_chrome_schema.py`; `write_brand_css()` in `register_template.py` (emits `brand.css` sidecar at registration); WCAG AA contrast warning at register time; `playwright>=1.40,<2.0` dep + INSTALL.md Step 1.5.
- **M4** (`c16b36e`): NEW `agents/slide-builder-translator.md` (~350 lines, per Spec 4); Pattern B branch added to `agents/slide-builder-worker.md`; INSTALL.md Step 7 for translator agent install + verify.
- **M5** (`0812fc5`): `build_deck.py` emits `PATTERN: B|C` into per-slide `_prompt.md` via `_classify_all_slides()` + `build_placeholders()`; `finalize_deck.py` discovers `option_X_native.py` (translator output), classifies it as `pattern_b_translated`, parses `__template_fields__` header for placeholder population, threads through `_apply_body_canonical_finishing()` with new `template_fields_override` kwarg.
- **M6** (`a712129`): R4.1 – R4.8 QC rules in `finalize_deck.py::_check_r4_rules_for_pattern_b()` (3 Critical / 4 Major / 1 Advisory per Spec 6); REVIEW.html surfaces per-zone SSIM + R4 severity chips via `build_review.py::render_pattern_b_qc_section()`; new `slide-qc/VISION_QC_PROTOCOL.md` documents R1 – R8 with severity table.

### Removed — M7 Mermaid retirement (2026-06-17, Decision 6 locked)
- `scripts/render_mermaid.py` — Mermaid CLI wrapper deleted. Pattern B HTML→PNG replaces it for curved-container diagrams.
- `reference/fallback.md` + `reference/fallback-examples/` directory — Mermaid contract docs + worked `.mmd` examples deleted.
- `scripts/finalize_deck.py` functions: `_resolve_mermaid_theme()`, `_render_mermaid_png()`, `_assemble_fallback_pptx()`. `FALLBACK_MERMAID_TOKEN` constant + the `fallback_mermaid` branch of `_classify_option()` + the build_pptx fallback branch removed. `--theme` CLI argument removed. `mermaid_theme` argument removed from `build_pptx()`, `write_result()`, `write_meta_json()` writes, and the dispatch_plan output. `OptionStatus.mmd_path` / `OptionStatus.mermaid_png_path` fields removed.
- `scripts/build_deck.py` functions: `_compute_theme_variables()`, `generate_mermaid_theme()`. The inline brand-theme sanity check that followed Mermaid theme generation was retired with it (brand-color validation now lives at `register_template.py` Phase 3 + M3 WCAG warning).
- `_meta_schema.py::MetaJson.mermaid_theme` made OPTIONAL (default `""`) so existing v3 metas with the field still validate; new writes omit it. No schema version bump.
- `INSTALL.md` Step 2 (Mermaid CLI install + verify). Consolidated verify block (line ~165) no longer checks `mmdc`.
- `agents/slide-builder-worker.md` fallback-trigger Step 7: replaced with Pattern C `SKELETON_REJECTED` route or Pattern B native HTML+SVG authoring.
- `prompt.md`: `{{FALLBACK_MD_PATH}}` and `{{FALLBACK_EXAMPLES_DIR}}` placeholder rows removed; Step 4 "fallback trigger" rewritten for the Pattern B / C split; output contract no longer mentions `# FALLBACK_MERMAID:` token.
- `SKILL.md`: Fallback-path description rewritten — Pattern B is the supersession; Mermaid CLI removed from the INSTALL.md summary.

Stale builds that carry `# FALLBACK_MERMAID:` line-1 markers will now fall through to the `native` classifier and crash at execution. The operator re-builds; no production decks contained Mermaid artifacts at retirement time.

### Resolved — Slide 16 strikethrough (2026-06-17)
The OTC slide 16 strikethrough defect (forensic entry in private `SLIDE_LAB_FEEDBACK_LOG.md` 2026-06-16) is closed as `resolved-by-pattern-b-superseding`. M4 demonstrated Pattern B rebuilds slide 16 cleanly. The actual root cause was confirmed in PowerPoint: overlapping textbox content from undersized description boxes — a geometry-cascade in the python-pptx layer, not a font-decoration bug. No inline patch to `option_A_native.py` is required because Pattern B replaces the rendering path wholesale.

### Deferred (M7 scope, not flipped)
Production defaults remain `enable_pattern_b: false` + `default_pattern: legacy`. Flipping the master switch requires a separate gating task — Mario validates Pattern B end-to-end on a real (non-test) deck before cutover. See plan at `C:\Users\m.a.peralta\.claude\plans\stop-telling-me-to-indexed-puzzle.md`.

---

## [Unreleased — pre-Pattern B] — v0.1 hardening + taxonomy consolidation (2026-05-26 post-tag)

### Changed — Deck-type taxonomy: 17 → 7 + 1 edge (2026-05-26)

Three-agent committee analysis (Reduction maximalist / Preservation realist / Mechanism check) found the canonical deck-type list in `storyline-helper/SKILL.md` had drifted to 17 types with only 6 unique gate-check mechanisms — half the labels were redundant. Worse, the Mode Check and Step 0.7 Decision-2 tables disagreed on which 16/17 were canonical (e.g., "Facilitation Deck" was in Decision-2 but not in Mode Check). Off-canon types silently bypassed the Step 7 Part 5 deck-type-specific gate check.

The taxonomy now consolidates to 7 + 1 edge:

1. **Recommendation / POV** — absorbs Executive Briefing, Strategic Plan, Investor Pitch, Partnership Proposal.
2. **Business Case** — kept distinct so a future CFO-grade gate (NPV / options compare / sensitivity) has a hook. Currently shares Recommendation's gate; v0.2 sharpens.
3. **Diagnosis** — absorbs Problem Diagnosis + Feasibility Study (verdict = cause-claim).
4. **Operating Review** — absorbs QBR, Status, Board Update, Market & Competitive Analysis (all G3+G4 variance-and-implication).
5. **Capability Pitch** — kept distinct (G5 differentiation; buyer chooses *who*, not *what*).
6. **Workshop Readout** — kept distinct (past-tense decision record).
7. **Workshop Design** — kept distinct per Agent C's pitfall: the label encodes a *routing decision* (gate bypass), not just a gate variant. Folding it into anything else would break the Step 0.7 overlay branch.

**+1 edge — Training / Enablement.** Demoted from primary type to documented sub-route. Edge cases use it; standard consulting work picks one of the 7.

**Files modified:**
- `storyline-helper/SKILL.md` § Mode Check (line ~110) — examples + list now reflect 7+1.
- `storyline-helper/SKILL.md` § Step 0.7 Decision 2 (line ~259) — 17-row table → 7-row table.
- `storyline-helper/SKILL.md` § Step 7 Part 5 (line ~505) — 9-row gate-check table → 7-row.
- `storyline-helper/SKILL.md` § Part 7 + Part 8 — updated absorbed-type references.
- `storyline-helper/SKILL.md` § Brief format spec (line ~778, 785) — "16 types" → "7 canonical + Training edge."
- `storyline-helper/_decisions/v0.2-improvements-queue.md` — Business Case gate sharpening + Workshop Design gate-bypass decision still parked.

Existing briefs with old type names (e.g., `deck_type: Executive Briefing`) continue to work — `slide-builder` treats `deck_type` as free-text metadata, no code key on the string.

---

## [Unreleased] — v0.1 hardening pass (2026-05-26 post-tag)

Behavioral guardrails + Tier 1 install/safety blockers + Tier 2 production-readiness fixes from the v0.1 audit handover (`_decisions/v0.1-audit-handover-2026-05-26.md`) and the follow-up 4-agent regression audit.

### Added

- **`slide-builder/agents/slide-builder-worker.md`** as source-of-truth for the per-slide Stage-2 worker (was orphaned at `~/.claude/agents/slide-builder-simple-worker.md`). INSTALL.md Step 6 documents the copy step.
- **INSTALL Step 6 content-aware verification** — `Select-String -Pattern "option_A.py"` proves the installed worker is the v0.1 contract, not a stale v1 copy.
- **`_contract.py` import-smoke check** — fourth check imports all 14 pipeline modules to surface module-load-time errors at contract test time.
- **`compile_picks.py` timestamped backup** of `final_deck.pptx` on overwrite.
- **`compile_picks.py` save-time error handling** — `PermissionError` / `OSError` surfaces an actionable message ("close PowerPoint") and exits with code 3 instead of a raw traceback.
- **`finalize_deck.stash_raw` loud failure** — Windows file-lock failures during the rename now surface via `st.error` instead of silent return.
- **`clean.py` safety guards** — refuses drive roots, user home, paths under the skill itself, and `--deep` without explicit `--yes-i-really-want-to-wipe-prompts`. Exit codes 3 / 4 / 5.
- **Storyline-helper hard rules** — per-slide handshake required (Step 5); review must be acknowledged before brief saves (Step 9); never ask the user to classify the deck (Mode Check).
- **Slide-builder hard rule** — no auto-accept on template registration; user must respond to `register.html`.

### Changed

- **SKILL.md** — v1/v2 history deferred to a bottom appendix; main flow no longer points new users at `DECISIONS.md` (503 lines) before doing work. Duplicate "Input contract" section deleted. Adjacency attribution fixed (gate-preview + review, not finalize). Mode Check opener hardened against menu-style questions.
- **`prompt.md`, `DECISIONS.md`** — Hardline #3 adjacency attribution corrected at all callers.
- **`prompt.md`, `SKILL.md`, `DECISIONS.md`** — Hardline #4 (brief fidelity) reframed as prompt-time-only with v0.2 enforcement target.
- **`TROUBLESHOOTING.md`** — exit-code tables re-derived from actual `sys.exit()` calls in every script.
- **`twins/composer.py`** — stripped 654 lines of dead v1 chassis-vocabulary code; kept only `_find_blank_layout`, `_strip_layout_placeholders`, `_clear_existing_slides` used by finalize/compile.
- **`convergence-hold-declaration-2026-05-26.md`** — banner enumerates what's now Path D-obsoleted in the body.
- **Cross-skill v1-script references** — `slide-qc/SKILL.md`, `rfp-helper/SKILL.md`, `slide-builder/icons/README.md`, `scripts/icon_helper.py`, `twins/helpers.py` repointed off deleted `build_slide.py` / `extract_icons.py` / `phase-a-rules.md` / `visual-treatment-library.md`.
- **Three anti-pattern WHY.md cross-references** repointed at `reference/anti-patterns.md` / `reference/layouts.md`.

### Removed

- **`QUICKSTART.md`** — content folded into `examples/RUN.md`; was a first-day onboarding speed bump.
- **Stale v1 worker** at `~/.claude/agents/slide-builder-simple-worker.md` (replaced by `slide-builder-worker.md`).

### Added — Phase 10 drift-prevention forcing function (2026-05-26)

- **`scripts/_contract.py` gained three new checks** (now 7 total): `check_install_sentinels` (source/installed content fingerprint match — first sentinel: worker agent must contain `option_A.pptx` output-contract string), `check_doc_file_refs` (every backtick-wrapped markdown ref must resolve; allowlists for runtime artifacts, deleted-by-design, user-memory cross-context, and user-context dir prefixes), `check_type_hints_resolve` (forces `typing.get_type_hints()` past PEP 563 deferral).
- Two new behavioral memories in `~/.claude/projects/.../memory/`: `feedback_existence_vs_content.md` ("done" means user-facing behavior works end-to-end), `feedback_cleanup_chat_cannot_self_declare.md` (cleanup chat marks `claimed-complete-by-cleanup`, only fresh audit chat marks `audit-confirmed`).

### Changed — Phase 10

- **Worker save contract fixed.** Worker agent rewrite (source + installed at `~/.claude/agents/slide-builder-worker.md`) corrected from "saves to `sys.argv[1]`" to the prompt.md-canonical `prs.save(str(Path(__file__).resolve().parent / "option_A.pptx"))`. md5 match verified between source and installed copies. INSTALL Step 6 sentinel grep enforces this going forward.
- **Phantom archive path refs rewritten.** `SKILL.md`, `CHANGELOG.md`, `reference/anti-patterns.md`, `twins/composer.py` no longer claim `slide-builder_archived_2026-05-26/` lives on disk (it doesn't). Refs rewritten as "archived and removed from disk."
- **`project_slide_lab_architecture.md` v1-perspective error fixed.** The "skill is being archived" instruction (written when v1 was active) no longer tells future Claude not to import from the live v0.1 skill.
- **`convergence-hold-declaration-2026-05-26.md`** banner expanded to declare the doc fully superseded; body intentionally retained as forensic audit trail.
- **Three stale anti-pattern WHY.md cross-refs** dropped (`do/single-finding/`, `do/chart-bottom-takeaway/`, etc.) — v1's `do/` corpus never ported to v0.1; refs were dangling.

### Removed — Phase 10

- **Three stale v1 agents** from `~/.claude/agents/`: `slide-builder.md`, `slide-designer.md`, `deck-builder.md`. Only `slide-builder-worker.md` remains.
- **`slide-builder/icons/_audit/`** (254 KB) + **`slide-builder/icons/_backup/`** (736 KB) hangover dirs.
- **`~/.claude/skills/smoke_test.py`** orphan (imported deleted v1 modules; crashed at step 1).

---

## [v0.1] — 2026-05-26

First release after the Path D consolidation (v1 retired, v2 wins). See `_decisions/cleanup-plan-master-2026-05-26.md` for the full 8-phase cleanup log.

### Added

- **Geometric-pattern build pipeline** — 9 splits + 3 diagram primitives + 2 special objects + 1 Mermaid fallback (14 patterns) governed by 5 hardline rules. The pattern is the spec.
- **Chat-driven `register_template.py`** — three subcommands (`propose` / `commit` / `interactive`). Replaces the PowerShell TTY-gated flow for coworker setup. Safety property preserved via explicit `picks.json`.
- **Pydantic-validated `_meta.json`** at schema version 2 — adds `brand_primary` + `brand_accent` fields driven from `brand.yml` so no FedEx-defaults leak into non-FedEx decks.
- **`_paths.py` registry** — single source of truth for ~35 pipeline artifact filenames across 5 scripts. Filename helpers + uppercase constants for both absolute-path and slide-relative call sites.
- **`_contract.py` module-load contract test** — verifies paths registry, meta-JSON schema round-trip, and handoff coverage at the manifest level. Required to pass before any release tag.
- **`_log.py` build.log tee** — every pipeline-script run appends timestamped stdout + stderr to `<out>/build.log`.
- **`clean.py`** — removes ephemeral artifacts from a build dir while preserving `picks.json`, agent build scripts, and prompts. `--deep` for full reset.
- **`diagnostic.py`** — bundles `_meta.json` + all `_prompt.md` + `*.qc.json` + `build.log` into a zip for bug reports.
- **Onboarding docs** — `README.md`, `INSTALL.md`, `examples/quickstart-brief.md`, `examples/RUN.md`, `TROUBLESHOOTING.md`.
- **9 Tier-1 anti-exemplars** ported from v1 corpus into `reference/anti-patterns/<slug>/` with PNG + WHY.md.
- **Brand-display polish in `REVIEW.html`** — `fedex` → `FedEx`, `accenture` → `Accenture`, etc., via per-brand override table.

### Changed

- **Default skill** — `slide-builder` is now the default Slide Lab build layer (was: opt-in alongside the legacy chassis-vocabulary skill). The legacy chassis-vocabulary skill was archived and removed from disk during Path D consolidation.
- **Shared infrastructure re-homed in-tree** — all infra previously imported from the legacy chassis-vocabulary skill (`twins/{client_theme,composer,helpers}.py`, `scripts/icon_helper.py`, `patches/patches.py`, `icons/*.xml`) was re-homed into this skill in Phase 2. No more cross-skill imports.
- **SKILL.md routing** — single-default-skill model. Drops A/B testing section, "Exclusive to v1" section rewritten as "v1 retirement," adds "first time?" + brief-format-spec sections.
- **Rotation seed documentation in `layouts.md:5`** — now correctly documents `pattern_pick_seed = md5(content_hash + slide_n)` and `variant_seed_{A,B,C} = md5(content_hash + slide_n + option_letter)` per `build_deck.py:404-427`. Previous text was a v1-era fiction.
- **`reference/fallback.md` brand mapping section** — rewritten for the `brand.yml`-canonical world; the slot-position mapping table is replaced with the canonical `brand.yml` field mapping from `build_deck.py::_compute_theme_variables`.
- **`page_type` lookup in build_review.py** — now reads only from `_meta.json` (canonical). The dead `**Page type (heuristic):**` regex against `_prompt.md` is removed.
- **PNG-too-small QC floor** — lowered from 50KB to 12KB so sparse/cover slides don't false-positive.
- **`render_mermaid.py --theme`** — now required (no FedEx-shaped default).

### Removed

- **`theme/mermaid-brand.json`** (dead fallback file — Stage-1 requires per-client brand.yml).
- **`scripts/_verify_critical_fixes.py`** (one-off scaffold).
- **12 already-decisioned v1 `dont/` slugs** (`b-bridge`, `b-framing`, etc.).
- **40 legacy process-artifact files** at the archived skill's `exemplars/` root (`_fix_report_*`, `_qc_report_*`, `_reverify_report_*`, `_phase3_*`).
- **NFL scope** — explicitly out of scope for v0.1.

### Notes

- Phase 7 (bloat archive) reclaimed approximately 1.26 GB across OneDrive, Documents, and Downloads — see `_decisions/cleanup-plan-master-2026-05-26.md` Phase 7 status log for the file-by-file accounting.
- Phase 8 archived the legacy chassis-vocabulary skill (since removed from disk) and consolidated the surviving skill at `slide-builder/`. All internal references, the storyline-helper handoff, and memory files were updated in the same pass.
