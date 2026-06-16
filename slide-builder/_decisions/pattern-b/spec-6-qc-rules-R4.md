# Pattern B — QC rules R4.1 through R4.8

> Eight new QC rules added to `slide-qc/VISION_QC_PROTOCOL.md` for Pattern B. Severities locked per Decision 5.

**Status:** locked 2026-06-16. Severities locked: 3 Critical / 4 Major / 1 Advisory.

---

## R4 — Pattern B (HTML → native translation) artifacts

These rules fire on the final native PPTX produced by the translator agent. Mostly checkable via static scan of the python-pptx script + post-render visual inspection.

---

### R4.1 — No strikethrough/underline on body text

**Severity:** **Critical**

**What it catches:** CSS `text-decoration: line-through`, `text-decoration: underline`, or `text-decoration: overline` surviving the HTML → native translation. Specific to the slide 16 failure case (2026-06-11) where strikethrough lines appeared across the "Why Hybrid" bullets on the recommendation card.

**How to check:**
1. Scan generated python-pptx code for any of: `run.font.underline = True`, `run.font.strikethrough = True` (the python-pptx XML attribute name may vary — also check `_r.set("u", ...)`, `_r.set("strike", ...)`).
2. Render the final PPTX to PNG.
3. Vision pass: scan for horizontal lines crossing body text. If detected, fail Critical.

**Exception:** A slide explicitly marking a deprecated/invalid option (e.g., a 3-option comparison with one option crossed out as "not chosen"). Worker must emit `# INTENTIONAL_STRIKETHROUGH: <reason>` to whitelist; that note appears in REVIEW.html context-ack.

**Recovery:** translator agent re-translates the slide, stripping `text-decoration` properties from runs.

---

### R4.2 — No opacity / transparency artifacts

**Severity:** **Major**

**What it catches:** CSS `opacity` < 1.0 or `rgba()` with alpha < 1.0 surviving translation. Creates semi-transparent text or backgrounds that reduce legibility.

**How to check:** Scan generated python-pptx code for `<a:alpha val="...">` XML elements on text-run colors, or `solid_fill` with alpha attribute. Vision pass: text or shapes that appear faded.

**Recovery:** translator strips alpha from text colors; allows alpha on non-text-bearing decorative shapes only (with severity reduction to Advisory).

---

### R4.3 — Font-weight preservation

**Severity:** **Major**

**What it catches:** CSS `font-weight: 100` (thin) or `font-weight: 900` (black) without the corresponding font variant installed. Without the variant, PowerPoint falls back to Regular weight; hierarchy intended by weight contrast collapses.

**How to check:** Scan generated python-pptx for explicit non-Regular weights. Cross-check with `theme.json::installed_font_variants` (new field added during registration: scans `Get-Font` output on Windows for available weights of the brand font).

**Recovery:** If the variant isn't available, translator (a) maps to nearest available weight, (b) flags the slide as Major in the translation report. User decides whether to ship or install the missing variant.

---

### R4.4 — Gradient conversion

**Severity:** **Major**

**What it catches:** CSS `linear-gradient` / `radial-gradient` in the body zone, which python-pptx can't natively render. Translator falls back to solid color (midpoint stop) — but this is silent visual fidelity loss.

**How to check:** Translator parses worker HTML and tags any element whose `backgroundImage` contains `gradient(`. If found, translator chooses solid fallback per Spec 2 §6 AND emits a warning in the translation report.

**Recovery:** Worker should not use gradients in the body zone (SPEC.md §7 kill-list). If gradient is essential, worker requests an `# IMAGE_EMBED_EXCEPTION: <region>` and the translator embeds that region as a small PNG instead of solid-approximating.

---

### R4.5 — No CSS filters

**Severity:** Advisory

**What it catches:** CSS `filter: drop-shadow()`, `filter: blur()`, `backdrop-filter: ...`, `mix-blend-mode`, etc. None of these translate to python-pptx; using them in HTML means the native output won't visually match.

**How to check:** Translator scans HTML computed-style for `filter` and `mix-blend-mode` properties not equal to default values.

