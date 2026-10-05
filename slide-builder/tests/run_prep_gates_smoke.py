#!/usr/bin/env python3
"""Smoke test: the two prep gates are proven, not self-certified.

Owner's decisions (2026-09-30):
  3. An unconfirmed template STOPS the build (exit 12). It used to print a
     warning and carry on while the docs said it stopped. The override is
     --allow-unconfirmed, and it is recorded in the build's _state.json.
     The yes/no prompt is gone: nobody can answer it from inside Claude Code,
     so it always aborted and --confirm-template became a reflex.
  4. The storyline gate marker must be SEALED by seal_brief.py, which writes a
     fingerprint of the brief's text. A typed marker has none; an edited brief
     no longer matches. Both stop prep (exit 10). A brief written in-session is
     built with --assume-gated, recorded in _state.json.

Run:  py -3 slide-builder/tests/run_prep_gates_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))

import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402
import run_layout_inheritance_smoke as fixture  # noqa: E402


def _prep(brief, tpl, out, *extra):
    return H.run("build_deck.py", "--brief", brief, "--template", tpl, "--out", out,
                 "--pattern", "direct", *extra)


def _overrides(out):
    return [o["override"] for o in _state.read_state(out).get("overrides", [])]


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="prep_gates_"))
    try:
        brief = tmp / "brief.md"
        brief.write_text(H.BRIEF.format(slides=H.SLIDE.format(n=1)), encoding="utf-8")

        print("[D4] a typed gate marker is refused")
        r = _prep(brief, H.TEMPLATE, tmp / "o1")
        assert r.returncode == 10 and "never sealed" in r.stderr, r.stderr[-600:]
        print("    ok: exit 10, 'never sealed'")

        print("[D4] a sealed brief builds; the old --confirm-template still works")
        assert H.run("seal_brief.py", "--brief", brief, "--accepted", "test brief").returncode == 0
        r = _prep(brief, H.TEMPLATE, tmp / "o2", "--confirm-template")
        assert r.returncode == 0, r.stderr[-800:]
        print("    ok")

        print("[D4] line endings changing does not count as an edit")
        raw = brief.read_bytes()
        brief.write_bytes(raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        assert _prep(brief, H.TEMPLATE, tmp / "o3").returncode == 0
        print("    ok")

        print("[D4] editing the brief after the gate is refused")
        text = brief.read_text(encoding="utf-8")
        brief.write_text(text.replace("Point two for slide 1", "A new claim"),
                         encoding="utf-8")
        r = _prep(brief, H.TEMPLATE, tmp / "o4")
        assert r.returncode == 10 and "changed after it passed" in r.stderr, r.stderr[-600:]
        print("    ok: exit 10, 'changed after it passed'")

        print("[D4] --assume-gated builds it and says so in the record")
        r = _prep(brief, H.TEMPLATE, tmp / "o5", "--assume-gated")
        assert r.returncode == 0, r.stderr[-800:]
        assert "assume_gated" in _overrides(tmp / "o5"), _overrides(tmp / "o5")
        print("    ok")

        print("[D3] an unconfirmed template stops the build")
        assert H.run("seal_brief.py", "--brief", brief, "--accepted", "test brief").returncode == 0
        tpl = tmp / "unconfirmed.pptx"
        shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        fixture.register_fixture(tpl, confirm=False)
        r = _prep(brief, tpl, tmp / "o6", "--confirm-template")
        assert r.returncode == 12 and "confirmed by a human" in r.stderr, (
            f"exit {r.returncode}: an unconfirmed template must stop the build, even "
            f"with the old --confirm-template flag\n{r.stderr[-600:]}")
        assert "Proceed with this template? [y/N]" not in r.stdout
        print("    ok: exit 12; no prompt")

        print("[D3] --allow-unconfirmed builds it and says so in the record")
        r = _prep(brief, tpl, tmp / "o7", "--allow-unconfirmed")
        assert r.returncode == 0, r.stderr[-800:]
        assert "allow_unconfirmed" in _overrides(tmp / "o7"), _overrides(tmp / "o7")
        print("    ok")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
