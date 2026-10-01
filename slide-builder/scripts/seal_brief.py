#!/usr/bin/env python3
"""seal_brief.py — record that a brief passed storyline-helper's quality gate.

Run this once the gate has passed (every Critical resolved, Majors handled).
It writes three lines into the brief's front matter:

    storyline_gate_passed: true
    storyline_gate_at: <UTC timestamp>
    storyline_gate_sha: <fingerprint of the brief>

The fingerprint covers the whole brief: the front matter (audience, governing
thought, layout...) and the text below it. build_deck.py checks it against the
brief it is given. Before this, the marker was a line anyone could type, so it
certified nothing. Now a typed marker, or any edit after the gate, stops prep
with exit 10.

This script does not run the gate; it records that the gate ran. Running it on
a brief that never went through the gate defeats the point, and the refusal
messages in build_deck.py deliberately do not suggest it. A brief the user
wrote in this session and wants built as-is goes through build_deck.py
--assume-gated instead, which is recorded and shown at delivery.

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


def brief_fingerprint(front_matter: dict, body: str) -> str:
    """Fingerprint of a brief: every front-matter field except the gate's own,
    plus the text below it.

    The front matter must be the dict build_deck.extract_front_matter returns,
    so prep and this script read the brief the same way. Line endings and
    trailing spaces, which editors change without anyone meaning to, do not
    count as edits; any change a person would call an edit does.
    """
    fm = "\n".join(f"{k}={str(v).strip()}" for k, v in sorted(front_matter.items())
                   if k not in GATE_KEYS)
    lines = [ln.rstrip() for ln in body.replace("\r\n", "\n").split("\n")]
    text = "\n".join(lines).strip("\n")
    return hashlib.sha256(f"{fm}\n\x00\n{text}".encode("utf-8")).hexdigest()[:16]


def split(text: str) -> tuple[str, str, str, str]:
    """(opening fence, front matter, closing fence, body). Raises if none."""
    m = FM_RE.match(text)
    if not m:
        raise ValueError("the brief has no YAML front matter (--- ... ---) at the top")
    return m.group(1), m.group(2), m.group(3), text[m.end():]


def _fingerprint_as_prep_reads(text: str) -> str:
    """Fingerprint the brief exactly as build_deck.py will parse it."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_deck import extract_front_matter
    fm, body = extract_front_matter(text.replace("\r\n", "\n").lstrip("﻿"))
    return brief_fingerprint(fm, body)


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

    def _compose(sha: str) -> str:
        lines = kept + ["storyline_gate_passed: true",
                        f"storyline_gate_at: {now}",
                        f"storyline_gate_sha: {sha}"]
        return open_f + nl.join(lines) + close_f + body

    # The gate keys are excluded from the fingerprint, so compose once with a
    # placeholder, fingerprint that as prep will read it, then write the real one.
    sha = _fingerprint_as_prep_reads(_compose("pending"))
    p.write_bytes(_compose(sha).encode("utf-8"))
    print(f"[ok] sealed {p.name}: storyline_gate_sha {sha}")
    print("     Any edit to the brief, front matter included, now needs the gate "
          "re-run and the brief re-sealed before build_deck.py will build it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
