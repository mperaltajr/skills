# Pattern B — Geometry translation spec

> How slide coordinates flow from PowerPoint EMU (template-native) through HTML pixel space (1280×720 canvas) into python-pptx output, with a migration path for existing chrome.yml files.

**Status:** locked 2026-06-16. Depends on Decision 1 (canvas 1280×720), SPEC.md (canvas + zone structure).

---

## 1. The coordinate systems

| System | Unit | Used by | Example |
|---|---|---|---|
| OOXML / python-pptx | EMU (English Metric Unit; 914400 EMU = 1 inch) | The actual PPTX file format | `Inches(10) = 9144000 EMU` |
| HTML canvas | pixel @ 96 DPI | The HTML the worker writes; the rendered PNG | `1280px × 720px` |
| PowerPoint render | pixel @ render DPI | What PowerPoint shows on screen | matches canvas at default zoom |

PowerPoint's default slide at 16:9 is 13.333 × 7.5 inches → 12,192,000 × 6,858,000 EMU → at 96 DPI renders to 1280 × 720 pixels.

**The 1:1 relationship:** because we locked Decision 1 at canvas = 1280×720, HTML pixels map directly to PowerPoint EMU via the constant `9525 EMU per pixel` (i.e., `12,192,000 EMU / 1280 px = 9525`). No scaling factor.

```
1 HTML pixel = 9525 EMU
1 inch = 96 HTML pixels = 914400 EMU
```

## 2. `chrome.yml` schema — current vs Pattern B

**Current schema (v0.2, before Pattern B):**

```yaml
layouts:
  "Use as default slide template":
    layout_class: body-canonical
    title_placeholder_idx: 0
    subtitle_placeholder_idx: 10
    body_top_y_px: 149
    body_bottom_y_px: 667
    # ... (other fields)
```

Geometry stored as **derived pixel values**. The original EMU source (from the PPTX layout XML) is not preserved; the pixels are computed once at registration time and persisted.

**Problem:** if a future change wants to use canvas size ≠ 1280×720 (or wants to recalculate pixel positions for any reason), the original EMU values are lost. Reverse-engineering pixels back to EMU is lossy.

**Pattern B schema (v0.3):** add the SOURCE EMU values alongside the derived pixels:

```yaml
layouts:
  "Use as default slide template":
    layout_class: body-canonical
    title_placeholder_idx: 0
    subtitle_placeholder_idx: 10

    # Derived pixel values at 1280×720 canvas (existing fields, kept for backward compat)
    body_top_y_px: 149
    body_bottom_y_px: 667

    # NEW: source EMU values from the template layout XML (Pattern B v0.3)
    body_top_y_emu: 1419225      # = 149 * 9525
    body_bottom_y_emu: 6354675   # = 667 * 9525
    title_box_emu:                # placeholder geometry in EMU
      x: 685800                   # = 72 * 9525
      y: 304800                   # = 32 * 9525
      width: 11430000             # = 1200 * 9525
      height: 685800              # = 72 * 9525
    subtitle_box_emu:
      x: 685800
      y: 1066800
      width: 11430000
      height: 304800
    # ... (other zone-relevant placeholders)
```

The EMU values become the source of truth; pixel values become the derived layer (still written for backward compat with current readers).

**Schema version bump:** `chrome.yml` adds `schema_version: 3` at the top. `load_chrome_yml()` reads this and routes to the correct loader (v0.2 or v0.3).

## 3. `register_template.py` changes

`extract_chrome_spec()` (existing) currently extracts pixel values directly. Pattern B requires:

```python
def _extract_layout_geometry(layout) -> dict:
    """
    Extract placeholder geometry from a layout, preserving source EMU values.
    Returns both EMU (source) and px (derived at 1280×720) for backward compat.
    """
    geometry = {}
    for ph in layout.placeholders:
        try:
            t = int(ph.placeholder_format.type)
            idx = ph.placeholder_format.idx
        except Exception:
            continue
        if t in (1, 13):  # TITLE / CENTER_TITLE
            geometry["title_box_emu"] = {
                "x": int(ph.left), "y": int(ph.top),
                "width": int(ph.width), "height": int(ph.height),
            }
            geometry["title_box_px"] = _emu_to_px_dict(geometry["title_box_emu"])
        # ... (similar for subtitle, footer, page_number)
    # body_top_y / body_bottom_y derived from title bottom + footer top:
    geometry["body_top_y_emu"] = title_bottom_emu  # from title placeholder
    geometry["body_top_y_px"] = _emu_to_px(geometry["body_top_y_emu"])
    geometry["body_bottom_y_emu"] = footer_top_emu  # from footer placeholder
    geometry["body_bottom_y_px"] = _emu_to_px(geometry["body_bottom_y_emu"])
    return geometry
```

`_emu_to_px` is the new converter:

