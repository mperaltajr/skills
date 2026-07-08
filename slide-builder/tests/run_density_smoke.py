#!/usr/bin/env python3
"""Smoke test for the content-density directive (Stage 2).

Slides came out too sparse by default. build_deck now threads a per-deck density
directive into every slide's worker prompt (prompt.md {{DENSITY_DIRECTIVE}}):
  - default (all decks): "fill the page — a content slide must be useful on its own";
  - opt-out: front-matter `density: executive` (or sparse/minimal) restores
    headline-led sparseness.

This checks the pure function AND that the directive actually renders into the
per-slide _prompt.md a worker reads.

Run:  py -3 slide-builder/tests/run_density_smoke.py   (python3 on macOS/Linux)
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_layout_inheritance_smoke as fixture
import build_deck


def _brief(tpl: Path, density_line: str = "") -> str:
    fm = (
        f"---\nclient_template: {tpl}\ndeck_type: Training / Enablement\n"
        f"default_layout: body_canonical_light\nmode: template-fill\n{density_line}---\n\n"
        f"## Deck-level design notes\n\nDensity smoke.\n\n"
    )
    body = (
        "## Slide 1 — Alpha\n**Layout:** body_canonical_light\n"
        "**Slide type:** Synthesis / Findings\n**Governing thought:** Alpha claim.\n"
        "**The takeaway:** Alpha takeaway.\n**Evidence:** N/A.\n\n"
    )
    return fm + body


def main() -> int:
    print("[1] density_directive() — default vs opt-out")
    default = build_deck.density_directive({})
    assert "fill the page" in default.lower(), default
    assert "defect" in default.lower(), default
    for d in ("executive", "sparse", "minimal"):
        opt = build_deck.density_directive({"density": d})
        assert "sparse" in opt.lower() and "proof only" in opt.lower(), (d, opt)
    print("    ok: default = fill-the-page; density: executive/sparse/minimal = opt-out")

    tmp = Path(tempfile.mkdtemp(prefix="density_smoke_"))
    try:
        tpl = tmp / fixture.FIXTURE_PPTX.name
        shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        fixture.register_fixture(tpl)

        def _prep(brief_text: str, out: Path) -> None:
            b = tmp / "b.md"
            b.write_text(brief_text, encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(SCRIPTS / "build_deck.py"), "--brief", str(b),
                 "--template", str(tpl), "--out", str(out), "--confirm-template"],
                capture_output=True, text=True,
            )
            assert r.returncode == 0, f"build failed ({r.returncode}):\n{r.stderr[-800:]}"

        print("[2] default brief -> worker prompt carries the fill-the-page directive")
        out1 = tmp / "out_default"
        _prep(_brief(tpl), out1)
        p1 = (out1 / "slide_01" / "_prompt.md").read_text(encoding="utf-8")
        assert "Content density (binding)" in p1, "density header missing from _prompt.md"
        assert "Fill the page" in p1, "default density directive not rendered in _prompt.md"
        print("    ok: _prompt.md has the binding fill-the-page directive")

        print("[3] density: executive brief -> opt-out directive in the prompt")
        out2 = tmp / "out_exec"
        _prep(_brief(tpl, "density: executive\n"), out2)
        p2 = (out2 / "slide_01" / "_prompt.md").read_text(encoding="utf-8")
        assert "Executive / sparse deck" in p2, "executive opt-out not rendered in _prompt.md"
        print("    ok: executive opt-out directive rendered")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
