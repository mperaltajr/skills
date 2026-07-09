# Install — Slide Lab

Works on Windows, macOS, and Linux. The steps below show Windows (PowerShell)
commands; **on macOS/Linux, translate each command with the mapping below** —
the scripts, flags, and arguments are identical across all three.

| Windows (as written below) | macOS / Linux |
|---|---|
| `py -3 …` | `python3 …` |
| `& "C:\Program Files\LibreOffice\program\soffice.exe"` | `soffice` (on PATH), or macOS `/Applications/LibreOffice.app/Contents/MacOS/soffice` |
| `$env:USERPROFILE\.claude\skills` | `~/.claude/skills` |
| `Copy-Item` | `cp` |

LibreOffice is located automatically on every OS (see Step 2). Set the
`SLIDE_LAB_SOFFICE` environment variable to the full `soffice` path only if you
installed it somewhere non-standard.

## Prerequisites

| Component | Version | Why |
|---|---|---|
| Python | **3.10+** | Type hints and f-string features used throughout |
| LibreOffice | any recent | Headless PPTX → PNG render path (via slide-qc) |
| PowerPoint | 2019+ (optional, **Windows-only**) | Pixel-perfect QC pass; LibreOffice render is the cross-platform default |

## Step 1 — Python deps

```powershell
py -3 -m pip install -r requirements.txt
```

Verify:

```powershell
py -3 -c "import pptx, PIL, yaml, lxml, pydantic, pypdfium2, skimage; print('python deps OK')"
```

Expected: `python deps OK`. If `import` fails, re-run the pip install. `pypdfium2` is used by the slide-qc render path; if it's missing here, slide-qc would auto-install it mid-build (which works but surprises the user with a pip log during finalize) — pin it at install time instead. `skimage` (scikit-image) is used by the sketch-path regression-check harness (`tests/capture_baseline.py` + `tests/regression_check.py`); it adds ~30 MB to the install but is the load-bearing dep for the "no silent regressions" quality guarantee.

## Step 1.5 — Playwright Chromium binary

`pip install` brings the Playwright Python package, but the headless Chromium binary it drives is downloaded separately. One-time, run:

```powershell
py -3 -m playwright install chromium
```

Downloads ~170 MB. Required for `scripts/render_html.py` (the sketch-path render path that turns worker-authored HTML into the 1280×720 PNG the operator picks from). Skip only if you have no plans to use the sketch path; the legacy python-pptx pipeline does not depend on it.

Verify:

```powershell
py -3 -c "from playwright.sync_api import sync_playwright; sync_playwright().__enter__().chromium.launch(headless=True).close(); print('playwright + chromium OK')"
```

Expected: `playwright + chromium OK`. If you see `BrowserType.launch: Executable doesn't exist`, re-run the `playwright install chromium` step.

## Step 2 — LibreOffice headless

Download from https://www.libreoffice.org/download and install. Default install locations Slide Lab finds automatically:

