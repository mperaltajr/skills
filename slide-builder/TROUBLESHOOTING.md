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
| 7  | Stage-1 sanity check failed — the installed worker/translator agents differ from the repo's, brand sidecar missing/stale, malformed `brand.yml`, `chrome.yml` missing or unloadable, or the `slide-qc` sibling skill isn't installed | For the agents: copy `slide-builder/agents/*.md` to `~/.claude/agents/` (the message prints the exact commands), then start a new session. Otherwise re-register the template via `propose` → `commit`, or install `slide-qc` (INSTALL.md Step 5). The message names which one fired. |
| 8  | (retired) was the yes/no template prompt, which could never be answered from inside Claude Code | `--confirm-template` is still accepted and does nothing. |
| 9  | Layout resolution failed — no per-slide `Layout:` AND no front-matter `default_layout:` AND chrome.yml has zero or multiple body-canonical layouts | Add `default_layout: <name>` to the brief's YAML front-matter (or `Layout:` per slide). See the error message for the list of available layouts. |
| 10 | Storyline gate: the brief is not sealed, its seal does not match its text (edited after the gate), or it has no marker | Run storyline-helper's gate, then `py -3 scripts/seal_brief.py --brief <brief>`. Typing the marker by hand is refused. A brief written in-session: `--assume-gated` (recorded in `_state.json`). Non-narrative flows: `mode: template-fill` / `rebuild-slice` / `rfp`. |
| 12 | The template has not been confirmed by a person | Have the user open the mock slide (`<stem>/selftest/mock.pptx`), then `register_template.py confirm <template>`. Or, on the user's say-so, `--allow-unconfirmed` (recorded in `_state.json`). |

### `finalize_deck.py`

| Code | Meaning | Fix |
|---|---|---|
| 2  | `--out` missing or not a directory, OR `_meta.json` missing under `--out` | Pass the same `--out` you gave `build_deck.py`. If `_meta.json` is missing, run `build_deck.py` first. |
| 7  | Chrome sidecar missing or stale — `chrome.yml` for the template is absent or no longer matches the registered template | Re-register the template via the chat-driven `propose` → `commit` flow to regenerate `chrome.yml`. |
| 8  | A slide title wraps into the heading band / body (`[4c] TITLE / BAND OVERLAP`) | Shorten the flagged titles (brief header for direct-path slides; `data-template-field="title"` in the HTML for sketch slides), then re-run. |
| 11 | Expected option output is missing | The message says which step: **"designed but not yet translated"** → dispatch `slide-builder-translator` on the listed HTML; **"no design output"** → the worker was never sent, is still running, or failed (wait, or re-dispatch). Unpicked sketch options are not missing; they are simply not converted. `--allow-missing` proceeds and records the gaps as blocked. |
| 12 | Brand primary and accent colors nearly identical | Re-register and pick visibly different swatches. |
| 13 | Graft halted: a title or takeaway would be silently dropped, or the layout drifted from registration | The message names the slide and option. Pick a layout with the needed placeholder, or re-register the template. |
| 14 | Dark-variant collision: content would be invisible on the dark background | Change the colliding colors in the option, or the template's `dark_bg_hex`. The offending options are recorded as blocked. |
| 15 | An option failed to build, graft or render | `RESULT.md` lists them; each is recorded as blocked with the reason, and compile will refuse to ship it. Fix the option and re-run. |
| 16 | A slide names a layout `chrome.yml` does not have | Fix the slide's `layout` in `_meta.json`, or re-register the template. |

### `compile_picks.py`

| Code | Meaning | Fix |
|---|---|---|
| 5  | Refused. The message says which: no recorded picks (the user's Build command from REVIEW.html runs `record_picks.py`); no final check, or a wrong `--final-token`; a file shown in FINAL-CHECK.html changed since; a slide with no pick; an option never finalized or with a blocking finding; unreconciled figures on a supplied page; or `--out` not the build's folder. `--review-token` is retired. | Follow the order: REVIEW.html → `record_picks.py` → translate picked sketches → `finalize_deck.py` → `build_review.py --final` → the Build command from FINAL-CHECK.html. Never invent a token. |
| 6  | Refused: the deck failed the **package-integrity** check (orphaned slide parts, duplicate zip entries, or structure PowerPoint refuses: an incomplete `<p:style>`, duplicate shape ids, a missing relationship) | Nothing was replaced: the previous `final_deck.pptx` is untouched and the rejected file is kept as `final_deck.REJECTED.pptx`. Fix the option through the pipeline (usually a re-translate), never by editing the package. |
| 2  | `--out` invalid, `_meta.json` missing, OR `--template` from `_meta.json` doesn't exist | Pass the build's output dir. Verify the template path stored in `_meta.json`. |
| 3  | Could not write or swap in `final_deck.pptx` — usually the old copy is open in PowerPoint, or OneDrive/antivirus holds the folder | Close PowerPoint and re-run. The new deck is left as `final_deck.incoming.pptx`; the old one is untouched. |
| 1  | A picked option could not be copied (no deck was written), or the deck does not reopen or render | The message lists the failing options. Nothing was replaced. |

### `check_done.py`

| Code | Meaning | Fix |
|---|---|---|
| 1  | Not deliverable. It lists every broken link: no successful compile; the deck is not the compiled file or changed since; the brief changed after compile; the deck does not open or has structure PowerPoint refuses; a shipped option is blocked; no vision pass, a partial one, or one over different bytes; an open Critical or Major finding; unreconciled figures | Fix what it lists. Defects are fixed by rebuilding through the pipeline and recompiling, then re-running slide-qc. Only Advisory findings may remain open. |

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
