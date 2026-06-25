# Troubleshooting — Slide Lab

If a pipeline script exits non-zero, find the exit code below. Each section also lists the most common console messages so you can grep `build.log` (in your output dir) for the relevant line.

## Quick triage

1. Open `<out>/build.log` — every pipeline-script invocation appends timestamped stdout + stderr there.
2. Run `py -3 scripts/_contract.py` from the skill root. If the contract test fails, the pipeline scripts are inconsistent with each other — fix that first.
3. Run the INSTALL verification one-liner. If `install OK` doesn't print, an environment dep is missing.

## Exit-code reference

The tables below list the exit codes each script returns. If you see a code in a script's `--help` output that isn't on this table, treat the table as wrong and update it.

### `build_deck.py`

| Code | Meaning | Fix |
|---|---|---|
| 1  | Brief file unreadable OR brief unparseable (no front-matter, malformed YAML) | Check the `--brief` path and that the file starts with `---` YAML front-matter ending with `---`. |
| 2  | No parseable slides found in the brief | Slide headers must match `## Slide N — Title` or `### Slide N — Title` (title is optional but recommended). Open the brief and confirm headers. |
| 3  | `--template` doesn't exist | Verify the `--template` path. Templates typically live under `OneDrive\Claude Projects\_templates\` or `<Client>\_templates\`. |
| 4  | `prompt.md` template missing from the skill | The skill directory is incomplete. Re-clone or re-extract the skill. |
| 5  | Brief load error (filesystem / encoding) | Check the brief file is readable + UTF-8 encoded. |
| 7  | Stage-1 sanity check failed — brand sidecar missing/stale, malformed `brand.yml`, `chrome.yml` missing or unloadable, or the `slide-qc` sibling skill isn't installed | Re-register the template via the chat-driven `propose` → `commit` flow (sidecar/chrome errors), or install the `slide-qc` skill at the expected path (see INSTALL.md Step 5). The error message names which one fired. |
| 8  | Template confirmation aborted — user answered "n" at the Y/N prompt, or stdin is not a TTY and `--confirm-template` was not passed | Re-run with the correct `--template`, or add `--confirm-template` for scripted/CI runs. |
| 9  | Layout resolution failed — no per-slide `Layout:` AND no front-matter `default_layout:` AND chrome.yml has zero or multiple body-canonical layouts | Add `default_layout: <name>` to the brief's YAML front-matter (or `Layout:` per slide). See the error message for the list of available layouts. |
| 10 | Storyline gate marker missing — the brief has no `storyline_gate_passed: true` | Re-run storyline-helper on the brief to emit `storyline_gate_passed: true`. Or add `mode: template-fill` / `mode: rebuild-slice` / `mode: rfp` to the front-matter for legitimate non-narrative flows. |

### `finalize_deck.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` missing or not a directory, OR `_meta.json` missing under `--out` | Pass the same `--out` you gave `build_deck.py`. If `_meta.json` is missing, run `build_deck.py` first. |
| 7  | Chrome sidecar missing or stale — `chrome.yml` for the template is absent or no longer matches the registered template | Re-register the template via the chat-driven `propose` → `commit` flow to regenerate `chrome.yml`. |
| 11 | Pre-flight gate — one or more expected `option_X.py` files are absent (interrupted worker) | The error message lists which slides need re-dispatch and prints the `_prompt.md` path for each. Re-dispatch the slide-builder-worker agent for those slides, then re-run `finalize_deck.py`. Override with `--allow-missing` to proceed with gaps (slides surface as `[MISSING]` in RESULT.md). |

### `compile_picks.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` invalid, `_meta.json` missing, OR `--template` from `_meta.json` doesn't exist | Pass the build's output dir. Verify the template path stored in `_meta.json`. |
| 3  | Could not write `final_deck.pptx` — destination locked (PowerPoint has it open, or antivirus mid-scan) | Close PowerPoint, pause AV on the build dir if needed, and re-run `compile_picks.py`. The prior deck was preserved via the timestamped backup. |
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
The client template at `<path>.pptx` lacks `<stem>/brand.yml` in the per-template sidecar subfolder. Register the template (see SKILL.md § "Register a new client template").

### "BrandSidecarStale"
The `<stem>/brand.yml` exists but its SHA stamp doesn't match the template's current SHA (the template was edited). Re-register the template — run `register_template.py propose` and `commit` again.

### "LegacyTemplateLayoutError"
The template was registered with the older flat sidecar layout (sidecars sit next to the .pptx instead of inside a `<stem>/` subfolder). Run the one-shot migration:

```powershell
py -3 slide-builder/scripts/migrate_template_layout.py "<directory containing the .pptx>"
```

This moves `<stem>.brand.yml`, `<stem>.theme.json`, `<stem>.chrome.yml`, and other sidecars into `<stem>/`. Existing builds keep working after the migration; no re-registration required.

### "ChromeSidecarMissingError"
The template's `<stem>/chrome.yml` is missing or has a null required field. Re-register the template — `register_template.py propose` then `commit` (or `commit-cli`). The chrome sidecar is regenerated from the template's actual layout XML each time.

### "ChromeLayoutMissingError"
A slide in `_meta.json` references a layout name that doesn't exist in `chrome.yml`. Either fix the slide's `Layout:` field in the brief to match a registered layout, OR re-register the template (a recent template edit may have removed/renamed the layout). The error message lists the layout names available in chrome.yml.

### "render_libre failed"
LibreOffice isn't installed, or `soffice.exe` isn't at the expected Windows path. See INSTALL.md § Step 3.

### "_meta.json schema_version=N is not supported"
Either you're running a newer `build_deck.py` against an older output dir, or vice versa. Re-run `build_deck.py` to regenerate `_meta.json` at the current schema version.

### "_meta.json schema validation: ..." (reader-side warning, not a hard error)
A reader (`finalize_deck`, `compile_picks`, `build_review`, `build_gate_preview`) loaded a `_meta.json` that didn't fully match the pydantic schema. The reader continues with degraded behavior. If the warning persists across re-runs, re-generate `_meta.json` via `build_deck.py`.

### "PNG too small (XXX bytes; floor 12KB)"
A rendered option thumbnail is smaller than expected — usually means the LibreOffice render produced a near-blank canvas. Open the corresponding `option_X.pptx` directly in PowerPoint to confirm whether the slide is actually empty. If the slide is intentionally minimal (cover with one line), the floor was lowered to 12KB — but a sub-12KB PNG is almost always a render failure.

### "SKELETON_REJECTED: ..."
A per-slide agent rejected the slide because the brief and the assigned pattern fundamentally disagree (e.g., brief enumerates 2 items, pattern expects 4 cells). This is **correct behavior** — see SKILL.md § "Hardline rules" #5. Either pick a different pattern for that slide or revise the brief.

### "worker did not produce option script" (classification: missing)
The parent session promised an option that no worker delivered. Surfaces in `RESULT.md` as a `[MISSING]` row + downgrades the Built count. Re-dispatch the worker for that slide if a fuller deck is wanted.

## If you're still stuck

Run `py -3 scripts/diagnostic.py --out <out>` to bundle `_meta.json`, all `_prompt.md` files, all `*.qc.json` files, and `build.log` into a single zip. Attach to your bug report.
