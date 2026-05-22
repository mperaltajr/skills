---
name: troubleshooting
description: "Symptom→cause→fix reference for Slide Lab pipeline problems. Organized by where the problem appears: Phase A preview, Phase B build, final PPTX."
---

# Slide Lab Troubleshooting

## Setup and Dependency Problems

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'pptx'` | python-pptx not installed in the active Python environment | Run `py -3 -m pip install python-pptx lxml openpyxl` |
| `ModuleNotFoundError: No module named 'playwright'` | Playwright not installed | Run `py -3 -m pip install playwright` then `py -3 -m playwright install chromium` |
| `py -3` resolves to wrong Python version (e.g. 2.7) | Windows PATH has an older Python before py -3 | Run `py -3 --version` to confirm. If wrong: use `python3` or the full path to the correct interpreter (e.g. `C:\Python312\python.exe`) |
| `ModuleNotFoundError: No module named 'openpyxl'` | openpyxl not installed; xlsx companion will be silently skipped | Run `py -3 -m pip install openpyxl`. The PPTX build still works without it; only xlsx generation is affected. |
| Playwright launch fails with `BrowserType.launch: Executable doesn't exist` | Chromium not installed after Playwright package install | Run `py -3 -m playwright install chromium` |
| Post-build QA step fails with LibreOffice / `soffice` error | LibreOffice is not installed or `soffice` is not on PATH | Install LibreOffice and ensure `soffice` is accessible from PATH, or skip LibreOffice-dependent QA steps and review the PPTX manually in PowerPoint |
| Process icons appear in flat brand color with no tint (untinted icons) | `PIL` / `Pillow` is not installed — `build_slide.py` falls back to un-tinted PNGs when `PIL` import fails | Run `py -3 -m pip install Pillow`. After install, rebuild the slide — no mockup changes needed. |

## Phase A Preview Problems

| Symptom | Cause | Fix |
|---------|-------|-----|
| Chart shows as broken image icon (outside `data-chart`) | `src="_session/..."` path resolves to `_session/_session/...` because the HTML file is already in `_session/` | Embed the chart PNG as a base64 data URI instead of a file path (see Issue 5 in `known-issues-and-improvements.md`) |
| Chart image appears broken inside a `data-chart` container | This is expected — `data-chart` containers require relative filenames (not base64) for Playwright. The preview breaks; the PPTX output is correct. | No fix needed — the PPTX will render correctly. If you need to verify the chart, open the built PPTX. |
| `_session/_session/` double-path in image src | Relative path used inside a `_session/`-relative src | Remove the `_session/` prefix — use a relative filename only (e.g. `chart-slide-1.png`) inside `data-chart` containers |
| Bottom third of slide is empty in Phase A preview | Content placed with flex flow instead of `position:absolute; bottom:52px` for bottom-anchored elements | Apply Footer Clearance Rule 6: `position:absolute; bottom:52px` for any bottom-anchored element |
| All three mockup options look identical | Options A/B/C share the same outer wrapper or the `data-option` attribute is missing | Each option root div must have a distinct `data-option` value (A, B, C) and structurally different layouts |
| Slide canvas appears cut off or wider than expected | Canvas div does not use the 1280×720px spec | Set canvas: `width:1280px; height:720px; position:relative; overflow:hidden` |
| Slide looks square / squished / 4:3 format | Canvas was set to 1024×768px — the obsolete pre-2013 "Standard" size | Regenerate with `width:1280px; height:720px`. All modern PowerPoint decks are 16:9. 1024×768 is never correct. |

## Phase B Build Problems

