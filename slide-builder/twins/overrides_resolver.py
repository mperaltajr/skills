"""
Pattern-aware overrides resolver.

For a picked pattern, walk its `shape_role_map` and produce a targeted dict
of `{shape_id: text}` overrides. Each shape_id gets content matched by its
semantic role (and grid index, when the shape_id is templated).

Key contract — every role resolver returns a 2-tuple:

    (text_or_none, is_content_role)

  text_or_none   — the resolved text to populate, or None if the brief
                   doesn't supply content for this shape
  is_content_role — True if this shape SHOULD be blanked when no override
                    is provided (so the builder default doesn't leak).
                    False for chrome / decoration / constant labels that
                    should keep their builder default.

The composer uses `is_content_role` to decide whether to blank an unmatched
shape. This replaces the regex-based heuristic in
composer._blank_unmatched_content_shapes — the role map is authoritative now.

Coverage notes:
  - Roles backed by the narrative brief schema (title / subtitle / cards /
    pillars / metrics / cover / sub_asks / convergence) are populated.
  - Roles for patterns that need brief fields the schema doesn't expose
    yet (risk / quadrant / glossary / compare-cell / io-grid / etc.) are
    marked content but resolve to None — they get blanked rather than
    leak the builder's hardcoded placeholder text.
  - Chrome roles (`chrome`, `decoration`) and constant labels
    (`cover-presented-label`, `primary-ask-label`) are preserved.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple

# (resolved_text, is_content_role)
Resolution = Tuple[Optional[str], bool]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PLACEHOLDER_RE = re.compile(r"\{[^}]+\}")
_INDEX_RE = re.compile(r"-(\d+)(?:-|$)")


def _substitute_index(template: str, idx: int) -> str:
    """Replace every {expr} placeholder in `template` with str(idx).

    Pattern templates from the catalog use varied placeholder forms:
      card-{n}-heading           -> card-1-heading
      legend-{i + 1}-label       -> legend-1-label
      cover-meta-{n}-label       -> cover-meta-1-label
    """
    return _PLACEHOLDER_RE.sub(str(idx), template)


def _extract_index(shape_id: str) -> Optional[int]:
    """Return the first numeric index found in a literal shape_id, e.g.,
    'card-2-heading' -> 2. None if no index present.
    """
    m = _INDEX_RE.search(shape_id)
    return int(m.group(1)) if m else None


def _cover(brief: Dict[str, Any]) -> Dict[str, Any]:
    """Return the cover dict from the brief (or {} if absent). Supports both
    nested `content.cover.*` and flat `content.*` cover authoring forms.
    """
    content = brief.get("content") or {}
    cover = content.get("cover") or {}
    if cover:
        return cover
    # Flat form: content.title / content.tagline / content.presenter etc.
    flat = {
        k: content.get(k)
        for k in ("title", "tagline", "subtitle", "presenter", "presented_by",
                  "client", "audience", "date", "eyebrow", "pre_label")
        if content.get(k) is not None
    }
    return flat


def _grid_items(brief: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the flat list of grid items for the slide, regardless of which
    container key the brief used (cards / pillars / columns / steps / panels /
    options / buckets / supporting_cards).
    """
    content = brief.get("content") or {}
    for key in ("cards", "pillars", "columns", "steps", "panels", "options",
                "buckets", "supporting_cards"):
        items = content.get(key)
        if isinstance(items, list) and items:
            return items
    return []


def _grid_field(brief: Dict[str, Any], shape_id: str, kind: str) -> Resolution:
    """Resolve a grid shape's text. `kind` is 'heading' | 'body' | 'label'."""
    items = _grid_items(brief)
    idx = _extract_index(shape_id)
    if idx is None or idx < 1 or idx > len(items):
        return (None, True)
    item = items[idx - 1]
    if not isinstance(item, dict):
        return (None, True)
    if kind == "heading":
        return (item.get("heading") or item.get("name") or item.get("title")
                or item.get("label"), True)
    if kind == "body":
        return (item.get("body") or item.get("description") or item.get("desc")
                or item.get("text"), True)
    if kind == "label":
        return (item.get("label") or item.get("eyebrow"), True)
    return (None, True)


