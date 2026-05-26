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
py -3 -c "import pptx, PIL, yaml, lxml, pydantic; print('python deps OK')"
```

Expected: `python deps OK`. If `import` fails, re-run the pip install.

## Step 2 — Mermaid CLI (pinned)

```powershell
npm install -g @mermaid-js/mermaid-cli@11.4.0
```

Verify:

```powershell
mmdc --version
```

Expected: `11.4.0`. If a different major version is installed, fallback diagram rendering may differ from what the v0 reference was tested against. Pin to `11.4.0`.

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

Verify:

```powershell
Test-Path "$env:USERPROFILE\.claude\agents\slide-builder-worker.md"
```

Expected: `True`. **Without this file, Stage 2 dispatch silently does nothing** — your build will reach `finalize_deck.py` with zero option scripts and produce nothing useful.

## Verification step

One command exercises every install step. `install OK` only if all five subsystems pass:

```powershell
$skill        = "$env:USERPROFILE\.claude\skills\slide-builder"
$mmdc_ok      = $false
try { $mmdc_ok = ((mmdc --version 2>$null) -match "11\.4") } catch {}
$soffice_ok   = (Test-Path "C:\Program Files\LibreOffice\program\soffice.exe")
$qc_ok        = (Test-Path "$env:USERPROFILE\.claude\skills\slide-qc\scripts\render_slides.py")
$worker_ok    = (Test-Path "$env:USERPROFILE\.claude\agents\slide-builder-worker.md")
$build_ok     = $false
try { py -3 "$skill\scripts\build_deck.py" --help *>$null; $build_ok = ($LASTEXITCODE -eq 0) } catch { $build_ok = $false }
if ($mmdc_ok -and $soffice_ok -and $qc_ok -and $worker_ok -and $build_ok) {
    "install OK"
} else {
    "install INCOMPLETE - mmdc11.4=$mmdc_ok  soffice=$soffice_ok  slide-qc=$qc_ok  worker-agent=$worker_ok  build_deck-help=$build_ok"
}
```

Expected: `install OK`. Any other line lists which subsystem(s) failed — re-check that step before proceeding to [examples/RUN.md](examples/RUN.md).
