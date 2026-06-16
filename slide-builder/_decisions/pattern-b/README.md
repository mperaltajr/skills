# Pattern B refactor — Phase 0 spec lock

This directory contains the locked design specs for the Slide Lab Pattern B refactor (HTML-spec → native PPTX translation). Drafted 2026-06-16 after a 3-agent audit committee identified 14 underspecified pieces in the initial plan. Phase 0 = lock all 14 before any code is written.

## What Pattern B is

A refactor of `slide-builder` that changes the default build path:

- **Today:** workers write `option_X.py` (python-pptx code) → finalize executes → render PNG. Output is editable PPTX. Visual quality limited by python-pptx muscle memory (workers default to `MSO_SHAPE.RECTANGLE`; output is sterile).
- **Pattern B:** workers write `option_X.html` → Playwright renders to PNG → user picks in REVIEW.html → a NEW translator agent converts picked HTML to native python-pptx that visually matches the HTML PNG. Output is editable PPTX with consulting-grade visual quality.

The HTML phase gives Claude visual feedback (sees what it's building). The translation phase preserves editability (text stays native, not embedded as image).

## The six design decisions (LOCKED 2026-06-16)

| # | Decision | Locked at |
|---|---|---|
| 1 | HTML canvas size | **1280×720** (PowerPoint default, 1:1 EMU/px mapping) |
| 2 | Pattern routing | **Moderate** — bullets/dividers → Pattern C native; visual structure → Pattern B HTML |
| 3 | Agent batching | **Defer** — ship Pattern B in 3-4 weeks; accept ~25% token increase; batching as separate workstream later |
| 4 | Editability boundary | Title/subtitle/footer ALWAYS in template placeholders. Charts via matplotlib + Excel sibling. Icons stay on existing library. Curved diagrams as image. Everything else native. |
| 5 | QC strictness | **3 Critical / 4 Major / 1 Advisory** across R4.1–R4.8 |
| 6 | Mermaid | **Retire entirely** — HTML supersedes it |

Plus one architectural clarification (Option I — full-slide HTML with body-zone extraction; chrome text → template placeholders, never freeform).

Full decision history with rationale lives in `C:\Users\m.a.peralta\Documents\SLIDE_LAB_FEEDBACK_LOG.md` under the "Pattern B refactor — Phase 0 decision log" section.

## The eight technical specs

| # | Spec | File |
|---|---|---|
| 1 | HTML canvas + CSS conventions (foundation) | [SPEC.md](SPEC.md) |
| 2 | Color translation (hex ↔ RGBColor, brand.css, WCAG contrast) | [spec-2-color-translation.md](spec-2-color-translation.md) |
| 3 | Geometry translation (chrome.yml EMU storage, emu↔px conversion, CSS layout extraction) | [spec-3-geometry-translation.md](spec-3-geometry-translation.md) |
| 4 | Translator worker contract (input/output/dispatch/validation) | [spec-4-translator-worker-contract.md](spec-4-translator-worker-contract.md) |
| 5 | Fidelity measurement (SSIM zone thresholds, baseline capture, regression check) | [spec-5-fidelity-measurement.md](spec-5-fidelity-measurement.md) |
| 6 | QC rules R4.1–R4.8 with locked severities | [spec-6-qc-rules-R4.md](spec-6-qc-rules-R4.md) |
| 7 | `_meta.json` schema v3 migration | [spec-7-schema-version-migration.md](spec-7-schema-version-migration.md) |
| 8 | `--pattern` rollback flag + settings.json feature flag | [spec-8-rollback-flag.md](spec-8-rollback-flag.md) |

## Status

- ✅ 6 design decisions locked
- ✅ 8 technical specs drafted
- ⏳ Next: agent audit of each spec before any code lands
- ⏳ Then: Phase 1 (HTML render pipeline) starts

## The four quality guarantees that must hold

1. **Text in final PPTX is always editable.** No exceptions. Verified by build-time check that every text element is in a placeholder or named textbox.
2. **Visual fidelity from HTML to native PPTX is ≥90% per zone via SSIM** (see Spec 5).
3. **No silent regressions on existing builds.** Verified by SSIM-comparing the refactored output against baselines captured from the current pipeline (see Spec 5 §5–6).
4. **Token cost per build may increase by up to ~25% under Pattern B** vs current dispatch (revised per Decision 3 — batching deferred). Visual quality improvement justifies the cost; batching recovers it later.

## Phase order (revised post-audit)

- **Phase 0**: lock all specs (this directory) ← current
- **Phase 1a + 2 interlocked**: Playwright pipeline + worker HTML build, with worker self-check (read own rendered PNG before declaring done)
- **Phase 1b**: Render determinism validation
- **Phase 3**: REVIEW.html shows HTML renders
- **Phase 3.5 (new)**: Translator agent dispatched after picks, per-slide
- **Phase 4**: Native python-pptx generation via translator
- **Phase 5**: Vision QC with R4 rules + per-zone SSIM
- **Phase 6**: Pattern routing wiring in `build_deck.py`
- **Phase 7**: Documentation + migration
- **Phase 8**: Known-defect cleanup (slide 16 strikethrough — closes 2026-06-16 open log entry)
- **Phase 9**: End-to-end smoke + token cost audit

## How to read these specs

If you're picking up this refactor in a new session, read in this order:

1. **SPEC.md** — understands the canvas, zones, CSS conventions, kill-list
2. **spec-4-translator-worker-contract.md** — the new agent that's the central new component
3. **spec-3-geometry-translation.md** — how shapes get positioned
4. **spec-2-color-translation.md** — how colors flow through
5. **spec-5-fidelity-measurement.md** — how we know the output matches the design
6. **spec-6-qc-rules-R4.md** — what failure modes catch what
7. **spec-7-schema-version-migration.md** — how the build artifacts evolve
8. **spec-8-rollback-flag.md** — how to unship if something goes wrong

Then read the decision log section in `SLIDE_LAB_FEEDBACK_LOG.md` for the rationale behind each lock.

## What's still open before Phase 1 can start

- Agent audit of each spec (3 lenses: architecture / QC sufficiency / backward-compat). Goal: catch anything the cleanup chat missed before code starts.
- Mario sign-off on the audit findings.

After those two: build.
