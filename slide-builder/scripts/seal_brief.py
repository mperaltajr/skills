#!/usr/bin/env python3
"""seal_brief.py — record that a brief passed storyline-helper's quality gate.

Run this once the gate has passed (every Critical resolved, Majors handled).
It writes three lines into the brief's front matter:

    storyline_gate_passed: true
    storyline_gate_at: <UTC timestamp>
    storyline_gate_sha: <fingerprint of the brief's text>

build_deck.py checks the fingerprint against the brief it is given. Before
this, the marker was a line anyone could type: the orchestrator was told to
add it by hand to get past the gate, so it certified nothing. Now a brief
edited after the gate, or a marker typed without running the gate, stops prep
with exit 10 and says which.

A brief written in the middle of a session, without storyline-helper, can
still be built with build_deck.py --assume-gated. That is visible and recorded
in the build's _state.json; it is not a quiet bypass.

Run:  py -3 scripts/seal_brief.py --brief <brief.md>
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

FM_RE = re.compile(r"\A(﻿?---\s*\r?\n)(.*?)(\r?\n---\s*\r?\n)", re.S)
GATE_KEYS = ("storyline_gate_passed", "storyline_gate_at", "storyline_gate_sha")


def body_fingerprint(body: str) -> str:
    """Fingerprint of the brief's text below the front matter.

    Normalized so that line endings and trailing spaces (which editors change
    without anyone meaning to) do not count as an edit; any change a person
    would call an edit does.
    """
    lines = [ln.rstrip() for ln in body.replace("\r\n", "\n").split("\n")]
    text = "\n".join(lines).strip("\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def split(text: str) -> tuple[str, str, str, str]:
    """(opening fence, front matter, closing fence, body). Raises if none."""
    m = FM_RE.match(text)
    if not m:
        raise ValueError("the brief has no YAML front matter (--- ... ---) at the top")
    return m.group(1), m.group(2), m.group(3), text[m.end():]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Seal a brief that passed the storyline gate.")
    ap.add_argument("--brief", required=True, type=Path)
    args = ap.parse_args(argv)
    p = args.brief
    if not p.exists():
        print(f"ERROR: no brief at {p}")
        return 2
    raw = p.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    try:
        open_f, fm, close_f, body = split(raw)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    kept = [ln for ln in fm.replace("\r\n", "\n").split("\n")
            if ln.split(":", 1)[0].strip() not in GATE_KEYS]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    kept += [f"storyline_gate_passed: true",
             f"storyline_gate_at: {now}",
             f"storyline_gate_sha: {body_fingerprint(body)}"]
    out = open_f + nl.join(kept) + close_f + body
    p.write_bytes(out.encode("utf-8"))
    print(f"[ok] sealed {p.name}: storyline_gate_sha {body_fingerprint(body)}")
    print("     Any edit to the brief below the front matter now needs the gate "
          "re-run and the brief re-sealed before build_deck.py will build it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
