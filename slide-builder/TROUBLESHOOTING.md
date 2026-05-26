# Troubleshooting — Slide Lab

If a pipeline script exits non-zero, find the exit code below. Each section also lists the most common console messages that map to that exit code so you can grep `build.log` (in your output dir) for the relevant line.

## Quick triage

1. Open `<out>/build.log` — every pipeline-script invocation appends timestamped stdout + stderr there.
2. Run `py -3 scripts/_contract.py` from the skill root. If the contract test fails, the pipeline scripts are inconsistent with each other — fix that first.
3. Run the INSTALL verification one-liner. If `install OK` doesn't print, an environment dep is missing.

## Exit-code reference

### `build_deck.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` missing or not a directory | Pass an existing directory or one Python can create. |
| 3  | Client template path doesn't exist | Verify the `--template` path. Templates live under `OneDrive\Claude Projects\<client>\_templates\`. |
| 4  | `prompt.md` template missing | The skill directory is incomplete. Re-clone or re-extract the skill. |
| 5  | Brief file doesn't exist or can't be parsed | Check the `--brief` path and front-matter YAML syntax (`---` delimiters, key:value pairs). |
| 6  | Stage-1 sanity check failed — `brand.yml` missing | Register the client template first: `register_template.py propose <template>` → take picks → `commit --picks <picks.json>`. See SKILL.md § "Register a new client template." |
| 7  | Stage-1 sanity check failed — `mmdc` not installed | `npm install -g @mermaid-js/mermaid-cli@11.4.0`. Verify with `mmdc --version`. |
| 8  | `_meta.json` schema validation failed at write time | The brief produced a meta dict that doesn't match the pydantic schema. Check the pydantic error in `build.log` — it names the failing field. |

### `finalize_deck.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` missing or not a directory | Pass the same `--out` you gave `build_deck.py`. |
| 5  | `_meta.json` not found in `--out` | Run `build_deck.py` first. The output dir must contain `_meta.json`. |
| 7  | Mermaid theme missing | `_meta.json::mermaid_theme` references a file that was deleted. Re-run `build_deck.py` to regenerate. |
| 9  | All options failed to build | Check each `slide_NN/` for `option_X.py` errors. The console log lists per-option tracebacks. |

### `compile_picks.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` not a directory | Pass the build's output dir. |
| 3  | `picks.json` missing or empty | Pass `--picks` explicitly, or write `<out>/picks.json` with `{"slide_01": "A", "slide_02": "B", ...}`. Keys are `slide_NN` (zero-padded), not bare integers. |
| 4  | A picked option doesn't exist | The slide+letter referenced in `picks.json` doesn't have a built PPTX. Re-run `finalize_deck.py` or fix the pick. |

### `build_review.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` not a directory | Same as above. |

### `build_gate_preview.py`

| Code | Meaning | Fix |
|---|---|---|
| 1  | `--out` is not a directory | Pass an existing build output dir. |
| 2  | No `slide_NN/` directories found in `--out` | `build_deck.py` hasn't been run yet, or the output dir was cleaned. |

### `register_template.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | Template missing, picks.json missing, or picks.json malformed | The `commit` subcommand requires `--picks <path>` pointing at a valid picks JSON. See SKILL.md or the script's `--help` for the JSON shape. |

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
Either you're running a newer build_deck against an older output dir, or vice versa. Re-run `build_deck.py` to regenerate `_meta.json` at the current schema version, or pin the skill to the version that produced the file.

### "FALLBACK FAILED: ..."
A `# FALLBACK_MERMAID:` option script declared a fallback, but the sibling `.mmd` is missing or syntactically broken. Check the per-slide agent's Mermaid spec at `<out>/slide_NN/option_X.mmd`.

### "PNG too small (XXX bytes; floor 12KB)"
A rendered option thumbnail is smaller than expected — usually means the LibreOffice render produced a near-blank canvas. Open the corresponding `option_X.pptx` directly in PowerPoint to confirm whether the slide is actually empty. If the slide is intentionally minimal (cover with one line), the floor was lowered to 12KB in v0.1 — but a sub-12KB PNG is almost always a render failure.

### "SKELETON_REJECTED: ..."
A per-slide agent rejected the slide because the brief and the assigned pattern fundamentally disagree (e.g., brief enumerates 2 items, pattern expects 4 cells). This is **correct behavior** — see SKILL.md § "Hardline rules" #5. Either pick a different pattern for that slide or revise the brief.

## If you're still stuck

Run `py -3 scripts/diagnostic.py --out <out>` to bundle `_meta.json`, all `_prompt.md` files, all `*.qc.json` files, and `build.log` into a single zip. Attach to your bug report.
