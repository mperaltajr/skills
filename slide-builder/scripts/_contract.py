"""_contract.py — module-load-time pipeline contract test.

Verifies the Slide Lab pipeline is internally consistent without requiring
a live build. Runs three checks:

1. **Paths registry sanity** — every helper named in `_paths.ARTIFACT_MANIFEST`
   resolves to a callable or constant on the `_paths` module.

2. **Meta-JSON schema round-trip** — a synthetic MetaJson model serialises
   to dict and validates back without drift.

3. **Handoff coverage** — every artifact in the manifest with a declared
   writer script appears in that script's source text via `_paths.<name>` or
   `_paths.<NAME>` form. Same for readers. Orphans marked `accepted: True`
   in the manifest are skipped with reason recorded.

Run directly:
    py -3 scripts/_contract.py
Exit code 0 = all green. Non-zero = at least one drift detected.

Wire into CI before any v0.1 release tag per DECISIONS.md § "Hardening
triple — items 2 + 3 acceptance gate."
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _paths as _p
from _meta_schema import (
    MetaJson, validate_meta_dict, MetaJsonSchemaError,
    META_SCHEMA_VERSION_CURRENT,
)


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")


def _ok(msg: str) -> None:
    print(f"  ok: {msg}")


# ---------------------------------------------------------------------------
# Check 1 — paths registry sanity
# ---------------------------------------------------------------------------

def check_paths_registry() -> list[str]:
    """Every name in ARTIFACT_MANIFEST must resolve on the _paths module."""
    errors: list[str] = []
    for entry in _p.ARTIFACT_MANIFEST:
        name = entry["name"]
        if not hasattr(_p, name):
            errors.append(f"manifest names '{name}' but _paths has no such attribute")
            continue
        attr = getattr(_p, name)
        if not (callable(attr) or isinstance(attr, str)):
            errors.append(f"_paths.{name} is neither a callable nor a string constant (got {type(attr).__name__})")
    if not errors:
        _ok(f"paths registry: {len(_p.ARTIFACT_MANIFEST)} manifest entries all resolve on _paths")
    return errors


# ---------------------------------------------------------------------------
# Check 2 — meta-JSON schema round-trip
# ---------------------------------------------------------------------------

def check_meta_schema_roundtrip() -> list[str]:
    """A synthetic MetaJson must serialise to dict and re-validate cleanly."""
    errors: list[str] = []
    synthetic = MetaJson(
        schema_version=META_SCHEMA_VERSION_CURRENT,
        template="C:/fake/template.pptx",
        brief="C:/fake/brief.md",
        out="C:/fake/out",
        mermaid_theme="C:/fake/theme.json",
        client_slug="acme",
        slide_count=2,
        generated_at="2026-05-26T00:00:00+00:00",
        brand_primary="#4D148C",
        brand_accent="#FF6600",
        slides=[
            {"n": 1, "title": "T1", "forecasted_pattern": "full-canvas", "page_type": "cover"},
            {"n": 2, "title": "T2", "forecasted_pattern": "50-50",       "page_type": "headline-finding"},
        ],
        deck_meta={"deck_type": "client-pitch", "governing_thought": "g", "audience": "a"},
    )
    as_dict = synthetic.model_dump()
    try:
        validated = validate_meta_dict(as_dict)
    except MetaJsonSchemaError as e:
        errors.append(f"round-trip validation failed: {e}")
        return errors
    if validated.schema_version != META_SCHEMA_VERSION_CURRENT:
        errors.append(
            f"round-trip schema_version mismatch: "
            f"{validated.schema_version} != {META_SCHEMA_VERSION_CURRENT}"
        )
    if not errors:
        _ok(f"meta-json schema round-trip @ version {META_SCHEMA_VERSION_CURRENT}")
    return errors


# ---------------------------------------------------------------------------
# Check 3 — handoff coverage
# ---------------------------------------------------------------------------

_SCRIPT_TEXT_CACHE: dict[str, str] = {}


def _script_text(name: str) -> str:
    if name not in _SCRIPT_TEXT_CACHE:
        p = HERE / name
        _SCRIPT_TEXT_CACHE[name] = p.read_text(encoding="utf-8") if p.exists() else ""
    return _SCRIPT_TEXT_CACHE[name]


def _references_artifact(script_name: str, artifact_name: str) -> bool:
    """A script 'uses' an artifact if it imports the helper name from _paths.

    Accepts any of:
      - `_p.<name>(...)` — absolute-path helper form
      - `_p.<name>_name(...)` — filename-only helper form (per-option assets)
      - `_p.<NAME>` — uppercase constant form (slide-relative filenames)
    """
    text = _script_text(script_name)
    if not text:
        return False
    patterns = [
        rf"\b_p\.{re.escape(artifact_name)}\b",
        rf"\b_p\.{re.escape(artifact_name)}_name\b",
        rf"\b_p\.{re.escape(artifact_name.upper())}\b",
    ]
    return any(re.search(p, text) for p in patterns)


def check_handoff_coverage() -> list[str]:
    errors: list[str] = []
    checked = 0
    skipped = 0
    for entry in _p.ARTIFACT_MANIFEST:
        if entry.get("accepted"):
            skipped += 1
            continue
        name = entry["name"]
        writer = entry["writer"]
        readers = entry["readers"]
        checked += 1
        if writer.endswith(".py") and not _references_artifact(writer, name):
            errors.append(f"writer mismatch: manifest says {writer} writes {name!r}, but the script doesn't reference _paths.{name}")
        for r in readers:
            if r.endswith(".py") and not _references_artifact(r, name):
                errors.append(f"reader mismatch: manifest says {r} reads {name!r}, but the script doesn't reference _paths.{name}")
    if not errors:
        _ok(f"handoff coverage: {checked} artifacts checked, {skipped} accepted-orphans skipped")
    return errors


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Check 4 — pipeline-script import smoke
# ---------------------------------------------------------------------------

def check_pipeline_imports() -> list[str]:
    """Actually import every pipeline script under try/except.

    `check_handoff_coverage` greps script text for path-helper references but
    never executes the module-level code. Module-load-time bugs (forward
    references to imports that don't land until later in the file, missing
    submodule deps, broken `from X import Y` lines) slip through that grep.
    This check imports each script so module-level errors surface here, not
    at the operator's first `--help`. Audit finding T2.7 (2026-05-26).
    """
    import importlib
    errors: list[str] = []
    # Scripts that are entry points (have an `if __name__ == "__main__"`) +
    # helper modules. All should import cleanly with sys.path already set
    # to HERE.
    targets = [
        "_paths", "_meta_schema", "_log", "_contract",
        "build_deck", "finalize_deck", "compile_picks",
        "build_review", "build_gate_preview",
        "register_template", "clean", "diagnostic",
        "icon_helper", "render_mermaid",
    ]
    imported = 0
    for name in targets:
        try:
            # importlib.import_module caches; reimport via reload is overkill
            # for the contract test. A successful first-import here proves
            # module-level code ran without exception, which is what matters.
            mod = importlib.import_module(name)
            if mod is None:
                errors.append(f"import {name}: returned None")
            else:
                imported += 1
        except Exception as exc:
            errors.append(f"import {name}: {type(exc).__name__}: {exc}")
    if not errors:
        _ok(f"pipeline imports: {imported} modules loaded cleanly")
    return errors


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> int:
    print("Slide Lab pipeline contract test")
    print("=" * 60)

    all_errors: list[str] = []
    for check in (check_paths_registry,
                  check_meta_schema_roundtrip,
                  check_handoff_coverage,
                  check_pipeline_imports):
        errs = check()
        for e in errs:
            _fail(e)
        all_errors.extend(errs)

    print("=" * 60)
    if all_errors:
        print(f"CONTRACT TEST FAILED: {len(all_errors)} drift(s) detected.")
        return 1
    print("CONTRACT TEST PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
