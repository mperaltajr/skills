"""
Pattern selector.

Given a slide brief (deck type + intent tags + structural shape), score every
approved pattern in the catalog and return the top N candidates so the user
can pick from three structurally distinct options.

Scoring axes (in priority order):
  1. Intent-tag overlap — exact tag matches between brief and pattern
  2. Deck-type compatibility — does the pattern belong to this deck type?
  3. Slot fit — does the pattern have enough cards/metrics/rows for the content?
  4. Structural variety — when returning top N, prefer N STRUCTURALLY DIFFERENT
     families/layouts rather than three near-duplicates

Usage:
  from twins.selector import load_catalog, propose_options

  catalog = load_catalog()
  options = propose_options(catalog, slide_brief={
      "intent_tags": ["problem-with-3-causes", "anchored-with-evidence"],
      "deck_type": "capability-pitch",
      "slots": {"cards": 3, "title": True, "subtitle": True},
      "structural_hint": "cards",   # optional — biases toward this family
  }, top_n=3)
  # → [{"pattern": "01_anchor-with-cards-icons", "score": 8, "thumbnail": "..."}, ...]
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml


CATALOG_PATH = Path(__file__).resolve().parent / "pattern_catalog.yaml"
PNG_ROOT = Path(__file__).resolve().parent.parent / "_renders" / "twins" / "_pngs"

# QC findings ledger — defaults to <skills-root>/slide-qc/_quality-ledger.yaml.
# Override with the SLIDE_QC_LEDGER env var. Returns an empty ledger if the
# file doesn't exist, so a fresh clone with no ledger still works.
_LEDGER_DEFAULT = (
    Path(__file__).resolve().parents[2] / "slide-qc" / "_quality-ledger.yaml"
)


def load_quality_ledger() -> Dict[str, Any]:
    """Load the QC findings ledger. Returns {} if the ledger doesn't exist yet."""
    p = Path(os.getenv("SLIDE_QC_LEDGER", str(_LEDGER_DEFAULT)))
    if not p.exists():
        return {}
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    data.pop("_meta", None)
    return data


def _open_findings_by_severity(ledger: Dict[str, Any], stem: str):
    """Return (n_critical, n_major) open finding counts for a pattern stem."""
    block = ledger.get(stem) or {}
    n_crit = n_major = 0
    for f in block.get("findings", []):
        if f.get("status") != "open":
            continue
        sev = f.get("severity", "")
        if sev == "critical":
            n_crit += 1
        elif sev == "major":
            n_major += 1
    return n_crit, n_major


