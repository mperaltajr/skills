#!/usr/bin/env python3
"""apply_qc_fix.py — finish a QC fix the user approved in chat, straight to the deck.

After a deck is compiled, slide-qc lists what is wrong and the user says "fix
it". The slides get rebuilt (build_deck.py --slide N with the QC finding in
_prior_feedback.md, one option each). Sending the user back through REVIEW.html
and FINAL-CHECK.html for a fix they already approved was pure friction (the
owner's call, 2026-10-02), so this records the approval from chat instead:

  py -3 scripts/apply_qc_fix.py --out <out_dir> --slides 5[,7] --approved "<the user's words>"

On a slide where the user kept several options (an all-options deck, or
"Picks: 1BC"), name the fixed option(s) after the slide number: --slides 1B
(or 1BC). Only those are converted again; the slide's other kept options stay
as they are, and the slide keeps all of them.

It
  1. refuses unless a deck was already compiled from this build (a first build
     still goes through both pages); a plain slide number needs exactly one
     option on disk (the redesign), a slide with several kept options needs
     the fixed letters, which must be among the kept ones;
  2. keeps every other slide's recorded pick and picks the redesign for the
     fixed slides, writing the user's words into the build record (check_done
     lists them at delivery as a chat approval);
  3. converts a redesigned sketch with translate_html.py when its design
     changed since it was last converted (stops if part of it needs the
     translator agent; run the agent, then this again: a slide the agent
     finished is not converted again, so its drawing is kept);
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
    ap.add_argument("--slides", required=True,
                    help="Comma-separated slides that were fixed: 5 or 5,7; on a slide "
                         "that keeps several options, the fixed letters too: 1B or 1BC,3.")
    ap.add_argument("--approved", required=True,
                    help="The user's own words approving the fix, recorded verbatim.")
    args = ap.parse_args(argv)
    out = args.out
    named: dict[int, str] = {}
    for tok in args.slides.split(","):
        tok = tok.strip()
        if not tok:
            continue
        m = re.fullmatch(r"(\d{1,3})([A-Fa-f]*)", tok)
        if not m:
            print("ERROR: --slides takes slide numbers, e.g. 5 or 5,7, or a slide "
                  "and its fixed options, e.g. 1B or 1BC,3")
            return 2
        n = int(m.group(1))
        named[n] = "".join(sorted(set(named.get(n, "") + m.group(2).upper())))
    fixed = sorted(named)
    if not fixed:
        print("ERROR: --slides takes slide numbers, e.g. 5 or 5,7")
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
    # A deck where the user kept several options of a slide (every option, or
    # "Picks: 1BC") stores every slide as a list and compiles as a labeled
    # all-options deck. A fix keeps that.
    all_options = bool((state.get("review") or {}).get("all_options")) or any(
        isinstance(v, list) for v in picks.values())

    to_convert: list[tuple[int, str]] = []
    for n in fixed:
        key = _p.slide_key(n)
        on_disk = _letters(out / key)
        prev = picks.get(key)
        kept = prev if isinstance(prev, list) else ([] if prev in (None, "-") else [prev])
        letters = list(named[n])
        if len(kept) > 1 and all(L in on_disk for L in kept):
            # The user kept several options of this slide and they are all
            # still there: rebuild the named ones only, keep the rest.
            if not letters:
                print(f"REFUSED: slide {n} keeps options {', '.join(kept)}. Say which were "
                      f"fixed, e.g. --slides {n}{kept[0]}; the others are kept as they are.")
                return 5
            stray = [L for L in letters if L not in kept]
            if stray:
                print(f"REFUSED: slide {n} keeps options {', '.join(kept)}, not "
                      f"{', '.join(stray)}. A fix rebuilds kept options only.")
                return 5
            to_convert += [(n, L) for L in letters]
            continue
        # One option on disk: the redesign (build_deck.py --slide N).
        if len(on_disk) != 1:
            print(f"REFUSED: slide {n} has {len(on_disk)} options ({', '.join(on_disk) or 'none'}) "
                  "that the user has not chosen between. A QC fix rebuilds the options "
                  "the user already kept; new alternatives are picked in REVIEW.html.")
            return 5
        if letters and letters != on_disk:
            print(f"REFUSED: slide {n} has only option {on_disk[0]}.")
            return 5
        picks[key] = list(on_disk) if all_options else on_disk[0]
        to_convert.append((n, on_disk[0]))
    for k, v in picks.items():
        for L in (v if isinstance(v, list) else [v]):
            if L != "-" and L not in _letters(out / k):
                print(f"REFUSED: {k} no longer has option {L}; pick in REVIEW.html.")
                return 5

    _state.record_review(out)                 # a review token for the current content
    _state.record_picks(out, picks, all_options=all_options, via="chat")
    picks_path.write_text(json.dumps(picks, indent=2), encoding="utf-8")
    what = ",".join(f"{n}{named[n]}" for n in fixed)
    _state.record_chat_approval(out, "qc_fix", args.approved.strip(),
                                {"slides": what, "after_compile_rev":
                                 int(((state.get("stages") or {}).get("compile") or {}).get("rev") or 0)})
    print(f"[ok] recorded the fix for slide(s) {what} as approved in chat; "
          + ("the slide's other kept options and " if any(named.values()) else "")
          + "other picks kept.")

    # Convert a redesigned sketch, only when its design changed since it was
    # last converted. Converting again rewrote the script from scratch: what
    # the translator agent drew was erased and the slide was pending again, so
    # this command looped on exit 3 for ever (2026-10-06). On a slide with
    # several kept options only the named ones are looked at.
    import translate_html
    pending = translate_html.convert_picked(out, to_convert)
    if pending:
        print("Part of the redesign needs the translator agent first (FALLBACK MODE):")
        for native in pending:
            print(f"  {native}")
        print("Run it, then run this command again (what it draws is kept).")
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
    flags = ["--all-variations", "--badge"] if all_options else []
    if meta.get("adopted_source"):
        flags += ["--splice-into", meta["adopted_source"]]
    rc = _run(HERE / "compile_picks.py", "--out", out, "--final-token", token, *flags)
    if rc == 0:
        print("\nNext: run slide-qc on the new deck (required), then check_done.py.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
