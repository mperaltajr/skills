#!/usr/bin/env python3
"""check_done.py — is this deck actually deliverable?

"Done" was an orchestrator claim. It has been claimed over a deck with open
defects, over a file that would not open, over a deck that was edited after QC,
over a deck compiled from an older brief, and over a folder with no deck in it.
An audit on 2026-09-30 got DELIVERABLE out of this script for a text file
containing the words "not a pptx".

So this checks one unbroken chain of recorded facts, each tied to the last:

  1. a compile SUCCEEDED and recorded what it produced (path, bytes, the content
     it was built from, slide count)
  2. the deck being checked IS that file, byte for byte
  3. it was built from the CURRENT brief (nothing re-prepped since)
  4. it opens, and has no structure PowerPoint refuses
  5. every option in it was finalized with no blocking findings
  6. a VISION pass was recorded over these same bytes, covering every slide
  7. that pass left no open Critical or Major findings (only Advisory may remain)
  8. every figure on a replicated supplied page was reconciled

It is deliberately dumb: it verifies recorded facts, it does not re-run QC.

Run:  py -3 scripts/check_done.py --out <out_dir> [--deck <path>]
Exit: 0 deliverable | 1 not deliverable | 2 bad usage
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "slide-qc" / "scripts"))
import _state  # noqa: E402


def _same_file(a, b) -> bool:
    try:
        return Path(a).resolve() == Path(b).resolve()
    except Exception:
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify a deck is actually deliverable.")
    ap.add_argument("--out", required=True, type=Path, help="Build output dir.")
    ap.add_argument("--deck", default=None,
                    help="The file you intend to send. Default: the file the last "
                         "successful compile recorded. A different path is accepted "
                         "only if it is byte-identical to that file.")
    args = ap.parse_args(argv)

    if not args.out.exists():
        print(f"ERROR: out dir not found: {args.out}")
        return 2

    state = _state.read_state(args.out)
    problems: list[str] = []

    def _refuse() -> int:
        print("NOT DELIVERABLE:")
        for p in problems:
            print(f"  - {p}")
        print("\nDo not tell the user the deck is finished until this passes.")
        return 1

    # 1. A successful compile, with a record of what it produced.
    comp = (state.get("stages") or {}).get("compile") or {}
    if not state:
        problems.append("no _state.json — this build has no recorded history at all")
        return _refuse()
    if not comp:
        problems.append("no successful compile recorded — the deck was never built "
                        "through compile_picks.py, or every compile failed")
        return _refuse()
    if not comp.get("output") or not comp.get("digest"):
        problems.append("the compile record predates output tracking; re-run "
                        "compile_picks.py so there is a record of what it produced")
        return _refuse()

    # 2. The deck being checked is that file.
    recorded = Path(comp["output"])
    deck = Path(args.deck) if args.deck else recorded
    if not deck.exists():
        problems.append(f"no deck at {deck} — nothing to deliver")
        return _refuse()
    digest = _state.file_digest(deck)
    if digest != comp["digest"]:
        if _same_file(deck, recorded):
            problems.append(
                "the deck has changed since it was compiled. Edits made to a "
                "compiled deck are how defects shipped before; rebuild through "
                "the pipeline and recompile.")
        else:
            problems.append(
                f"{deck} is not the deck the last compile produced ({recorded}). "
                "Check the file you are actually sending.")

    # 3. Built from the current brief, and nothing rebuilt since.
    if comp.get("content_hash") != state.get("content_hash"):
        problems.append(
            "the brief or build inputs changed after this deck was compiled "
            "(prep ran again). This deck shows the old content; recompile.")
    # A single-slide rebuild keeps the same brief, so the content hash alone
    # missed it: the old deck stayed DELIVERABLE after slide 2 was redesigned.
    # The build's event counter says what happened after the compile.
    _crev = int(comp.get("rev") or 0)
    _prep_rev = int(((state.get("stages") or {}).get("prep") or {}).get("rev") or 0)
    _fin_rev = int((state.get("finalize") or {}).get("rev") or 0)
    if _crev and _prep_rev > _crev:
        problems.append(
            "a slide was rebuilt or inserted after this deck was compiled, so the "
            "deck does not contain it. Finish the review sequence and recompile.")
    elif _crev and _fin_rev > _crev:
        problems.append(
            "finalize ran again after this deck was compiled, so the deck may not "
            "match the current slides. Finish the review sequence and recompile.")

    # 4. Opens, and no structure PowerPoint refuses.
    n_deck = 0
    try:
        from pptx import Presentation
        prs = Presentation(str(deck))
        n_deck = len(prs.slides)
    except Exception as exc:
        problems.append(f"the deck does not open: {type(exc).__name__}: {exc}")
        prs = None
    if prs is not None:
        try:
            from pptx_openability import check_openability
            issues = check_openability(prs)
            if issues:
                problems.append(
                    f"{len(issues)} structure(s) PowerPoint would refuse, e.g. "
                    f"slide {issues[0]['slide']}: {issues[0]['issue'][:120]}")
        except Exception as exc:
            problems.append(f"could not check openability: {type(exc).__name__}: {exc}")
        if comp.get("slides") and n_deck != int(comp["slides"]):
            problems.append(f"the deck has {n_deck} slides; the compile produced "
                            f"{comp['slides']}")

    # 5. Every shipped option finalized clean (a re-finalize after compile can
    # record new blocks against options already in the deck).
    shipped = comp.get("options") or []
    if shipped:
        ok, why = _state.check_options_finalized(state, shipped)
        if not ok:
            problems.append(why)

    # 6 + 7. A vision pass over these bytes, every slide, nothing open above Advisory.
    vq = state.get("vision_qc") or {}
    if not vq:
        problems.append(
            "no vision pass recorded — the deterministic self-check does NOT "
            "count. Run slide-qc over the compiled deck; it records the pass.")
    else:
        if vq.get("digest") != digest:
            problems.append(
                "the recorded vision pass was over different bytes than this deck "
                "(it was edited, recompiled, or the pass looked at another file). "
                "Re-run slide-qc on the deck you are sending.")
        seen = int(vq.get("slides_reviewed") or 0)
        if n_deck and seen != n_deck:
            problems.append(
                f"the vision pass records {seen} slide(s) reviewed; the deck has "
                f"{n_deck}. A partial look is how defects shipped last time.")
        crit, maj = int(vq.get("criticals") or 0), int(vq.get("majors") or 0)
        if "criticals" not in vq:
            problems.append("the vision pass predates severity tracking; re-run "
                            "slide-qc so Critical and Major counts are recorded")
        elif crit or maj:
            problems.append(
                f"the vision pass left {crit} Critical and {maj} Major finding(s) "
                "open. Everything above Advisory must be fixed (or corrected to "
                "'not a defect' if the finding was wrong), then QC re-run.")

    # 8. Supplied-page figures.
    sl = state.get("source_ledger") or {}
    if int(sl.get("unresolved") or 0) > 0:
        problems.append(
            f"{sl['unresolved']} figure(s) on a supplied/replicated page are "
            "unreconciled; resolve every row in source_ledger.json")

    if problems:
        return _refuse()

    kind = comp.get("kind", "picks")
    label = {"picks": "final deck", "all_variations": "all-options comparison deck",
             "splice": "spliced deck"}.get(kind, kind)
    print(f"DELIVERABLE ({label}): {deck}")
    print(f"  compiled at   : {comp.get('at')}  ({n_deck} slides)")
    print(f"  vision pass   : {vq.get('slides_reviewed')} slide(s), "
          f"{vq.get('advisories', 0)} Advisory open, {vq.get('at')}")
    # Every gate that was deliberately passed over in this build. They were
    # recorded and then never shown to anyone; delivery is where the user sees
    # what the deck did NOT go through.
    overrides = state.get("overrides") or []
    if overrides:
        print(f"  overrides     : {len(overrides)} gate(s) passed over in this build:")
        for o in overrides:
            print(f"                  - {o.get('override')}: {o.get('detail', '')} "
                  f"({o.get('at', '')})")
        print("                  Tell the user about these when you deliver.")
    if sl:
        # State plainly how much was taken on trust rather than verified.
        print(f"  supplied page : {sl.get('keep_source', 0)} figure(s) kept "
              f"verbatim from the source, {sl.get('unreachable', 0)} surface(s) "
              f"unreadable and covered only by the vision pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
