#!/usr/bin/env python3
"""slide_ids.py: give every slide of a brief a fixed id (`**Slide id:** risks`).

Slide numbers move: a divider is inserted, a slide is cut, and "slide 18" is a
different page. On one client deck, folder slide_25 held the brief's Slide 18 and
the user's comments landed on the wrong page. A slide id never changes and is
never reused, so rulings, picks and the source-page map stay on the right page
(owner's decision, 2026-10-14).

storyline-helper runs this when the storyline is approved (emit_dot_dash.py
calls it); it is safe to run again: slides that have an id keep it, new slides
get one, and an id once used is never handed out again (the ids used so far are
kept in `_session/slide_ids.json`). The seal does not count the id lines, so a
sealed brief stays sealed.

  py -3 scripts/slide_ids.py --brief <brief.md>          add the missing ids
  py -3 scripts/slide_ids.py --brief <brief.md> --check  list them, change nothing
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

HEADER_RE = re.compile(r"^#{2,3}\s+Slide\s+(\d+)\s*(?:[—\-:]\s*(.+?)\s*)?$", re.M)
ID_LINE_RE = re.compile(r"^\*\*Slide id:?\*\*:?\s*`?([^`\s]+)`?\s*$", re.M | re.I)
TYPE_RE = re.compile(r"^\*\*(?:Slide type|Archetype):?\*\*:?\s*(.+)$", re.M | re.I)
ID_OK = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
REGISTRY = "slide_ids.json"

STOP = set("""a an the and or of to in on for with by at from as is are was were be been
this that these those it its into over under than then so but not no our we you your their
they how why what who which when where will can could should would may might must has have
had do does did each every all any more most less one two three four five six seven eight
nine ten new now just only also very about across per vs via up down out off""".split())


# Headlines are claims ("The biggest risks to the plan are met by ..."), so
# their first words are often verbs or adjectives. These go last when naming.
SOFT = set("""biggest largest smallest best worst first last next main key major top full
real whole same other older newer newest working tested locked separate global early late
reaches reach grows grow builds build helps help needs need makes make keeps keep turns turn
sells sell buys buy runs run carries carry pays pay funds fund choose chooses cover covers
acquires acquire launches launch returns return gets get comes come goes go leads led shows
show protect protects should already more less much many still even""".split())


def _words(title: str, common: frozenset = frozenset()) -> list[str]:
    t = re.sub(r"\*\*|`|_", " ", title or "").lower().replace("’", "'")
    t = re.sub(r"'s\b", "", t)
    ws = [w for w in re.findall(r"[a-z][a-z0-9]+", t) if len(w) >= 3 and w not in STOP]
    strong = [w for w in ws if w not in SOFT and w not in common]
    return strong + [w for w in ws if w not in strong]


def _base_ids(title: str, slide_type: str, common: frozenset = frozenset()) -> list[str]:
    st = (slide_type or "").lower()
    tl = (title or "").lower()
    words = _words(title, common)
    if "cover" in st or st.strip() in ("title", "title slide"):
        return ["cover", "cover-" + "-".join(words[:1])]
    if "contents" in st or "agenda" in st or tl.strip() in ("contents", "agenda"):
        return ["contents"]
    if "executive summary" in st or "executive summary" in tl:
        return ["exec-summary"]
    if "divider" in st or "section" in st:
        return ["divider-" + "-".join(words[:n]) for n in (1, 2, 3)] if words else ["divider"]
    if not words:
        return ["slide"]
    return ["-".join(words[:n])[:28].strip("-") for n in (1, 2, 3)]


def registry_path(brief: Path) -> Path:
    import _rulings
    return _rulings.session_dir(brief=brief) / REGISTRY


def load_registry(brief: Path) -> dict:
    p = registry_path(brief)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"ids": {}}


def blocks(text: str) -> list[dict]:
    """Every slide block: number, title, start/end offsets, its id if set."""
    ms = list(HEADER_RE.finditer(text))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        # A block ends at the next H1/H2 heading too (Flags, Deck-level notes).
        nxt = re.search(r"^#{1,2}\s+(?!#)(?!Slide\s+\d)", text[m.end():end], re.M)
        if nxt:
            end = m.end() + nxt.start()
        body = text[m.end():end]
        idm = ID_LINE_RE.search(body)
        tm = TYPE_RE.search(body)
        out.append({"n": int(m.group(1)), "title": (m.group(2) or "").strip(),
                    "header_end": m.end(), "end": end,
                    "id": idm.group(1).strip().lower() if idm else "",
                    "type": tm.group(1).strip() if tm else ""})
    return out


def ids_in_brief(text: str) -> dict[int, str]:
    return {b["n"]: b["id"] for b in blocks(text) if b["id"]}


def assign(brief: Path, write: bool = True) -> tuple[list[tuple[int, str]], dict[int, str], list[str]]:
    """Add the missing ids. Returns (added [(n, id)], every id {n: id}, problems)."""
    raw = brief.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    bl = blocks(text)
    problems = []
    seen: dict[str, int] = {}
    for b in bl:
        if not b["id"]:
            continue
        if not ID_OK.match(b["id"]):
            problems.append(f"slide {b['n']}: the id {b['id']!r} is not a short name of "
                            "lower-case letters, digits and hyphens")
        if b["id"] in seen:
            problems.append(f"slides {seen[b['id']]} and {b['n']} have the same id "
                            f"{b['id']!r}; ids must be unique")
        seen[b["id"]] = b["n"]
    reg = load_registry(brief)
    used = set(reg.get("ids", {})) | set(seen)
    added: list[tuple[int, str]] = []
    # A word in many headlines (the company's name) tells the slides apart badly.
    freq: dict[str, int] = {}
    for b in bl:
        for w in set(_words(b["title"])):
            freq[w] = freq.get(w, 0) + 1
    common = frozenset(w for w, c in freq.items() if c >= max(3, len(bl) // 5))
    for b in bl:
        if b["id"]:
            continue
        cand = None
        for base in _base_ids(b["title"], b["type"], common):
            if base and base not in used:
                cand = base
                break
        if cand is None:
            base = _base_ids(b["title"], b["type"], common)[0] or "slide"
            k = 2
            while f"{base}-{k}" in used:
                k += 1
            cand = f"{base}-{k}"
        used.add(cand)
        b["id"] = cand
        added.append((b["n"], cand))
    if problems or not write:
        return added, {b["n"]: b["id"] for b in bl}, problems
    if added:
        # Insert from the bottom up so offsets stay right.
        for b in sorted((b for b in bl if (b["n"], b["id"]) in added),
                        key=lambda b: b["header_end"], reverse=True):
            text = text[:b["header_end"]] + f"\n\n**Slide id:** {b['id']}" + text[b["header_end"]:]
        brief.write_bytes(text.replace("\n", nl).encode("utf-8"))
    now = datetime.now().isoformat(timespec="seconds")
    ids = reg.setdefault("ids", {})
    for b in bl:
        ids.setdefault(b["id"], {"first_title": b["title"], "at": now})
    p = registry_path(brief)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")
    return added, {b["n"]: b["id"] for b in bl}, problems


def label(n: int, slide_id: str | None) -> str:
    """'Slide 25 (risks)', the way every page and message names a slide."""
    return f"Slide {n} ({slide_id})" if slide_id else f"Slide {n}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Give every slide of a brief a fixed id.")
    ap.add_argument("--brief", required=True, type=Path)
    ap.add_argument("--check", action="store_true", help="List the ids; change nothing.")
    args = ap.parse_args(argv)
    if not args.brief.is_file():
        print(f"ERROR: no brief at {args.brief}")
        return 2
    import _rulings
    _rulings.announce(brief=args.brief)
    added, ids, problems = assign(args.brief, write=not args.check)
    if problems:
        print("NOT CHANGED: fix these in the brief first:")
        for p in problems:
            print(f"  - {p}")
        return 3
    for n in sorted(ids):
        new = " (new)" if (n, ids[n]) in added else ""
        print(f"  {label(n, ids[n])}{new}")
    if args.check:
        missing = [n for n, _i in added]
        print(f"{len(ids)} slide(s); " + (f"{len(missing)} without an id: run without --check "
                                          "to add them." if missing else "every slide has an id."))
        return 0
    print(f"[ok] {len(added)} id(s) added, {len(ids)} slide(s) in all. Ids never change and "
          "are never reused; the seal does not count them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
