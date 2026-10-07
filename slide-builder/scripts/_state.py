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


def _bump(state: dict) -> int:
    """Next value of the build's event counter. Timestamps are to the second,
    so "did the compile come after the last prep/finalize?" needs a counter."""
    state["rev"] = int(state.get("rev") or 0) + 1
    return state["rev"]


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
    state.setdefault("stages", {})["prep"] = {"at": _now(), "rev": _bump(state)}
    state.pop("review", None)       # any (re)prep invalidates prior approval
    state.pop("final_check", None)  # ...and the final look at the finished picks
    _write(out_dir, state)


def record_review(out_dir) -> str:
    """Review page built: return the approval token for this content, minting one
    only if there is none yet for the current content.

    Reusing it matters: a fresh token on every rebuild of the page voided the
    command the user had already copied from the previous one, and compile then
    said "does not match" for no reason the user could see.
    """
    state = read_state(out_dir)
    review = state.get("review") or {}
    if review.get("token") and review.get("content_hash") == state.get("content_hash"):
        return review["token"]
    token = secrets.token_hex(8)
    state.setdefault("stages", {})["review"] = {"at": _now()}
    state["review"] = {"token": token, "content_hash": state.get("content_hash"), "at": _now()}
    _write(out_dir, state)
    return token


# ---------------------------------------------------------------------------
# Approval binding. The review page emits a line like
#     PICKS slide_01=A;slide_02=C CHECK 1a2b3c4d
# where CHECK is computed from the review token and the exact picks. The same
# function runs in the page (JavaScript) and here. It is not cryptography: it
# makes a mistyped or hand-edited pick list fail loudly instead of shipping the
# wrong option. (The 09/24 build recorded slide 2 as B when A was picked.)
# ---------------------------------------------------------------------------

def fnv1a32(text: str) -> str:
    """32-bit FNV-1a over the text's characters, as 8 hex digits. Mirrors the
    JavaScript in build_review.py character for character (ASCII input)."""
    h = 0x811C9DC5
    for ch in text:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return f"{h:08x}"


def canonical_picks(picks) -> str:
    """'ALL', or 'slide_01=A;slide_02=C' sorted by slide."""
    if picks == "ALL":
        return "ALL"
    return ";".join(f"{k}={picks[k]}" for k in sorted(picks))


def approval_check(token: str, canonical: str) -> str:
    return fnv1a32(f"{token}|{canonical}")


def record_picks(out_dir, picks: dict, all_options: bool = False) -> None:
    """The user's approved picks, as verified by record_picks.py. Recording new
    picks clears any earlier final check: that look was at different slides."""
    state = read_state(out_dir)
    review = state.get("review") or {}
    review.update({"picks": picks, "all_options": bool(all_options),
                   "approved_at": _now()})
    state["review"] = review
    state.pop("final_check", None)
    _write(out_dir, state)


def record_final_check(out_dir, digests: dict) -> str:
    """The final-check page was built over these finished files. Returns the
    token its Build command carries; compile refuses unless the files still have
    these exact bytes."""
    state = read_state(out_dir)
    fc = state.get("final_check") or {}
    # Same files, same content: keep the token, so rebuilding the page does not
    # void a Build command the user already copied.
    if (fc.get("token") and fc.get("digests") == dict(digests)
            and fc.get("content_hash") == state.get("content_hash")):
        return fc["token"]
    token = secrets.token_hex(8)
    state["final_check"] = {"token": token, "digests": dict(digests), "at": _now(),
                            "content_hash": state.get("content_hash")}
    _write(out_dir, state)
    return token


def record_qc(out_dir, blocks: int, detail: str = "") -> None:
    """Record finalize's QC outcome. `severity: "block"` used to be decorative:
    finalize counted blocks, printed the tally, and returned 0, and nothing
    downstream ever read it. Recording it here lets compile refuse."""
    state = read_state(out_dir)
    state["qc"] = {"blocks": int(blocks or 0), "detail": detail, "at": _now()}
    _write(out_dir, state)


def record_override(out_dir, name: str, detail: str = "") -> None:
    """A gate was deliberately overridden. Kept in the build's record so a deck
    built past a check says so, rather than looking like it passed it."""
    state = read_state(out_dir)
    state.setdefault("overrides", []).append(
        {"override": name, "detail": detail, "at": _now()})
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
    # Anything finalize writes is something the user has not looked at yet.
    state.pop("final_check", None)
    _write(out_dir, state)


