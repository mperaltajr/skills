"""_context_pack.py: the per-slide context pack and the steer receipt.

Every designer dispatch gets a short pack in `slide_NN/_context.md` (under
2 KB): the slide's sources (its Source line, its pinned page, the deck's
registered sources with their status), its number trail, the user's rulings
for that slide in their exact words, and the deck-wide rulings. Only scripts
write it: the chat's own wording never reaches a designer as the user's
direction (owner's decision, 2026-10-14; the chat once wrote "inspiration
only" for pages the user had said to copy).

The designer answers each ruling of its slide in `slide_NN/_steer_answers.txt`,
one line per ruling: `R7: <what I changed for it>`. REVIEW.html shows one row
per ruling with that answer (the steer receipt); a ruling with no answer, or
added after the design was made, shows red before the user looks.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import _rulings

START = "<!-- RULINGS PACK START (written by Slide Lab; do not edit) -->"
END = "<!-- RULINGS PACK END -->"
ANSWERS = "_steer_answers.txt"
SOURCES_JSON = "sources.json"
MAX_BYTES = 2048


def _meta(out_dir: Path) -> dict:
    try:
        return json.loads((Path(out_dir) / "_meta.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def slide_entry(out_dir: Path, n: int) -> dict:
    for s in _meta(out_dir).get("slides") or []:
        if int(s.get("n") or 0) == int(n):
            return s
    return {}


def slide_id_for(out_dir: Path, n: int) -> str:
    return (slide_entry(out_dir, n).get("slide_id") or "").strip()


def n_for_id(out_dir: Path, slide_id: str) -> int | None:
    for s in _meta(out_dir).get("slides") or []:
        if (s.get("slide_id") or "") == slide_id:
            return int(s.get("n"))
    return None


def load_sources(sd: Path) -> dict:
    try:
        return json.loads((Path(sd) / SOURCES_JSON).read_text(encoding="utf-8"))
    except Exception:
        return {"sources": [], "trail": []}


def _for_slide(item: dict, slide_id: str) -> bool:
    ids = item.get("slides") or ["all"]
    return "all" in ids or (slide_id and slide_id in ids)


def _ruling_line(r: dict, with_reading: bool = True, cap: int = 0) -> list[str]:
    q = r["quote"]
    if cap and len(q) > cap:
        q = q[:cap].rstrip() + "..."
    out = [f"- R{r['n']} ({r.get('topic') or 'no topic'}): the user said \"{q}\""]
    if with_reading and r.get("reading"):
        out.append(f"  Chat's reading (not the user's words): {r['reading']}")
    return out


def pack_block(out_dir: Path, slide: dict, brief=None) -> str:
    """The pack for one slide. `slide` is a parsed brief slide or a _meta entry;
    `brief` (its path) finds the session folder before _meta.json exists."""
    out_dir = Path(out_dir)
    sd = _rulings.session_dir(out=out_dir, brief=brief)
    sid = (slide.get("slide_id") or "").strip()
    n = slide.get("slide_n") or slide.get("n")
    data = _rulings.load(sd)
    mine = _rulings.active(data, sid) if sid else []
    deck = _rulings.active(data, _rulings.DECK_ID)
    src = load_sources(sd)
    head = [START, "## 0b. Sources and the user's rulings for this slide (exact words)", "",
            f"Slide {n}" + (f", slide id `{sid}`" if sid else " (no slide id in the brief)")
            + f". Full record: {_rulings.rulings_md(sd)}", ""]
    srcs = ["**Sources:**"]
    if (slide.get("source") or "").strip():
        srcs.append(f"- Source line: {slide['source'].strip()}")
    pin = (slide.get("pinned_source_page") or "").strip()
    if pin:
        srcs.append(f"- Pinned page (option A reproduces it): {pin}")
    for s in src.get("sources") or []:
        if _for_slide(s, sid):
            status = ("validated by the user, do not re-check its numbers"
                      if s.get("validated") else "not validated")
            srcs.append(f"- {s.get('name')}: {s.get('path')} ({status})")
    trail = [t for t in (src.get("trail") or []) if _for_slide(t, sid)]
    if trail:
        srcs.append("**Number trail:**")
        srcs += [f"- {t['figure']}: {t['where']}" for t in trail[:8]]
    if len(srcs) == 1:
        srcs.append("- none recorded beyond the brief")
    srcs += ["Every number comes from the brief or a source above. When a number has "
             "no source, write \"no source for <number>\" in your answers file; never guess.", ""]
    rules = ["**The user's rulings for this slide:**"]
    for r in mine:
        rules += _ruling_line(r)
    if not mine:
        rules.append("- none")
    rules.append("")
    tail = ["Answer every ruling above in `_steer_answers.txt` next to this file, one line "
            "each: `R<n>: <what you changed for it>` (or `R<n>: already true, <where>`). "
            "The review page shows the user each ruling beside your answer.", END]

    def compose(deck_lines):
        return "\n".join(head + srcs + rules + deck_lines + tail) + "\n"

    deck_lines = ["**Deck-wide rulings (every slide):**"]
    for r in deck:
        deck_lines += _ruling_line(r)
    if not deck:
        deck_lines.append("- none")
    deck_lines.append("")
    text = compose(deck_lines)
    if len(text.encode("utf-8")) > MAX_BYTES:
        short = ["**Deck-wide rulings (every slide; readings in the rulings file):**"]
        for r in deck:
            short += _ruling_line(r, with_reading=False, cap=160)
        short.append("")
        text = compose(short)
        k = len(deck)
        while len(text.encode("utf-8")) > MAX_BYTES and k > 0:
            k -= 1
            cut = ["**Deck-wide rulings (every slide; the rest are in the rulings file):**"]
            for r in deck[-k:] if k else []:
                cut += _ruling_line(r, with_reading=False, cap=120)
            cut += [f"- {len(deck) - k} more: read {_rulings.rulings_md(sd)}", ""]
            text = compose(cut)
    return text


_DIRECTION_RE = re.compile(r"^(#{1,6})\s*Direction from the user\b.*$", re.M | re.I)


def drop_chat_direction(text: str) -> tuple[str, int]:
    """Take hand-written "Direction from the user" blocks out of a designer's
    file (each runs to the next heading of the same or a higher level). The
    chat wrote these in its own words; one turned "spacing between impact and
    high" into a different request. Returns (text, blocks removed)."""
    n = 0
    while True:
        m = _DIRECTION_RE.search(text)
        if not m:
            return text, n
        level = len(m.group(1))
        nxt = re.compile(rf"^#{{1,{level}}}\s", re.M).search(text, m.end())
        end = nxt.start() if nxt else len(text)
        text = text[:m.start()] + text[end:]
        n += 1


