#!/usr/bin/env python3
"""Smoke test for the machine-local template registry (_registry.py).

Proves the pick-list index works without touching the user's real registry:
  - a missing registry reads as an empty skeleton (never raises);
  - an entry built from a template's theme.json sidecar carries the right fields
    (incl. build_template_path defaulting to the template path);
  - add_or_update is insert-or-replace (idempotent — no duplicates);
  - reconcile() prunes entries whose files vanished; and
  - reconcile() rediscovers sidecar bundles under the scan roots (so the index
    self-heals / effectively follows the user across machines).

Both the registry path and the disk-scan roots are monkeypatched to a temp dir,
so this never reads or writes the real ~/.claude/slide_lab_registry.json.

Run:  py -3 slide-builder/tests/run_registry_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_layout_inheritance_smoke as fixture  # reuse fixture template + registration
import _registry
import _contract


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="registry_smoke_"))
    # Isolate: redirect the registry file + the disk-scan roots into the temp dir
    # so the real user registry is never read or written.
    _registry.REGISTRY_PATH = tmp / "slide_lab_registry.json"
    scan_root = tmp / "scanroot"
    _contract._registered_template_search_roots = lambda: (scan_root,)
    try:
        # Lay a fixture template + its sidecars under the scan root.
        proj = scan_root / "proj"
        proj.mkdir(parents=True)
        tpl = proj / fixture.FIXTURE_PPTX.name
        shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        fixture.register_fixture(tpl)  # writes brand.yml + theme.json + chrome.yml
        key = str(tpl.resolve()).casefold()

        print("[1] Missing registry reads as an empty skeleton")
        reg = _registry.load_registry()
        assert reg["templates"] == [], reg
        assert reg["schema_version"] == _registry.REGISTRY_SCHEMA_VERSION
        print("    ok: empty skeleton, no raise")

        print("[2] Entry from theme.json + add_or_update")
        entry = _registry._entry_from_template(tpl)
        assert entry is not None, "sidecar present but entry came back None"
        assert _registry._key(entry["template_path"]) == key
        # Registration now records the normalized build copy as build_template_path.
        btp = Path(entry["build_template_path"])
        assert btp.name == "build-template.pptx", entry["build_template_path"]
        assert btp.exists(), f"build copy not created: {btp}"
        assert len(entry["template_sha8"]) == 8, entry["template_sha8"]
        assert entry["brand_primary_hex"], "brand primary not captured"
        _registry.add_or_update(entry)
        got = _registry.load_registry()["templates"]
        assert len(got) == 1 and _registry._key(got[0]["template_path"]) == key, got
        print("    ok: 1 entry, fields populated, build_template_path -> build copy")

        print("[3] add_or_update is idempotent (no duplicates)")
        _registry.add_or_update(_registry._entry_from_template(tpl))
        assert len(_registry.load_registry()["templates"]) == 1
        print("    ok: still 1 entry after re-add")

        print("[4] reconcile() prunes a vanished entry, keeps the real one")
        _registry.add_or_update({"template_path": str(tmp / "ghost.pptx"),
                                 "display_name": "Ghost — ghost"})
        assert len(_registry.load_registry()["templates"]) == 2
        _registry.reconcile()
        after = _registry.load_registry()["templates"]
        assert len(after) == 1, [t["template_path"] for t in after]
        assert _registry._key(after[0]["template_path"]) == key
        print("    ok: ghost pruned, real template retained")

        print("[5] reconcile() rediscovers a sidecar bundle into an empty index")
        _registry.REGISTRY_PATH.unlink()  # start from nothing
        assert _registry.load_registry()["templates"] == []
        _registry.reconcile()
        red = _registry.load_registry()["templates"]
        assert len(red) == 1 and _registry._key(red[0]["template_path"]) == key, red
        print("    ok: template rediscovered from disk")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