def load_catalog(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load pattern_catalog.yaml. Returns dict keyed by pattern stem
    (e.g., '01_anchor-with-cards-icons') with metadata values.
    """
    path = Path(path) if path else CATALOG_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Pattern catalog not found at {path}. "
            "Build it first by tagging the approved patterns."
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Catalog must be a YAML mapping; got {type(data)}")
    return data


_RHYTHM_TO_EMPHASIS = {
    "conclusion-dominant": "the_conclusion",
    "contrast-dominant": "the_contrast",
    "data-dominant": "the_data",
    "evidence-dominant": "the_evidence",
    "ask-dominant": "the_ask",
    "numbers-dominant": "the_numbers",
    # process / framework don't map to editorial_emphasis; handled via family boost.
}

_SHAPE_NORMALIZE = {
    "2-column": "two-column",
    "two-col": "two-column",
    "2col": "two-column",
    "3-column": "three-column",
    "three-col": "three-column",
    "3col": "three-column",
    "4-column": "four-column",
    "four-col": "four-column",
    "5-column": "five-column",
    "five-col": "five-column",
    "2x2": "2x2-grid",
    "quadrant": "2x2-grid",
}


def _normalize_shape(s: str) -> str:
    s = (s or "").strip().lower()
    return _SHAPE_NORMALIZE.get(s, s)


def _score_pattern(entry: Dict[str, Any], brief: Dict[str, Any]) -> int:
    """Return an integer fitness score for a pattern entry given the brief.

    Score components:
      +5 per intent-tag overlap (strongest signal)
      +4 per editorial_emphasis overlap (storyline-helper alignment)
      +3 if deck_type matches (or pattern allows "all")
      +2 if structural_hint matches the family or layout
      +2 per good_for match against brief.so_what or brief.intent
      +1 per matching slot type that fits within the pattern's capacity
      -3 if any required slot exceeds the pattern's capacity (over-fill)
      -4 per bad_for match against brief.so_what or brief.intent (anti-pattern)
      +6 if visual_rhythm steers toward this pattern's editorial_emphasis/family
     +10 if mandatory_shape exactly matches this pattern's layout
    """
    score = 0

    brief_tags: Set[str] = set(brief.get("intent_tags") or [])
    pat_tags: Set[str] = set(entry.get("intent_tags") or [])
    score += 5 * len(brief_tags & pat_tags)

    # editorial_emphasis match — single most authoritative storyline-helper signal
    brief_emph: Set[str] = set(brief.get("editorial_emphasis") or [])
    pat_emph: Set[str] = set(entry.get("editorial_emphasis") or [])
    score += 4 * len(brief_emph & pat_emph)

    deck_type = brief.get("deck_type")
    pat_decks = set(entry.get("deck_types") or [])
    if deck_type and (deck_type in pat_decks or "all" in pat_decks):
        score += 3

    hint = (brief.get("structural_hint") or "").lower()
    if hint:
        if hint in (entry.get("family") or "").lower():
            score += 2
        elif hint in (entry.get("layout") or "").lower():
            score += 2

    # good_for / bad_for keyword matching against brief.so_what + brief.intent
    so_what = (brief.get("so_what") or "").lower()
    intent_text = (brief.get("intent") or "").lower()
    haystack = f"{so_what} {intent_text}"
    if haystack.strip():
        def _flatten(item):
            """Coerce an entry's good_for/bad_for item to a single string.
            Most are strings; a few catalog entries used dict form. Be robust."""
            if isinstance(item, str):
                return item
            if isinstance(item, dict):
                # Flatten {key: value} pairs into "key value" string.
                return " ".join(f"{k} {v}" for k, v in item.items())
            if isinstance(item, list):
                return " ".join(str(x) for x in item)
            return str(item)

        for good in entry.get("good_for") or []:
            text = _flatten(good)
            # Match if any 2+ significant words from `good` appear in the haystack.
            good_words = [w for w in text.lower().split() if len(w) > 3]
            if good_words and sum(1 for w in good_words if w in haystack) >= 2:
                score += 2
                break
        for bad in entry.get("bad_for") or []:
            text = _flatten(bad)
            bad_words = [w for w in text.lower().split() if len(w) > 3]
            if bad_words and sum(1 for w in bad_words if w in haystack) >= 2:
                score -= 4
                break

    # P1: visual_rhythm — steer toward patterns whose emphasis/family aligns
    rhythm = (brief.get("visual_rhythm") or "").strip().lower()
    if rhythm:
        rhythm_emph = _RHYTHM_TO_EMPHASIS.get(rhythm)
        if rhythm_emph and rhythm_emph in pat_emph:
            score += 6
        # Family boost for rhythms without emphasis mapping
        if rhythm == "process-dominant" and (entry.get("family") or "").lower() in ("process", "timeline", "phased"):
            score += 6
        if rhythm == "framework-dominant" and (entry.get("family") or "").lower() in ("framework", "pillars"):
            score += 6

    # P1: mandatory_shape — hard boost when layout matches exactly
    mand = _normalize_shape(brief.get("mandatory_shape") or "")
    if mand:
        if mand == _normalize_shape(entry.get("layout") or ""):
            score += 10

    # Slot fit
    brief_slots = brief.get("slots") or {}
    pat_slots = entry.get("slots") or {}
    for slot, val in brief_slots.items():
        if val is True or val is False:
            # Boolean slot — pattern needs to support it
            if pat_slots.get(slot) is True or pat_slots.get(slot, False):
                score += 1
        elif isinstance(val, (int, float)):
            cap = pat_slots.get(slot)
            if isinstance(cap, (int, float)):
                if cap >= val:
                    score += 1
                elif cap < val:
                    score -= 3
            else:
                score -= 1

    # Path A++ capacity check — penalize patterns whose role map can't carry
    # the brief's content count. Empirically: pattern 314 has 2 content
    # shapes in role_map; brief gives 2 cards × heading+body = 4 content
    # fields. Today's selector picks 314 anyway because intent_tags match.
    # The capacity check penalizes (heavily) so a thinner-coverage pattern
    # is preferred when content density is high.
    import re as _re
    role_map = entry.get("shape_role_map") or {}
    # Count grid-content role keys (heading/body/label/etc. on indexed shapes)
    content_role_count = sum(
        1 for sid in role_map
        if _re.match(r"^(card|panel|column|pillar|step|option|bucket|col|compare-col|compare-row|memo|sig|meta|body-p|decision|option-\d+-row)", sid)
    )
    # Count brief content density
    brief_content = brief.get("content") or {}
    brief_card_count = 0
    for key in ("cards", "pillars", "columns", "panels", "steps", "buckets", "options"):
        items = brief_content.get(key) or []
        if isinstance(items, list) and items:
            brief_card_count = max(brief_card_count, len(items))
    # Per-card fields supplied (heading + body + label)
    fields_per_card = 0
    if brief_card_count > 0:
        sample = (
            brief_content.get("cards") or brief_content.get("pillars")
            or brief_content.get("columns") or brief_content.get("panels") or []
        )[0]
        if isinstance(sample, dict):
            fields_per_card = sum(1 for k in ("heading", "name", "title", "body", "description", "label") if sample.get(k))
    brief_content_demand = brief_card_count * fields_per_card
    # Penalize when pattern can't carry the load
    if brief_content_demand > 0:
        if content_role_count == 0:
            # No content roles at all in a pattern picked for card-heavy brief
            score -= 10
        elif content_role_count < brief_content_demand // 2:
            # Less than half coverage
            score -= 6
        elif content_role_count < brief_content_demand:
            # Some coverage but insufficient
            score -= 3

    return score


def _light_dark_stem(stem: str) -> str:
    """Normalize a stem so a pattern and its dark twin share the same key.

    Catalog convention: `Nd_*` is the dark variant of `N_*` (e.g., `1_*` and
    `1d_*`). Light/dark variants of the same pattern look identical to a
    reviewer and shouldn't both appear in the top-3 options.
    """
    if len(stem) >= 3 and stem[0].isdigit():
        i = 0
        while i < len(stem) and stem[i].isdigit():
            i += 1
        if i < len(stem) and stem[i] == "d":
            return stem[:i] + stem[i+1:]
    return stem


def _is_dark_twin_of_picked(picked: List[Dict[str, Any]], candidate_stem: str) -> bool:
    """True if `candidate_stem` is the light/dark twin of any already-picked
    pattern (e.g., `1d_anchor-...` when `1_anchor-...` is picked, or vice
    versa). Used to prevent showing both variants as separate options.
    """
    cnorm = _light_dark_stem(candidate_stem)
    for p in picked:
        if _light_dark_stem(p["pattern"]) == cnorm:
            return True
    return False


def _layout_distinct_within_family(picked: List[Dict[str, Any]], candidate_entry: Dict[str, Any],
                                    candidate_stem: str = "") -> bool:
    """True if `candidate_entry` is in the same family as the first picked
    option, uses a DIFFERENT layout, AND is not a light/dark twin of any
    already-picked pattern — the variety-within-family rule.

    The 3 options for a slide should be three visual treatments of the same
    intent (e.g., 2-bucket horizontal / 2-bucket vertical / 2-bucket cards),
    not three unrelated families AND not the same pattern shown in light and
    dark. The selector picks the top scorer first; subsequent picks must
    share that family, bring a new layout, and not duplicate the picked
    pattern's light/dark twin.

    Falls back via `propose_options`'s relaxation passes when no more
    same-family-different-layout candidates exist.
    """
    if not picked:
        return True  # First pick has no family constraint yet
    target_family = picked[0]["entry"].get("family")
    cf = candidate_entry.get("family")
    if cf != target_family:
        return False  # Must share family with #1
    cl = candidate_entry.get("layout")
    for p in picked:
        if p["entry"].get("layout") == cl:
            return False  # Layout already used
    if candidate_stem and _is_dark_twin_of_picked(picked, candidate_stem):
        return False  # Already showing this pattern's light/dark twin
    return True


def _same_family(picked: List[Dict[str, Any]], candidate_entry: Dict[str, Any],
                  candidate_stem: str = "") -> bool:
    """True if `candidate_entry` shares the family of the first pick AND is
    not a light/dark twin of an already-picked pattern. Layout repeats are
    allowed — used by the relaxation pass when the family is too thin to
    give 3 distinct layouts.
    """
    if not picked:
        return True
    if candidate_entry.get("family") != picked[0]["entry"].get("family"):
        return False
    if candidate_stem and _is_dark_twin_of_picked(picked, candidate_stem):
        return False
    return True


# Backwards-compat alias for any external callers.
_structurally_distinct = _layout_distinct_within_family


def propose_options(catalog: Dict[str, Any], slide_brief: Dict[str, Any],
                    top_n: int = 3, require_distinct: bool = True,
                    ledger: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return top_n pattern recommendations, sorted by descending fit score.

    When `require_distinct=True`, candidates that share both family and layout
    with an already-picked option are skipped — yielding structurally varied
    choices for the user. Falls back to relaxing this constraint if fewer than
    top_n distinct candidates exist.

    When `ledger` is provided (or auto-loaded from SLIDE_QC_LEDGER), patterns
    with open Critical findings are excluded entirely; open Majors incur -5 each.

    Returns a list of dicts:
      {"pattern": <stem>, "score": <int>, "entry": <catalog entry>,
       "thumbnail": <Path to PNG or None>}
    """
    if ledger is None:
        ledger = load_quality_ledger()

    # P1: forbidden_patterns filter — exclude patterns whose family or stem
    # contains any forbidden token (case-insensitive substring match).
    forbidden = [str(x).lower() for x in (slide_brief.get("forbidden_patterns") or [])]

    def _is_forbidden(stem: str, entry: Dict[str, Any]) -> bool:
        if not forbidden:
            return False
        fam = (entry.get("family") or "").lower()
        s_low = stem.lower()
        for tok in forbidden:
            if tok and (tok in fam or tok in s_low):
                return True
        return False

    scored = []
    for stem, entry in catalog.items():
        if not isinstance(entry, dict):
            continue
        if _is_forbidden(stem, entry):
            continue
        n_crit, n_major = _open_findings_by_severity(ledger, stem)
        if n_crit > 0:
            continue  # hard exclude — open Critical
        s = _score_pattern(entry, slide_brief)
        s -= 5 * n_major  # penalty for open Majors
        if s > 0:
            scored.append((s, stem, entry))
    scored.sort(key=lambda t: (-t[0], t[1]))

    picked: List[Dict[str, Any]] = []
    seen_stems: Set[str] = set()
    for score, stem, entry in scored:
        if stem in seen_stems:
            continue
        if require_distinct and not _layout_distinct_within_family(picked, entry, stem):
            continue
        picked.append({
            "pattern": stem,
            "score": score,
            "entry": entry,
            "thumbnail": _thumbnail_path(stem),
        })
        seen_stems.add(stem)
        if len(picked) >= top_n:
            return picked

    # Relaxation pass 1: same family, ANY layout (allow layout repeats within
    # the family before reaching outside it). Still dedupes light/dark twins
    # of already-picked patterns. Keeps the family lock when the family is
    # too thin to give top_n distinct layouts.
    if require_distinct and len(picked) < top_n:
        for score, stem, entry in scored:
            if stem in seen_stems:
                continue
            if not _same_family(picked, entry, stem):
                continue
            picked.append({
                "pattern": stem,
                "score": score,
                "entry": entry,
                "thumbnail": _thumbnail_path(stem),
            })
            seen_stems.add(stem)
            if len(picked) >= top_n:
                return picked

    # Relaxation pass 2: open — any remaining pattern, but still dedupe
    # light/dark twins of already-picked patterns. Only reached when the
    # picked family is exhausted. Last-resort to avoid returning fewer than
    # top_n options.
    if require_distinct and len(picked) < top_n:
        for score, stem, entry in scored:
            if stem in seen_stems:
                continue
            if _is_dark_twin_of_picked(picked, stem):
                continue
            picked.append({
                "pattern": stem,
                "score": score,
                "entry": entry,
                "thumbnail": _thumbnail_path(stem),
            })
            seen_stems.add(stem)
            if len(picked) >= top_n:
                break

    return picked


def _zero_pad_stem(stem: str) -> str:
    """Normalize a pattern stem so single-digit numbers (1_, 2_, ..., 9_) are
    zero-padded to match the on-disk filenames (01_, 02_, ..., 09_).

    Catalog keys can be either form; on-disk PPTX/PNG files use zero-padded
    only for single-digit numbers. This makes the selector robust to either.
    """
    if len(stem) >= 2 and stem[0].isdigit() and stem[1] == "_":
        return "0" + stem
    return stem


def _thumbnail_path(stem: str) -> Optional[Path]:
    """Return the PNG path for a pattern's twin render, or None if missing.

    Tries both the catalog-key form and the zero-padded on-disk form.
    """
    for s in (stem, _zero_pad_stem(stem)):
        p = PNG_ROOT / s / "slide_01.png"
        if p.exists():
            return p
    return None


def pattern_to_pptx_stem(stem: str) -> str:
    """Map a catalog stem to its on-disk PPTX/PNG stem (zero-padded for 1-9)."""
    return _zero_pad_stem(stem)


def render_missing_thumbnails(catalog: Dict[str, Any], dpi: int = 100) -> List[str]:
    """Render PNG thumbnails for any approved patterns missing one. Returns the
    list of pattern stems that were rendered.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slide-qc" / "scripts"))
    from render_slides import render_libre
    twins_dir = Path(__file__).resolve().parent.parent / "_renders" / "twins"

    rendered = []
    for stem in catalog.keys():
        png = PNG_ROOT / stem / "slide_01.png"
        if png.exists():
            continue
        pptx = twins_dir / f"{stem}.pptx"
        if not pptx.exists():
            continue
        try:
            render_libre(pptx, PNG_ROOT / stem, dpi=dpi)
            rendered.append(stem)
        except Exception:
            pass
    return rendered


if __name__ == "__main__":
    # Smoke test
    catalog = load_catalog()
    print(f"Loaded {len(catalog)} patterns from catalog")

    test_brief = {
        "intent_tags": ["problem-with-3-causes", "anchored-with-evidence"],
        "deck_type": "capability-pitch",
        "slots": {"cards": 3, "title": True, "subtitle": True},
        "structural_hint": "cards",
    }
    print(f"\nTest brief: {test_brief}")
    options = propose_options(catalog, test_brief, top_n=3)
    print(f"\nTop {len(options)} options:")
    for o in options:
        print(f"  [score {o['score']}] {o['pattern']}")
        print(f"    family={o['entry'].get('family')} layout={o['entry'].get('layout')}")
        print(f"    tags={o['entry'].get('intent_tags')}")
        print(f"    thumb={o['thumbnail']}")
