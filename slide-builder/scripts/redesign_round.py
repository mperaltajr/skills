#!/usr/bin/env python3
"""redesign_round.py — a "Replace these" round with one new design per slide
goes straight to the final check (owner's decision, 2026-10-05).

Picking the only option on a second review page added nothing, so:

  1. Before redesigning, record the picks the user kept (the review page puts
     them in its message as "Keep: 1B 3A ... (check 1a2b3c4d)"):
       py -3 scripts/redesign_round.py start --out <out> --slides 2,5 --kept "<Keep line>"
     (omit --kept when no slide was picked yet)
  2. Redesign each slide as usual (build_deck.py --slide N, one worker each,
     render the sketch).
  3. Finish:
       py -3 scripts/redesign_round.py finish --out <out>
     It picks each slide's single new design, keeps the recorded picks,
     converts and finalizes, writes FINAL-CHECK.html and opens it. The user's
     look at the finished slides there is still required before anything is
     built.

finish refuses when a redesigned slide has more than one option (the user
asked for alternatives: build REVIEW.html and let them pick) or when any slide
would be left without a pick.
Exit: 0 ok | 3 translator agent needed first | 5 refused | 2 bad usage
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

KEEP_RE = re.compile(r"Keep:\s*(.+?)\s*\(check\s+([0-9a-fA-F]{8})\)", re.I)


def _letters(slide_dir: Path) -> list[str]:
    found = set()
    for p in slide_dir.glob("option_*"):
        m = re.match(r"option_([A-F])(?:[._])", p.name)
        if m and p.is_file():
            found.add(m.group(1))
    return sorted(found)


def _parse_keep(line: str):
    m = KEEP_RE.search(line or "")
    if not m:
        return None, None
    picks = {}
    for tok in m.group(1).replace(",", " ").split():
        mm = re.fullmatch(r"(\d{1,3})([A-Fa-f]|-)", tok)
        if not mm:
            return None, None
        picks[_p.slide_key(int(mm.group(1)))] = mm.group(2).upper()
    return picks, m.group(2).lower()


def start(out: Path, slides: list[int], kept_line: str) -> int:
    state = _state.read_state(out)
    kept: dict = {}
    if kept_line.strip():
        kept, check = _parse_keep(kept_line)
        if kept is None:
            print('REFUSED: the Keep line looks like "Keep: 1B 3A (check 1a2b3c4d)".')
            return 5
        token = (state.get("review") or {}).get("token")
        if not token or _state.approval_check(token, _state.canonical_picks(kept)) != check:
            print("REFUSED: the kept picks do not match their check code (changed after "
                  "the user clicked, or copied from another review page).")
            return 5
    state["redesign_round"] = {"slides": sorted(slides), "kept": kept}
    _state._write(out, state)
    print(f"[ok] kept {len(kept)} pick(s); redesigning slide(s) "
          f"{', '.join(map(str, sorted(slides)))}. Rebuild them, then run finish.")
    return 0


def finish(out: Path) -> int:
    state = _state.read_state(out)
    rr = state.get("redesign_round") or {}
    if not rr.get("slides"):
        print("REFUSED: no redesign round recorded; run start first.")
        return 5
    picks = dict(rr.get("kept") or {})
    for n in rr["slides"]:
        letters = _letters(out / _p.slide_key(n))
        if len(letters) != 1:
            print(f"REFUSED: slide {n} has {len(letters)} options. With alternatives "
                  "the user picks: run build_review.py --open.")
            return 5
        picks[_p.slide_key(n)] = letters[0]
    meta = json.loads(_p.meta_json(out).read_text(encoding="utf-8"))
    every = [_p.slide_key(int(s["n"])) for s in meta.get("slides", []) if isinstance(s.get("n"), int)]
    missing = [k for k in every if k not in picks]
    if missing:
        print(f"REFUSED: no pick for {', '.join(missing)}. Build REVIEW.html so the user "
              "can decide them.")
        return 5
    _state.record_review(out)
    _state.record_picks(out, picks)
    (out / "picks.json").write_text(json.dumps(picks, indent=2), encoding="utf-8")
    _state.record_override(out, "single_option_redesign_picked",
                           f"slides {','.join(map(str, rr['slides']))}: one new design each, "
                           "picked without a second review page; the final check still shown")
    jobs = []
    import translate_html
    for n in rr["slides"]:
        k = _p.slide_key(n)
        html = out / k / f"option_{picks[k]}.html"
        if html.exists():
            jobs.append((html, out / k, picks[k], translate_html._subtitle_as_shape(out, n)))
    if jobs:
        pending = [r for r in translate_html.translate_many(jobs) if r["needs_agent"]]
        if pending:
            print("Part of a redesign needs the translator agent first (FALLBACK MODE):")
            for r in pending:
                h = Path(r["html"])
                print(f"  {h.with_name(h.stem + '_native.py')}")
            print("Run it, then run finish again.")
            return 3
    tpl = meta.get("template")
    for n in rr["slides"]:
        rc = subprocess.run([sys.executable, str(HERE / "finalize_deck.py"), "--out", str(out),
                             "--template", str(tpl), "--slide", str(n)]).returncode
        if rc != 0:
            print(f"finalize_deck.py --slide {n} exited {rc}.")
            return rc
    rc = subprocess.run([sys.executable, str(HERE / "build_review.py"), "--out", str(out),
                         "--final", "--open"]).returncode
    if rc == 0:
        state = _state.read_state(out)
        state.pop("redesign_round", None)
        _state._write(out, state)
        print("Show the user FINAL-CHECK.html (now open) and wait for its Build it message.")
    return rc


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--out", required=True, type=Path)
    s.add_argument("--slides", required=True)
    s.add_argument("--kept", default="")
    f = sub.add_parser("finish")
    f.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "start":
        try:
            slides = [int(x) for x in a.slides.split(",") if x.strip()]
        except ValueError:
            print("ERROR: --slides takes numbers, e.g. 2,5")
            return 2
        return start(a.out, slides, a.kept)
    return finish(a.out)


if __name__ == "__main__":
    sys.exit(main())
