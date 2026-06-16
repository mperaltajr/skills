# Pattern B — Translator worker contract

> Defines the `slide-builder-translator` agent: input, output, validation, dispatch, editability invariant, prompt structure.

**Status:** locked 2026-06-16. Depends on SPEC.md, Spec 2 (color), Spec 3 (geometry), Decision 3 (per-slide dispatch), Decision 4 (editability), Decision 5 (QC severities).

---

## 1. Role in the pipeline

```
Stage 2: workers write option_A.html, option_B.html, option_C.html per slide
Stage 2.5: Playwright renders each HTML → PNG
Stage 3: user picks per-slide options in REVIEW.html
Stage 3.5 (NEW — this spec): translator agent runs per picked slide
   → reads picked HTML, its PNG, the brief, brand.yml, chrome.yml, _context.md
   → emits option_X_native.py (python-pptx code) with shape coordinates
       extracted via headless-browser computed-style + EMU conversion
Stage 4: finalize_deck.py executes the .py file → grafted PPTX
```

One translator dispatch per picked slide. NOT batched (per Decision 3 — defer batching to separate workstream).

## 2. Translator agent definition

Lives at `%USERPROFILE%\.claude\agents\slide-builder-translator.md`. Source-of-truth copy in `slide-builder/agents/slide-builder-translator.md` (matches the worker pattern; INSTALL.md gets a Step 6.5 to copy).

Frontmatter:

```yaml
---
name: slide-builder-translator
description: Per-slide translator for the slide-builder skill's Pattern B path. Reads ONE picked option_X.html + its rendered PNG + brief + brand context, produces a native python-pptx script (option_X_native.py) that visually matches the HTML render. Dispatched per slide (not batched) after user picks in REVIEW.html. Does NOT orchestrate the deck.
tools: Bash, Read, Glob, Grep, Write, Edit
---
```

## 3. Input contract

The translator receives ONE message from the parent session containing:

```
SLIDE: N
PICKED_OPTION: A   (or B, or C)
HTML_PATH: <out_dir>/slide_NN/option_A.html
PNG_PATH: <out_dir>/slide_NN/option_A.png
BRIEF_PATH: <out_dir>/_brief.md          (the gated narrative brief)
CONTEXT_PATH: <out_dir>/slide_NN/_context.md
BRAND_YML: <template-stem>/brand.yml
BRAND_CSS: <template-stem>/brand.css
CHROME_YML: <template-stem>/chrome.yml
THEME_JSON: <template-stem>/theme.json
TEMPLATE_PPTX: <absolute path to .pptx>
OUTPUT_PY: <out_dir>/slide_NN/option_A_native.py
OUTPUT_PPTX: <out_dir>/slide_NN/option_A_native.pptx (path the .py must save to)
LAYOUT_NAME: <name of the slide layout from _meta.json[slide_N][layout]>
```

