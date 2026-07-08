#!/usr/bin/env python3
"""Smoke test for the normalized build-copy resolver (Stage 3A plumbing).

Registration saves a normalized copy at <stem>/build-template.pptx and records
it in theme.json::build_template_path; builds open that copy while sidecars stay
keyed off the original stem. This verifies twins.client_theme.resolve_build_template:
  - a registered template resolves to its build copy;
  - the rail: handed the copy itself (a path inside a sidecar dir), it returns it
    unchanged rather than re-resolving off a phantom sidecar folder;
  - fallback: a missing copy resolves back to the original;
  - legacy: a template with no build_template_path resolves to the original.

Run:  py -3 slide-builder/tests/run_build_template_resolve_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_layout_inheritance_smoke as fixture  # reuse fixture template + registration
import _paths as _p
from twins.client_theme import resolve_build_template


def _same(a: Path, b: Path) -> bool:
    """Compare paths by resolved form (Windows 8.3 short names vs long names)."""
    return a.resolve() == b.resolve()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="build_resolve_smoke_"))
    try:
        tpl = tmp / fixture.FIXTURE_PPTX.name
        shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        fixture.register_fixture(tpl)  # writes sidecars + build-template.pptx
        copy = _p.build_template_pptx(tpl)

        print("[1] Registered template resolves to its build copy")
        assert copy.exists(), f"registration did not create the build copy: {copy}"
        r = resolve_build_template(tpl)
        assert _same(r, copy), f"expected {copy}, got {r}"
        print("    ok: resolves to build-template.pptx")

        print("[2] Rail: the copy itself resolves to itself (no re-resolve)")
        r2 = resolve_build_template(copy)
        assert _same(r2, copy), f"rail failed: {r2}"
        print("    ok: path inside a sidecar dir returned unchanged")

        print("[3] Fallback: a missing copy resolves back to the original")
        copy.unlink()
        r3 = resolve_build_template(tpl)
        assert _same(r3, tpl), f"expected fallback to {tpl}, got {r3}"
        print("    ok: missing copy -> original template")

        print("[4] Legacy: no build_template_path -> original template")
        theme_path = _p.theme_json(tpl)
        data = json.loads(theme_path.read_text(encoding="utf-8"))
        data["build_template_path"] = ""
        theme_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        r4 = resolve_build_template(tpl)
        assert _same(r4, tpl), f"expected {tpl}, got {r4}"
        print("    ok: un-normalized template -> original")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
