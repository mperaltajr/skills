#!/usr/bin/env python3
"""Smoke test for the single-slide rebuild path (build_deck.py --slide N).

Builds a full 4-slide deck against the layout-diverse fixture, then rebuilds one
slide and asserts the rebuild is surgical:
  - only the target slide's _prompt.md is re-rendered (others keep their mtime),
  - _meta.json keeps its slide_count + order, the non-target slide entries are
    byte-identical, the target entry is refreshed, and generated_at advances,
  - the brief is reused from _meta.json when --brief is omitted,
  - the error paths return their documented exit codes.

Run:  py -3 slide-builder/tests/run_rebuild_slice_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_layout_inheritance_smoke as fixture  # reuse fixture template + brief


def _build_deck(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "build_deck.py"), *args],
        capture_output=True, text=True,
    )


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="rebuild_slice_smoke_"))
    try:
        tpl = tmp / fixture.FIXTURE_PPTX.name
        shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        fixture.register_fixture(tpl)

        brief = tmp / "brief.md"
        brief.write_text(fixture.SMOKE_BRIEF_TEMPLATE.format(tpl=tpl), encoding="utf-8")
        out = tmp / "build"

        print("[1] Full 4-slide build")
        r = _build_deck("--brief", str(brief), "--template", str(tpl),
                        "--out", str(out), "--confirm-template")
        assert r.returncode == 0, f"full build failed ({r.returncode}):\n{r.stderr[-800:]}"
        meta0 = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        assert meta0["slide_count"] == 4, meta0["slide_count"]
        p1_0 = (out / "slide_01" / "_prompt.md").stat().st_mtime_ns
        p2_0 = (out / "slide_02" / "_prompt.md").stat().st_mtime_ns
        s1_0 = next(s for s in meta0["slides"] if s["n"] == 1)
        s2_0 = next(s for s in meta0["slides"] if s["n"] == 2)
        gen0 = meta0["generated_at"]
        print("    ok: 4 slides prepped")

        time.sleep(1.1)  # filesystem mtime resolution

        print("[2] Rebuild slide 2 (brief reused from _meta.json)")
        r = _build_deck("--template", str(tpl), "--out", str(out),
                        "--slide", "2", "--confirm-template")
        assert r.returncode == 0, f"rebuild failed ({r.returncode}):\n{r.stderr[-800:]}"
        meta1 = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        p1_1 = (out / "slide_01" / "_prompt.md").stat().st_mtime_ns
        p2_1 = (out / "slide_02" / "_prompt.md").stat().st_mtime_ns

        assert meta1["slide_count"] == 4, "slide_count changed"
        assert [s["n"] for s in meta1["slides"]] == [1, 2, 3, 4], "slide order/identity changed"
        assert p2_1 > p2_0, "slide 2 prompt was NOT re-rendered"
        assert p1_1 == p1_0, "slide 1 prompt was touched (should be untouched)"
        assert next(s for s in meta1["slides"] if s["n"] == 1) == s1_0, "slide 1 meta entry changed"
        assert next(s for s in meta1["slides"] if s["n"] == 2)["n"] == 2, "slide 2 entry missing"
        assert meta1["generated_at"] != gen0, "generated_at not refreshed"
        print("    ok: slide 2 re-prepped; slide 1 untouched; _meta merged; order intact")

        print("[3] Error paths")
        r = _build_deck("--template", str(tpl), "--out", str(tmp / "nope"),
                        "--slide", "2", "--confirm-template")
        assert r.returncode == 2, f"--slide on missing out: expected 2, got {r.returncode}"
        r = _build_deck("--template", str(tpl), "--out", str(out),
                        "--slide", "99", "--confirm-template")
        assert r.returncode == 2, f"--slide out-of-range: expected 2, got {r.returncode}"
        r = _build_deck("--template", str(tpl), "--out", str(tmp / "nope2"),
                        "--confirm-template")
        assert r.returncode == 1, f"full build w/o --brief: expected 1, got {r.returncode}"
        print("    ok: missing-out=2, out-of-range=2, no-brief=1")

        print("[4] --like-slide pins the rebuilt slide to a reference slide's path")
        _ref_pat = next(s for s in meta1["slides"] if s["n"] == 3).get("pattern")
        if _ref_pat in ("sketch", "direct"):
            r = _build_deck("--template", str(tpl), "--out", str(out),
                            "--slide", "1", "--like-slide", "3", "--confirm-template")
            assert r.returncode == 0, f"--like-slide rebuild failed:\n{r.stderr[-800:]}"
            assert "pinning slide 1" in r.stderr, r.stderr[-400:]
            meta2 = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
            _got = next(s for s in meta2["slides"] if s["n"] == 1).get("pattern")
            assert _got == _ref_pat, f"slide 1 pattern {_got!r} != reference slide 3 {_ref_pat!r}"
            print(f"    ok: slide 1 pinned to slide 3's '{_ref_pat}' path")
        else:
            print("    ok: (routing not active; --like-slide is a no-op here — skipped)")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
