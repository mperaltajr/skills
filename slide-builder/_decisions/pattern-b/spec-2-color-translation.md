# Pattern B — Color translation spec

> How brand colors flow from `brand.yml` → HTML/CSS render → native python-pptx, with gamut validation and gradient handling.

**Status:** locked 2026-06-16. Depends on SPEC.md (§4 brand-variable injection).

---

## 1. The flow

```
brand.yml (human-authored at registration)
   │
   │  primary_hex, accent_hex, cover_bg_hex, dark_bg_hex
   ▼
register_template.py commit
   │
   │  generates brand.css (CSS variables) for HTML render
   │  generates theme.json (existing) for python-pptx
   ▼
HTML worker writes content with var(--brand-primary) etc.
   │
   │  Playwright renders HTML → PNG at 1280×720
   ▼
Translator agent reads HTML + PNG + brief
   │
   │  extracts color values from HTML inline styles / computed CSS
   │  converts hex → python-pptx RGBColor for native shapes
   ▼
finalize_deck.py applies theme remap (existing path)
   │
   │  uses theme.json color_map for any literal Slide Lab brand hexes
   ▼
Final PPTX shapes have RGBColor values matching the HTML render
```

## 2. Hex → RGBColor conversion

Standard formula. No surprises:

```python
def hex_to_rgbcolor(hex_str: str) -> RGBColor:
    """Convert '#4D148C' or '4D148C' to python-pptx RGBColor."""
    s = hex_str.lstrip('#').upper()
    if len(s) != 6:
        raise ValueError(f"hex must be 6 chars after stripping '#'; got {hex_str!r}")
    try:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
    except ValueError as exc:
        raise ValueError(f"hex contains non-hex chars: {hex_str!r}") from exc
    return RGBColor(r, g, b)
```