```python
EMU_PER_PX_AT_1280 = 9525  # locked: canvas 1280×720 means 1 px = 9525 EMU

def emu_to_px(emu: int) -> int:
    """Convert EMU to HTML pixel at the locked 1280×720 canvas scale."""
    return int(round(emu / EMU_PER_PX_AT_1280))

def px_to_emu(px: int) -> int:
    """Convert HTML pixel to EMU at the locked 1280×720 canvas scale."""
    return int(round(px * EMU_PER_PX_AT_1280))

def _emu_to_px_dict(emu_dict: dict) -> dict:
    """Convert a {x, y, width, height} EMU dict to pixels."""
    return {k: emu_to_px(v) for k, v in emu_dict.items()}
```

These helpers live in `slide-builder/scripts/_chrome_schema.py` (or `twins/helpers.py` — pick one canonical location; recommend `_chrome_schema.py` since it owns chrome.yml structure).

## 4. Migration for existing chrome.yml files

Existing registered templates have `chrome.yml` files at schema v0.2 (pixel-only). When loaded under Pattern B:

```python
def load_chrome_yml(path: Path) -> ChromeSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    schema_version = raw.get("schema_version", 2)

    if schema_version == 2:
        # Reverse-infer EMU from stored pixels. Lossy but survivable.
        # Surface a one-time warning telling user to re-register.
        sys.stderr.write(
            f"  NOTICE: chrome.yml at {path} is schema v0.2 (pixel-only). "
            f"Reverse-inferring EMU values from stored pixels. Recommend "
            f"re-running register_template.py to get accurate v0.3 schema:\n"
            f"    py -3 scripts/register_template.py propose <template.pptx>\n"
        )
        raw = _migrate_v2_to_v3(raw)

    return ChromeSpec.parse_obj(raw)

def _migrate_v2_to_v3(raw: dict) -> dict:
    """Migrate chrome.yml schema v0.2 → v0.3. Lossy reverse-inference of EMU from px."""
    for layout_name, layout_spec in raw.get("layouts", {}).items():
        if "body_top_y_px" in layout_spec and "body_top_y_emu" not in layout_spec:
            layout_spec["body_top_y_emu"] = px_to_emu(layout_spec["body_top_y_px"])
            layout_spec["body_bottom_y_emu"] = px_to_emu(layout_spec["body_bottom_y_px"])
        # ... (similar for other box geometry)
    raw["schema_version"] = 3
    return raw
```

No hard-fail on schema mismatch; soft-migrate with a warning. Users are encouraged but not forced to re-register.

(Note: `_meta.json` schema version is separate. Spec 7 handles the build-output schema; this Spec 3 handles the registration-output schema.)

## 5. Worker / translator usage

**Worker uses HTML pixel coordinates** for positioning content within the body zone:

```html
<div class="body-zone" style="position: absolute; top: 149px; bottom: 53px; left: 0; right: 0;">
  <!-- worker positions content within this zone using HTML pixels -->
  <div class="anchor-row" style="position: absolute; top: 230px; left: 80px; width: 1120px; height: 60px;">
    <!-- ... -->
  </div>
</div>
```

The values `top: 149px`, `bottom: 53px` come from `chrome.yml::body_top_y_px` and `(720 - body_bottom_y_px)` — already in `_context.md` as CSS variables `--body-top` and computed.

**Translator converts to EMU** for native python-pptx output:

```python
def translate_body_shape(html_x_px: int, html_y_px: int,
                          html_w_px: int, html_h_px: int) -> dict:
    """Convert HTML pixel coordinates to python-pptx EMU keyword args."""
    return {
        "left": Emu(px_to_emu(html_x_px)),
        "top": Emu(px_to_emu(html_y_px)),
        "width": Emu(px_to_emu(html_w_px)),
        "height": Emu(px_to_emu(html_h_px)),
    }
```

Translator wraps every `add_shape()` call through this helper. No magic constants in translator output.

## 6. Border-radius conversion

CSS `border-radius: 18px` → python-pptx `ROUNDED_RECTANGLE` with adjustment value.

python-pptx's `MSO_SHAPE.ROUNDED_RECTANGLE` has one adjustment handle (`adjustments[0]`) that takes a FRACTION of the shape's shorter dimension (0.0 = sharp, 0.5 = pill). The conversion:

```python
def css_radius_to_pptx_adjustment(border_radius_px: int,
                                    shape_width_px: int,
                                    shape_height_px: int) -> float:
    """
    Convert CSS border-radius (px) to python-pptx ROUNDED_RECTANGLE
    adjustment value (fraction of shorter dimension).
    """
    shorter = min(shape_width_px, shape_height_px)
    # adjustment[0] is the corner radius as fraction of HALF the shorter side
    fraction = border_radius_px / (shorter / 2)
    # clamp to [0.0, 1.0] — 1.0 produces a full pill on the short axis
    return max(0.0, min(1.0, fraction))
```

