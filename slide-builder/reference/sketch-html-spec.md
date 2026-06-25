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
- Background color defaults to `#FFFFFF`; the master template's true background renders through this layer because the body PNG only covers the body zone.

**Why this size:** matches PowerPoint's default 16:9 slide dimensions exactly. Geometry math becomes 1:1 (HTML pixel = PPT EMU/9525). No scaling factors. Worker can position elements using coordinates that map directly to chrome.yml pixel values.

## 2. Zone structure inside the canvas

The 1280×720 canvas has three logical zones. Coordinates come from the registered template's `chrome.yml`:

```
┌─────────────────────────────────────────────┐  y=0
│  CHROME TOP                                 │
│  (title bar, subtitle bar, accent stripe)   │
├─────────────────────────────────────────────┤  y=body_top_y_px (e.g., 149)
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
  --font-heading: "FedEx Sans", "Segoe UI", -apple-system, sans-serif;
  --font-sans: "FedEx Sans", "Segoe UI", -apple-system, sans-serif;
  --font-mono: ui-monospace, "Consolas", monospace;

  /* Canvas */
  --slide-canvas-bg: #FFFFFF;

  /* Body zone bounds (from chrome.yml) */
  --body-top: 149px;
  --body-bottom: 667px;
  --body-height: 518px;
  --body-width: 1280px;
}
```

The `:root` block is generated by `register_template.py commit` from `brand.yml` + `chrome.yml` and saved as `<template-stem>/brand.css`. The worker references this file in their HTML:

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

The `build_deck.py` Stage 1 generates `_context.md` with the `:root` block inlined so the worker can copy it directly into their HTML without an external file dependency.

## 5. Font handling

- Brand fonts (e.g., FedEx Sans, Graphik) are referenced by name in `--font-heading` and `--font-sans`.
- The worker assumes the brand font is installed locally during HTML render (Playwright uses the system font stack).
- If the brand font is missing during render, the CSS fallback chain kicks in (`"Segoe UI", -apple-system, sans-serif`).
- The translator agent uses the SAME font name in python-pptx (`run.font.name = "FedEx Sans"`). If the font isn't installed on the build machine, PowerPoint falls back when the deck is opened — known limitation; INSTALL.md documents the install step for brand fonts.
- **Font sizes are specified in pixels at the 1280×720 canvas scale**, NOT in pt. Conversion to pt for python-pptx: `pt = px * 72 / 96` (e.g., 16px = 12pt).

Standard font sizes (consulting-grade typography):
- Slide title: `22px–28px`, weight 700
- Subtitle / so-what: `14px–16px`, weight 500
- Body / card title: `13px–16px`, weight 600
- Body text / bullets: `11px–13px`, weight 400
- Footnote / source / page #: `9px–10px`, weight 400
- Eyebrow / caps label: `10px–11px`, weight 600, letter-spacing 0.05em, text-transform uppercase

**No font sizes below 9px.** No font sizes above 32px (except specific hero numerals).

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
| `linear-gradient`, `radial-gradient`, any `<gradient-image>` | python-pptx has no native gradient fill on shapes. Translator would have to render the gradient region as image — loss of editability. |
| `box-shadow` (drop shadows on shapes) | python-pptx shadow API is partial; visual fidelity not preserved. |
| `text-shadow` | Not supported in python-pptx text runs. |
| `filter: blur()`, `filter: drop-shadow()`, any CSS filter | Not supported in python-pptx. |
| `backdrop-filter` | Not supported. |
| `mix-blend-mode`, `background-blend-mode` | Not supported. |
| `clip-path`, `mask`, `mask-image` | Not supported. |
| CSS `transform: rotate/skew` on text containers | python-pptx can rotate but text within rotated containers loses readability. Avoid. |
| `opacity` < 1 on text elements | Translates to transparency in python-pptx, often reducing legibility. Avoid on text; allowed on shape fills with explicit color reduction instead. |
| Custom web fonts loaded via `@font-face` (other than the brand fonts) | Worker assumes only brand fonts are installed. Loading additional web fonts at render time is non-deterministic. |
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

> Before emitting `# OPTION_A_DONE`, run the HTML render pipeline (`scripts/render_html.py --in option_A.html --out option_A.png --canvas 1280x720`) and READ the rendered PNG. Describe in one sentence what you see (e.g., "Anchor row visible at row 3 with rounded card + purple stripe + checkmark icon; comparison rows below with subtler weight"). If the render doesn't match your intent, fix the HTML and re-render before emitting done.

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
