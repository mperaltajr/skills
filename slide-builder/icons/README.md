# Slide Lab — Icons Library

Icons are pre-extracted shape XML fragments under `slide-builder/icons/<file>.xml`. At build time, `icon_helper.insert_icon()` looks the name up, reads the XML, applies a color tint, repositions to the target bounding box, and injects directly into the slide's `spTree` via lxml. The pipeline never opens a PPTX at this step — pure XML manipulation.

This preserves perfect vector quality at any size and removes any rasterization dependency.

---

## What ships

`slide-builder/icons/` contains the pre-extracted XML files plus `icon-index.json` which maps each icon name → source-slide metadata (kept for provenance). There is **no live extraction step in the pipeline** — icons are added by hand (see below).

**Unknown names are refused (owner's decision 2026-10-21).** Every name goes through `scripts/icon_names.py`, the one lookup. A plain name from `checked-icons.json` opens its file. An old name of an allowed icon (its file name, such as `gear` or `people`, or one of the three 10/08 names that moved: `team-35` to `org-chart`, `mobile-100` to `mobile-data`, `search-31` to `person-search`) still works and prints its plain name, so old scripts rebuild. Any other name stops the build on the direct path (`icon_names.UnknownIcon`, with the next step) and blocks the option on the review page on the sketch path (`ICON_UNKNOWN`, Critical).

---

## How icons get used at build time

The per-slide option script (written by `slide-builder-worker`) calls `icon_helper.insert_icon()`:

```python
from icon_helper import insert_icon

insert_icon(
    icon_name="gear-refresh",
    target_slide=prs.slides[0],
    left_emu=914400,        # bounding-box left from your pattern coords
    top_emu=1143000,
    width_emu=457200,       # 40px at 96 DPI → EMU
    height_emu=457200,
    # accent_color: leave it out for the template's dark text color (the default)
)
```

The function:

1. Looks the name up (`icon_names.resolve`) and reads `icons/<file>.xml`
2. Replaces all `solidFill/srgbClr` values with the supplied hex (default `#000000`, TEXT_DARK, which the theme step turns into the template's dark text color) (theme-aware `schemeClr` fills are deliberately preserved)
3. Repositions to the supplied bounding box
4. Gives every shape a fresh id (the library XML carries the ids of its source deck; two shapes with one id make PowerPoint refuse a file) names the outer shape `icon-<name>` and gives it the alt text `Icon: <name>` (slide-qc counts icons by it)
5. Injects into the target slide's `spTree`

---

## The allowed list: the names designers use

**About half of the library's file names do not match their pictures** (the names were assigned by position in the source deck: `certified-75` is a clipboard, `bank-12` a gavel, `shield-warning` a vault). So designers use only **`checked-icons.json`**: 238 icons (2026-10-21), each drawn and checked by eye at 24 px. Each entry has a plain `name` that says what the picture is, the `file` it draws from, a `topic` (21 topics, from people to legal), what the picture `shows`, its `old_names`, `min_px` 32 when it blurs smaller, and a `note` for `rocket` and `lightbulb` (use sparingly). No two names share a file and no two files are the same drawing. The other library files stay on disk; they are not offered. Do not rename or delete files: old scripts use the file names.

How the 238 were chosen: an expander and a challenger each went through all 1,143 files, an adjudicator settled 283 by eye, and the owner asked for about 240 (2026-10-21). Trimmed: icons that blur at 24 px unless they were the only icon for a main deck topic (kept: `currency-exchange`, `server-cost`, `time-is-money`, `person-search`, all marked 32 px+), near-twins within a topic (the clearer one stays), and extras in second-tier topics (shop, medical, extra person variants). Every topic still has icons.

**Rules (owner's, 2026-10-21):** the default list marker is a number for a real sequence, otherwise a plain circle or square; an icon only when its picture adds meaning. At most 6 icons on a page, never an icon and a number on one item, no icon in the headline or inside a chart; in a table only as row labels (counted in the 6). Color: the template's dark text color by default; the accent only when asked; a light accent (such as a pale yellow) only on a dark area. Each design prompt offers 2 to 4 topics picked from the page's words plus the status group (`{{ICON_TOPICS}}`, filled by `build_deck.py`). slide-qc flags an icon inside a chart (Major) and, as Advisory notes, more than 6 icons on a page, icons on more than a third of the pages, or one icon on 3 or more pages.

**Not in the library yet:** a GPU card, a data-center hall, a lease document. Use `microchip` for a chip, `server-rack` for installed GPUs or GPU capacity, `site-pin` for a site, `sign-here` or `handshake` for a lease (and say "Lease" in the text). New drawings come later.

See the icons: `py -3 scripts/icon_names.py --topics` lists them by topic; `py -3 scripts/icon_svg.py --sheet sheet.html --names allowed --px 24` (or `--names topic:finance`) writes a picture sheet. `py -3 scripts/icon_names.py NAME` says what a name opens. Adding an icon: render it at 24 px, look at it, give it a plain name that says what it shows, and add it only if no allowed icon already shows the same thing.

## Previews for the sketch path (`svg/`)

`icons/svg/<file>.svg` holds one small SVG per library file (about 2 MB in all), converted once from the icon's own DrawingML by `py -3 scripts/icon_svg.py --build` (re-run it after adding an icon). The conversion reads the same geometry `insert_icon` puts on a slide, and every shape is filled with `currentColor`, so the sketch shows the slide's picture in the designer's color. `render_html.py` and `translate_html.py` both use them; the finished slide gets the real vector icon, not the SVG. Two library icons have no preview (one is a picture, not shapes); asking for them gives a labeled placeholder.

## Sketch path: how an icon gets from HTML to the slide

```html
<i data-icon-name="clipboard-check" style="width:32px;height:32px;color:#1F3A93"></i>
```

1. `render_html.py` draws it from its file's preview in `svg/` in the element's color (or `data-icon-color`).
2. `translate_html.py` records an `icon` step: name, box (the picture fitted into the element's box, keeping its shape) and color.
3. `twins/html_emit.py` calls `insert_icon()` at that box and color. The group is named `icon-<name>` and gets fresh shape ids.
4. An old name is drawn and becomes its plain name on the slide (`ICON_OLD_NAME` note). An unknown name: a labeled dashed box on the sketch and the slide, and an `ICON_UNKNOWN` warning on the render and the translation report; on the review card it is Critical and the option says "Needs a fix".

See `icon-index.json` for per-icon source-slide provenance and grid coordinates (kept for reference; not used at build time).

---

## Color tinting — how the accent applies

`icon_helper.py` replaces every `solidFill/srgbClr` value in the extracted XML with the supplied `accent_color` hex, by default `#000000` (TEXT_DARK: the template's dark text color once the theme step runs). Before 2026-10-21 the default was `#A100FF` (a purple accent), which is why icons came out in the accent color unasked.

Shape elements that use `schemeClr` (theme-bound colors) are intentionally skipped — those are template-aware fills that the registered theme should drive, not the icon.

---

## Fallback behavior

If an allowed name's `icons/<file>.xml` is missing (an unknown name never gets this far):

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
