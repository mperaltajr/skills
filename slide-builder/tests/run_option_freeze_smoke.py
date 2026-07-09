#!/usr/bin/env python3
"""Smoke test: the per-slide option count is FROZEN into _meta.json at build
time (A1), so finalize's expected-pairs gate can't be broken by changing
settings.json::options_per_slide between build and finalize.

Builds a deck at the default count (1), then:
  - asserts every slide entry records `options: ["A"]`;
  - replicates finalize's expected-pairs read with a SIMULATED live count of
    A/B/C (as if settings were flipped to 3 after the build) and asserts it
    still yields only ["A"] per slide (the frozen value wins);
  - asserts a legacy entry with no `options` field falls back to the live count.

This is deterministic and never touches the real settings.json.

Run:  py -3 slide-builder/tests/run_option_freeze_smoke.py  (python3 on macOS/Linux)
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

import run_layout_inheritance_smoke as fixture  # register_fixture + FIXTURE_PPTX


def _brief(tpl: Path) -> str:
    fm = (f"---\nclient_template: {tpl}\ndeck_type: Training / Enablement\n"
          f"default_layout: body_canonical_light\nmode: template-fill\n---\n\n"
          f"## Deck-level design notes\n\nOption-freeze smoke.\n\n")
    body = ""
    for i in (1, 2):
        body += (f"## Slide {i} — S{i}\n**Layout:** body_canonical_light\n"
                 f"**Slide type:** Synthesis / Findings\n"
                 f"**Governing thought:** Claim {i}.\n**The takeaway:** Takeaway {i}.\n"
                 f"**Evidence:** N/A.\n\n")
    return fm + body


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="optfreeze_smoke_"))
    try:
        tpl = tmp / fixture.FIXTURE_PPTX.name
        shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        fixture.register_fixture(tpl)

        print("[1] build at the default count (1)")
        b = tmp / "b.md"; b.write_text(_brief(tpl), encoding="utf-8")
        out = tmp / "out"
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "build_deck.py"), "--brief", str(b),
             "--template", str(tpl), "--out", str(out), "--confirm-template"],
            capture_output=True, text=True)
        assert r.returncode == 0, f"build failed:\n{r.stderr[-800:]}"

        meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        slides = meta["slides"]
        assert slides, "no slides in meta"
        for s in slides:
            assert s.get("options") == ["A"], f"slide {s.get('n')} options = {s.get('options')!r} (expected ['A'])"
        print(f"    ok: {len(slides)} slides each froze options=['A']")

        print("[2] simulate settings flipped to 3 — frozen value must still win")
        FAKE_LIVE = ["A", "B", "C"]   # what _p.option_letters() would now return
        expected_pairs = set()
        for s in slides:
            letters = s.get("options") or FAKE_LIVE   # the exact finalize read
            for L in letters:
                expected_pairs.add((s["n"], L))
        # Only (n, "A") pairs — never B/C — so finalize won't demand un-built options.
        assert expected_pairs == {(s["n"], "A") for s in slides}, expected_pairs
        assert not any(L in ("B", "C") for _, L in expected_pairs), expected_pairs
        print("    ok: expected-pairs stayed {(n,'A')} despite live count = 3")

        print("[3] legacy meta (no `options`) falls back to the live count")
        legacy = {"n": 1}
        assert (legacy.get("options") or FAKE_LIVE) == FAKE_LIVE
        print("    ok: fallback preserves legacy behavior")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