The translator reads these files in order:
1. `_context.md` (canonical reference + design rules + constraint set)
2. `_brief.md` (full deck context + this slide's evidence/title/so-what)
3. `option_A.html` (the picked HTML — what the user approved)
4. `option_A.png` (the rendered visual target — what the native PPTX must match)
5. `brand.css` (CSS variable resolution table)
6. `chrome.yml` (layout geometry, EMU + px values for this slide's layout)

If any required file is missing, translator emits `# TRANSLATOR_BLOCKED: missing <file>` and stops. Parent session reports the block.

## 4. Output contract

Translator produces exactly two files:

**Primary output:** `option_A_native.py` (native python-pptx script). Structure:

```python
# CONTEXT_READ: Translator picked the anchor-row treatment to match the HTML's hybrid-recommendation framing per Decision 5 R4.7 editability invariant.
# BRIEF_IS_AUTHORITATIVE: True
# PATTERN: B-translated
# HTML_SOURCE: option_A.html (sha256: <hash>)
# PNG_TARGET: option_A.png (sha256: <hash>)

from pathlib import Path
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
# ... (standard imports)

def build():
    prs = Presentation()
    # Use template chrome — graft onto the registered template at finalize time
    slide_layout = prs.slide_layouts[0]  # placeholder; finalize_deck handles graft
    slide = prs.slides.add_slide(slide_layout)

    # ===== TEMPLATE-FIELD POPULATION (chrome top) =====
    # Title and subtitle go into INHERITED PLACEHOLDERS (not freeform shapes)
    # finalize_deck.py::_populate_layout_placeholders handles this via the
    # template-field data extracted below:
    # __template_fields__ = {
    #     "title": "Approve a hybrid resource model to stand up the GPO inside 90 days",
    #     "subtitle": "Stand up week 1 / Pair with vendor / Sequence over 90 days",
    #     "footer": "FedEx OTC | Confidential | 16/16",
    #     "page_number": "16",
    # }

    # ===== BODY ZONE — NATIVE SHAPES =====
    # All coordinates are EMU. Body zone bounds (per chrome.yml):
    #   body_top_emu = 1419225 (149px)
    #   body_bottom_emu = 6354675 (667px)

    # Shape: anchor-row container for the Hybrid recommendation
    # (extracted from HTML element with data-shape-id="row-hybrid")
    row_hybrid = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Emu(762000),   # x=80px
        Emu(3000000),  # y=315px (inside body zone)
        Emu(10668000), # w=1120px
        Emu(571500),   # h=60px
    )
    row_hybrid.adjustments[0] = 0.6   # border-radius: 18px on a 60px-tall card
    row_hybrid.fill.solid()
    row_hybrid.fill.fore_color.rgb = RGBColor(0xEE, 0xED, 0xFE)  # --brand-primary-soft
    row_hybrid.line.color.rgb = RGBColor(0x7F, 0x77, 0xDD)
    row_hybrid.line.width = Emu(7620)  # 0.8px

    # Shape: accent stripe on the recommended row
    stripe = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Emu(762000),   # x=80px (same as row left)
        Emu(3000000),  # y=315px (same as row top)
        Emu(28575),    # w=3px
        Emu(571500),   # h=60px (same as row)
    )
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = RGBColor(0x53, 0x4A, 0xB7)
    stripe.line.fill.background()  # no border

    # Text frame inside the anchor row — text content from data-template-field-text on shape
    row_hybrid.text_frame.text = "Hybrid model ★"
    # ... (font, size, weight per CSS computed style)

    # ... (additional shapes for other body-zone elements)

    # Save to the path specified by the parent session
    out_path = Path(__file__).resolve().parent / "option_A_native.pptx"
    prs.save(str(out_path))

if __name__ == "__main__":
    build()
```

**Secondary output:** `option_A_translation_report.json` — machine-readable artifact for QC:

```json
{
  "slide_n": 16,
  "option_letter": "A",
  "html_source": "option_A.html",
  "png_target": "option_A.png",
  "html_sha256": "...",
  "png_sha256": "...",
  "template_fields": {
    "title": "Approve a hybrid resource model to stand up the GPO inside 90 days",
    "subtitle": "Stand up week 1 / Pair with vendor / Sequence over 90 days",
    "footer": "FedEx OTC | Confidential | 16/16",
    "page_number": "16"
  },
  "shape_count": 17,
  "shapes_with_data_shape_id": 17,
  "shapes_without_data_shape_id": 0,
  "translator_self_check": {
    "ssim_per_zone": {
      "title": 0.94,
      "subtitle": 0.92,
      "body": 0.91,
      "footer": 0.95
    },
    "lowest_zone_score": 0.91,
    "pass": true
  },
  "warnings": []
}
```

The report is read by `finalize_deck.py` and `build_review.py` to surface QC results.

## 5. Template fields — the chrome contract

Per the chrome-handling clarification (Option I, locked), title/subtitle/footer/page-number text are NEVER created as freeform shapes by the translator. They are extracted from the HTML and written as data fields to be populated into the template's inherited placeholders by `finalize_deck.py::_populate_layout_placeholders()` (existing function, already used today for native path).

Extraction logic (in the translator's prompt):

```
1. Find every HTML element with attribute `data-template-field`
2. The attribute value is the placeholder type: title, subtitle, footer, page_number
3. Extract `el.textContent.trim()` as the value
4. Emit a `__template_fields__` dict (as a structured comment) in option_A_native.py
   AND in the translation report JSON
5. Do NOT generate any python-pptx code for the title/subtitle/footer/page_number shapes
```

The native script's body code creates ONLY body-zone shapes. The chrome zones are template-inherited.

`finalize_deck.py::graft_and_theme` already handles the population from the brief's title/subtitle fields. Update needed: also accept `__template_fields__` from the translator script as a higher-priority source.

## 6. Body-zone shape extraction

The translator's main task: walk HTML elements with `data-shape-id` (within the body zone only), use Playwright `getComputedStyle()` to read post-layout properties, emit a python-pptx call per shape.

**Required computed-style properties to capture per shape:**

| CSS property | Used for | python-pptx target |
|---|---|---|
| `getBoundingClientRect()` x, y, width, height | Position + size | `shape.left/top/width/height` (in EMU via px_to_emu) |
| `backgroundColor` | Solid fill | `shape.fill.fore_color.rgb` |
| `borderRadius` | Corner radius | `shape.adjustments[0]` via `css_radius_to_pptx_adjustment` |
| `borderColor`, `borderWidth`, `borderStyle` | Stroke | `shape.line.color.rgb`, `shape.line.width` |
| `color` | Text color | `run.font.color.rgb` |
| `fontFamily` | Text font | `run.font.name` |
| `fontSize` | Text size | `run.font.size = Pt(px * 72/96)` |
| `fontWeight` | Bold | `run.font.bold = (weight >= 600)` |
| `fontStyle` | Italic | `run.font.italic = (style == "italic")` |
| `textTransform` | Caps | manual case conversion before setting text |
| `textAlign` | Alignment | `paragraph.alignment` |
| `letterSpacing` | Tracking | `run.font.spc` (in 100ths of point) |

If a CSS property is on the SPEC.md kill-list (gradient, shadow, filter, etc.), translator logs a warning and chooses the locked fallback (solid color for gradient; no shadow; no filter).

## 7. Editability invariant (QC R4.7)

Per Decision 5, R4.7 is Critical (build hard-fails). The translator's contract:

> Every text element in the body zone MUST be created via `shape.text_frame.text = ...` on a SHAPE that python-pptx recognizes as having a text frame. No text rendered into a picture shape. No text positioned at arbitrary coordinates as a transparent/invisible shape. Text-as-image is forbidden in Pattern B output.

Translator self-check before emitting `option_A_native.py`:
1. Scan generated python code for `add_picture` calls — any `add_picture` whose source PNG contains rendered text (icon library OK; rendered text glyphs not OK) is a violation.
2. Scan for shapes with `text_frame.text` but invisible/zero-width — that's editable text positioned where it can't be edited; violation.
3. Scan for chrome-zone elements that don't have `data-template-field` AND are positioned in the chrome y-range — they should route through template placeholders.

If any violation found, emit `# EDITABILITY_VIOLATION: <detail>` at the top of the script and stop. Parent session catches the marker and surfaces in REVIEW.html as Critical.

## 8. Self-check via SSIM zone diff

Per Spec 5 (fidelity measurement), translator must self-check its output against the HTML PNG target. After emitting `option_A_native.py`:

1. Execute the script in a subprocess to produce `option_A_native.pptx`.
2. Render that PPTX to `option_A_native.png` via the existing LibreOffice path (or a fast python-pptx-to-image preview if available).
3. Compute per-zone SSIM between `option_A.png` (target) and `option_A_native.png` (output):
   - Title zone (0 to body_top_y_px)
   - Body zone (body_top_y_px to body_bottom_y_px)
   - Footer zone (body_bottom_y_px to 720)
4. If any zone SSIM < 0.85 (Major threshold), append warning to `option_A_translation_report.json`.
5. If any zone SSIM < 0.70 (Critical threshold), emit `# LOW_CONFIDENCE: zone <name> at SSIM <value>` at top of script.

`finalize_deck.py` reads the report and surfaces in REVIEW.html.

## 9. Prompt template

The translator's prompt (rendered into a `_translator_prompt.md` per slide by parent session at Stage 3.5):

```markdown
# Translator — slide N option X

You are translating a picked HTML option into a native python-pptx script
for the final editable PPTX. The HTML render is your visual ground truth.

## Read these in order

1. `_context.md` — canonical reference + design rules + constraint set
2. `_brief.md` — deck and slide context
3. `<picked>.html` — the picked option's HTML
4. `<picked>.png` — the rendered visual target
5. `brand.css` — CSS variable resolution
6. `chrome.yml` — layout geometry + EMU values

## Your task

Produce `<picked>_native.py` containing python-pptx code that:

1. Extracts title/subtitle/footer/page_number text from HTML elements with
   `data-template-field` and emits them as a `__template_fields__` dict
   structured comment. Do NOT create freeform shapes for these.

2. For every HTML element with `data-shape-id` in the body zone, generates
   a native python-pptx shape with:
   - Coordinates from getBoundingClientRect() converted px → EMU (1 px = 9525 EMU)
   - Fill from computed backgroundColor (solid only; no gradients)
   - Stroke from computed border properties
   - For text content: shape.text_frame.text + run-level font properties
     from computed style

3. Honors the CSS feature kill-list in SPEC.md §7. Forbidden features get
   the documented fallback (solid color for gradient, no shadow, etc.).

4. Saves to the path passed by the parent session.

5. Self-checks before emitting:
   - Editability invariant (R4.7 Critical): every text in a text_frame
   - SSIM zone diff against the PNG target
   - Sentinel comments in the script header

## Output

- `<picked>_native.py` — the native script
- `<picked>_translation_report.json` — machine-readable QC artifact

## Don't

- Don't invent shapes that aren't in the HTML — only translate what's there
- Don't apply CSS-kill-listed features (SPEC.md §7)
- Don't position title/subtitle/footer as freeform shapes — use the
  template field path
- Don't skip the SSIM self-check
```

## 10. Dispatch sequence

Parent session at Stage 3.5:

```python
for slide_n, picks in picks_json.items():
    if picks["pattern"] != "B":
        continue  # Pattern C slides skip the translator
    picked_letter = picks["picked_option"]
    dispatch_translator(
        slide_n=slide_n,
        option_letter=picked_letter,
        html_path=f"slide_{slide_n:02d}/option_{picked_letter}.html",
        png_path=f"slide_{slide_n:02d}/option_{picked_letter}.png",
        # ... (other paths from §3)
    )
# All translator dispatches run in parallel — they're independent.
# Per-slide, not batched (Decision 3 lock).
```

## 11. Failure modes + handling

| Marker the translator emits | Severity | Parent session behavior |
|---|---|---|
| `# TRANSLATOR_BLOCKED: <reason>` | Critical | Halt finalize; surface in REVIEW.html as Critical. User must re-pick or re-prep. |
| `# EDITABILITY_VIOLATION: <detail>` | Critical | Same as above. R4.7 Critical. |
| `# LOW_CONFIDENCE: zone <name> at SSIM <value>` | Major | Build continues; flag in REVIEW.html with the specific zone and score. |
| `# TRANSLATOR_WARNING: <detail>` | Advisory | Logged; not user-facing. |

## 12. Integration points

| File | Change |
|---|---|
| (new) `agents/slide-builder-translator.md` | Source-of-truth agent definition. |
| `%USERPROFILE%\.claude\agents\` | Installed copy. INSTALL.md Step 6.5 to copy. |
| `scripts/finalize_deck.py` | Add Stage 3.5 dispatcher: for each Pattern B slide with picks, dispatch translator. Read `_translation_report.json`. Surface markers in QC output. |
| `scripts/build_review.py` | Show SSIM scores per zone alongside option PNGs. Surface Critical / Major / Advisory markers from translator. |
| `_context.md` template | Add a "for translator" section that includes the same info but framed for the translator's task. |
| (new) `scripts/render_html.py` | Playwright wrapper. Used by both worker self-check and translator self-check. |

## 13. Out of scope

- Translator batching (Decision 3: deferred)
- Translator caching (same HTML → same output): out of scope for v0; rebuilds always re-translate
- Cross-slide consistency check (does slide N's translation use the same visual register as slide N-1?): out of scope; relies on per-slide variant_seed for variety
- Style transfer learning (translator learns from past picks): out of scope

---

**The translator is the central new component of Pattern B.** Its contract is precise so that the parent session can dispatch deterministically and `finalize_deck.py` can graft + render without ambiguity. The HTML PNG is the visual ground truth; the translator's job is to make python-pptx output match it as closely as possible while preserving editability.
