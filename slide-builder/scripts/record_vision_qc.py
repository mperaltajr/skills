#!/usr/bin/env python3
"""record_vision_qc.py — record that a real page-by-page VISION pass ran.

slide-qc calls this at the end of its review. It exists so "done" is a recorded
fact instead of an orchestrator claim: check_done.py refuses to call a deck
deliverable without it, and refuses a pass that covered fewer slides than the
deck actually has.

Run:
  py -3 scripts/record_vision_qc.py --out <out_dir> --deck <final_deck.pptx> \
      --slides-reviewed 13 [--findings 2]
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
    ap.add_argument("--deck", required=True, help="The deck that was reviewed.")
    ap.add_argument("--slides-reviewed", required=True, type=int,
                    help="How many slides you actually LOOKED at, one by one.")
    ap.add_argument("--findings", type=int, default=0,
                    help="How many issues the pass raised (0 is fine).")
    args = ap.parse_args(argv)

    if not args.out.exists():
        print(f"ERROR: out dir not found: {args.out}")
        return 2
    _state.record_vision_qc(args.out, args.deck, args.slides_reviewed, args.findings)
    print(f"[ok] recorded vision pass: {args.slides_reviewed} slide(s), "
          f"{args.findings} finding(s) over {args.deck}")
    print("     check_done.py will now accept this deck (if compile + QC are clean).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
