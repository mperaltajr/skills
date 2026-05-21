"""
Brief-time QC checks.

Runs before the brief is handed to the selector + composer. Flags content
issues that will produce bad slides downstream: titles that wrap to 3 lines,
overflowing card bodies, forbidden placeholders, missing required fields,
run-on sentences, mid-sentence truncation.

Two severity levels:
  - blocking: must be fixed before the brief proceeds
  - warning: the user should acknowledge but can ship

Usage:
  from twins.brief_qc import check_brief
  result = check_brief(narrative)
  # or with an LLM-callback for deeper language analysis:
  result = check_brief(narrative, language_callback=my_llm_judge)
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional


# Approximate char-per-line at 32pt over 1000px-wide title box. Empirically
# titles wrap to a new line around 50-55 chars. Use 50 as the conservative
# threshold; titles > 100 chars predict 3 lines.
_TITLE_CHARS_PER_LINE = 50
_TITLE_MAX_CHARS = 80   # A1 — hard cap
_TITLE_2LINE_CHARS = 100  # A2 — predicted line-count threshold

_CARD_BODY_MAX = 200    # A3
_CARD_HEADING_MAX = 40  # A4

# Pairs of (compiled_pattern, human_label). The label is what gets shown to
# the user in the QC report — the raw regex (e.g., `\bplaceholder\b`) leaks
# unhelpful syntax.
_FORBIDDEN_PLACEHOLDER_PATTERNS = [
    (re.compile(r"\bTBD\b", re.IGNORECASE), "TBD"),
    (re.compile(r"\bLorem\b", re.IGNORECASE), "Lorem ipsum"),
    (re.compile(r"\[Client Name\]", re.IGNORECASE), "[Client Name]"),
    (re.compile(r"\bxxxx+\b", re.IGNORECASE), "xxxx"),
    (re.compile(r"\bClick to edit\b", re.IGNORECASE), "Click to edit"),
    (re.compile(r"\bplaceholder\b", re.IGNORECASE), "placeholder"),
    (re.compile(r"\[insert.*?\]", re.IGNORECASE), "[insert ...]"),
]

_MAX_EDITORIAL_EMPHASIS = 3  # A9 — narrative should pick at most 3

_REQUIRED_COVER_FIELDS = ("title", "tagline", "presenter")
_REQUIRED_CTA_FIELDS = ("primary_ask",)
_REQUIRED_CTA_SUB_ASKS = 3

# A6 — run-on detection. A "sentence" (segment between . ! ?) longer than
# this is flagged as a run-on candidate. Tune conservatively — we'd rather
# under-flag than annoy with false positives.
_RUNON_MAX_WORDS = 35
_RUNON_MAX_CHARS = 260

# A8 — truncation patterns: trailing ellipsis, dangling comma/em-dash,
# missing terminal punctuation after a long-enough body.
_ELLIPSIS_RE = re.compile(r"\.{3}\s*$")  # trailing "..." at any length
_DANGLING_TRUNCATION_RE = re.compile(r"(,|—|–|-)\s*$")  # dangling , — - only at length
_MISSING_TERMINAL_PUNCT_RE = re.compile(r"[A-Za-z0-9]\s*$")  # body ends w/o . ! ?

# A6 — sentence terminator split (handles e.g., Mr. Smith via simple lookahead).
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[\.\!\?])\s+(?=[A-Z])")


def _predict_lines(title: str) -> int:
    """Predict how many rendered lines a title will take at 32pt over a
    1000px-wide box. Naive character-per-line heuristic, conservative.
    """
    n = len(title or "")
    if n == 0:
        return 0
    # Use ceil division
    return (n + _TITLE_CHARS_PER_LINE - 1) // _TITLE_CHARS_PER_LINE


def _scan_text(text: Any) -> List[str]:
    """Return the forbidden-placeholder human labels matched by `text`."""
    if not isinstance(text, str):
        return []
    found = []
    for pat, label in _FORBIDDEN_PLACEHOLDER_PATTERNS:
        if pat.search(text):
            found.append(label)
    return found


def _slide_is_cover(slide: Dict[str, Any]) -> bool:
    gov = (slide.get("governing_thought") or "").lower()
    em = (slide.get("editorial_emphasis") or "")
    em_text = " ".join(em) if isinstance(em, list) else str(em)
    return (slide.get("slide_num") == 1
            or "[cover" in gov
            or "cover slide" in em_text.lower())


def _slide_is_closing_cta(slide: Dict[str, Any]) -> bool:
    gov = (slide.get("governing_thought") or "").lower()
    em = (slide.get("editorial_emphasis") or "")
    em_text = " ".join(em) if isinstance(em, list) else str(em)
    em_l = em_text.lower()
    return (
        "the ask" in em_l or "next steps" in em_l or "cta" in em_l
        or "primary ask" in gov or "closing" in em_l
    )


def _scan_all_text(slide: Dict[str, Any]) -> List[str]:
    """Walk every text field on a slide and return forbidden hits."""
    hits: List[str] = []
    for k in ("governing_thought", "so_what", "editorial_emphasis"):
        for p in _scan_text(slide.get(k)):
            hits.append(f"'{p}' in {k}")
    content = slide.get("content") or {}
    for k, v in content.items():
        if isinstance(v, str):
            for p in _scan_text(v):
                hits.append(f"'{p}' in content.{k}")
        elif isinstance(v, list):
            for i, item in enumerate(v, 1):
                if isinstance(item, dict):
                    for ck, cv in item.items():
                        for p in _scan_text(cv):
                            hits.append(f"'{p}' in content.{k}[{i}].{ck}")
                elif isinstance(item, str):
                    for p in _scan_text(item):
                        hits.append(f"'{p}' in content.{k}[{i}]")
        elif isinstance(v, dict):
            for ck, cv in v.items():
                for p in _scan_text(cv):
                    hits.append(f"'{p}' in content.{k}.{ck}")
    return hits


def _iter_prose(slide: Dict[str, Any]):
    """Yield (location_label, text) for every long-form text field on a slide.

    Yields headings + bodies + so_what + governing_thought. Skips structured
    fields like editorial_emphasis lists (those don't need language QC).
    """
    n = slide.get("slide_num", "?")
    for k in ("governing_thought", "so_what"):
        v = slide.get(k)
        if isinstance(v, str) and v.strip():
            yield (f"slide {n}.{k}", v)
    content = slide.get("content") or {}
    if isinstance(content, dict):
        for ck, cv in content.items():
            if isinstance(cv, str) and len(cv) > 20:
                yield (f"slide {n}.content.{ck}", cv)
            elif isinstance(cv, list):
                for i, item in enumerate(cv, 1):
                    if isinstance(item, dict):
                        for fk in ("heading", "name", "title", "body", "description", "desc", "label"):
                            fv = item.get(fk)
                            if isinstance(fv, str) and len(fv) > 20:
                                yield (f"slide {n}.content.{ck}[{i}].{fk}", fv)
                    elif isinstance(item, str) and len(item) > 20:
                        yield (f"slide {n}.content.{ck}[{i}]", item)
            elif isinstance(cv, dict):
                for fk, fv in cv.items():
                    if isinstance(fv, str) and len(fv) > 20:
                        yield (f"slide {n}.content.{ck}.{fk}", fv)


def _check_language_heuristics(slide: Dict[str, Any]) -> Dict[str, List[str]]:
    """A6/A8 heuristic language pass — no LLM required.

    A6: detect run-on sentences (a "sentence" with > _RUNON_MAX_WORDS words
        or > _RUNON_MAX_CHARS chars).
    A8: detect mid-sentence truncation (trailing ..., dangling em-dash,
        comma at end, or body ending without terminal punctuation).
    """
    blocking: List[str] = []
    warnings: List[str] = []

    for loc, text in _iter_prose(slide):
        t = text.strip()
        if not t:
            continue

        # A6 — run-on
        sentences = _SENTENCE_SPLIT_RE.split(t)
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            n_words = len(s.split())
            n_chars = len(s)
            if n_words > _RUNON_MAX_WORDS or n_chars > _RUNON_MAX_CHARS:
                warnings.append(
                    f"{loc}: run-on sentence ({n_words} words, {n_chars} chars): "
                    f"{s[:60]!r}... (A6)"
                )

        # A8 — truncation
        loc_lower = loc.lower()
        # Skip cover/title fields where ellipsis can be intentional brand copy.
        is_title_field = ".title" in loc_lower or ".tagline" in loc_lower
        # Trailing ellipsis — strong truncation signal at ANY length unless title.
        if _ELLIPSIS_RE.search(t) and not is_title_field:
            warnings.append(f"{loc}: trailing ellipsis (...) — mid-thought? {t[-40:]!r} (A8)")
        # Dangling comma / em-dash — flag only on body-length text.
        if len(t) > 40 and _DANGLING_TRUNCATION_RE.search(t) and not is_title_field:
            warnings.append(f"{loc}: dangling truncation marker (,—-): {t[-40:]!r} (A8)")
        # Missing terminal punctuation on body-length text.
        if len(t) > 80 and _MISSING_TERMINAL_PUNCT_RE.search(t):
            warnings.append(f"{loc}: no terminal punctuation (.!?): {t[-40:]!r} (A8)")

    return {"blocking": blocking, "warnings": warnings}


def _check_slide(slide: Dict[str, Any]) -> Dict[str, List[str]]:
    """Run all per-slide checks. Returns {blocking: [...], warnings: [...]}."""
    blocking: List[str] = []
    warnings: List[str] = []
    n = slide.get("slide_num", "?")
    label = f"slide {n}"

    # A1 + A2 — title length. Dedup: report only the most severe finding per
    # title. Blocking (predicted 3+ lines, >100 chars) supersedes warnings.
    title = (slide.get("governing_thought")
             or (slide.get("content") or {}).get("title")
             or "")
    if title:
        n_chars = len(title)
        n_lines = _predict_lines(title)
        if n_chars > _TITLE_2LINE_CHARS:
            blocking.append(
                f"{label}: title is {n_chars} chars — will wrap to 3+ lines (A1/A2)"
            )
        elif n_lines > 2:
            warnings.append(
                f"{label}: title predicted to wrap to {n_lines} lines (A2)"
            )
        elif n_chars > _TITLE_MAX_CHARS:
            warnings.append(
                f"{label}: title is {n_chars} chars (over the {_TITLE_MAX_CHARS}-char guideline, A1)"
            )

    # A3 / A4 — card body / heading lengths
    content = slide.get("content") or {}
    for list_key in ("cards", "columns", "pillars", "steps", "supporting_cards"):
        for i, c in enumerate(content.get(list_key) or [], 1):
            if not isinstance(c, dict):
                continue
            heading = c.get("heading") or c.get("name") or c.get("title") or ""
            body = c.get("body") or c.get("description") or c.get("desc") or ""
            if len(heading) > _CARD_HEADING_MAX:
                warnings.append(f"{label}: {list_key}[{i}].heading is {len(heading)} chars (>40, A4)")
            if len(body) > _CARD_BODY_MAX:
                warnings.append(f"{label}: {list_key}[{i}].body is {len(body)} chars (>200, A3)")

    # A5 — forbidden placeholders
    for hit in _scan_all_text(slide):
        blocking.append(f"{label}: forbidden placeholder {hit}")

    # A7 — required fields per slide type. Cover fields support aliases:
    # presenter/presented_by, client/audience, etc. Recognize all of them
    # before flagging a missing-required-field.
    _COVER_ALIASES = {
        "title": ("title",),
        "tagline": ("tagline",),
        "presenter": ("presenter", "presented_by", "presented_name"),
    }
    if _slide_is_cover(slide):
        cover = content.get("cover") or {}
        for f in _REQUIRED_COVER_FIELDS:
            aliases = _COVER_ALIASES.get(f, (f,))
            has_value = any(cover.get(a) or content.get(a) for a in aliases)
            if not has_value:
                blocking.append(f"{label}: cover missing required field '{f}' (A7)")
    if _slide_is_closing_cta(slide):
        for f in _REQUIRED_CTA_FIELDS:
            if not content.get(f):
                blocking.append(f"{label}: closing CTA missing required field '{f}' (A7)")
        sub_asks = content.get("sub_asks") or []
        if isinstance(sub_asks, list) and len(sub_asks) < _REQUIRED_CTA_SUB_ASKS:
            blocking.append(
                f"{label}: closing CTA has {len(sub_asks)} sub_asks; needs {_REQUIRED_CTA_SUB_ASKS} (A7)"
            )

    # A9 — editorial_emphasis count (1-3)
    em = slide.get("editorial_emphasis")
    if isinstance(em, list) and len(em) > _MAX_EDITORIAL_EMPHASIS:
        warnings.append(f"{label}: editorial_emphasis has {len(em)} items; trim to <=3 (A9)")

    # A6 + A8 — heuristic language pass
    lang = _check_language_heuristics(slide)
    blocking.extend(lang["blocking"])
    warnings.extend(lang["warnings"])

    return {"blocking": blocking, "warnings": warnings}


LanguageCallback = Callable[[str, str], List[Dict[str, str]]]
"""Type for an optional deep language analyzer the orchestrator can supply.

Signature: callback(location_label, text) -> [{"severity": "warning"/"blocking", "msg": "..."}].

The orchestrator (Claude in the chat session) is the natural place to run
this since it has model access. Slide-builder's pure-Python checks can't
do nuanced grammar / tone / coherence analysis on their own.
"""


def check_brief(narrative: List[Dict[str, Any]], *, strict: bool = False,
                 language_callback: Optional[LanguageCallback] = None) -> Dict[str, Any]:
    """Run brief-time QC checks across every slide. Returns:

        {
            "blocking": [list of issues that must be fixed],
            "warnings": [list of issues the user should acknowledge],
            "summary": "human-readable summary string"
        }

    When `strict=True`, warnings are promoted to blocking.

    A6/A8 (run-on sentences, mid-sentence truncation) are covered by the
    heuristic pass in _check_language_heuristics. For deeper grammar / tone
    / coherence checks, supply `language_callback` — the orchestrator calls
    an LLM on each prose field and returns severity-tagged issues. Slide-
    builder calls this callback per prose field and merges the results.
    """
    if not isinstance(narrative, list):
        raise ValueError(f"narrative must be a list of slide dicts; got {type(narrative).__name__}")

    blocking: List[str] = []
    warnings: List[str] = []
    for slide in narrative:
        if not isinstance(slide, dict):
            continue
        r = _check_slide(slide)
        blocking.extend(r["blocking"])
        warnings.extend(r["warnings"])

        # Optional deep language pass via orchestrator-supplied callback
        if language_callback is not None:
            for loc, text in _iter_prose(slide):
                try:
                    issues = language_callback(loc, text) or []
                except Exception as e:
                    warnings.append(f"{loc}: language_callback error: {e}")
                    continue
                for it in issues:
                    sev = (it.get("severity") or "warning").lower()
                    msg = it.get("msg") or "language issue"
                    line = f"{loc}: {msg}"
                    if sev == "blocking":
                        blocking.append(line)
                    else:
                        warnings.append(line)

    if strict:
        blocking.extend(warnings)
        warnings = []

    n = len(narrative)
    summary = (
        f"Checked {n} slide(s): {len(blocking)} blocking, {len(warnings)} warning(s)."
        if blocking or warnings
        else f"Checked {n} slide(s): clean."
    )
    return {"blocking": blocking, "warnings": warnings, "summary": summary}


if __name__ == "__main__":
    # Smoke test
    test_narrative = [
        {
            "slide_num": 1,
            "governing_thought": "[Cover slide]",
            "content": {"cover": {"title": "Slide Lab", "tagline": "Think. Argue. Build.", "presenter": "Mario"}},
        },
        {
            "slide_num": 2,
            "governing_thought": "Consultants rarely lack ideas " * 20,  # 320+ chars — will block
            "editorial_emphasis": ["the_conclusion", "the_evidence", "the_contrast", "the_data"],  # warning
            "content": {
                "cards": [
                    {"heading": "A" * 50, "body": "B" * 250},  # warning
                ],
            },
        },
        {
            "slide_num": 3,
            "governing_thought": "TBD",  # blocking
            "content": {"cards": [{"heading": "ok", "body": "ok"}]},
        },
    ]
    import json
    print(json.dumps(check_brief(test_narrative), indent=2))
