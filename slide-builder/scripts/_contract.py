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
# Check 5 — install sentinels (source/installed content fingerprint match)
# ---------------------------------------------------------------------------
#
# Drift class this prevents: a file installed at the right path with the
# wrong content. Existence checks (`Test-Path`) pass; user-facing behavior
# silently breaks. Worker-agent T1-R1 (v1 content at v0.1 path) and the
# T1-NEW-A `sys.argv[1]` regression both belong to this class.
#
# Each entry declares:
#   source            — absolute path to the canonical source artifact
#                       (lives inside the skill)
#   installed         — environment-resolved path to the installed copy
#                       (typically under ~/.claude/agents/ for sub-agents)
#   sentinels         — list of EXACT strings that must appear in BOTH
#                       files. Choose strings that encode the user-facing
#                       CONTRACT (e.g., the output filename pattern, the
#                       save-contract verb) — not strings that describe
#                       the file itself. The point is to catch "right
#                       path, wrong content."
#
# Adding new sentinels: when a future drift surfaces because the installed
# copy diverged from the source, add a sentinel here that would have
# caught the specific contradiction. This file is the institutional
# learning surface for install-time drift.

import os

_SKILL_ROOT = HERE.parent

INSTALL_SENTINELS = [
    {
        "name": "slide-builder-worker agent",
        "source": _SKILL_ROOT / "agents" / "slide-builder-worker.md",
        "installed": Path(os.path.expanduser("~/.claude/agents/slide-builder-worker.md")),
        # "option_A.pptx" encodes the OUTPUT-filename contract from
        # prompt.md:252-260. The string "option_A.py" (the SCRIPT name)
        # is not sufficient because v1 worker content also contains it.
        # The OUTPUT contract is what tells the worker to save to a
        # literal filename rather than sys.argv[1].
        "sentinels": ["option_A.pptx"],
    },
]


def check_install_sentinels() -> list[str]:
    errors: list[str] = []
    checked = 0
    for entry in INSTALL_SENTINELS:
        name = entry["name"]
        source: Path = entry["source"]
        installed: Path = entry["installed"]
        sentinels: list[str] = entry["sentinels"]

        if not source.exists():
            errors.append(f"sentinel: source for {name!r} missing at {source}")
            continue

        source_text = source.read_text(encoding="utf-8", errors="replace")
        for s in sentinels:
            if s not in source_text:
                errors.append(
                    f"sentinel: source {name!r} ({source.name}) does not "
                    f"contain canonical contract string {s!r} — the source "
                    f"itself drifted from its declared contract"
                )

        if not installed.exists():
            errors.append(
                f"sentinel: installed {name!r} missing at {installed} — "
                f"INSTALL step likely not run, or wrong destination"
            )
            continue

        installed_text = installed.read_text(encoding="utf-8", errors="replace")
        for s in sentinels:
            if s not in installed_text:
                errors.append(
                    f"sentinel: installed {name!r} at {installed} does not "
                    f"contain canonical contract string {s!r} — file exists "
                    f"but content is wrong (likely a stale copy)"
                )
        checked += 1

    if not errors:
        _ok(f"install sentinels: {checked} entries verified at source AND installed")
    return errors


# ---------------------------------------------------------------------------
# Check 6 — every markdown file:path reference resolves on disk
# ---------------------------------------------------------------------------
#
# Drift class this prevents: docs that name files which no longer exist
# (CHANGELOG listing QUICKSTART.md after it was deleted; SKILL.md naming
# `slide-builder_archived_2026-05-26/` when that path doesn't exist;
# cross-skill references to deleted v1 scripts).
#
# Scope: every .md under the skill EXCEPT under _decisions/. The decisions
# dir is forensic — historical records intentionally cite paths that may
# have moved or been deleted.

_DOC_REF_EXTS = (".py", ".md", ".json", ".yml", ".yaml", ".pptx", ".png",
                 ".html", ".css", ".xml", ".txt", ".toml")