This goes in `twins/client_theme.py` as a public helper (it doesn't exist there today; need to add). The existing `_hex_to_rgb_tuple` in `finalize_deck.py` does the same thing but returns a tuple — convert internal callers to use the new `hex_to_rgbcolor` helper to centralize.

## 3. CSS `rgb()` and `rgba()` → RGBColor

The translator may encounter CSS colors in non-hex form (e.g., `rgb(77, 20, 140)`, `rgba(77, 20, 140, 0.85)`). Convert:

```python
def css_color_to_rgbcolor(css_value: str) -> tuple[RGBColor, float]:
    """
    Parse a CSS color value. Returns (RGBColor, alpha) where alpha is 0.0-1.0.
    Supports: hex (#RGB, #RRGGBB), rgb(r, g, b), rgba(r, g, b, a).
    """
    # ... (regex match for hex / rgb / rgba; raise on unsupported)
```

**Alpha handling:** python-pptx supports fill transparency via the `<a:alpha>` element on `solidFill`. The translator may set this where alpha < 1. **But:** the locked QC rule R4.2 (severity: Major) flags any alpha-on-text. Translator strips alpha from text-element colors before writing.

## 4. CSS `var(--brand-primary)` → RGBColor

When the HTML uses CSS variables (the SPEC.md preferred pattern), the translator must resolve the variable to its concrete value. Two ways:

**(A) Static resolution from `brand.css`** — translator reads the `:root` block, builds a lookup dict, resolves `var(--brand-primary)` → `#4D148C` before converting to RGBColor.

**(B) Computed-style resolution via headless browser** — translator runs the same Playwright instance, queries `getComputedStyle()` on the rendered element, gets the resolved color value, converts.

**Locked approach: (A) static resolution.** Faster, deterministic, no second browser run. The `brand.css` file IS the source of truth for variable values (generated at registration time from `brand.yml`).

The translator's `resolve_css_var(var_name, brand_css_dict) -> str` helper performs this lookup. Brand css dict is loaded once per slide build.

## 5. Gamut validation

Brand colors must satisfy three constraints (existing checks in `finalize_deck.py`; reused here):

1. **Primary/accent distance:** RGB Euclidean ≥ 30. Existing `_rgb_distance` and `PrimaryAccentCollisionError` enforce this (locked in earlier work).
2. **No pure black or pure white as brand primary/accent.** Both extremes are reserved for text/background defaults; brand colors must be chromatic.
3. **Brand colors used on text must contrast with their background** ≥ 4.5:1 (WCAG AA). New check added under Pattern B because brand.yml colors land directly in HTML text colors now.

WCAG contrast calculation:

```python
def wcag_contrast(fg_hex: str, bg_hex: str) -> float:
    """Calculate WCAG 2.1 contrast ratio between two hex colors."""
    def luminance(hex_str: str) -> float:
        rgb = [int(hex_str.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        rgb = [
            (c / 12.92) if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            for c in rgb
        ]
        return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    l1, l2 = luminance(fg_hex), luminance(bg_hex)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)
```

If brand primary text on brand accent background contrast < 4.5:1, emit a registration-time warning: *"Brand primary `#4D148C` on accent `#FF6600` has contrast 3.2:1 (below WCAG AA 4.5:1). Slides using this combination for text may be hard to read on projection."*

Non-blocking (Major in REVIEW.html), not Critical. Some brand systems intentionally use low-contrast pairings.

## 6. Gradient handling

CSS gradients (`linear-gradient`, `radial-gradient`) are on the SPEC.md kill-list — workers must not use them in the body zone. But the chrome zones (template-inherited) may have them, and HTML rendered for context might still produce them.

Translator behavior:
- If a gradient appears in a chrome zone → fine; chrome doesn't get translated to native shapes.
- If a gradient appears in the body zone → translator raises a warning, picks the gradient's middle stop as a solid approximation, and surfaces the slide in REVIEW.html with QC rule R4.4 (severity: Major).

Approximation logic:

```python
def gradient_to_solid(gradient_css: str) -> str:
    """Pick the middle color stop from a linear-gradient as a solid approximation."""
    # parse 'linear-gradient(180deg, #4D148C 0%, #FF6600 100%)'
    # return the midpoint color (e.g., #A93547 in this case — mechanical mix)
    stops = parse_gradient_stops(gradient_css)
    if len(stops) == 1:
        return stops[0].color
    # mix all stops with equal weight
    return mix_hexes([s.color for s in stops])
```

Alternative path (opt-in per slide): the translator embeds the gradient region as a small image instead of approximating. This requires an explicit `# GRADIENT_AS_IMAGE: <region>` marker in the worker HTML. Default behavior is solid approximation.

## 7. `brand.css` generation at register_template commit time

`register_template.py commit` currently writes `brand.yml` + `theme.json` + `chrome.yml`. Pattern B adds `brand.css`:

```python
def write_brand_css(path: Path, *,
                    primary_hex: str, accent_hex: str,
                    cover_bg_hex: str, dark_bg_hex: str,
                    font_heading: str, font_body: str,
                    chrome_geometry: dict) -> None:
    """
    Generate brand.css containing the :root CSS variables block.
    Read by the worker's HTML at render time; read by the translator
    for var(--brand-*) resolution.
    """
    content = f"""
:root {{
  /* Brand colors */
  --brand-primary: #{primary_hex.upper()};
  --brand-accent: #{accent_hex.upper()};
  --brand-cover-bg: #{cover_bg_hex.upper()};
  --brand-dark-bg: #{dark_bg_hex.upper()};

  /* Derived */
  --brand-primary-soft: {mix_hex(primary_hex, "FFFFFF", 0.30)};
  --brand-accent-soft: {mix_hex(accent_hex, "FFFFFF", 0.60)};
  --brand-text-primary: #1A1A1A;
  --brand-text-secondary: #5F5E5A;
  --brand-text-tertiary: #888780;
  --brand-border-light: #D3D1C7;
  --brand-divider: #E1E1E6;

  /* Fonts */
  --font-heading: "{font_heading}", "Segoe UI", -apple-system, sans-serif;
  --font-sans: "{font_body}", "Segoe UI", -apple-system, sans-serif;
  --font-mono: ui-monospace, "Consolas", monospace;

  /* Canvas */
  --slide-canvas-bg: #FFFFFF;

  /* Body zone bounds (from chrome.yml::default_content_layout) */
  --body-top: {chrome_geometry['body_top_y_px']}px;
  --body-bottom: {chrome_geometry['body_bottom_y_px']}px;
  --body-height: {chrome_geometry['body_bottom_y_px'] - chrome_geometry['body_top_y_px']}px;
  --body-width: 1280px;
}}
"""
    path.write_text(content, encoding="utf-8")
```

Written to `<template-stem>/brand.css` next to existing `brand.yml`. The contents are also inlined into each slide's `_context.md` so the worker can copy-paste into a self-contained HTML file.

## 8. `mix_hex` helper

Already exists in `twins/client_theme.py` as `_mix_hex`. Make it public (`mix_hex`) for reuse in `register_template.py::write_brand_css`. Signature unchanged:

```python
def mix_hex(a_hex: str, b_hex: str, b_weight: float) -> str:
    """
    Mix two hex colors. b_weight is fraction of b in the result.
    mix_hex('#000000', '#FFFFFF', 0.5) → '#808080'.
    """
```

## 9. Integration points

| File | Change |
|---|---|
| `twins/client_theme.py` | Add public `hex_to_rgbcolor()`, `css_color_to_rgbcolor()`, `resolve_css_var()`, `wcag_contrast()`. Make `mix_hex` public. |
| `scripts/register_template.py` | Add `write_brand_css()` call in `_write_outputs()` after `write_brand_yml`. Add WCAG contrast warning when primary-on-accent < 4.5:1. |
| `scripts/build_deck.py` | Inline `brand.css` contents into `_context.md` per slide so workers have self-contained styles. |
| (new) Translator agent | Resolve `var(--brand-*)` via static lookup; convert hex/rgb/rgba to RGBColor; handle gradients per §6. |

## 10. Out of scope

- Color naming or semantic conventions for non-brand colors (e.g., status reds, success greens) — these stay hardcoded in worker HTML using standard hexes; not template-variable
- Light/dark mode handling — Slide Lab outputs are PowerPoint slides, not dark-mode-aware UI. Single light theme only.
- Color blindness simulation — out of scope for v0

---

**Color translation is mechanical** with the kill-list in place. The risk is reduced to: "workers respect the kill-list" (enforced via `_context_ack.txt` per SPEC.md §9) and "WCAG contrast is acceptable on this brand" (warned at registration).
