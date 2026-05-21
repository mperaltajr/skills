"""
Build-with-options workflow.

Walks a narrative brief slide by slide. For each slide:
  1. Derives a slide brief (intent tags + slot needs + structural hint) from
     the storyline-helper output.
  2. Calls selector.propose_options() to get 3 structurally distinct candidate
     patterns.
  3. Presents the 3 candidate twin thumbnails (PNGs) to the user — Claude
     surfaces them via Read on the PNG files.
  4. The caller (Claude in the orchestrator) picks one based on the user's
     choice and writes the picked pattern into the deck YAML.
  5. After all slides are picked, compose_from_spec() builds the PPTX.

The mechanical primitive lives here. The presentation step (showing the user
the three thumbnails and capturing a pick) is intentionally not a tight loop
inside Python — it's run interactively by the orchestrator. This module
provides:

  - `derive_slide_brief(narrative_slide)` — extract intent + slots from a
    storyline-helper slide entry
  - `prepare_deck_specs(narrative)` — for each slide, call propose_options
    and return the 3 candidates per slide (so the orchestrator can show them
    and capture picks)
  - `compose_picked_deck(narrative, picks, output_path, client_template=None)`
    — once picks are captured, write the deck YAML + run compose

Example narrative slide entry (storyline-helper output):

  {
    "slide_num": 2,
    "governing_thought": "Consultants rarely lack ideas — they struggle to cut through them.",
    "so_what": "Not a knowledge gap. Not a skill deficit. A structural problem.",
    "editorial_emphasis": "Three compounding forces as supporting evidence",
    "content": {"cards": [{"heading": "...", "body": "..."}, ...]},
    "chart_type": "none",
  }
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from twins.selector import load_catalog, propose_options


def derive_slide_brief(narrative_slide: Dict[str, Any]) -> Dict[str, Any]:
    """Translate a storyline-helper slide entry into a selector brief.

    Emits intent_tags and editorial_emphasis from the catalog's Phase-4 vocab
    (NOT legacy tags). Also extracts so_what + intent text for the selector's
    good_for/bad_for keyword matcher.
    """
    brief: Dict[str, Any] = {
        "intent_tags": [],
        "editorial_emphasis": [],
        "slots": {"title": True},
    }

    content = narrative_slide.get("content") or {}
    # editorial_emphasis can be a string (narrative-brief form) or a list of
    # tag strings (after narrative_with_feedback adjustments). Tolerate both.
    _em_raw = narrative_slide.get("editorial_emphasis") or ""
    if isinstance(_em_raw, list):
        editorial = " ".join(str(x) for x in _em_raw).lower()
    else:
        editorial = str(_em_raw).lower()
    gov = (narrative_slide.get("governing_thought") or "").lower()
    sw = (narrative_slide.get("so_what") or "").lower()
    chart_type = (narrative_slide.get("chart_type") or "").lower()
    slide_num = narrative_slide.get("slide_num")

    # Pass-through text for selector good_for/bad_for matching
    brief["so_what"] = narrative_slide.get("so_what") or ""
    brief["intent"] = narrative_slide.get("governing_thought") or ""

    # P1 enrichment — optional per-slide steering fields (see storyline-helper).
    # Pass through verbatim; selector decides how to use them.
    for key in ("visual_rhythm", "mandatory_shape", "accent_placement"):
        val = narrative_slide.get(key)
        if val:
            brief[key] = val
    forbidden = narrative_slide.get("forbidden_patterns")
    if isinstance(forbidden, list) and forbidden:
        brief["forbidden_patterns"] = [str(x).lower() for x in forbidden]

    # Count structural elements early — drives nuance below
    _cards_count = len(content.get("cards") or content.get("supporting_cards") or [])
    _cols_count = len(content.get("pillars") or content.get("columns") or [])
    _n = max(_cards_count, _cols_count)

    # ---- editorial_emphasis extraction from the narrative's prose ----
    # Phase 4 vocab: the_conclusion / the_evidence / the_contrast /
    #                the_data / the_ask / the_numbers
    em_tags = []
    if any(w in editorial for w in ("conclusion", "answer", "recommendation", "anchor", "thesis")):
        em_tags.append("the_conclusion")
    if any(w in editorial for w in ("evidence", "proof", "support", "supporting")):
        em_tags.append("the_evidence")
    # `the_contrast` ONLY for binary comparisons (2 cards/columns) or
    # explicit "before/after" / "vs." language. 3+ pillars is conclusion-led,
    # not contrast-led, even when the narrative uses the word "contrast" loosely.
    binary_contrast_lang = any(w in editorial for w in (
        "before/after", "before-after", "vs.", "versus", "two failure modes", "side by side",
    ))
    if binary_contrast_lang or (("contrast" in editorial or "compare" in editorial) and _n == 2):
        em_tags.append("the_contrast")
    elif ("contrast" in editorial or "compare" in editorial) and _n >= 3:
        # Multi-bucket "contrast" really means "the_conclusion" (here are N things)
        if "the_conclusion" not in em_tags:
            em_tags.append("the_conclusion")
    if any(w in editorial for w in ("data", "chart", "trend", "distribution")):
        em_tags.append("the_data")
    if any(w in editorial for w in ("ask", "cta", "next steps", "approval", "decision required")):
        em_tags.append("the_ask")
    if any(w in editorial for w in ("numbers", "metric", "kpi", "scorecard", "hero stat", "headline number")):
        em_tags.append("the_numbers")
    brief["editorial_emphasis"] = em_tags

    # ---- structural detection ----
    is_cover = (slide_num == 1) or "[cover" in gov or "cover slide" in editorial
    is_closing_ask = ("the ask" in editorial or "next steps" in editorial
                      or "primary ask" in gov or "cta" in editorial)
    is_screenshot = ("screenshot" in editorial or "demo" in editorial
                     or "screenshot" in gov or "[demo" in gov)
    is_hero = "hero" in editorial or "manifesto" in editorial or "single bold" in editorial
    is_contrast = ("contrast" in editorial or "before" in editorial or "vs." in gov
                   or "vs " in gov or "side by side" in editorial)
    is_honest = "honest" in editorial or "still growing" in gov or "works well" in gov

    # ---- intent_tags from Phase-4 vocab ----
    if is_cover:
        brief["intent_tags"].extend([
            "cover-standard", "cover-photo", "cover-minimal",
            "cover-with-logo", "cover-split", "deck-opener",
        ])
        brief["structural_hint"] = "cover"

    if is_screenshot:
        # Screenshots use photo/statement patterns
        brief["intent_tags"].extend(["statement", "insight"])
        brief["structural_hint"] = "photo"

    if is_closing_ask:
        brief["intent_tags"].extend(["closing-cta", "ask", "next-steps"])
        brief["structural_hint"] = "hero"

    # Card grids → anchor-with-cards + bucket-N
    cards = content.get("cards") or content.get("supporting_cards") or []
    if isinstance(cards, list) and len(cards) > 0:
        n = len(cards)
        brief["slots"]["cards"] = n
        brief["intent_tags"].append("anchor-with-cards")
        if n in (2, 3, 4, 5):
            brief["intent_tags"].append(f"bucket-{n}")
        brief["intent_tags"].append("bucket-list")
        if not brief.get("structural_hint"):
            brief["structural_hint"] = "cards"

    # Pillars / columns (3-col Think/Argue/Build pattern)
    if "pillars" in content or "columns" in content:
        cols = content.get("pillars") or content.get("columns") or []
        n = len(cols) if isinstance(cols, list) else 0
        if n:
            brief["slots"]["pillars"] = n
            if n in (2, 3, 4, 5):
                brief["intent_tags"].append(f"bucket-{n}")
            brief["intent_tags"].extend(["comparison-cards", "anchor-with-cards"])
            if n == 3 and "think" in str(cols).lower():
                # Think/Argue/Build special case
                brief["intent_tags"].extend(["methodology-overview", "framework-house"])

    # KPI / metrics
    metrics = content.get("metrics") or content.get("kpis") or []
    if isinstance(metrics, list) and metrics:
        brief["slots"]["metrics"] = len(metrics)
        brief["intent_tags"].extend(["kpi-dashboard", "scorecard", "status-table"])
        brief["structural_hint"] = "scorecard"

    # Hero / statement
    if is_hero:
        brief["intent_tags"].extend(["hero-statement", "statement", "insight"])
        brief["structural_hint"] = "hero"

    # Comparison / contrast — ONLY for binary (2-way) comparisons. For 3+
    # pillars, don't broadcast comparison tags (they steer the selector toward
    # before-after patterns instead of N-bucket patterns).
    if is_contrast and _n <= 2:
        brief["intent_tags"].extend([
            "comparison-cards", "comparison-matrix",
            "before-after", "pros-cons", "tradeoff",
        ])
        brief["structural_hint"] = "comparison"

    # Honest expectations — specific pattern family (7d, 7)
    if is_honest:
        brief["intent_tags"].extend(["pros-cons", "comparison-cards", "tradeoff"])

    # Chart slides
    if chart_type and chart_type != "none":
        brief["intent_tags"].append("chart-with-takeaway")
        chart_tag_map = {
            "waterfall": "waterfall",
            "bar": "bar-chart",
            "line": "line-chart",
            "donut": "donut-chart",
            "funnel": "funnel-chart",
            "tornado": "tornado-chart",
            "radar": "radar-chart",
            "slope": "slope-chart",
            "pareto": "pareto",
            "lollipop": "lollipop",
            "diverging": "diverging-bar",
        }
        for keyword, tag in chart_tag_map.items():
            if keyword in chart_type:
                brief["intent_tags"].append(tag)
        brief["structural_hint"] = "chart"

    # SCQA / structured narrative
    if "scqa" in editorial or "situation" in gov or "complication" in gov:
        brief["intent_tags"].extend(["scqa", "exec-summary"])

    # Convergence band — most patterns support takeaway
    if "convergence" in editorial or "takeaway" in editorial or sw:
        brief["slots"]["convergence"] = True

    return brief


def prepare_deck_specs(narrative: List[Dict[str, Any]], top_n: int = 3,
                        deck_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """For each slide in the narrative, derive its brief and propose top_n
    candidate patterns. Returns a list of:

      {
        "slide_num": N,
        "governing_thought": "...",
        "brief": <derived brief>,
        "options": [{"pattern": ..., "score": ..., "entry": ..., "thumbnail": ...}, ...],
      }

    The caller (Claude in the orchestrator) iterates this list and presents
    the options to the user, capturing one pick per slide.
    """
    catalog = load_catalog()
    out = []
    for s in narrative:
        brief = derive_slide_brief(s)
        if deck_type:
            brief["deck_type"] = deck_type
        options = propose_options(catalog, brief, top_n=top_n)
        out.append({
            "slide_num": s.get("slide_num"),
            "governing_thought": s.get("governing_thought"),
            "brief": brief,
            "options": options,
        })
    return out


def compose_picked_deck(picks: List[Dict[str, Any]], out_path: str,
                       client_template: Optional[str] = None,
                       verbose: bool = True) -> Path:
    """Once the user has picked a pattern per slide, compose the deck.

    `picks` is a list of:
      {"pattern": <stem>, "overrides": {<shape_id>: <text>, ...}}

    Returns the output path.
    """
    from twins.composer import compose_deck
    return compose_deck(
        out_path=str(out_path),
        slides=[{"pattern": p["pattern"], "overrides": p.get("overrides", {})} for p in picks],
        client_template=client_template,
        verbose=verbose,
    )


def compose_from_review_yaml(review_picks: Dict[str, Any], out_path: str,
                              client_template: Optional[str] = None,
                              verbose: bool = True) -> Path:
    """Compose a deck from the review-page YAML schema that the user pastes back.

    Accepts a dict shaped like:

        slides:
          - slide_num: 3
            decision: picked       # or "none" or "tweak"
            pattern: 01_anchor-with-cards-icons
            feedback:              # optional, keys map to shape IDs in the pattern
              headline: "..."
              card_1: "..."
              layout: "..."
          - slide_num: 4
            decision: none
            feedback: "needs a chart instead of cards"

    Behavior:
      - Slides with decision != "picked" are SKIPPED (no slide in output).
      - `feedback` is hydrated into the composer's `overrides` map; the keys
        must match shape IDs the pattern emits (the catalog `slots` schema
        documents the well-known IDs).
      - String-valued `feedback` (NONE-with-comment) is preserved as a note
        but does not contribute overrides — Claude should re-run selector with
        the comment as new brief input.

    Returns the output path.

    Example caller:
        import yaml
        review = yaml.safe_load(Path("deck-review-picks.yaml").read_text())
        compose_from_review_yaml(review, "deck-final.pptx", client_template="...")
    """
    if not isinstance(review_picks, dict) or "slides" not in review_picks:
        raise ValueError(
            "Review YAML must be a mapping with a top-level 'slides' list. "
            "Got: %s" % (type(review_picks).__name__,)
        )

    picks: List[Dict[str, Any]] = []
    skipped: List[int] = []
    for s in review_picks["slides"]:
        if not isinstance(s, dict):
            raise ValueError(f"slide entry must be a mapping; got {type(s).__name__}")
        slide_num = s.get("slide_num", "?")
        decision = (s.get("decision") or "").lower().strip()
        if decision != "picked":
            skipped.append(slide_num)
            continue
        pattern = s.get("pattern")
        if not pattern:
            raise ValueError(
                f"slide {slide_num} decision='picked' but has no 'pattern' field"
            )
        # Hydrate feedback into overrides. Dict-shaped feedback becomes a map of
        # shape_id -> text. String-shaped feedback (a free-text comment) is
        # ignored here — it's intended for re-selection, not composition.
        feedback = s.get("feedback")
        overrides: Dict[str, Any] = {}
        if isinstance(feedback, dict):
            overrides = {k: v for k, v in feedback.items() if v is not None}
        picks.append({"pattern": pattern, "overrides": overrides})

    if not picks:
        raise ValueError(
            "No slides marked decision='picked' in review YAML — nothing to compose."
        )

    if verbose:
        if skipped:
            print(f"Skipping {len(skipped)} slide(s) not marked 'picked': {skipped}")
        print(f"Composing {len(picks)} picked slide(s) -> {out_path}")

    return compose_picked_deck(
        picks=picks,
        out_path=out_path,
        client_template=client_template,
        verbose=verbose,
    )


# ---------------------------------------------------------------------------
# P2 — Per-slide refine loop
# ---------------------------------------------------------------------------

# Feedback-phrase → brief-adjustment rules. Each rule names words/phrases that
# might appear in user feedback and the (editorial_emphasis, intent_tags,
# visual_rhythm, mandatory_shape) adjustments to make to the narrative slide.
# Extend this list as new patterns emerge — the rules are intentionally
# additive and conservative.
_REFINE_RULES = [
    # phrase tokens, add_emphasis, add_intent_tags, set_rhythm, set_shape
    (("spectrum", "comparison", " vs ", " vs.", "versus", "side by side", "side-by-side", "before/after", "before-after"),
        ["the_contrast"], ["comparison-cards"], "contrast-dominant", None),
    (("value", "roi", "benefit", "value-prop", "value proposition"),
        [], ["value-proposition"], None, None),
    (("process", "steps", "phases", "phased", "stages", "stage gate"),
        [], ["process", "timeline"], "process-dominant", None),
    (("data", "metric", "metrics", "kpi", "kpis", "scorecard", "numbers", "the number"),
        ["the_numbers", "the_data"], ["kpi-dashboard", "scorecard"], "data-dominant", None),
    (("persona", "audience", "stakeholder", "stakeholders", "segments", "segmentation"),
        [], ["persona", "audience-segmentation"], None, None),
    (("dramatic", "punchier", "punchy", "bolder", "hero", "big statement", "one statement"),
        ["the_conclusion"], ["hero-statement", "statement"], None, None),
    (("framework", "pillars", "pillar", "three pillars"),
        [], ["framework-house", "methodology-overview"], "framework-dominant", None),
    (("table", "matrix"),
        [], ["comparison-matrix"], None, None),
    (("three column", "3 column", "3-column", "three-column"),
        [], [], None, "three-column"),
    (("two column", "2 column", "2-column", "two-column"),
        [], [], None, "two-column"),
    (("four column", "4 column", "4-column", "four-column"),
        [], [], None, "four-column"),
    (("2x2", "quadrant", "four quadrant"),
        [], [], None, "2x2-grid"),
    (("ask", "next steps", "cta", "call to action", "decision required"),
        ["the_ask"], ["closing-cta", "ask"], "ask-dominant", None),
]


def _feedback_to_text(feedback: Any) -> str:
    """Flatten a feedback dict / string into a single lowercase searchable string."""
    if not feedback:
        return ""
    if isinstance(feedback, str):
        return feedback.lower()
    if isinstance(feedback, dict):
        parts: List[str] = []
        for v in feedback.values():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, dict):
                parts.extend(str(x) for x in v.values() if x)
            elif isinstance(v, list):
                parts.extend(str(x) for x in v if x)
        return " ".join(parts).lower()
    return str(feedback).lower()


def narrative_with_feedback(narrative_slide: Dict[str, Any],
                             feedback: Any) -> Dict[str, Any]:
    """Return a MODIFIED copy of `narrative_slide` with editorial_emphasis,
    intent_tags, visual_rhythm, and mandatory_shape adjusted based on the
    user's feedback. Pure function — no I/O, no mutation of input.

    Feedback can be a string or a dict of per-section strings (the shape
    produced by review_html's feedback textareas). The function searches the
    combined text for known phrase tokens and applies the matching rule's
    adjustments.

    Conservative on removal: rules ADD signal. To DROP intent_tags or
    emphasis the user wants gone, the caller should reset the field before
    calling this function, or pass an explicit override via feedback.
    """
    out = dict(narrative_slide)  # shallow copy is enough; we don't mutate nested dicts
    text = _feedback_to_text(feedback)
    if not text.strip():
        return out

    # Pad with spaces so " vs " token matches at boundaries
    haystack = f" {text} "

    add_em: List[str] = []
    add_tags: List[str] = []
    set_rhythm: Optional[str] = None
    set_shape: Optional[str] = None

    for tokens, emph, tags, rhythm, shape in _REFINE_RULES:
        if any(t in haystack for t in tokens):
            add_em.extend(emph)
            add_tags.extend(tags)
            if rhythm and not set_rhythm:
                set_rhythm = rhythm
            if shape and not set_shape:
                set_shape = shape

    # "Simpler" / "less" → strip non-core intent_tags (heuristic: keep only the
    # last 2 most-recently-added — caller can override with explicit feedback).
    if any(t in haystack for t in ("too busy", "simpler", "less is more", "fewer", "trim")):
        existing = list(out.get("intent_tags") or [])
        out["intent_tags"] = existing[:2]

    # Apply additions (de-duped, preserve order)
    if add_em:
        existing_em = list(out.get("editorial_emphasis") or [])
        if isinstance(existing_em, str):
            existing_em = [existing_em]
        for e in add_em:
            if e not in existing_em:
                existing_em.append(e)
        out["editorial_emphasis"] = existing_em
    if add_tags:
        existing_tags = list(out.get("intent_tags") or [])
        for t in add_tags:
            if t not in existing_tags:
                existing_tags.append(t)
        out["intent_tags"] = existing_tags
    if set_rhythm and not out.get("visual_rhythm"):
        out["visual_rhythm"] = set_rhythm
    if set_shape and not out.get("mandatory_shape"):
        out["mandatory_shape"] = set_shape

    return out


def refine_slide(narrative_slide: Dict[str, Any],
                 feedback: Any,
                 catalog: Optional[Dict[str, Any]] = None,
                 top_n: int = 3,
                 deck_type: Optional[str] = None) -> Dict[str, Any]:
    """End-to-end refine: take a narrative slide + feedback, return fresh
    option proposals reflecting the modified brief.

    Returns:
      {
        "slide_num": N,
        "brief": <derived brief from modified narrative slide>,
        "options": [{"pattern": ..., "score": ..., "entry": ...}, ...],
        "modified_narrative": <the narrative slide after feedback adjustments>,
      }
    """
    if catalog is None:
        catalog = load_catalog()
    modified = narrative_with_feedback(narrative_slide, feedback)
    brief = derive_slide_brief(modified)
    if deck_type:
        brief["deck_type"] = deck_type
    options = propose_options(catalog, brief, top_n=top_n)
    return {
        "slide_num": modified.get("slide_num"),
        "brief": brief,
        "options": options,
        "modified_narrative": modified,
    }


if __name__ == "__main__":
    # Smoke test — derive briefs for the intro-to-Slide-Lab narrative
    import json
    test_narrative = [
        {"slide_num": 1, "governing_thought": "[Cover slide — no governing thought required]",
         "editorial_emphasis": "Title, tagline, and presenter name only."},
        {"slide_num": 2, "governing_thought": "Consultants rarely lack ideas — they struggle to cut through them.",
         "editorial_emphasis": "Three compounding forces as supporting evidence",
         "content": {"cards": [{"heading": "Too much to say"}, {"heading": "Too many cooks"}, {"heading": "Audience needs next"}]}},
        {"slide_num": 5, "governing_thought": "Three skill domains — connected, not stacked.",
         "editorial_emphasis": "Three columns mapping to Think / Argue / Build",
         "content": {"pillars": [{"name": "Think"}, {"name": "Argue"}, {"name": "Build"}]}},
        {"slide_num": 10, "governing_thought": "One real deck is all it takes — try it.",
         "editorial_emphasis": "The ask dominates — one clear CTA"},
    ]
    specs = prepare_deck_specs(test_narrative, top_n=3, deck_type="capability-pitch")
    for s in specs:
        print(f"\nSlide {s['slide_num']}: {s['governing_thought'][:60]}")
        print(f"  brief tags: {s['brief'].get('intent_tags')}")
        print(f"  3 options:")
        for o in s["options"]:
            print(f"    [{o['score']:>2}] {o['pattern']}")
            print(f"          {o['entry'].get('family')} / {o['entry'].get('layout')}")
