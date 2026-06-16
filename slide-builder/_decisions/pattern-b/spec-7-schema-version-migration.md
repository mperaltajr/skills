# Pattern B — `_meta.json` schema version migration

> Defines schema version 3 for build outputs and the migration / hard-fail behavior for older schemas.

**Status:** locked 2026-06-16.

---

## 1. Current state — schema v2

`build_deck.py` currently writes `_meta.json` with `schema_version: 2`. Fields include `client_template`, `deck_type`, per-slide entries with `title / subtitle / layout / archetype`, `mermaid_theme`, `classification_counts`, `forecasts`.

`finalize_deck.py` reads `_meta.json` and proceeds with the python-pptx-direct path (executes `option_X.py`, grafts, renders).

Under Pattern B, the build artifacts change shape: workers produce `option_X.html` instead of `option_X.py`, plus a translator stage produces `option_X_native.py`, plus a `_translation_report.json` per slide. The schema needs to track which pattern each slide used so `finalize_deck.py` can route correctly.

## 2. Schema v3 additions

`build_deck.py` writes `_meta.json` with `schema_version: 3`. New top-level + per-slide fields:

```json
{
  "schema_version": 3,
  "pattern_default": "B",
  "pattern_per_slide": {
    "1": "C",
    "2": "B",
    "3": "B",
    "...": "..."
  },
  "html_render_canvas": "1280x720",
  "translator_dispatched": false,
  "translation_reports": {},

  "client_template": "...",
  "deck_type": "...",
  "slides": [
    {
      "slide_n": 1,
      "title": "...",
      "subtitle": "...",
      "layout": "Use as default slide template",
      "archetype": "Cover/Title",
      "pattern": "C",
      "artifacts": {
        "py": "slide_01/option_A.py",
        "py_classification": "native"
      }
    },
    {
      "slide_n": 2,
      "title": "...",
      "subtitle": "...",
      "layout": "Use as default slide template",
      "archetype": "Synthesis/Findings",
      "pattern": "B",
      "artifacts": {
        "html": "slide_02/option_A.html",
        "png_target": "slide_02/option_A.png",
        "translated_py": null,
        "translated_pptx": null
      }
    }
  ]
}
```

After picks + translator dispatch, `translator_dispatched: true` and per-Pattern-B-slide artifacts gain `translated_py` + `translated_pptx` + `translation_report` paths.

## 3. Migration / hard-fail behavior

`finalize_deck.py` at entry reads `_meta.json` and checks `schema_version`:

```python
def main():
    # ... arg parsing
    meta = load_meta(args.out)
    schema = meta.get("schema_version", 1)

    if schema == 3:
        # Pattern B aware; normal flow
        pass
    elif schema == 2:
        # Pre-Pattern-B builds. Run in legacy mode (python-pptx-direct only).
        # No translator dispatch; treat all slides as Pattern C-equivalent.
        sys.stderr.write(
            f"  NOTICE: _meta.json schema_version={schema} predates Pattern B. "
            f"Running in legacy mode (python-pptx-direct, no translator).\n"
        )
        meta = _upgrade_meta_v2_to_v3_minimal(meta)
        # ... proceed with legacy path
    elif schema < 2:
        sys.stderr.write(
            f"ERROR: _meta.json schema_version={schema} is too old.\n"
            f"  Slide Lab requires schema v2+ since 2026-05-26 (chassis-vocabulary retirement).\n"
            f"  Re-prep the deck:\n"
            f"    py -3 scripts/build_deck.py --brief <brief.md> --template <template.pptx> --out <out>\n"
        )
        return 8
    else:
        sys.stderr.write(
            f"ERROR: _meta.json schema_version={schema} is newer than this finalize_deck "
            f"supports (max: 3). Re-install the slide-builder skill.\n"
        )
        return 8

def _upgrade_meta_v2_to_v3_minimal(meta: dict) -> dict:
    """In-place upgrade for v2→v3. All slides default to Pattern C (legacy)."""
    meta["schema_version"] = 3
    meta["pattern_default"] = "C"
    meta["pattern_per_slide"] = {str(s["slide_n"]): "C" for s in meta.get("slides", [])}
    meta["html_render_canvas"] = None
    meta["translator_dispatched"] = False
    meta["translation_reports"] = {}
    for slide in meta.get("slides", []):
        slide["pattern"] = "C"
        slide.setdefault("artifacts", {})
        slide["artifacts"].setdefault("py", f"slide_{slide['slide_n']:02d}/option_A.py")
        slide["artifacts"].setdefault("py_classification", "native")
    return meta
```

