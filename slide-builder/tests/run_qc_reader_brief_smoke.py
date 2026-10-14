#!/usr/bin/env python3
"""Smoke test: the QC reader agent's brief (qc_reader.py, owner's decision
2026-10-14, speed verdict Q2 C). Made-up content.

  1. the filled brief names the round's pages, the notes file, the record
     command, every approved headline, the rules (no person attribution,
     type rules) and the deck's rulings file when there is one
  2. no placeholder is left; without a rulings file it says none recorded
  3. the hand-off lines tell the main chat to dispatch a fresh agent and not
     to read the pages itself

Run:  py -3 slide-builder/tests/run_qc_reader_brief_smoke.py
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import qc_reader as R  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        (out / "_session").mkdir()
        brief = out / "_session" / "narrative-brief-acme.md"
        brief.write_text("# Acme\n", encoding="utf-8")
        (out / "_meta.json").write_text(json.dumps({"brief": str(brief), "slides": [
            {"n": 1, "title": "Acme cuts churn 38% by fixing onboarding", "page_type": "cover"},
            {"n": 2, "title": "Churn | jumped in Q3", "page_type": "content"}]}),
            encoding="utf-8")
        plan = {"read_pages": [1, 2], "sheets": [{"file": "sheet_01.png"}], "pairs": []}

        print("[1] without a rulings file")
        dest = R.write(out, out / "Acme.pptx", plan)
        t = dest.read_text(encoding="utf-8")
        assert dest == out / "_qc" / "reader_brief.md"
        assert "{{" not in t and "<!--" not in t, t[:400]
        assert "none recorded for this deck" in t
        assert "| 1 | Acme cuts churn 38% by fixing onboarding |" in t
        assert "| 2 | Churn / jumped in Q3 |" in t, "a | in a headline must not break the table"
        for must in ("ONE page at a time", "No person attribution", "10.5 pt",
                     "record_vision_qc.py", "page_notes.json", str(brief),
                     "slide N [category] Severity:", "Under 40 lines", "never\nclose",
                     "1, 2"):
            assert must.replace("\n", " ") in t.replace("\n", " "), must
        print("    ok")

        print("[2] with a rulings file")
        (out / "_session" / "rulings.md").write_text("- deck: keep v3.1 financials\n",
                                                     encoding="utf-8")
        t = R.write(out, out / "Acme.pptx", plan).read_text(encoding="utf-8")
        assert str(out / "_session" / "rulings.md") in t and "none recorded" not in t
        print("    ok")

        print("[3] the hand-off")
        lines = "\n".join(R.handoff_lines(dest))
        assert "FRESH reader agent" in lines and "Do not read the pages" in lines, lines
        assert str(dest) in lines
        print("    ok")
    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
