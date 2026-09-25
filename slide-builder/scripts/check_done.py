#!/usr/bin/env python3
"""check_done.py — is this deck actually deliverable?

"Done" was an orchestrator claim. The deck was declared QC'd while defects
survived on three slides, because the deterministic self-check is structurally
blind to the things that shipped (a rule drawn through text, large empty areas)
and nothing forced a real page-by-page look.

This turns the claim into a checkable fact. It refuses unless ALL of:

  1. a final deck was compiled from an approved review   (stages.compile)
  2. finalize recorded no blocking QC findings           (qc.blocks == 0)
  3. a VISION pass was recorded over that same deck      (vision_qc)
     covering every slide in it

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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify a deck is actually deliverable.")
    ap.add_argument("--out", required=True, type=Path, help="Build output dir.")
    ap.add_argument("--deck", default=None,
                    help="Final deck path (default: <out>/final_deck.pptx).")
    args = ap.parse_args(argv)

    if not args.out.exists():
        print(f"ERROR: out dir not found: {args.out}")
        return 2

    deck = Path(args.deck) if args.deck else (args.out / "final_deck.pptx")
    state = _state.read_state(args.out)
    problems: list[str] = []

    if not state:
        problems.append("no _state.json — this build has no recorded history at all")

    if not state.get("stages", {}).get("compile"):
        problems.append("no compile recorded — the final deck was never built "
                        "through compile_picks.py")

    blocks = int((state.get("qc") or {}).get("blocks") or 0)
    if blocks:
        problems.append(f"finalize recorded {blocks} blocking QC finding(s); "
                        "fix them and re-run finalize_deck.py")

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
        n_deck = 0
        if deck.exists():
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
