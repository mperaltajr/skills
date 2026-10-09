#!/usr/bin/env python3
"""record_vision_qc.py — record that a real page-by-page VISION pass ran.

slide-qc calls this at the end of its review. It exists so "done" is a recorded
fact instead of an orchestrator claim: check_done.py refuses to call a deck
deliverable without it, refuses a pass over different bytes than the deck being
sent, refuses a pass that did not cover every slide, and refuses while any
Critical or Major finding is still open. Only Advisory findings may remain.

Record the counts that are OPEN after fixes, not the counts first found. A
finding that turned out to be wrong is not open: correct it in the QC report as
"not a defect" and leave it out of the count.

Run:
  py -3 scripts/record_vision_qc.py --out <out_dir> [--deck <the compiled deck>] \\
      --slides-reviewed 13 --criticals 0 --majors 0 --advisories 2
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _state  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Record a vision QC pass.")
    ap.add_argument("--out", required=True, type=Path, help="Build output dir.")
    ap.add_argument("--deck", default=None,
                    help="The deck that was reviewed (default: the deck the last "
                         "compile wrote, named after the topic).")
    ap.add_argument("--slides-reviewed", required=True, type=int,
                    help="How many slides you actually LOOKED at, one by one.")
    ap.add_argument("--criticals", required=True, type=int,
                    help="Critical findings still open.")
    ap.add_argument("--majors", required=True, type=int,
                    help="Major findings still open.")
    ap.add_argument("--advisories", type=int, default=0,
                    help="Advisory findings still open (these may remain).")
    args = ap.parse_args(argv)

    if not args.out.exists():
        print(f"ERROR: out dir not found: {args.out}")
        return 2
    deck = Path(args.deck) if args.deck else _state.compiled_deck(args.out)
    if not deck.exists():
        # The record is evidence about a specific file. Recording a pass over a
        # deck that is not there would leave check_done unable to verify anything.
        print(f"ERROR: no deck at {deck} — record the pass over the file you "
              f"actually looked at.")
        return 2
    try:
        from pptx import Presentation
        n = len(Presentation(str(deck)).slides)
    except Exception as exc:
        print(f"ERROR: the deck does not open ({type(exc).__name__}: {exc}); there "
              "is nothing a vision pass could have looked at.")
        return 2
    if args.slides_reviewed > n:
        print(f"ERROR: --slides-reviewed {args.slides_reviewed} but the deck has {n} "
              "slides. Record the number you actually looked at.")
        return 2
    if min(args.criticals, args.majors, args.advisories) < 0:
        print("ERROR: finding counts cannot be negative.")
        return 2

    _state.record_vision_qc(args.out, str(deck), args.slides_reviewed,
                            criticals=args.criticals, majors=args.majors,
                            advisories=args.advisories)
    print(f"[ok] recorded vision pass over {deck.name}: {args.slides_reviewed} of {n} "
          f"slide(s); open: {args.criticals} Critical, {args.majors} Major, "
          f"{args.advisories} Advisory")
    if args.criticals or args.majors:
        print("     check_done.py will refuse until the Critical and Major findings "
              "are fixed and QC is re-run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
