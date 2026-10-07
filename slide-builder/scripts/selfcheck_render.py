#!/usr/bin/env python3
"""selfcheck_render.py — render ONE option's drawn slide for the translator's self-check.

The translator agent used to render into the slide folder itself and rename
the renderer's `slide_01.png`. Two agents converting options B and C of the
same slide at the same time wrote the same `slide_01.png`, so one option was
checked against the other's picture: in one build option_B_native.png and
option_C_native.png were byte-identical although the designs differed
(2026-10-06). This renders each option into its own folder
(`slide_NN/_render_tmp/option_X_native/`), so no other option can touch it,
and copies the result to `option_X_native.png`.

It then runs the arrow-end check on the drawn slide (scripts/arrow_ends.py)
and records what it finds in `option_X_translation_report.json`.

LibreOffice only: it never falls back to PowerPoint.

Run:
  py -3 scripts/selfcheck_render.py <slide_dir>/option_X_native.pptx
Exit 0 = rendered, no arrowhead at a box; 1 = rendered, arrowhead(s) at a box
(listed: fix them and run again); 2 = could not render.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SKILL.parent / "slide-qc" / "scripts"))

import _paths as _p  # noqa: E402

DPI = 96


def render_option(pptx: Path, dpi: int = DPI) -> Path:
    """Render pptx's first slide into its own folder; return option_X_native.png."""
    import render_slides as RS
    RS.SOFFICE = RS._resolve_soffice()      # raises if LibreOffice is missing: no PowerPoint
    folder = _p.render_tmp_dir(pptx)
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True, exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        RS.render_libre(pptx.resolve(), folder.resolve(), dpi)
    got = folder / "slide_01.png"
    if not got.exists():
        raise RuntimeError(f"the render produced no slide_01.png in {folder}")
    png = pptx.with_suffix(".png")
    shutil.copyfile(got, png)
    return png


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render one option for the translator's self-check.")
    ap.add_argument("pptx", type=Path, help="slide_NN/option_X_native.pptx")
    ap.add_argument("--dpi", type=int, default=DPI)
    args = ap.parse_args(argv)
    pptx = args.pptx.resolve()
    if not pptx.exists():
        print(f"ERROR: {pptx} not found")
        return 2
    try:
        png = render_option(pptx, args.dpi)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not render {pptx.name}: {type(exc).__name__}: {exc}")
        return 2
    print(f"[ok] rendered {pptx.name} -> {png}")
    import arrow_ends as AE
    hits = AE.check_pptx(pptx)
    letter = pptx.stem.split("_")[1] if pptx.stem.startswith("option_") else None
    report = pptx.parent / f"option_{letter}_translation_report.json" if letter else None
    if report is not None and report.exists():
        AE.merge_into_report(report, hits)
    if not hits:
        print(f"[ok] arrow ends: no arrowhead within {AE.GAP_PX:.0f} px of a box")
        return 0
    print(f"ARROW ENDS: {len(hits)} arrowhead(s) at a box. Move each end back so it "
          f"stops at least {AE.GAP_PX + 2:.0f} px short of the box, then run this again:")
    for h in hits:
        print("  - " + AE.describe(h))
    return 1


if __name__ == "__main__":
    sys.exit(main())
