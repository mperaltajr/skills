"""_rulings.py: the deck's record of the user's rulings, in their own words.

One file per deck: `<session folder>\\_session\\rulings.md` (what people read)
and `rulings.json` beside it (what scripts read). Only `add_ruling.py` writes
them. Every entry is the user's exact words, checked word for word against
the live session transcript, with the chat's reading on its own labeled line.
A newer ruling on the same topic for the same slide replaces the older one;
the older one stays in the file, struck out.

Why (owner's decision, 2026-10-14): about 6 in 10 of the user's steers on two
decks repeated something already said. The chat retyped them into prompts in
its own words and got three of them wrong, word for word checkable. A script
that stores only the user's exact words, keyed on fixed slide ids, cannot.

Also here:
  - the transcript reader shared by every "the user's own words" check
    (add_ruling.py, map_source_pages.py approve, steer_checks.py approve);
  - announce(): every pipeline script prints `RULINGS: <path>` when it starts,
    so the path is in front of the chat after a compaction too;
  - compact_hint(): the /compact suggestion at the two stage boundaries.
"""
from __future__ import annotations

import atexit
import glob
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

RULINGS_MD = "rulings.md"
RULINGS_JSON = "rulings.json"
SESSION_DIR = "_session"
DECK_ID = "deck"

# ------------------------------------------------------------------ places

