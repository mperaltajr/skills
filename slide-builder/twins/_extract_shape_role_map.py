"""
One-shot extraction script: walk every twins/builders/build_*.py, find every
text-emitting call (add_text, add_title_block, add_convergence, add_source,
add_footnote), recover the shape_id template and the default text, then
classify each shape_id into a semantic role.

Output written to:
  - twins/_extracted_shape_role_map.json  (audit artifact)
  - twins/pattern_catalog.yaml             (each entry gets a shape_role_map field)

Run from the slide-builder directory:
  cd %USERPROFILE%\\.claude\\skills\\slide-builder
  python -m twins._extract_shape_role_map

Re-runnable — overwrites the audit JSON and the catalog field. Safe to run
on a clean working tree (commit before to make diffs easy to review).
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

BUILDERS_DIR = Path(__file__).resolve().parent / "builders"
CATALOG_PATH = Path(__file__).resolve().parent / "pattern_catalog.yaml"
AUDIT_PATH = Path(__file__).resolve().parent / "_extracted_shape_role_map.json"


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _func_name(node: ast.expr) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _literal(node: ast.AST) -> Optional[str]:
    """Best-effort extract a literal string from an AST node. Returns None
    for non-string / dynamic expressions.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        # f-string: render only the literal parts, keep {var} as {{var}}
        parts: List[str] = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            elif isinstance(v, ast.FormattedValue):
                src = ast.unparse(v.value)
                parts.append("{" + src + "}")
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        l = _literal(node.left)
        r = _literal(node.right)
        if l is not None and r is not None:
            return l + r
    return None


def _kwarg(node: ast.Call, name: str) -> Optional[ast.AST]:
    for kw in node.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _arg(node: ast.Call, idx: int) -> Optional[ast.AST]:
    if idx < len(node.args):
        return node.args[idx]
    return None


# ---------------------------------------------------------------------------
# Builder extraction
# ---------------------------------------------------------------------------

