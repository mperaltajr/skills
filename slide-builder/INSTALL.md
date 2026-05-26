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

(After Phase 8 of `_decisions/cleanup-plan-master-2026-05-26.md`, the folder will be renamed to `slide-builder\`. Until that lands, the `-simple` suffix is the current path.)

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

## Verification step

End-to-end smoke that touches every component:

```powershell
$skill = "$env:USERPROFILE\.claude\skills\slide-builder"
py -3 -c "import sys; sys.path.insert(0, r'$skill'); from twins.client_theme import load_brand_sidecar; from twins.composer import _clear_existing_slides; from twins.helpers import new_slide; import sys; sys.path.insert(0, r'$skill\scripts'); import icon_helper; print('install OK')"
```

Expected: `install OK`. Any traceback means one of Steps 1–5 was incomplete — re-check that step before proceeding to [QUICKSTART.md](QUICKSTART.md).
