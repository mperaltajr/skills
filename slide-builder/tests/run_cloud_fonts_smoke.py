#!/usr/bin/env python3
"""Smoke test: Office cloud fonts (Aptos and the like) are found and picked right.

Office downloads Aptos, Aptos Display and other cloud fonts into
%LOCALAPPDATA%\\Microsoft\\FontCache\\<n>\\CloudFonts\\<Family>\\<number>.ttf,
never into the Windows font folders. Registration looked only there, printed
"brand title font not resolved on this machine; title-fit measurement
skipped", and titles on Aptos templates were never checked (2026-10-14).

Aptos Display's faces also give "Aptos" as their typographic family, so once
the folder is read, a search for "Aptos" could pick Aptos Display.

On a made-up LOCALAPPDATA with numbered font files laid out like Office's:
  1. _font_index() lists every cloud file, even two with the same number in
     different family folders
  2. pick_family_faces("Aptos") picks Aptos Regular and Aptos Bold, not the
     Aptos Display faces that share the typographic family
  3. pick_family_faces("Aptos Display") picks the Aptos Display faces
  4. bold_ttf_for() finds Aptos Display Bold from Aptos Display Regular, and
     Aptos Bold from Aptos Regular

Run:  py -3 slide-builder/tests/run_cloud_fonts_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(HERE))

from _fake_fonts import make_font  # noqa: E402
import _chrome_schema as CS  # noqa: E402


def main() -> None:
    local = Path(tempfile.mkdtemp())
    cloud = local / "Microsoft" / "FontCache" / "4" / "CloudFonts"
    aptos, display = cloud / "Aptos", cloud / "Aptos Display"
    aptos.mkdir(parents=True)
    display.mkdir(parents=True)
    # Named as Office names them (numbers); the Display files sort first by
    # path, which is the tie the old pick lost. "111.ttf" exists twice.
    reg = make_font(aptos / "30153066857.ttf", family="Aptos", style="Regular",
                    typo_family="Aptos", typo_style="Regular", weight=400)
    bold = make_font(aptos / "32483553004.ttf", family="Aptos", style="Bold",
                     typo_family="Aptos", typo_style="Bold", weight=700)
    make_font(aptos / "111.ttf", family="Aptos Light", style="Regular",
              typo_family="Aptos", typo_style="Light", weight=300)
    d_reg = make_font(display / "30169865670.ttf", family="Aptos Display",
                      style="Regular", typo_family="Aptos", typo_style="Display",
                      weight=400, scale=1.1)
    d_bold = make_font(display / "111.ttf", family="Aptos Display", style="Bold",
                       typo_family="Aptos", typo_style="Display Bold", weight=700,
                       scale=1.1)

    os.environ["LOCALAPPDATA"] = str(local)
    CS._font_index.cache_clear()
    CS._FACES_MEM.clear()

    found = {os.path.normcase(p) for p in CS._font_index().values()}
    for p in (reg, bold, d_reg, d_bold, aptos / "111.ttf"):
        assert os.path.normcase(str(p)) in found, f"cloud font not indexed: {p}"
    print("  ok: every numbered cloud font file is indexed (same number in two folders too)")

    hit = CS.pick_family_faces("Aptos")
    assert os.path.normcase(hit["regular"]) == os.path.normcase(str(reg)), hit["regular"]
    assert os.path.normcase(hit["bold"]) == os.path.normcase(str(bold)), hit["bold"]
    print("  ok: 'Aptos' -> Aptos Regular + Aptos Bold, not Aptos Display")

    hit = CS.pick_family_faces("Aptos Display")
    assert os.path.normcase(hit["regular"]) == os.path.normcase(str(d_reg)), hit["regular"]
    assert os.path.normcase(hit["bold"]) == os.path.normcase(str(d_bold)), hit["bold"]
    print("  ok: 'Aptos Display' -> the Aptos Display faces")

    assert os.path.normcase(CS.bold_ttf_for(str(d_reg)) or "") == os.path.normcase(str(d_bold))
    assert os.path.normcase(CS.bold_ttf_for(str(reg)) or "") == os.path.normcase(str(bold))
    print("  ok: bold_ttf_for keeps Display with Display and Aptos with Aptos")

    print("SMOKE PASSED.")


if __name__ == "__main__":
    main()