def _brief_from_meta(out_dir: Path) -> Path | None:
    try:
        meta = json.loads((Path(out_dir) / "_meta.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    bp = meta.get("brief") or (meta.get("deck") or {}).get("brief")
    return Path(bp) if bp else None


def session_dir(out=None, brief=None) -> Path:
    """The deck's `_session` folder. A brief saved inside a `_session` folder
    names it; else the build's recorded brief does; else `<out>/_session`."""
    for b in ([Path(brief)] if brief else []) + (
            [_brief_from_meta(Path(out))] if out else []):
        if b and b.parent.name.lower() == SESSION_DIR:
            return b.parent
    if out:
        return Path(out) / SESSION_DIR
    if brief:
        return Path(brief).parent / SESSION_DIR
    raise ValueError("session_dir needs an out folder or a brief")


def rulings_md(sd: Path) -> Path:
    return Path(sd) / RULINGS_MD


def rulings_json(sd: Path) -> Path:
    return Path(sd) / RULINGS_JSON


def find_brief(sd: Path, out=None) -> Path | None:
    """The deck's brief: the build's recorded one, else the one
    narrative-brief-*.md in the session folder (newest when several)."""
    if out:
        b = _brief_from_meta(Path(out))
        if b and b.is_file():
            return b
    hits = sorted(Path(sd).glob("narrative-brief-*.md"), key=lambda p: p.stat().st_mtime,
                  reverse=True)
    return hits[0] if hits else None


# ------------------------------------------------------------------ store

def load(sd: Path) -> dict:
    p = rulings_json(sd)
    if not p.exists():
        return {"schema": 1, "rulings": []}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        data.setdefault("rulings", [])
        return data
    except Exception:
        return {"schema": 1, "rulings": []}


def active(data: dict, slide_id: str | None = None) -> list[dict]:
    rs = [r for r in data.get("rulings", [])
          if not r.get("replaced_by") and not r.get("retired")]
    if slide_id is not None:
        rs = [r for r in rs if r.get("id") == slide_id]
    return rs


def norm_topic(t: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).split())


def save(sd: Path, data: dict) -> None:
    Path(sd).mkdir(parents=True, exist_ok=True)
    rulings_json(sd).write_text(json.dumps(data, indent=2, ensure_ascii=False),
                                encoding="utf-8")
    rulings_md(sd).write_text(render_md(data, sd), encoding="utf-8")


def _entry_md(r: dict) -> list[str]:
    struck = bool(r.get("replaced_by") or r.get("retired"))
    s = (lambda t: f"~~{t}~~") if struck else (lambda t: t)
    head = f"R{r['n']} · topic: {r.get('topic') or '(none)'} · {r.get('at', '')[:16].replace('T', ' ')}"
    why = (f" (replaced by R{r['replaced_by']})" if r.get("replaced_by") else
           f" (retired: {r['retired'].get('why', '')})" if r.get("retired") else "")
    lines = [f"### {s(head)}" + why]
    if r.get("moved_from"):
        lines.append(f"(moved from R{r['moved_from']['n']} on slide id "
                     f"{r['moved_from']['id']}, at the user's word)")
    lines.append(s(f"**The user's words:** \"{r['quote']}\""))
    if r.get("reading"):
        lines.append(s(f"**Chat's reading:** {r['reading']}"))
    where = r.get("transcript_file") or ""
    if where:
        lines.append(f"(word for word in {Path(where).name}, line {r.get('transcript_line')})")
    return lines + [""]


def render_md(data: dict, sd: Path) -> str:
    rs = data.get("rulings", [])
    out = ["# Rulings for this deck", "",
           "Written only by `add_ruling.py`; never edit this file by hand. Each entry is the "
           "user's exact words, checked word for word against the session transcript. The "
           "chat's reading is on its own labeled line and is not the user's words. A newer "
           "ruling on the same topic for the same slide replaces the older one, which stays "
           "here struck out.", "",
           f"This file: {rulings_md(sd)}", ""]
    ids = [DECK_ID] + sorted({r["id"] for r in rs if r["id"] != DECK_ID})
    retired_ids = _retired_ids(sd)
    for sid in ids:
        mine = [r for r in rs if r["id"] == sid]
        if not mine and sid != DECK_ID:
            continue
        gone = retired_ids.get(sid)
        out.append("## Whole deck" if sid == DECK_ID else f"## Slide id: {sid}"
                   + (f" ({gone})" if gone else ""))
        out.append("")
        if not mine:
            out += ["(none yet)", ""]
        for r in mine:
            out += _entry_md(r)
    return "\n".join(out).rstrip() + "\n"


def _retired_ids(sd: Path) -> dict:
    """{slide id: 'slide removed <date>'} from _session/slide_ids.json
    (build_deck.py --delete retires the removed slide's id there)."""
    try:
        reg = json.loads((Path(sd) / "slide_ids.json").read_text(encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for sid, ent in (reg.get("ids") or {}).items():
        ret = ent.get("retired") if isinstance(ent, dict) else None
        if ret:
            out[sid] = f"slide removed {str(ret.get('at', ''))[:10]}".strip()
    return out


def retire(sd: Path, n: int, why: str, words: str, where=None) -> dict:
    """The user retired ruling R<n> (its slide was removed, or it no longer
    applies). Kept in the file, struck out; never active again."""
    data = load(sd)
    r = next((x for x in data["rulings"] if x["n"] == n), None)
    if r is None:
        raise KeyError(n)
    r["retired"] = {"why": why.strip() or "retired", "words": words.strip(),
                    "at": datetime.now().isoformat(timespec="seconds"),
                    "transcript_file": where[0] if where else "",
                    "transcript_line": where[1] if where else None}
    save(sd, data)
    return r


def move(sd: Path, n: int, new_id: str, words: str, where=None) -> tuple[dict, dict]:
    """The user said ruling R<n> belongs to another slide. A new entry with
    the same quote and reading on `new_id`; the old one is struck out as
    replaced. The quote is never changed."""
    data = load(sd)
    old = next((x for x in data["rulings"] if x["n"] == n), None)
    if old is None:
        raise KeyError(n)
    m = 1 + max([x["n"] for x in data["rulings"]] or [0])
    entry = {k: old.get(k) for k in ("topic", "quote", "reading", "transcript_file",
                                      "transcript_line")}
    entry.update({"n": m, "id": new_id, "at": datetime.now().isoformat(timespec="seconds"),
                  "moved_from": {"n": n, "id": old["id"], "words": words.strip(),
                                 "transcript_file": where[0] if where else "",
                                 "transcript_line": where[1] if where else None}})
    old["replaced_by"] = m
    data["rulings"].append(entry)
    save(sd, data)
    return entry, old


def add(sd: Path, slide_id: str, quote: str, reading: str, topic: str,
        where: tuple[str, int] | None, replaces: list[int] | None = None) -> tuple[dict, list[dict]]:
    """Store one ruling. Returns (the new entry, the entries it replaced)."""
    data = load(sd)
    n = 1 + max([r["n"] for r in data["rulings"]] or [0])
    entry = {"n": n, "id": slide_id, "topic": topic.strip(), "quote": quote.strip(),
             "reading": (reading or "").strip(),
             "at": datetime.now().isoformat(timespec="seconds"),
             "transcript_file": where[0] if where else "",
             "transcript_line": where[1] if where else None}
    replaced = []
    want = norm_topic(topic)
    for r in data["rulings"]:
        if r.get("replaced_by"):
            continue
        if (r["id"] == slide_id and want and norm_topic(r.get("topic", "")) == want) or \
                (replaces and r["n"] in replaces):
            r["replaced_by"] = n
            replaced.append(r)
    data["rulings"].append(entry)
    save(sd, data)
    return entry, replaced


# ------------------------------------------------------------------ transcript

_STRIP_BLOCKS = ("system-reminder", "task-notification", "local-command-stdout",
                 "local-command-stderr", "bash-stdout", "bash-stderr",
                 "command-message", "command-name")
_QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                         " ": " "})


def transcript_files(explicit: str | None = None, hours: float = 48.0) -> list[Path]:
    """Transcripts to search, newest first. `explicit` (a file or folder),
    else SLIDE_LAB_TRANSCRIPT (a file or folder), else every top-level session
    transcript under ~/.claude/projects changed in the last `hours` (the live
    session is the newest). Agent transcripts (sub-folders) are never read:
    only the user's own messages count."""
    src = explicit or os.environ.get("SLIDE_LAB_TRANSCRIPT", "")
    if src:
        p = Path(src)
        if p.is_file():
            return [p]
        files = list(p.glob("*.jsonl")) if p.is_dir() else []
    else:
        root = Path(os.path.expanduser("~")) / ".claude" / "projects"
        cutoff = time.time() - hours * 3600
        files = [Path(f) for f in glob.glob(str(root / "*" / "*.jsonl"))
                 if os.path.getmtime(f) >= cutoff]
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)