**Recovery:** None — log the violation; translator proceeds without applying the filter. Worker should remove these from their HTML.

---

### R4.6 — Icons embedded cleanly

**Severity:** **Major**

**What it catches:** Icons in the HTML that don't map to the existing icon library, OR `add_picture` calls in generated python-pptx where the source SVG/PNG fails to load.

**How to check:**
1. Translator inspects every `<img src="icons/..."` or `<i data-icon-name="...">` in the HTML.
2. Verifies the icon name exists in the `slide-builder/icons/` catalog.
3. Verifies the generated `add_picture(...)` call references an actual file.
4. Post-render: vision pass checks for broken-image placeholders.

**Recovery:** Worker references a valid icon name from the library. If a needed icon isn't in the library, worker emits a `# ICON_REQUEST: <name>` and the orchestrator surfaces the request (icons get added to the library out-of-band).

---

### R4.7 — Editability verified at build time

**Severity:** **Critical**

**What it catches:** Any text element in the final PPTX that is NOT inside a recognizable text frame. Failure modes:
- Text rendered into a picture shape (text-as-image)
- Text positioned at arbitrary (x, y) as a transparent/zero-size shape
- Text in a chrome zone but NOT routed through a template placeholder

**How to check:**
1. Open the generated PPTX in python-pptx.
2. For every shape, check whether it has a `text_frame` attribute and the text frame contains the expected text.
3. For chrome-zone text (title, subtitle, footer, page_number), verify it's in a placeholder shape (`shape.is_placeholder == True`) OR a named textbox.
4. For body-zone text, verify each text-bearing shape has `text_frame.text != ""` AND the shape is recognizable as a text container (not a picture or freeform).
5. Open in PowerPoint UI test: click on each text element → confirm cursor enters edit mode.

**Recovery:** translator hard-fails before emitting the script. R4.7 violations are the load-bearing Pattern B failure mode (entire reason for the refactor). No exceptions.

---

### R4.8 — Text decorations audit (catch-all)

**Severity:** **Critical**

**What it catches:** Any unexpected text decoration (bold, italic, underline, strikethrough) that wasn't requested in the brief. Acts as the safety net for R4.1.

**How to check:**
1. Parse the brief for explicit decoration requests (e.g., "Bold the metric value", "Italicize the source attribution").
2. Scan generated python-pptx for `run.font.bold = True`, `run.font.italic = True`, `run.font.underline = True`.
3. Cross-reference: any decoration NOT explicit in the brief is a violation.

**Exception:** Default styling per the slide's pattern treatment (e.g., card titles are bold by convention) is acceptable. The check fires only on UNEXPECTED decorations — those derived from the HTML without brief support.

**Recovery:** translator re-translates with decorations stripped. If brief lacked explicit decoration but slide needs it (e.g., headline emphasis), worker emits `# DECORATION_INTENT: <field> <decoration>` in the HTML to whitelist.

---

## Severity summary

| Rule | Severity |
|---|---|
| R4.1 strikethrough/underline | Critical |
| R4.2 opacity / transparency | Major |
| R4.3 font-weight preservation | Major |
| R4.4 gradient conversion | Major |
| R4.5 CSS filters | Advisory |
| R4.6 icons embedded cleanly | Major |
| R4.7 editability verified | Critical |
| R4.8 text decorations audit | Critical |

**3 Critical / 4 Major / 1 Advisory.**

Critical = build hard-fails; user must fix before shipping.
Major = surfaces in REVIEW.html with flag; user decides.
Advisory = logged; not user-facing.

## Integration points

| File | Change |
|---|---|
| `slide-qc/VISION_QC_PROTOCOL.md` | Add the R4 section verbatim from this spec. |
| `slide-qc/scripts/run_vision_qc.py` (or equivalent) | Implement the static-scan + vision-pass checks. |
| `scripts/finalize_deck.py` | Read translator report JSON; surface markers in REVIEW.html. |
| `scripts/build_review.py` | Render severity chips per slide per option (Critical red, Major yellow, Advisory gray). |
