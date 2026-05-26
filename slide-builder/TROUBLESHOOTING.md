# Troubleshooting — Slide Lab

If a pipeline script exits non-zero, find the exit code below. Each section also lists the most common console messages so you can grep `build.log` (in your output dir) for the relevant line.

## Quick triage

1. Open `<out>/build.log` — every pipeline-script invocation appends timestamped stdout + stderr there.
2. Run `py -3 scripts/_contract.py` from the skill root. If the contract test fails, the pipeline scripts are inconsistent with each other — fix that first.
3. Run the INSTALL verification one-liner. If `install OK` doesn't print, an environment dep is missing.

## Exit-code reference

Tables below were re-derived from each script's actual `sys.exit()` / `return` calls on 2026-05-26 per audit finding T2.9. If you see a code listed in a script's `--help` output that isn't on this table, treat the table as wrong and update it.

### `build_deck.py`

| Code | Meaning | Fix |
|---|---|---|
| 1  | Brief file unreadable OR brief unparseable (no front-matter, malformed YAML) | Check the `--brief` path and that the file starts with `---` YAML front-matter ending with `---`. |
| 2  | No parseable slides found in the brief | Slide headers must match `## Slide N — Title` or `### Slide N — Title` (title is optional but recommended). Open the brief and confirm headers. |
| 3  | `--template` doesn't exist | Verify the `--template` path. Templates typically live under `OneDrive\Claude Projects\_templates\` or `<Client>\_templates\`. |
| 4  | `prompt.md` template missing from the skill | The skill directory is incomplete. Re-clone or re-extract the skill. |
| 5  | Brief load error (filesystem / encoding) | Check the brief file is readable + UTF-8 encoded. |
| 6  | Theme generation or validation failed (brand.yml malformed, primary == accent, etc.) | Re-register the template via the chat-driven `propose` → `commit` flow. See SKILL.md § "Register a new client template." |
| 7  | Stage-1 sanity check failed — `BrandSidecarMissing` / `BrandSidecarStale` / `mmdc` not installed / `mmdc` version mismatch | Re-register the template (BrandSidecar errors) or `npm install -g @mermaid-js/mermaid-cli@11.4.0` (mmdc errors). |

### `finalize_deck.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` missing or not a directory, OR `_meta.json` missing under `--out` | Pass the same `--out` you gave `build_deck.py`. If `_meta.json` is missing, run `build_deck.py` first. |
| 7  | Mermaid theme missing — `_meta.json::mermaid_theme` references a file that doesn't exist | Re-run `build_deck.py` to regenerate the theme. |

### `compile_picks.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` invalid, `_meta.json` missing, OR `--template` from `_meta.json` doesn't exist | Pass the build's output dir. Verify the template path stored in `_meta.json`. |
| 3  | Could not write `final_deck.pptx` — destination locked (PowerPoint has it open, or antivirus mid-scan) | Close PowerPoint, pause AV on the build dir if needed, and re-run `compile_picks.py`. The prior deck was preserved via the T2.6 timestamped backup. |
| 1  | Compile finished but final deck doesn't open cleanly, OR per-option copy failures occurred | Check `COMPILED.md` for per-option failure rows. Open the produced final deck in PowerPoint to confirm. |

### `build_review.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` missing or not a directory | Pass the build's output dir. |
| 3  | No slides discoverable in `--out` (no `slide_NN/` subdirs) | Run `build_deck.py` then `finalize_deck.py` first. |

### `build_gate_preview.py`

| Code | Meaning | Fix |
|---|---|---|
| 1  | `--out` not a directory | Pass an existing build output dir. |
| 2  | No `slide_NN/` directories found in `--out` | `build_deck.py` hasn't run yet, or `clean.py --deep` wiped the dispatch outputs. |

### `register_template.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | Template path missing, picks.json missing/unreadable, OR picks.json malformed | The `commit` subcommand requires `--picks <path>` pointing at a valid picks JSON. See the script's `--help` for the JSON shape. |

### `clean.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` not a directory | Pass an existing output dir. |
| 3  | Safety check — refused (drive root, user home, or under the skill itself) | `clean.py` is for build output directories only. Pass the deck's `out/` path, not a system path. |
| 4  | Safety check — refused (`_meta.json` AND `dispatch_plan.md` both missing) | The path doesn't look like a Slide Lab output directory. Probably a typo'd `--out`. If you really want to delete that directory, use `Remove-Item` or `rm` directly. |
| 5  | `--deep` requires `--yes-i-really-want-to-wipe-prompts` | The flag is intentional — `--deep` wipes the worker fanout output. Add the long flag if that's really what you want. |

### `diagnostic.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` not a directory | Pass the build output dir you want bundled. |

## Common console-message diagnoses

### "BrandSidecarMissing"
The client template at `<path>.pptx` lacks `<stem>.brand.yml` next to it. Register the template (see SKILL.md § "Register a new client template").

### "BrandSidecarStale"
The `<stem>.brand.yml` exists but its SHA stamp doesn't match the template's current SHA (the template was edited). Re-register the template — run `register_template.py propose` and `commit` again.

### "mmdc not on PATH" / "Mermaid CLI version mismatch"
`npm install -g @mermaid-js/mermaid-cli@11.4.0`. The pinned version matters — fallback diagram rendering was tested against 11.4.0 specifically.

### "render_libre failed"
LibreOffice isn't installed, or `soffice.exe` isn't at the expected Windows path. See INSTALL.md § Step 3.

### "_meta.json schema_version=N is not supported"
Either you're running a newer `build_deck.py` against an older output dir, or vice versa. Re-run `build_deck.py` to regenerate `_meta.json` at the current schema version.

### "_meta.json schema validation: ..." (reader-side warning, not a hard error)
A reader (`finalize_deck`, `compile_picks`, `build_review`, `build_gate_preview`) loaded a `_meta.json` that didn't fully match the pydantic schema. The reader continues with degraded behavior. If the warning persists across re-runs, re-generate `_meta.json` via `build_deck.py`.

### "FALLBACK FAILED: ..."
A `# FALLBACK_MERMAID:` option script declared a fallback, but the sibling `.mmd` is missing or syntactically broken. Check the per-slide agent's Mermaid spec at `<out>/slide_NN/option_X.mmd`.

### "PNG too small (XXX bytes; floor 12KB)"
A rendered option thumbnail is smaller than expected — usually means the LibreOffice render produced a near-blank canvas. Open the corresponding `option_X.pptx` directly in PowerPoint to confirm whether the slide is actually empty. If the slide is intentionally minimal (cover with one line), the floor was lowered to 12KB in v0.1 — but a sub-12KB PNG is almost always a render failure.

### "SKELETON_REJECTED: ..."
A per-slide agent rejected the slide because the brief and the assigned pattern fundamentally disagree (e.g., brief enumerates 2 items, pattern expects 4 cells). This is **correct behavior** — see SKILL.md § "Hardline rules" #5. Either pick a different pattern for that slide or revise the brief.

### "worker did not produce option script" (classification: missing)
The parent session promised an option that no worker delivered. Surfaces in `RESULT.md` as a `[MISSING]` row + downgrades the Built count. Re-dispatch the worker for that slide if a fuller deck is wanted.

## If you're still stuck

Run `py -3 scripts/diagnostic.py --out <out>` to bundle `_meta.json`, all `_prompt.md` files, all `*.qc.json` files, and `build.log` into a single zip. Attach to your bug report.
