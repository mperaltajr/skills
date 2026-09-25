#!/usr/bin/env python3
"""Smoke test for cover-layout routing and the compile-time layout discard.

Two coupled defects. Either one alone makes the other pointless:

  1. build_deck.resolve_slide_layouts never looked at page_type, so a slide whose
     brief archetype is "Cover" landed on the CONTENT layout and the template's
     branded Cover layout was never used. The deck then needed a hand-built
     cover, and building it outside the pipeline is what orphaned a slide part
     and lost a page number.
  2. compile_picks.copy_picked_slide_into discarded any NON-body-canonical layout
     name and grafted onto the blank layout, so even a correctly routed cover was
     thrown away at compile time. finalize honored the name; compile did not.

Run:  py -3 slide-builder/tests/run_cover_routing_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import inspect
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE))

import run_layout_inheritance_smoke as fixture  # noqa: E402
import _paths as _p  # noqa: E402

BRIEF = """---
client_template: {tpl}
deck_type: test
default_layout: body_canonical_light
storyline_gate_passed: true
---

## Deck-level design notes

Cover-routing fixture.

### Slide 1 — The cover page
**Slide type:** Cover
**Governing thought (the claim):** The cover carries the deck title.
**The takeaway:** The cover carries the deck title.
**Evidence / content:**
- **TITLE** — the deck title sits here.

### Slide 2 — A normal content slide
**Slide type:** Synthesis / Findings
**Governing thought (the claim):** Content slides use the content layout.
**The takeaway:** Content slides use the content layout.
**Evidence / content:**
- **ONE** — first point.
- **TWO** — second point.
"""


def _layouts(out: Path) -> dict[int, str]:
    meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
    return {s["n"]: (s.get("layout") or "") for s in meta["slides"]}


def _page_types(out: Path) -> dict[int, str]:
    meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
    return {s["n"]: (s.get("page_type") or "") for s in meta["slides"]}


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cover_routing_smoke_"))
    try:
        tpl = tmp / fixture.FIXTURE_PPTX.name
        shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        fixture.register_fixture(tpl)

        brief = tmp / "brief.md"
        brief.write_text(BRIEF.format(tpl=tpl), encoding="utf-8")

        print("[1] ambiguous cover names are NOT guessed")
        # The fixture has cover_light AND cover_dark: two candidates, so the
        # name-based fallback must refuse rather than pick the wrong one.
        out0 = tmp / "b0"
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "build_deck.py"), "--brief", str(brief),
             "--template", str(tpl), "--out", str(out0), "--confirm-template"],
            capture_output=True, text=True)
        assert r.returncode == 0, f"build failed:\n{r.stderr[-800:]}"
        assert _page_types(out0)[1] == "cover", "slide 1 should be page_type cover"
        assert "cover routing" not in r.stderr, \
            "two cover candidates must not be auto-guessed"
        print("    ok: refused to guess between cover_light and cover_dark")

        print("[2] a registered cover_layout routes the cover slide")
        theme_path = _p.theme_json(tpl)
        theme = json.loads(theme_path.read_text(encoding="utf-8"))
        theme["cover_layout"] = "cover_light"
        theme_path.write_text(json.dumps(theme, indent=2), encoding="utf-8")

        out1 = tmp / "b1"
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "build_deck.py"), "--brief", str(brief),
             "--template", str(tpl), "--out", str(out1), "--confirm-template"],
            capture_output=True, text=True)
        assert r.returncode == 0, f"build failed:\n{r.stderr[-800:]}"
        lay = _layouts(out1)
        assert lay[1] == "cover_light", f"slide 1 not routed to the cover layout: {lay}"
        assert lay[2] != "cover_light", f"content slide wrongly routed to cover: {lay}"
        assert "cover routing" in r.stderr, "no breadcrumb for the routing decision"
        print(f"    ok: slide 1 -> {lay[1]!r}; slide 2 -> {lay[2]!r}")

        print("[3] an explicit per-slide Layout: still wins over cover routing")
        brief2 = tmp / "brief2.md"
        brief2.write_text(
            BRIEF.format(tpl=tpl).replace(
                "**Slide type:** Cover",
                "**Slide type:** Cover\n**Layout:** body_canonical_light"), encoding="utf-8")
        out2 = tmp / "b2"
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "build_deck.py"), "--brief", str(brief2),
             "--template", str(tpl), "--out", str(out2), "--confirm-template"],
            capture_output=True, text=True)
        assert r.returncode == 0, f"build failed:\n{r.stderr[-800:]}"
        assert _layouts(out2)[1] == "body_canonical_light", \
            f"explicit Layout: must win: {_layouts(out2)}"
        print("    ok: explicit Layout: override respected")

        print("[4] compile no longer discards a non-body-canonical layout name")
        import compile_picks
        src = inspect.getsource(compile_picks.copy_picked_slide_into)
        assert "_is_body_canonical and layout_name" not in src, \
            "compile still gates the named layout on body-canonical"
        assert "_find_named_layout(dst_prs, layout_name) if layout_name else None" in src, \
            "compile does not honor the named layout unconditionally"
        print("    ok: named layout honored for bespoke layouts too")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