def put_pack(text: str, block: str) -> str:
    """Replace the pack in a file's text, or add it before section 1."""
    if START in text and END in text:
        a = text.index(START)
        b = text.index(END) + len(END)
        return text[:a] + block.rstrip("\n") + text[b:]
    m = re.search(r"^## 1\. ", text, re.M)
    if m:
        return text[:m.start()] + block + "\n" + text[m.start():]
    return text.rstrip("\n") + "\n\n" + block


def refresh(out_dir: Path, n: int) -> list[Path]:
    """Write the current pack into slide n's _context.md and _edit_request.md
    (whichever exist). Returns the files changed."""
    out_dir = Path(out_dir)
    entry = dict(slide_entry(out_dir, n))
    entry.setdefault("n", n)
    block = pack_block(out_dir, entry)
    done = []
    for name in ("_context.md", "_edit_request.md"):
        p = out_dir / f"slide_{int(n):02d}" / name
        if p.exists():
            t = p.read_text(encoding="utf-8")
            new = put_pack(t, block)
            if new != t:
                p.write_text(new, encoding="utf-8")
                done.append(p)
    return done


# ------------------------------------------------------------------ receipt

ANSWER_RE = re.compile(r"^\s*R(\d+)\s*[:\-]\s*(.+?)\s*$")


def read_answers(slide_dir: Path) -> tuple[dict[int, str], float | None]:
    p = Path(slide_dir) / ANSWERS
    if not p.exists():
        return {}, None
    got = {}
    for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = ANSWER_RE.match(ln)
        if m:
            got[int(m.group(1))] = m.group(2)
    return got, p.stat().st_mtime


def receipt(out_dir: Path, n: int) -> list[dict]:
    """One row per ruling in force for slide n: the user's words, the
    designer's answer, and whether it is missing."""
    out_dir = Path(out_dir)
    sid = slide_id_for(out_dir, n)
    if not sid:
        return []
    sd = _rulings.session_dir(out=out_dir)
    rows = []
    answers, mtime = read_answers(out_dir / f"slide_{int(n):02d}")
    for r in _rulings.active(_rulings.load(sd), sid):
        ans = answers.get(r["n"], "")
        late = False
        try:
            late = bool(mtime) and datetime.fromisoformat(r["at"]).timestamp() > mtime + 1
        except Exception:
            pass
        why = ("" if ans and not late else
               "the ruling came after this design was made" if late else
               "the designer did not answer it")
        rows.append({"n": r["n"], "topic": r.get("topic", ""), "quote": r["quote"],
                     "reading": r.get("reading", ""), "answer": "" if late else ans,
                     "ok": not why, "why": why})
    return rows