| Symptom | Cause | Fix |
|---------|-------|-----|
| Fonts are wrong in PPTX (wrong typeface) | `--print-theme` was not run or `theme.json` is stale | Re-run `build_slide.py --print-theme <template.pptx>` and overwrite `_session/theme.json` |
| Colors are wrong in PPTX | Template color slots differ from assumed positions (e.g. brand color is in `dk2` not `accent1`) | Read the `theme.json` output and cross-reference with the client template to confirm which slot carries the brand color |
| Chart did not appear in PPTX | `data-chart-data` attribute missing — xlsx generation silently skipped, chart screenshot not taken | Add `data-chart-data` JSON attribute to the chart wrapper div; `data-chart="true"` triggers the screenshot |
| Text appears below the footer bar | Bottom-anchored element used flex flow instead of `position:absolute; bottom:52px` | Apply Rule 6 (Footer Clearance): `position:absolute; bottom:52px` |
| Floating title shape appears above slide content | The slide layout has a title placeholder that wasn't suppressed | Add `data-layout-index` attribute and use layout-aware mode, or clear the title placeholder in the mockup |
| Phase B refuses to build — asks to re-run Phase A | `<!-- PHASE-A-PRECHECK: PASS -->` comment is absent from mockups.html | Re-run Phase A pre-check on the mockup and add the machine-readable comment block |
| PPTX file fails to open or shows schema error | build_slide.py wrote an invalid XML relationship during the build | Check the build log for "WARNING: relationship" lines; rebuild from the template using a fresh `--target` path |

## Unsupported CSS — Silently Broken in PPTX

These properties work in HTML preview but produce wrong output in the PPTX. `build_slide.py` warns on some at pre-build time; others must be caught at authoring.

| Symptom in PPTX | CSS used | Fix |
|---|---|---|
| Circle renders as a square | `border-radius:50%` on a `<div>` | Replace with `<svg><circle cx="..." cy="..." r="..."/></svg>` |
| Text lands at wrong vertical position | `transform:translateY(-50%)` | Replace with explicit `position:absolute; top:Npx` |
| Element renders behind others despite high z-index | CSS `z-index` | Move element later in the DOM — PPTX layer order = DOM insertion order |
| Element completely missing after removing `data-placeholder` | Element had no `position:absolute` coords once placeholder attribute was removed | Add explicit `position:absolute; top:Npx; left:Npx; width:Npx; height:Npx` |
| Text routed into wrong position / invisible | `data-placeholder="title"` on non-title element (quote, body text, subtitle) | Remove attribute; use `position:absolute` coords instead |
| Background renders as white / transparent | `background:linear-gradient(...)` — gradients are in `backgroundImage`, not `backgroundColor`. Builder now reads `backgroundImage` and uses the first stop color. If background is still wrong, replace with a solid hex `background:#XXXXXX` | Use solid hex colors; gradients are approximated to their first stop |
| Element missing or clipped unexpectedly | `inset:0` shorthand — Playwright may not resolve `inset` to `top/left/right/bottom` computed values in all versions | Replace with explicit `top:0; left:0; right:0; bottom:0` or `width:1280px; height:720px` |
| Multi-column layout renders blank | `display:flex` children with `flex:1` and no `position:absolute` — the builder's geometry extraction requires explicit pixel coordinates | Convert flex columns to `position:absolute` with explicit `left`, `top`, `width`, `height` values |

## Final PPTX Problems

| Symptom | Cause | Fix |
|---------|-------|-----|
| Bullet dots are missing | CSS `::before` pseudo-element used for bullets — not captured by DOM walker | Replace `::before` bullets with `<span class="bullet">•</span>` inline in the HTML |
| Text boxes overlap in PPTX | Sibling `<span>` elements inside a `<li>` become separate text boxes | Move inline span content into the parent element's text, not as siblings |
| Dark background bleeds past the slide boundary | Background div is positioned outside the 1280×720 canvas | Constrain all background elements inside the canvas div with `overflow:hidden` |
| Text is smaller than expected in PPTX | px→pt conversion: browser renders at 96dpi, PPTX at 72dpi. 16px = 12pt, not 16pt | Use the canonical type scale: title = 28pt, sub-heading = 16pt, body = 12pt, hero = 30–45pt |

## Canonical Type Scale

Source of truth: `slide-builder/SKILL.md` Hard Constraint #10. Do not maintain a parallel list — if this table disagrees with SKILL.md, trust SKILL.md.

| Role | HTML (px) | PPTX (pt) |
|------|-----------|-----------|
| Slide title / Governing thought | ~37px | 28pt |
| Sub-heading / Section label | ~21px | 16pt |
| Body text | 16px | 12pt |
| Supporting detail / Caption / Source | 14px | 10.5pt (minimum) |
| Hero numbers (stat callouts) | 40–60px | 30–45pt |

Never use a px value not in this table. Never use fractional px values. Hero numbers are the only exception to the strict list — pick one size per deck and use it consistently.