def _metric_field(brief: Dict[str, Any], shape_id: str) -> Resolution:
    """Resolve a metric/kpi shape: metric-N-{label|value|delta|unit}."""
    content = brief.get("content") or {}
    metrics = content.get("metrics") or content.get("kpis") or []
    m = re.match(r"^(?:metric|kpi)-(\d+)-(label|value|delta|unit)$", shape_id)
    if not m or not isinstance(metrics, list):
        return (None, True)
    idx, field = int(m.group(1)), m.group(2)
    if idx < 1 or idx > len(metrics):
        return (None, True)
    item = metrics[idx - 1]
    if not isinstance(item, dict):
        return (None, True)
    val = item.get(field)
    return (str(val) if val is not None else None, True)


def _sub_ask_field(brief: Dict[str, Any], shape_id: str) -> Resolution:
    """Resolve a sub-ask shape: sub-ask-N-{label|body|num|meta}."""
    content = brief.get("content") or {}
    sub_asks = content.get("sub_asks") or []
    m = re.match(r"^sub-ask-(\d+)-(label|body|num|meta)$", shape_id)
    if not m:
        return (None, True)
    idx, field = int(m.group(1)), m.group(2)
    if idx < 1 or idx > len(sub_asks):
        return (None, True)
    item = sub_asks[idx - 1]
    if not isinstance(item, dict):
        return (None, True)
    if field == "num":
        # Auto-numbered chrome — keep builder default
        return (None, False)
    return (item.get(field), True)


def _cover_meta(brief: Dict[str, Any], shape_id: str) -> Resolution:
    """Resolve cover-meta-N shapes for the meta grid block.

    Builders use two conventions:
      A. Paired shapes: `cover-meta-N-label` + `cover-meta-N-value`
      B. Combined shape: `cover-meta-N` holding "<strong>LABEL</strong> value"

    Conventional ordering: 1 = presenter, 2 = client/audience, 3 = date.
    Patterns that need different ordering get blanked (brief doesn't supply
    their layout-specific meta).
    """
    cover = _cover(brief)
    presenter = cover.get("presenter") or cover.get("presented_by")
    client = cover.get("client") or cover.get("audience")
    date = cover.get("date")
    grid = []
    if presenter:
        grid.append(("PRESENTED BY", presenter))
    if client:
        grid.append(("PREPARED FOR", client))
    if date:
        grid.append(("DATE", date))

    # Form A: cover-meta-N-{label|value}
    m_pair = re.match(r"^cover-meta-(\d+)-(label|value)$", shape_id)
    if m_pair:
        idx, field = int(m_pair.group(1)), m_pair.group(2)
        if idx < 1 or idx > len(grid):
            return (None, True)
        label, value = grid[idx - 1]
        return ((label if field == "label" else value), True)

    # Form B: cover-meta-N (combined label + value)
    m_combined = re.match(r"^cover-meta-(\d+)$", shape_id)
    if m_combined:
        idx = int(m_combined.group(1))
        if idx < 1 or idx > len(grid):
            return (None, True)
        label, value = grid[idx - 1]
        return (f"<strong>{label}</strong>  {value}", True)

    # cover-meta with no index suffix at all → mark content (will blank)
    return (None, True)


def _chart_field(brief: Dict[str, Any], shape_id: str, key: str) -> Resolution:
    """Resolve chart-title / chart-source from optional brief.content fields."""
    content = brief.get("content") or {}
    val = content.get(key)
    return (str(val) if val else None, True)


# ---------------------------------------------------------------------------
# Role resolver table
# ---------------------------------------------------------------------------

# Each entry: role -> resolver(brief, shape_id) -> (text_or_none, is_content_role)
#
# Roles backed by the brief schema produce text. Roles whose brief schema is
# not yet defined (risk, glossary, quadrant, ...) return (None, True) so the
# composer's blanking pass empties them instead of leaking builder defaults.

