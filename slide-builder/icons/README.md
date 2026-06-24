# Slide Lab — Icons Library

Icons are pre-extracted shape XML fragments under `slide-builder/icons/<name>.xml`. At build time, `icon_helper.insert_icon()` reads the XML, applies an accent-color tint, repositions to the target bounding box, and injects directly into the slide's `spTree` via lxml. The pipeline never opens a PPTX at this step — pure XML manipulation.

This preserves perfect vector quality at any size and removes any rasterization dependency.

---

## What ships

`slide-builder/icons/` contains the pre-extracted XML files plus `icon-index.json` which maps each icon name → source-slide metadata (kept for provenance). There is **no live extraction step in the pipeline** — icons are added by hand (see below).

**Missing-icon behavior.** If a pattern asks for an icon name that has no XML file in `icons/`, `icon_helper.insert_icon()` falls back to a labeled dashed-border placeholder. The build never errors on a missing icon. The placeholder includes the requested name so the user can see what was wanted on the rendered slide.

---

## How icons get used at build time

The per-slide option script (written by `slide-builder-worker`) calls `icon_helper.insert_icon()`:

```python
from icon_helper import insert_icon

insert_icon(
    icon_name="gear",
    target_slide=prs.slides[0],
    left_emu=914400,        # bounding-box left from your pattern coords
    top_emu=1143000,
    width_emu=457200,       # 40px at 96 DPI → EMU
    height_emu=457200,
    accent_color="#A100FF", # from registered template's theme.json accent1
)
```

The function:

1. Reads `icons/<name>.xml`
2. Replaces all `solidFill/srgbClr` values with the supplied accent hex (theme-aware `schemeClr` fills are deliberately preserved)
3. Repositions to the supplied bounding box
4. Injects into the target slide's `spTree`

---

## Standard 15-icon vocabulary

The pre-extracted set covers the most common consulting concepts. Pattern prompts should pick from these names by default; anything outside the list falls through to a placeholder.

| `data-icon` | Concept | Visual |
|-------------|---------|--------|
| `gear` | Process / operations | Single cog wheel |
| `wrench` | Work in progress / tools | Standalone wrench |
| `people` | People / team / workforce | 3-tier org-chart hierarchy |
| `chart-bar` | Data / analytics | 3-bar vertical chart |
| `compass` | Strategy / direction | Lighthouse with light beams |
| `calendar` | Timeline / schedule | Calendar grid |
| `coins` | Cost / budget | Stacked coin cylinders |
| `shield-warning` | Risk / escalation | Vault with combination dial |
| `diamond` | Decision / approval | Hands holding diamond |
| `lightbulb` | Insight / finding | Head silhouette with lightbulb |
| `globe` | External / market | Globe with continent outlines |
| `clipboard-check` | Compliance / audit | Clipboard with checkmark |
| `chip` | Technology / systems | Head silhouette with binary overlay |
| `speech` | Communication | Podium / lectern |
| `package` | Delivery / output | 3D cube outline |

See `icon-index.json` for per-icon source-slide provenance and grid coordinates (kept for reference; not used at build time).

---

## Color tinting — how the accent applies

`icon_helper.py` replaces every `solidFill/srgbClr` value in the extracted XML with the supplied `accent_color` hex. This works because the extracted icons normalize all fill colors to `#000000` at extraction time; at build time every `srgbClr` is rewritten to the brand accent.

Shape elements that use `schemeClr` (theme-bound colors) are intentionally skipped — those are template-aware fills that the registered theme should drive, not the icon.

---

## Fallback behavior

If `insert_icon()` cannot find `icons/<name>.xml`:

- Inserts a 40×40pt rectangle with dashed border at the requested bounding box
- Labels the rectangle with the requested icon name
- Logs a one-line warning to stdout

This prevents build failures and surfaces the missing-icon condition visually for the reviewer to catch in REVIEW.html.

---

## Adding new icons (out of band)

There is no in-skill extraction script. If you need to add an icon:

1. Hand-author a new `icons/<name>.xml` file matching the structure of an existing one (a single `p:sp` group, with `solidFill/srgbClr` values where you want the accent to apply).
2. Optionally append a metadata entry to `icon-index.json` for provenance.

This is intentionally an explicit, low-frequency operation. The current icon vocabulary covers the patterns the skill ships.
