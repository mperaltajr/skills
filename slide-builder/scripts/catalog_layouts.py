"""
catalog_layouts.py — Dump every layout across every slide master of a template.

Usage:
    python catalog_layouts.py <template.pptx>
    python catalog_layouts.py <template.pptx> --json out.json
    python catalog_layouts.py <template.pptx> --pick blank
    python catalog_layouts.py <template.pptx> --pick "title slide"

Without --pick, prints a sorted table of every layout: master idx, layout idx,
shape count, has_picture flag, layout name. Use this to verify which layout the
builder will select for a given template, and to spot which masters carry
decorative imagery you don't want bleeding into content slides.

With --pick <name>, runs get_named_layout (or get_blank_layout for 'blank') and
reports which layout the builder will choose. Use this when debugging "the cover
photo is bleeding through" — confirm the picked layout is on a clean master.
"""
import sys
import json
import argparse
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "patches"))

from patches import (
    _iter_all_layouts,
    _layout_or_master_has_picture,
    catalog_layouts,
    get_blank_layout,
    get_named_layout,
)
from pptx import Presentation

p = argparse.ArgumentParser()
p.add_argument("pptx", help="template PPTX path")
p.add_argument("--json", help="write JSON output to this path")
p.add_argument("--pick", help="if set, also report which layout get_named_layout (or get_blank_layout for 'blank') selects")
args = p.parse_args()

prs = Presentation(args.pptx)
catalog = catalog_layouts(prs)

print(f"Template: {args.pptx}")
print(f"Slide size: {prs.slide_width.inches:.2f} x {prs.slide_height.inches:.2f} in")
print(f"Masters: {len(prs.slide_masters)}")
print(f"Total layouts: {len(catalog)}")
print()
print(f"{'M':>2}.{'L':<2}  {'SHAPES':>6}  {'PIC':>3}  NAME")
print("-" * 80)
for entry in catalog:
    pic = "YES" if entry["has_picture"] else "no"
    print(f"{entry['master_idx']:>2}.{entry['layout_idx']:<2}  {entry['shape_count']:>6}  {pic:>3}  {entry['name']}")

if args.json:
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
    print(f"\nJSON written: {args.json}")

if args.pick:
    print()
    print(f"=== get_layout('{args.pick}') ===")
    if args.pick.lower() == "blank":
        picked = get_blank_layout(prs)
    else:
        picked = get_named_layout(prs, args.pick)
    # Locate the picked layout's master + layout indices
    for mi, li, layout in _iter_all_layouts(prs):
        if layout is picked:
            has_pic = _layout_or_master_has_picture(layout)
            print(f"Picked: master {mi}, layout {li}, name='{layout.name}', shapes={len(layout.shapes)}, has_picture={has_pic}")
            if has_pic:
                print(f"  WARNING: picked layout has decorative imagery on layout or master — content slides will inherit it")
            break
    else:
        print("Picked layout not found in catalog (unexpected)")