| OS | Default location |
|---|---|
| Windows | `C:\Program Files\LibreOffice\program\soffice.exe` |
| macOS | `/Applications/LibreOffice.app/Contents/MacOS/soffice` |
| Linux | `/usr/bin/soffice` (or your package manager's path; the `libreoffice` command also works) |

> **macOS note:** LibreOffice installs to `/Applications` but is **not** added to your PATH. Slide Lab checks that default location automatically, so no PATH change is needed. If you moved it, set `SLIDE_LAB_SOFFICE` to the full `soffice` path.

Verify (Windows):

```powershell
& "C:\Program Files\LibreOffice\program\soffice.exe" --version
```

macOS / Linux:

```bash
soffice --version   # or: /Applications/LibreOffice.app/Contents/MacOS/soffice --version
```

Expected: a version string like `LibreOffice 24.x.x ...`. The headless render path is invoked by `slide-qc/scripts/render_slides.py`, which Slide Lab calls via subprocess.

## Step 4 — Skill location

This skill must live at:

```
C:\Users\<you>\.claude\skills\slide-builder\
```

Verify:

```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\build_deck.py" --help
```

Expected: argparse help text starting with `usage: build_deck.py`. Any `ImportError` means a Python dep above is missing.

## Step 5 — Sibling skill: slide-qc

Slide Lab calls `slide-qc/scripts/render_slides.py` for PPTX → PNG rendering. Make sure `slide-qc` is installed at the sibling path:

```
C:\Users\<you>\.claude\skills\slide-qc\
```

Verify:

```powershell
Test-Path "$env:USERPROFILE\.claude\skills\slide-qc\scripts\render_slides.py"
```

Expected: `True`.

## Step 6 — Worker agent (Stage-2 fanout)

Stage 2 of the build pipeline dispatches **one `slide-builder-worker` agent per slide in parallel**. That subagent definition must exist at:

```
%USERPROFILE%\.claude\agents\slide-builder-worker.md
```

The skill ships the source-of-truth copy at `slide-builder/agents/slide-builder-worker.md`. Install it with:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\agents" | Out-Null
Copy-Item "$env:USERPROFILE\.claude\skills\slide-builder\agents\slide-builder-worker.md" `
          "$env:USERPROFILE\.claude\agents\slide-builder-worker.md" -Force
```

Verify (existence AND correct content — a stale copy at this path will pass `Test-Path` and silently break Stage 2):

```powershell
$wp = "$env:USERPROFILE\.claude\agents\slide-builder-worker.md"
(Test-Path $wp) `
  -and (Select-String -Path $wp -Pattern "option_A\.py" -Quiet) `
  -and (Select-String -Path $wp -Pattern "_context\.md" -Quiet) `
  -and (Select-String -Path $wp -Pattern "_context_ack\.txt" -Quiet) `
  -and (Select-String -Path $wp -Pattern "PATTERN: sketch" -Quiet)
```

Expected: `True`. The four greps prove the installed file is the current worker contract:
  - `option_A.py` — writes `option_A.py` (plus `option_B.py` / `option_C.py` only when the option count > 1) — rules out v1-era workers that wrote 4 options or used `sys.argv` paths
  - `_context.md` — knows to read the per-slide context bundle BEFORE the prompt (Gate C.1, added)
  - `_context_ack.txt` — knows to write the soft-enforcement acknowledgment (Gap 3, added)
  - `PATTERN: sketch` — knows the sketch-path branch (HTML output when dispatched with `PATTERN: sketch`). A worker pre-dating this branch silently falls back to python-pptx output even when the sketch path is enabled

**Without this file (or with the wrong content), Stage 2 dispatch silently does nothing** — your build will reach `finalize_deck.py` with zero option scripts and produce nothing useful. A stale worker that passes only the first grep will silently produce builds without context awareness, with yellow ⚠ chips on every slide in REVIEW.html.

## Step 7 — Translator agent (the sketch path Stage-3.5 dispatch)

When the sketch path is enabled (`--pattern sketch` or `settings.json::default_pattern: "auto"|"sketch"`), Stage 3.5 dispatches **one `slide-builder-translator` agent per picked sketch-path slide**. That subagent converts the picked `option_X.html` to a native `option_X_native.py` with editable text frames. Its definition must exist at:

```
%USERPROFILE%\.claude\agents\slide-builder-translator.md
```

The skill ships the source-of-truth copy at `slide-builder/agents/slide-builder-translator.md`. Install it with:

```powershell
Copy-Item "$env:USERPROFILE\.claude\skills\slide-builder\agents\slide-builder-translator.md" `
          "$env:USERPROFILE\.claude\agents\slide-builder-translator.md" -Force
```

Verify (existence AND content — a stale copy will silently produce non-editable or visually-broken sketch-path output):

```powershell
$tp = "$env:USERPROFILE\.claude\agents\slide-builder-translator.md"
(Test-Path $tp) `
  -and (Select-String -Path $tp -Pattern "data-template-field" -Quiet) `
  -and (Select-String -Path $tp -Pattern "data-shape-id" -Quiet) `
  -and (Select-String -Path $tp -Pattern "__template_fields__" -Quiet) `
  -and (Select-String -Path $tp -Pattern "EDITABILITY_VIOLATION" -Quiet)
```

Expected: `True`. The four greps prove the installed translator understands the sketch-path contract:
  - `data-template-field` — extracts chrome (title/subtitle/footer/page_number) from HTML attributes per Spec 4 §5
  - `data-shape-id` — translates body-zone elements to native python-pptx shapes per Spec 4 §6
  - `__template_fields__` — emits the structured comment header `finalize_deck.py` reads for placeholder population
  - `EDITABILITY_VIOLATION` — implements the R4.7 Critical editability self-check

**Without this file**, sketch-path dispatch (Stage 3.5) emits `TRANSLATOR_BLOCKED` on every picked slide and finalize halts. Legacy / direct-path builds (the shipped default) are unaffected and continue working without this file.

## Verification step

One command exercises every install step. `install OK` only if all subsystems pass:

```powershell
$skill        = "$env:USERPROFILE\.claude\skills\slide-builder"
$soffice_ok   = (Test-Path "C:\Program Files\LibreOffice\program\soffice.exe")
$qc_ok        = (Test-Path "$env:USERPROFILE\.claude\skills\slide-qc\scripts\render_slides.py")
$worker_path  = "$env:USERPROFILE\.claude\agents\slide-builder-worker.md"
$worker_ok    = (Test-Path $worker_path) `
  -and (Select-String -Path $worker_path -Pattern "option_A\.py" -Quiet) `
  -and (Select-String -Path $worker_path -Pattern "_context\.md" -Quiet) `
  -and (Select-String -Path $worker_path -Pattern "_context_ack\.txt" -Quiet) `
  -and (Select-String -Path $worker_path -Pattern "PATTERN: sketch" -Quiet)
$translator_path = "$env:USERPROFILE\.claude\agents\slide-builder-translator.md"
$translator_ok   = (Test-Path $translator_path) `
  -and (Select-String -Path $translator_path -Pattern "data-template-field" -Quiet) `
  -and (Select-String -Path $translator_path -Pattern "data-shape-id" -Quiet) `
  -and (Select-String -Path $translator_path -Pattern "__template_fields__" -Quiet) `
  -and (Select-String -Path $translator_path -Pattern "EDITABILITY_VIOLATION" -Quiet)
$build_ok     = $false
try { py -3 "$skill\scripts\build_deck.py" --help *>$null; $build_ok = ($LASTEXITCODE -eq 0) } catch { $build_ok = $false }
if ($soffice_ok -and $qc_ok -and $worker_ok -and $translator_ok -and $build_ok) {
    "install OK"
} else {
    "install INCOMPLETE - soffice=$soffice_ok  slide-qc=$qc_ok  worker-agent=$worker_ok  translator-agent=$translator_ok  build_deck-help=$build_ok"
}
```

Expected: `install OK`. Any other line lists which subsystem(s) failed — re-check that step before proceeding to [examples/RUN.md](examples/RUN.md).