def _clean(text: str) -> str:
    for tag in _STRIP_BLOCKS:
        text = re.sub(rf"<{tag}>.*?</{tag}>", " ", text, flags=re.S)
    return text


def norm_words(text: str) -> str:
    return " ".join((text or "").translate(_QUOTES).split())


def user_messages(path: Path):
    """(line number, text) of every message the user typed or pasted. Tool
    results, compaction summaries, agent threads and injected notices are not
    the user's words and are skipped."""
    try:
        fh = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return
    with fh:
        for i, line in enumerate(fh, 1):
            if '"user"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") != "user" or d.get("isCompactSummary") or d.get("isSidechain") \
                    or d.get("isMeta"):
                continue
            msg = d.get("message") or {}
            if msg.get("role") not in (None, "user"):
                continue
            c = msg.get("content")
            if isinstance(c, str):
                parts = [c]
            elif isinstance(c, list):
                parts = [x.get("text", "") for x in c
                         if isinstance(x, dict) and x.get("type") == "text"]
            else:
                parts = []
            text = _clean("\n".join(parts))
            if text.strip().startswith("This session is being continued from a previous"):
                continue
            if text.strip():
                yield i, text


def find_quote(quote: str, files: list[Path]) -> tuple[str, int] | None:
    """Where the user wrote `quote`, word for word (spacing and curly quotes
    aside; case counts). Pieces joined by "..." must all be in one message, in
    order. None when it is in none of their messages."""
    pieces = [norm_words(p) for p in re.split(r"\s*(?:\.\.\.|…)\s*", quote or "")]
    pieces = [p for p in pieces if p]
    if not pieces:
        return None
    for f in files:
        for ln, text in user_messages(f):
            t = norm_words(text)
            pos = 0
            for p in pieces:
                k = t.find(p, pos)
                if k < 0:
                    break
                pos = k + len(p)
            else:
                return str(f), ln
    return None


def quote_too_short(quote: str) -> bool:
    words = norm_words(quote.replace("...", " ")).split()
    return len(words) < 2 or len(" ".join(words)) < 6


def check_users_words(words: str, explicit: str | None = None) -> tuple[bool, str, tuple | None]:
    """(ok, message, where). Shared by every step that records the user's
    approval in their own words."""
    if quote_too_short(words):
        return False, ("too short to check: give at least two of the user's words, "
                       "exactly as they typed them"), None
    files = transcript_files(explicit)
    if not files:
        return False, ("no session transcript was found to check the words against "
                       "(looked in ~/.claude/projects; set SLIDE_LAB_TRANSCRIPT to the "
                       "session's .jsonl file)"), None
    where = find_quote(words, files)
    if not where:
        return False, ("these words are not in any message the user typed in this "
                       f"session (searched {len(files)} transcript(s), newest "
                       f"{files[0].name}). Copy their words exactly; do not "
                       "paraphrase, shorten inside a sentence or fix their typos. "
                       "Join separate pieces of one message with ..."), None
    return True, "", where


# ------------------------------------------------------------------ printing

_announced: dict = {}


def announce(out=None, brief=None, stream=None) -> None:
    """Print `RULINGS: <path>` once per process, when the script starts.
    Printed first, not last: every refusal and next-step message keeps its
    commands in its LAST two lines (sessions read only the tail of an
    output), and a trailing RULINGS line pushed them out. Never raises: a
    script must not fail over this line."""
    if _announced.get("on"):
        return
    try:
        sd = session_dir(out=out, brief=brief)
    except Exception:
        return
    _announced["on"] = True

    def _say():
        try:
            data = load(sd)
            n = len(active(data))
            tail = (f"({n} in force; read it before any slide reply or storyline change)"
                    if n else "(none recorded yet)")
            print(f"RULINGS: {rulings_md(sd)} {tail}", file=stream or sys.stdout)
        except Exception:
            pass
    _say()


def compact_hint(sd: Path, stage: str) -> list[str]:
    """The /compact suggestion at the two stage boundaries (owner's decision,
    2026-10-14): when the storyline is approved, and after the picks."""
    page_map = Path(sd) / "page_map.json"
    keep = f"the path to {rulings_md(sd)}"
    if page_map.exists() or stage == "picks":
        keep += " and the page map"
    return [
        "",
        f"Suggestion for the user ({stage}): this is a good point to compact the chat. It "
        "saves tokens on every later turn, and nothing the build needs is lost: the "
        "rulings, the page map and the build state are all in files.",
        f"  Suggest typing: /compact keep {keep}",
        "  After it, read the rulings file before replying about any slide.",
    ]
