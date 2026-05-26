# Changelog — Slide Lab

All notable changes to this skill. Versioning follows [Semantic Versioning](https://semver.org/) loosely: major bumps signal architectural changes, minor bumps signal feature additions, patch bumps signal fixes.

## [Unreleased]

### Added
- (place new work-in-progress items here)

### Changed
- (place in-progress changes here)

### Fixed
- (place in-progress fixes here)

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
- **Onboarding docs** — `README.md`, `INSTALL.md`, `QUICKSTART.md`, `examples/quickstart-brief.md`, `examples/RUN.md`, `TROUBLESHOOTING.md`.
- **9 Tier-1 anti-exemplars** ported from v1 corpus into `reference/anti-patterns/<slug>/` with PNG + WHY.md.
- **Brand-display polish in `REVIEW.html`** — `fedex` → `FedEx`, `accenture` → `Accenture`, etc., via per-brand override table.

### Changed

- **Default skill** — `slide-builder` is now the default Slide Lab build layer (was: opt-in alongside the legacy chassis-vocabulary skill). The legacy skill is archived at `slide-builder_archived_2026-05-26/`.
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
- Phase 8 archived the legacy chassis-vocabulary skill to `slide-builder_archived_2026-05-26/` and consolidated the surviving skill at `slide-builder/`. All internal references, the storyline-helper handoff, and memory files were updated in the same pass.
