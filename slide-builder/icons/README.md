# Slide Lab — Icons Library

Icons are extracted once from a **client- or firm-supplied icon library PPTX** and inserted into slides as native PowerPoint vector shapes. This preserves perfect quality at any size and removes any rasterization or conversion dependency.

---

## Source file

Set `SLIDE_LAB_ICON_LIBRARY` to the absolute path of your icon library PPTX, or pass it on the CLI to `extract_icons.py`. Pre-extracted icon XML files live in `slide-builder/icons/<name>.xml`; only re-run extraction when the library changes.

The author's reference library has 163 slides, 29 categories, ~1,971 keyword-labelled icons. **A new user does not need this exact library** — `icon_helper.insert_icon()` falls back to a labeled dashed-border placeholder if the named icon XML is missing, so the pipeline still builds. To use your own icon corpus, point `extract_icons.py` at any PPTX with named shapes; see "Adding new icons" below.

---

## How icons work in the pipeline

**Phase A (HTML mockup):**  
Icons are inline SVG approximations inside `.process-icon` divs. Visual only — Phase B ignores the SVG paths entirely and looks at the `data-icon` attribute.

```html
<div class="process-icon" data-icon="gear"
     style="width:40px; height:40px; margin:0 auto 10px auto;">
  <!-- inline SVG for preview only -->
</div>
```

**Phase B (PPTX build):**  
`build_slide.py` calls `icon_helper.insert_icon()`:

1. Reads `icons/<name>.xml` (pre-extracted shape XML)
2. Applies accent color tint by replacing all `solidFill/srgbClr` values with `accent1` hex
3. Repositions to the bounding box coordinates from the HTML element
4. Injects directly into the target slide's `spTree` using lxml
5. If XML file is missing: inserts a labeled dashed-border placeholder

No PPTX opening at build time — just XML read + inject.

---

## Vocabulary — 15 standard icons

| `data-icon` | Concept | Visual description | Source slide |
|-------------|---------|-------------------|-------------|
| `gear` | Process / operations | Single cog wheel — workflow/process | 131 |
| `wrench` | Work in progress / tools | Standalone wrench | 131 |
| `people` | People / team / workforce | 3-tier org chart hierarchy with person icons | 35 |
| `chart-bar` | Data / analytics | Clean 3-bar vertical bar chart | 13 |
| `compass` | Strategy / direction | Lighthouse with light beams — vision/navigate | 51 |
| `calendar` | Timeline / schedule | Calendar grid with all date cells | 152 |
| `coins` | Cost / budget | Stacked coin cylinders (3 heights) | 15 |
| `shield-warning` | Risk / escalation | Vault/safe with combination dial — security | 14 |
| `diamond` | Decision / approval | Hands holding diamond gem — key value | 13 |
| `lightbulb` | Insight / finding | Head silhouette with lightbulb and rays | 36 |
| `globe` | External / market | Globe with continent outlines | 50 |
| `clipboard-check` | Compliance / audit | Clipboard with checkmark and task items | 75 |
| `chip` | Technology / systems | Head silhouette with binary code overlay | 33 |
| `speech` | Communication | Podium / lectern | 15 |
| `package` | Delivery / output | 3D box / cube outline | 78 |

See `icon-index.json` for source slide, position coordinates, and full metadata.

---

## Extraction approach — position-based

Icons are extracted using **visual position coordinates** (`source_x_pct`, `source_y_pct`), not keyword matching. Each entry in `icon-index.json` specifies the fractional slide position of the exact icon shape as visually confirmed in the exported PNG slides.

This is far more reliable than keyword proximity, which would pick wrong neighbors in compound-icon sections.

### How the slide layout maps to coordinates

Each icon slide has:
- 6% header bar at top
- 3 rows of icon sections below
- 6 or 7 columns per row
- Within each section: 4 icon variants in a 2×2 grid (gray outline, purple filled, alt-gray, black outline)

The coordinates target the **gray outline variant** (top-left of each section cell) — the one with no solid fill, which tints cleanly at build time.

### Finding coordinates for a new icon

1. Export all slides to PNG (use `slide-qc/scripts/render_slides.py <icon-library.pptx> <out-dir>`)
2. Open the target slide PNG and visually identify the icon section
3. Run the inspect tool to list shapes near that position:

```
py -3 extract_icons.py --inspect 131 0.60 0.73
```

Output shows shape type, bounding box (pt), distance, and any text labels — use these to confirm which shape is selected.

4. Set `source_x_pct` and `source_y_pct` to a point INSIDE the gray icon's bounding box
5. The text label shown in `--inspect` output confirms which section you're in

### Coordinate calibration tips

- The gray icon center is typically at `col_center - 3%` horizontally (slightly left of section center)
- Row centers: row 1 ≈ 18% of slide height, row 2 ≈ 48%, row 3 ≈ 73% of slide height
- Individual icons are approximately 37-42pt wide × 33-40pt tall
- If containment fails, the proximity fallback finds the nearest shape — use `--inspect` to verify

---

## Adding new icons

1. Browse the PNG export of your icon library (see "Finding coordinates for a new icon" above)
2. Find the slide and section containing the icon you want
3. Run `--inspect` to get exact bounding box:
   ```
   py -3 extract_icons.py --inspect <slide_num> <x_pct> <y_pct>
   ```
4. Add entry to `icon-index.json`:
   ```json
   {
     "name": "my-icon",
     "concept": "Human-readable concept",
     "source_slide": 42,
     "source_x_pct": 0.33,
     "source_y_pct": 0.45,
     "concept_label": "exact label text from the slide section",
     "visual": "Description of what the icon looks like",
     "slide_category": "CATEGORY NAME",
     "grid_position": "row N, col N of N"
   }
   ```
5. Extract: `py -3 extract_icons.py --icon my-icon`
6. Verify: `py -3 extract_icons.py --icon my-icon --verify` (opens PNG preview)

---

## Color tinting

When copying an icon shape, `icon_helper.py` replaces all `solidFill/srgbClr` values with the template `accent1` hex. This works because:
- At extraction time, `normalize_colors()` sets all fill colors to `#000000`
- At build time, `_apply_accent_color()` replaces all `srgbClr` with the accent color

Shape elements that use `schemeClr` (theme colors) are intentionally skipped — these are theme-aware fills that should not be overridden.

---

## Fallback behavior

If `insert_icon()` fails to find the XML file:
- Inserts a 40×40pt rectangle with dashed border
- Labels it with the `data-icon` value
- Adds a post-build note: `"Icon '{name}' not found — run extract_icons.py to populate"`

This prevents build failures due to missing icons.

---

## Script locations

| Script | Purpose |
|--------|---------|
| `slide-builder/scripts/icon_helper.py` | Build-time icon injection into PPTX slides |
| `slide-builder/scripts/extract_icons.py` | One-time extraction from source PPTX |

```python
# Build-time usage
from icon_helper import insert_icon

insert_icon(
    icon_name="gear",
    target_slide=prs.slides[0],
    left_emu=914400,       # position from HTML bounding box
    top_emu=1143000,
    width_emu=457200,      # 40px at 96dpi -> EMU
    height_emu=457200,
    accent_color="#A100FF" # from theme.json accent1
)
```
