#!/usr/bin/env python3
"""rescale_template.py — resize a 16:9 template to Slide Lab's 1280x720 canvas.

Slide Lab builds every page at 13.333 x 7.5 in (1280 x 720 px). A template
saved at another 16:9 size (10 x 5.625 in, i.e. 960 x 540, is common) gets every
measurement wrong: one session built a whole round of pages against such a
template and threw it away. register_template.py now refuses those templates
and points here.

This writes a resized copy next to the original, "<name> 1280x720.pptx": every
position and size on the masters, layouts and slides is scaled, and so are text
sizes, line widths, text-box insets and point spacing, so the template looks the
same, just bigger. The original is not touched. Then register the copy.

Not 16:9 (4:3, say)? It refuses: scaling would distort the design. Change the
slide size in PowerPoint (Design > Slide Size) and register that.

Run:  py -3 scripts/rescale_template.py <template.pptx>
Exit: 0 written | 0 (nothing to do: already 1280x720) | 2 bad input | 3 not 16:9
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pptx import Presentation

TARGET_W, TARGET_H = 12192000, 6858000      # 13.333 x 7.5 in, 1280 x 720 px

_SCALE_XY = {"off": ("x", "y"), "chOff": ("x", "y"), "ext": ("cx", "cy"), "chExt": ("cx", "cy")}
_INSETS = ("lIns", "tIns", "rIns", "bIns")


def is_canvas_size(w: int, h: int) -> bool:
    return abs(w - TARGET_W) <= 12700 and abs(h - TARGET_H) <= 12700   # within 1 pt


def _scale_part(root, f: float) -> int:
    n = 0
    for el in root.iter():
        tag = el.tag.split("}")[-1] if isinstance(el.tag, str) else ""
        if tag in _SCALE_XY:
            for a in _SCALE_XY[tag]:
                if el.get(a) is not None:
                    el.set(a, str(int(round(int(el.get(a)) * f))))
                    n += 1
        elif tag.endswith("RPr") and el.get("sz") is not None:       # rPr, defRPr, endParaRPr
            el.set("sz", str(max(100, int(round(int(el.get("sz")) * f)))))
            n += 1
        elif tag == "ln" and el.get("w") is not None:
            el.set("w", str(int(round(int(el.get("w")) * f))))
        elif tag == "bodyPr":
            for a in _INSETS:
                if el.get(a) is not None:
                    el.set(a, str(int(round(int(el.get(a)) * f))))
        elif tag == "spcPts" and el.get("val") is not None:
            el.set("val", str(int(round(int(el.get("val")) * f))))
    return n


def rescale(src: Path, dst: Path | None = None) -> Path | None:
    """Write the 1280x720 copy and return its path; None when already the
    right size. Raises ValueError when the template is not 16:9."""
    prs = Presentation(str(src))
    w, h = int(prs.slide_width), int(prs.slide_height)
    if is_canvas_size(w, h):
        return None
    if abs(w / h - TARGET_W / TARGET_H) > 0.01:
        raise ValueError(f"{w / 914400:.3g} x {h / 914400:.3g} in is not 16:9")
    f = TARGET_W / w
    for master in prs.slide_masters:
        _scale_part(master.element, f)
        for layout in master.slide_layouts:
            _scale_part(layout.element, f)
    for slide in prs.slides:
        _scale_part(slide.element, f)
    prs.slide_width, prs.slide_height = TARGET_W, TARGET_H
    dst = dst or src.with_name(f"{src.stem} 1280x720{src.suffix}")
    prs.save(str(dst))
    return dst


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Resize a 16:9 template to 1280x720.")
    ap.add_argument("template", type=Path)
    ap.add_argument("--out", type=Path, help="Where to write (default: '<name> 1280x720.pptx').")
    args = ap.parse_args(argv)
    if not args.template.exists():
        print(f"ERROR: template not found: {args.template}")
        return 2
    try:
        out = rescale(args.template, args.out)
    except ValueError as exc:
        print(f"REFUSED: {exc}. Scaling it would distort the design. Change the slide "
              "size in PowerPoint (Design > Slide Size > Widescreen 16:9), check the "
              "masters, save, and register that file.")
        return 3
    if out is None:
        print("[ok] already 1280x720 (13.333 x 7.5 in); nothing to do.")
        return 0
    print(f"[ok] wrote {out}\n     Register this copy: py -3 scripts/register_template.py propose \"{out}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
