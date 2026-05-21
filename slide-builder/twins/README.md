# Slide Lab Twins

Hand-built PPTX twins of the HTML pattern library. Compose decks by substituting text into copies of the twins — no CSS parsing at build time.

## What this is

The pattern library at `_pattern-library/*.html` is the design spec; each approved pattern has a 1:1 hand-built PPTX twin at `_renders/twins/NN_<slug>.pptx`. The composer copies a twin and replaces text/fill by `shape.name` (which mirrors the HTML's `data-shape-id`). The translator applies small per-twin adjustments (text, fill, position, font). There is no runtime HTML/CSS parser.

## Quick start

1. Write a YAML deck spec **in your project folder** (not inside this skill — see "Where your decks live" below). Reference `_example-deck.yaml` for the shape:
   ```yaml
   output: my-deck.pptx           # relative to this YAML's directory
   slides:
     - pattern: 19_cover-split-panel
       overrides:
         cover-deck-title: Pilot Recap
         cover-tagline: Four weeks, six metrics.
   ```
2. Run the composer from the slide-builder dir, passing the full path to your YAML:
   ```
   python -m twins.deck_spec "C:/Users/you/path/to/my-deck.yaml"
   ```
3. PPTX appears at the `output:` path, resolved relative to the YAML's directory.

## Where your decks live

**Deck YAMLs and their PPTX outputs are project artifacts, not skill artifacts.** Put them in your project/session folder (e.g., next to a narrative brief), not in this skill's `twins/` directory. The skill stays brand-and-project-agnostic; your project owns its own decks.

Recommended layout:
```
your-project/
├── narrative-brief.md
├── deck-spec.yaml          ← the spec
└── deck-spec.pptx          ← the output (composer writes here)
```

## How it works

**HTML patterns** (`_pattern-library/*.html`) — 85 approved 1280×720 mockups, each stamped with `data-shape-id` attributes following `_pattern-library/SHAPE-ROLES.md`. These are the design spec; humans iterate here.

**PPTX twins** (`twins/builders/build_NN.py` → `_renders/twins/NN_*.pptx`) — one Python builder per pattern. Each builder calls `helpers.py` for chrome/title/footer/convergence, then adds its body-specific shapes with explicit pixel coordinates. Every `slide.shapes` shape gets a `name` that matches the HTML's `data-shape-id`. Run a builder directly with `python -m twins.builders.build_NN` to regenerate its twin.

**The composer** (`twins/composer.py`) — `compose_deck(out_path, slides=[{pattern, overrides}, ...])`. For each slide: load the twin PPTX, find shapes by name, substitute text (preserving font properties) or recolor fills. Missing shape ids are logged and skipped (find-or-skip, never raise). Single-slide and multi-slide modes; multi-slide clones slide XML into one deck.

**The translator** (`twins/translator.py`) — `apply(twin_path, adjustments)` for small adjustments to a twin: text, fill, left/top/width/height, font size/color/bold/italic/align. Caller supplies the adjustments dict explicitly — no CSS, no layout inference. Used when you move or restyle a shape inside a twin without rebuilding the whole builder.

## Common tasks

- **Build a deck from a spec** — `python -m twins.deck_spec twins/_example-deck.yaml`
- **Build a single slide programmatically** — `from twins.composer import compose_deck; compose_deck(out_path, slides=[{"pattern": "12_kpi-tile-dashboard", "overrides": {"title": "...", "metric-1-value": "62%"}}])`
- **Edit text or color in an existing twin** — `from twins.translator import apply; apply("path/to/twin.pptx", {"title": {"text": "New title", "font_color": "#1A1A2E"}, "brand-rule": {"left": 80, "width": 120}})`
- **Rebuild a twin from its builder** — `python -m twins.builders.build_NN` (writes to `_renders/twins/NN_*.pptx`)
- **List available patterns** — `ls _pattern-library/*.html` or read `_pattern-library/INDEX.md`
- **Look up shape ids for a pattern** — `_pattern-library/SHAPE-ROLES.md` is the canonical vocabulary

## Architecture notes

- **1:1 HTML↔PPTX pairs** — 85 patterns, 85 builders, 85 twins.
- **One-way sync** — HTML is the design spec, PPTX twin is the client deliverable. When the HTML changes, edit the builder (or apply a translator adjustment) and re-emit the twin. Never edit the twin freely in PowerPoint as the source of truth.
- **Find-or-skip overrides** — the composer logs unknown shape ids and continues. ~11 patterns lack `draft-badge`; ~9 lack `subtitle`; deck specs that target either still build cleanly against patterns that have them.
- **Universal invariants live in `helpers.py`** — `add_chrome`, `add_title_block`, `add_footer`, `add_convergence` plus the brand palette (`BRAND_PRIMARY`, `BRAND_ACCENT`, etc.) and CSS-px-to-EMU/pt converters. Every builder imports from here.
- **Composer string semantics** — `"text"` or `{"text": "..."}` substitute text; `{"fill": "#RRGGBB"}` recolors; both keys can co-occur.

## Client templates: what the composer does and doesn't do

When a deck spec sets `client_template:` to a path of a `.pptx` or `.potx`, the composer rebuilds the deck on top of that template. This is what changes:

**What you get automatically:**

- **Theme colors flow through.** The composer extracts `dk1/lt1/dk2/lt2/accent1-6` from the template's `theme1.xml`, picks the most-saturated dark color as the brand primary and the most-saturated contrasting color as the accent (handles templates that put brand in accent1 instead of dk2), and remaps every literal Slide Lab color in the twin to the client equivalent.
- **Theme fonts flow through.** Inter is swapped for the template's `minorFont` everywhere.
- **Per-pattern layout routing.** Each twin pattern lands on a meaningful layout from the template: covers on a `Title Slide` layout, section dividers on `Section Divider`, hero quotes on `Statement`, closings on `Closing`, everything else on `Text Only` / `Text` / `Content`. Layout names are matched as substrings, so templates that follow PowerPoint's standard naming work out of the box.
- **Master chrome inherits.** Logos, footer text, slide numbers from the template's master appear on every slide. The twin's own chrome (`accenture-tag`, `draft-badge`, `footer-*`) is stripped.
- **Title binds to the template's TITLE placeholder.** When the chosen layout has a proper TITLE placeholder, the slide's title text is pushed into it — so switching the layout in PowerPoint moves the title with it. When the layout has no TITLE placeholder (e.g., FedEx's `Closing`), the twin's title shape is kept instead.
- **Sections cleared.** Any `<p:sectionLst>` shipped with the template is removed so the slide-panel sidebar shows a flat slide list.

**What stays opinionated (and you should know):**

- **Subtitle and brand-rule are dropped when the title goes into a layout placeholder.** The template's title placeholder is typically much taller than the twin's title box and would overlap the twin's subtitle. The convergence band at the bottom of each pattern carries the so-what; the subtitle is redundant in templated mode. (If you want the subtitle to survive, edit `_CHROME_SHAPE_IDS_TO_STRIP` in `composer.py`.)
- **Body shapes (cards, pillars, hero statements, convergence bands, etc.) are NOT bound to placeholders.** They're free shapes placed on top of the layout. Switching layouts in PowerPoint moves the title but leaves the body shapes where they are.
- **Layouts are picked by name substring.** If your template uses non-English names ("Portada", "Conclusión") or wildly custom names ("v3_FINAL"), routing falls back to blank. Future work: per-slide `layout:` override in the YAML.
- **Brand colors are picked from saturated palette colors.** If the entire palette is muted/neutral, the picker falls back to `dk2`/`lt2` as PowerPoint convention dictates.

Inspect any template's theme + layouts with:
```
python -m twins._inspect_template "path/to/template.pptx"
```
