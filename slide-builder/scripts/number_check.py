#!/usr/bin/env python3
"""number_check.py: tag every finding of a number-check round with whether
its page changed since round 1, so the second round can be measured.

The number check (the fact-checker agents that compare every figure on the
finished deck with the brief and its sources) runs twice on a big deck. The
second round covers every page today. The owner's decision (2026-10-14,
speed verdict Q2, decision D): keep round 2 on every page, and on the next
two decks tag each round-2 finding with whether its page changed since round
1. If no finding ever lands on an unchanged page, round 2 can move to the
changed pages only (about 10-15M tokens saved per deck); that switch is the
owner's call, not this script's.

  start   before a round's checkers start: keeps each page's text fingerprint
          (and its picture's fingerprint when the deck was rendered) for the
          deck as it is now, in <build>/_qc/number_check/round_N.json.
  record  after the round: reads the round's findings (a JSON list of
          {"page": N, "issue": "..."} or lines "slide N: ..."), tags each one
          with "page_changed_since_round_1" (true / false) and writes
          findings_round_N.json; prints the tally.
  tally   prints every recorded round's tally (the measurement).

A page counts as unchanged when round 1 had a page with exactly the same
text (page numbers ignored, so an inserted page does not make every later
page look changed). Its picture is compared too and reported separately: a
page whose text is the same but whose picture changed is "same text, new
picture".

Run:
  py -3 scripts/number_check.py start  --out <build> --round 1
  py -3 scripts/number_check.py record --out <build> --round 1 --findings <file>
  py -3 scripts/number_check.py start  --out <build> --round 2
  py -3 scripts/number_check.py record --out <build> --round 2 --findings <file>
  py -3 scripts/number_check.py tally  --out <build>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "slide-qc" / "scripts"))
import _state  # noqa: E402
import qc_pages  # noqa: E402

DIR = "number_check"


def _dir(out) -> Path:
    return qc_pages.qc_dir(out) / DIR


def _text_fp(text: str) -> str:
    lines = [ln for ln in (text or "").splitlines() if not re.fullmatch(r"\s*\d{1,3}\s*", ln)]
    return hashlib.sha1(qc_pages.norm_text("\n".join(lines)).encode("utf-8")).hexdigest()[:16]


def snapshot(out, deck=None) -> dict:
    """{"deck", "at", "pages": [{"page", "title", "text_fp", "image_hash"}]}."""
    out = Path(out)
    deck = Path(deck) if deck else _state.compiled_deck(out)
    if not deck.exists():
        raise SystemExit(f"ERROR: no deck at {deck}. Compile first, or pass --deck <file>.")
    texts = qc_pages.page_texts(deck)
    images = {}
    try:
        import render_manifest as RM
        man = RM.read(qc_pages.qc_dir(out))
        if man and man.get("deck_digest") == RM.file_md5(deck):
            images = {int(p["page"]): p.get("hash", "") for p in man.get("pages") or []}
    except Exception:
        pass
    pages = []
    for i, t in enumerate(texts, 1):
        first = next((ln.strip() for ln in t.splitlines() if ln.strip()), "")
        pages.append({"page": i, "title": first[:120], "text_fp": _text_fp(t),
                      "image_hash": images.get(i, "")})
    return {"deck": str(deck), "at": datetime.now().isoformat(timespec="seconds"),
            "pages": pages}


def parse_findings(raw: str) -> list[dict]:
    """A JSON list of {"page": N, "issue": ...} (also "slide"), or text lines
    'slide N: issue' / 'page N: issue'."""
    raw = (raw or "").strip()
    if raw.startswith("["):
        items = json.loads(raw)
        out = []
        for it in items:
            n = it.get("page", it.get("slide"))
            out.append({**it, "page": int(n) if n is not None else None,
                        "issue": str(it.get("issue", ""))})
        return out
    out = []
    for ln in raw.splitlines():
        m = re.match(r"\s*(?:slide|page)\s+(\d{1,3})\b\s*[:.,-]?\s*(.*)", ln, re.I)
        if m:
            out.append({"page": int(m.group(1)), "issue": m.group(2).strip()})
        elif ln.strip():
            out.append({"page": None, "issue": ln.strip()})
    return out


def tag(findings: list[dict], now: dict, base: dict | None) -> list[dict]:
    """Each finding plus "page_changed_since_round_1" (None when there is no
    round 1, or the finding names no page) and "picture_changed"."""
    by_now = {p["page"]: p for p in now["pages"]}
    base_text = {p["text_fp"]: p for p in (base or {}).get("pages") or []}
    tagged = []
    for f in findings:
        p = by_now.get(f.get("page"))
        rec = dict(f)
        if base is None or p is None:
            rec["page_changed_since_round_1"] = None
            rec["picture_changed"] = None
        else:
            old = base_text.get(p["text_fp"])
            rec["page_changed_since_round_1"] = old is None
            rec["picture_changed"] = (None if old is None or not (old["image_hash"] and p["image_hash"])
                                      else old["image_hash"] != p["image_hash"])
            if old is not None and old["page"] != p["page"]:
                rec["round_1_page"] = old["page"]
        rec["title"] = p["title"] if p else ""
        tagged.append(rec)
    return tagged


def tally(tagged: list[dict]) -> dict:
    ch = sum(1 for f in tagged if f.get("page_changed_since_round_1") is True)
    un = sum(1 for f in tagged if f.get("page_changed_since_round_1") is False)
    na = len(tagged) - ch - un
    return {"findings": len(tagged), "on_changed_pages": ch, "on_unchanged_pages": un,
            "not_tagged": na}


def _line(rnd: int, t: dict) -> str:
    return (f"round {rnd}: {t['findings']} finding(s); {t['on_changed_pages']} on pages changed "
            f"since round 1, {t['on_unchanged_pages']} on unchanged pages"
            + (f", {t['not_tagged']} not tagged (no page, or no round 1)" if t["not_tagged"] else ""))


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("start", "record", "tally"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--round", type=int, default=0)
    ap.add_argument("--deck", type=Path)
    ap.add_argument("--findings", help="a file with the round's findings (JSON list or "
                                       "'slide N: ...' lines), or '-' for standard input")
    a = ap.parse_args(argv)
    d = _dir(a.out)
    if a.cmd in ("start", "record") and a.round < 1:
        print("ERROR: give --round 1, 2, ...")
        return 2
    if a.cmd == "start":
        snap = snapshot(a.out, a.deck)
        d.mkdir(parents=True, exist_ok=True)
        (d / f"round_{a.round}.json").write_text(json.dumps(snap, indent=1), encoding="utf-8")
        n = len(snap["pages"])
        print(f"Round {a.round}: kept the fingerprint of all {n} page(s) of {Path(snap['deck']).name}.")
        print(f"  Check EVERY page this round (owner's decision 2026-10-14: round 2 stays on "
              f"every page until the measurement says otherwise).")
        print(f"  Then: py -3 \"{Path(__file__)}\" record --out \"{a.out}\" --round {a.round} "
              f"--findings <file with one 'slide N: issue' line per finding>")
        return 0
    if a.cmd == "record":
        snap_p = d / f"round_{a.round}.json"
        if not snap_p.exists():
            print(f"REFUSED: no fingerprint for round {a.round}. Run first, before the checkers "
                  f"start: number_check.py start --out \"{a.out}\" --round {a.round}")
            return 3
        if not a.findings:
            print("ERROR: give --findings <file> (or '-' to read them from standard input).")
            return 2
        raw = sys.stdin.read() if a.findings == "-" else Path(a.findings).read_text(encoding="utf-8")
        now = json.loads(snap_p.read_text(encoding="utf-8"))
        base_p = d / "round_1.json"
        base = json.loads(base_p.read_text(encoding="utf-8")) if a.round > 1 and base_p.exists() else None
        if a.round > 1 and base is None:
            print("NOTE: no round 1 fingerprint in this build, so findings cannot be tagged "
                  "changed / unchanged. Next deck: run 'start --round 1' before round 1.")
        tagged = tag(parse_findings(raw), now, base)
        t = tally(tagged)
        (d / f"findings_round_{a.round}.json").write_text(json.dumps(
            {"round": a.round, "at": datetime.now().isoformat(timespec="seconds"),
             "tally": t, "findings": tagged}, indent=1), encoding="utf-8")
        print(_line(a.round, t) + ".")
        for f in tagged:
            if f.get("page_changed_since_round_1") is False:
                print(f"  on an UNCHANGED page: slide {f['page']}: {f['issue'][:100]}")
        print(f"  Recorded in {d / f'findings_round_{a.round}.json'}. Fix findings as usual; "
              "this record only measures where they land.")
        return 0
    rounds = sorted(d.glob("findings_round_*.json")) if d.exists() else []
    if not rounds:
        print(f"No number-check round recorded in {d}.")
        return 0
    for p in rounds:
        rec = json.loads(p.read_text(encoding="utf-8"))
        print(_line(rec["round"], rec["tally"]) + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