# Match path-like tokens inside backticks. Restricting to backtick-wrapped
# tokens keeps us out of prose ("the design.md" vs "`design.md`") and
# avoids false positives on natural language.
_DOC_REF_RE = re.compile(
    r"`([A-Za-z_][\w./\-]*?(?:\.[A-Za-z0-9]{1,8}))`"
)

# Match directory-path refs (trailing slash) inside backticks. Catches
# the `slide-builder_archived_2026-05-26/` class of phantom-archive ref.
# Requires at least one path component (i.e., presence of "/" before
# the trailing slash, OR a leading skill-relative path with separators).
_DOC_DIR_REF_RE = re.compile(
    r"`([A-Za-z_][\w\-]*(?:/[\w.\-]+)*/)`"
)

# Dir refs that legitimately point at user-context paths (the user's
# home/.claude/agents/ install location, the user's OneDrive Claude
# Projects, etc.) — not under the skill tree by design.
_DIR_USER_CONTEXT_PREFIXES = (
    "~/.claude/", "OneDrive", "Documents/", "Downloads/",
    "_session/",  # session output dirs
    "C:/", "C:\\",  # absolute Windows paths
)

# Directory-path templates / placeholders used in prose, not literal
# paths. `slide_NN/` is the per-slide template (NN is a slot); `out/`
# is the build output dir as named in CLI examples.
_DIR_TEMPLATE_REFS = {
    "slide_NN/", "out/", "dont/", "exemplars/",
    "_templates/", "_session/",
}

# Directories legitimately cited in deletion-context entries
# (CHANGELOG history, master plan archive log). The check skips them
# globally — these are forensic citations, not live refs.
_DIR_DELETED_BY_DESIGN = {
    "slide-builder_archived_2026-05-26/",
    "slide-builder_archived_2026-05-26/exemplars/dont/",
    "slide-builder/icons/_audit/",
    "slide-builder/icons/_backup/",
    "icons/_audit/", "icons/_backup/",
    # v1 do/ positive-exemplar corpus never ported
    "do/", "do/single-finding/", "do/chart-bottom-takeaway/",
    "do/hero-kpi-tile/", "do/2panel-delta-spine/",
    "do/chart-right-takeaway/",
}

# Runtime artifacts produced by the pipeline. These appear in docs as
# "the output is X" — they intentionally don't live in the source tree.
# Catching them as broken refs is noise.
_RUNTIME_ARTIFACTS = {
    "_meta.json", "_prompt.md", "_finalize_meta.json",
    "picks.json", "brand.yml", "theme.json",
    "final_deck.pptx", "final.pptx",  # legacy/example name
    "REVIEW.html", "GATE3-PREVIEW.html",
    "register.html", "register.proposal.json",
    "preview.pptx", "preview.png", "palette.png",
    "COMPILED.md", "RESULT.md", "build.log",
    "dispatch_plan.md",
    "qc.json", "raw.pptx",
    # Per-option artifacts, written at build time under slide_NN/
    "option_A.py", "option_B.py", "option_C.py",
    "option_A.pptx", "option_B.pptx", "option_C.pptx",
    "option_A.mmd", "option_B.mmd", "option_C.mmd",
    "option_X.py", "option_X.pptx", "option_X.mmd",  # template names in docs
    "option_X-mermaid.png",  # rendered fallback PNG
    "spec.md",
}

# Per-client runtime theme files (mermaid-<slug>.json). The slug
# varies by client; we treat the whole family as runtime.
_RUNTIME_PREFIXES = (
    "_session/",  # session-folder outputs (DECISIONS.md, briefs, etc.)
    "mermaid-",   # per-client mermaid theme JSON
)

# Filenames that are LEGITIMATELY referenced in deletion-context
# entries (CHANGELOG, master plan, audit handovers). The check skips
# them globally — if they reappear as live code, the import check
# would catch it.
_DELETED_BY_DESIGN = {
    "build_slide.py", "extract_icons.py", "QUICKSTART.md",
    "phase-a-rules.md", "visual-treatment-library.md",
    "designer-brief.md", "rules.md",
    "_verify_critical_fixes.py", "mermaid-brand.json",
    "stage-a-precommit.md", "slide-builder-simple-worker.md",
    "slide-builder.md", "slide-designer.md", "deck-builder.md",
    "smoke_test.py",
    # Path-class deletions
    "theme/mermaid-brand.json", "scripts/_verify_critical_fixes.py",
    # v0.2 candidate work — documented as future-pending, not present
    "check_brief_fidelity.py", "extract_lucide.py",
}

