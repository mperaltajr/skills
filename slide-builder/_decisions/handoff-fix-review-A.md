# Handoff-fix review — Reviewer A

## Verdict

**Option 1 + 2 combined, with a scope correction.** v2''s recommendation is
directionally right, but it under-sells the change. `_meta.json` is not just a
Mermaid-theme breadcrumb — it is the missing deck manifest that
`compile_picks.py` and `build_review.py` already read. v2 needs to commit to
writing it as a first-class artifact, not as a Mermaid-handoff side effect.
Option 3 (finalize derives the theme from the template via
`load_brand_sidecar`) is locally elegant but architecturally wrong for this
codebase right now.

## Reasoning

### `compile_picks.py` and `build_review.py` already depend on `_meta.json`

`compile_picks.py:177-185` hard-fails when `<out>/_meta.json` is absent and
reads `meta["template"]` to find the client PPTX:

```python
meta_path = out_dir / "_meta.json"
if not meta_path.exists():
    print(f"ERROR: _meta.json not found at {meta_path}")
    return 2
meta = json.loads(meta_path.read_text(encoding="utf-8"))
template_path = Path(meta["template"])
```

`build_review.py:1203-1213` opportunistically reads `_meta.json` for
`meta["slides"]` (slide metadata). Today both code paths are broken — the
Mermaid bug is the same disease showing through a different symptom.
`_meta.json` is **the** deck manifest in v2''s design; `build_deck.py` simply
forgot to write it.

That re-frames the question. v2 isn''t choosing between "indirection" and
"directness." v2 is choosing between *writing the manifest its own downstream
already requires* or *carrying multiple stage-specific lookup paths and
letting them drift*. The first is the correct call.

### Why not Option 3 (finalize reads `load_brand_sidecar` directly)

`finalize_deck.py` already has `args.template` (line 838), so technically it
could call `load_brand_sidecar(args.template)` and regenerate the Mermaid
theme on the fly. It would work. But it solves the wrong problem:

1. **It only fixes the Mermaid theme leg.** `compile_picks.py` still needs a
   manifest. Patching just `_resolve_mermaid_theme` would leave the other
   manifest consumers broken — and in fact they are broken today for the same
   reason, you just haven''t hit them in smoke yet.
2. **It re-derives state that build_deck already computed.** `build_deck.py`
   already runs `load_brand_sidecar`, already runs `generate_mermaid_theme`,
   already validates the result with `validate_theme()` (lines 1071-1122),
   and already writes the theme JSON to disk. Asking finalize to redo all
   that is duplicate work that can drift. Worse, finalize would skip the
   `validate_theme()` step — which is the structural belt-and-braces guard.
3. **Tighter coupling to v1 internals.** `load_brand_sidecar` lives in
   `slide-builder/twins/client_theme.py`. v2 already imports
   `load_client_theme` for the graft pass; adding `load_brand_sidecar` is
   not a new sin per se, but every additional v1 symbol v2 binds to is
   another cross-stream contract that needs change-control (see
   `unblock-review-A.md § "pre-merge inventory of cross-stream callers"`).
   The manifest pattern avoids that by snapshotting the result at build time.

Option 3 is the right choice in a greenfield codebase. It is the wrong choice
in *this* codebase, where the manifest already exists conceptually and two
other scripts already depend on it.

### `client_slug` vs `mermaid_theme` — one is redundant

`_resolve_mermaid_theme()` reads either `mermaid_theme` (absolute path) or
`client_slug` (then constructs `theme/mermaid-<slug>.json`). One is redundant.
`mermaid_theme` is the better one to keep: it''s explicit, doesn''t assume the
theme lives under `SKILL_ROOT/theme/`, and survives a hypothetical move of
the per-client theme into the project directory (where, per memory, deck
artifacts ought to live next to the brief). `client_slug` is still useful in
`_meta.json` as a *descriptive* field but should not be a lookup fallback.
Drop the `client_slug` branch from `_resolve_mermaid_theme`.

### Is `_meta.json` part of the disease or the cure?

Reviewer B''s prior "no shared `paths.py` module" point stands as a deeper
issue. But `_meta.json` is the *cure* for the current symptom, not another
disease, because:

