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
4. Gives every shape a fresh id (the library XML carries the ids of its source deck; two shapes with one id make PowerPoint refuse a file) and names the outer shape `icon-<name>`
5. Injects into the target slide's `spTree`

---

## The checked list: the names designers use

**About half of the library's names do not match their pictures** (the names were assigned by position in the source deck, and many are shifted onto a neighbor: `certified-75` is a clipboard, `bank-12` a gavel, `partner-17` a yen sign). So designers pick only from **`checked-icons.json`**: names whose picture was checked by eye (2026-10-08) to match the name, each with what the picture `shows` and what it suits (`use_for`). The full library stays on disk so older scripts keep working; a name outside the list still draws, with an advisory on the review card that its picture may not match. Do not rename files: old briefs and scripts use the current names.

Three of the original 15 standard names are NOT on the checked list because their pictures do not match: `shield-warning` (a vault with a combination dial), `chip` (a head silhouette with binary digits), `speech` (a podium). `compass` is a compass rose in a circle (an older version of this page wrongly called it a lighthouse).

See every checked icon at once: `py -3 scripts/icon_svg.py --sheet sheet.html --names checked` and open the sheet (a check mark marks checked names). Adding a name to the list: render it, look at it, and add it only if the picture is what the name says.

## Previews for the sketch path (`svg/`)

`icons/svg/<name>.svg` holds one small SVG per icon (about 2 MB in all), converted once from the icon's own DrawingML by `py -3 scripts/icon_svg.py --build` (re-run it after adding an icon). The conversion reads the same geometry `insert_icon` puts on a slide, and every shape is filled with `currentColor`, so the sketch shows the slide's picture in the designer's color. `render_html.py` and `translate_html.py` both use them; the finished slide gets the real vector icon, not the SVG. Two library icons have no preview (one is a picture, not shapes); asking for them gives a labeled placeholder.

## Sketch path: how an icon gets from HTML to the slide

```html
<i data-icon-name="clipboard-check" style="width:32px;height:32px;color:#1F3A93"></i>
```

1. `render_html.py` draws it from `svg/clipboard-check.svg` in the element's color (or `data-icon-color`).
2. `translate_html.py` records an `icon` step: name, box (the picture fitted into the element's box, keeping its shape) and color.
3. `twins/html_emit.py` calls `insert_icon()` at that box and color. The group is named `icon-<name>` and gets fresh shape ids.
4. An unknown name: a labeled dashed box on the sketch, `insert_icon`'s labeled placeholder on the slide, and an `ICON_UNKNOWN` warning on the render, the translation report and the review card.

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
