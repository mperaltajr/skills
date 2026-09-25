"""Build state manifest for the Slide Lab pipeline (`_state.json`).

Records which stage legitimately completed, the deck content-hash the stage ran
against, the one canonical out-dir, and the review-approval token. Pipeline
scripts read this to refuse out-of-order or stale execution, and compile_picks.py
uses it to verify a real human review happened (the token is minted only by
build_review.py and shown only inside REVIEW.html) instead of trusting a
self-asserted flag.

Deliberately mechanical: a script refuses based on a recorded fact, not on
doc-only "MUST" prose (doc-only rules are exactly what got routed around).
"""
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime
from pathlib import Path

STATE_NAME = "_state.json"
SCHEMA = 1


def state_path(out_dir) -> Path:
    return Path(out_dir) / STATE_NAME


def read_state(out_dir) -> dict:
    p = state_path(out_dir)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _write(out_dir, state: dict) -> None:
    state["schema"] = SCHEMA
    state_path(out_dir).write_text(json.dumps(state, indent=2), encoding="utf-8")


def deck_content_hash(brief_text: str, template: str, pattern: str) -> str:
    """Stable hash of the inputs that define the deck. If any changes, a prior
    review/approval is stale."""
    h = hashlib.md5()
    for part in (brief_text or "", template or "", pattern or ""):
        h.update(part.encode("utf-8", "replace"))
        h.update(b"\x00")
    return h.hexdigest()


def record_prep(out_dir, content_hash: str, canonical_out: str) -> None:
    """Prep ran: set the content-hash + canonical out, stamp the prep stage, and
    INVALIDATE any prior review approval (a (re)build must be re-reviewed)."""
    state = read_state(out_dir)
    state["content_hash"] = content_hash
    state["canonical_out"] = str(Path(canonical_out).resolve())
    state.setdefault("stages", {})["prep"] = {"at": _now()}
    state.pop("review", None)  # any (re)prep invalidates prior approval
    _write(out_dir, state)


def record_review(out_dir) -> str:
    """Review page built: mint + record an approval token bound to the deck
    content-hash recorded at prep, and return it. build_review.py shows it ONLY
    inside REVIEW.html. On a legacy build with no prep record, content_hash is
    None on both sides, so the token match alone gates compile."""
    state = read_state(out_dir)
    token = secrets.token_hex(8)
    state.setdefault("stages", {})["review"] = {"at": _now()}
    state["review"] = {"token": token, "content_hash": state.get("content_hash"), "at": _now()}
    _write(out_dir, state)
    return token


def record_qc(out_dir, blocks: int, detail: str = "") -> None:
    """Record finalize's QC outcome. `severity: "block"` used to be decorative:
    finalize counted blocks, printed the tally, and returned 0, and nothing
    downstream ever read it. Recording it here lets compile refuse."""
    state = read_state(out_dir)
    state["qc"] = {"blocks": int(blocks or 0), "detail": detail, "at": _now()}
    _write(out_dir, state)


def record_vision_qc(out_dir, deck: str, slides_reviewed: int, findings: int = 0) -> None:
    """Record that a real page-by-page VISION pass ran over the compiled deck.

    "Done" used to be an orchestrator claim backed by the deterministic
    self-check, which is structurally blind to overlaps and whitespace. This
    turns the claim into a fact another step can verify. slide-qc writes it.
    """
    state = read_state(out_dir)
    state["vision_qc"] = {"deck": str(deck), "slides_reviewed": int(slides_reviewed),
                          "findings": int(findings), "at": _now()}
    _write(out_dir, state)


def record_compile(out_dir) -> None:
    """A final deck was compiled from the approved picks."""
    state = read_state(out_dir)
    state.setdefault("stages", {})["compile"] = {"at": _now()}
    _write(out_dir, state)


def has_compiled(out_dir) -> bool:
    """True once this build has produced a final deck from an approval."""
    return bool(read_state(out_dir).get("stages", {}).get("compile"))


def invalidate_review(out_dir, reason: str = "") -> bool:
    """Drop any recorded review approval. Called when a stage REBUILDS output that
    was already reviewed (a targeted re-finalize, or any re-finalize after a
    compile), so a changed deck cannot ship on the approval the user gave for the
    previous content. Returns True if an approval was actually dropped.

    Deliberately NOT called on the first full finalize: the documented order is
    review -> finalize -> compile, so finalize runs once between the pick and the
    compile, and invalidating there would make every build unshippable.
    """
    state = read_state(out_dir)
    if not state.get("review"):
        return False
    state.pop("review", None)
    state.setdefault("stages", {})["review_invalidated"] = {
        "at": _now(), "reason": reason or "output rebuilt after approval"}
    _write(out_dir, state)
    return True


def check_compile_allowed(out_dir, review_token: str) -> tuple[bool, str]:
    """True only if a real review happened for the CURRENT content and the
    supplied token matches. Returns (ok, reason)."""
    state = read_state(out_dir)
    if not state:
        return False, ("no _state.json in this out dir — prep + build_review have "
                       "not run here (or you pointed --out at the wrong folder)")
    review = state.get("review")
    if not review:
        return False, ("no review recorded — REVIEW.html was not built, or a "
                       "(re)build invalidated it. Run build_review.py and have the "
                       "user pick first.")
    if not review_token:
        return False, ("no --review-token supplied — copy it from REVIEW.html's "
                       "'Build my deck' command after the user picks.")
    if review_token != review.get("token"):
        return False, ("--review-token does not match the current REVIEW.html. "
                       "Rebuild the review or copy the current token; never invent one.")
    cur = state.get("content_hash")
    if cur and review.get("content_hash") != cur:
        return False, ("the review is stale — the deck was re-prepped/rebuilt after "
                       "this review. Run build_review.py again and have the user re-pick.")
    # A recorded QC block is a hard stop. Absence of a QC record is "no opinion"
    # (finalize has not run here), never an implicit pass.
    qc = state.get("qc") or {}
    if int(qc.get("blocks") or 0) > 0:
        return False, (f"QC recorded {qc['blocks']} blocking issue(s) for this build"
                       + (f": {qc.get('detail')}" if qc.get("detail") else "")
                       + ". Fix them and re-run finalize_deck.py; 'block' severity "
                         "now actually blocks the compile.")
    return True, "ok"


def canonical_out(out_dir):
    """The out-dir recorded at prep, or None."""
    return read_state(out_dir).get("canonical_out")
