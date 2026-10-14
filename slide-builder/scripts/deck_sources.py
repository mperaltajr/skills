#!/usr/bin/env python3
"""deck_sources.py: the deck's sources and number trail, for every designer.

Kept in `_session\\sources.json` and shown in each slide's context pack:

  - Sources: a file, what it is, which slides use it, and whether the user
    said it is already validated. A validated source's numbers are not
    checked again: the copied-page check (source_ledger.py) counts them
    instead of asking about each one, and source_check.py lists them as
    from a validated source. Marking a source validated needs the user's
    own words (checked against the session transcript): on 10/13 agents spent
    hours re-checking numbers of a deck the user had validated already.
  - Number trail: where a figure comes from ("120%: model tab 30_Revenue,
    cell F12"), so a designer never guesses and the user is not asked twice.

  py -3 scripts/deck_sources.py add --out <deck> --name "Investor deck v2" \\
        --path "<file>" [--slides risks,leaders | all] [--validated \\
        --approved-in-chat "<the user's words>"]
  py -3 scripts/deck_sources.py trail --out <deck> --figure "120%" \\
        --where "financial model, 30_Revenue F12" [--slides p38-revenue | all]
  py -3 scripts/deck_sources.py list --out <deck>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _rulings  # noqa: E402
import _context_pack  # noqa: E402


def _path(sd: Path) -> Path:
    return Path(sd) / _context_pack.SOURCES_JSON


def save(sd: Path, data: dict) -> None:
    Path(sd).mkdir(parents=True, exist_ok=True)
    _path(sd).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _slides(v: str) -> list[str]:
    ids = [x.strip().lower() for x in (v or "all").split(",") if x.strip()]
    return ids or ["all"]


def validated_sources(sd: Path) -> list[dict]:
    return [s for s in _context_pack.load_sources(sd).get("sources") or [] if s.get("validated")]


def is_validated(sd: Path, file_path) -> dict | None:
    """The validated source entry for this file (same file, or same name and
    size when the path differs), else None."""
    try:
        fp = Path(file_path).resolve()
    except Exception:
        return None
    for s in validated_sources(sd):
        try:
            sp = Path(s.get("path") or "")
            if sp.resolve() == fp:
                return s
            if sp.name.lower() == fp.name.lower() and sp.exists() and fp.exists() \
                    and sp.stat().st_size == fp.stat().st_size:
                return s
        except Exception:
            continue
    return None


def _refresh_all(out: Path) -> int:
    meta_p = Path(out) / "_meta.json"
    if not meta_p.exists():
        return 0
    try:
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
    except Exception:
        return 0
    n = 0
    for s in meta.get("slides") or []:
        n += len(_context_pack.refresh(out, int(s["n"])))
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="The deck's sources and number trail.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--name", required=True)
    p.add_argument("--path", required=True)
    p.add_argument("--what", default="")
    p.add_argument("--slides", default="all")
    p.add_argument("--validated", action="store_true")
    p.add_argument("--approved-in-chat", dest="approved_in_chat", default="")
    p.add_argument("--transcript", default=None, help=argparse.SUPPRESS)
    p = sub.add_parser("trail")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--figure", required=True)
    p.add_argument("--where", required=True)
    p.add_argument("--slides", default="all")
    p = sub.add_parser("list")
    p.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    _rulings.announce(out=a.out)
    sd = _rulings.session_dir(out=a.out)
    data = _context_pack.load_sources(sd)
    data.setdefault("sources", [])
    data.setdefault("trail", [])
    now = datetime.now().isoformat(timespec="seconds")
    if a.cmd == "list":
        for s in data["sources"]:
            st = "validated" if s.get("validated") else "not validated"
            print(f"  {s['name']}: {s['path']} [{st}] slides: {', '.join(s['slides'])}")
        for t in data["trail"]:
            print(f"  {t['figure']}: {t['where']} (slides: {', '.join(t['slides'])})")
        if not data["sources"] and not data["trail"]:
            print("No sources or number trail recorded yet.")
        return 0
    if a.cmd == "add":
        entry = {"name": a.name.strip(), "path": a.path.strip().strip('"'), "what": a.what.strip(),
                 "slides": _slides(a.slides), "validated": False, "at": now}
        if a.validated:
            ok, why, where = _rulings.check_users_words(a.approved_in_chat, a.transcript)
            if not ok:
                print(f"REFUSED: a source is marked validated only in the user's own words. {why}")
                return 4
            entry.update(validated=True, words=a.approved_in_chat.strip(),
                         where=f"{Path(where[0]).name}:{where[1]}")
        data["sources"] = [s for s in data["sources"] if s["name"] != entry["name"]] + [entry]
        save(sd, data)
        st = "validated: its numbers are not checked again" if entry["validated"] else "not validated"
        print(f"[ok] source \"{entry['name']}\" recorded ({st}).")
    else:
        entry = {"figure": a.figure.strip(), "where": a.where.strip(),
                 "slides": _slides(a.slides), "at": now}
        data["trail"] = [t for t in data["trail"]
                         if not (t["figure"] == entry["figure"] and t["slides"] == entry["slides"])]
        data["trail"].append(entry)
        save(sd, data)
        print(f"[ok] number trail: {entry['figure']} -> {entry['where']}")
    n = _refresh_all(a.out)
    if n:
        print(f"     refreshed the context pack in {n} designer file(s).")
    print(f"Sources file: {_path(sd)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
