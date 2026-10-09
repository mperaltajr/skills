#!/usr/bin/env python3
"""apply_qc_fix.py — finish a QC fix straight to the deck: one the user approved
in chat, or an automatic one (owner's decisions, 2026-10-02 and 2026-10-09).

After a deck is compiled, slide-qc lists what is wrong. The slides get rebuilt
(build_deck.py --slide N with the QC finding in _prior_feedback.md, one option
each). Sending the user back through REVIEW.html and FINAL-CHECK.html for a fix
was pure friction, so this records the fix and compiles:

  py -3 scripts/apply_qc_fix.py --out <out_dir> --slides 5[,7] --approved "<the user's words>"

Automatic fixes (2026-10-09). Criticals and layout/format Majors are fixed
WITHOUT asking (qc_fix_policy.py says which), at most two rounds, then one
message to the user. Before rebuilding a slide, keep its current design:

  py -3 scripts/apply_qc_fix.py --out <out_dir> --slides 5,7 --snapshot

then rebuild the slides as usual, then

  py -3 scripts/apply_qc_fix.py --out <out_dir> --slides 5,7 --auto "slide 5 [overflow] Critical: ...; slide 7 [text_size] Major: ..."

It refuses a finding qc_fix_policy.py classes "ask" (content: the user decides),
a third automatic round, and a slide with no snapshot. Each automatic fix is
recorded with its finding text; check_done.py lists it at delivery as "fixed
automatically" and prints the before/after pictures. The user can then say
"undo slide N":

  py -3 scripts/apply_qc_fix.py --out <out_dir> --undo 5 --approved "<the user's words>"

restores slide 5's design from before its automatic fix and compiles the deck
again (every other slide as it is now).

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
     fixed slides, recording the user's words (a chat approval) or the
     finding (an automatic fix);
  3. converts a redesigned sketch with translate_html.py when its design
     changed since it was last converted (stops if part of it needs the
     translator agent; run the agent, then this again: a slide the agent
     finished is not converted again, so its drawing is kept);
  4. finalizes the fixed slides, writes the final-check record over the
     finished files (FINAL-CHECK.html is still written, as the record), and
     compiles.
Then run slide-qc on the new deck, as after any compile.

Exit: 0 compiled (or snapshot kept) | 3 translator agent needed first | 5 refused | 2 bad usage
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import _paths as _p  # noqa: E402
import _state  # noqa: E402
import qc_fix_policy  # noqa: E402

SNAP_DIR = "_autofix_prev"


def _letters(slide_dir: Path) -> list[str]:
    found = set()
    for p in slide_dir.glob("option_*"):
        m = re.match(r"option_([A-F])(?:[._])", p.name)
        if m and p.is_file():
            found.add(m.group(1))
    return sorted(found)


def _run(*args) -> int:
    return subprocess.run([sys.executable, *map(str, args)]).returncode


def _parse_slides(spec: str) -> dict[int, str] | None:
    named: dict[int, str] = {}
    for tok in (spec or "").split(","):
        tok = tok.strip()
        if not tok:
            continue
        m = re.fullmatch(r"(\d{1,3})([A-Fa-f]*)", tok)
        if not m:
            return None
        n = int(m.group(1))
        named[n] = "".join(sorted(set(named.get(n, "") + m.group(2).upper())))
    return named or None


def _load_picks(out: Path):
    try:
        return json.loads((out / "picks.json").read_text(encoding="utf-8"))
    except Exception:
        return None


def snapshot(out: Path, slides: list[int]) -> int:
    """Keep each slide's current design (every option_* file) and the deck,
    so an automatic fix can be undone."""
    state = _state.read_state(out)
    comp = (state.get("stages") or {}).get("compile") or {}
    if not comp:
        print("REFUSED: no deck has been compiled from this build yet.")
        return 5
    picks = _load_picks(out) or {}
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    snaps = dict((state.get("auto_qc") or {}).get("snapshots") or {})
    for n in slides:
        sid = _p.slide_key(n)
        dest = out / sid / SNAP_DIR / stamp
        dest.mkdir(parents=True, exist_ok=True)
        for f in (out / sid).glob("option_*"):
            if f.is_file():
                shutil.copy2(f, dest / f.name)
        snaps[sid] = {"dir": str(dest), "pick": picks.get(sid), "at": stamp}
        print(f"[ok] kept slide {n}'s current design: {dest}")
    deck = Path(comp.get("output") or "")
    if deck.exists():
        keep = out / SNAP_DIR / f"deck_before_{stamp}{deck.suffix}"
        keep.parent.mkdir(exist_ok=True)
        shutil.copy2(deck, keep)
        print(f"[ok] kept the deck from before the fix: {keep}")
    state = _state.read_state(out)
    aq = state.get("auto_qc") or {}
    aq["snapshots"] = snaps
    state["auto_qc"] = aq
    _state._write(out, state)
    return 0


def _restore(out: Path, sid: str, snap_dir: Path) -> None:
    """Put a kept design back; what is there now is moved aside, not deleted."""
    sd = out / sid
    aside = sd / SNAP_DIR / (datetime.now().strftime("%Y%m%dT%H%M%S") + "_undone")
    aside.mkdir(parents=True, exist_ok=True)
    for f in sd.glob("option_*"):
        if f.is_file():
            shutil.move(str(f), str(aside / f.name))
    for f in snap_dir.glob("option_*"):
        shutil.copy2(f, sd / f.name)


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Compile a QC fix: approved in chat, or automatic.")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--slides", default="",
                    help="Comma-separated slides that were fixed: 5 or 5,7; on a slide "
                         "that keeps several options, the fixed letters too: 1B or 1BC,3.")
    ap.add_argument("--approved", default=None,
                    help="The user's own words approving the fix (or asking for the undo), "
                         "recorded verbatim.")
    ap.add_argument("--auto", default=None,
                    help="An automatic fix: the findings it fixes, e.g. \"slide 5 [overflow] "
                         "Critical: text cut off\". Refused for content findings.")
    ap.add_argument("--snapshot", action="store_true",
                    help="Before rebuilding for an automatic fix: keep the slides' current design.")
    ap.add_argument("--undo", type=int, default=None,
                    help="Restore slide N's design from before its automatic fix, and compile.")
    args = ap.parse_args(argv)
    out = args.out

    modes = sum(bool(x) for x in (args.auto is not None, args.snapshot, args.undo is not None))
    if modes > 1:
        print("ERROR: use one of --auto, --snapshot or --undo.")
        return 2
    named: dict[int, str] = {}
    if args.undo is None:
        named = _parse_slides(args.slides)
        if not named:
            print("ERROR: --slides takes slide numbers, e.g. 5 or 5,7, or a slide "
                  "and its fixed options, e.g. 1B or 1BC,3")
            return 2
    if args.snapshot:
        return snapshot(out, sorted(named))
    if args.auto is None and not (args.approved or "").strip():
        print("REFUSED: --approved needs the user's words approving the fix "
              "(or use --auto for an automatic fix).")
        return 5
    if args.auto is not None and args.approved:
        print("ERROR: --auto is a fix without the user's approval; do not pass --approved.")
        return 2

    state = _state.read_state(out)
    if not (state.get("stages") or {}).get("compile"):
        print("REFUSED: no deck has been compiled from this build yet. A first build "
              "goes through REVIEW.html and FINAL-CHECK.html; this command is only for "
              "fixes after the quality check.")
        return 5
    picks = _load_picks(out)
    if not isinstance(picks, dict):
        print("REFUSED: no earlier picks.json to keep the other slides' picks from.")
        return 5

    snaps = (state.get("auto_qc") or {}).get("snapshots") or {}
    if args.undo is not None:
        return undo(out, args.undo, args.approved, state, picks)

    auto_findings = ""
    if args.auto is not None:
        rows = qc_fix_policy.classify(args.auto)
        if not rows:
            print("REFUSED: --auto needs the findings it fixes, e.g. "
                  "\"slide 5 [overflow] Critical: text cut off\".")
            return 5
        asked = [r for r in rows if r["decision"] != "auto"]
        if asked:
            print("REFUSED: these are not automatic fixes (qc_fix_policy.py); the user "
                  "decides them, in one table with proposed fixes:")
            for r in asked:
                print(f"  - [{r['category'] or 'unrecognized'}] {r['finding']}")
            return 5
        if _state.auto_qc_rounds(state) >= _state.AUTO_QC_MAX_ROUNDS:
            print(f"REFUSED: {_state.AUTO_QC_MAX_ROUNDS} automatic rounds are done. Do not "
                  "start another: send the user ONE message with what was fixed per slide "
                  "(before/after pictures), the content findings table, and what is still open.")
            return 5
        missing = [n for n in named if _p.slide_key(n) not in snaps]
        if missing:
            print(f"REFUSED: no design kept from before the fix for slide(s) "
                  f"{', '.join(map(str, missing))}, so it could not be undone. Run "
                  "apply_qc_fix.py --snapshot --slides ... BEFORE rebuilding them.")
            return 5
        auto_findings = "; ".join(r["finding"] for r in rows)

    # A deck where the user kept several options of a slide (every option, or
    # "Picks: 1BC") stores every slide as a list and compiles as a labeled
    # all-options deck. A fix keeps that.
    all_options = bool((state.get("review") or {}).get("all_options")) or any(
        isinstance(v, list) for v in picks.values())
    fixed = sorted(named)
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
    _state.record_picks(out, picks, all_options=all_options,
                        via="auto" if args.auto is not None else "chat")
    (out / "picks.json").write_text(json.dumps(picks, indent=2), encoding="utf-8")
    what = ",".join(f"{n}{named[n]}" for n in fixed)
    if args.auto is not None:
        entry = _state.record_auto_fix(
            out, what, auto_findings,
            {_p.slide_key(n): snaps[_p.slide_key(n)] for n in fixed})
        print(f"[ok] automatic fix, round {entry['round']} of at most "
              f"{_state.AUTO_QC_MAX_ROUNDS}, slide(s) {what}: recorded with its findings.")
    else:
        _state.record_chat_approval(out, "qc_fix", args.approved.strip(),
                                    {"slides": what, "after_compile_rev":
                                     int(((state.get("stages") or {}).get("compile") or {}).get("rev") or 0)})
        _state.reset_auto_qc_rounds(out)      # the user replied: a new QC cycle
        print(f"[ok] recorded the fix for slide(s) {what} as approved in chat; "
              + ("the slide's other kept options and " if any(named.values()) else "")
              + "other picks kept.")
    rc = _convert_finalize_compile(out, fixed, to_convert, all_options)
    if rc == 0 and args.auto is not None:
        for n in fixed:
            sid = _p.slide_key(n)
            snap = Path(snaps[sid]["dir"])
            for L in sorted({L for m, L in to_convert if m == n}):
                print(f"  slide {n} option {L}: before {snap / _p.option_png_name(L)}")
                print(f"  slide {n} option {L}: after  {out / sid / _p.option_png_name(L)}")
    return rc


def undo(out: Path, n: int, words, state: dict, picks: dict) -> int:
    sid = _p.slide_key(n)
    if not (words or "").strip():
        print("REFUSED: --undo needs --approved with the user's words (\"undo slide N\").")
        return 5
    entry = next((e for e in reversed(state.get("auto_fixes") or [])
                  if sid in (e.get("before") or {})
                  and sid not in (e.get("undone_slides") or [])), None)
    if not entry:
        print(f"REFUSED: slide {n} has no automatic fix to undo.")
        return 5
    before = entry["before"][sid]
    snap = Path(before["dir"])
    if not snap.is_dir() or not any(snap.glob("option_*")):
        print(f"REFUSED: the design kept from before the fix is gone ({snap}).")
        return 5
    _restore(out, sid, snap)
    if before.get("pick") is not None:
        picks[sid] = before["pick"]
    all_options = bool((state.get("review") or {}).get("all_options")) or any(
        isinstance(v, list) for v in picks.values())
    _state.record_review(out)
    _state.record_picks(out, picks, all_options=all_options, via="chat")
    (out / "picks.json").write_text(json.dumps(picks, indent=2), encoding="utf-8")
    _state.mark_auto_fix_undone(out, n)
    _state.record_chat_approval(out, "qc_undo", words.strip(), {"slide": sid})
    print(f"[ok] slide {n}: the design from before its automatic fix is back "
          f"(from {snap}); the fixed one was moved aside.")
    v = picks.get(sid)
    letters = v if isinstance(v, list) else ([] if v in (None, "-") else [v])
    return _convert_finalize_compile(out, [n], [(n, L) for L in letters], all_options)


def _convert_finalize_compile(out: Path, fixed: list[int], to_convert, all_options: bool) -> int:
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
