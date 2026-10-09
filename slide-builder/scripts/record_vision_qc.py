#!/usr/bin/env python3
"""record_vision_qc.py — record a quality-check round, with proof the pages were opened.

slide-qc calls this at the end of each round. It exists so "done" is a
recorded fact instead of an orchestrator claim: check_done.py refuses to call
a deck deliverable unless every page's reviewed image is that page's image in
the current render of this exact deck, a deck-wide look was recorded for this
exact deck, and no Critical or Major finding is open (owner's definition of
done, approved 2026-10-09).

Until 2026-10-09 this took a typed count (--slides-reviewed 71). One session
recorded 71 pages reviewed after opening about 9 page images. Now the count is
not typed; it is what the notes prove:

  1. qc_pages.py plan --out <build> works out which pages to read (the ones
     whose image changed since they were reviewed, or every page when there is
     no earlier review, the page count, renderer, dpi or template changed),
     and writes their pictures, each with a one-time check code in a band
     under the page, plus thumbnail sheets and changed-beside-unchanged pairs
     for the deck-wide look, and _qc/page_notes.json to fill in.
  2. For each page: its code, a short quote of its own visible text (checked
     against the slide's text), and the findings still OPEN on it.
  3. This script refuses unless every page of the round has a verified note,
     every sheet and pair code is right, and --slides-reviewed (if given) is
     no more than the pages the notes prove. It runs the whole-file hygiene and
     type-scale check itself, then records: re-read pages get their new
     review, unchanged pages keep theirs and their open findings.

Record findings that are OPEN after fixes. A finding that turned out to be
wrong is not open: leave it out (to clear one carried on an unchanged page,
plan with --also N and read that page again).

What the proof shows and does not show is in qc_pages.py's docstring: a right
code shows the picture was opened; nothing shows it was inspected carefully.

Run:
  py -3 scripts/record_vision_qc.py --out <build dir> [--deck <deck>]
      [--notes <_qc/page_notes.json>] [--slides-reviewed N]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "slide-qc" / "scripts"))
import _state  # noqa: E402
import qc_pages  # noqa: E402


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Record a quality-check round.")
    ap.add_argument("--out", required=True, type=Path, help="Build output dir.")
    ap.add_argument("--deck", default=None,
                    help="The deck that was reviewed (default: the deck the last "
                         "compile wrote, named after the topic).")
    ap.add_argument("--notes", default=None, type=Path,
                    help="The filled-in notes (default: <out>/_qc/page_notes.json).")
    ap.add_argument("--slides-reviewed", type=int, default=None,
                    help="Optional: how many pages you opened this round. Refused "
                         "when it is more than the notes prove.")
    for gone in ("--criticals", "--majors", "--advisories"):
        ap.add_argument(gone, type=int, default=None, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    if not args.out.exists():
        print(f"ERROR: out dir not found: {args.out}")
        return 2
    if any(v is not None for v in (args.criticals, args.majors, args.advisories)):
        print("ERROR: finding counts are no longer typed. Write each open finding on "
              "its page in _qc/page_notes.json (severity, issue); the record counts "
              "them, and keeps the ones on pages that did not change.")
        return 2
    deck = Path(args.deck) if args.deck else _state.compiled_deck(args.out)
    if not deck.exists():
        print(f"ERROR: no deck at {deck}. Record the round over the file you "
              "actually looked at.")
        return 2
    try:
        from pptx import Presentation
        Presentation(str(deck))
    except Exception as exc:
        print(f"ERROR: the deck does not open ({type(exc).__name__}: {exc}); there "
              "is nothing a vision pass could have looked at.")
        return 2
    notes_p = args.notes or (qc_pages.qc_dir(args.out) / qc_pages.NOTES)
    try:
        notes = json.loads(Path(notes_p).read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: could not read the notes at {notes_p} ({type(exc).__name__}: "
              f"{exc}). Run qc_pages.py plan --out \"{args.out}\" and fill in the file "
              "it writes.")
        return 2
    try:
        problems, result = qc_pages.verify_notes(args.out, deck, notes, args.slides_reviewed)
    except qc_pages.PlanError as exc:
        print(f"ERROR: {exc}")
        return 2
    if problems:
        print("REFUSED: the notes do not prove this round's pages were read:")
        for p in problems[:40]:
            print(f"  - {p}")
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more")
        print("Nothing was recorded. Fix the notes (or read the pages), then run this again.")
        return 3

    hyg = qc_pages.run_hygiene(deck)
    if not hyg.get("ran"):
        print(f"ERROR: the whole-file hygiene and type-scale check did not run "
              f"({hyg.get('error')}). Nothing was recorded.")
        return 2
    vq = qc_pages.record(args.out, deck, result, hyg)
    plan = result["plan"]
    print(f"[ok] recorded the round over {deck.name}: {vq['slides_reviewed']} page(s) "
          f"read with proof ({'every page' if plan.get('full') else 'the changed ones'}), "
          f"{vq['carried']} carried from earlier rounds, of {vq['pages_total']}.")
    if result.get("no_text"):
        print(f"     {len(result['no_text'])} page(s) have no text the script can read "
              f"(pictures): {', '.join(map(str, result['no_text'][:12]))}; for those "
              "only the check code was verified.")
    print(f"     deck-wide look: {len(plan.get('sheets') or [])} sheet(s), "
          f"{len(plan.get('pairs') or [])} pair(s); whole-file hygiene and type-scale "
          f"check: {hyg['criticals']} Critical, {hyg['majors']} Major, "
          f"{hyg['advisories']} Advisory (each Critical and Major there goes in the "
          "report; one still open goes in its page's findings).")
    print(f"     open now: {vq['criticals']} Critical, {vq['majors']} Major, "
          f"{vq['advisories']} Advisory")
    if vq["criticals"] or vq["majors"]:
        print("     check_done.py will refuse until the Critical and Major findings "
              "are fixed and the changed pages are read again.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