Test: 18px radius on a 100×40 card → shorter = 40, half = 20, fraction = 18/20 = 0.9 (nearly pill, intentional for tight cards). 18px on a 1000×60 wide row → shorter = 60, half = 30, fraction = 18/30 = 0.6 (rounded but not pill).

This matches MBB playbook guidance: subtle 10-14px on large cards, modern 16-22px on medium cards, product-like 24-32px on small chips.

## 7. Padding and margin handling

CSS `padding` and `margin` translate to absolute positioning offsets. Translator computes child positions accounting for parent padding:

```python
def apply_padding(parent_box: dict, padding: dict) -> dict:
    """Return the inner box after applying CSS-style padding."""
    return {
        "x": parent_box["x"] + padding.get("left", 0),
        "y": parent_box["y"] + padding.get("top", 0),
        "width": parent_box["width"] - padding.get("left", 0) - padding.get("right", 0),
        "height": parent_box["height"] - padding.get("top", 0) - padding.get("bottom", 0),
    }
```

Translator's parser walks the HTML DOM, accumulates padding+margin per element, computes absolute coordinates for each leaf shape.

## 8. Flexbox and CSS Grid decomposition

CSS layout primitives don't have direct python-pptx equivalents. Translator must DECOMPOSE the laid-out HTML into absolute coordinates by reading the rendered DOM via headless browser:

```python
def extract_layout_from_rendered_html(html_path: Path, browser_page) -> list[dict]:
    """
    Use Playwright to get the computed bounding rect for each element with
    data-shape-id. Returns list of {shape_id, x, y, width, height, css_props}.
    """
    page = browser_page
    page.goto(f"file://{html_path}")
    elements = page.evaluate("""
      () => Array.from(document.querySelectorAll('[data-shape-id]')).map(el => {
        const rect = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        return {
          shape_id: el.dataset.shapeId,
          x: rect.x, y: rect.y, width: rect.width, height: rect.height,
          background_color: cs.backgroundColor,
          border_radius: cs.borderRadius,
          font_family: cs.fontFamily,
          font_size: parseFloat(cs.fontSize),
          font_weight: cs.fontWeight,
          color: cs.color,
          /* ... other relevant computed properties */
        };
      })
    """)
    return elements
```

**Translator pulls computed style from the same Playwright instance that rendered the PNG.** This gives it the true post-layout coordinates without re-implementing flex/grid math in python.

`data-shape-id` is the contract: any element the worker wants the translator to create as a native shape must have this attribute. Elements without it are ignored (they exist for visual context in the HTML render but don't become native shapes).

## 9. Worker contract for data-shape-id

Worker prompt directive:

> Every element you want to become a native PowerPoint shape MUST have a `data-shape-id` attribute. Without it, the translator skips the element. Use this on body-zone elements only — chrome zones (title, subtitle, footer) are handled separately via `data-template-field`.

Example:

```html
<div class="anchor-row" data-shape-id="row-hybrid" style="position: absolute; ...">
  <div class="anchor-stripe" data-shape-id="row-hybrid-stripe" style="..."></div>
  <h3 class="row-label" data-shape-id="row-hybrid-label">Hybrid model</h3>
  <span class="row-metric" data-shape-id="row-hybrid-metric-1">Medium — pair team live in week 1</span>
  <!-- ... -->
</div>
```

Each `data-shape-id` becomes a native shape in the PPTX, positioned at the computed-style coordinates.

## 10. Integration points

| File | Change |
|---|---|
| `scripts/_chrome_schema.py` | Add `emu_to_px`, `px_to_emu`, `_emu_to_px_dict` helpers. Bump chrome.yml schema version handling. Add `_migrate_v2_to_v3` for backward compat. |
| `scripts/register_template.py` | Update `_extract_layout_geometry` (or equivalent) to extract and store EMU source values alongside derived pixels. |
| (new) Translator agent | Use Playwright `getComputedStyle()` to extract post-layout coordinates. Convert HTML px to EMU for all shape creation. |
| (new) `_context.md` | Inline body-zone bounds as `--body-top`, `--body-bottom`, `--body-width` so worker can position absolutely. |

## 11. Out of scope

- Multi-canvas support (different aspect ratios) — locked at 16:9 1280×720 only
- Vector path generation from CSS (e.g., `clip-path` translation) — kill-listed in SPEC.md
- Animation timeline → PowerPoint animation pane — out of scope; output is static
- CSS transforms (rotate, skew) — kill-listed except in specific opt-in cases

---

**Geometry translation is mechanical** given the 1:1 EMU/pixel mapping at the locked canvas size. The novel work is the headless-browser-driven layout extraction (§8), which gets us out of having to re-implement CSS flex/grid math in Python.
