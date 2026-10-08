#!/usr/bin/env python3
"""Smoke test: what the brief says reaches the designer, or prep says why not.

A real brief (2026-10-08) named its deck-wide rules section differently from
"## Deck-level design notes" and wrote each page's source line and section
tag as fields of their own. Prep read none of it and said nothing: every
designer was told "(no deck-level design notes)" and pages went out with no
source. This runs the real prep on a fictional brief and checks:

  1. deck-wide rules under a different heading reach every _prompt.md;
  2. **Source:** and **Section tag:** reach _prompt.md, _context.md and
     _meta.json (kept for the template's Source slot);
  3. a section and a field prep does not read are named in a WARNING in the
     prep output instead of being dropped silently;
  4. the stale "you see the patterns picked for the previous two slides"
     sentence is gone from the prompt.

Run:  py -3 slide-builder/tests/run_brief_fields_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))

import _e2e_harness as H  # noqa: E402
import build_deck as b  # noqa: E402

RULES_RULE = "Every number carries its unit and year"
SOURCE = "Fictional Widget Survey 2026; team analysis"
TAG = "MARKET CONTEXT"

BRIEF_EXTRA = f"""
## Section content rules (binding on every page)
- {RULES_RULE}
- No dashes used as punctuation

## Notes for the photographer
- Something prep has no use for
"""

SLIDE = """
### Slide {n} — Claim number {n} is stated plainly here

**Slide type:** Content
**Section tag:** {tag}
**Governing thought (the claim):** Claim number {n} is stated plainly here.
**The takeaway:** Takeaway {n}.
**Evidence / content:**
- Point one for slide {n}
- Point two for slide {n}
**Mood board:** calm blues
**Source:** {source}
**Chart type:** none
"""


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="brief_fields_"))
    try:
        print("[1] heading variants are read as deck-level design notes")
        for h in ("## Deck-level design notes (optional)", "## Deck-wide content rules",
                  "## Section content rules (binding on every page)", "## Design rules",
                  "## Deck rules", "## Rules (binding on every slide)"):
            assert b.is_deck_notes_heading(h[3:]), h
        for h in ("## Audience", "## Flags — live issues, not historical notes", "## Sequence",
                  "## Notes for the photographer"):
            assert not b.is_deck_notes_heading(h[3:]), h
        print("    ok")

        brief = tmp / "brief.md"
        slides = "".join(SLIDE.format(n=i, tag=TAG, source=SOURCE) for i in (1, 2))
        brief.write_text(H.BRIEF.format(slides=BRIEF_EXTRA + "\n## Sequence\n" + slides),
                         encoding="utf-8")
        r = H.run("seal_brief.py", "--brief", brief, "--accepted", "test brief")
        assert r.returncode == 0, r.stdout + r.stderr
        out = tmp / "out"
        r = H.run("build_deck.py", "--brief", brief, "--template", H.TEMPLATE,
                  "--out", out, "--pattern", "direct", "--confirm-template")
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]

        print("[2] deck-wide rules reach every designer")
        for n in (1, 2):
            p = (out / f"slide_{n:02d}" / "_prompt.md").read_text(encoding="utf-8")
            assert RULES_RULE in p, f"slide {n}: deck rules missing"
            assert "(no deck-level design notes)" not in p
        print("    ok")

        print("[3] source line and section tag reach prompt, context and _meta.json")
        p1 = (out / "slide_01" / "_prompt.md").read_text(encoding="utf-8")
        c1 = (out / "slide_01" / "_context.md").read_text(encoding="utf-8")
        assert f"**Source line:** {SOURCE}" in p1, "source not in _prompt.md"
        assert f"**Section tag:** {TAG}" in p1, "section tag not in _prompt.md"
        assert SOURCE in c1 and TAG in c1, "source / tag not in _context.md"
        meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        s1 = next(s for s in meta["slides"] if s["n"] == 1)
        assert s1.get("source") == SOURCE and s1.get("section_tag") == TAG, s1
        # The source field must not have been swallowed into the evidence.
        ev = b.parse_brief(brief, bypass_gate=True)["slides"][0]["evidence_content"]
        assert SOURCE not in ev, ev
        print("    ok")

        print("[4] unknown section and unknown field are warned about at prep")
        assert "WARNING" in r.stdout and "Notes for the photographer" in r.stdout, r.stdout[-1500:]
        assert "Mood board" in r.stdout and "slide 1, 2" in r.stdout, r.stdout[-1500:]
        # The known sections and fields raise nothing.
        for word in ("Section content rules", "Governing thought", "Sequence", "Section tag",
                     "Source:", "Chart type"):
            assert not any(word in ln for ln in r.stdout.splitlines() if "WARNING" in ln), word
        print("    ok")

        print("[5] the stale prior-patterns sentence is gone")
        assert "patterns picked for the previous two slides" not in p1
        print("    ok")
        print("SMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
