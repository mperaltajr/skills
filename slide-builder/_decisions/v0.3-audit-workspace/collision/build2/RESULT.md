# Slide Lab v2 deck — finalize result

Generated: 2026-05-28T23:37:50

Out: `slide-builder\_decisions\v0.3-audit-workspace\collision\build2`
Template: `C:\Users\m.a.peralta\OneDrive - Accenture\Library\FedEx\OTC\OTC Opportunity.pptx`
Mermaid theme: `C:\Users\m.a.peralta\.claude\skills\.claude\worktrees\agent-abaae9e70ed8f6544\slide-builder\theme\mermaid-otc.json`

## Counts

- Total options: **3**
- Native      : 1
- Mermaid     : 0
- Rejected    : 0
- Missing     : 2
- Built       : **1 / 3**
- Themed      : **1 / 3**
- Rendered    : **1 / 3**

## Per-option status

| Slide | Option | Class | Built | Themed | Rendered | Shapes | Subs | Error/Reason |
|-------|--------|-------|-------|--------|----------|--------|------|--------------|
|  1 | A | native | ok | ok | ok | 2 | 0 |  |
|  1 | B | missing | FAIL | - | - | 0 | 0 | worker did not produce option script |
|  1 | C | missing | FAIL | - | - | 0 | 0 | worker did not produce option script |

## Outputs

- **Themed PPTX**: `<out>/slide_NN/option_X.pptx`
- **PNG thumbnails**: `<out>/slide_NN/option_X.png`
- **Mermaid PNG (fallback only)**: `<out>/slide_NN/option_X-mermaid.png`
- **QC self-check**: `<out>/slide_NN/option_X.qc.json`
- **Raw pre-theme PPTX**: `<out>/slide_NN/_raw/option_X.pptx`

## Failures + rejections

- **slide 01 option B** [MISSING]: worker did not produce option script — re-dispatch the worker if a fuller deck is wanted
- **slide 01 option C** [MISSING]: worker did not produce option script — re-dispatch the worker if a fuller deck is wanted
