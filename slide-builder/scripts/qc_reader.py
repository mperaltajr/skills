#!/usr/bin/env python3
"""qc_reader.py: the brief for the fresh agent that reads a QC round's pages.

Owner's decision 2026-10-14 (speed verdict Q2, decision C): the page reading
of a QC round moves out of the main chat into a fresh reader agent. It reads
every page alone, fills <build>/_qc/page_notes.json, runs record_vision_qc.py
itself (the proof of reading is unchanged: codes and quotes), and hands back
only the open Critical and Major findings, one line each. The main chat keeps
the fixes, the user's approvals and check_done. Reading in the main chat cost
about 17M tokens a round on a 60-page deck; a reader agent about 3-6M.

Without the user's rules a fresh agent flags settled items (an approved
headline reworded) or misses rule breaks (a named quote), so the brief
carries them: each page's approved headline, no person attribution, the type
rules, and the deck's rulings file (<session>/_session/rulings.md) when there
is one.

qc_pages.py plan writes the filled brief to <build>/_qc/reader_brief.md every
round (from slide-qc/READER_BRIEF.md) and prints how to hand it over.

Run by hand:  py -3 scripts/qc_reader.py --out <build dir>   (after plan)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[1] / "slide-qc" / "READER_BRIEF.md"
SKILL_MD = HERE.parents[1] / "slide-qc" / "SKILL.md"
BRIEF_NAME = "reader_brief.md"


def rulings_path(out) -> Path | None:
    """The deck's rulings file (add_ruling.py writes <session>/_session/rulings.md)."""
    out = Path(out)
    for p in (out / "_session" / "rulings.md", out.parent / "_session" / "rulings.md"):
        if p.exists():
            return p
    return None


def _meta(out) -> dict:
    try:
        return json.loads((Path(out) / "_meta.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def brief_path(out, meta: dict) -> Path | None:
    b = meta.get("brief")
    if b and Path(b).exists():
        return Path(b)
    hits = sorted((Path(out) / "_session").glob("narrative-brief-*.md"),
                  key=lambda p: p.stat().st_mtime)
    return hits[-1] if hits else None


def _cell(s: str) -> str:
    return str(s or "").replace("|", "/").replace("\n", " ").strip()


def headlines(meta: dict) -> str:
    rows = [(int(s.get("n") or 0), s.get("title") or "", s.get("page_type") or "")
            for s in meta.get("slides") or []]
    rows = [r for r in rows if r[1]]
    if not rows:
        return "  (no approved headlines recorded for this build: read titles against the brief)"
    out = ["", "  | Page | Approved headline |", "  |---|---|"]
    out += [f"  | {n} | {_cell(t)} |" for n, t, _pt in sorted(rows)]
    return "\n".join(out)


def _code(p) -> str:
    return f"`{p}`"


def write(out, deck, plan: dict) -> Path:
    """Fill the template for this round; returns the written file."""
    out = Path(out)
    qc = out / "_qc"
    meta = _meta(out)
    rp = rulings_path(out)
    bp = brief_path(out, meta)
    fc = out / "FINAL-CHECK.html"
    fields = {
        "deck": str(deck),
        "n_pages": str(len(plan.get("read_pages") or [])),
        "pages": ", ".join(map(str, plan.get("read_pages") or [])) or "none",
        "to_read": str(qc / "to_read"),
        "n_sheets": str(len(plan.get("sheets") or [])),
        "n_pairs": str(len(plan.get("pairs") or [])),
        "notes": str(qc / "page_notes.json"),
        "final_check": str(fc) if fc.exists() else "(none in this build)",
        "brief": _code(bp) if bp else "(no brief file found: ask the main chat)",
        "rulings": _code(rp) if rp else "none recorded for this deck",
        "skill": str(SKILL_MD),
        "policy": str(HERE / "qc_fix_policy.py"),
        "record_cmd": f'py -3 "{HERE / "record_vision_qc.py"}" --out "{out}"',
        "headlines": headlines(meta),
    }
    text = re.sub(r"<!--.*?-->\s*", "", TEMPLATE.read_text(encoding="utf-8"), count=1,
                  flags=re.S)
    for k, v in fields.items():
        text = text.replace("{{" + k + "}}", v)
    qc.mkdir(parents=True, exist_ok=True)
    dest = qc / BRIEF_NAME
    dest.write_text(text, encoding="utf-8")
    return dest


def handoff_lines(dest: Path) -> list[str]:
    """What qc_pages.py plan prints after writing the brief."""
    return [
        f"  reader brief  : {dest}",
        "Hand the reading to a FRESH reader agent (owner's decision 2026-10-14): dispatch one "
        "general-purpose agent with the prompt",
        f"  \"Read {dest} and do exactly what it says.\"",
        "It reads every page alone, fills page_notes.json, runs record_vision_qc.py and hands "
        "back only the open Critical and Major findings, one line each. Do not read the pages "
        "in this chat as well; fix what it returns (slide-qc Step 7), then plan the next round.",
    ]


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Write the QC reader agent's brief.")
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(HERE))
    import _state
    st = _state.read_state(a.out)
    vp = st.get("vision_plan") or {}
    if not vp:
        print(f"ERROR: no QC round planned. Run first: qc_pages.py plan --out \"{a.out}\"")
        return 2
    plan = {"read_pages": vp.get("read_pages"), "sheets": vp.get("sheets"),
            "pairs": vp.get("pairs")}
    dest = write(a.out, _state.compiled_deck(a.out), plan)
    for ln in handoff_lines(dest):
        print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