def shift_option_records(out_dir, insert_n: int) -> None:
    """An insert at N moved slide folders >= N up by one; move their records too.

    The new slide N has no record (nothing has been finalized for it), so it
    cannot be shipped until it is.
    """
    state = read_state(out_dir)
    qc = state.get("qc") or {}
    by = qc.get("by_option") or {}
    shifted = {}
    for key, val in by.items():
        try:
            slide, letter = key.split("/")
            n = int(slide.split("_")[1])
        except (ValueError, IndexError):
            shifted[key] = val
            continue
        shifted[option_key(n + 1, letter) if n >= insert_n else key] = val
    qc["by_option"] = shifted
    state["qc"] = qc
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
    fin.update({"status": status, "reason": reason, "ended": _now(), "rev": _bump(state)})
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
                         unreachable: int = 0, visual_only: bool = False) -> None:
    """Record reconciliation state for a SUPPLIED page that is being replicated.

    Deliberately records only what the machine owns: how many figure-bearing
    slots a human has not yet resolved. It does NOT record "the figures match the
    brief" — deciding that "6-12 months" and "sold out" denote the same quantity
    is a semantic judgment, and a gate that asserted it would be false assurance.
    `keep_source` and `unreachable` are carried so delivery can state how much was
    taken on trust rather than checked. `visual_only` marks a supplied PDF page
    or picture: nothing on it was machine-read, it is checked by eye only.
    """
    state = read_state(out_dir)
    state["source_ledger"] = {"unresolved": int(unresolved or 0),
                              "keep_source": int(keep_source or 0),
                              "unreachable": int(unreachable or 0),
                              "visual_only": bool(visual_only),
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


def record_vision_qc(out_dir, deck: str, slides_reviewed: int, findings: int = 0,
                     criticals: int = 0, majors: int = 0, advisories: int = 0) -> None:
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
                          "findings": int(findings or (criticals + majors + advisories)),
                          "criticals": int(criticals), "majors": int(majors),
                          "advisories": int(advisories),
                          "at": _now(), "digest": file_digest(deck)}
    _write(out_dir, state)


def record_compile(out_dir, kind: str = "picks", output=None, slides: int = 0,
                   options=None) -> None:
    """A deck was compiled. Records what came out, so check_done can verify
    the file it is shown is that file, unchanged, built from current content.

    kind: 'picks' (the final deck), 'all_variations' (every option, for
    comparison) or 'splice' (rebuilt slides put back into an external deck).
    """
    state = read_state(out_dir)
    state.setdefault("stages", {})["compile"] = {
        "at": _now(), "kind": kind, "rev": _bump(state),
        "output": str(Path(output).resolve()) if output else "",
        "digest": file_digest(output) if output else "",
        "content_hash": state.get("content_hash"),
        "slides": int(slides or 0),
        "options": list(options or [])}
    _write(out_dir, state)


def has_compiled(out_dir) -> bool:
    """True once this build has produced a final deck from an approval."""
    return bool(read_state(out_dir).get("stages", {}).get("compile"))


def check_compile_allowed(out_dir, final_token: str, themed_path_for=None) -> tuple[bool, str]:
    """May a deck be compiled? Returns (ok, reason).

    The order this enforces (the owner's decision, 2026-09-30):
      1. REVIEW.html: the user picks per slide, from sketches for sketch-path
         slides and finished renders for direct-path ones.
      2. record_picks.py records exactly those picks, verified against the
         page's check code.
      3. Only the picked sketch designs are translated; finalize runs.
      4. build_review.py --final: the user looks at every pick, finished, on
         the template. That page's Build command carries the final token.
      5. compile, which refuses unless the finished files still have the bytes
         the user saw at step 4.

    themed_path_for(option_key) -> Path of that option's finished .pptx. When
    given, each shipped option's bytes are compared with the final check.
    """
    state = read_state(out_dir)
    if not state:
        return False, ("no _state.json in this out dir — prep has not run here "
                       "(or --out points at the wrong folder)")
    review = state.get("review")
    if not review:
        return False, ("no review recorded — REVIEW.html was not built, or a "
                       "(re)build cleared it. Run build_review.py and have the user pick.")
    cur = state.get("content_hash")
    if cur and review.get("content_hash") != cur:
        return False, ("the review is stale — the deck was re-prepped after it. "
                       "Run build_review.py again and have the user re-pick.")
    if not review.get("picks"):
        return False, ("no approved picks recorded. The user's 'Build my deck' "
                       "command from REVIEW.html runs record_picks.py; nothing else "
                       "records picks.")
    fc = state.get("final_check")
    if not fc:
        return False, ("the user has not had the final look at the finished picks. "
                       "Run finalize_deck.py, then build_review.py --final, and wait "
                       "for the user's Build command from FINAL-CHECK.html.")
    if not final_token:
        return False, ("no --final-token supplied. It is in the Build command on "
                       "FINAL-CHECK.html; never invent it.")
    if final_token != fc.get("token"):
        return False, ("--final-token does not match the current FINAL-CHECK.html. "
                       "Use the command from the latest final check.")
    if themed_path_for is not None:
        changed = [k for k, d in (fc.get("digests") or {}).items()
                   if file_digest(themed_path_for(k)) != d]
        if changed:
            return False, (f"{len(changed)} finished slide(s) changed after the final "
                           f"check ({', '.join(changed[:4])}). The user approved "
                           "different files. Run build_review.py --final again.")
    ok, why = check_ledger(state)
    if not ok:
        return False, why
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
