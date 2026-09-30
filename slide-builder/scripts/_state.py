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


def option_key(slide_n: int, letter: str) -> str:
    """Stable key for one design option, e.g. 'slide_05/A'."""
    return f"slide_{int(slide_n):02d}/{letter}"


def begin_finalize(out_dir, slide=None) -> None:
    """Finalize is starting. Drop the per-option QC records it is about to
    replace, and mark the run as in progress.

    Dropping them first is what makes a crash or an early refusal honest: an
    option finalize never finished has NO record, and compile refuses an option
    with no record. Before this, a refused finalize left its already-saved
    output looking finished and the last clean QC count in place, so the deck
    shipped anyway.
    """
    state = read_state(out_dir)
    qc = state.get("qc") or {}
    by = dict(qc.get("by_option") or {})
    if slide is None:
        by = {}
    else:
        prefix = f"slide_{int(slide):02d}/"
        by = {k: v for k, v in by.items() if not k.startswith(prefix)}
    state["qc"] = {**qc, "by_option": by,
                   "blocks": sum(int(v.get("blocks") or 0) for v in by.values())}
    state["finalize"] = {"status": "running", "slide": slide, "at": _now(),
                         "content_hash": state.get("content_hash")}
    _write(out_dir, state)


def record_option_qc(out_dir, results: dict) -> None:
    """Merge per-option QC results: {option_key: {"blocks": n, "reasons": [...]}}.

    Per option, not per deck. A deck-wide count was overwritten by every
    `finalize --slide N`, so fixing slide 3 erased the blocks on slides 5 and 7.
    """
    state = read_state(out_dir)
    qc = state.get("qc") or {}
    by = dict(qc.get("by_option") or {})
    by.update(results)
    blocked = sorted(k for k, v in by.items() if int(v.get("blocks") or 0) > 0)
    state["qc"] = {"by_option": by,
                   "blocks": sum(int(v.get("blocks") or 0) for v in by.values()),
                   "detail": (f"blocked: {', '.join(blocked[:6])}"
                              + (" ..." if len(blocked) > 6 else "")) if blocked else "",
                   "at": _now()}
    _write(out_dir, state)


def end_finalize(out_dir, status: str, reason: str = "") -> None:
    """Record how the finalize run ended: 'ok' or 'failed'."""
    state = read_state(out_dir)
    fin = state.get("finalize") or {}
    fin.update({"status": status, "reason": reason, "ended": _now()})
    state["finalize"] = fin
    _write(out_dir, state)


def check_options_finalized(state: dict, option_keys) -> tuple[bool, str]:
    """Every option about to ship has a finished, unblocked finalize record."""
    fin = state.get("finalize") or {}
    if not fin:
        return False, ("finalize_deck.py has not run for this build, so nothing "
                       "has been put on the template or checked. Run it first.")
    if fin.get("status") == "running":
        return False, ("the last finalize_deck.py run did not finish (it crashed or "
                       "was interrupted). Re-run it.")
    by = (state.get("qc") or {}).get("by_option") or {}
    missing = [k for k in option_keys if k not in by]
    if missing:
        return False, (f"{len(missing)} option(s) about to ship were never finalized "
                       f"or their finalize did not finish: {', '.join(missing[:6])}. "
                       "Re-run finalize_deck.py for those slides.")
    blocked = [k for k in option_keys if int(by[k].get("blocks") or 0) > 0]
    if blocked:
        why = "; ".join(f"{k}: {', '.join(by[k].get('reasons') or [])[:120]}"
                        for k in blocked[:4])
        return False, (f"{len(blocked)} option(s) about to ship have blocking QC "
                       f"findings. {why}. Fix them and re-run finalize_deck.py.")
    return True, "ok"


def record_source_ledger(out_dir, unresolved: int, keep_source: int = 0,
                         unreachable: int = 0) -> None:
    """Record reconciliation state for a SUPPLIED page that is being replicated.

    Deliberately records only what the machine owns: how many figure-bearing
    slots a human has not yet resolved. It does NOT record "the figures match the
    brief" — deciding that "6-12 months" and "sold out" denote the same quantity
    is a semantic judgment, and a gate that asserted it would be false assurance.
    `keep_source` and `unreachable` are carried so delivery can state how much was
    taken on trust rather than checked.
    """
    state = read_state(out_dir)
    state["source_ledger"] = {"unresolved": int(unresolved or 0),
                              "keep_source": int(keep_source or 0),
                              "unreachable": int(unreachable or 0),
                              "at": _now()}
    _write(out_dir, state)


def file_digest(path) -> str:
    """Hash a file's bytes. Empty string when it cannot be read."""
    p = Path(path)
    h = hashlib.md5()
    try:
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()


def record_vision_qc(out_dir, deck: str, slides_reviewed: int, findings: int = 0) -> None:
    """Record that a real page-by-page VISION pass ran over the compiled deck.

    "Done" used to be an orchestrator claim backed by the deterministic
    self-check, which is structurally blind to overlaps and whitespace. This
    turns the claim into a fact another step can verify. slide-qc writes it.

    The deck's bytes are hashed into the record, because the pass is only
    evidence about the file that was actually looked at. Every ad hoc fix applied
    to a compiled deck after QC (badges, a label patch, a collision fix) produced
    a file nobody had reviewed, and each one broke something.
    """
    state = read_state(out_dir)
    state["vision_qc"] = {"deck": str(deck), "slides_reviewed": int(slides_reviewed),
                          "findings": int(findings), "at": _now(),
                          "digest": file_digest(deck)}
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
    # A supplied page that is being replicated must have every figure-bearing
    # slot resolved by a human first. Unresolved means nobody decided whether the
    # page's number or the brief's number is the right one.
    sl = state.get("source_ledger") or {}
    if int(sl.get("unresolved") or 0) > 0:
        return False, (f"{sl['unresolved']} figure(s) on the supplied page are "
                       "unreconciled. Every row in source_ledger.json needs a "
                       "resolution (bind_from_brief / keep_source / replace_with). "
                       "Replicating a page also replicates its numbers, and that is "
                       "how stale figures have shipped before.")
    # QC blocks are checked per option by check_options_finalized, against the
    # options actually being shipped. A deck-wide count here refused a compile
    # over an option nobody picked, and was wiped by every finalize --slide.
    return True, "ok"


def check_ledger(state: dict) -> tuple[bool, str]:
    """A replicated supplied page has every figure-bearing slot resolved."""
    sl = state.get("source_ledger") or {}
    if int(sl.get("unresolved") or 0) > 0:
        return False, (f"{sl['unresolved']} figure(s) on the supplied page are "
                       "unreconciled. Every row in source_ledger.json needs a "
                       "resolution (bind_from_brief / keep_source / replace_with).")
    return True, "ok"


def canonical_out(out_dir):
    """The out-dir recorded at prep, or None."""
    return read_state(out_dir).get("canonical_out")