ROLE_RESOLVERS: Dict[str, Callable[[Dict[str, Any], str], Resolution]] = {
    # Title / hero family — pull from narrative top-level
    "title": lambda b, sid: (b.get("governing_thought") or None, True),
    "subtitle": lambda b, sid: (b.get("so_what") or None, True),
    "eyebrow": lambda b, sid: ((b.get("content") or {}).get("eyebrow") or None, True),
    "headline": lambda b, sid: (b.get("governing_thought") or None, True),
    "hero-statement": lambda b, sid: (b.get("governing_thought") or None, True),
    "hero-context": lambda b, sid: (b.get("so_what") or None, True),
    "hero-attribution": lambda b, sid: (b.get("so_what") or None, True),
    "hero-statement-label": lambda b, sid: ((b.get("content") or {}).get("eyebrow") or None, True),
    "key-question": lambda b, sid: (b.get("governing_thought") or None, True),
    "anchor-statement": lambda b, sid: (b.get("governing_thought") or None, True),
    "subhead": lambda b, sid: (b.get("so_what") or None, True),
    "tagline": lambda b, sid: (_cover(b).get("tagline") or None, True),

    # Cover family
    "cover-deck-title": lambda b, sid: (_cover(b).get("title") or None, True),
    "cover-wordmark": lambda b, sid: (_cover(b).get("title") or None, True),
    "cover-tagline": lambda b, sid: (_cover(b).get("tagline") or None, True),
    "cover-subtitle": lambda b, sid: (
        _cover(b).get("subtitle") or _cover(b).get("tagline") or None, True),
    "cover-eyebrow": lambda b, sid: (
        _cover(b).get("eyebrow") or _cover(b).get("pre_label") or None, True),
    "cover-presenter": lambda b, sid: (
        _cover(b).get("presenter") or _cover(b).get("presented_by") or None, True),
    "cover-client-name": lambda b, sid: (
        _cover(b).get("client") or _cover(b).get("audience") or None, True),
    "cover-brand-name": lambda b, sid: (_cover(b).get("client") or None, True),
    "cover-date": lambda b, sid: (_cover(b).get("date") or None, True),
    # Constant label — preserve builder default ("PRESENTED BY" etc.)
    "cover-presented-label": lambda b, sid: (None, False),
    "cover-meta": _cover_meta,

    # Grid items (cards / pillars / columns / steps / panels / options / buckets)
    "grid-heading": lambda b, sid: _grid_field(b, sid, "heading"),
    "grid-body": lambda b, sid: _grid_field(b, sid, "body"),
    "grid-label": lambda b, sid: _grid_field(b, sid, "label"),
    "grid-other": lambda b, sid: (None, True),

    # Before/after comparison
    "compare": lambda b, sid: (None, True),
    "compare-header": lambda b, sid: (None, True),
    "compare-row-label": lambda b, sid: (None, True),
    "compare-cell": lambda b, sid: (None, True),

    # Metrics / KPI
    "metric": _metric_field,
    "kpi": _metric_field,

    # Asks
    "primary-ask": lambda b, sid: ((b.get("content") or {}).get("primary_ask") or None, True),
    "primary-ask-label": lambda b, sid: (None, False),  # constant chrome label
    "sub-ask": _sub_ask_field,

    # Convergence / takeaway
    "convergence": lambda b, sid: (b.get("so_what") or None, True),
    "takeaway": lambda b, sid: (b.get("so_what") or None, True),
    "convergence-detail": lambda b, sid: (None, True),

    # Charts
    "chart-title": lambda b, sid: _chart_field(b, sid, "chart_title"),
    "chart-source": lambda b, sid: _chart_field(b, sid, "chart_source"),
    "chart-data": lambda b, sid: (None, True),
    "chart-data-label": lambda b, sid: (None, True),
    "chart-canvas": lambda b, sid: (None, True),
    "chart-detail": lambda b, sid: (None, True),

    # Pattern-specific roles with no brief mapping yet — blank when not supplied
    "risk": lambda b, sid: (None, True),
    "opportunity": lambda b, sid: (None, True),
    "glossary": lambda b, sid: (None, True),
    "io-grid": lambda b, sid: (None, True),
    "quadrant": lambda b, sid: (None, True),
    "axis-label": lambda b, sid: (None, True),
    "table-header": lambda b, sid: (None, True),
    "table-cell": lambda b, sid: (None, True),
    "table-detail": lambda b, sid: (None, True),
    "legend": lambda b, sid: (None, True),
    "annotation": lambda b, sid: (None, True),
    "quote": lambda b, sid: (None, True),
    "vision": lambda b, sid: (None, True),
    "section": lambda b, sid: (None, True),
    "divider": lambda b, sid: (None, True),
    "toc": lambda b, sid: (None, True),
    "lane-label": lambda b, sid: (None, True),
    "lane-heading": lambda b, sid: (None, True),
    "lane-body": lambda b, sid: (None, True),
    "lane-outcome": lambda b, sid: (None, True),
    "memo": lambda b, sid: (None, True),
    "priority": lambda b, sid: (None, True),
    "hero-sub": lambda b, sid: (None, True),
    "hero-stat": lambda b, sid: (None, True),
    "generic-content": lambda b, sid: (None, True),
    "decoration": lambda b, sid: (None, True),
    "tag": lambda b, sid: (None, False),  # decorative chip labels stay as-is

    # Chrome / unknown — preserve builder default
    "chrome": lambda b, sid: (None, False),
    "unknown": lambda b, sid: (None, False),
}