def extract_from_builder(path: Path) -> List[Dict[str, Any]]:
    """Return a list of dicts: [{shape_id, default_text, source_fn}]."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [{"_error": f"parse failed: {e}", "_file": str(path)}]

    rows: List[Dict[str, Any]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = _func_name(node.func)
        if fn is None:
            continue

        if fn == "add_text":
            # add_text(slide, shape_id, text, ...)
            sid = _literal(_arg(node, 1)) if len(node.args) > 1 else None
            txt = _literal(_arg(node, 2)) if len(node.args) > 2 else None
            if sid is None:
                # try kwargs (rare for add_text)
                sid_kw = _kwarg(node, "shape_id")
                if sid_kw:
                    sid = _literal(sid_kw)
            if sid:
                rows.append({"shape_id": sid, "default_text": txt, "source_fn": "add_text"})

        elif fn == "add_title_block":
            # add_title_block(slide, title=..., subtitle=...)
            t = _kwarg(node, "title") or _arg(node, 1)
            s = _kwarg(node, "subtitle") or _arg(node, 2)
            rows.append({"shape_id": "title", "default_text": _literal(t) if t else None, "source_fn": "add_title_block"})
            rows.append({"shape_id": "subtitle", "default_text": _literal(s) if s else None, "source_fn": "add_title_block"})

        elif fn == "add_convergence":
            t = _arg(node, 1)
            rows.append({"shape_id": "convergence", "default_text": _literal(t) if t else None, "source_fn": "add_convergence"})

        elif fn == "add_source":
            t = _arg(node, 1)
            rows.append({"shape_id": "source", "default_text": _literal(t) if t else None, "source_fn": "add_source"})

        elif fn == "add_footnote":
            n_node = _arg(node, 1)
            t_node = _arg(node, 2)
            n_val = None
            if isinstance(n_node, ast.Constant):
                n_val = n_node.value
            shape_id = f"footnote-{n_val}" if n_val is not None else "footnote-N"
            rows.append({"shape_id": shape_id, "default_text": _literal(t_node) if t_node else None, "source_fn": "add_footnote"})

        elif fn == "add_eyebrow":
            # Pattern-library convention: add_eyebrow(slide, text)
            t = _arg(node, 1)
            rows.append({"shape_id": "eyebrow", "default_text": _literal(t) if t else None, "source_fn": "add_eyebrow"})

    # De-duplicate by shape_id (keep first occurrence)
    seen = set()
    dedup = []
    for r in rows:
        sid = r.get("shape_id")
        if sid in seen:
            continue
        seen.add(sid)
        dedup.append(r)
    return dedup


# ---------------------------------------------------------------------------
# Role classification
# ---------------------------------------------------------------------------

# Ordered rules — first match wins. Patterns checked against the shape_id.
# The role names map to the broadcaster's content keys where possible.
_ROLE_RULES = [
    # Chrome (NOT overridable by brief — left as-is, not blanked)
    (r"^(source|footnote-\d+|footnote-N|page-(number|num)|brand-rule|brand-bar|"
     r"accenture-bug|client-logo|wordmark-chrome)$", "chrome"),
    # Title/subtitle/etc.
    (r"^title$", "title"),
    (r"^subtitle$", "subtitle"),
    (r"^eyebrow$", "eyebrow"),
    (r"^headline$", "headline"),
    (r"^hero-statement$", "hero-statement"),
    (r"^hero-context$", "hero-context"),
    (r"^hero-attribution$", "hero-attribution"),
    (r"^key-question$", "key-question"),
    (r"^anchor-statement$", "anchor-statement"),
    (r"^tagline$", "tagline"),
    # Cover-family
    (r"^cover-deck-title$", "cover-deck-title"),
    (r"^cover-title$", "cover-deck-title"),
    (r"^cover-wordmark$", "cover-wordmark"),
    (r"^cover-tagline$", "cover-tagline"),
    (r"^cover-subtitle$", "cover-subtitle"),
    (r"^cover-eyebrow$", "cover-eyebrow"),
    (r"^cover-pre-label$", "cover-eyebrow"),
    (r"^cover-presenter$", "cover-presenter"),
    (r"^cover-presented-name$", "cover-presenter"),
    (r"^cover-presented-label$", "cover-presented-label"),
    (r"^cover-client-name$", "cover-client-name"),
    (r"^cover-brand-name$", "cover-brand-name"),
    (r"^cover-date$", "cover-date"),
    (r"^cover-meta(-\{[^}]+\})?(-\d+)?(-label|-value)?$", "cover-meta"),
    # Grid items
    (r"^(card|panel|column|pillar|step|option|bucket|col)-(\d+|\{[^}]+\})-heading$", "grid-heading"),
    (r"^(card|panel|column|pillar|step|option|bucket|col)-(\d+|\{[^}]+\})-name$", "grid-heading"),
    (r"^(card|panel|column|pillar|step|option|bucket|col)-(\d+|\{[^}]+\})-title$", "grid-heading"),
    (r"^(card|panel|column|pillar|step|option|bucket|col)-(\d+|\{[^}]+\})-body$", "grid-body"),
    (r"^(card|panel|column|pillar|step|option|bucket|col)-(\d+|\{[^}]+\})-description$", "grid-body"),
    (r"^(card|panel|column|pillar|step|option|bucket|col)-(\d+|\{[^}]+\})-label$", "grid-label"),
    (r"^(card|panel|column|pillar|step|option|bucket|col)-(\d+|\{[^}]+\})-eyebrow$", "grid-label"),
    (r"^(card|panel|column|pillar|step|option|bucket|col)-(\d+|\{[^}]+\})-.*", "grid-other"),
    # Before/after comparison
    (r"^(before|after)-panel-(heading|body|label)$", "compare"),
    (r"^(before|after)-(heading|body|label)$", "compare"),
    # Metrics
    (r"^metric-(\d+|\{[^}]+\})-(label|value|delta)$", "metric"),
    # Asks
    (r"^sub-ask-(\d+|\{[^}]+\})-(label|body)$", "sub-ask"),
    (r"^primary-ask-text$", "primary-ask"),
    # Convergence / takeaway band
    (r"^convergence$", "convergence"),
    (r"^takeaway$", "takeaway"),
    (r"^convergence-mark$", "convergence-detail"),
    # Convergence chrome (bg, divider, etc.)
    (r"^conv-.*-bg$", "chrome"),
    (r"^conv-.*", "convergence-detail"),
    # Charts
    (r"^chart-title$", "chart-title"),
    (r"^chart-source$", "chart-source"),
    (r"^chart-canvas-(label|placeholder)$", "chart-canvas"),
    (r"^chart-.*", "chart-detail"),
    # Bars / lines / dots
    (r"^(bar|line|dot|point|node)-(\d+|\{[^}]+\})-(label|value|name)$", "chart-data-label"),
    (r"^(bar|line|dot|point|node)-(\d+|\{[^}]+\}).*", "chart-data"),
    # Tables
    (r"^table-col-(\d+|\{[^}]+\})-header$", "table-header"),
    (r"^table-row-(\d+|\{[^}]+\})-(cell|num)-?\d*$", "table-cell"),
    (r"^table-row-(\d+|\{[^}]+\})-cell-(\d+|\{[^}]+\})$", "table-cell"),
    (r"^table-.*-header$", "table-header"),
    (r"^table-row-.*", "table-cell"),
    (r"^table-.*", "table-detail"),
    # Legends
    (r"^legend-title$", "legend"),
    (r"^legend-(\d+|\{[^}]+\})-(label|value)$", "legend"),
    (r"^legend-.*", "legend"),
    # Subhead / sub-headline
    (r"^subhead(-.*)?$", "subhead"),
    (r"^sub-head(line)?(-.*)?$", "subhead"),
    # Annotations / callouts
    (r"^annot-(header|sub|body|title|label)$", "annotation"),
    (r"^annot-(\d+|\{[^}]+\})-(header|sub|body|title|label)$", "annotation"),
    (r"^annot-.*", "annotation"),
    (r"^callout-.*", "annotation"),
    # Quotes
    (r"^quote-(mark|text|attribution|author)$", "quote"),
    (r"^quote-.*", "quote"),
    # Quadrants / 2x2 axes
    (r"^quadrant-(x|y)-(axis-label|high|low)$", "axis-label"),
    (r"^quadrant-(\d+|\{[^}]+\}|.*)-(name|label|body)$", "quadrant"),
    (r"^quadrant-.*", "quadrant"),
    # Priorities / rankings
    (r"^priority-(\d+|\{[^}]+\})-(num|text|label|body)$", "priority"),
    (r"^priority-.*", "priority"),
    # Vision / mission text blocks
    (r"^vision-(label|text|body|title)$", "vision"),
    (r"^vision-.*", "vision"),
    # Photo / image chrome
    (r"^photo-.*", "chrome"),
    # Extra ask label
    (r"^primary-ask-label$", "primary-ask-label"),
    # Metric units (cousin of metric)
    (r"^metric-(\d+|\{[^}]+\})-unit$", "metric"),
    # Compare-column patterns (binary or N-way comparison tables)
    (r"^compare-col-(\d+|\{[^}]+\})-header$", "compare-header"),
    (r"^compare-col-(\d+|\{[^}]+\})-meta$", "compare-header"),
    (r"^compare-row-(\d+|\{[^}]+\})-label$", "compare-row-label"),
    (r"^compare-row-(\d+|\{[^}]+\})-col-(\d+|\{[^}]+\})-cell$", "compare-cell"),
    (r"^compare-.*", "compare"),
    # Section dividers
    (r"^divider-(title|numeral|section-label|subtitle)$", "divider"),
    (r"^divider-.*", "divider"),
    # TOC
    (r"^toc-(\d+|\{[^}]+\})-(num|title|desc)$", "toc"),
    (r"^toc-.*", "toc"),
    # Sections (numbered)
    (r"^section-(\d+|\{[^}]+\})-(num|name|body|label|title)$", "section"),
    (r"^section-.*", "section"),
    # Hero stats / hero subs
    (r"^hero-stat-(label|value|caption|unit|delta)$", "hero-stat"),
    (r"^hero-stat-.*", "hero-stat"),
    (r"^hero-sub-(\d+|\{[^}]+\})-(label|text|body)$", "hero-sub"),
    (r"^hero-statement-label$", "hero-statement-label"),
    # KPI dashboard (alt of metric)
    (r"^kpi-(\d+|\{[^}]+\})-(label|value|delta|unit)$", "kpi"),
    (r"^kpi-.*", "kpi"),
    # Output / input grids
    (r"^(output|input)-(\d+|\{[^}]+\})-(label|text|body|name)$", "io-grid"),
    # Risk / opportunity grids
    (r"^risk-(\d+|\{[^}]+\})-(desc|badge|note|name|label|body)$", "risk"),
    (r"^opp-(\d+|\{[^}]+\})-(desc|badge|note|name|label|body)$", "opportunity"),
    # Glossary / terms
    (r"^term-(\d+|\{[^}]+\})-(label|def|name|body)$", "glossary"),
    # Sub-ask numerals + meta (extends existing sub-ask)
    (r"^sub-ask-(\d+|\{[^}]+\})-(num|meta)$", "sub-ask"),
    # Generic row / col headers
    (r"^col-header-(\d+|\{[^}]+\})$", "table-header"),
    (r"^row-(\d+|\{[^}]+\})-(desc|label|body)$", "table-cell"),
    # Generic-prefix patterns (parameterized shape IDs)
    (r"^\{[^}]+\}-(heading|body|eyebrow|label|name|title|text)$", "generic-content"),
    # Eyebrow variants
    (r"^eyebrow-(meta|label|sub)$", "eyebrow"),
    # Tags (small chips like "PILLARS" / "METRICS")
    (r"^tag-.*", "tag"),
    # Background / decoration
    (r".*-bg$", "chrome"),
    (r".*-accent$", "chrome"),
    (r".*-icon$", "chrome"),
    (r".*-rule$", "chrome"),
    (r".*-divider$", "chrome"),
    (r".*-pill-.*", "decoration"),
    (r".*-arrow-.*", "chrome"),
    (r".*-stem$", "chrome"),
    (r".*-head$", "chrome"),
    # Lane / track labels
    (r"^lane-.*-(tag|label|name)$", "lane-label"),
    (r"^path-.*-eyebrow$", "lane-label"),
    (r"^path-.*-outcome$", "lane-outcome"),
    (r"^path-.*-title$", "lane-heading"),
    (r"^path-.*-desc$", "lane-body"),
    # Memo / executive briefing
    (r"^memo-.*-(label|value)$", "memo"),
    (r"^memo-.*", "memo"),
]


def classify_shape_id(shape_id: str) -> str:
    """Return the semantic role for a shape_id template. Falls back to
    'unknown' when no rule matches — those should be reviewed and either
    added to the rules or marked as chrome.
    """
    for pattern, role in _ROLE_RULES:
        if re.match(pattern, shape_id):
            return role
    return "unknown"


# ---------------------------------------------------------------------------
# Catalog stem ↔ builder file mapping
# ---------------------------------------------------------------------------

def _builder_filename_for_stem(stem: str) -> Optional[str]:
    """Map a catalog key (e.g., '1_anchor-with-cards-icons' or '1d_*') to its
    builder filename ('build_01.py' or 'build_01d.py' — usually).

    Conventions seen in twins/builders/:
      - 1_  -> build_01.py
      - 1d_ -> build_01d.py OR sometimes shares build_01.py with a dark flag
      - 10_ -> build_10.py
      - 100_ -> build_100.py
    """
    m = re.match(r"^(\d+)(d?)_", stem)
    if not m:
        return None
    num, dark = m.group(1), m.group(2)
    # Zero-pad single-digit numbers to 2 chars
    if len(num) == 1:
        num = "0" + num
    candidates = [f"build_{num}{dark}.py", f"build_{num}.py"]
    for c in candidates:
        if (BUILDERS_DIR / c).exists():
            return c
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    builders = sorted(BUILDERS_DIR.glob("build_*.py"))
    print(f"Scanning {len(builders)} builders...")

    # extracted: builder_filename -> [{shape_id, default_text, source_fn}, ...]
    extracted: Dict[str, List[Dict[str, Any]]] = {}
    for bp in builders:
        rows = extract_from_builder(bp)
        extracted[bp.name] = rows

    # Build shape_role_map per catalog entry
    print(f"\nLoading catalog from {CATALOG_PATH}")
    catalog = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8")) or {}
    print(f"Catalog has {len(catalog)} entries.")

    unknown_ids: Dict[str, int] = {}  # shape_id -> occurrence count
    coverage: Dict[str, int] = {}     # role -> entry count
    builder_misses: List[str] = []    # catalog stems without a matching builder

    for stem, entry in catalog.items():
        if not isinstance(entry, dict):
            continue
        bf = _builder_filename_for_stem(stem)
        if bf is None or bf not in extracted:
            builder_misses.append(stem)
            entry["shape_role_map"] = {}
            continue
        role_map: Dict[str, str] = {}
        for row in extracted[bf]:
            sid = row.get("shape_id")
            if not sid:
                continue
            role = classify_shape_id(sid)
            role_map[sid] = role
            if role == "unknown":
                unknown_ids[sid] = unknown_ids.get(sid, 0) + 1
            coverage[role] = coverage.get(role, 0) + 1
        entry["shape_role_map"] = role_map

    # Write audit JSON
    audit = {
        "summary": {
            "builders_scanned": len(builders),
            "catalog_entries": len(catalog),
            "entries_without_builder": len(builder_misses),
            "role_coverage": coverage,
            "unknown_shape_id_count": len(unknown_ids),
        },
        "builder_misses": builder_misses,
        "unknown_shape_ids": dict(sorted(unknown_ids.items(), key=lambda x: -x[1])),
        "per_builder": extracted,
    }
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote audit: {AUDIT_PATH}")
    print(f"  builders scanned:           {len(builders)}")
    print(f"  catalog entries:            {len(catalog)}")
    print(f"  entries without builder:    {len(builder_misses)}")
    print(f"  role coverage:              {coverage}")
    print(f"  unknown shape_id templates: {len(unknown_ids)} (top 10:)")
    for sid, n in list(sorted(unknown_ids.items(), key=lambda x: -x[1]))[:10]:
        print(f"    {n:>4}× {sid}")

    # Write catalog (preserves field order on existing entries)
    print(f"\nWriting catalog with shape_role_map to {CATALOG_PATH}")
    CATALOG_PATH.write_text(
        yaml.safe_dump(catalog, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )
    print("Done.")


if __name__ == "__main__":
    main()
