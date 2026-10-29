#!/usr/bin/env python3
"""Smoke test: the committed tutorial is exactly what its source builds.

Slide-Lab-Tutorial.html is built from docs/tutorial/tutorial_src.html by
docs/tutorial/assemble.py. By 2026-10-23 several builders had edited the
built page directly, so the source was stale: rebuilding brought back
"3 options per slide" and dropped the "+3 DESIGNS" wording. The tutorial is
public, so it must also come from the published settings.json only, never
from the owner's settings.local.json (three designs per slide).

  1. assemble.py, with a settings.local.json that says 3 designs per slide,
     writes a page byte-identical to the committed Slide-Lab-Tutorial.html
     (a difference means the built page was edited by hand: carry the edit
     into tutorial_src.html and rebuild)
  2. check_tutorial.py passes on the committed page with and without that
     local file
  3. a page whose facts say 3 designs per slide fails the check (it compares
     with settings.json, which says 1)

Run:  py -3 slide-builder/tests/run_tutorial_build_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401  (temp folders under the scratch root, deleted at exit)

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
ROOT = SKILL.parent
ASSEMBLE = ROOT / "docs" / "tutorial" / "assemble.py"
CHECK = SKILL / "scripts" / "check_tutorial.py"
TUTORIAL = ROOT / "Slide-Lab-Tutorial.html"
SETTINGS = SKILL / "settings.json"


def _run(args: list[str], env: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="tutorial_build_"))
    published = json.loads(SETTINGS.read_text(encoding="utf-8"))
    local = tmp / "settings.local.json"
    local.write_text(json.dumps({"options_per_slide": 3}), encoding="utf-8")
    with_local = {**os.environ, "SLIDE_LAB_SETTINGS_LOCAL": str(local)}
    without_local = {**os.environ, "SLIDE_LAB_SETTINGS_LOCAL": "none"}

    print("1. assemble.py rebuilds the committed tutorial exactly")
    built = tmp / "Slide-Lab-Tutorial.html"
    r = _run([str(ASSEMBLE), "--out", str(built)], with_local)
    assert r.returncode == 0, r.stdout + r.stderr
    new, old = built.read_bytes(), TUTORIAL.read_bytes()
    if new != old:
        a, b = new.decode("utf-8").splitlines(), old.decode("utf-8").splitlines()
        diff = [i for i in range(max(len(a), len(b)))
                if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)]
        raise AssertionError(
            f"assemble.py output differs from the committed Slide-Lab-Tutorial.html "
            f"on line(s) {', '.join(str(i + 1) for i in diff[:10])}. Someone edited the "
            f"built page by hand: make the same edit in docs/tutorial/tutorial_src.html, "
            f"then run py -3 docs/tutorial/assemble.py")
    print("    ok: byte-identical, with a local file saying 3 designs per slide")

    print("2. check_tutorial.py passes with and without the local file")
    for label, env in (("with", with_local), ("without", without_local)):
        r = _run([str(CHECK), "--tutorial", str(TUTORIAL)], env)
        assert r.returncode == 0, f"{label} the local file:\n{r.stdout}{r.stderr}"
    print("    ok: both pass")

    print("3. a page that says 3 designs per slide fails the check")
    assert published.get("options_per_slide") != 3, "settings.json now says 3; pick another number"
    page = TUTORIAL.read_text(encoding="utf-8")
    key = f'"options_per_slide": {published.get("options_per_slide")},'
    assert page.count(key) == 1, f"facts block line {key} not found once"
    wrong = tmp / "wrong.html"
    wrong.write_text(page.replace(key, '"options_per_slide": 3,'), encoding="utf-8", newline="\n")
    r = _run([str(CHECK), "--tutorial", str(wrong)], with_local)
    assert r.returncode == 1 and "options_per_slide" in r.stdout, r.stdout + r.stderr
    print("    ok: the check names options_per_slide")

    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
