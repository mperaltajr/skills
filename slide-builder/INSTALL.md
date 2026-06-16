# Install — Slide Lab

Tested on Windows 11. Linux + macOS should work; the LibreOffice command differs.

## Prerequisites

| Component | Version | Why |
|---|---|---|
| Python | **3.10+** | Type hints and f-string features used throughout |
| Node.js | 18+ | Required by Mermaid CLI |
| LibreOffice | any recent | Headless PPTX → PNG render path (via slide-qc) |
| PowerPoint | 2019+ (optional) | Pixel-perfect QC pass; LibreOffice render is the default |

## Step 1 — Python deps

```powershell
py -3 -m pip install -r requirements.txt
```

Verify:

```powershell
py -3 -c "import pptx, PIL, yaml, lxml, pydantic, pypdfium2, skimage; print('python deps OK')"
```

Expected: `python deps OK`. If `import` fails, re-run the pip install. `pypdfium2` is used by the slide-qc render path; if it's missing here, slide-qc would auto-install it mid-build (which works but surprises the user with a pip log during finalize) — pin it at install time instead. `skimage` (scikit-image) is used by the Pattern B regression-check harness (`tests/capture_baseline.py` + `tests/regression_check.py`); it adds ~30 MB to the install but is the load-bearing dep for the "no silent regressions" quality guarantee.

## Step 2 — Mermaid CLI (pinned)

```powershell
npm install -g @mermaid-js/mermaid-cli@11.4.0
```

Verify:

```powershell
mmdc --version
```

Expected: `11.4.0`. If a different major version is installed, fallback diagram rendering may differ from what the v0 reference was tested against. Pin to `11.4.0`.

If verify still shows the wrong version after re-running the install, your global npm cache is holding the old binary. Uninstall, then reinstall:

```powershell
npm uninstall -g @mermaid-js/mermaid-cli
npm install -g @mermaid-js/mermaid-cli@11.4.0
mmdc --version   # should now show 11.4.0
```

## Step 3 — LibreOffice headless

Download from https://www.libreoffice.org/download and install. The default Windows install path is `C:\Program Files\LibreOffice\program\soffice.exe`.

Verify:

```powershell
& "C:\Program Files\LibreOffice\program\soffice.exe" --version
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
  -and (Select-String -Path $wp -Pattern "_context_ack\.txt" -Quiet)
```

Expected: `True`. The three greps prove the installed file is the current worker contract:
  - `option_A.py` — writes `option_A.py` / `option_B.py` / `option_C.py` (rules out v1-era workers that wrote 4 options or used `sys.argv` paths)
  - `_context.md` — knows to read the per-slide context bundle BEFORE the prompt (Gate C.1, added 2026-06-08)
  - `_context_ack.txt` — knows to write the soft-enforcement acknowledgment (Gap 3, added 2026-06-08)

**Without this file (or with the wrong content), Stage 2 dispatch silently does nothing** — your build will reach `finalize_deck.py` with zero option scripts and produce nothing useful. A stale worker that passes only the first grep will silently produce builds without context awareness, with yellow ⚠ chips on every slide in REVIEW.html.

## Verification step

One command exercises every install step. `install OK` only if all five subsystems pass:

```powershell
$skill        = "$env:USERPROFILE\.claude\skills\slide-builder"
$mmdc_ok      = $false
try { $mmdc_ok = ((mmdc --version 2>$null) -match "11\.4") } catch {}
$soffice_ok   = (Test-Path "C:\Program Files\LibreOffice\program\soffice.exe")
$qc_ok        = (Test-Path "$env:USERPROFILE\.claude\skills\slide-qc\scripts\render_slides.py")
$worker_path  = "$env:USERPROFILE\.claude\agents\slide-builder-worker.md"
$worker_ok    = (Test-Path $worker_path) `
  -and (Select-String -Path $worker_path -Pattern "option_A\.py" -Quiet) `
  -and (Select-String -Path $worker_path -Pattern "_context\.md" -Quiet) `
  -and (Select-String -Path $worker_path -Pattern "_context_ack\.txt" -Quiet)
$build_ok     = $false
try { py -3 "$skill\scripts\build_deck.py" --help *>$null; $build_ok = ($LASTEXITCODE -eq 0) } catch { $build_ok = $false }
if ($mmdc_ok -and $soffice_ok -and $qc_ok -and $worker_ok -and $build_ok) {
    "install OK"
} else {
    "install INCOMPLETE - mmdc11.4=$mmdc_ok  soffice=$soffice_ok  slide-qc=$qc_ok  worker-agent=$worker_ok  build_deck-help=$build_ok"
}
```

Expected: `install OK`. Any other line lists which subsystem(s) failed — re-check that step before proceeding to [examples/RUN.md](examples/RUN.md).
