#!/usr/bin/env python3
"""Smoke test for inserting a slide into an existing build (build_deck.py --insert N).

Builds a 3-slide deck, writes picks, then inserts a new slide at position 2 and
asserts the insert is surgical and correctly renumbered:
  - the deck grows to 4 slides, order 1..4, titles [old1, NEW, old2, old3];
  - only the new slide's dir is freshly prepped; the shifted slides keep their
    built output under their new numbers;
  - picks.json keys shift (>= N move up one; the new slide has no pick yet);
  - error paths (out-of-range N, brief not exactly one slide longer) exit 2.

Run:  py -3 slide-builder/tests/run_insert_slice_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_layout_inheritance_smoke as fixture  # reuse fixture template + registration


def _brief(tpl: Path, titles: list[str]) -> str:
    head = (
        f"---\nclient_template: {tpl}\ndeck_type: Smoke test\n"
        f"default_layout: body_canonical_light\nmode: template-fill\n---\n\n"
        f"## Deck-level design notes\n\nInsert smoke fixture.\n\n"
    )
    body = ""
    for i, title in enumerate(titles, 1):
        body += (
            f"## Slide {i} — {title}\n"
            f"**Layout:** body_canonical_light\n"
            f"**Archetype:** Synthesis / Findings\n"
            f"**Governing thought:** {title} governing thought.\n"
            f"**So-what:** {title} so-what.\n"
            f"**Evidence:** N/A.\n\n"
        )
    return head + body


def _build(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "build_deck.py"), *args],
        capture_output=True, text=True,
    )


def _titles(meta: dict) -> list[str]:
    return [s["title"] for s in sorted(meta["slides"], key=lambda e: e["n"])]


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="insert_slice_smoke_"))
    try:
        tpl = tmp / fixture.FIXTURE_PPTX.name
        shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        fixture.register_fixture(tpl)
        out = tmp / "build"

        print("[1] Full 3-slide build")
        brief3 = tmp / "b3.md"
        brief3.write_text(_brief(tpl, ["Alpha", "Beta", "Gamma"]), encoding="utf-8")
        r = _build("--brief", str(brief3), "--template", str(tpl), "--out", str(out), "--confirm-template")
        assert r.returncode == 0, f"full build failed ({r.returncode}):\n{r.stderr[-800:]}"
        meta0 = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        assert meta0["slide_count"] == 3 and _titles(meta0) == ["Alpha", "Beta", "Gamma"], _titles(meta0)
        # seed picks so we can prove the shift
        (out / "picks.json").write_text(
            json.dumps({"slide_01": "A", "slide_02": "B", "slide_03": "C"}), encoding="utf-8")
        print("    ok: 3 slides [Alpha, Beta, Gamma] + picks A/B/C")

        print("[2] Insert a new slide at position 2")
        brief4 = tmp / "b4.md"
        brief4.write_text(_brief(tpl, ["Alpha", "INSERTED", "Beta", "Gamma"]), encoding="utf-8")
        r = _build("--brief", str(brief4), "--template", str(tpl), "--out", str(out),
                   "--insert", "2", "--confirm-template")
        assert r.returncode == 0, f"insert failed ({r.returncode}):\n{r.stderr[-800:]}"
        meta1 = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        assert meta1["slide_count"] == 4, meta1["slide_count"]
        assert [s["n"] for s in sorted(meta1["slides"], key=lambda e: e["n"])] == [1, 2, 3, 4]
        assert _titles(meta1) == ["Alpha", "INSERTED", "Beta", "Gamma"], _titles(meta1)
        assert (out / "slide_02" / "_prompt.md").exists(), "new slide 2 not prepped"
        assert (out / "slide_04").is_dir(), "shifted slide 4 dir missing"
        picks = json.loads((out / "picks.json").read_text(encoding="utf-8"))
        assert picks == {"slide_01": "A", "slide_03": "B", "slide_04": "C"}, picks
        print("    ok: 4 slides [Alpha, INSERTED, Beta, Gamma]; picks shifted A/-/B/C")

        print("[3] Error paths")
        r = _build("--brief", str(brief4), "--template", str(tpl), "--out", str(out),
                   "--insert", "9", "--confirm-template")
        assert r.returncode == 2, f"out-of-range insert: expected 2, got {r.returncode}"
        # brief not exactly one longer than the current 4-slide build
        r = _build("--brief", str(brief3), "--template", str(tpl), "--out", str(out),
                   "--insert", "2", "--confirm-template")
        assert r.returncode == 2, f"count-mismatch insert: expected 2, got {r.returncode}"
        print("    ok: out-of-range=2, count-mismatch=2")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
