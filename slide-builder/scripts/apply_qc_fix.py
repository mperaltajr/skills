#!/usr/bin/env python3
"""apply_qc_fix.py — finish a QC fix the user approved in chat, straight to the deck.

After a deck is compiled, slide-qc lists what is wrong and the user says "fix
it". The slides get rebuilt (build_deck.py --slide N with the QC finding in
_prior_feedback.md, one option each). Sending the user back through REVIEW.html
and FINAL-CHECK.html for a fix they already approved was pure friction (the
owner's call, 2026-10-02), so this records the approval from chat instead:

  py -3 scripts/apply_qc_fix.py --out <out_dir> --slides 5[,7] --approved "<the user's words>"

It
  1. refuses unless a deck was already compiled from this build (a first build
     still goes through both pages), and each fixed slide has exactly one
     option (the redesign);
  2. keeps every other slide's recorded pick and picks the redesign for the
     fixed slides, writing the user's words into the build record;
  3. converts a redesigned sketch with translate_html.py (stops if part of it
     needs the translator agent; run the agent, then this again);
  4. finalizes the fixed slides, writes the final-check record over the
     finished files (FINAL-CHECK.html is still written, as the record), and
     compiles.
Then run slide-qc on the new deck, as after any compile.

Exit: 0 compiled | 3 translator agent needed first | 5 refused | 2 bad usage
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import _paths as _p  # noqa: E402
import _state  # noqa: E402


def _letters(slide_dir: Path) -> list[str]:
    found = set()
    for p in slide_dir.glob("option_*"):
        m = re.match(r"option_([A-F])(?:[._])", p.name)
        if m and p.is_file():
            found.add(m.group(1))
    return sorted(found)


def _run(*args) -> int:
    return subprocess.run([sys.executable, *map(str, args)]).returncode


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Compile a QC fix the user approved in chat.")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--slides", required=True, help="Comma-separated slide numbers that were fixed.")
    ap.add_argument("--approved", required=True,
                    help="The user's own words approving the fix, recorded verbatim.")
    args = ap.parse_args(argv)
    out = args.out
    try:
        fixed = sorted({int(x) for x in args.slides.split(",") if x.strip()})
    except ValueError:
        print("ERROR: --slides takes numbers, e.g. 5 or 5,7")
        return 2
    if not args.approved.strip():
        print("REFUSED: --approved needs the user's words approving the fix.")
        return 5

    state = _state.read_state(out)
    if not (state.get("stages") or {}).get("compile"):
        print("REFUSED: no deck has been compiled from this build yet. A first build "
              "goes through REVIEW.html and FINAL-CHECK.html; this command is only for "
              "fixes after the quality check.")
        return 5
    picks_path = out / "picks.json"
    try:
        picks = json.loads(picks_path.read_text(encoding="utf-8"))
    except Exception:
        print("REFUSED: no earlier picks.json to keep the other slides' picks from.")
        return 5
    if not isinstance(picks, dict):
        print("REFUSED: the earlier build was an all-options deck; pick in REVIEW.html.")
        return 5

    for n in fixed:
        key = _p.slide_key(n)
        letters = _letters(out / key)
        if len(letters) != 1:
            print(f"REFUSED: slide {n} has {len(letters)} options ({', '.join(letters) or 'none'}). "
                  "A QC fix rebuilds one option; with several, the user picks in REVIEW.html.")
            return 5
        picks[key] = letters[0]
    for k, v in picks.items():
        if v != "-" and v not in _letters(out / k):
            print(f"REFUSED: {k} no longer has option {v}; pick in REVIEW.html.")
            return 5

    _state.record_review(out)                 # a review token for the current content
    _state.record_picks(out, picks)
    picks_path.write_text(json.dumps(picks, indent=2), encoding="utf-8")
    _state.record_override(out, "qc_fix_approved_in_chat",
                           f"slides {','.join(map(str, fixed))}: {args.approved.strip()}")
    print(f"[ok] recorded the fix for slide(s) {', '.join(map(str, fixed))} "
          f"as approved in chat; other picks kept.")

    # Convert a redesigned sketch.
    jobs = []
    for n in fixed:
        key = _p.slide_key(n)
        L = picks[key]
        html = out / key / f"option_{L}.html"
        if html.exists():
            import translate_html
            jobs.append((html, out / key, L, translate_html._subtitle_as_shape(out, n)))
    if jobs:
        import translate_html
        reports = translate_html.translate_many(jobs)
        pending = [r for r in reports if r["needs_agent"]]
        if pending:
            print("Part of the redesign needs the translator agent first (FALLBACK MODE):")
            for r in pending:
                h = Path(r["html"])
                print(f"  {h.with_name(h.stem + '_native.py')}")
            print("Run it, then run this command again.")
            return 3

    meta = json.loads(_p.meta_json(out).read_text(encoding="utf-8"))
    tpl = meta.get("template")
    for n in fixed:
        rc = _run(HERE / "finalize_deck.py", "--out", out, "--template", tpl, "--slide", n)
        if rc != 0:
            print(f"finalize_deck.py --slide {n} exited {rc}; fix that and run this again.")
            return rc

    import build_review
    rc = build_review.build_final_check(out, meta)
    if rc != 0:
        return rc
    token = (_state.read_state(out).get("final_check") or {}).get("token")
    flags = []
    if meta.get("adopted_source"):
        flags = ["--splice-into", meta["adopted_source"]]
    rc = _run(HERE / "compile_picks.py", "--out", out, "--final-token", token, *flags)
    if rc == 0:
        print("\nNext: run slide-qc on the new deck (required), then check_done.py.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