## 4. `build_deck.py` writes schema v3

```python
SCHEMA_VERSION = 3

def write_meta_json(out_dir, brief_path, brief, template_path, theme_path,
                     client_slug, forecasts, brand,
                     pattern_per_slide=None):
    pattern_per_slide = pattern_per_slide or _classify_all_slides(brief.slides)
    meta = {
        "schema_version": SCHEMA_VERSION,
        "pattern_default": "B",
        "pattern_per_slide": {str(n): p for n, p in pattern_per_slide.items()},
        "html_render_canvas": "1280x720" if "B" in pattern_per_slide.values() else None,
        "translator_dispatched": False,
        "translation_reports": {},
        "client_template": str(template_path),
        "deck_type": brief.deck_type,
        # ... (existing fields)
        "slides": [
            {
                "slide_n": s.slide_n,
                "title": s.title,
                "subtitle": s.subtitle,
                "layout": s.layout,
                "archetype": s.archetype,
                "pattern": pattern_per_slide[s.slide_n],
                "artifacts": _initial_artifacts(s.slide_n, pattern_per_slide[s.slide_n]),
            }
            for s in brief.slides
        ],
    }
    # ... write to _meta.json
```

`_classify_all_slides` implements Decision 2 routing (Pattern B vs C per slide content). Lives in `build_deck.py`; spec for the classifier in Spec 8 (rollback flag — the `--pattern` flag overrides per-slide routing).

## 5. Where schema is read

| File | Reads schema for |
|---|---|
| `finalize_deck.py` | Routing per slide (B → translator path; C → native-direct path) |
| `build_review.py` | Loading per-slide options + translation reports |
| `compile_picks.py` | Picking up the correct PPTX file per slide (option_X.pptx for C; option_X_native.pptx for B) |
| Worker dispatch (orchestrator) | Knowing which worker prompt to dispatch (HTML worker vs python-pptx worker) |

## 6. Recovery on schema mismatch

User-facing message when `schema_version` is `< 3` on a Pattern-B-only `finalize_deck.py`:

```
NOTICE: _meta.json schema_version=2 predates Pattern B.

This build was prepared before the Pattern B refactor landed. Running in
legacy mode: all slides treated as Pattern C (native python-pptx direct,
no HTML translator).

To use Pattern B for this deck, re-prep:

  py -3 scripts/build_deck.py \
       --brief <path/to/brief.md> \
       --template <path/to/template.pptx> \
       --out <path/to/out>

Re-prep takes ~30 seconds and writes a fresh _meta.json with schema v3.
The existing slide_NN/option_X.py files are preserved; they just won't be
used in Pattern B mode (workers will re-dispatch with HTML output).
```

## 7. Integration points

| File | Change |
|---|---|
| `scripts/build_deck.py` | Write `schema_version: 3` + new top-level + per-slide fields. Add `_classify_all_slides` (Decision 2 logic). |
| `scripts/finalize_deck.py` | Read schema. If v2: legacy mode. If v3: route per-slide via `pattern_per_slide`. If <2 or >3: hard-fail. |
| `scripts/build_review.py` | Read schema + per-slide artifacts. Show Pattern B options as HTML-rendered PNGs; Pattern C options as native-rendered PNGs. |
| `scripts/compile_picks.py` | Pick the correct PPTX file per slide based on pattern. |
| (new) `scripts/_meta_schema.py` | If a `SlideMeta` pydantic model exists, extend it. Else inline the schema validation. |

## 8. Out of scope

- Forward-compat for future schema versions (4+) — handle when needed
- Schema validation via JSON Schema files — for v0, code-level dict access is sufficient
- Cross-machine schema sync — schema is per-build-output, not per-skill-install; no sync needed
