#!/usr/bin/env python3
"""Smoke test for the settings-driven option count (Stage 3).

Default is ONE design option per slide (settings.json::options_per_slide, default 1);
the reviewer requests more only where wanted. This checks the option-letter helper
across counts. The end-to-end "the prompt asks for one option" assertion lives in
run_density_smoke.py (which already builds a default deck).

Run:  py -3 slide-builder/tests/run_options_smoke.py   (python3 on macOS/Linux)
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _paths as _p


def main() -> int:
    print("[1] default option count = 1")
    assert _p.options_per_slide() >= 1, _p.options_per_slide()
    default = _p.option_letters()
    assert default == ("A",), f"expected one option by default, got {default}"
    print(f"    ok: option_letters() = {default}")

    print("[2] count is honored + clamped to A/B/C")
    assert _p.option_letters(3) == ("A", "B", "C"), _p.option_letters(3)
    assert _p.option_letters(2) == ("A", "B"), _p.option_letters(2)
    assert _p.option_letters(0) == ("A",), "count < 1 must clamp to 1"
    assert _p.option_letters(9) == ("A", "B", "C"), "count > 3 must clamp to 3"
    print("    ok: 3 -> A/B/C, 2 -> A/B, clamps 0->1 and 9->3")

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
