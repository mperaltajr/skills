#!/usr/bin/env python3
"""Export PPTX slides to PNG using PowerPoint itself (Windows + Office required).

Safe while the user has PowerPoint open (ppt_safe.py): the deck is opened
read-only without a window, only that deck is closed, and PowerPoint is quit
only if this script started it and nothing else is open in it. It never
closes, saves or touches another presentation.

Usage:
    py -3 export_slides.py <path/to/deck.pptx> [--out <output_dir>] [--width 1920]

Output:
    slide_01.png, slide_02.png, ... in <output_dir> (default: <pptx_dir>/_qc/)
    Prints one line per slide on success. Exits 1 on failure.
"""

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def export_via_powerpoint(pptx_path: pathlib.Path, out_dir: pathlib.Path, width: int = 1920):
    try:
        import win32com.client  # noqa: F401
    except ImportError:
        print("ERROR: pywin32 not installed.", file=sys.stderr)
        print("  Run: pip install pywin32", file=sys.stderr)
        sys.exit(1)
    import ppt_safe
    try:
        count = ppt_safe.export_pngs(pptx_path, out_dir, width)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    for i in range(1, count + 1):
        print(f"  slide {i:02d}/{count}: {out_dir / f'slide_{i:02d}.png'}")
    print(f"OK {count} slides -> {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Export PPTX slides to PNG via PowerPoint")
    parser.add_argument("pptx", help="Path to the .pptx file")
    parser.add_argument("--out", default=None, help="Output directory (default: <pptx_dir>/_qc/)")
    # Default 1920 (1.5x 1280) so small text (chart annotations, footnotes,
    # numerals) is legible at thumbnail zoom. At 1280 a 9pt footnote was ~6px
    # tall and Claude could not reliably read it. Do not lower.
    parser.add_argument("--width", type=int, default=1920, help="Export width in pixels (default: 1920)")
    args = parser.parse_args()

    pptx_path = pathlib.Path(args.pptx).resolve()
    if not pptx_path.exists():
        print(f"ERROR: file not found: {pptx_path}", file=sys.stderr)
        sys.exit(1)
    if pptx_path.suffix.lower() != ".pptx":
        print(f"ERROR: expected a .pptx file, got: {pptx_path.suffix}", file=sys.stderr)
        sys.exit(1)

    out_dir = pathlib.Path(args.out).resolve() if args.out else pptx_path.parent / "_qc"
    export_via_powerpoint(pptx_path, out_dir, args.width)


if __name__ == "__main__":
    main()
