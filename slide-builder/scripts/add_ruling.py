#!/usr/bin/env python3
"""add_ruling.py: record one of the user's rulings, in their exact words.

The only way anything is written to the deck's `_session\\rulings.md`. The
quote must be found word for word in a message the user typed in this session
(the live Claude Code transcript); a paraphrase is refused. What the chat
understood goes on its own labeled line ("Chat's reading"), never into the
quote. A newer ruling on the same topic for the same slide replaces the older
one; both stay in the file, the older one struck out (owner's decision,
2026-10-14).

  py -3 scripts/add_ruling.py --out <deck folder> --id risks --topic "impact spacing" \\
      --quote "white spacing between high and impat" \\
      --reading "a visible gap between the High/Medium/Low labels and the risk rows"
  py -3 scripts/add_ruling.py --out <deck folder> --id deck --topic "source pages" --quote "..."
  py -3 scripts/add_ruling.py --out <deck folder> --list

--id is the slide's fixed id (`**Slide id:**` in the brief; slide_ids.py adds
them) or `deck` for a ruling on every slide. Before the build exists, pass
--brief instead of --out. Join separate pieces of one message with "...".
The slide's designer sees the ruling in its _context.md (refreshed here) and
answers it; REVIEW.html shows the answer beside the ruling.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _rulings  # noqa: E402


def _known_ids(brief: Path | None) -> dict[int, str]:
    if not brief or not brief.is_file():
        return {}
    import slide_ids
    return slide_ids.ids_in_brief(brief.read_text(encoding="utf-8").replace("\r\n", "\n"))


def _refresh_packs(out: Path | None, slide_id: str) -> list[Path]:
    if not out or not (out / "_meta.json").exists():
        return []
    import _context_pack
    import json
    try:
        meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
    except Exception:
        return []
    done = []
    for s in meta.get("slides") or []:
        if slide_id == _rulings.DECK_ID or s.get("slide_id") == slide_id:
            done += _context_pack.refresh(out, int(s["n"]))
    return done


def list_rulings(sd: Path) -> int:
    data = _rulings.load(sd)
    rs = data.get("rulings", [])
    if not rs:
        print("No rulings recorded yet.")
        return 0
    for r in rs:
        mark = f"  (replaced by R{r['replaced_by']})" if r.get("replaced_by") else ""
        print(f"R{r['n']} [{r['id']}] {r.get('topic', '')}: \"{r['quote']}\"{mark}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Record one of the user's rulings in their exact words.")
    ap.add_argument("--out", type=Path, help="The deck's build (session) folder.")
    ap.add_argument("--brief", type=Path, help="The brief, before the build folder exists.")
    ap.add_argument("--id", dest="slide_id", default="", help="The slide's fixed id, or 'deck'.")
    ap.add_argument("--topic", default="", help="A short topic; a newer ruling on the same "
                                                "topic for the same slide replaces the older.")
    ap.add_argument("--quote", default="", help="The user's words, exactly as typed.")
    ap.add_argument("--reading", default="", help="What the chat understood (its own line).")
    ap.add_argument("--replaces", type=int, action="append", default=[],
                    help="Also strike out ruling R<n> (the user reversed it on another topic).")
    ap.add_argument("--list", action="store_true", help="List the rulings and stop.")
    ap.add_argument("--transcript", default=None, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if not args.out and not args.brief:
        print("ERROR: give --out <deck folder> (or --brief <brief.md> before the build exists).")
        return 2
    sd = _rulings.session_dir(out=args.out, brief=args.brief)
    _rulings.announce(out=args.out, brief=args.brief)
    if args.list:
        return list_rulings(sd)
    sid = args.slide_id.strip().strip("`").lower()
    if not sid or not args.quote.strip() or not args.topic.strip():
        print("ERROR: --id, --topic and --quote are all needed (--reading is strongly "
              "recommended: say what you understood, on its own line).")
        return 2
    brief = args.brief or _rulings.find_brief(sd, args.out)
    ids = _known_ids(brief)
    if sid != _rulings.DECK_ID and sid not in ids.values():
        if not ids:
            print(f"REFUSED: the brief has no slide ids yet ({brief or 'no brief found'}). "
                  "Record this one with --id deck (say which slide in --reading), or add the "
                  f"ids first: py -3 scripts/slide_ids.py --brief \"{brief or '<brief.md>'}\"")
        else:
            print(f"REFUSED: no slide has the id {sid!r}. The ids are: "
                  + ", ".join(f"{v} (slide {k})" for k, v in sorted(ids.items()))
                  + ", or deck.")
        return 3
    if _rulings.quote_too_short(args.quote):
        print("REFUSED: the quote is too short to check. Give at least two of the user's "
              "words, exactly as they typed them.")
        return 3
    ok, why, where = _rulings.check_users_words(args.quote, args.transcript)
    if not ok:
        print(f"REFUSED: {why}")
        print("Nothing was recorded. Find the user's message, copy the words as they are, "
              "and put your own understanding in --reading.")
        return 4
    data = _rulings.load(sd)
    earlier_same = [r for r in data["rulings"] if r["id"] == sid
                    and _rulings.norm_topic(r.get("topic", "")) == _rulings.norm_topic(args.topic)]
    entry, replaced = _rulings.add(sd, sid, args.quote, args.reading, args.topic, where,
                                   args.replaces)
    label = "the whole deck" if sid == _rulings.DECK_ID else (
        f"slide {next((k for k, v in ids.items() if v == sid), '?')} ({sid})")
    print(f"[ok] R{entry['n']} recorded for {label}, topic \"{entry['topic']}\": "
          f"\"{entry['quote']}\"")
    print(f"     found word for word in {Path(where[0]).name}, line {where[1]}")
    for r in replaced:
        print(f"     replaces R{r['n']}: \"{r['quote']}\" (kept in the file, struck out)")
    changed = _refresh_packs(args.out, sid)
    if changed:
        print(f"     refreshed the rulings pack in {len(changed)} designer file(s); a design "
              "made before this ruling shows it red on REVIEW.html until it is redone.")
    if earlier_same:
        olds = ", ".join(f"R{r['n']}" for r in earlier_same)
        print("")
        print(f"REPEAT: the user has now given a ruling on \"{entry['topic']}\" for {label} "
              f"before ({olds}). If it is the same point said again, it should become an "
              "automatic check so nobody has to say it a third time. Propose one to the user "
              "(they approve the change; nothing is turned on before they do):")
        print(f"  py -3 scripts/steer_checks.py propose --out \"{args.out or '<deck folder>'}\" "
              f"--kind <kind> --because R{entry['n']},{olds.replace(' ', '')} ...")
        print("  py -3 scripts/steer_checks.py kinds   (lists the checks that exist; a new "
              "kind is a code change the user approves first)")
        print("  If the user changed their mind instead, nothing more to do: the newest "
              "ruling is the one in force.")
    print(f"Rulings file: {_rulings.rulings_md(sd)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