# Bare-filename refs that legitimately point at the user's external
# memory directory (~/.claude/projects/.../memory/) rather than the
# skill tree. Cross-context refs by design.
_MEMORY_FILE_PREFIXES = ("feedback_", "project_")


def _resolve_doc_ref(ref: str, md_file: Path) -> bool:
    """True iff `ref` resolves to an existing path under the skill tree
    or a sibling skill (one level up from the skill root).

    Search order:
    1. Absolute path (rare in docs but supported)
    2. Relative to md_file's directory
    3. Relative to skill root
    4. Strip leading skill-name component, retry under skill root
       (handles "slide-builder/foo/bar.md" written from parent perspective)
    5. Cross-skill: relative to skills root (handles "slide-qc/SKILL.md")
    6. Subtree Glob: bare filename matched anywhere under skill root
    """
    candidate = Path(ref.replace("\\", "/"))
    if candidate.is_absolute() and candidate.exists():
        return True
    if (md_file.parent / candidate).exists():
        return True
    if (_SKILL_ROOT / candidate).exists():
        return True
    parts = candidate.parts
    if parts and parts[0] == _SKILL_ROOT.name and (_SKILL_ROOT / Path(*parts[1:])).exists():
        return True
    # Cross-skill: skills/ root is the parent of the skill root.
    skills_root = _SKILL_ROOT.parent
    if (skills_root / candidate).exists():
        return True
    # Bare-filename subtree search: only meaningful when ref has no
    # directory component.
    if len(parts) == 1:
        # Use a constrained glob — rglob is O(tree) but the skill is small.
        for _ in _SKILL_ROOT.rglob(ref):
            return True
    return False


