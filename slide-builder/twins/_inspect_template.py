"""Inspect a client PPTX template: theme colors, fonts, and layouts.

Usage:
    python -m twins._inspect_template "path/to/template.pptx"
"""
import re
import sys
from pathlib import Path
from pptx import Presentation


def inspect(template_path: str):
    p = Presentation(template_path)

    # Theme XML lives in the package's theme part. Find it via the package iter.
    theme_xml = None
    for part in p.part.package.iter_parts():
        pn = part.partname.lower()
        if pn.endswith("theme1.xml") or "/theme/theme" in pn:
            theme_xml = part.blob.decode("utf-8", errors="replace")
            break

    print(f"\n=== {Path(template_path).name} ===\n")
    print(f"Slide size: {p.slide_width/914400:.3f}\" x {p.slide_height/914400:.3f}\"")
    print(f"Masters: {len(p.slide_masters)}")

    # Theme colors
    if theme_xml:
        cs = re.search(r"<a:clrScheme[^>]*>(.*?)</a:clrScheme>", theme_xml, re.DOTALL)
        if cs:
            print("\nTheme colors:")
            # named blocks: dk1, lt1, dk2, lt2, accent1..6, hlink, folHlink
            order = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3",
                     "accent4", "accent5", "accent6", "hlink", "folHlink"]
            block_text = cs.group(1)
            for name in order:
                m = re.search(rf"<a:{name}>(.*?)</a:{name}>", block_text, re.DOTALL)
                if not m:
                    continue
                inner = m.group(1)
                srgb = re.search(r'srgbClr\s+val="([0-9A-Fa-f]{6})"', inner)
                sysc = re.search(r'sysClr[^/>]*lastClr="([0-9A-Fa-f]{6})"', inner)
                color = srgb.group(1) if srgb else (sysc.group(1) if sysc else "?")
                print(f"  {name:10s} #{color}")
        # Fonts
        fs = re.search(r"<a:fontScheme[^>]*>(.*?)</a:fontScheme>", theme_xml, re.DOTALL)
        if fs:
            print("\nTheme fonts:")
            for kind in ("majorFont", "minorFont"):
                m = re.search(rf"<a:{kind}>(.*?)</a:{kind}>", fs.group(1), re.DOTALL)
                if not m:
                    continue
                latin = re.search(r'<a:latin\s+typeface="([^"]+)"', m.group(1))
                print(f"  {kind:10s} {latin.group(1) if latin else '?'}")

    # Layouts per master
    print("\nLayouts:")
    for mi, m in enumerate(p.slide_masters):
        print(f"  Master {mi} ({len(m.slide_layouts)} layouts):")
        for li, l in enumerate(m.slide_layouts):
            n_shapes = len(l.shapes)
            print(f"    {mi}.{li:2d}  {l.name!r}   shapes={n_shapes}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m twins._inspect_template <path-to-pptx>")
        sys.exit(1)
    inspect(sys.argv[1])
