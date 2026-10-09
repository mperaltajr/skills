#!/usr/bin/env python3
"""add_style_refs.py — show the designers what the client's own deck looks like.

Pictures 3-4 good pages from a real client deck and keeps them with a registered
template (<template stem>/style_refs/). Every build then lists them in each
designer's context, with instructions to match the client's visual language
(how they number steps, use icons, draw charts, how dense a page is) without
copying content. Without them, designers have only colors and box positions to
go on, and one client round came back "definitely look Claude generated".

Pick pages that show the client's look at its best: a process page, a chart
page, a dense content page. Not covers or dividers.

Run:
  py -3 scripts/add_style_refs.py --template <registered template.pptx> \
        --from <client deck.pptx> --pages 4,5,33,37
  py -3 scripts/add_style_refs.py --template <...> --list
  py -3 scripts/add_style_refs.py --template <...> --clear
Exit: 0 ok | 2 bad input | 1 render failed
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "slide-qc" / "scripts"))
import _paths as _p  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Add client style-reference pages to a template.")
    ap.add_argument("--template", required=True, type=Path)
    ap.add_argument("--from", dest="source", type=Path, help="The client deck to take pages from.")
    ap.add_argument("--pages", help="Comma-separated page numbers, e.g. 4,5,33,37 (3-4 is best).")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--clear", action="store_true")
    args = ap.parse_args(argv)
    if not args.template.exists():
        print(f"ERROR: template not found: {args.template}")
        return 2
    refs = _p.style_refs_dir(args.template)
    if args.clear:
        shutil.rmtree(refs, ignore_errors=True)
        print(f"[ok] cleared {refs}")
        return 0
    if args.list or not args.source:
        found = sorted(refs.glob("*.png")) if refs.exists() else []
        print(f"{len(found)} style reference(s) in {refs}")
        for f in found:
            print(f"  {f.name}")
        return 0
    if not args.source.exists():
        print(f"ERROR: client deck not found: {args.source}")
        return 2
    try:
        pages = [int(x) for x in (args.pages or "").split(",") if x.strip()]
    except ValueError:
        print("ERROR: --pages takes numbers, e.g. 4,5,33,37")
        return 2
    if not pages:
        print("ERROR: give --pages, e.g. --pages 4,5,33,37")
        return 2
    from render_slides import render as render_default
    with tempfile.TemporaryDirectory() as td:
        try:
            render_default(args.source, Path(td), dpi=96)
        except Exception as exc:
            print(f"ERROR: could not render the deck ({type(exc).__name__}: {exc})")
            return 1
        rendered = {int(p.stem.split("_")[-1]): p for p in Path(td).glob("slide_*.png")}
        refs.mkdir(parents=True, exist_ok=True)
        added = []
        for n in pages:
            if n not in rendered:
                print(f"  WARN: the deck has no page {n} (it has {len(rendered)})")
                continue
            dst = refs / f"{args.source.stem[:40]}_p{n:02d}.png"
            shutil.copyfile(rendered[n], dst)
            added.append(dst.name)
    if not added:
        print("ERROR: no pages added.")
        return 2
    print(f"[ok] {len(added)} style reference(s) in {refs}: {', '.join(added)}")
    print("     Every build on this template now shows them to the designers. "
          "Re-run build_deck.py prep for a build already in progress.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