def check_doc_file_refs() -> list[str]:
    errors: list[str] = []
    md_files = [p for p in _SKILL_ROOT.rglob("*.md")
                if "_decisions" not in p.parts
                and "__pycache__" not in p.parts
                and "_audit" not in p.parts      # hangover dir, slated for deletion
                and "_backup" not in p.parts]    # hangover dir, slated for deletion
    refs_checked = 0
    refs_skipped_runtime = 0
    refs_skipped_deleted = 0
    refs_skipped_memory = 0
    dir_refs_checked = 0
    dir_refs_skipped = 0
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(f"doc refs: cannot read {md_file}: {exc}")
            continue
        # File-path refs
        for match in _DOC_REF_RE.finditer(text):
            ref = match.group(1)
            if not ref.endswith(_DOC_REF_EXTS):
                continue
            if ref.startswith(("http://", "https://", "mailto:", "#")):
                continue
            ref_name = Path(ref).name
            # Runtime prefix match (e.g., _session/..., mermaid-acme.json)
            if any(ref.startswith(p) for p in _RUNTIME_PREFIXES) or \
               any(ref_name.startswith(p) for p in _RUNTIME_PREFIXES):
                refs_skipped_runtime += 1
                continue
            # Runtime-artifact allowlist (output files, not source)
            if ref in _RUNTIME_ARTIFACTS or ref_name in _RUNTIME_ARTIFACTS:
                refs_skipped_runtime += 1
                continue
            # Intentionally-deleted-by-design allowlist (history docs
            # legitimately cite these as removed artifacts)
            if ref in _DELETED_BY_DESIGN or ref_name in _DELETED_BY_DESIGN:
                refs_skipped_deleted += 1
                continue
            # User-memory cross-context refs (live outside the skill)
            if any(ref_name.startswith(p) for p in _MEMORY_FILE_PREFIXES) and ref_name.endswith(".md"):
                refs_skipped_memory += 1
                continue
            refs_checked += 1
            if not _resolve_doc_ref(ref, md_file):
                rel = md_file.relative_to(_SKILL_ROOT)
                errors.append(
                    f"doc refs: {rel} cites {ref!r} but no such path exists "
                    f"under the skill tree or sibling skills"
                )
        # Directory-path refs (trailing slash) — catches the
        # `slide-builder_archived_2026-05-26/` class of phantom-archive ref
        for match in _DOC_DIR_REF_RE.finditer(text):
            dref = match.group(1)
            # Skip user-context dir refs (~/.claude/, OneDrive, etc.)
            if any(dref.startswith(p) for p in _DIR_USER_CONTEXT_PREFIXES):
                dir_refs_skipped += 1
                continue
            # Skip placeholder/template dir refs (slide_NN/, out/, etc.)
            if dref in _DIR_TEMPLATE_REFS:
                dir_refs_skipped += 1
                continue
            # Skip deletion-context dir refs (forensic citations)
            if dref in _DIR_DELETED_BY_DESIGN:
                dir_refs_skipped += 1
                continue
            # Skip if it's actually a file ref that happens to have a
            # trailing slash captured elsewhere — shouldn't happen with
            # the regex, but defensive
            if "." in dref.rstrip("/").split("/")[-1]:
                dir_refs_skipped += 1
                continue
            dir_refs_checked += 1
            # Resolve without the trailing slash
            dref_clean = dref.rstrip("/")
            if not _resolve_doc_ref(dref_clean, md_file):
                rel = md_file.relative_to(_SKILL_ROOT)
                errors.append(
                    f"doc refs (dir): {rel} cites {dref!r} but no such "
                    f"directory exists under the skill tree or sibling skills"
                )
    if not errors:
        _ok(
            f"doc file refs: {refs_checked} file refs + {dir_refs_checked} "
            f"dir refs resolve ({refs_skipped_runtime} runtime + "
            f"{refs_skipped_deleted} deleted-by-design + {refs_skipped_memory} "
            f"memory-context + {dir_refs_skipped} user-context skipped)"
        )
    return errors


# ---------------------------------------------------------------------------
# Check 7 — typing.get_type_hints() succeeds for every callable
# ---------------------------------------------------------------------------
#
# Drift class this prevents: `from __future__ import annotations` defers
# annotation evaluation, so `Optional[str]` without `from typing import
# Optional` runs fine at module load but breaks any code that calls
# `typing.get_type_hints(fn)`. Caught the `clean.py:149` Optional
# regression in the prior cycle (after manual investigation).

def check_type_hints_resolve() -> list[str]:
    import importlib
    import inspect
    import typing
    errors: list[str] = []
    targets = [
        "_paths", "_meta_schema", "_log",
        "build_deck", "finalize_deck", "compile_picks",
        "build_review", "build_gate_preview",
        "register_template", "clean", "diagnostic",
        "icon_helper", "render_mermaid",
    ]
    callables_checked = 0
    for mod_name in targets:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:
            # Module import already covered by check_pipeline_imports.
            # If it failed there, don't double-report; if it succeeded
            # there but fails here, something race-y is happening —
            # surface it.
            errors.append(f"type hints: cannot re-import {mod_name}: {exc}")
            continue
        for attr_name, attr in list(vars(mod).items()):
            if attr_name.startswith("_"):
                continue
            if not callable(attr):
                continue
            # Only inspect callables actually defined in this module
            # (skip re-exports / aliases of third-party stuff).
            try:
                defining = inspect.getmodule(attr)
                if defining is None or defining.__name__ != mod_name:
                    continue
            except Exception:
                continue
            try:
                typing.get_type_hints(attr)
                callables_checked += 1
            except Exception as exc:
                errors.append(
                    f"type hints: {mod_name}.{attr_name}: "
                    f"{type(exc).__name__}: {exc}"
                )
    if not errors:
        _ok(f"type hints: {callables_checked} callables across {len(targets)} modules resolve")
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
                  check_pipeline_imports,
                  check_install_sentinels,
                  check_doc_file_refs,
                  check_type_hints_resolve):
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