# Roles that count as "content" — used by the composer's blanking pass.
# A shape whose role is in this set AND wasn't supplied an override gets
# blanked (so builder defaults can't leak).
CONTENT_ROLES = {
    role for role, fn in ROLE_RESOLVERS.items()
    # Probe each resolver with an empty brief; the role is "content" iff its
    # default tuple says so (second element True).
    if fn({}, "_probe_") and fn({}, "_probe_")[1]
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def pattern_aware_overrides(narrative_slide: Dict[str, Any],
                             pattern_entry: Dict[str, Any]) -> Dict[str, str]:
    """Compute pattern-aware overrides for a single slide.

    For each (shape_id_template, role) in pattern_entry's shape_role_map:
      - If the template has no {placeholder}, resolve directly.
      - If the template has placeholders, enumerate indices 1..MAX_GRID
        until the resolver returns None (signaling no more items).

    Returns a dict keyed by literal shape_ids (with placeholders substituted).
    Only shape_ids whose role resolved to non-None text are included.
    """
    role_map = pattern_entry.get("shape_role_map") or {}
    overrides: Dict[str, str] = {}

    for template, role in role_map.items():
        resolver = ROLE_RESOLVERS.get(role)
        if resolver is None:
            continue  # unknown role; preserve builder default
        if "{" not in template:
            text, _ = resolver(narrative_slide, template)
            if text:
                overrides[template] = str(text)
            continue
        # Templated — enumerate. Stop when a resolver returns None at idx,
        # signaling no more items at that index OR no brief content.
        for idx in range(1, 13):  # bound; no pattern uses >12 grid slots
            shape_id = _substitute_index(template, idx)
            text, _ = resolver(narrative_slide, shape_id)
            if text:
                overrides[shape_id] = str(text)
            elif idx > 1:
                # First miss after at least one hit → stop enumerating.
                # (idx=1 with None could just mean the brief lacks this role.)
                break
    return overrides


def role_for_shape(shape_role_map: Dict[str, str], shape_id: str) -> Optional[str]:
    """Look up a literal shape_id (e.g., 'card-2-heading') in a role_map that
    uses templated keys (e.g., 'card-{n}-heading'). Returns the role name or
    None if no template matches.
    """
    # Fast path: exact match (non-templated entries)
    if shape_id in shape_role_map:
        return shape_role_map[shape_id]
    # Template match — convert template to regex, try each
    for template, role in shape_role_map.items():
        if "{" not in template:
            continue
        pattern = _PLACEHOLDER_RE.sub(r"\\d+", re.escape(template).replace(r"\{", "{").replace(r"\}", "}"))
        # The substitution turned escaped {...} into literal regex; re-escape
        # any leftover regex metacharacters by going through escape after sub.
        # Simpler: build pattern manually.
        pat = "^" + _PLACEHOLDER_RE.sub(r"\\d+", re.escape(template)) + "$"
        # re.escape escaped the braces; the _PLACEHOLDER_RE on escaped string
        # won't match. Build from the unescaped template instead.
        parts = []
        last = 0
        for m in _PLACEHOLDER_RE.finditer(template):
            parts.append(re.escape(template[last:m.start()]))
            parts.append(r"\d+")
            last = m.end()
        parts.append(re.escape(template[last:]))
        pat = "^" + "".join(parts) + "$"
        if re.match(pat, shape_id):
            return role
    return None


def is_content_role(role: Optional[str]) -> bool:
    """True if a role represents brief-driven content (should be blanked when
    no override is supplied). False for chrome / decoration / constant labels.
    """
    if role is None:
        return False
    return role in CONTENT_ROLES


if __name__ == "__main__":
    # Smoke test
    import json
    sample_brief = {
        "slide_num": 2,
        "governing_thought": "Three failure modes consultants hit.",
        "so_what": "The fix is structural, not personal.",
        "content": {
            "cards": [
                {"heading": "Too much", "body": "Volume of analysis."},
                {"heading": "Too many cooks", "body": "Every collaborator has a view."},
                {"heading": "Buried recos", "body": "Audience needs next step."},
            ],
        },
    }
    sample_pattern = {
        "shape_role_map": {
            "title": "title",
            "subtitle": "subtitle",
            "card-{n}-heading": "grid-heading",
            "card-{n}-body": "grid-body",
            "card-{n}-icon": "chrome",
            "convergence": "convergence",
            "brand-rule": "chrome",
        }
    }
    out = pattern_aware_overrides(sample_brief, sample_pattern)
    print(json.dumps(out, indent=2))
