#!/usr/bin/env python3
"""build_status.py: where a deck's build stands and the one next step.

The chat used to spend many turns opening files to work out what stage a build
was at (79 turns on one deck). This reads the build's own records and prints a
short status and the exact next command (Q2 decision, 2026-10-14). It changes
nothing.

  py -3 scripts/build_status.py --out <deck folder>
  py -3 scripts/build_status.py --brief <brief.md>     (before the build exists)
  add --measure to count the user's messages that repeat an earlier steer
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _rulings  # noqa: E402


def _read(p: Path) -> dict:
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return {}


def storyline_status(brief: Path | None, sd: Path) -> tuple[list[str], str]:
    lines, nxt = [], ""
    if not brief or not brief.is_file():
        return ["Brief: none found"], "Write the storyline with storyline-helper."
    import build_deck
    import slide_ids
    text = brief.read_text(encoding="utf-8")
    fm, _body = build_deck.extract_front_matter(text.replace("\r\n", "\n").lstrip("﻿"))
    sealed = bool((fm.get("storyline_gate_sha") or "").strip())
    lines.append(f"Brief: {brief}" + (" (sealed)" if sealed else " (NOT sealed)"))
    ids = slide_ids.ids_in_brief(text.replace("\r\n", "\n"))
    n = len(slide_ids.blocks(text.replace("\r\n", "\n")))
    lines.append(f"Brief slides: {n}; slide ids on {len(ids)} of them")
    pm = _read(sd / "page_map.json")
    if pm:
        lines.append("Page map: " + ("approved" if pm.get("approved") else
                                     "proposed, NOT approved (map_source_pages.py show)"))
    if not sealed:
        nxt = "Run storyline-helper's quality gate, then seal_brief.py and emit_dot_dash.py."
    elif len(ids) < n:
        nxt = f"Add the slide ids: py -3 scripts/slide_ids.py --brief \"{brief}\""
    elif pm and not pm.get("approved"):
        nxt = "Show the user the page map list (map_source_pages.py show), wait for their answer, then map_source_pages.py approve."
    return lines, nxt


def build_status(out: Path) -> tuple[list[str], str]:
    import _state
    meta = _read(out / "_meta.json")
    state = _state.read_state(out)
    slides = meta.get("slides") or []
    lines, nxt = [], ""
    tpl = meta.get("template") or "<template>"
    with_designs = rendered = 0
    waiting_sketch = []
    for s in slides:
        sdir = out / f"slide_{int(s['n']):02d}"
        letters = s.get("options") or ["A"]
        has = [L for L in letters if (sdir / f"option_{L}.html").exists()
               or (sdir / f"option_{L}.py").exists()]
        if has:
            with_designs += 1
        sk = [L for L in has if (sdir / f"option_{L}.html").exists()]
        if sk and all((sdir / f"option_{L}.sketch.png").exists() for L in sk):
            rendered += 1
        elif sk:
            waiting_sketch.append(int(s["n"]))
    lines.append(f"Slides: {len(slides)}; designs on disk for {with_designs}")
    review = state.get("review") or {}
    stages = state.get("stages") or {}
    picks = review.get("picks")
    pending = _state.pending_comments(state)
    fin = state.get("finalize") or {}
    comp = stages.get("compile") or {}
    prep_rev = (stages.get("prep") or {}).get("rev") or 0
    compiled_now = bool(comp) and (comp.get("rev") or 0) > prep_rev \
        and comp.get("content_hash") == state.get("content_hash")
    if fin:
        lines.append(f"Finalize: {fin.get('status', '?')}"
                     + (f" ({fin.get('reason')})" if fin.get("reason") else ""))
    if picks:
        n_pick = sum(1 for v in picks.values() if v != "-")
        lines.append(f"Picks: recorded for {len(picks)} slide(s) ({n_pick} in the deck), "
                     f"via {review.get('approved_via', 'page')}")
    if pending:
        lines.append(f"Comments waiting: {len(pending)} ("
                     + ", ".join(sorted({c['slide'] for c in pending})) + ")")
    if state.get("redesign_round"):
        lines.append("Redesign round open for slide(s) "
                     + ",".join(str(x) for x in state["redesign_round"].get("slides", [])))
    if state.get("final_check"):
        lines.append("Final check page: built" + (" and the deck compiled" if compiled_now else
                                                  ", waiting for the user's Build it"))
    if compiled_now:
        lines.append(f"Deck: {comp.get('output')}")
    vp = state.get("vision_pages") or {}
    if compiled_now:
        lines.append("QC: " + (f"{len(vp)} page(s) reviewed" if vp else "not run yet"))
    # The next step, first unmet condition wins.
    if with_designs < len(slides):
        missing = [int(s["n"]) for s in slides
                   if not any((out / f"slide_{int(s['n']):02d}" / f"option_{L}.{e}").exists()
                              for L in (s.get("options") or ["A"]) for e in ("html", "py"))]
        nxt = (f"Dispatch the designers for slide(s) {','.join(map(str, missing))} "
               f"(dispatch_plan.md: {out / 'dispatch_plan.md'}).")
    elif waiting_sketch:
        nxt = ("Render the sketches of slide(s) " + ",".join(map(str, waiting_sketch))
               + " (render_html.py), then finalize_deck.py and build_review.py --open.")
    elif not review.get("token"):
        nxt = (f"py -3 scripts/finalize_deck.py --out \"{out}\" --template \"{tpl}\", then "
               f"py -3 scripts/build_review.py --out \"{out}\" --open, and wait for the picks.")
    elif not picks:
        nxt = "REVIEW.html is open: wait for the user's picks message, then record_picks.py."
    elif pending:
        nxt = ("Apply the waiting comments (the EDIT MODE workers on slide_NN/_edit_request.md, "
               f"then py -3 scripts/record_picks.py --out \"{out}\" --edits-done).")
    elif state.get("redesign_round"):
        nxt = f"Finish the redesign: py -3 scripts/redesign_round.py finish --out \"{out}\""
    elif not state.get("final_check"):
        nxt = (f"py -3 scripts/finalize_deck.py --out \"{out}\" --template \"{tpl}\", then "
               f"py -3 scripts/build_review.py --out \"{out}\" --final --open.")
    elif not compiled_now:
        nxt = "FINAL-CHECK.html is open: wait for the user's Build it message, then compile_picks.py."
    elif not vp:
        nxt = "Run slide-qc on the compiled deck (Skill slide-qc with the deck path)."
    else:
        nxt = f"py -3 scripts/check_done.py --out \"{out}\""
    return lines, nxt


def rulings_lines(sd: Path, out: Path | None) -> list[str]:
    data = _rulings.load(sd)
    rs = data.get("rulings", [])
    act = _rulings.active(data)
    lines = [f"Rulings: {len(act)} in force, {len(rs) - len(act)} replaced "
             f"({_rulings.rulings_md(sd)})"]
    seen, repeats = {}, 0
    for r in rs:
        k = (r["id"], _rulings.norm_topic(r.get("topic", "")))
        repeats += 1 if k in seen else 0
        seen[k] = 1
    if repeats:
        lines.append(f"Repeated rulings (same slide and topic given again): {repeats}")
    if out and (out / "_meta.json").exists():
        try:
            import _context_pack
            red = 0
            for s in _read(out / "_meta.json").get("slides") or []:
                red += sum(1 for row in _context_pack.receipt(out, int(s["n"])) if not row["ok"])
            if red:
                lines.append(f"Rulings not answered by a designer (red on REVIEW.html): {red}")
        except Exception:
            pass
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Where a deck's build stands and the next step.")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--brief", type=Path)
    ap.add_argument("--measure", action="store_true",
                    help="Also count the user's messages that repeat an earlier steer.")
    a = ap.parse_args(argv)
    if not a.out and not a.brief:
        print("ERROR: give --out <deck folder> or --brief <brief.md>.")
        return 2
    sd = _rulings.session_dir(out=a.out, brief=a.brief)
    _rulings.announce(out=a.out, brief=a.brief)
    brief = a.brief or _rulings.find_brief(sd, a.out)
    lines, nxt = storyline_status(brief, sd)
    if a.out and (a.out / "_meta.json").exists():
        b_lines, b_next = build_status(a.out)
        lines += b_lines
        if nxt:
            lines.append(f"Also: {nxt}")
        nxt = b_next
        stage = "build"
    else:
        stage = "storyline"
        if not nxt:
            nxt = "Build: build_deck.py --brief <brief> --template <template> --out <deck folder>."
    lines += rulings_lines(sd, a.out)
    if a.measure:
        lines += measure_lines()
    print(f"STATUS ({stage} stage)")
    for ln in lines:
        print(f"  {ln}")
    print(f"NEXT: {nxt}")
    return 0


# How the context design is measured on the next deck (ctx verdict): the
# user's messages that say they are repeating themselves. Baseline on the two
# 10/12-10/13 decks: 33 repeats in about 150 feedback lines.
REPEAT_PHRASES = ("i said", "i told you", "we had", "literally", "again", "i already")


def measure_lines() -> list[str]:
    files = _rulings.transcript_files()
    if not files:
        return ["Measure: no session transcript found"]
    n_msgs = hits = 0
    for _ln, text in _rulings.user_messages(files[0]):
        n_msgs += 1
        t = " ".join(text.lower().split())
        if any(p in t for p in REPEAT_PHRASES):
            hits += 1
    return [f"Measure ({files[0].name}): {hits} of {n_msgs} message(s) from the user say they "
            "are repeating themselves (\"I said\", \"I told you\", \"we had\", \"literally\", "
            "\"again\"). Target: under 5 per deck."]


if __name__ == "__main__":
    sys.exit(main())
