# Sketch path — HTML/CSS canvas specification

> The authoring contract for the sketch (HTML-first) build path. Defines the HTML canvas dimensions, CSS conventions, brand-variable injection, font fallback, icon handling, and CSS feature kill-list that every worker-generated HTML file must conform to.

**Key rules this spec defines:**
- HTML canvas = **1280×720** (PowerPoint default, 1:1 with PPT slide dimensions)
- Pattern routing: bullets/dividers → direct path; visual structure → sketch path
- Chrome handling = Option I: full-slide HTML; title/subtitle/footer text are data fields written into template placeholders by translator

---

## 1. Canvas dimensions

Every worker-generated HTML file MUST use this exact canvas:

```html
<div class="slide-canvas">
  <!-- title bar zone, body zone, footer zone all live here -->
</div>
```

```css
.slide-canvas {
  width: 1280px;
  height: 720px;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
  background: var(--slide-canvas-bg, #FFFFFF);
}
```

Rules:
- Canvas is FIXED at `1280px × 720px`. No responsive sizing. No viewport units.
- `overflow: hidden` enforces that content cannot extend past the canvas edges.
- `position: relative` enables absolute positioning of child zones inside the canvas.
- `box-sizing: border-box` so padding doesn't extend the canvas size.
- Background color is **the template's own background for this slide's layout**: `_context.md` gives it as `--slide-canvas-bg` (it can be a light gray-blue, not white; the `#FFFFFF` fallback is for a loose file only). Paint the canvas with it, so the sketch you design and the user approves looks like the finished slide. Sketches used to be drawn on a fixed white, and a pale panel approved on white vanished on a gray-blue master (2026-10-06). The translator leaves a canvas of that color to the template (the slide already has it; a full-slide rectangle would cover the master's own artwork) and draws a canvas of any other color as the design's own. A large panel within a few shades of what is behind it gets a `PALE_FILL_ON_BACKGROUND` advisory on the review page: give it a clearly different fill or an outline.

**Why this size:** matches PowerPoint's default 16:9 slide dimensions exactly. Geometry math becomes 1:1 (HTML pixel = PPT EMU/9525). No scaling factors. Worker can position elements using coordinates that map directly to chrome.yml pixel values.

## 2. Zone structure inside the canvas

The 1280×720 canvas has three logical zones. Coordinates come from the registered template's `chrome.yml`:

```
┌─────────────────────────────────────────────┐  y=0
│  CHROME TOP                                 │
│  (title bar, subtitle bar, accent stripe)   │
├─────────────────────────────────────────────┤  y=body_top_y_px (per-layout; see _context.md)
│                                             │
│  BODY ZONE                                  │
│  (worker writes consulting-grade content    │
│   here — comparison cards, value trees,     │
│   iconified rows, etc.)                     │
│                                             │
├─────────────────────────────────────────────┤  y=body_bottom_y_px (e.g., 667)
│  CHROME BOTTOM                              │
│  (footer band, page number)                 │
└─────────────────────────────────────────────┘  y=720
```

The worker is required to:
1. **Render the full canvas** so the body composition is visually contextualized by surrounding chrome. The worker SEES the title + body + footer together while designing.
2. **Position body content between `body_top_y_px` and `body_bottom_y_px`**. The translator agent extracts only this region for native shape generation.
3. **Place title, subtitle, footer text in the appropriate chrome zones** of the HTML for design context, but these text values are also extracted as separate data fields and written into the template's inherited placeholders by the translator (not as freeform shapes).

Chrome top/bottom dimensions come from `chrome.yml` per layout. The worker reads these from `_context.md` at build time.

## 3. CSS reset

Every HTML file begins with this exact CSS reset (no variations):

```css
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: var(--font-sans);
  color: var(--text-primary);
  font-size: 16px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
img { max-width: 100%; display: block; }
table { border-collapse: collapse; border-spacing: 0; }
```

No external CSS frameworks (no Bootstrap, Tailwind, etc.). Inline styles allowed but discouraged; prefer named classes for anything reused across multiple elements.

## 4. Brand-variable injection

Brand colors and fonts are injected as CSS variables at the top of every HTML file. The translator and the render pipeline both rely on these names being stable.

**Required CSS variable names** (worker must use these exact names):

```css
:root {
  /* Brand colors (from brand.yml) */
  --brand-primary: #4D148C;      /* primary_hex */
  --brand-accent: #FF6600;       /* accent_hex */
  --brand-cover-bg: #4D148C;     /* cover_bg_hex */
  --brand-dark-bg: #1A0A2E;      /* dark_bg_hex */

  /* Derived brand colors (mechanical from primary + accent + neutrals) */
  --brand-primary-soft: #EEEDFE;   /* primary mixed 30% toward white */
  --brand-accent-soft: #FFF4EB;    /* accent mixed 60% toward white */
  --brand-text-primary: #1A1A1A;
  --brand-text-secondary: #5F5E5A;
  --brand-text-tertiary: #888780;
  --brand-border-light: #D3D1C7;
  --brand-divider: #E1E1E6;

  /* Fonts (from brand.yml font_heading + font_body) */
  --font-heading: "<brand heading font>", "Segoe UI", -apple-system, sans-serif;
  --font-sans: "<brand body font>", "Segoe UI", -apple-system, sans-serif;
  --font-mono: ui-monospace, "Consolas", monospace;

  /* Canvas: the layout's own background. brand.css carries the default
     content layout's; _context.md carries this slide's layout's. Use that. */
  --slide-canvas-bg: <from _context.md>;

  /* Body zone bounds — COPY THESE FROM YOUR SLIDE'S _context.md.
     The values below are placeholders, NOT real numbers. They differ per
     template AND per layout. Hardcoding them is a known defect: the numbers
     that used to sit here came from this repo's test fixture, and worker
     options copied them onto a client template whose real body top was
     different, which put content underneath the grafted takeaway line. */
  --body-top: <from _context.md>;
  --body-bottom: <from _context.md>;
  --body-height: <from _context.md>;
  --body-left: <from _context.md>;    /* the template's side margins: */
  --body-right: <from _context.md>;   /* keep body content between them */
  --body-width: 1280px;
}
```

The brand/colour/font part of this `:root` block is generated by `register_template.py commit` from `brand.yml` and saved as `<template-stem>/brand.css`. **The body-zone bounds are NOT in brand.css** — they are per-layout, and brand.css is per-template. Take them from the slide's `_context.md` (see below). The worker references this file in their HTML:

```html
<link rel="stylesheet" href="brand.css">
```

OR (preferred for self-contained HTML files):

```html
<style>
  /* CSS variables inlined here from brand.css */
  :root { --brand-primary: #4D148C; /* ... etc */ }
</style>
```

`build_deck.py` Stage 1 writes each slide's `_context.md` with an authoritative body-zone `:root` block for **that slide's layout**, resolved from the same code finalize uses. **Use those numbers. Do not guess and do not copy them from this document.** The body top already excludes the band the grafted title and takeaway occupy, so content placed at or below `--body-top` cannot collide after the graft. Content placed above it will. The same block gives the layout's background (`--slide-canvas-bg`) and its side margins (`--body-left` / `--body-right`: the left and right edges of the template's title and text area). Panels used to run past the template's right margin because designers had only the top and bottom. Both are read from chrome.yml, or from the template itself for a template registered before they were recorded.

