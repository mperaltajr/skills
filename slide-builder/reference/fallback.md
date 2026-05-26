# Fallback path — HTML→PNG via Mermaid

The fallback for slides whose brief implies a curved-container diagram that native python-pptx cannot render cleanly. Python-pptx can position shapes with `(x, y)` precision but cannot shape-fit text to ovals — text inside circles, ellipses, and free-form containers wraps badly across the curve. Mermaid (an HTML/SVG renderer) does shape-fit text correctly because it's rendering through the browser layout engine.

**Tradeoff acknowledged:** fallback slides ship as an embedded PNG. They are not editable in PowerPoint after the deck is built. The user picks fallback-rendered slides knowing they sacrifice editability for visual correctness.

---

## When the fallback fires

Per `layouts.md § Fallback path`, the agent emits the fallback marker and routes to Mermaid for any slide whose brief implies:

- Hub-and-spoke
- Porter's Five Forces
- Ecosystem map
- Free-form network

Diagrams that the native primitives can carry cleanly (org chart, swimlane, decision tree) do **not** route here — those are layout patterns #10, #11, #12 in `layouts.md`. Native first; fallback only for the curved-container failure cases above.

**Not supported in v0** (deferred to v0.1 — see § "What is not in this fallback" below):

- Fishbone / cause-and-effect (Ishikawa) — Mermaid has no native spine syntax; auto-layout produces a left-justified tree, not a fishbone.
- Concentric rings — Mermaid has no analogue. (`mindmap` was considered and rejected: it's hierarchical, not concentric.)

For these two cases the agent emits `# SKELETON_REJECTED: no Mermaid analogue — <fishbone|concentric-rings>` and stops. The rejection surfaces in REVIEW.html and the user resolves manually (SmartArt, manual build, or wait for the v0.1 Playwright escalation).

---

## Agent contract — what gets written

For a slide that triggers the fallback, the agent writes **both** of these files for each option (A, B, C):

```
{{OUTPUT_DIR}}\option_A.py    # SKELETON_REJECTED marker; tells finalize_deck.py to use the .mmd
{{OUTPUT_DIR}}\option_A.mmd   # Mermaid spec for option A
{{OUTPUT_DIR}}\option_B.py    # SKELETON_REJECTED marker
{{OUTPUT_DIR}}\option_B.mmd   # Mermaid spec for option B
{{OUTPUT_DIR}}\option_C.py    # SKELETON_REJECTED marker
{{OUTPUT_DIR}}\option_C.mmd   # Mermaid spec for option C
```

The three `.mmd` specs differ on **variant choices the agent has autonomy over**:
- Diagram orientation (`graph LR`, `graph TD`, `graph TB`)
- Node shape (rectangles, rounded rectangles, stadium, circles)
- Connector style (solid, thick, dashed)
- Color emphasis (which node carries the brand-accent vs. brand-primary fills)

Cosmetic variants are appropriate here — the underlying diagram structure is fixed by the brief (a hub-spoke is a hub-spoke; you don't have variant choice over the topology). The three options give the user aesthetic choice, not structural choice. This is the only place in v2 where the three sibling options are intentionally close to each other.

### The `.py` companion — hard discriminator token

The `.py` file for each option exists with a **hard discriminator token** on line 1 so `finalize_deck.py`'s file scan can branch deterministically without substring guessing:

```python
# FALLBACK_MERMAID: curved-container diagram, see option_A.mmd
# Slide N option A — Mermaid fallback
import sys
sys.exit(0)
```

The token is exactly `# FALLBACK_MERMAID:`. Not `# SKELETON_REJECTED:` (which is reserved for brief/pattern disagreement). Not substring-matched on words like "Mermaid" or "fallback". Either the token matches the prefix exactly **or** the sibling `option_X.mmd` exists and is non-empty — finalize_deck.py uses **both** signals to branch:

```
discriminator = (option_X.py line 1 starts with "# FALLBACK_MERMAID:")
                OR
                (option_X.mmd exists in OUTPUT_DIR AND is non-empty)
```

This is belt-and-braces. The agent should always write both signals (token on line 1 of the .py AND a .mmd file). If only one signal is present, finalize_deck.py logs a warning and uses the present signal; if neither is present, the option is treated as a normal native build (which will then fail because line 1 doesn't start with `# `).

On detection, finalize_deck.py for that option:

1. Read `option_X.mmd`
2. Run `scripts/render_mermaid.py` with the brand theme override
3. Get `option_X-mermaid.png` (sized to fit the body zone — see § "Rendering" for dimensions)
4. Build the slide PPTX: title block + footer chrome from `twins/helpers.py`, with the rendered PNG embedded in the body zone at the dimensions the renderer produced

---

## Mermaid diagram types per pattern (v0 supported set)

Mermaid covers four curved-container failure cases via the `flowchart` family. The agent adapts the worked example matching the brief.

| Failure case | Mermaid type | Notes |
|---|---|---|
| **Hub-and-spoke** | `flowchart TD` or `flowchart LR` | Hub at top/left, spokes radiating. Use `(( ))` for circular nodes if hub is genuinely a circle. |
| **Porter's Five Forces** | `flowchart TD` with arrows-to-center | Center node = industry rivalry; 4 surrounding nodes = supplier power, buyer power, threat of substitutes, threat of new entrants. Arrows all pointing to center. |
| **Ecosystem map** | `flowchart TB` with subgraphs | Group nodes by ecosystem tier (e.g., "Internal," "Partners," "External"). Connections cross subgraph boundaries. |
| **Free-form network** | `flowchart` (any direction) | Use whatever layout Mermaid's auto-layout produces. Manual `linkStyle` if specific connections need emphasis. |

**Worked examples** at `reference/fallback-examples/`:
- `hub-spoke.mmd`
- `porters-five-forces.mmd`

The agent reads the example matching the brief's diagram type and adapts it to the brief's content. Preserve the `classDef` blocks (those carry brand color emphasis); change topology, node labels, and orientation as the brief requires.

---

## Brand theme override — per-client generation

Mermaid's default theme uses generic blue + gray colors. To match the client template, the renderer applies a config JSON that overrides Mermaid's `themeVariables`. **Every deck gets its own theme file** generated at prep time by `build_deck.py` from the client's `brand.yml` sidecar — no global default.

### File paths

```
Per-client at prep time:  theme/mermaid-<client_slug>.json
```

`<client_slug>` is the lowercase, hyphen-separated client name (e.g., `mermaid-acme.json`, `mermaid-fedex.json`). `build_deck.py` derives the slug from the client template's filename or the `client_name` field in the brief front-matter. There is **no generic fallback file** — Stage-1 sanity check halts the build if the client template is not registered (no `<template-stem>.brand.yml` next to the PPTX). See `_decisions/cleanup-plan-master-2026-05-26.md` Phase 0 amendment A.

### brand.yml → mermaid themeVariables mapping (canonical)

The client's `<template-stem>.brand.yml` sidecar (human-authored once via `register_template.py`, verified by `<template-stem>.theme.json` SHA stamp) is the single source of truth for brand colors and fonts. `build_deck.py` calls `twins.client_theme.load_brand_sidecar()` to read it.

`brand.yml` shape:

```yaml
primary_hex:   "4D148C"     # brand primary (no leading #; case-insensitive)
accent_hex:    "FF6600"     # brand accent
font_heading:  "FedEx Sans Bold"
font_body:     "FedEx Sans Regular"
```

`build_deck.py::_compute_theme_variables(brand)` writes the per-deck Mermaid override. Mapping (canonical, from `build_deck.py:460`):

| themeVariable (Mermaid)   | brand.yml source | Notes |
|---|---|---|
| `primaryColor`            | `primary_hex` | Hex prefixed with `#` |
| `primaryBorderColor`      | `primary_hex` | Same as primaryColor; nodes have matching border |
| `lineColor`               | `primary_hex` | Connector lines in brand primary |
| `nodeBorder`              | `primary_hex` | Default node border |
| `defaultLinkColor`        | `primary_hex` | Link color when not overridden |
| `secondaryColor`          | `accent_hex` | Used by classDef `brandAccent` |
| `secondaryBorderColor`    | `accent_hex` | Matching border on accent nodes |
| `primaryTextColor`        | `#FFFFFF` (fixed) | White text on dark primary fill |
| `secondaryTextColor`      | `#FFFFFF` (fixed) | White text on accent fill |
| `tertiaryColor`           | `#F2F2F2` (fixed neutral) | Light gray neutral surfaces |
| `tertiaryTextColor`       | `#333333` (fixed neutral) | Dark text on light gray |
| `tertiaryBorderColor`     | `#E3E3E3` (fixed neutral) | Subtle border on neutral surfaces |
| `background`              | `#FFFFFF` (fixed) | Slide canvas background is always white for fallback |
| `mainBkg`                 | `#FAFAFA` (fixed) | **Slight off-white** so unstyled nodes are visible against pure-white background. NOT `#FFFFFF` — white-on-white nodes vanish. |
| `secondBkg`               | `#F2F2F2` (fixed neutral) | Subgraph cluster background |
| `clusterBkg`              | `#FAFAFA` (fixed) | Cluster (subgraph) fill |
| `clusterBorder`           | `#E3E3E3` (fixed neutral) | Cluster border |
| `titleColor`              | `#333333` (fixed neutral) | Title text |
| `edgeLabelBackground`     | `#FFFFFF` (fixed) | Edge label bg so labels read on any background |
| `textColor`               | `#333333` (fixed neutral) | Default text color |
| `fontFamily`              | `font_body` (or `font_heading` if `font_body` blank) + fallback stack | **Per-client** — DO NOT hardcode `Helvetica`. Example: `"FedEx Sans Regular", Helvetica, Arial, sans-serif`. The fallback stack matters because Mermaid renders in headless Chromium; if the corporate font isn't installed in the build environment, the fallback applies. |
| `fontSize`                | `16px` (fixed) | Sized for the body zone at 1240×540 render dimensions |

`build_deck.py::validate_theme()` runs belt-and-braces checks after generating the override: `primary != accent`, plausible saturation and luminance, hue range sanity. The build halts loudly on theme-yml authoring errors.

**Missing brand.yml.** If the client template is not registered (no `<template-stem>.brand.yml`), `twins.client_theme.load_brand_sidecar()` raises `BrandSidecarMissing`. `build_deck.py` halts at Stage-1 before any agent dispatch. Register the template via `register_template.py` first.

**Missing `font_body` / `font_heading`.** If both are blank in brand.yml, the override uses Mermaid's default font stack. `build_deck.py` logs the fallback so the build is auditable.

---

## Rendering — `scripts/render_mermaid.py`

The renderer is a thin Python wrapper around the Mermaid CLI (`mmdc`).

**Prerequisites:**

```powershell
# One-time install (Node.js required):
npm install -g @mermaid-js/mermaid-cli@11.4.0

# Verify the installed version matches the tested version:
mmdc --version
# Expected: 11.4.0 (the version this script was tested against)
```

If `mmdc --version` returns a different major version, the rendered output may differ from what artifact 5 was tested against. Pin to `11.4.0` for v0 reproducibility; revisit in v0.1 if a newer version offers material improvements.

**Render dimensions: body zone, not full canvas.**

The fallback PNG must fit the slide's **body zone** (the area between the title block at the top and the footer at the bottom), not the full 1280×720 canvas. Title block occupies y≈0–110; footer occupies y≈660–720. Body zone is 1280×550. The renderer defaults to **1240×540** (with 20px horizontal padding inside the body zone) so the PNG embeds cleanly without scaling.

| Dimension | Value | Reason |
|---|---|---|
| Render width | 1240 px | 1280 canvas − 20 px padding each side |
| Render height | 540 px | Body zone height (y≈110 to y≈650) |
| Background | `white` | Matches slide canvas; renderer can also emit `transparent` for slides with a non-white body |

**Invocation:**

```powershell
py -3 "$env:USERPROFILE\.claude\skills\slide-builder\scripts\render_mermaid.py" `
    --input  <path-to-option_X.mmd> `
    --output <path-to-option_X-mermaid.png> `
    --theme  "$env:USERPROFILE\.claude\skills\slide-builder\theme\mermaid-<client_slug>.json" `
    --width  1240 `
    --height 540
```

The `--theme` argument is **required** and should point to the **per-deck override file** generated by `build_deck.py` from the client `brand.yml`. Stage-1 sanity check requires a registered `brand.yml`; there is no generic fallback. Register the client template before building.

**Behavior:**

1. Validates input file exists and is non-empty.
2. Validates theme file exists.
3. Invokes `mmdc` subprocess with the inputs.
4. Verifies output PNG was created and has nonzero size.
5. Returns 0 on success, nonzero on failure with diagnostic message.

**Failure modes:**

- `mmdc` not installed → exits with install instructions and the pinned version.
- Mermaid spec has a syntax error → exits with `mmdc`'s error message verbatim.
- Output file not produced → exits with diagnostic asking for `--verbose` rerun.

---

## Integration with `finalize_deck.py`

`finalize_deck.py` (built in artifact #6) handles the per-option dispatch:

```python
# Pseudocode for the finalize-time fallback branch
import sys, subprocess

def finalize_option(slide_n, option_letter, output_dir, client_theme_path):
    py_file  = output_dir / f"option_{option_letter}.py"
    mmd_file = output_dir / f"option_{option_letter}.mmd"
    first_line = py_file.read_text(encoding="utf-8").splitlines()[0]

    # Hard discriminator — either the token on line 1, OR a non-empty sibling .mmd
    is_fallback = (
        first_line.startswith("# FALLBACK_MERMAID:")
        or (mmd_file.exists() and mmd_file.stat().st_size > 0)
    )

    if is_fallback:
        if not mmd_file.exists():
            return f"FALLBACK FAILED: {mmd_file} missing (token present but no spec)"
        png_file = output_dir / f"option_{option_letter}-mermaid.png"
        result = subprocess.run(
            [
                sys.executable,                              # cross-platform; do NOT hardcode "py -3"
                str(SCRIPTS_DIR / "render_mermaid.py"),
                "--input",  str(mmd_file),
                "--output", str(png_file),
                "--theme",  str(client_theme_path),          # per-deck override
                "--width",  "1240",
                "--height", "540",
            ],
            capture_output=True,
        )
        if result.returncode != 0:
            return f"FALLBACK FAILED: {result.stderr.decode()}"
        build_fallback_slide_pptx(
            client_template, slide_n, option_letter,
            png_path=png_file, brief_title=brief_title, page_num=slide_n,
        )
        return "BUILT (fallback)"

    if first_line.startswith("# SKELETON_REJECTED:"):
        # Brief/pattern disagreement OR fishbone/concentric-rings rejection — surface in REVIEW.html
        return f"REJECTED: {first_line}"

    # Normal native path
    return execute_option_script(py_file, ...)
```

The fallback-slide PPTX layout:
- Title block at top (from `twins.helpers.add_title_block`)
- Body zone (y≈110–650) holds the rendered Mermaid PNG, full-bleed inside the body, with margin matching the slide grid
- Footer at bottom (from `twins.helpers.add_footer`)
- No accent bars or supplementary elements — the diagram is the slide

The fallback assembly is implemented in `scripts/finalize_deck.py::_assemble_fallback_pptx` (line 543). The pseudocode above shows the discriminator logic and rendering step; the real function operates on the `OptionStatus` data class with the same effect.

---

## What is not in this fallback (v0.1 limitations)

- **Fishbone / Ishikawa.** Mermaid has no native spine syntax — `flowchart LR` auto-layout produces a left-justified tree, which the architecture-review reviewers correctly flagged as not-a-fishbone. v0 emits `SKELETON_REJECTED: no Mermaid analogue — fishbone`. v0.1 escalation candidates: (a) manual node positioning in Mermaid via `subgraph` hacks (brittle, fragile across Mermaid versions); (b) raw HTML+SVG+Playwright with an explicit fishbone template; (c) generate as SmartArt placeholder for manual completion. Decide based on how often fishbone shows up in real briefs.
- **Concentric rings.** Mermaid has no analogue. `mindmap` is hierarchical, not concentric (one central node with radiating branches, no enclosing ring topology). v0 emits `SKELETON_REJECTED: no Mermaid analogue — concentric-rings`. v0.1 escalation candidates: raw HTML+SVG+Playwright with a concentric-rings template, or accept it as a permanent SmartArt manual-build case.
- **Pixel-perfect brand fidelity.** Mermaid theme overrides cover the major colors and font family, but Mermaid's auto-layout still controls spacing, line curvature, and arrowhead style. If a real A/B build shows brand mismatch on the four supported types, v0.1 swaps in Playwright for those specific slide types.
- **Interactive / animated outputs.** Mermaid can emit SVG with interactivity; the fallback uses PNG output only. Interactive PowerPoint isn't a v2 goal.

---

## What the agent must NOT do

1. **Do not attempt to build a curved-container diagram natively** to avoid SKELETON_REJECTED. The whole point of the fallback is that native python-pptx fails on these cases — silent substitution ships broken slides.
2. **Do not vary structural topology across the three .mmd options.** Hub-spoke stays hub-spoke; the three options vary only cosmetic choices (orientation, node shape, color emphasis). Structural variants here mean the user can't pick "the same diagram, different styling" — they have to mentally reconcile three different diagram shapes for the same slide.
3. **Do not include brief content the brief did not enumerate** (Hardline #2). If the brief lists 4 forces, the Porter's diagram has 4 forces. No invented fifth.
4. **Do not bake brand colors into the .mmd spec.** Brand colors come from the theme override JSON. The .mmd uses Mermaid's class names (`classDef brandPrimary fill:#4D148C` is acceptable for ad-hoc emphasis but the bulk styling is in the theme file).

---

## Files referenced

```
Renderer:           slide-builder\scripts\render_mermaid.py
Brand theme:        slide-builder\theme\mermaid-brand.json
Worked examples:    slide-builder\reference\fallback-examples\hub-spoke.mmd
                    slide-builder\reference\fallback-examples\porters-five-forces.mmd
                    (fishbone.mmd deferred to v0.1 — see § "What is not in this fallback")
Integration:        slide-builder\scripts\build_deck.py    (artifact #6)
                    slide-builder\scripts\finalize_deck.py (artifact #6)
```
