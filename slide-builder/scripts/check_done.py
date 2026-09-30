#!/usr/bin/env python3
"""check_done.py — is this deck actually deliverable?

"Done" was an orchestrator claim. The deck was declared QC'd while defects
survived on three slides, because the deterministic self-check is structurally
blind to the things that shipped (a rule drawn through text, large empty areas)
and nothing forced a real page-by-page look.

This turns the claim into a checkable fact. It refuses unless ALL of:

  1. the deck exists                                     (--deck, or in <out>)
  2. a final deck was compiled from an approved review   (stages.compile)
  3. finalize recorded no blocking QC findings           (qc.blocks == 0)
  4. a VISION pass was recorded over that same deck      (vision_qc)
     covering every slide in it, and over these exact bytes — a deck
     hand-edited after QC is a deck nobody has reviewed

It is deliberately dumb: it verifies recorded facts, it does not re-run QC.

Run:  py -3 scripts/check_done.py --out <out_dir>   (python3 on macOS/Linux)
Exit: 0 deliverable | 1 not deliverable | 2 bad usage
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _paths as _p  # noqa: E402
import _state  # noqa: E402


# The names compile_picks.py gives its output. --all-variations writes the
# second one (every option for every slide, one editable deck), and that IS a
# deliverable — it is what "put all the options in a deck" produces.
_DECK_NAMES = ("final_deck.pptx", "final_deck_all_variations.pptx")


def _resolve_deck(out: Path, explicit: str | None) -> Path:
    """Find the deck to check. An explicit --deck always wins."""
    if explicit:
        return Path(explicit)
    existing = [out / n for n in _DECK_NAMES if (out / n).exists()]
    if len(existing) == 1:
        return existing[0]
    if len(existing) > 1:
        # Both present: check the one the vision pass actually looked at, so a
        # stale sibling from an earlier run cannot decide the answer.
        recorded = (_state.read_state(out).get("vision_qc") or {}).get("deck")
        if recorded:
            for cand in existing:
                try:
                    if Path(recorded).resolve() == cand.resolve():
                        return cand
                except Exception:
                    continue
        return max(existing, key=lambda p: p.stat().st_mtime)
    return out / _DECK_NAMES[0]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify a deck is actually deliverable.")
    ap.add_argument("--out", required=True, type=Path, help="Build output dir.")
    ap.add_argument("--deck", default=None,
                    help="Final deck path. Default: final_deck.pptx or "
                         "final_deck_all_variations.pptx in <out>, whichever is there.")
    args = ap.parse_args(argv)

    if not args.out.exists():
        print(f"ERROR: out dir not found: {args.out}")
        return 2

    deck = _resolve_deck(args.out, args.deck)
    state = _state.read_state(args.out)
    problems: list[str] = []

    if not deck.exists():
        # Without this the checks below silently degrade: the deck-identity test
        # is skipped, the slide count reads 0, and the coverage test never fires.
        # A build with no deck at all used to print DELIVERABLE.
        problems.append(
            f"no deck at {deck} — nothing to deliver. Pass --deck if the final "
            f"file is somewhere else.")

    if not state:
        problems.append("no _state.json — this build has no recorded history at all")

    if not state.get("stages", {}).get("compile"):
        problems.append("no compile recorded — the final deck was never built "
                        "through compile_picks.py")

    blocks = int((state.get("qc") or {}).get("blocks") or 0)
    if blocks:
        problems.append(f"finalize recorded {blocks} blocking QC finding(s); "
                        "fix them and re-run finalize_deck.py")

    sl = state.get("source_ledger") or {}
    if int(sl.get("unresolved") or 0) > 0:
        problems.append(
            f"{sl['unresolved']} figure(s) on a supplied/replicated page are "
            "unreconciled; resolve every row in source_ledger.json")

    vq = state.get("vision_qc") or {}
    if not vq:
        problems.append(
            "no vision pass recorded — the deterministic self-check does NOT "
            "count. Run slide-qc over the compiled deck; it records the pass.")
    else:
        if vq.get("deck") and deck.exists():
            try:
                same = Path(vq["deck"]).resolve() == deck.resolve()
            except Exception:
                same = False
            if not same:
                problems.append(
                    f"the recorded vision pass was over {vq.get('deck')!r}, not "
                    f"{str(deck)!r} — re-run slide-qc on the deck you are shipping")
        if deck.exists():
            recorded_digest = vq.get("digest") or ""
            if recorded_digest and recorded_digest != _state.file_digest(deck):
                problems.append(
                    "the deck has changed since the vision pass — you are looking "
                    "at a file nobody reviewed. Re-run slide-qc over the current "
                    "deck. (Every hand-edit applied after QC last time broke "
                    "something.)")
            try:
                from pptx import Presentation
                n_deck = len(Presentation(str(deck)).slides)
            except Exception:
                n_deck = 0
            seen = int(vq.get("slides_reviewed") or 0)
            if n_deck and seen < n_deck:
                problems.append(
                    f"the vision pass covered {seen} of {n_deck} slides — "
                    "a partial look is how defects shipped last time")

    if problems:
        print("NOT DELIVERABLE:")
        for p in problems:
            print(f"  - {p}")
        print("\nDo not tell the user the deck is finished until this passes.")
        return 1

    print(f"DELIVERABLE: {deck}")
    print(f"  compiled at        : {state['stages']['compile']['at']}")
    print(f"  blocking QC        : 0")
    print(f"  vision pass        : {vq.get('slides_reviewed')} slide(s), "
          f"{vq.get('findings', 0)} finding(s), {vq.get('at')}")
    if sl:
        # State plainly how much was taken on trust rather than verified. These
        # are not failures; they are the size of the unchecked surface, and they
        # belong in front of the person shipping the deck.
        print(f"  supplied page      : {sl.get('keep_source', 0)} figure(s) kept "
              f"verbatim from the source, {sl.get('unreachable', 0)} surface(s) "
              f"unreadable and covered only by the vision pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