- It''s a single artifact whose schema is owned by build_deck (the writer) and
  read by every downstream stage. That''s the manifest pattern, not the
  parallel-files anti-pattern.
- The parallel-files problem would be writing `_meta.json` AND
  `dispatch_plan.md` AND `_finalize_meta.json` as overlapping deck-metadata
  artifacts. v2 is already doing exactly that (Reviewer B flagged this in
  `fidelity-threshold-review-B.md:48-56`). That smell is real, but it''s
  orthogonal to today''s fix. The fix here is: write `_meta.json`; rationalize
  the three-files-mess in a follow-on.

A `paths.py` module would be the deeper cure (centralize artifact locations,
get a typed manifest reader) but it''s a v0.2 refactor, not a Mermaid-bug fix.

## Code-level specifics

### `build_deck.py` — write `_meta.json` after theme generation

Insert after `validate_theme` succeeds (after line 1122, before line 1124
`# 5. Render per-slide prompts`):

```python
# 4.6 Write deck manifest (_meta.json) — single source of truth for
# downstream stages (finalize_deck.py, compile_picks.py, build_review.py).
meta = {
    "client_slug": client_slug,
    "template": str(args.template.resolve()),
    "brief": str(args.brief.resolve()),
    "mermaid_theme": str(theme_path.resolve()),
    "slide_total": slide_total,
    "slides": [
        {"n": s["slide_n"], "title": s.get("title", "")}
        for s in slides
    ],
}
(args.out / "_meta.json").write_text(
    json.dumps(meta, indent=2), encoding="utf-8"
)
```

This also fixes `compile_picks.py:182` (`meta["template"]`) and
`build_review.py:1211` (`meta["slides"]`) which are silently broken today.

### `finalize_deck.py::_resolve_mermaid_theme` — fail loud, drop client_slug

Replace lines 451-476 with:

```python
def _resolve_mermaid_theme(out_dir: Path, override: Optional[Path]) -> Path:
    """Pick the Mermaid theme JSON.
    Precedence: --theme override, else <out>/_meta.json[''mermaid_theme''].
    Refuses to fall back to mermaid-brand.json (FedEx-shaped by convention —
    would silently mis-color non-FedEx clients). See _decisions/handoff-fix-*.
    """
    if override and override.exists():
        return override
    meta_path = out_dir / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(
            f"_meta.json not found at {meta_path}. "
            f"Run build_deck.py first; refusing to fall back to "
            f"mermaid-brand.json (would silently render with FedEx colors)."
        )
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    cand = meta.get("mermaid_theme")
    if not cand or not Path(cand).exists():
        raise FileNotFoundError(
            f"_meta.json[''mermaid_theme''] missing or points to a non-existent "
            f"file: {cand!r}. Re-run build_deck.py."
        )
    return Path(cand)
```

Also delete the `DEFAULT_MERMAID_THEME = SKILL_ROOT / "theme" / "mermaid-brand.json"`
constant at line 443 — nothing else should reference it. Better: rename
`mermaid-brand.json` on disk to `mermaid-fedex-reference.json` so future
readers can''t mistake it for a generic default.

### Catch the raise in `finalize_deck.py::main`

Wrap line 857 (`mermaid_theme = _resolve_mermaid_theme(...)`) in a
try/except that prints the message and returns a non-zero exit so the user
gets a clean error instead of a stack trace.

## Biggest concern

The Mermaid bug is a tracer for a deeper rot: **v2 has at least three
overlapping deck-metadata artifacts** (`_meta.json` as conceptually expected,
`dispatch_plan.md` actually written, `_finalize_meta.json` written at the end)
and **no shared schema enforcement**. Fixing the Mermaid handoff by writing
`_meta.json` is correct but it doesn''t address the broader drift. After this
fix lands, somebody needs to spend a half-day on a `paths.py`-equivalent
module that:

1. Declares the canonical artifact layout (`_meta.json`, `slide_NN/`,
   `final_deck.pptx`, `qc/`) as constants.
2. Provides typed reader/writer functions for `_meta.json` so build_deck,
   finalize_deck, compile_picks, and build_review can''t drift on field names.
3. Deprecates `dispatch_plan.md` as a structured data source — keep it as a
   human-readable summary only.

Without that, the next handoff bug is a quarter away. The Mermaid fix is
necessary but not sufficient.