**Arrows.** Work out each arrow's ends from the box edges, not the box centers, and stop every arrowhead at least 8 px short of the box it points at. On a cycle or loop diagram leave at least 60 px between neighboring boxes. The translator checks every arrow with an arrow marker against the design's boxes, and the translator agent's self-check checks the drawn slide the same way (`scripts/arrow_ends.py`): an arrowhead inside a box or within 6 px of one is a `MAJOR_ARROW_END_AT_BOX` warning on the review page.

## 5. Font handling

- Brand fonts (the client's heading/body typefaces from brand.yml) are referenced by name in `--font-heading` and `--font-sans`.
- The worker assumes the brand font is installed locally during HTML render (Playwright uses the system font stack).
- If the brand font is missing during render, the CSS fallback chain kicks in (`"Segoe UI", -apple-system, sans-serif`).
- The translator agent uses the SAME font name in python-pptx (`run.font.name = "<brand font>"`). If the font isn't installed on the build machine, PowerPoint falls back when the deck is opened — known limitation; INSTALL.md documents the install step for brand fonts.

### Font-size grid (locked)

Font sizes are specified in pixels at the 1280×720 canvas scale. They convert to pt as `pt = px × 72 / 96` (= px × 0.75), and **every size must land on PowerPoint's default grid, floored at 8pt**: `8, 9, 10, 10.5, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 44, 48, 54, 60, 66, 72, 80, 88, 96`. The translator and the finalize step snap to the nearest grid value, but **author on the grid** so the rendered PNG you review matches the shipped PPTX. Use these px values (px → resulting pt):

| Role | px | pt |
|---|---|---|
| Source / footnote (`data-shape-id="source-..."`, `"footnote-..."`) | 12–13px | 9–10pt |
| Chart text: axis, ticks, legend, data labels (`data-shape-id="chart-..."`) | 12–14px | 9–10.5pt |
| Body detail, eyebrows, caps labels, table cells, step numbers | 16px | 12pt |
| Last resort for dense detail, only when it cannot be cut | 14–14.67px | 10.5–11pt |
| Key lines, card titles | 18.67px | 14pt |
| Headings inside the body | 21.33px | 16pt |
| Subtitle / takeaway (template field) | template | template |
| Slide title (template field) | template | template |
| One hero figure | 32px or more | 24pt or more |

- **Body text is 12pt (16px) by default, using 12, 14 and 16pt, at most 3 sizes per slide** (owner's rule, checked on FINAL-CHECK.html and by slide-qc). Dense detail may drop to 11 or 10.5pt only when the content cannot be cut (shown as a note); **under 10.5pt is a Major finding**. Only sources, footnotes and chart text go smaller, and **never under 9pt (12px)**; give those elements a `chart-`, `source-` or `footnote-` shape id so the check recognizes them.
- If content does not fit at 12pt, cut words, drop a column or split the slide first. 10.5pt is the last resort, never below.
- **The takeaway, footnotes and source line are placed by Slide Lab** (owner's rule, 2026-10-08): finalize puts the takeaway directly under the title at the title's text left edge (the template's Subtitle-slot size, else 16pt, regular weight), the source line at the template's source position and the footnotes stacked directly above it (9pt, same left edge), whatever the sketch drew. Draw them where they go so the review picture matches, give footnotes `data-shape-id="footnote-1"`, `"footnote-2"` … and the source line the `footer` template field (or a `source-` shape id), and leave room above the source line for the footnotes.
- Hero numerals may exceed the title range (e.g., 64px ≈ 48pt) — still on the grid.
- Pick a px value from the table; don't free-type arbitrary px that lands between grid points (e.g., 13px → 9.75pt snaps to 10pt anyway, so just use 13px for a 10pt label).

## 6. Icon handling

Icons stay on the existing icon library (`slide-builder/scripts/icon_helper.py` + `slide-builder/icons/`). The worker references icons in HTML by name:

```html
<img src="icons/check-circle.svg" class="icon icon-anchor" alt="">
<!-- OR -->
<i class="icon" data-icon-name="check-circle"></i>
```

The translator agent maps these references to the icon library and inserts them as small picture shapes in the native PPTX. The worker does NOT generate inline SVG paths for icons; they reference the library.

Standard icon sizes:
- Anchor icons (recommendation indicator, status glyph): `24px–32px`
- Inline icons (within body text, status indicator): `16px–20px`
- Decorative icons: `≤24px`
- Hero icons (single icon dominates a card): `40px–48px`

Icon CSS rules:
- `aria-hidden="true"` on every decorative icon
- Icons inherit `currentColor` so brand-variable color cascades work
- Icons positioned via flexbox or absolute, never floated

## 7. CSS feature kill-list

These CSS features DO NOT translate cleanly to python-pptx. The worker MUST NOT use them in the body zone (chrome zones are unaffected since they don't get translated):

| Feature | Why forbidden |
|---|---|
| `radial-gradient`, `conic-gradient`, layered or repeating gradients | No faithful native equivalent; the translator flattens them to one color (QC R4.4, Major). A single `linear-gradient` does translate, to a native gradient fill with the same stops and direction, but keep body fills flat unless the design calls for one. |
| `box-shadow` (drop shadows on shapes) | python-pptx shadow API is partial; visual fidelity not preserved. |
| `text-shadow` | Not supported in python-pptx text runs. |
| `filter: blur()`, `filter: drop-shadow()`, any CSS filter | Not supported in python-pptx. |
| `backdrop-filter` | Not supported. |
| `mix-blend-mode`, `background-blend-mode` | Not supported. |
| `clip-path`, `mask`, `mask-image` | Not supported. |
| CSS `transform: rotate/skew` on text containers | python-pptx can rotate but text within rotated containers loses readability. Avoid. |
| `opacity` < 1 on text elements | Translates to transparency in python-pptx, often reducing legibility. Avoid on text; allowed on shape fills with explicit color reduction instead. |
| Any `@font-face` rule, the brand fonts included | Name the font in `font-family` and let the installed font draw it. Never point a font at a file: a designer once loaded the brand family from a copied file that held its narrow face, so the approved sketch was a quarter narrower than the finished slide (2026-10-08). Slide Lab's renderer removes any `@font-face` rule that names an installed font and warns (`FONT_FACE_REMOVED`); for a font that is not installed, Slide Lab supplies the files, not the designer. |
| Animations (`@keyframes`, `transition`, etc.) | Rendered output is a static PNG; animations have no effect. Use static visual hierarchy instead. |
| `position: fixed` (any element) | Doesn't make sense on a fixed-size canvas; will produce unexpected results. |
| External CSS frameworks (Bootstrap, Tailwind, etc.) | Render pipeline doesn't load external resources except the `brand.css` injected by Slide Lab. |

**Permitted CSS that translates cleanly:**
- `background-color` (solid only) → python-pptx solid fill
- `color` → python-pptx text color
- `border` (solid, single-side or all-sides) → python-pptx line
- `border-radius` (any radius) → python-pptx ROUNDED_RECTANGLE with corner_radius_emu
- `padding`, `margin` → translates to position math
- `display: flex`, `display: grid`, `display: block` → translates to absolute positioning in python-pptx
- `font-family`, `font-size`, `font-weight`, `font-style`, `letter-spacing`, `line-height`, `text-align`, `text-transform` → all translate to python-pptx text run properties
  - `font-weight` ships as regular (under 600) or bold (600 and up). PowerPoint has only bold on or off, so 800 and 900 come out as the family's bold, not a heavier face; design hierarchy with size and color, not with 800 versus 700.
- `position: absolute`, `position: relative` → translates to absolute x/y positioning

If the worker reaches for a forbidden feature, the worker prompt says: "If you genuinely need a forbidden feature for design impact, route to the direct path (native-only) or flag the slide as requiring an image-embed exception."

## 8. HTML file structure

Every sketch-path worker HTML file follows this exact structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Slide N — option X</title>
<style>
  /* CSS variables block (inlined from brand.css; injected by build_deck.py into _context.md) */
  :root {
    --brand-primary: #4D148C;
    /* ... (full block from §4 above) */
  }
  /* CSS reset (verbatim from §3) */
  *, *::before, *::after { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body { font-family: var(--font-sans); color: var(--brand-text-primary); font-size: 16px; line-height: 1.5; }

  /* Canvas */
  .slide-canvas { width: 1280px; height: 720px; position: relative; overflow: hidden; box-sizing: border-box; background: var(--slide-canvas-bg, #FFFFFF); }

  /* Worker-specific styles for THIS slide */
  /* ... worker writes their slide-specific CSS here ... */
</style>
</head>
<body>
<div class="slide-canvas">

  <!-- Chrome top: title bar (style approximates template; actual title text re-used as data field for placeholder population) -->
  <div class="chrome-top" style="position: absolute; top: 0; left: 0; right: 0; height: var(--body-top);">
    <h1 class="slide-title" data-template-field="title">[Slide title text]</h1>
    <p class="slide-subtitle" data-template-field="subtitle">[So-what text]</p>
  </div>

  <!-- Body zone: worker's consulting-grade content (this is what gets translated to native shapes) -->
  <div class="body-zone" style="position: absolute; top: var(--body-top); left: 0; right: 0; bottom: calc(720px - var(--body-bottom));">
    <!-- worker's body content -->
  </div>

  <!-- Chrome bottom: footer band (style approximates template; actual footer text re-used as data field) -->
  <div class="chrome-bottom" style="position: absolute; left: 0; right: 0; bottom: 0; height: calc(720px - var(--body-bottom));">
    <p class="slide-footer" data-template-field="footer">[Footer text]</p>
    <p class="slide-page-number" data-template-field="page_number">[N]</p>
  </div>

</div>
</body>
</html>
```

**The `data-template-field` attribute** is the critical contract between worker and translator. Any element with this attribute has its text content extracted as a data field and written into the corresponding template placeholder by the translator agent — NOT positioned as a freeform shape.

Supported field names:
- `title` → template title placeholder
- `subtitle` → template subtitle/so-what placeholder
- `footer` → template footer placeholder
- `page_number` → template page-number placeholder

The translator agent's contract (Spec 4) details the extraction logic.

## 9. Worker self-check requirement

The HTML phase is not optional: the worker MUST render their HTML and read the rendered PNG before declaring the option done. This is the SEEING mechanism. Workers that skip the render+read step produce sterile output.

Worker prompt directive (enforced in `slide-builder-worker.md`):

> Before emitting `# OPTION_A_DONE`, run the HTML render pipeline (`py -3 scripts/render_html.py option_A.html option_A.sketch.png`; the canvas is 1280x720 by default) and READ the rendered PNG. Describe in one sentence what you see (e.g., "Anchor row visible at row 3 with rounded card + purple stripe + checkmark icon; comparison rows below with subtler weight"). If the render doesn't match your intent, fix the HTML and re-render before emitting done.

This is enforced via `_context_ack.txt` (existing pattern from Gap 3 in prior work). The acknowledgment line cites both the constraint that informed the design AND the visual confirmation after render.

## 10. Out of scope for this spec

- Specific shape-language treatments per pattern (handled by SPEC.md's reference to `reference/layouts.md` and `reference/anti-patterns.md`)
- Color translation math (Spec 2)
- Geometry conversion math (Spec 3)
- Translator worker contract details (Spec 4)
- Fidelity measurement (Spec 5)
- QC rules (Spec 6)
- Schema versioning (Spec 7)
- Rollback flag (Spec 8)

Each of those is its own locked spec in this directory.

---

**This SPEC.md is the contract between worker, translator, and render pipeline.** Any deviation requires a documented exception in the slide's `_context_ack.txt`.
